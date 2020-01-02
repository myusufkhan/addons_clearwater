# -*- coding: utf-8 -*-
# from odoo import http

# class Equipments(http.Controller):
#     @http.route('/installed_equipments/installed_equipments/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/installed_equipments/installed_equipments/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('installed_equipments.listing', {
#             'root': '/installed_equipments/installed_equipments',
#             'objects': http.request.env['installed_equipments.installed_equipments'].search([]),
#         })

#     @http.route('/installed_equipments/installed_equipments/objects/<model("installed_equipments.installed_equipments"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('installed_equipments.object', {
#             'object': obj
#         })