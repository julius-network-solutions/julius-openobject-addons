# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
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
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from tools.translate import _
from tools import DEFAULT_SERVER_DATE_FORMAT

TIME_UNIT = [
    ('year','Year'),
    ('month','Month'),
    ('day','Day'),
]

class certificate_template(osv.osv):
    _name = "certificate.template"
    
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self , cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)
    
    _columns = {
        'name' : fields.char("Template", size=64, required=True),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Name'),
        'certificate_ids': fields.one2many('certificate', 'template_id', 'Certificates'),
        'validity':  fields.integer('Validity' , required=True),
        'time_unit': fields.selection(TIME_UNIT, 'Time Unit', store= True, required=True),
        'object_id': fields.many2one('ir.model', 'Object Name'),
        'parent_id': fields.many2one('certificate.template', 'Parent Template', select=True),
        'child_ids': fields.one2many('certificate.template', 'parent_id', 'Childs Template'),
        'score_min': fields.integer('Minimum Score'),
        'score_max': fields.integer('Maximum Score'),
        'survey_id': fields.many2one('survey', 'Survey'),
        'survey_response_ids': fields.one2many('survey.response', 'certificate_template_id', 'Evaluations'),
    }

    def _find_object_id(self, cr, uid, context=None):
        """Finds id for case object"""
        object_id = context and context.get('object_id', False) or False
        ids = self.pool.get('ir.model').search(cr, uid, [('id', '=', object_id)])
        return ids and ids[0] or False

    _defaults = {
        'time_unit': 'year',
        'object_id' : _find_object_id,
    }
    
certificate_template()

class certificate(osv.osv):
    _name = "certificate"
    _description = "Certificate"
    
    def expiry_day_compute(self, cr, uid, ids, fields, args, context=None):
        res={}
        for this in self.browse(cr, uid, ids, context=context):
            res[this.id] = {
                'expiry_date': False,
            }
            if this.date_obtained:
                date_obtained = datetime.strptime(this.date_obtained, DEFAULT_SERVER_DATE_FORMAT)
                time_unit = this.time_unit
                validity = this.validity
                if time_unit == 'year':
                    time = relativedelta(years=validity)
                    expiry_date = datetime(date_obtained.year, date_obtained.month, date_obtained.day)
                if time_unit == 'month':
                    time = relativedelta(months=validity)
                    expiry_date = datetime(date_obtained.year, date_obtained.month, date_obtained.day) 
                if time_unit == 'day':
                    time = timedelta(days=validity)
                expiry_date = datetime(date_obtained.year, date_obtained.month, date_obtained.day) + time
                expiry_date = datetime.strftime(expiry_date, DEFAULT_SERVER_DATE_FORMAT)
                res[this.id]['expiry_date'] = expiry_date
        return res
            
    _columns = {
        'name' : fields.char("Certificate", size=64),
        'active': fields.boolean('Active'),
        'template_id': fields.many2one('certificate.template', 'Certificate Template'),
        'date_obtained': fields.date('Date Obtained', required=True),
        'validity': fields.integer('Validity' , required=True),
        'time_unit': fields.selection(TIME_UNIT, 'Time Unit', store=True, required=True),
        'expiry_date': fields.function(expiry_day_compute, string='Expiry Date', type='date', method=True, multi='expiry_date', strore=True),
        'field': fields.many2one('ir.model.fields', 'Field'),
        'object_id': fields.many2one('ir.model', 'Object Name'),
        'state': fields.selection([('close' , 'Close'), ('open' , 'Open') , ('updated', 'Updated')] , 'State', store=True, readonly=True),
        'send': fields.boolean('Send'),
    }

    def _find_object_id(self, cr, uid, context=None):
        """Finds id for case object"""
        ids = False
        object_id = context and context.get('object_id') or False
        if object_id:
            ids = self.pool.get('ir.model').search(cr, uid, [('id', '=', object_id)], limit=1, context=context)
        return ids and ids[0] or False

    _defaults = {
        'time_unit': 'year',
        'object_id': _find_object_id,
        'state': 'open',
        'send': False,
        'active': True,
    }
    
    def onchange_template_id(self, cr, uid, ids, template_id=False, context=None):
        value = {}
        if template_id:
            template_data = self.pool.get('certificate.template').browse(cr, uid, template_id, context=context)
            value = {
                'validity': template_data.validity,
                'time_unit': template_data.time_unit,
            }
        return {'value': value}
                     
    def create(self, cr, uid, vals, context=None):
        template_obj = self.pool.get('certificate.template')
        if vals.get('template_id'):
            template_data = template_obj.browse(cr, uid, vals.get('template_id'), context=context)
            vals.update({
                'name': template_data.name,
                'time_unit': template_data.time_unit,
            })
        return super(certificate, self).create(cr, uid, vals, context=context)  
    
    ### Send Email for Expiration Certificate ###
    def certificate_email(self, cr, uid, fields, ids=False, context=None):
        model_data = self.pool.get('ir.model.data')
        mail_message = self.pool.get('mail.message')
        email_template_obj  = self.pool.get('email.template')
        ## Manager information from Email Template ##
        manager_email_id = model_data.get_object_reference(cr, uid, 'base_certificate', 'update_manager')[1]
        manager_email_data = email_template_obj.browse(cr, uid, manager_email_id, context=context)
        mail_message.schedule_with_attach(cr, uid, 
                                                manager_email_data.email_from, 
                                                [str(manager_email_data.email_to)],
                                                manager_email_data.subject, 
                                                manager_email_data.body_text, 
                                                manager_email_data.model_id.model,
                                                mail_server_id = manager_email_data.mail_server_id.id, 
                                                context=context)
        ## User information from Email Template ##
        user_email_id = model_data.get_object_reference(cr, uid, 'base_certificate', 'update_user')[1]
        user_email_data = email_template_obj.browse(cr, uid, user_email_id, context=context)
        mail_message.schedule_with_attach(cr, uid, 
                                                user_email_data.email_from, 
                                                [str(user_email_data.email_to)], 
                                                user_email_data.subject, 
                                                user_email_data.body_text, 
                                                user_email_data.model_id.model,
                                                mail_server_id = user_email_data.mail_server_id.id, 
                                                context=context)   
        return True
    ### Check Certificate State ###
    def check_certificate_state(self, cr, uid, ids=False, context=None):
        res = {} 
        now = datetime.now()
        cert_ids = self.search(cr, uid, [], context=context)
        for certificate_data in self.browse(cr, uid, cert_ids, context=context):
            state = certificate_data.state
            date_obtained = datetime.strptime(certificate_data.date_obtained, DEFAULT_SERVER_DATE_FORMAT)
            expiry_date = datetime.strptime(certificate_data.expiry_date, DEFAULT_SERVER_DATE_FORMAT)
            if not (date_obtained < now and now < expiry_date) and (state=='open'):
                self.write(cr, uid, certificate_data.id, {'state':'close'}, context=context)
            if (state=='close') and expiry_date > now:
                self.write(cr, uid, certificate_data.id, {'state':'open'}, context=context)
        return res
    
    ### Certificate Creation form Template Present in Parent ### 
    def certificate_form_parent(self, cr, uid, parent_id, parent_model, child_id, child_field_name, context=None):
        if not parent_id or not parent_model:
            return False
        parent_model = self.pool.get(parent_model)
        parent_data = parent_model.browse(cr, uid, parent_id, context=context)
        # Loop on all certificate template present in parent record #
        template_cert_ids = parent_data.template_ids
        for template_data in template_cert_ids:
            valid_certificate = False
            # Search each certificates of this template in a field #
            cert_ids = self.search(cr, uid, [
                ('template_id', '=', template_data.id),
                (child_field_name, '=', child_id.id),
                ('active', '=', True),
            ], context=context)
            for cert_data in self.browse(cr, uid, cert_ids, context=context):
                if cert_data.state == 'open':
                    valid_certificate = True
                if cert_data.state == 'close': # Inactive Old Certificates #
                    self.write(cr, uid, cert_data.id, {'active': False}, context=context)
            # If no open certificates are found we create a new certificate #     
            if not valid_certificate:
                vals = {
                    'template_id': template_data.id,
                    'validity': 0,
                    'date_obtained': datetime.now(),
                    'expiry_date': datetime.now(),
                    'state': 'close',
                    child_field_name: child_id.id,
                }
                self.create(cr, uid, vals, context=context) 
        return True
    
    ### Update Certificate State As a Function of Survey Result ###
    def update_certificate(self, cr, uid, parent_id, parent_model, child_id, child_model, child_field_id, context=None):
        # Initialization #
        fields_obj = self.pool.get('ir.model.fields')
        srv_obj = self.pool.get('survey')
        resp_obj = self.pool.get('survey.response')
        child_model_obj = self.pool.get(child_model)
        child_field_name = fields_obj.browse(cr,uid,child_field_id,context=context).name
        # Current User determination #
        user_id = child_model_obj.browse(cr,uid, child_id.id, context=context).user_id.id
        # Certificates are created for each template present in parent #
        self.certificate_form_parent(cr, uid, parent_id, parent_model, child_id, child_field_name, context=context)   
        # Loop on each close certificate #
        cert_ids = self.search(cr, uid, [
            (field,'=',child_id.id),
            ('state', '=', 'close'),
        ], context=context)
        for certificate in self.browse(cr, uid, cert_ids, context=context):
            response_ids = resp_obj.search(cr, uid, [
                ('user_id', '=', user_id),
                ('state', '=', 'done'),
                ('survey_id','=',certificate.template.survey_id.id),
            ], context=context)
            # Loop on each response #
            for response_data in resp_obj.browse(cr, uid, response_ids, context=context):
                # Check if the score is correct #
                srv_min = certificate.template.score_min
                score = response_data.score
                if srv_min < score or score == srv_min:
                    # Update each certificate with the appropriate score #
                    vals = {
                        'date_obtained': response_data.date_create,
                        'validity': certificate.template.validity,
                        'state': 'updated',
                    }
                    self.write(cr, uid, certificate.id, vals, context=context)
        return cert_ids

    def check_documents(self, cr, uid, ids, context=None):
        data_obj = self.pool.get('ir.model.data')
        tree_id = data_obj._get_id(cr, uid, 'document', 'view_document_file_tree')
        form_id  = data_obj._get_id(cr, uid, 'document', 'view_document_file_form')
        if tree_id:
            tree_id = data_obj.browse(cr, uid, tree_id, context=context).res_id
        if form_id:
            form_id = data_obj.browse(cr, uid, form_id, context=context).res_id
        for id in ids:
            return {
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'ir.attachment',
                'views': [(tree_id, 'tree'),(form_id, 'form')],
                'type': 'ir.actions.act_window',
                'domain': ['&',('res_id','=',id),('res_model','=','base.certificate')],
                'target': 'new',
            }

certificate()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: