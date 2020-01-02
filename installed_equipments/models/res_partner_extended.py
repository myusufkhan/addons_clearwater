# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartnerExtended(models.Model):
    _inherit = 'res.partner'
    phone = fields.Char(string="Primary Phone")
    mobile = fields.Char(string='Secondary Phone')

    _sql_constraints = [(
        'unique_phone_uniq',
        'UNIQUE(phone)',
        "Primary Phone must be unique !"
    )]
    equipments_count = fields.Integer(compute='_equipments_count', string='Equipments Count' )
    equipments_ids = fields.One2many('cw.equipments', 'partner_id')


    # _sql_constraints = [
    #     ('phone_uniq', 'unique (phone)', "Primary Phone must be unique !"),
    # ]

    # @api.depends('equipments_ids.is_equipment')
    def _equipments_count(self):
        # for line in self.equipments_ids:
            # print(line.is_equipment == True)
            # print(line.picking_id.state == 'done')
        equipment = self.equipments_ids.filtered(lambda rec: (rec.is_equipment == True) and (rec.picking_id.state == 'done') and (rec.picking_id.picking_type_code == 'outgoing'))
        #
        # print("equipment",equipment)

        self.equipments_count = len(equipment)


    def action_create_equipments(self):
        equipment = self.equipments_ids.filtered(lambda rec: (rec.is_equipment == True) and (rec.picking_id.state == 'done') and (rec.picking_id.picking_type_code == 'outgoing') )
        # print("action_create_equipments",equipment)
        # and (rec.picking_id.picking_code == 'outgoing')
        action = self.env.ref('installed_equipments.action_installed_equipments').read()[0]
        action['domain'] = [('id', 'in', equipment.ids)]
        action['views'] = [(self.env.ref('installed_equipments.cw_equipments_list').id, 'tree')
            ,(self.env.ref('installed_equipments.cw_equipments_form').id, 'form')
                           ]
        return action



