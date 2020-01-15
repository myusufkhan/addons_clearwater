# -*- coding: utf-8 -*-


from odoo import models, fields, api, _

class ProjectTaskExt(models.Model):
    _inherit = "project.task"

    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Add Sale Order',

        help='Encoding help. When selected, the associated sales order lines are added to the site survey. Several SO can be selected.'
    )


class SaleOrdExtd(models.Model):
    _inherit = 'sale.order'

    fsm_task_count = fields.Integer(compute='_get_fsm_tasks', string='FSM task Count',default = 0)
    task_ids = fields.Many2many("project.task",string="# of Tasks",compute='_get_fsm_tasks',readonly=True, copy=False)

    def action_create_fsm_task(self):

        tasks = self.mapped('task_ids')
        action = self.env.ref('industry_fsm.project_task_action_fsm').read()[0]
        action['context'] = {'default_order_id': self.id, 'default_partner_id': self.partner_id.id,
                             'default_user_id': self.user_id.id}

        if len(tasks) > 1:
            action['domain'] = [('id', 'in', tasks.ids)]
            action['views'] = [(self.env.ref('industry_fsm.project_task_view_list_fsm').id, 'tree'),
                               (self.env.ref('industry_fsm.project_task_view_form').id, 'form'),
                               (self.env.ref('industry_fsm.project_task_view_calendar_fsm').id, 'calendar'),
                               (self.env.ref('project_enterprise.project_task_map_view').id, 'map'),
                               (self.env.ref('project_enterprise.project_task_view_gantt').id, 'gantt')]
        elif len(tasks) == 1:
            action['views'] = [(self.env.ref('industry_fsm.project_task_view_form').id, 'form')]
            action['res_id'] = tasks.ids[0]
        else:
            action['domain'] = [('id', 'in', tasks.ids)]
            action['views'] = [(self.env.ref('industry_fsm.project_task_view_list_fsm').id, 'tree'),
                               (self.env.ref('industry_fsm.project_task_view_form').id, 'form'),
                               (self.env.ref('industry_fsm.project_task_view_calendar_fsm').id, 'calendar'),
                               (self.env.ref('project_enterprise.project_task_map_view').id, 'map'),
                               (self.env.ref('project_enterprise.project_task_view_gantt').id, 'gantt')]
        return action


    def _get_fsm_tasks(self):
        self.fsm_task_count = 0
        self.task_ids = []
        for order in self:
            tasks_list = order.env['project.task'].search([('order_id', '=', order.id)]).ids
            if tasks_list:
                order.task_ids = [(6, 0, tasks_list)]
                order.fsm_task_count = len(tasks_list)



