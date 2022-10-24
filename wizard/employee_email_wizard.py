import base64

from odoo.addons.mail.wizard.mail_compose_message import MailComposer
from odoo import models, fields, api


class EmployeeEMailWizard(models.TransientModel):

    _inherit = 'mail.compose.message'
    _description = 'Employee Email Wizard that allow to send an Email with an attachment'

    employee_ids = fields.Many2many('hr.employee', string="Notification Recipt")

    #ToDo:
    #1-security Done
    #2-models   Done
    #3-wizard   Done
    def get_mail_values(self, res_ids):
        self.ensure_one()
        results = dict.fromkeys(res_ids, False)
        rendered_values = {}
        mass_mail_mode = self.composition_mode == 'mass_mail'

        # render all template-based value at once
        if mass_mail_mode and self.model:
            rendered_values = self.render_message(res_ids)
        # compute alias-based reply-to in batch
        reply_to_value = dict.fromkeys(res_ids, None)
        if mass_mail_mode and not self.no_auto_thread:
            records = self.env[self.model].browse(res_ids)
            reply_to_value = records._notify_get_reply_to(default=self.email_from)

        blacklisted_rec_ids = set()
        if mass_mail_mode and issubclass(type(self.env[self.model]), self.pool['mail.thread.blacklist']):
            self.env['mail.blacklist'].flush(['email'])
            self._cr.execute("SELECT email FROM mail_blacklist WHERE active=true")
            blacklist = {x[0] for x in self._cr.fetchall()}
            if blacklist:
                targets = self.env[self.model].browse(res_ids).read(['email_normalized'])
                # First extract email from recipient before comparing with blacklist
                blacklisted_rec_ids.update(target['id'] for target in targets
                                           if target['email_normalized'] in blacklist)

        for res_id in res_ids:
            mail_values = {
                'subject': self.subject,
                'body': self.body or '',
                'parent_id': self.parent_id and self.parent_id.id,
                'partner_ids': [partner.id for partner in self.partner_ids],
                'attachment_ids': [attach.id for attach in self.attachment_ids],
                'author_id': self.author_id.id,
                'email_from': self.email_from,
                'record_name': self.record_name,
                'no_auto_thread': self.no_auto_thread,
                'mail_server_id': self.mail_server_id.id,
                'mail_activity_type_id': self.mail_activity_type_id.id,
            }
            mail_values['partner_ids'] = [employee.user_partner_id.id for employee in self.employee_ids]
            if mass_mail_mode and self.model:
                record = self.env[self.model].browse(res_id)
                mail_values['headers'] = record._notify_email_headers()
                # keep a copy unless specifically requested, reset record name (avoid browsing records)
                mail_values.update(notification=not self.auto_delete_message, model=self.model, res_id=res_id,
                                   record_name=False)
                # auto deletion of mail_mail
                if self.auto_delete or self.template_id.auto_delete:
                    mail_values['auto_delete'] = True
                # rendered values using template
                email_dict = rendered_values[res_id]
                mail_values['partner_ids'] += email_dict.pop('partner_ids', [])
                mail_values.update(email_dict)
                if not self.no_auto_thread:
                    mail_values.pop('reply_to')
                    if reply_to_value.get(res_id):
                        mail_values['reply_to'] = reply_to_value[res_id]
                if self.no_auto_thread and not mail_values.get('reply_to'):
                    mail_values['reply_to'] = mail_values['email_from']
                # mail_mail values: body -> body_html, partner_ids -> recipient_ids
                mail_values['body_html'] = mail_values.get('body', '')
                mail_values['recipient_ids'] = [(4, id) for id in mail_values.pop('partner_ids', [])]

                # process attachments: should not be encoded before being processed by message_post / mail_mail create
                mail_values['attachments'] = [(name, base64.b64decode(enc_cont)) for name, enc_cont in
                                              email_dict.pop('attachments', list())]
                attachment_ids = []
                for attach_id in mail_values.pop('attachment_ids'):
                    new_attach_id = self.env['ir.attachment'].browse(attach_id).copy(
                        {'res_model': self._name, 'res_id': self.id})
                    attachment_ids.append(new_attach_id.id)
                attachment_ids.reverse()
                mail_values['attachment_ids'] = \
                self.env['mail.thread'].with_context(attached_to=record)._message_post_process_attachments(
                    mail_values.pop('attachments', []),
                    attachment_ids,
                    {'model': 'mail.message', 'res_id': 0}
                )['attachment_ids']
                # Filter out the blacklisted records by setting the mail state to cancel -> Used for Mass Mailing stats
                if res_id in blacklisted_rec_ids:
                    mail_values['state'] = 'cancel'
                    # Do not post the mail into the recipient's chatter
                    mail_values['notification'] = False

            results[res_id] = mail_values
        return results

    def send_mail(self,auto_commit):
        return super(EmployeeEMailWizard, self).send_mail(auto_commit=auto_commit)

    def action_send_mail(self):
        self.partner_ids = [employee.user_partner_id.id for employee in self.employee_ids]
        self.send_mail(auto_commit=False)
        for employee in self.employee_ids:
            self.env['mail.message'].sudo().create({
                'message_type': "notification",
                'email_from': "business_support@ingaz.com.sa",
                'body': "an invitation for attending this event",
                'subject': "Invitation ",
                'model': "hr.employee",
                'res_id': employee.id,
                'partner_ids': [employee.user_partner_id.id],
                'author_id': False,  # ToDo:need to be changed to Email partner id
                'date': False,
                'notification_ids': [
                    (0, 0, {'res_partner_id': employee.user_partner_id.id, 'notification_type': 'inbox'})
                ]})
            self.env.cr.commit()

        res = super(MailComposer, self)

        return res


