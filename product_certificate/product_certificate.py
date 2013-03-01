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
from datetime import datetime
from tools.translate import _

class product_product(osv.osv):
    _inherit = "product.product"
    
    _columns = {
        'prodlot_ids': fields.one2many('stock.production.lot', 'product_id', 'Production Lot ID'),
        'template_ids': fields.many2many('certificate.template', 'certif_prod_rel', 'template_id', 'product_id', 'Certificates'),
    }
    
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'prodlot_ids': [],
            'template_ids': []
        })
        return super(product_product, self).copy(cr, uid, id, default, context=context)
    
product_product()

class stock_production_lot(osv.osv):
    _inherit = "stock.production.lot"
    
    _columns = {
        'user_id': fields.many2one('res.users', 'User'),
        'certificate_ids': fields.one2many('certificate', 'prodlot_id', 'Qualification Certificate'),
        'survey_response_ids': fields.one2many('survey.response', 'user_id', 'Survey Response'),
    }

    ### Update Prodlot Certificate ### 
    def update_prodlot_certificate(self, cr, uid, ids, fields, context=None):
        field_obj = self.pool.get('ir.model.fields')
        certificate_obj = self.pool.get('certificate')
        field_id = field_obj.search(cr, uid, [
                    ('model','=','certificate'),
                    ('name','=','prodlot_id')
                ], limit=1)[0]
        for this in self.browse(cr, uid, ids, context=context):
            product_id = this.product_id.id
            certificate_obj.update_certificate(cr, uid, 
                                               parent_id=product_id, parent_model='product.product', 
                                               child_id=this.id, child_model='stock.production.lot', 
                                               child_field_id=field_id, context=context)
        return True

stock_production_lot()

class certificate_template(osv.osv):
    _inherit = "certificate.template"

    _columns = {
        'product_id': fields.many2one('product.product', 'Product'),
        'product_ids': fields.many2many('product.product', 'certif_prod_rel', 'product_id', 'template_id', 'Products'),
    }
    
    # Update the object with the correct link #
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('product_ids') and vals.get('product_ids')[0][2]:
            object_ids = self.pool.get('ir.model').search(cr, uid, [
                                                                    ('model', '=', 'product.product'),
                                                                    ], limit=1, context=context)
            vals.update({'object_id': object_ids and object_ids[0] or False})
        return super(certificate_template, self).create(cr, uid, vals, context=context)
    
    ### Create Missing Certificate ### 
    def product_update_certificate_template(self, cr, uid, ids, fields, context=None):
        field_obj = self.pool.get('ir.model.fields')
        certificate_obj = self.pool.get('certificate')
        for template_data in self.browse(cr, uid, ids, context=context):
            for product_data in template_data.product_ids:
                for prodlot_data in product_data.prodlot_ids:
                    vals = {}
                    product_cert_ids = certificate_obj.search(cr, uid, [
                            ('template_id','=',template_data.id),
                            ('prodlot_id','=',prodlot_data.id),
                        ], context=context) 
                    if not product_cert_ids:
                        vals = {
                            'template_id': template_data.id,
                            'date_obtained': datetime.now(),
                            'validity':0,
                            'expiry_date': datetime.now(),
                            'prodlot_id': prodlot_data.id,
                            'state': 'close',
                        } 
                        certificate_obj.create(cr, uid, vals, context=context) 
        return True
    
certificate_template()

class certificate(osv.osv):
    _inherit = "certificate"
               
    _columns = {
        'product_id': fields.many2one('product.product', 'Product'),
        'prodlot_id': fields.many2one('stock.production.lot', 'Production Lot [Internal Reference]'),
    }
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        model_obj = self.pool.get('ir.model')
        if context.get('active_model',False) and context.get('active_model') == 'stock.production.lot':
            if context.get('active_id'):
                prodlot_id = context.get('active_id')
                vals.update({'prodlot_id': prodlot_id})
            if vals.get('prodlot_id') or vals.get('product_id'):
                object_ids = model_obj.search(cr, uid, [
                                                        ('model','=','stock.production.lot'),
                                                        ], limit=1, context=context)
                vals.update({'object_id': object_ids and object_ids[0] or False})
            else:
                vals.update({'object_id': 1})
        return super(certificate, self).create(cr, uid, vals, context)
    
    #####  Send Expiration Mail ######
    def prod_send_email(self, cr, uid, ids=False, context=None):
        result = True
        cert_ids = self.search(cr, uid, [
                                         ('state', '=', 'close'),
                                         ('send','=',False),
                                         ], context=context)
        for certificate in self.browse(cr, uid, cert_ids, context=context):
            product = certificate.product_id
            if product:
                self.write(cr, uid, certificate.id, {'send': True}, context=context)             
                result = super(base_certificate, self).certificate_email(cr, uid, product, [certificate.id], context)
        return result

certificate()

class stock_tracking(osv.osv):
    _inherit = "stock.tracking"
    
    _columns = {
        'responsible_id': fields.many2one('res.users','Responsable'),
        'sent': fields.boolean('Send'),
    }
    #####  Send Expiration Mail ######
    def expiry_packs_email(self, cr, uid, ids=False, context=None):
        model_data = self.pool.get('ir.model.data')
        mail_message = self.pool.get('mail.message')
        email_template_obj  = self.pool.get('email.template')
        stock_move = self.pool.get('stock.move')
        for pack_data in self.browse(cr, uid, ids, context=context):
            responsable = pack_data.responsible_id
            body = "Pack %s is expired\n  " % (pack_data.name)
            for serial_cert in pack_data.serial_cerificate_ids:
                child_pack = []
                state = serial_cert.state
                if state == 'close':
                    prodlot_id = serial_cert.prodlot_id
                    lot_move_ids = stock_move.search(cr, uid, [
                                    ('prodlot_id', '=', prodlot_id.id)
                                ], order='date desc', limit=1, context=context)
                    if lot_move_ids:
                        move = stock_move.browse(cr, uid, lot_move_ids[0], context=context)
                        tracking_id = move.tracking_id.id
                        body = body + "Certificate %s  is in pack : " % (serial_cert.name)
                        while tracking_id != pack_data.id:
                            tracking_data = self.browse(cr, uid, tracking_id, context=context)
                            parent_id = tracking_data.parent_id
                            body = body + "/ %s " % (tracking_data.name)
                            tracking_id = parent_id.id
                            
                    ## Manager information from Email Template ##
                    resp_email_id = model_data.get_object_reference(cr, uid, 'wilog_stock', 'expiration_pack')[1]
                    resp_email_data = email_template_obj.browse(cr, uid, resp_email_id, context=context)
                    mail_message.schedule_with_attach(cr, uid, 
                                                            resp_email_data.email_from, 
                                                            [str(resp_email_data.email_to)],
                                                            resp_email_data.subject, 
                                                            body, 
                                                            resp_email_data.model_id.model,
                                                            mail_server_id = resp_email_data.mail_server_id.id, 
                                                            context=context)
        return True
    
stock_tracking()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: