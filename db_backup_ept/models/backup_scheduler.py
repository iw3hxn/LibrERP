# -*- coding: utf-8 -*-
# © 2014 Emipro Technologies (www.emiprotechnologies.com)
# © 2015-2018 Didotech srl (www.didotech.com)

import codecs
import ftplib
import logging
import os
import socket
import tarfile
import threading
import time
import xmlrpclib
from datetime import datetime

import pooler
import tools
from openerp.osv import orm, fields
from tools.translate import _

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


def ftp_login(ept_ftp_host, ept_ftp_username, ept_ftp_password):
    ftp = ftplib.FTP()
    server = ept_ftp_host.split(':')
    ftp_host = server[0]
    if len(server) == 2:
        ftp_port = ept_ftp_host.split(':')[1]
        if ftp_port:
            ftp_port = int(ftp_port)
    else:
        ftp_port = 21
    ftp.connect(ftp_host, ftp_port)
    ftp.login(ept_ftp_username, ept_ftp_password)
    return ftp


def ftp_connect(ept_ftp_host, ept_ftp_username, ept_ftp_password, to_ept_location):
    s = None
    try:
        s = ftp_login(ept_ftp_host, ept_ftp_username, ept_ftp_password)
    except Exception, e:
        raise orm.except_orm(_('FTP Authentication Fail!'), _(
            'Please check the account setting for Auto FTP backup. Some details may be missing/Incorrect.'))
    if s:
        dir = ''
        try:
            dir = s.cwd(to_ept_location)
        except Exception, ex:
            raise orm.except_orm(_(''), _('FTP Connection test successfully. But Specified directory is not locate.'))

        if "250 CWD" in dir:
            return True

    return False


def execute(connector, method, *args):
    res = False
    try:
        res = getattr(connector, method)(*args)
    except socket.error, e:
            raise e
    return res


addons_path = tools.config['addons_path'] + '/db_backup_ept/DBbackups'


class DbBackupEpt_Thread(threading.Thread):

    def __init__(self, cr, uid, context=None):
        # Inizializzazione superclasse
        threading.Thread.__init__(self)
        self.cr = pooler.get_db(cr.dbname).cursor()
        self.db_backup_ept_obj = pooler.get_pool(self.cr.dbname).get('db.autobackup.ept')
        self.start_time = datetime.now()
        self.uid = uid
        self.context = context

    def run(self):

        conf_ids = self.db_backup_ept_obj.search(self.cr, self.uid, [('active', '=', 'True')], context=self.context)

        self.db_backup_ept_obj.delete_obsolete_backups(self.cr, self.uid, conf_ids, self.context)

        for rec in self.db_backup_ept_obj.browse(self.cr, self.uid, conf_ids, self.context):
            db_list = self.db_backup_ept_obj.get_db_list(self.cr, self.uid, [], rec.host, rec.port)
            if rec.name in db_list:
                try:
                    if not os.path.isdir(rec.backup_dir):
                        os.makedirs(rec.backup_dir)
                except:
                    raise
                self.db_backup_ept_obj.ept_backup(self.cr, self.uid, [rec.id], rec.name, rec.backup_dir, True, rec.ftp_enable, rec.FTP_id, rec, rec.keep_backup_local, self.context)
                # self.hv_backup(cr, user,[Bak conf ID], db_name, db_bkp_dir,AUTO,FTP)
                self.cr.commit()
        if not self.cr.closed:
            self.cr.close()
        end_time = datetime.now()
        duration_seconds = (end_time - self.start_time).seconds
        duration = '{min}m {sec}sec'.format(min=duration_seconds / 60,
                                            sec=duration_seconds - duration_seconds / 60 * 60)
        _logger.info(u'Execution time in: {0}'.format(duration))
        return True

    def terminate(self):
        if not self.cr.closed:
            self.cr.close()
        return super(DbBackupEpt_Thread, self).terminate()


class db_backup_ept(orm.Model):
    _name = 'db.autobackup.ept'
  
    def get_db_list(self, cr, user, ids, host='localhost', port='8069', context=None):
        uri = 'http://' + host + ':' + port
        conn = xmlrpclib.ServerProxy(uri + '/xmlrpc/db')
        db_list = execute(conn, 'list')
        return db_list
        
    def get_addons_path(self, cr, user, context=None):
        addons_path = tools.config['addons_path'] + '/db_backup_ept/DBbackups'
        return addons_path

    def _count_backups(self, cr, uid, ids, field_name, arg, context):
        result = {}

        for backup in self.browse(cr, uid, ids, context):
            result[backup.id] = len(backup.history_line)

        return result

    _columns = {
        'name': fields.char('Database', size=100, required='True', help='Database you want to schedule backups for'),
        'host': fields.char('Host', size=255, required='True'),
        'port': fields.char('Port', size=10, required='True'),
        'history_line': fields.one2many('db.backup.line', 'backup_id', 'History', readonly=True),
        'active': fields.boolean('Active'),
        'ftp_enable': fields.boolean('FTP Enable ?'),
        'keep_backup_local': fields.boolean(
            'Keep Backup on Local Path?',
            help="Check this field if you want to keep database backup in Local directory. If this is unchecked then database backup will only be able transfer to FTP server."
        ),
        'FTP_id': fields.many2one('ept.ftpbackup', "FTP"),
        'backup_dir': fields.char(
            'Backup Directory', size=512, help='Absolute path for storing the backups', required='True'
        ),
        'ept_enable_email_notification': fields.boolean('ept_enable_email_notification'),
        'email_ids': fields.char(
            'Email Ids', size=1024,
            help='Add email id for FTP backup schedule notification. Separate Email Ids by comma(,). '
        ),
        'user_ids': fields.many2many(
            'res.users', 'db_backup_users_rel', 'backup_id', 'user_id',
            'users', help='select user for email notification.'
        ),
        'backups_to_keep': fields.integer('Backups to keep', help="If set to 0 backups will not be deleted"),
        'backups_on_disk': fields.function(_count_backups, string='Backups on disk', method=True, type='integer')
    }

    _defaults = {
        'backup_dir': lambda *a: addons_path,
        'host': lambda *a: 'localhost',
        'port': lambda *a: '8069',
        'active': True,
    }
    
    def _check_db_exist(self, cr, user, ids, context=None):
        for record in self.browse(cr, user, ids, context):
            db_list = self.get_db_list(cr, user, ids, record.host, record.port)
            if record.name in db_list:
                return True
        return False
    
    _constraints = [
        (_check_db_exist, 'Error!!! No such database exist.', [])
    ]
    
    def __init__(self, cr, pool):
        super(db_backup_ept, self).__init__(cr, pool)
        self._pg_psw_env_var_is_set = False
    
    def schedule_backup(self, cr, uid, context=None):
        final_process = DbBackupEpt_Thread(cr, uid, context)
        final_process.start()

        # conf_ids = self.search(cr, uid, [('active', '=', 'True')], context=context)
        #
        # self.delete_obsolete_backups(cr, uid, conf_ids, context)
        #
        # for rec in self.browse(cr, uid, conf_ids, context):
        #     db_list = self.get_db_list(cr, uid, [], rec.host, rec.port)
        #     if rec.name in db_list:
        #         try:
        #             if not os.path.isdir(rec.backup_dir):
        #                 os.makedirs(rec.backup_dir)
        #         except:
        #             raise
        #         self.ept_backup(
        #             cr, uid, [rec.id], rec.name, rec.backup_dir, True, rec.ftp_enable,
        #             rec.FTP_id, rec, rec.keep_backup_local, context)
        #         # self.hv_backup(cr, user,[Bak conf ID], db_name, db_bkp_dir,AUTO,FTP)
        return True

    def delete_obsolete_backups(self, cr, uid, ids, context):
        for backup in self.browse(cr, uid, ids, context):
            if backup.backups_to_keep and len(backup.history_line) > backup.backups_to_keep:
                backups_to_delete = backup.history_line[(backup.backups_to_keep - 1):]
                for condemned in backups_to_delete:
                    _logger.info(u'Deleting backup {} ...'.format(condemned.path))
                    try:
                        os.unlink(condemned.path)
                    except:
                        pass
                    condemned.unlink()
        return True

    def _set_pg_psw_env_var(self):
        #if os.name != 'nt' and not os.environ.get('PGPASSWORD', ''):
        if tools.config.get('db_password'):
            os.environ['PGPASSWORD'] = tools.config['db_password']
        #    self._pg_psw_env_var_is_set = True
        #else:
        #    self._pg_psw_env_var_is_set = True
        self._pg_psw_env_var_is_set = True

    def _unset_pg_psw_env_var(self):
        #if os.name == 'nt' and self._pg_psw_env_var_is_set:
        os.environ['PGPASSWORD'] = ''
    
    def ept_backup(self, cr, uid, ids, db_name, bkup_dir, automatic, ftp_enable, FTP_id, bak_conf, keep_backup_local, context=None):
        context = context or self.pool['res.users'].context_get(cr, uid)
        self._set_pg_psw_env_var()

        bkp_file_name = '%s_%s.sql' % (db_name, time.strftime('%Y%m%d_%H_%M_%S'))
        tar_file_name = '%s_%s.tar.gz' % (db_name, time.strftime('%Y%m%d_%H_%M_%S'))

        bck_file_path = os.path.join(bkup_dir, bkp_file_name)

        # - - - - - - - - - - - - - - - - - - - -
        # Build the pg_dump command line
        # - - - - - - - - - - - - - - - - - - - -
        cmd = ['pg_dump', '--format=p', '--no-owner']

        # Get DB connection parameters from OpenERP configuration
        if tools.config['db_user']:
            cmd.append('--username=' + tools.config['db_user'])
        # end if
        if tools.config['db_host']:
            cmd.append('--host=' + tools.config['db_host'])
        # end if
        if tools.config['db_port']:
            cmd.append('--port=' + str(tools.config['db_port']))
        # end if

        # Add the output file path
        cmd.append("--file=" + bck_file_path)

        # Add the DB name
        cmd.append(db_name)

        # Run the backup
        stdin, stdout = tools.exec_pg_command_pipe(*tuple(cmd))
        stdin.close()
        data = stdout.read()  # NB: the this is not the data from the DB dump, just the pg_dump output text
        res = stdout.close()

        tar_file_path = os.path.join(bkup_dir, tar_file_name)
        tar_obj = tarfile.open(tar_file_path, 'w:gz')
        tar_obj.add(bck_file_path, bkp_file_name)
        tar_obj.close()

        user_id = None
        user_name = ''
        backup_status = ''
        if not automatic:
            user_id = uid
            user_name = self.pool['res.users'].browse(cr, uid, uid, context=context).name
        if res:
            _logger.error(u"DUMP DB: %s failed\n%s" % (db_name, data))
            for obj in self.browse(cr, uid, ids, context):
                self.pool['db.backup.line'].create(cr, uid, {
                    'backup_id': obj.id,
                    'name': obj.name,
                    'date_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'done_by': user_id,
                    'message': 'Could not create back up of database. Backup Failed.',
                    'automatic': automatic,
                })
                backup_status = 'Could not create back up of database. Backup Failed.'
            self._unset_pg_psw_env_var()
            return False
        else:
            _logger.info(u"DUMP DB: %s" % (db_name))
            if ftp_enable:
                if FTP_id:
                    ftpbackup_obj = self.pool['ept.ftpbackup']
                    ept_ftp = ftpbackup_obj.browse(cr, uid, FTP_id.id, context)
                    if not ept_ftp.ept_ftp_host or not ept_ftp.ept_ftp_username or \
                            not ept_ftp.ept_ftp_password or not ept_ftp.to_ept_location:
                        for obj in self.browse(cr, uid, ids):
                            self.pool['db.backup.line'].create(cr, uid, {
                                'backup_id': obj.id,
                                'name': tar_file_name,
                                'date_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                                'done_by': uid,
                                'message': 'Could not create back up of database. Backup Failed. Invalid FTP Credentials',
                                'automatic': automatic,
                            }, context)
                        backup_status = 'Could not create back up of database. Backup Failed. Invalid FTP Credentials'
                        os.remove(bck_file_path)
                        return True
                    try:
                        if ept_ftp.is_ftp_active:
                            ftp = ftp_login(ept_ftp.ept_ftp_host, ept_ftp.ept_ftp_username, ept_ftp.ept_ftp_password)
                            # s = ftplib.FTP(ept_ftp.ept_ftp_host, ept_ftp.ept_ftp_username, ept_ftp.ept_ftp_password)  # Connect
                            f = open(tar_file_path, 'rb')                # file to send

                            remote_file_path = os.path.join(ept_ftp.to_ept_location, tar_file_name)
                            ftp.storbinary('STOR ' + remote_file_path, f)         # Send the file
                            f.close()                                # Close file and FTP
                            ftp.quit()
                            for obj in self.browse(cr, uid, ids, context):
                                backup_status = 'Backup completed successfully at Remote FTP path : %s/%s.' % (ept_ftp.to_ept_location, tar_file_name)
                                self.pool['db.backup.line'].create(cr, uid, {
                                    'backup_id': obj.id,
                                    'name': obj.name,
                                    'date_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                                    'message': backup_status,
                                    'automatic': automatic,
                                    'done_by': user_id,
                                    'path': tar_file_path,
                                    'file_size': str(os.path.getsize(tar_file_path)),
                                }, context)
                    except Exception, e:
                        for obj in self.browse(cr, uid, ids, context):
                            backup_status = 'Could not create back up of database at Remote FTP path: %s/%s. Backup Failed. Exception: %s' % (e, ept_ftp.to_ept_location, tar_file_name)
                            self.pool['db.backup.line'].create(cr, uid, {
                                'backup_id': obj.id,
                                'name': tar_file_name,
                                'date_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                                'done_by': uid,
                                'message': backup_status,
                                'automatic': automatic,
                            }, context)
                                      
                if not keep_backup_local:
                    os.remove(tar_file_path)
            else:
                for obj in self.browse(cr, uid, ids, context):
                    backup_status = 'Backup completed successfully at path: %s ' % (tar_file_path)
                    self.pool['db.backup.line'].create(cr, uid, {
                        'backup_id': obj.id,
                        'name': obj.name,
                        'date_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'message': backup_status,
                        'automatic': automatic,
                        'done_by': user_id,
                        'path': tar_file_path,
                        'file_size': str(os.path.getsize(tar_file_path)),
                    }, context)
        self._unset_pg_psw_env_var()
        if bak_conf and bak_conf.ept_enable_email_notification:
            email_from_ids = self.pool['ir.config_parameter'].search(
                cr, uid, [('key', '=', 'auto_backup_from_email_Id')], context=context
            )
            
            to_user_email_ids = ''
            to_email_ids = bak_conf.email_ids
            # users = self.browse(cr, uid, bak_conf.user_ids )
            user_ids = []
            if bak_conf.user_ids:
                user_ids = [x['id'] for x in bak_conf.user_ids]
            for users in self.pool['res.users'].browse(cr, uid, user_ids or [], context):
                if users.user_email:
                    to_user_email_ids = to_user_email_ids + users.user_email + ','
            if to_email_ids and to_email_ids.endswith(','):
                to_email_ids = to_email_ids + to_user_email_ids
            elif to_email_ids:
                to_email_ids = to_email_ids + ',' + to_user_email_ids
            else:
                to_email_ids = to_user_email_ids
            if email_from_ids:
                email_from = self.pool['ir.config_parameter'].browse(cr, uid, email_from_ids[0], context)
                # email_to = to_email_ids
                email_subject = """Database backup notification at ERP server"""
                report_body = """Hello, <br/><br/>"""
                report_body += """<b> '%s'</b> Database backup was taken""" % (db_name)
                if not automatic:
                    report_body += " manually by %s" % (user_name)
                else:
                    report_body += " automatically by the scheduler"
                report_body += " at the time of " + time.strftime('%Y-%m-%d %H:%M:%S')
                report_body += """<br/><br/><b>Details : </b>"""
                report_body += """<br/><br/> <table cellpadding="5" cellspacing="0" align="center" width="600" style="border:2px solid black">"""
                report_body += """<tr><td width="100" align="center" style="border-right:1px solid black; border-bottom:1px solid black"><b>  Directory  </b></td><td width="500" align="center" style="border-right:1px solid black; border-bottom:1px solid black"> %s </td></tr>""" % (bkup_dir)
                report_body += """<tr><td width="100" align="center" style="border-right:1px solid black; border-bottom:1px solid black"><b>  File       </b></td><td width="500" align="center" style="border-right:1px solid black; border-bottom:1px solid black"> %s </td></tr>""" % (tar_file_name)
                report_body += """<tr><td width="100" align="center" style="border-right:1px solid black; border-bottom:1px solid black"><b> Status      </b></td><td width="500" align="center" style="border-right:1px solid black; border-bottom:1px solid black"> %s</td></tr>""" % (backup_status)
                report_body += """</table>"""
                model = 'db.autobackup.ept'
                if to_email_ids:
                    for email in to_email_ids.split(","):
                        email_to = email
                        if email_to:
                            self.pool['mail.message'].schedule_with_attach(
                                cr, uid, email_from.value or '', [email_to], email_subject,
                                report_body, model=model, subtype='html'
                            )
        os.remove(bck_file_path)
        return True


class db_backup_line(orm.Model):
    _name = 'db.backup.line'
    _columns = {
        'backup_id': fields.many2one('db.autobackup.ept', 'Backup'),
        'name': fields.char('DB Name', size=100),
        'date_time': fields.datetime('Date', size=100),
        'path': fields.text('Backup Path'),
        'file_size': fields.char('File Size', size=100),
        'automatic': fields.boolean('Automatic Backup?'),
        'done_by': fields.many2one('res.users', 'Done By'),
        'message': fields.text('Message'),
    }

    _order = 'date_time desc'
  

class Eptftpbackup(orm.Model):
    """
    This will add four fields for ftp_server(host), ftp_username, ftp_password.
    """
    _name = 'ept.ftpbackup'
    _columns = {
        'name': fields.char('Name', size=255, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'is_ftp_active': fields.boolean('Is FTP Active'),
        'ept_ftp_host': fields.char(
            'FTP Host/Server', size=255, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'ept_ftp_username': fields.char(
            'FTP Username', size=255, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'ept_ftp_password': fields.char(
            'FTP Password', size=255, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'ept_ftp_location': fields.char(
            'FTP Location', size=255, readonly=True, states={'draft': [('readonly', False)]},
            help="The location must contain a trailing `/`"
        ),
        'to_ept_location': fields.char(
            'To Directory', size=255, help="The location must contain a trailing `/`",
            required=True, readonly=True, states={'draft': [('readonly', False)]}
        ),
        'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], 'State', readonly=True),
    }
    
    _defaults = {
        'state': 'draft',
        'is_ftp_active': True
    }
    
    def btn_confirm(self, cr, uid, ids, context=None):
        ftpbackup_obj = self.pool['ept.ftpbackup']
        ept_ftp = ftpbackup_obj.browse(cr, uid, ids[0], context)
        if ftp_connect(ept_ftp.ept_ftp_host, ept_ftp.ept_ftp_username, ept_ftp.ept_ftp_password, ept_ftp.to_ept_location):
            self.write(cr, uid, ids, {'state': 'confirmed'}, context=context)
        return True
    
    def btn_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True
    
    def testConnection(self, cr, uid, ids, context=None):
        ftpbackup_obj = self.pool['ept.ftpbackup']
        ept_ftp = ftpbackup_obj.browse(cr, uid, ids[0], context)
        if ftp_connect(ept_ftp.ept_ftp_host, ept_ftp.ept_ftp_username, ept_ftp.ept_ftp_password, ept_ftp.to_ept_location):
            raise orm.except_orm(_(''), _('FTP Connection test successfully.'))
        return True
