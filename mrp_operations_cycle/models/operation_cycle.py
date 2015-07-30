# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import time
from openerp import api, models, fields
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

STATUS = [('draft','Draft'),('cancel','Cancelled'),('pause','Pending'),('startworking', 'In Progress'),('done','Finished')]

class operation_cycle(models.Model):
    _name = 'operation.cycle'
    _description = 'Operation Cycle'
    _order = 'date_planned'
    
    def _default_user(self):
        return self.env.uid
    
    ''' Definition Fields '''
    name = fields.Char('Name', size=64)
    sequence = fields.Integer('Sequence', default=(lambda *a: 1))
    qty = fields.Float('Quantity')
    real_qty = fields.Float('Real Quantity')
    uom_id = fields.Many2one('product.uom', 'Unit')
    user_id = fields.Many2one('res.users', string='User', default=_default_user)
    total_cycle = fields.Float('Total Cycle', digits=(16, 2))
    cycle_number = fields.Float('Cycle Number', digits=(16, 2))
    hour = fields.Float('Number of Hours', digits=(16, 2))
    state = fields.Selection(STATUS, 'Status', readonly=True, copy=False, default='draft')
    
    ''' Relational Fields '''
    product_id = fields.Many2one('product.product', string='Product', related='operation_id.product')
    operation_id = fields.Many2one('mrp.production.workcenter.line')
    workcenter_id = fields.Many2one('mrp.workcenter', string='Workcenter', related='operation_id.workcenter_id')
    production_id = fields.Many2one('mrp.production',
                                 related='operation_id.production_id',
                                 string='Production', store=True)
    ''' Time Fields '''
    date_planned = fields.Datetime(string='Date Planned')
    date_planned_end = fields.Datetime('End Date Planned', compute="_get_date_end", store=True)
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    uptime = fields.Float(string='Uptime', compute='operation_uptime',
                          store=True, digits=(12, 6))
    consistent = fields.Selection([('ok', 'OK'),('ko', 'KO')], 'Consistent', compute='_check_date', store=True)
    
    @api.one
    @api.depends('date_planned', 'date_planned_end','workcenter_id')
    def _check_date(self):
        domain = [
            ('date_planned', '<', self.date_planned),
            ('date_planned_end', '>', self.date_planned),
            ('workcenter_id', '=', self.workcenter_id.id),
            ('id', '!=', self.id),
            ('state', 'not in', ['cancel']),
        ]
        cycles = self.search(domain)
        if cycles:
            self.consistent = 'ko'
        else: 
            self.consistent = 'ok'
    
    @api.one
    @api.depends('date_planned', 'hour', 'operation_id.workcenter_id.calendar_id')
    def _get_date_end(self):
        """ Finds ending date.
        @return: Dictionary of values.
        """
        date_planned_end = False
        if self.date_planned:
            date = datetime.strptime(self.date_planned, DEFAULT_SERVER_DATETIME_FORMAT)
            date_planned_end = date + timedelta(hours=self.hour)
        self.date_planned_end = date_planned_end
    
    @api.one
    @api.depends('start_date', 'end_date')
    def operation_uptime(self):
        if self.end_date and self.start_date:
            timedelta = fields.Datetime.from_string(self.end_date) - \
                fields.Datetime.from_string(self.start_date)
            self.uptime = timedelta.total_seconds() / 3600.
        else:
            self.uptime = 0
            
    @api.model
    def compute_cycle_date(self, date, hour):
        if isinstance(date,str): 
            date = datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT)
            new_date = date + timedelta(hours=hour)
        else: 
            new_date = date + timedelta(hours=hour)
        return new_date
    
    """ State Action """
    @api.multi 
    def action_draft(sel):
        return self.write({'state': 'draft'})
    
    @api.multi 
    def action_start_working(self):
        self.write({'state':'startworking', 'date_start': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True
    
    @api.multi 
    def action_done(self):
        delay = 0.0
        if self.date_start:
            date_now = time.strftime('%Y-%m-%d %H:%M:%S')
            
            date_start = datetime.strptime(self.date_start,'%Y-%m-%d %H:%M:%S')
            date_finished = datetime.strptime(date_now,'%Y-%m-%d %H:%M:%S')
            delay += (date_finished-date_start).days * 24
            delay += (date_finished-date_start).seconds / float(60*60)
    
            self.write({'state':'done', 'date_finished': date_now,'delay':delay})
            self.modify_production_order_state('done')
        return True
    
    @api.multi
    def action_cancel(self):
        return self.write({'state':'cancel'})

    @api.multi
    def action_pause(self):
        return self.write({'state':'pause'})

    @api.multi
    def action_resume(self):
        return self.write({'state':'startworking'})
            
class mrp_production_workcenter_line(models.Model):
    _inherit = 'mrp.production.workcenter.line'
    
    operation_cycle_ids = fields.One2many('operation.cycle',
                                          'operation_id',
                                          string='Operation Cycles')
    
    real_qty = fields.Float(string='Real Quantity', compute='compute_real_values', store=True, digits=(12, 6))
    delay = fields.Float(string='Delay', compute='compute_real_values', store=True, digits=(12, 6))
    date_start = fields.Datetime(string='Start Date', compute='compute_real_values', store=True, digits=(12, 6))
    date_finished = fields.Datetime(string='End Date', compute='compute_real_values', store=True, digits=(12, 6))
    
    @api.one
    @api.depends('operation_cycle_ids')
    def compute_real_values(self):
        """ Init """
        delay = real_qty = 0
        start_date = end_date = False
        """ Process """
        for cycle in self.operation_cycle_ids:
            delay += cycle.uptime
            real_qty += cycle.real_qty
            if not start_date or cycle.start_date < start_date:
                start_date = cycle.start_date
            if not end_date or cycle.end_date > end_date:
                end_date = cycle.end_date
        """ Result """
        self.real_qty = real_qty
        self.delay = delay
        self.date_start = start_date
        self.date_finished = end_date

class mrp_production(models.Model):
    _inherit = 'mrp.production'
    
    production_cycle_ids = fields.One2many('operation.cycle',
                                          'production_id',
                                          string='Operation Cycles')
    
    real_qty = fields.Float(string='Real Quantity', compute='compute_real_values', store=True, digits=(12, 6))
    real_time = fields.Float(string='Delay', compute='compute_real_values', store=True, digits=(12, 6))
    date_start = fields.Datetime(string='Start Date', compute='compute_real_values', store=True, digits=(12, 6))
    date_finished = fields.Datetime(string='End Date', compute='compute_real_values', store=True, digits=(12, 6))
    
    @api.one
    @api.depends('production_cycle_ids')
    def compute_real_values(self):
        """ Init """
        real_time = real_qty = 0
        start_date = end_date = False
        """ Process """
        for work_order in self.production_cycle_ids:
            real_time += work_order.uptime
            real_qty += work_order.real_qty
            if not start_date or work_order.start_date < start_date:
                start_date = work_order.start_date
            if not end_date or work_order.end_date > end_date:
                end_date = work_order.end_date
        """ Result """
        self.real_qty = real_qty
        self.real_time = real_time
        self.date_start = start_date
        self.date_finished = end_date
        
    @api.one
    def _action_compute_lines(self, properties=None):
        """ Initialization """
        workcenter_line_obj = self.env['mrp.production.workcenter.line']
        workcenter_cycle_obj = self.env['operation.cycle']
        """ Initial Process  """
        result = super(mrp_production, self)._action_compute_lines(properties)
        global_date = False
        for workcenter_line in self.workcenter_lines:
            hour = workcenter_line.hour/(workcenter_line.cycle or 1)
            vals = {
                'name': workcenter_line.name,
                'uom_id': workcenter_line.uom.id,
                'total_cycle': workcenter_line.cycle,
                'operation_id': workcenter_line.id,
                'hour': hour,
            }
            """ Creation of cycle for the work-order """
            cycle_number = 1  
            if not global_date:
                date = workcenter_line.date_planned or workcenter_line.production_id.date_planned
                global_date = workcenter_cycle_obj.compute_cycle_date(date, (hour*(workcenter_line.cycle)))
            else:
                date = global_date
                global_date = workcenter_cycle_obj.compute_cycle_date(global_date, (hour*(workcenter_line.cycle)))
                
             
            global_qty = workcenter_line.qty
            
            while cycle_number <= workcenter_line.cycle:
                if global_qty < workcenter_line.workcenter_id.capacity_per_cycle:
                    qty = global_qty
                else:
                    qty = workcenter_line.workcenter_id.capacity_per_cycle
                    global_qty -= qty
                vals.update({
                    'qty': qty,
                    'cycle_number': cycle_number,
                    'date_planned': workcenter_cycle_obj.compute_cycle_date(date, (hour*(cycle_number-1))),
                })
                workcenter_cycle_obj.create(vals)
                cycle_number += 1
        return result
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: