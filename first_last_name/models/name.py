# -*- coding: utf-8 -*-

from odoo import api, models, fields

class FirstNameLastName(models.Model):
    _inherit = 'res.partner'

    first_name = fields.Char(string='First Name', compute='_compute_first_name',default=False,store=True, readonly=False)
    last_name = fields.Char(string='Last Name', compute='_compute_last_name', default=False,store=True, readonly=False)
    nick_name = fields.Char(string='Nick Name')

    @api.onchange('last_name', 'first_name')
    def _onchange_first_last_name(self):
        for i in self:
            if i.first_name and i.last_name:
                i.name = (i.first_name + ' ' + i.last_name)

    @api.onchange('name','company_type')
    def _onchange_name(self):
        for i in self:
            if i.name and (i.company_type == 'person' or i.company_type == False):
                name = i.name
                list = name.split(' ', 1)
                i.first_name = list[0]
                if len(list) == 2:
                    i.last_name = list[1]
                else: i.last_name = False
            else:
                i.first_name = False
                i.last_name = False

    @api.depends('name')
    def _compute_first_name(self):

        for i in self:
            if i.name and  i.company_type == 'company':
                i.first_name = False
                i.last_name = False
                i.nick_name = False
            if i.name :
                if i.company_type == 'person' or i.company_type == False :
                    list = i.name.split(' ', 1)
                    if list and i.company_type == 'person':
                        i.first_name = list[0]

    @api.depends('name')
    def _compute_last_name(self):
        for i in self:

            if i.name and i.company_type == 'company':
                i.first_name = False
                i.last_name = False
                i.nick_name = False
            elif i.name:
                if i.company_type == 'person' or i.company_type == False:
                    list = i.name.split(' ', 1)
                    if len(list) == 2 and i.company_type == 'person':
                        i.last_name = list[1]
                    else:i.last_name = False