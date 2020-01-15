# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResPartner(models.Model):
    """ Res Partner """
    _inherit = 'res.partner'
    _description = "Inherit Res Partner"

    code = fields.Char(string='Account ID', required=False,
                       copy=False, readonly=False, index=True,
                       default=lambda self: _(''))

    @api.model
    def create(self, vals):
        if 'parent_id' in vals.keys():
            if vals['parent_id'] == False:
                vals['code'] = self.env['ir.sequence'].next_by_code(
                                                'res.partner.code') or 'New'
        partner = super(ResPartner, self).create(vals)
        return partner

    @api.model
    def create_from_ui(self, partner):
        """ create or modify a partner from the point of sale ui.
            partner contains the partner's fields. """
        # image is a dataurl, get the data after the comma
        if partner.get('image_1920'):
            partner['image_1920'] = partner['image_1920'].split(',')[1]
        partner_id = partner.pop('id', False)

        # Calculate  Code for partner custom
        #-----------------------------------
        partner_code_check = self.env['res.partner'].search([('id','=',partner_id)])
        if 'code' not in partner.keys():
            if not partner_code_check.code:
                partner['code'] = self.env['ir.sequence'].next_by_code(
                    'res.partner.code') or 'New'
            else:
                partner['code'] = partner_code_check.code

        # Calculate First Name Last Name custom
        #------------------------
        if 'name' in partner.keys():
            name = partner['name']
            if name != False:
                list = name.split(' ', 1)
                partner['first_name'] = list[0]
                if len(list) == 2:
                    partner['last_name'] = list[1]
        #------------------------
        if partner_id:  # Modifying existing partner
            self.browse(partner_id).write(partner)
        else:
            partner['lang'] = self.env.user.lang
            partner_id = self.create(partner).id
        return partner_id