# -*- coding: utf-8 -*-
import odoo
from odoo import http
from odoo.http import Controller, route, request
from odoo.exceptions import AccessDenied,AccessError, UserError, AccessDenied
import urllib
from datetime import timedelta, datetime


# Done! The Odoo server is up and running. Specifications:
# Port: 8069
# User service: odoo
# User PostgreSQL: odoo
# Code location: odoo
# Addons folder: odoo/odoo-server/addons/
# Start Odoo service: sudo service odoo-server start
# Stop Odoo service: sudo service odoo-server stop
# Restart Odoo service: sudo service odoo-server restart

# recently_created_tasks = self.env['project.task'].search([
#                 ('create_date', '>', datetime.now() - timedelta(days=30)),
#                 ('is_fsm', '=', True),
#                 ('user_id', '!=', False)
#             ])

import odoo.addons.web.controllers.main as main


class Home(main.Home):

    @http.route('/web/session/authenticate', type='json', auth="none" ,cors='*')
    def authenticate(self, db, login, password, base_location=None):
        request.session.authenticate(db, login, password)
        return request.env['ir.http'].session_info()


class SubscriptionRoutes(http.Controller):

    @http.route('/get_profile/user', type="json", auth="none",cors='*')
    def get_profile_user(self, **kw):
        uid = self.check_authentication(kw)
        if isinstance(uid, dict):
            return uid
        try:
            user_info =request.env['res.users'].sudo().browse(uid)
            user_profile = {
                            'name':user_info.name,
                            'contact': user_info.phone,
                            'email': user_info.email,
                            'company_name': user_info.company_name,
                            }
            return {
                'success': True,
                'status': 'OK',
                'code': 200,
                'user_profile':user_profile
            }

        except Exception as e:
            return {
                'success': False,
                'status': 'FAILED',
                'code': 400,
                'reason': e
            }


    @http.route('/get_product',  cors='*' , type="json", methods=['POST','GET','OPTIONS'], auth="none" )
    def get_products(self, **kw):
        uid = self.check_authentication(kw)
        if isinstance(uid, dict):
            return uid
        try:
            product_dictonary = {}
            products = request.env['product.product'].sudo().search([('sale_ok', '=', True),('type', '!=', 'service'),('tracking', '=', 'none')])
            for line in products:
                attributes = {}
                for lines in line.product_template_attribute_value_ids:
                    attributes[lines.id] = {"variant_name":lines.display_name}

                product_dictonary[line.id] = {
                    'name': line.name if line.name else '',
                    'prduct_type': line.type if line.type else '',
                    'lst_price': line.name if line.name else '',
                    'taxes_id': line.name if line.name else '',
                    'qty_available': line.qty_available if line.qty_available else '',
                    'attributes': attributes if attributes else '',
                }
            return {
                'success': True,
                'status': 'OK',
                'code': 200,
                'products': product_dictonary,
                # 'user_profile':user_profile
            }

        except Exception as e:
            return {
                'success': False,
                'status': 'FAILED',
                'code': 400,
                'reason': e
            }

    @http.route('/get_tasks' ,methods=['POST','GET','OPTIONS'], type="json", auth="none",cors='*')
    def get_tasks(self, **kw):
        uid = self.check_authentication(kw)
        if isinstance(uid, dict):
            return uid
        try:
            if 'days' in kw.keys():
                user_tasks_ids = request.env['project.task'].sudo().search(([('user_id.id', '=', kw['uid']),('create_date', '>', datetime.now() - timedelta(days=int(kw['days'])))]))
            else:
                user_tasks_ids = request.env['project.task'].sudo().search(([('user_id.id','=', kw['uid'])]))
            # products = self.get_products()
            dictonary = {}
            for lines in user_tasks_ids:
                dictonary[lines.id] = {
                                       'title':lines.name if lines.name else '' ,
                                       'customer':lines.partner_id.name if lines.partner_id.name else '' ,
                                       'phone':lines.partner_phone if lines.partner_phone else '',
                                       'email':lines.partner_email if lines.partner_email else '',
                                       'date_begin':str(lines.planned_date_begin) if lines.planned_date_begin else '',
                                       'date_end':str(lines.planned_date_end) if lines.planned_date_end else '',
                                       'effective_time': lines.timesheet_timer_first_start if lines.timesheet_timer_first_start else '',
                                       'project_id': lines.project_id.name if lines.project_id.name else '',
                                       'created_on': lines.create_date if lines.create_date else '',
                                        # 'products':products if products else '',
                                        }
            return {
                'success': True,
                'status': 'OK',
                'code': 200,
                'user_id': dictonary,
                # 'user_profile':user_profile
            }
        except :
            return {
                'success': False,
                'status': 'FAILED',
                'code': 400,
                'reason':"User id not found or authentication failed"
            }

    @http.route('/update_tasks', type="json", auth="none", cors='*')
    def update_tasks(self, **kw):
        uid = self.check_authentication(kw)
        if isinstance(uid, dict):
            return uid
        try:
            if all(name in kw for name in ['id', 'uid', 'date_begin', 'date_end']):
                user_tasks_ids = request.env['project.task'].sudo().search(
                    ([('user_id.id', '=', kw['uid']), ('id', '=', kw['id'])]))
                user_tasks_ids.write({
                    'planned_date_begin': kw['date_begin'],
                    'planned_date_end': kw['date_end']
                })
                return {
                    'success': True,
                    'status': 'Date Updated Successfully',
                    'code': 200}
            else:
                return {
                'success': False,
                'status': 'FAILED',
                'code': 400,
                'reason': "Value missing from 'id', 'uid', 'date_begin', 'date_end'"
            }

        except Exception as e:
            return {
                'success': False,
                'status': 'FAILED',
                'code': 400,
                'reason': e
            }

    @http.route('/update_tasks/time', type="json", auth="none",cors='*')
    def update_tasks_time(self, **kw):
        uid = self.check_authentication(kw)
        if isinstance(uid, dict):
            return uid
        # if 'id' in list(kw.keys()): # ALL MANDATORY PARAMETERS SHOULD BE CHECK NOT ID "ONLY"
        if all(name in kw for name in ['id','uid','project_id','time_spend','name']):

            user_analytic_ids = request.env['account.analytic.line']
            date = datetime.today().date()
            if 'date' in kw.keys():
                date = kw['date']
                # search in hr.employee user id = uid if get multiple ue th first one
            user_id = request.env['res.users'].sudo().search([('id','=',int(kw['uid']))])
            if user_id.employee_ids:
                employee_id = user_id.employee_ids.id
            else:
                employee_id = ""
            user_analytic_ids.sudo().create({
                                'task_id' : int(kw['id']),
                                'employee_id' :employee_id,#(uid)  # employee id needs to get from user
                                'project_id' : int(kw['project_id']),
                                'unit_amount' : int(kw['time_spend']),
                                'date'    :date,   # optional if this task is done some other time
                                'name':kw['name']
                                  })
            return {
            'success': True,
            'status': 'success',
            'code': 200,
            'reason': "Time updated"
            }
        else:
            return {
            'success': False,
            'status': 'FAILED',
            'code': 400,
            'reason': "One or more are mission or invalid from Following task_id(id),employee_id(uid),project_id,name"
            }

    def check_authentication(self,kw):
        try:
            return request.session.authenticate(kw['db'], kw['login'],kw['password'] )
        except Exception as e: #(AccessDenied, AccessError, UserError, AccessDenied)
            e = str(e)
            if e == "Access denied":
                code = 420
            elif e.startswith("FATAL:  database"):
                code = 120
            else:
                code=400

            return {'success': False,
                    'status': False,
                    'code': code,
                    'reason': e
                    }




# CODE BACK UP


# # -*- coding: utf-8 -*-
# import base64
# from odoo import http
# from odoo.http import Controller, route, request
# from odoo.exceptions import AccessDenied
# import urllib
# from datetime import timedelta, datetime
# # class DataCheckRoute(http.Controller):
#
#     # @http.route('/subscription/update', type="json", auth='user', methods=['POST'] )
#     # def some_html(self, **kw):
#     #     print("kw",kw)
#     #    # request.env['res.partner'].create({'name':kw['check_server']})
#     #     return {
#     #        'success': True,
#     #        'status': 'OK',
#     #        'code': 200
#     #     }
#
#
# # Done! The Odoo server is up and running. Specifications:
# # Port: 8069
# # User service: odoo
# # User PostgreSQL: odoo
# # Code location: odoo
# # Addons folder: odoo/odoo-server/addons/
# # Start Odoo service: sudo service odoo-server start
# # Stop Odoo service: sudo service odoo-server stop
# # Restart Odoo service: sudo service odoo-server restart
#
# # recently_created_tasks = self.env['project.task'].search([
# #                 ('create_date', '>', datetime.now() - timedelta(days=30)),
# #                 ('is_fsm', '=', True),
# #                 ('user_id', '!=', False)
# #             ])
#
# import odoo.addons.web.controllers.main as main
#
#
# class Home(main.Home):
#
#     @http.route('/web/session/authenticate', type='json', auth="none" ,cors='*')
#     def authenticate(self, db, login, password, base_location=None):
#         request.session.authenticate(db, login, password)
#         return request.env['ir.http'].session_info()
#
#
# # class SubscriptionRoutes(http.Controller):
#
#     @http.route('/get_profile/user', type="json", auth="none",cors='*')
#     def get_profile_user(self, **kw):
#         try:
#             user_info =request.env['res.users'].sudo().browse(kw['uid'])
#             user_profile = {'name':user_info.name,
#                             'contact': user_info.phone,
#                             'email': user_info.email,
#                             'company_name': user_info.company_name,
#                             }
#
#             return {
#                 'success': True,
#                 'status': 'OK',
#                 'code': 200,
#                 'user_profile':user_profile
#             }
#
#         except:
#             return {
#                 'success': False,
#                 'status': 'FAILED',
#                 'code': 400,
#                 'reason': "Not Authenticate or Unknown"
#             }
#
#
#     @http.route('/get_product',  cors='*' , type="json", methods=['POST','GET','OPTIONS'], auth="none" )
#     def get_products(self, **kw):
#         try:
#             if self.check_authentication(kw) == 0:
#                 return {'success': False,
#                 'status': 'fail',
#                 'code': 400,
#                 'Reason':"Authentication Failed"
#             }
#             product_dictonary = {}
#             products = request.env['product.product'].sudo().search([('sale_ok', '=', True),('type', '!=', 'service'),('tracking', '=', 'none')])
#             for line in products:
#                 attributes = {}
#                 for lines in line.product_template_attribute_value_ids:
#                     attributes[lines.id] = {"variant_name":lines.display_name}
#
#                 product_dictonary[line.id] = {
#                     'name': line.name if line.name else '',
#                     'prduct_type': line.type if line.type else '',
#                     'lst_price': line.name if line.name else '',
#                     'taxes_id': line.name if line.name else '',
#                     'qty_available': line.qty_available if line.qty_available else '',
#                     'attributes': attributes if attributes else '',
#                 }
#             return {
#                 'success': True,
#                 'status': 'OK',
#                 'code': 200,
#                 'products': product_dictonary,
#                 # 'user_profile':user_profile
#             }
#
#         except:
#             return {
#                 'success': False,
#                 'status': 'FAILED',
#                 'code': 400,
#                 'reason': "Not Authenticate or Unknown"
#             }
#
#     @http.route('/get_tasks' ,methods=['POST','GET','OPTIONS'], type="json", auth="none", csrf=False)
#     def get_tasks(self, **kw):
#
#         # try:
#
#             if 'days' in kw.keys():
#                 user_tasks_ids = request.env['project.task'].sudo().search(([('user_id.id', '=', kw['uid']),('create_date', '>', datetime.now() - timedelta(days=int(kw['days'])))]))
#             else:
#                 user_tasks_ids = request.env['project.task'].sudo().search(([('user_id.id','=', kw['uid'])]))
#             # products = self.get_products()
#             dictonary = {}
#             for lines in user_tasks_ids:
#                 dictonary[lines.id] = {
#                                        'title':lines.name if lines.name else '' ,
#                                        'customer':lines.partner_id.name if lines.partner_id.name else '' ,
#                                        'phone':lines.partner_phone if lines.partner_phone else '',
#                                        'email':lines.partner_email if lines.partner_email else '',
#                                        'date_begin':str(lines.planned_date_begin) if lines.planned_date_begin else '',
#                                        'date_end':str(lines.planned_date_end) if lines.planned_date_end else '',
#                                        'effective_time': lines.timesheet_timer_first_start if lines.timesheet_timer_first_start else '',
#                                        'project_id': lines.project_id.name if lines.project_id.name else '',
#                                        'created_on': lines.create_date if lines.create_date else '',
#                                         # 'products':products if products else '',
#                                         }
#             return {
#                 'success': True,
#                 'status': 'OK',
#                 'code': 200,
#                 'user_id': dictonary,
#                 # 'user_profile':user_profile
#             }
#         # except :
#         #     return {
#         #         'success': False,
#         #         'status': 'FAILED',
#         #         'code': 400,
#         #         'reason':"User id not found"
#         #     }
#     @http.route('/update_tasks', type="json", auth="none",cors='*')
#     def update_tasks(self, **kw):
#         if ['uid','id'] in kw.keys():
#             user_tasks_ids = request.env['project.task'].sudo().search(([('user_id.id', '=', kw['uid']),('id', '=', kw['id'])]))
#             user_tasks_ids.write({
#                                   'date_begin': kw['id']['date_begin'],
#                                   'date_end': kw['id']['date_end']
#                                   })
#
#     @http.route('/update_tasks/time', type="json", auth="none",cors='*')
#     def update_tasks_time(self, **kw):
#         print(list(kw.keys()))
#         # if 'id' in list(kw.keys()): # ALL MANDATORY PARAMETERS SHOULD BE CHECK NOT ID "ONLY"
#         if all(name in kw for name in ['id','uid','project_id','time_spend','name']):
#
#             user_analytic_ids = request.env['account.analytic.line']
#             date = datetime.today().date()
#             if 'date' in kw.keys():
#                 date = kw['date']
#                 # search in hr.employee user id = uid if get multiple ue th first one
#             user_id = request.env['res.users'].sudo().search([('id','=',int(kw['uid']))])
#             if user_id.employee_ids:
#                 employee_id = user_id.employee_ids.id
#             else:
#                 employee_id = ""
#             user_analytic_ids.sudo().create({
#                                 'task_id' : int(kw['id']),
#                                 'employee_id' :employee_id,#(uid)  # employee id needs to get from user
#                                 'project_id' : int(kw['project_id']),
#                                 'unit_amount' : int(kw['time_spend']),
#                                 'date'    :date,   # optional if this task is done some other time
#                                 'name':kw['name']
#                                   })
#             return {
#             'success': True,
#             'status': 'success',
#             'code': 200,
#             'reason': "Time updated"
#             }
#         else:
#             return {
#             'success': False,
#             'status': 'FAILED',
#             'code': 400,
#             'reason': "One or more are mission or invalid from Following task_id(id),employee_id(uid),project_id,name"
#             }
#
#     def check_authentication(self,kw):
#         uid = request.session.authenticate(kw['db'], kw['login'],kw['password'] )
#         if uid:
#             return uid
#         else: return 0