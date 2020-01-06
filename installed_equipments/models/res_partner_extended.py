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
    equipments_count = fields.Integer(compute='_equipments_count', string='Equipments Count')
    equipments_ids = fields.One2many('stock.move.dates', 'partner_id')

    def _equipments_count(self):
        all_partners = self.search([('id', 'child_of', self.ids)])
        all_partners.read(['parent_id'])
        equipments = self.env['stock.move.dates'].search([('partner_id', 'in', all_partners.ids),
                                                     ('is_equipment', '=', True),
                                                     ('picking_id.state', '=', 'done'),
                                                     ('picking_id.picking_type_code', '=', 'outgoing')
                                                    ])
        self.equipments_count = len(equipments)


    # @api.depends('equipments_ids.is_equipment')
    # def _equipments_count(self):
    #     self.equipments_count = 0
    #     # retrieve all children partners and prefetch 'parent_id' on them
    #     all_partners = self.search([('id', 'child_of', self.ids)])
    #     all_partners.read(['parent_id'])
    #     # ('is_equipment', '==', True), ('picking_id.state', '==', 'done'), (
    #     # 'picking_id.picking_type_code', '==', 'outgoing')
    #     equipments_groups = self.env['stock.move.dates'].read_group(
    #         domain=[('partner_id', 'in', all_partners.ids),('is_equipment','=',True),('picking_id.state', '=', 'done')],
    #         fields=['partner_id'], groupby=['partner_id']
    #     )
    #     print("equipments_groups",equipments_groups)
    #     partners = self.browse()
    #     for group in equipments_groups:
    #         print("group",group)
    #         partner = self.browse(group['partner_id'][0])
    #
    #         while partner:
    #             if partner in self:
    #                 print ("partner if ",partner,self)
    #                 partner.equipments_count += group['partner_id_count']
    #                 print("partner",partner)
    #                 partners |= partner
    #                 print("partners",partners)
    #             partner = partner.parent_id
    #             print("self",self,partners,self - partners,(self - partners).equipments_count)
    #     (self - partners).equipments_count = 0

    def action_create_equipments(self):
        all_partners = self.search([('id', 'child_of', self.ids)])
        all_partners.read(['parent_id'])
        equipment = self.env['stock.move.dates'].search([('is_equipment', '=', True),
                                                         ('partner_id', 'in', all_partners.ids),
                                                         ('picking_id.state', '=', 'done'),
                                                         ('picking_id.picking_type_code', '=', 'outgoing')])

        action = self.env.ref('installed_equipments.action_installed_equipments').read()[0]
        action['domain'] = [('id', 'in', equipment.ids)]
        action['views'] = [(self.env.ref('installed_equipments.cw_equipments_list').id, 'tree')
            ,(self.env.ref('installed_equipments.cw_equipments_form').id, 'form')
                           ]
        action['context'] =action['context'] = {'search_default_partner_id': self.id, 'default_partner_id': self.id}
        return action



