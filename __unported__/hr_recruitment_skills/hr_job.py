# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
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
#################################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _

class hr_employee_category(orm.Model):
    _inherit = 'hr.employee.category'

    _columns = {
        'is_skill': fields.boolean('Is Skill'),
    }

    _defaults = {
        'is_skill': False,
    }

class hr_job(orm.Model):
    _inherit = 'hr.job'

    _columns = {
        'skill_ids': fields.many2many('hr.employee.category',
                                      'job_skill_rel',
                                      'job_id',
                                      'skill_id',
                                      'Skills',
                                      domain=[('is_skill', '=', True)]),
        'applicant_ids': fields.many2many('hr.applicant', 'job_applicant_rel','job_id','applicant_id', 'Applicants'),
    }

    def open_list_of_applicants(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data_obj = self.pool.get('ir.model.data')
        action_model, action_id = data_obj.get_object_reference(
                cr, uid, 'hr_recruitment', 'crm_case_categ0_act_job')
        action = self.pool.get(action_model).read(
            cr, uid, action_id, context=context)
        if context.get('skill_ids'):
            skill_ids = context['skill_ids'][-1][-1]
            act_context = eval(action['context'])
            act_context.update({'skill_ids': skill_ids})
            for skill_id in skill_ids:
                act_context.update({('search_default_skill_%s' %str(skill_id)): 1})
            act_context.update({'job_id': ids[0]})
            action['context'] = act_context
        return action

    def fields_view_get(self, cr, uid,
                        view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        res = super(hr_job, self).fields_view_get(cr, uid,
            view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=submenu)
        if view_type == 'search' and context.get('skill_ids', False):
            xml = '<separator/>\n'
            skills_obj = self.pool.get('hr.employee.category')
            skill_ids = context.get('skill_ids')
            if skill_ids and skill_ids[-1] and isinstance(skill_ids[-1], list):
                skill_ids = skill_ids[-1][-1]
            for skill in skills_obj.browse(
                cr, uid, skill_ids, context=context):
                skill_id = skill.id
                new_xml = ("""<filter name="skill_%s" string="%s" """
                    """domain="[('skill_ids', '=', %s)]"/>\n"""
                    %(str(skill_id), skill.complete_name, skill_id))
                xml += new_xml
            if xml != '<separator/>':
                xml += '<separator/>'
            res['arch'] = unicode(res['arch'],
                'utf8').replace('<separator name="skills"/>', xml)
        return res
    
    def add_job(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if context.get('applicant_id'):
            applicant_obj = self.pool.get('hr.applicant')
            applicant_id = context.get('applicant_id')
            job_ids = []
            for job_id in ids:
                applicant = applicant_obj.browse(cr, uid, applicant_id, context=context)
                if applicant.job_ids:
                    job_ids = [x.id for x in applicant.job_ids]
                job_ids.append(job_id)
                applicant_obj.write(cr, uid, [applicant_id], {'job_ids': [(6, 0, job_ids)]}, context=context)
        return True
    
class hr_applicant(orm.Model):
    _inherit = "hr.applicant"

    _columns = {
        'categ_ids': fields.many2many('hr.employee.category',
                                      'applicant_categ_rel',
                                      'job_id',
                                      'categ_id',
                                      'Categories'),
        'job_ids': fields.many2many('hr.job', 'applicant_job_rel','applicant_id','job_id', 'Jobs'),
    }

    def open_list_of_jobs(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data_obj = self.pool.get('ir.model.data')
        action_model, action_id = data_obj.get_object_reference(
                cr, uid, 'hr', 'action_hr_job')
        action = self.pool.get(action_model).read(
            cr, uid, action_id, context=context)
        if context.get('skill_ids'):
            skill_ids = context['skill_ids'][-1][-1]
            act_context = eval(action['context'])
            act_context.update({'skill_ids': skill_ids})
            for skill_id in skill_ids:
                act_context.update({('search_default_skill_%s' %str(skill_id)): 1})
            act_context.update({'applicant_id': ids[0]})
            action['context'] = act_context
        return action

    def fields_view_get(self, cr, uid,
                        view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        res = super(hr_applicant, self).fields_view_get(cr, uid,
            view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=submenu)
        if view_type == 'search' and context.get('skill_ids', False):
            xml = '<separator/>\n'
            skills_obj = self.pool.get('hr.employee.category')
            skill_ids = context.get('skill_ids')
            if skill_ids and skill_ids[-1] and isinstance(skill_ids[-1], list):
                skill_ids = skill_ids[-1][-1]
            for skill in skills_obj.browse(
                cr, uid, skill_ids, context=context):
                skill_id = skill.id
                new_xml = ("""<filter name="skill_%s" string="%s" """
                    """domain="[('categ_ids', '=', %s)]" filter_condition="and"/>\n"""
                    %(str(skill_id), skill.complete_name, skill_id))
                xml += new_xml
            if xml != '<separator/>\n':
                xml += '<separator/>'
            res['arch'] = unicode(res['arch'],
                'utf8').replace('<separator name="skills"/>', xml)
        return res
    
    def add_applicant(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        job_id = False
        if context.get('job_id'):
            job_id = context.get('job_id')
        elif context.get('active_model') == 'hr.job' and context.get('active_id'):
            job_id = context.get('active_id')
        if job_id:
            job_obj = self.pool.get('hr.job')
            applicant_ids = []
            for applicant_id in ids:
                job = job_obj.browse(cr, uid, job_id, context=context)
                if job.applicant_ids:
                    applicant_ids = [x.id for x in job.applicant_ids]
                applicant_ids.append(applicant_id)
                job_obj.write(cr, uid, [job_id], {'applicant_ids': [(6, 0, applicant_ids)]}, context=context)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
