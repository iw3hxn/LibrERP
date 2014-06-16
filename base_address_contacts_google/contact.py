# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 - TODAY DeneroTeam. (<http://www.deneroteam.com>)
#    Copyright (C) 2011 - TODAY Didotech Inc. (<http://www.didotech.com>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
from tools.translate import _
import pooler
import time
import gdata.contacts
import gdata.contacts.service
import gdata.contacts.client
import gdata.contacts.data
import tempfile

import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)


class google_contact_account(osv.osv):
    _name = "google.contact_account"
    _description = "Google Contact Account"
    _columns = {
        'name': fields.char('User', size=255, required=True, select=1),
        'password': fields.char('Password', size=255, required=True,),
        'active': fields.boolean('Active'),
        'last_sync_time': fields.datetime("Last Updated on "),
    }
    _order = 'name asc'
    _defaults = {
        'active': lambda *a: True,
    }
    
    def check_login(self, cr, uid, ids, context=None):
        account = self.browse(cr, uid, ids[0])
        test = gdata.contacts.service.ContactsService()
        test.email = account.name
        test.password = account.password
        try:
            test.ProgrammaticLogin()
            raise osv.except_osv(_("Connection OK"), _("Your login information is correct."))
        except gdata.service.CaptchaRequired:
            raise osv.except_osv(_("Error"), _("Required Captcha."))
        except gdata.service.BadAuthentication:
            raise osv.except_osv(_("Error"), _("Bad Authentication."))
        except gdata.service.Error:
            raise osv.except_osv(_("Error"), _("Login Error."))
        return self.write(cr, uid, ids[0], {'active': True})
    
    def create_google_contact(self, cr, uid, gc, contact, context=None):
        if not gc or not contact:
            return False
    
        if contact.last_name and contact.first_name:
            name = " ".join([contact.last_name, contact.first_name])
        elif contact.last_name:
            name = contact.last_name
        else:
            name = contact.first_name
        
        primary_email = contact.email and contact.email or ''
        primary_email = primary_email.replace(' ', '').replace("'", "").decode('utf-8')
        _logger.info(u"Contact %s going to create with email = %s" % (name, primary_email))
        if not primary_email:
            return False
        #--
        #--Check Any google contact exist with same email ?
        #--
        query = gdata.contacts.client.ContactsQuery(text_query=primary_email)
        feed = gc.GetContacts(q=query)
        if feed and len(feed.entry):
            _logger.info(u"Contact with email = %s exist" % (primary_email))
            _logger.info(u"FEED: total feed matched = %s" % (str(len(feed.entry))))
            
            feed_entry = None
            for entry in feed.entry:
                _e = None
                for _email in entry.email:
                    if _email.address and _email.address == primary_email:
                        _e = True
                        break
                if _e:
                    feed_entry = entry
                    break
            if feed_entry:
                if feed_entry.name:
                    _logger.info(u"FEED:\nName : %s" % (feed_entry.name.full_name.text))
                if not feed_entry.name:
                        feed_entry.name = gdata.data.Name()
                if contact.last_name and contact.first_name:
                    new_name = " ".join([contact.last_name, contact.first_name])
                elif contact.last_name:
                    new_name = contact.last_name
                else:
                    new_name = contact.first_name

                feed_entry.name.full_name = gdata.data.FullName(text=new_name)
                
                phone = None
                for _phone in feed_entry.phone_number:
                    if _phone.primary == 'true':
                        phone = _phone
                if not phone and feed_entry.phone_number:
                    phone = feed_entry.phone_number[0]
                
                if phone:
                    phone.text = contact.mobile
                    phone.rel = 'http://schemas.google.com/g/2005#mobile'
                else:
                    if contact.mobile:
                        feed_entry.phone_number.append(
                            gdata.data.PhoneNumber(text=contact.mobile, rel='http://schemas.google.com/g/2005#mobile', primary="true")
                        )
                try:
                    gc.Update(feed_entry)
                    self.pool.get('res.partner.address.contact').write(cr, uid, [contact.id], {'google_updated': feed_entry.updated.text, 'google_id': feed_entry.id.text})
                except:
                    _logger.info(u"UnknownError: Google Contact (%s) does not updated" % (contact.email))
                    return False
                return True
        
        new_contact = gdata.contacts.data.ContactEntry(name=gdata.data.Name(full_name=gdata.data.FullName(text=name)))
        new_contact.email.append(gdata.data.Email(address=primary_email,
                                 primary='true', rel=gdata.data.WORK_REL))
        
        feed = gc.GetGroups()
        group = filter(lambda g: g.title.text == 'System Group: My Contacts', feed.entry)[0]
        gmeminfo = gdata.contacts.data.GroupMembershipInfo(href=group.get_id())
        new_contact.group_membership_info.append(gmeminfo)
        if contact.mobile:
            new_contact.phone_number.append((gdata.data.PhoneNumber(text=contact.mobile, rel='http://schemas.google.com/g/2005#mobile', primary="true")))
        try:
            entry = gc.CreateContact(new_contact)
            if entry:
                self.pool.get('res.partner.address.contact').write(cr, uid, [contact.id], {'google_updated': entry.updated.text, 'google_id': entry.id.text})
                if contact.photo:
                    try:
                        tmp_image_file = tempfile.mktemp('%s_photo.jpg' % (str(contact.id)))
                        fp = open(tmp_image_file, 'wb+')
                        fp.write(contact.photo.decode('base64'))
                        gc.ChangePhoto(tmp_image_file, entry, content_type='image/jpeg')
                    finally:
                        fp.close()
        except:
            _logger.info(u"UnknownError: Google Contact (%s  <%s>) does not created" % (name, contact.email))
            return False
        return True

    def _google_sync_contractor_updates(self, cr, uid, ids=False, context=None):
        if context is None:
            context = {}
        google_accounts = self.search(cr, uid, [('active', '=', True)])
        for gac in google_accounts:
            self.openerp_google_sync(cr, uid, gac, context=context)
        return True

    def openerp_google_sync(self, cr, uid, account_id, context=None):
        if not account_id:
            return False
        g_account = self.pool.get('google.contact_account').browse(cr, uid, account_id, context=context)
        gc_client = gdata.contacts.client.ContactsClient(source='openerp-sync-google-1')
        gc_client.ClientLogin(g_account.name, g_account.password, gc_client.source)
        _logger.info(u"Login successfully to Google Contact: %s" % g_account.name)
        success_cb_ids = []
        search_filter = [('google_account_id', '=', g_account.id)]
        if g_account.last_sync_time:
            search_filter.append(('create_date', '>=', g_account.last_sync_time))
        
        #--
        #--create contacts to Google
        #--
        create_buffers = self.pool.get('google.contact_buffer').search(cr, uid, search_filter + [('action', '=', 'create')])
        for cb in self.pool.get('google.contact_buffer').browse(cr, uid, create_buffers, context=context):
            if self.create_google_contact(cr, uid, gc_client, cb.contact_id, context=context):
                self.pool.get('google.contact_buffer').unlink(cr, uid, [cb.id], context=context)
                #success_cb_ids.append(cb.id)

        #--
        #--update contacts to google
        #--
        update_buffer = self.pool.get('google.contact_buffer').search(cr, uid, search_filter + [('action', '=', 'update')])
        for cb in self.pool.get('google.contact_buffer').browse(cr, uid, update_buffer, context=context):
            if not cb.contact_id.google_id:
                self.create_google_contact(cr, uid, gc_client, cb.contact_id, context=context)
                continue
            try:
                feed_entry = gc_client.GetContact(cb.contact_id.google_id)
            except:
                _logger.info(u"UnknownError: Google contact does not exist with key = %s\nSo new google contact is created" % cb.contact_id.google_id)
                self.create_google_contact(cr, uid, gc_client, cb.contact_id, context=context)
                continue
            #feed_entry = feed_hash.get(cb.contact_id.google_id, False)
            if feed_entry:
                contact = cb.contact_id
                if not feed_entry.name:
                    feed_entry.name = gdata.data.Name()                
                if contact.last_name and contact.first_name:
                    new_name = " ".join([contact.last_name, contact.first_name])
                elif contact.last_name:
                    new_name = contact.last_name
                else:
                    new_name = contact.first_name

                feed_entry.name.full_name = gdata.data.FullName(text=new_name)
                email = None
                for _email in feed_entry.email:
                    if _email.primary == 'true':
                        email = _email
                if not email and feed_entry.email:
                    email = feed_entry.email[0]
                
                if email:
                    email.address = contact.email
                    
                phone = None
                for _phone in feed_entry.phone_number:
                    if _phone.primary == 'true':
                        phone = _phone
                if not phone and feed_entry.phone_number:
                    phone = feed_entry.phone_number[0]
                
                if phone:
                    phone.text = contact.mobile
                    phone.rel = 'http://schemas.google.com/g/2005#mobile'
                else:
                    if contact.mobile:
                        feed_entry.phone_number.append(
                            gdata.data.PhoneNumber(text=contact.mobile, rel='http://schemas.google.com/g/2005#mobile', primary="true")
                        )
                try:
                    gc_client.Update(feed_entry)
                    success_cb_ids.append(cb.id)
                except:
                    _logger.info(u"UnknownError: Google Contact (%s) does not updated" % (contact.work_email))

        #--
        #--Delete contacts to Google
        #--
        unlink_buffer = self.pool.get('google.contact_buffer').search(cr, uid, search_filter + [('action', '=', 'unlink')])
        for cb in self.pool.get('google.contact_buffer').browse(cr, uid, unlink_buffer, context=context):
            if not cb.google_id:
                continue
            try:
                feed_entry = gc_client.GetContact(cb.google_id)
                if feed_entry:
                    gc_client.Delete(feed_entry)
                    success_cb_ids.append(cb.id)
            except:
                _logger.info(u"UnknownError : Google can not able to delete contact with key = %s" % (cb.google_id))
                
        self.pool.get('google.contact_buffer').unlink(cr, uid, success_cb_ids, context=context)
        self.pool.get('google.contact_account').write(cr, uid, [account_id], {'last_sync_time': time.strftime("%Y-%m-%d %H:%M:%S")})
        return True


class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
        'google_account_id': fields.many2one('google.contact_account', 'Google Account'),
    }


class google_contact_buffer(osv.osv):
    _name = "google.contact_buffer"
    _description = "Sync Buffer"
    _columns = {
        'action': fields.selection([('unlink', 'Delete'), ('update', 'Update'), ('create', 'Create')], 'Action'),
        'contact_id': fields.many2one('res.partner.address.contact', 'Contacto'),
        'google_account_id': fields.many2one('google.contact_account', 'Google Account'),
        'google_id': fields.char('Google ID', size=255),
    }


### INHERITED ###
class res_partner_address_contact(osv.osv):
    _inherit = 'res.partner.address.contact'
    
    def _get_company_google_account(self, cr, uid, context):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id and user.company_id.google_account_id:
            return user.company_id.google_account_id.id
        else:
            google_account_ids = self.pool.get('google.contact_account').search(cr, uid, [], context=context)
            if google_account_ids:
                return google_account_ids[0]
        return False
        
    _columns = {
        'google_account_id': fields.many2one('google.contact_account', 'Google Account', size=255),
        'google_id': fields.char('Google ID', size=255),
        'google_updated': fields.char('Google updated', size=255),
        'active': fields.boolean("Active"),
    }
    
    _defaults = {
        'active': lambda *a: True,
        'google_account_id': _get_company_google_account,
    }
    
    def create(self, cr, uid, vals, context=None):
        vals.update({'active': True})
        contact_id = super(res_partner_address_contact, self).create(cr, uid, vals, context)
        contact = self.browse(cr, uid, contact_id)
        google_account_id = contact.google_account_id and contact.google_account_id.id or self._get_company_google_account(cr, uid, context=context)
        if google_account_id and not contact.google_id:
            pooler.get_pool(cr.dbname).get('google.contact_buffer').create(cr, uid, {
                'action': 'create',
                'contact_id': contact_id,
                'google_account_id': google_account_id
            })
            cr.commit()
        return contact_id
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(res_partner_address_contact, self).write(cr, uid, ids, vals, context=context)
        if 'google_updated' in vals:
            return res
        
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        
        for contact in self.browse(cr, uid, ids):
            if contact.active:
                google_account_id = contact.google_account_id and contact.google_account_id.id or self._get_company_google_account(cr, uid, context=context) or False
                if not google_account_id:
                    continue
                pooler.get_pool(cr.dbname).get('google.contact_buffer').create(cr, uid, {
                    'action': contact.google_id and 'update' or 'create',
                    'contact_id': contact.id,
                    'google_account_id': google_account_id,
                    'google_id': contact.google_id,
                })
                cr.commit()
        return res

    def unlink(self, cr, uid, ids, context=None):
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        for contact in self.browse(cr, uid, ids):
            google_account_id = contact.google_account_id and contact.google_account_id.id or self._get_company_google_account(cr, uid, context=context) or False
            if google_account_id:
                pooler.get_pool(cr.dbname).get('google.contact_buffer').create(cr, uid, {
                    'action': 'unlink',
                    'google_account_id': google_account_id,
                    'google_id': contact.google_id,
                })
                cr.commit()
        return super(res_partner_address_contact, self).unlink(cr, uid, ids, context=context)
