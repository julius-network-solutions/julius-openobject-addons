# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Julius Network Solutions SARL <contact@julius.fr>
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

import base64
from openerp.osv import orm, fields
import time
from openerp.tools.translate import _

trans=[(u'ￃﾩ','e'),
       (u'ￃﾨ','e'),
       (u'ￃﾠ','a'),
       (u'ￃﾪ','e'),
       (u'ￃﾮ','i'),
       (u'ￃﾯ','i'),
       (u'ￃﾢ','a'),
       (u'ￃﾤ','a')]
def tr(s):
    s= s.decode('utf-8')
    for k in trans:
        s = s.replace(k[0],k[1])
    try:
        res= s.encode('ascii','replace')
    except:
        res = s
    return res

class record:
    def __init__(self,global_context_dict):

        for i in global_context_dict:
            global_context_dict[i]= global_context_dict[i] and tr(global_context_dict[i])
        self.fields = []
        self.global_values = global_context_dict
        self.pre={'padding':'','seg_num1':'0','seg_num2':'1',
                  'seg_num3':'1','seg_num4':'1','seg_num5':'1','seg_num8':'1','seg_num_t':'9',
                   'flag':'0','flag1':'\n'
                           }
        self.init_local_context()

    def init_local_context(self):
        """
        Must instanciate a fields list, field = (name,size)
        and update a local_values dict.
        """
        raise "not implemented"

    def generate(self):
        res=''
        value=0
        go=True
        for field in self.fields :
            if field[0]=='section3':
                if self.global_values['section3']=='0':
                    go=False
                continue
            if field[0]=='section6':
                go=True
            if go:
                if self.pre.has_key(field[0]):
                    value = self.pre[field[0]]
                elif self.global_values.has_key(field[0]):
                    value = self.global_values[field[0]]
                else :
                    continue
                    #raise Exception(field[0]+' not found !')
                try:
                    res = res + c_ljust(value, field[1])
                except :
                    pass

        return res

class record_header(record):
    def init_local_context(self):
        self.fields=[
            #Header record start
            ('seg_num1',1),
            ('creation_date',6),('padding',12),
            ('institution_code',3),('app_code',2),('reg_number',10),('id_sender',11),('id_order_customer',11),('file_status',1),
            ('ver_code',1),('bilateral',12),('totalisation_code',1),('padding',4),('ver_subcode',1),('padding',52),('flag1',1)
            ]

class record_trailer(record):
    def init_local_context(self):
        self.fields=[
            #Trailer record start
            ('seg_num_t',1),
            ('tot_record',6),('tot_pay_order',6),
            ('tot_amount',15),('padding',100),('flag1',1),
            ]

class record_payline(record):
    def init_local_context(self):
        self.fields=[
            ('seg_num2',1),('sequence',4),('sub_div1',2),('order_exe_date',6),
            ('order_ref',16),('cur_code',3),('padding',1),('code_pay',1),('amt_pay',15),('padding',1),
            ('cur_code_debit_1',3),('padding',6),
            ('acc_debit',12),('padding',22),('indicate_date',1),('padding',34),('flag1',1),

            ('section3',1),

            ('seg_num6',1),('sequence4',4),('sub_div3',2),('order_cust_address',35),('padding',10),
            ('order_cust_bic',11),('padding',65),('flag1',1),

            ('seg_num7',1),('sequence5',4),('sub_div5',2),('benf_bank_name',35),('benf_bank_street',35),
            ('benf_bank_address',35),('padding',16),('flag1',1),

            ('section6',1),

            ('seg_num3',1),('sequence1',4),('sub_div6',2),('benf_accnt_no',34),('benf_name',35),('benf_address',35),
            ('type_accnt',1),('bank_country_code',2),('padding',14),('flag1',1),

            ('seg_num5',1),('sequence3',4),('sub_div07',2),('benf_address_continue',35),('benf_address_place',35),('padding',10),('comm_1',35),
            ('padding',6),('flag1',1),

            ('seg_num8',1),('sequence6',4),('sub_div8',2),('comm_2',35),('comm_3',35),
            ('comm_4',35),('padding',16),('flag1',1),

            ('seg_num4',1),('sequence2',4),('sub_div10',2),('order_msg',35),('method_pay',3),('charge_code',3),('padding',1),
            ('cur_code_debit',3),('padding',6),('debit_cost',12),('padding',1),('benf_country_code',2),('padding',55),('flag1',1),
            ]

def c_ljust(s, size):
    """
    check before calling ljust
    """
    s= s or ''
    if len(s) > size:
        s= s[:size]
    s = s.decode('utf-8').encode('latin1','replace').ljust(size)
    return s

class Log:
    def __init__(self):
        self.content= ""
        self.error= False
    def add(self,s,error=True):
        self.content= self.content + s
        if error:
            self.error= error
    def __call__(self):
        return self.content

def float2str(lst):
    return str(lst).rjust(16).replace('.','')

class payment_export(orm.TransientModel):
    
    _name = 'payment.export'
    
    _columns = {
        'payment_method': fields.many2one('payment.method', 'Payment Method'),
        'charges_code' : fields.many2one('charges.code', 'Charges Code', required=True),
    }
    
    def create_pay(self, cr, uid, ids, data, context=None):
        v = {}
#        v1 = {}
        v2 = {}
#        log = ''
        log = Log()
        blank_space= ' '

        seq = 0
        total = 0
        pay_order = ''
        currency_obj = self.pool.get('res.currency')
        order_obj = self.pool.get('payment.order')
        method_obj = self.pool.get('payment.method')
        partner_bank_obj = self.pool.get('res.partner.bank')
        bank_obj = self.pool.get('res.bank')
        pay_line_obj = self.pool.get('payment.line')
        partner_obj = self.pool.get('res.partner')
        zip_obj = self.pool.get('res.partner.zip')
        country_obj = self.pool.get('res.country')
        charges_obj = self.pool.get('charges.code')

        payment = order_obj.browse(cr, uid, ids[0], context=context)

        #Header Record Start
        v1 = {
            'uid': str(uid),
            'creation_date': time.strftime('%d%m%y'),#2-7
            'app_code': '51',#23-24
            'reg_number': payment.reference,#25-34
            'id_order_customer': payment.mode.bank_id.partner_id.vat or '',#vat number46-56
            'ver_code': '3',#58
            'bilateral': '',#59-70
            'totalisation_code': '0',
            'file_status': '',#57
            'ver_subcode': '1',#76
        }

        #look in the mode for insititute_code or protocol number
        cr.execute("SELECT m.bank_id from payment_order o inner join payment_mode m on o.mode=m.id and o.id in (%s) group by bank_id;"% (ids[0]))
        bank_id = cr.fetchone()

        if bank_id:
            bank = partner_bank_obj.browse(cr, uid, bank_id[0], context)
            if not bank:
                return {'note':'Please Provide Bank for the Ordering Customer.', 'reference': payment.id, 'pay': False, 'state':'failed' }
            v1['institution_code'] = bank.institution_code #20-22
            if not v1['institution_code']:
                return {'note':'Please provide Institution Code number for the ordering customer.', 'reference': payment.id, 'pay': False, 'state':'failed' }
        pay_header = record_header(v1).generate()
        #Header Record End

        pay_line_id = pay_line_obj.search(cr, uid, [('order_id','=',ids[0])])

        if not payment.line_ids:
            return {'note':'Wizard can not generate export file: there are no payment lines.', 'reference': payment.id, 'pay': False, 'state':'failed' }

        pay_line = pay_line_obj.read(cr, uid, pay_line_id,['date','company_currency','currency','partner_id','amount','bank_id','move_line_id','name','info_owner','info_partner','communication','communication2'])

        for pay in pay_line:

            #sub1 Start
            seq = seq+1
            v = {
                'sequence': str(seq).rjust(4).replace(' ','0'),#2-5
                'sub_div1': '01',#6-7'
            }

            if pay['date']:
                v['order_exe_date'] = time.strftime('%d%m%y', time.strptime(pay['date'],"%Y-%m-%d"))
            else:
                v['order_exe_date'] = ''#8-13

            v['order_ref'] = pay['name']#14-29
            if pay['amount'] == 0.0:
                return {'note':'Payment amount in payment lines should not be zero.', 'reference': payment.id, 'pay': False, 'state':'failed'}
            v['amt_pay'] = float2str('%.2f'%pay['amount'])#35-49

            default_cur = ''
            if pay['company_currency']:
                default_cur = currency_obj.browse(cr,uid,pay['company_currency'][0]).code

            v['cur_code'] = default_cur#30-32

            cur_code = ''
            if pay['currency']:
                cur_code = currency_obj.browse(cr,uid,pay['currency'][0]).code
            if default_cur != pay['currency'][1]:
                v['code_pay'] = 'D'#34
                v['cur_code_debit_1'] = cur_code # 51-53
                v['cur_code_debit'] = cur_code #sub 10 50-52
            else:
                v['code_pay'] = 'C'
                v['cur_code_debit_1'] = default_cur
                v['cur_code_debit'] = default_cur

            total = total + pay['amount']

            v['acc_debit'] = bank.acc_number # 60-71
            if bank.state == 'iban':
                v['acc_debit'] = partner_bank_obj.get_bban_from_iban(cr, uid, [bank.id])[bank.id]

            if not v['acc_debit']:
                return {'note':'Please Provide Bank Account Number for the Ordering Customer.', 'reference': payment.id, 'pay': False, 'state':'failed' }
            v['indicate_date'] = ''
            #sub1 End
            # subdivision3 if its a foreign payment taking place.
            cust_country = benf_country = section3 = False
            order_cust_address_obj = payment.mode.bank_id.partner_id

            if order_cust_address_obj.address:
                for ads in order_cust_address_obj.address:
                    if ads.type == 'default':
                        cust_country = ads.country_id and ads.country_id.code or False
                        if cust_country:
                            order_country_name = ads.country_id.name
                            order_state = ads.state_id and ads.state_id.name or ''
                            if 'zip_id' in ads:
                                obj_zip_city = ads.zip_id and zip_obj.browse(cr, uid, ads.zip_id.id, context=context) or ''
                                order_zip = obj_zip_city and obj_zip_city.name or ''
                                order_city = obj_zip_city and obj_zip_city.city or  ''
                            else:
                                order_zip = ads.zip and ads.zip or ''
                                order_city = ads.city and ads.city or  ''

            v['benf_address'] = v['benf_name'] = v['benf_address_place'] = ''

            if pay['partner_id']:
                part_obj = partner_obj.browse(cr, uid, pay['partner_id'][0], context=context)
                v['benf_name'] = part_obj.name # 42-76 sub div 06
                if part_obj.address:
                    for ads in part_obj.address:
                        if ads.type == 'default':
                            adrs = ads.street or ''
                            adrs += (ads.street2 or '')
                            v['benf_address'] = adrs #sub div 06 77-111
                            benf_country = ads.country_id and ads.country_id.code or False
                            if benf_country:
                                benf_country_name = ads.country_id.name
                                v['benf_country_code'] = ads.country_id.code#72-73 sub div 10
                                benf_state = ads.state_id and ads.state_id.name or ''
                                if 'zip_id' in ads:
                                    obj_zip_city = ads.zip_id and zip_obj.browse(cr,uid,ads.zip_id.id) or ''
                                    benf_zip = obj_zip_city and obj_zip_city.name or ''
                                    benf_city = obj_zip_city and obj_zip_city.city or  ''
                                else:
                                    benf_zip = ads.zip and ads.zip or ''
                                    benf_city = ads.city and ads.city or  ''
                                ct_st_ctry = str(benf_city) + ' ' + str(benf_state) + ' ' + str(benf_country_name)
                                v['benf_address_place'] = "*" + str(benf_country).rjust(3) + blank_space + str(benf_zip).rjust(6) + str(ct_st_ctry).rjust(24)#sub div 07 43-77
                            else:
                                return {'note':'Please Provide Country in Payment Line for \nPartner:' + str(pay['partner_id'][1]) + ' Ref:'+ str(pay['name']), 'reference': payment.id, 'pay': False, 'state':'failed' }
                        break

            v['section3'] = '0'
            if cust_country and benf_country:
                if cust_country != benf_country:
                    # Sub division3- Start
                    v['seg_num6'] = '1'
                    v['section3'] = '1'
                    v['sequence4'] = str(seq).rjust(4).replace(' ','0')#2-5
                    v['sub_div3'] = '03'#6-7
                    v['order_cust_address'] = ''#8-42
                    ct_st_ctry = str(order_city) + ' ' + str(order_state) + ' ' + str(order_country_name)
                    v['order_cust_address'] = "*" + str(cust_country).rjust(3) + blank_space + str(order_zip).rjust(6) + str(ct_st_ctry).rjust(24)
                    v['order_cust_bic'] = ''#53-63
                    if payment.mode.bank_id.bank:
                        v['order_cust_bic'] = payment.mode.bank_id.bank.bic or ''
                    section3 = True
                    # Sub division3- End

            # if section 3 exists ,section5 comes into existance.
            if section3:
                if pay['bank_id']:
                    #sub division5 -start
                    v['sequence5'] = str(seq).rjust(4).replace(' ','0')#2-5
                    v['sub_div5'] = '05'#6-7
                    v['seg_num7'] = '1'
                    bank_partner = partner_bank_obj.read(cr, uid, pay['bank_id'][0], context=context)
                    v['benf_bank_name'] = v['benf_bank_street'] = v['benf_bank_address'] = ''
                    if bank_partner['bank']:
                        bank_main = bank_obj.read(cr, uid, bank_partner['bank'][0], context=context)
                        v['benf_bank_name'] = bank_main['name'] #8-42
                        v['benf_bank_street'] = (bank_main['street'] or '') + blank_space + (bank_main['street2'] or '') # 43-77
                        v['benf_bank_address'] = '' #78-112
                        ctry_code = ''
                        ct_st_ctry = str(bank_main['city'] or '') + ' ' + str(bank_main['state'][1]) + ' ' + str(bank_main['country'][1])
                        if bank_main['country']:
                            code_country = country_obj.read(cr,uid,bank_main['country'][0], ['code'], context=context) #get bank address of counrty for pos 113-114 sub06
                            ctry_code = v['bank_country_code'] = code_country['code'] # 113-114 in sub div6
                        v['benf_bank_address'] = "*" + str(ctry_code).rjust(3) + blank_space + str(bank_main['zip']).rjust(6) + str(ct_st_ctry).rjust(24)
    
                #sub division5 -End
    
            #sub6 start
            v['sequence1'] = str(seq).rjust(4).replace(' ','0') #2-5
            v['sub_div6'] = '06' #6-7
    
            if pay['bank_id']:
                bank1 = partner_bank_obj.read(cr, uid, pay['bank_id'][0], context=context)#searching pay line bank account number
                v['benf_accnt_no'] = bank1['acc_number'] # 8-41
                if bank1['state'] == 'bank':
                    v['type_accnt'] = '2' # 112
                elif bank1['state'] == 'pay_iban':
                    v['type_accnt'] = '1'
                else:
                    v['type_accnt'] = ''
            else:
                return {'note':'Please Provide Bank Account in Payment Line for \nPartner:'+str(pay['partner_id'][1])+' Ref:'+str(pay['name']), 'reference': payment.id, 'pay': False, 'state':'failed' }
    
            v['bank_country_code'] = ''
    
            if bank1['bank']:
                bank2 = bank_obj.read(cr, uid, bank1['bank'][0], context=context)
                if bank2['country']:
                    code_country = country_obj.read(cr, uid, bank2['country'][0], ['code'], context=context)
                    v['bank_country_code'] = code_country['code'] # 113-114
    
            #sub6 End
    
            #sub7 and sub8 -start
            v['sequence3'] = str(seq).rjust(4).replace(' ','0') #2-5 sub7
            v['sub_div07'] = '07'#6-7 sub7
            v['sequence6'] = str(seq).rjust(4).replace(' ','0') #2-5 sub8
            v['sub_div8'] = '08' #6-7 sub8
            v['benf_address_continue'] = '' #8-42 sub7
            v['comm_1'] = v['comm_2'] = v['comm_3'] = v['comm_4'] = ''
            if pay['communication']:
                if len(pay['communication']) >= 36:
                    v['comm_1'] = pay['communication'][:35] # 88-122 sub7
                    v['comm_2'] = pay['communication'][35:] # 8-42 sub8
                else:
                    v['comm_1'] = pay['communication']# 88-122 sub7
            if pay['communication2']:
                if len(pay['communication2']) >= 36:
                    v['comm_3'] = pay['communication2'][:35] # 43-77 sub8
                    v['comm_4'] = pay['communication2'][35:] # 78-112 sub8
                else:
                    v['comm_3'] = pay['communication2'] # 43-77 sub8
            #sub7 and sub 8 -End
    
            #seg10 start
            v['sequence2'] = str(seq).rjust(4).replace(' ','0') #2-5
            v['sub_div10'] = '10' #6-7
            v['order_msg'] = '' #msg from order customer to order cutomer bank 8-42
            v['method_pay'] = '' #43-45
            if data['payment_method']:
                v['method_pay'] = method_obj.browse(cr, uid, data['payment_method'], context=context).name
            v['charge_code'] = charges_obj.browse(cr, uid, data['charges_code'], context=context).name #46-48
            v['debit_cost'] = '000000000000' #field will only fill when ordering customer account debitted with charges if not field will contain blank or zero
            #sub10 End
            pay_order = pay_order + record_payline(v).generate()
    
        #Trailer Record Start
        v2['tot_record'] = v2['tot_pay_order']=str(seq)
        v2['tot_amount'] = float2str('%.2f'%total)
        pay_trailer = record_trailer(v2).generate()
        #Trailer Record End
    
        try:
            pay_order = pay_header + pay_order + pay_trailer
        except Exception,e :
            log= log +'\n'+ str(e) + 'CORRUPTED FILE !\n'
            raise
        log.add("Successfully Exported\n--\nSummary:\n\nTotal amount paid : %.2f \nTotal Number of Payments : %d \n-- " %(total,seq))
    
        order_obj.set_done(cr, uid, payment.id, context=context)
        return {'note':log(), 'reference': payment.id, 'pay': base64.encodestring(pay_order), 'state':'succeeded'}
    
    def log_create(self, cr, uid, ids, context=None):
        history_obj = self.pool.get('account.pay')
        read_data = self.read(cr, uid, ids, [], context=context)
        ids = context.get('active_ids', [])
        data = self.create_pay(cr, uid, ids, read_data, context=context)

        history_id = history_obj.create(cr, uid, {
                'payment_order_id': data['reference'],
                'note': data['note'],
                'file': data['pay'] and base64.encodestring(data['pay'] or False),
                'state': data['state'],
            })

        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        mod_id = mod_obj.search(cr, uid, [('name', '=', 'action_account_pay_tree')])[0]
        res_id = mod_obj.read(cr, uid, mod_id, ['res_id'])['res_id']
        act_win = act_obj.read(cr, uid, res_id, [])
        act_win['domain'] = [('id', '=', history_id)]
        act_win['name'] = _('Export Payment')
        return act_win

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
