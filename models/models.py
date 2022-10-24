# -*- coding: utf-8 -*-
from odoo.addons.mail.wizard.mail_compose_message import MailComposer
from odoo import models, fields, api


# class mail_mail(models.TransientModel):
#     _inherit = 'mail.mail'
#     _description = ' Allow user to Compose a message with an attachment and send it'

class EmployeeMailComposer(models.TransientModel):

    _inherit = 'mail.compose.message'

    _description = 'Employee EMail Wizard that allow to send an Email with an attachment'

    # employee_ids = fields.Many2many('hr.employee', string='Employees')
    # @api.model
    # def send_mail(self,auto_commit=False):
    #     print("=====================self============================")
    #     print(self)

    #     for res in self.recieptient_ids:
    #         self.env['mail.message'].sudo().create({
    #             'message_type': "notification",
    #             'email_from': "Employee Email" ,  # ToDo:need to be changed to Employee Email
    #             'body': "an invitation for attending this event",
    #             'subject': "Invitation ",
    #             'model': "hr.employee",
    #             'res_id': res.id,
    #             'partner_ids': [res.id],
    #             'author_id': "HR Employee",  # ToDo:need to be changed to Email partner id
    #             'date': False,
    #             'notification_ids': [
    #                 (0, 0, {'res_partner_id': res.id, 'notification_type': 'inbox'})
    #             ]})
    #     self.env.cr.commit()

    #     res = super(MailComposer,self).send_mail(auto_commit=auto_commit)
    #     return res


