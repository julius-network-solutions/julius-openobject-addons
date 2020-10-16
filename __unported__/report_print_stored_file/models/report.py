# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015-Today Julius Network Solutions SARL <contact@julius.fr>
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

from openerp import models, api, fields
import base64
import tempfile
from contextlib import closing
import os
import logging
_logger = logging.getLogger(__name__)
from pyPdf import PdfFileWriter, PdfFileReader


class ir_action_report(models.Model):
    _inherit = 'ir.actions.report.xml'
    direct_pdf = fields.Binary('Direct PDF stored file')
    set_direct_pdf = fields.Selection([
                                       ('before', 'Before'),
                                       ('after', 'After'),
                                       ('merge', 'Merge'),
                                       ], 'Set PDF stored file',
                                      default='after')


class Report(models.Model):
    _inherit = 'report'

    @api.model
    def add_direct_pdf(self, direct_pdf, temporary_files):
        """
        Add the direct pdf in the temporary files to be merged
        """
        att = base64.decodestring(direct_pdf)
        content_file_fd, content_file_path = tempfile.\
            mkstemp(suffix='.pdf', prefix='direct_pdf.tmp.')
        temporary_files.append(content_file_path)
        with closing(os.fdopen(content_file_fd, 'w')) as content_file:
            content_file.write(att)
        return temporary_files

    @api.v7
    def get_pdf(self, cr, uid, ids, report_name, html=None,
                data=None, context=None):
        """This method generates and returns pdf version of a report.
        """
        if context is None:
            context = {}
        result = super(Report, self).\
            get_pdf(cr, uid, ids, report_name, html=html, data=data,
                    context=context)
        # Get the ir.actions.report.xml record we are working on.
        report = self._get_report_from_name(cr, uid, report_name)
        if not report.direct_pdf:
            return result
        temporary_files = []
        if report.set_direct_pdf == 'before':
            temporary_files = self.add_direct_pdf(cr, uid, report.direct_pdf,
                                                  temporary_files,
                                                  context=context)
        content_file_fd, content_file_path = tempfile.\
            mkstemp(suffix='.pdf', prefix='result.tmp.')
        temporary_files.append(content_file_path)
        with closing(os.fdopen(content_file_fd, 'w')) as content_file:
            content_file.write(result)
        if report.set_direct_pdf in ('after', 'merge'):
            temporary_files = self.add_direct_pdf(cr, uid, report.direct_pdf,
                                                  temporary_files,
                                                  context=context)
        if report.set_direct_pdf == 'merge':
            entire_report_path = self._merge_files_pdf(temporary_files)
        else:
            entire_report_path = self._merge_pdf(temporary_files)
        with open(entire_report_path, 'rb') as pdfdocument:
            result = pdfdocument.read()
        # Manual cleanup of the temporary files
        for temporary_file in temporary_files:
            try:
                os.unlink(temporary_file)
            except (OSError, IOError):
                _logger.error('Error when trying to remove '
                              'file %s' % temporary_file)
        return result

    @api.v8
    def get_pdf(self, records, report_name, html=None, data=None):
        return self._model.get_pdf(self._cr, self._uid, records.ids, report_name,
                                   html=html, data=data, context=self._context)

    def _merge_files_pdf(self, documents):
        """Merge PDF files into one.

        :param documents: list of path of pdf files
        :returns: path of the merged pdf
        """
        writer = PdfFileWriter()
        
        streams = []  # We have to close the streams *after* PdfFilWriter's call to write()

        docs = {}
        direct = False
        # Open and read all documents
        for document in documents:
            pdfreport = file(document, 'rb')
            streams.append(pdfreport)
            reader = PdfFileReader(pdfreport)
            num_page = reader.getNumPages()
            docs.setdefault(num_page, [])
            docs[num_page].append(reader)
            direct = reader

        # Get all the document to merge
        numbers = docs.keys()
        documents = {}
        page_to_merge = range(1, max(numbers) + 1)
        for number in page_to_merge:
            documents.setdefault(number, [])
            for number2 in page_to_merge:
                if number2 >= number:
                    if docs.get(number2):
                        documents[number].extend(docs.get(number2))

        previous_number = 0
        for number in sorted(documents.keys()):
            # Find if need to merge or not
            docs = documents.get(number)
            len_documents = len(docs)
            # Find if there is many files merge them
            if len_documents > 1:
                previous_doc = False
                # Put the direct_pdf in the back
                docs2 = [direct]
                for doc in docs:
                    if direct != doc:
                        docs2.append(doc)
                # Merge pages
                for doc in docs2:
                    if previous_doc:
                        page_number = doc.getPage(number - 1)
                        page_number.mergePage(previous_doc.getPage(number - 1))
                        writer.addPage(page_number)
                    previous_doc = doc
            else:
                # There is only one file so add it directly
                for page in range(previous_number, number):
                    writer.addPage(docs[0].getPage(page))
            previous_number = number

        merged_file_fd, merged_file_path = tempfile.mkstemp(suffix='.html', prefix='report.merged.tmp.')
        with closing(os.fdopen(merged_file_fd, 'w')) as merged_file:
            writer.write(merged_file)

        for stream in streams:
            stream.close()

        return merged_file_path

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
