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

from osv import osv, fields
import tools
from datetime import datetime
from tools.translate import _

class hr_job(osv.osv):
    _inherit = "hr.job"
    
    _columns = {
        'type_ids': fields.many2many('certificate.template', 'certif_job_rel', 'job_id', 'type_id', 'Certificates Type'),
    }
    
hr_job()

class hr_employee(osv.osv):
    _inherit = "hr.employee"
     
    _columns = {
        'certificate_ids': fields.one2many('certificate', 'employee_id', 'Qualification Certificate'),
        'survey_response_ids': fields.one2many('survey.response', 'user_id', 'Survey Response'),
    }

    ### Check Job Certificate ### 
    def check_certificate(self, cr, uid, ids, fields, context=None):
        field_obj = self.pool.get('ir.model.fields')
        certif_obj = self.pool.get('certificate')
        job_model = 'hr.job'
        child_model = 'hr.employee'
        emp_field_name = 'employee_id'
        for this in self.browse(cr, uid, ids, context=context):
            job_id = this.job_id.id
            emp_field_id = field_obj.search(cr, uid, [
                ('model','=','certificate'),
                ('name','=','employee_id')
            ], limit=1, context=context)[0]
            close_certif_ids = certif_obj.check_certificate(cr, uid, parent_id=job_id, parent_model=job_model, child_model=child_model, child_id=this, child_field_name=emp_field_name, child_field_id=emp_field_id, context=context)                
        return True

    ### Failed Certificate Survey ### 
    def certificate_survey(self, cr, uid, ids, fields, context=None):
        model_data = self.pool.get('ir.model.data')
        mail_message = self.pool.get('mail.message')
        email_template_obj  = self.pool.get('email.template')
        survey_resp = self.pool.get('survey.response')
        for this in self.browse(cr, uid, ids, context=context):
            empl_survey_ids = survey_resp.search(cr, uid, [
                                ('user_id', '=', this.id),
                                ('state', '=', 'done')
                            ], context=context)
            certificate_ids = this.certificate_ids
            for certificate_id in certificate_ids:
                type_score = certificate_id.type_id.score_min
                survey_id = certificate_id.type_id.survey_id
                for resp in survey_resp.browse(cr, uid, empl_survey_ids, context=context):
#                    and survey_id.score <type_score:
                    empl_survey_id = empl_survey_ids.survey_id
                    if survey_id.id == empl_survey_id.id:
                        resp_email_id = model_data.get_object_reference(cr, uid, 'hr_certificate', 'failed_survey_manager')[1]
                        resp_email_data = email_template_obj.browse(cr, uid, resp_email_id, context=context)
                        mail_message.schedule_with_attach(cr, uid, 
                                                                resp_email_data.email_from, 
                                                                [str(resp_email_data.email_to)],
                                                                resp_email_data.subject, 
                                                                resp_email_data.body_text, 
                                                                resp_email_data.model_id.model,
                                                                mail_server_id = resp_email_data.mail_server_id.id, 
                                                                context=context)
        return True
    
hr_employee()

class base_certificate_type(osv.osv):
    _inherit = "certificate.template"

    _columns = {
        'job_ids': fields.many2many('hr.job', 'certif_job_rel', 'type_id', 'job_id', 'Jobs'),
    }
    
#    def create(self, cr, uid, vals, context=None):
#        if context is None:
#            context = {}
#        if vals.get('job_ids') and vals.get('job_ids')[0][2]:
#            object_id = self.pool.get('ir.model').search(cr, uid, [('model','=','hr.employee')], limit=1, context=context)[0]
#            vals.update({'object_id':object_id})
#        return super(base_certificate_type, self).create(cr, uid, vals, context)
    
    ### Update Certificate ### 
    def job_update_certificate_type(self, cr, uid, ids, fields, context=None):
        field_obj = self.pool.get('ir.model.fields')
        certificate_obj = self.pool.get('certificate')
        for certificate_type in self.browse(cr, uid, ids, context=context):
            for job_data in certificate_type.job_ids:
                field = 'employee_id'
                employee_ids = job_data.employee_ids
                for employee in employee_ids:
                    vals = {}
                    job_cert_ids = certificate_obj.search(cr, uid, [
                            ('type_id', '=', certificate_type.id),
                            (field, '=', employee.id)
                        ], context=context) 
                    if not job_cert_ids:
                        vals = {
                            'name': certificate_type.name,
                            'type_id': certificate_type.id,
                            'date_obtained': datetime.now(),
                            'validity': 0,
                            'time_unit': certificate_type.time_unit,
                            'expiry_date': datetime.now(),
                            'employee_id': employee.id,
                            'state': 'close',
                        } 
                        certificate_obj.create(cr, uid, vals, context=context) 
        return True

base_certificate_type()

class base_certificate(osv.osv):
    _inherit = "certificate"
               
    _columns = {
        'job_id': fields.many2one('hr.job', 'Job'),
        'employee_id': fields.many2one('hr.employee', 'Employee'),
        'parent_id': fields.many2one('hr.employee', 'Manager'),
        'department_id': fields.many2one('hr.department', 'Deparment'),
    }
    
    def onchange_employee(self, cr, uid, ids, employee_id=False, context=None):
        value = {}
        if employee_id:
            employee_data = self.pool.get('hr.employee').browse(cr, uid, employee_id, context=context)
            value = {
                'parent_id': employee_data.parent_id.id,
                'department_id': employee_data.department_id.id
            }
        return {'value': value}
    
    def onchange_fiscalyear(self, cr, uid, ids, fiscalyear_id=False, context=None):
        value = {}
        if fiscalyear_id:
            start_period = end_period = False
            cr.execute('''
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               ORDER BY p.date_start ASC
                               LIMIT 1) AS period_start
                UNION ALL
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND p.date_start < NOW()
                               ORDER BY p.date_stop DESC
                               LIMIT 1) AS period_stop''', (fiscalyear_id, fiscalyear_id))
            periods =  [i[0] for i in cr.fetchall()]
            if periods and len(periods) > 1:
                start_period = periods[0]
                end_period = periods[1]
            value = {
                'period_from': start_period,
                'period_to': end_period,
            }
        else:
            value = {
                'period_from': False,
                'period_to': False,
            }
        return {'value': value}
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if context.get('active_model',False) and context.get('active_model') == 'hr.employee':
            if context.get('active_id'):
                employee_id = context.get('active_id')
                vals.update({
                    'employee_id':employee_id,
                })
    #        if vals.get('job_id') or vals.get('employee_id'):
    #            object_id = self.pool.get('ir.model').search(cr, uid, [('model','=','hr.employee')], limit=1, context=context)[0]
    #            vals.update({'object_id':object_id})
            survey_obj = self.pool.get('survey')
            employee_obj = self.pool.get('hr.employee')
            type_obj = self.pool.get('certificate.template')
            employee_model_id = self.pool.get('ir.model').search(cr, uid, [('model','=','hr.employee')], limit=1)[0]
            if vals.get('state') == 'close' and vals.get('type_id') and vals.get('employee_id'):
                survey_id = type_obj.browse(cr, uid, vals.get('type_id'), context=context).survey_id
                employee_data = employee_obj.browse(cr, uid, vals.get('employee_id'), context=context)
                if survey_id:
                    survey_user_id = employee_data.user_id.id
                    survey_obj.write(cr, uid, survey_id.id, {
                        'invited_user_ids': [(4, survey_user_id)]
                    }, context=context)
                    
        return super(base_certificate, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        survey_obj = self.pool.get('survey')
        employee_model_id = self.pool.get('ir.model').search(cr, uid, [('model','=','hr.employee')], limit=1)[0]
        for certif_data in self.browse(cr, uid, ids, context=context):
            if (certif_data.object_id.id == employee_model_id) and (certif_data.state == 'close' or vals.get('state')  == 'close'):
                if certif_data.type_id and certif_data.type_id.survey_id:
                    survey_user_id = certif_data.employee_id.user_id.id
                    survey_obj.write(cr, uid, certif_data.type_id.survey_id.id, {
                        'invited_user_ids': [(4, survey_user_id)]
                    }, context=context)
        return super(base_certificate, self).write(cr, uid, ids, vals, context=context)
    
    #####  Send Expiration Mail ######
    def send_email(self, cr, uid, ids=False, context=None):
        result = True
        cert_ids = self.search(cr, uid, [
            ('state', '=', 'close'),
            ('send','=',False)
        ], context=context)
        for cert in self.browse(cr, uid, cert_ids, context=context):
            employee = cert.employee_id
            if employee:
                self.write(cr, uid, cert.id, {'send': True}, context=context)             
                result = super(base_certificate, self).certificate_email(cr, uid, employee, [cert.id], context=context)
        return result
                
base_certificate()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: