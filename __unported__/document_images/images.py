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

from openerp.osv import fields as old_fields
import logging
_logger = logging.getLogger(__name__)

import imghdr
import mimetypes
import urllib
import urllib2
import base64
try:
    from PIL import Image
except:
    _logger.warning("ERROR IMPORTING PIL, if not installed, please install it:"
    " get it here: https://pypi.python.org/pypi/PIL")
import io

from openerp import models, fields, api

def is_url_image(url):    
    mimetype,encoding = mimetypes.guess_type(url)
    return (mimetype and mimetype.startswith('image'))

def check_url(url):
    """Returns True if the url returns a response code between 200-300,
       otherwise return False.
    """
    try:
        headers={
            "Range": "bytes=0-10",
            "User-Agent": "MyTestAgent",
            "Accept":"*/*"
        }

        req = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(req)
        return response.code in range(200, 209)
    except Exception, ex:
        return False

def is_image_and_ready(url):
    return check_url(url) and is_url_image(url) or False

def get_image_data_from_url(url):
    u = urllib.urlopen(url)
    raw_data = u.read()
    u.close()
    return base64.encodestring(raw_data)

TYPE_IMAGES = ['png', 'jpg', 'gif', 'bmp', 'svg', 'jpeg']
FORMAT_IMAGES = ['PNG', 'JPG', 'GIF', 'BMP', 'SVG', 'JPEG']

class ir_attachment(models.Model):
    _inherit = 'ir.attachment'

    def _is_image_fnct(self, cr, uid, ids, name, args, context=None):
        if context is None:
            context = {}
        res = {}
        ctx = context.copy()
        ctx.update({'bin_size' : False})
        parameter_obj = self.pool.get('ir.config_parameter')
        location = parameter_obj.get_param(cr, uid, 'ir_attachment.location')
        for document in self.browse(cr, uid, ids, context=ctx):
            res[document.id] = False
            if document.type == 'url':
                is_image = False
                try:
                    is_image = is_image_and_ready(document.url)
                except IOError:
                    _logger.error("_read_file reading %s",full_path)
                res[document.id] = is_image
            elif document.type == 'binary':
                if location and document.store_fname:
                    full_path = self._full_path(cr, uid,
                                                location, document.store_fname)
                    is_image = False
                    try:
                        type = imghdr.what(full_path)
                        if type in TYPE_IMAGES:
                            is_image = True
                    except IOError:
                        _logger.error("_read_file reading %s",full_path)
                if not location:
                    is_image = False
                    try:
                        image_stream = io.BytesIO(document.datas.decode('base64'))
                        image = Image.open(image_stream)
                        if image.format in FORMAT_IMAGES:
                            is_image = True
                    except IOError:
                        _logger.error("_read_file reading %s", document.name)
                res[document.id] = is_image
        return res

    _columns = {
        'is_image': old_fields.function(_is_image_fnct,
                                    type='boolean',
                                    string='Is image',
                                    store=True,
                                    ),
    }

    image_data = fields.Binary('Image', compute='_get_image_data', store=False)

    @api.one
    def _get_image_data(self):
        image_data = False
        document = self.with_context({'bin_size' : False})
        if document.is_image:
            if document.type == 'binary':
                image_data = document.datas
            else:
                image_data = get_image_data_from_url(document.url)
        self.image_data = image_data

    color = fields.Integer('Color Index', default=0)

class document_images(models.AbstractModel):
    _name = 'document.images'
    _description = 'Attachment Images'
    
    image_ids = fields.One2many('ir.attachment', string='Images',
                                compute='_get_images')
    
    @api.model
    def _get_images_from_attachment(self, res_id, domain=None):
        attachment_obj = self.env['ir.attachment']
        domain += [
                   ('res_id', '=', res_id),
                   ('res_model', '=', self._name),
                   ('is_image', '=', True),
                   ]
        return attachment_obj.search(domain)

    @api.one
    def _get_images(self):
        self.image_ids = self._get_images_from_attachment(self.id, domain=[])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
