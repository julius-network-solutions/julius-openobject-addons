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
from tools.translate import _

class survey_question(osv.osv):
    _inherit = 'survey.question'
    _columns = {
        'score': fields.float('Score', digits=(16,2)),
    }
survey_question()

class survey_answer(osv.osv):
    _inherit = 'survey.answer'
    _columns = {
        'good_answer': fields.boolean('Good Answer'),
    }
survey_answer()

class survey_response(osv.osv):
    _inherit = 'survey.response'

    def _survey_score(self, cr, uid, ids, fields, args, context=None):
        res = {}
        if isinstance(ids,(long,int)):
            ids = [ids]
        for survey_resp in self.browse(cr, uid, ids, context=context):
            score = 0.0
            for question in survey_resp.question_ids:
                score += question.score
            res[survey_resp.id] = score
        return res
     
    _columns = {
        'score': fields.function(_survey_score, string='Score', type='float', digits=(16,2), method=True, store=True),
        'certificate_template_id': fields.many2one('certificate.template', 'Certificate Template'),
    }
                   
survey_response()

class survey_response_line(osv.osv):
    _inherit = 'survey.response.line'
    
    _columns = {
        'score': fields.float('Score', digits=(16,2)),
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (long,int)):
            ids = [ids]
        response_obj = self.pool.get('survey.response')
        for response_line in self.browse(cr, uid, ids, context=context):
            response_id = response_line.response_id.id
            response_obj._survey_score(cr, uid, [response_id], fields='score', args=None, context=context)
        return super(survey_response_line, self).write(cr, uid, ids, vals, context=context)
    
survey_response_line()

class survey_response_answer(osv.osv):
    _inherit = 'survey.response.answer'
     
    def create(self, cr, uid, vals, context=None):
        answer_obj = self.pool.get('survey.answer')
        response_obj = self.pool.get('survey.response.line')
        answer_data = answer_obj.browse(cr, uid, int(vals.get('answer_id')), context=context)
        if answer_data.good_answer:
            score = answer_data.question_id.score
            response_obj.write(cr, uid, vals.get('response_id'), {'score': score}, context=context)
        return super(survey_response_answer, self).create(cr, uid, vals, context=context)

survey_response_answer()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: