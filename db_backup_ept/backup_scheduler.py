from osv import fields, osv
import xmlrpclib
import socket
import os
import time
import tools
import codecs
import tarfile
import ftplib
from tools.translate import _

import logging
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


def execute(connector, method, *args):
    res = False
    try:
        res = getattr(connector, method)(*args)
    except socket.error, e:
            raise e
    return res

addons_path = tools.config['addons_path'] + '/db_backup_ept/DBbackups'


class db_backup_ept(osv.osv):
    _name = 'db.autobackup.ept'
  
    def get_db_list(self, cr, user, ids, host='localhost', port='8069', context={}):
        uri = 'http://' + host + ':' + port
        conn = xmlrpclib.ServerProxy(uri + '/xmlrpc/db')
        db_list = execute(conn, 'list')
        return db_list
        
    def get_addons_path(selfcr, user, context={}):
        addons_path = tools.config['addons_path'] + '/db_backup_ept/DBbackups'
        return addons_path

    _columns = {
        'name': fields.char('Database', size=100, required='True', help='Database you want to schedule backups for'),
        'host': fields.char('Host', size=255, required='True'),
        'port': fields.char('Port', size=10, required='True'),
        'history_line': fields.one2many('db.backup.line', 'backup_id', 'History', readonly=True),
        'active': fields.boolean('Active'),
        'ftp_enable': fields.boolean('FTP Enable ?'),
        'keep_backup_local': fields.boolean('Keep Backup on Local Path?',
                                            help="Check this field if you want to keep database backup in Local directory. If this is unchecked then database backup will only be able transfer to FTP server."),
        'FTP_id': fields.many2one('ept.ftpbackup', "FTP"),
        'backup_dir': fields.char('Backup Directory', size=512, help='Absolute path for storing the backups', required='True'),
        'ept_enable_email_notification': fields.boolean('ept_enable_email_notification'),
        'email_ids': fields.char('Email Ids', size=1024, help='Add email id for FTP backup schedule notification. Separate Email Ids by comma(,). '),
        'user_ids': fields.many2many('res.users', 'db_backup_users_rel', 'backup_id', 'user_id', 'users', help='select user for email notification.')
    }

    _defaults = {
        'backup_dir': lambda *a: addons_path,
        'host': lambda *a: 'localhost',
        'port': lambda *a: '8069',
        'active': True,
    }
    
    def _check_db_exist(self, cr, user, ids):
        for record in self.browse(cr, user, ids):
            db_list = self.get_db_list(cr, user, ids, record.host, record.port)
            if record.name in db_list:
                return True
        return False
    
    _constraints = [
        (_check_db_exist, 'Error !!! No such database exist.', [])
    ]
    
    def __init__(self, cr, pool):
        super(db_backup_ept, self).__init__(cr, pool)
        self._pg_psw_env_var_is_set = False
    
    def schedule_backup(self, cr, user, context={}):
        conf_ids = self.search(cr, user, [('active', '=', 'True')])
        confs = self.browse(cr, user, conf_ids)
        for rec in confs:
            db_list = self.get_db_list(cr, user, [], rec.host, rec.port)
            if rec.name in db_list:
                try:
                    if not os.path.isdir(rec.backup_dir):
                        os.makedirs(rec.backup_dir)
                except:
                    raise
                self.ept_backup(cr, user, [rec.id], rec.name, rec.backup_dir, True, rec.ftp_enable, rec.FTP_id, rec, rec.keep_backup_local)
                # self.hv_backup(cr, user,[Bak conf ID], db_name, db_bkp_dir,AUTO,FTP)
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
    
    def ept_backup(self, cr, uid, ids, db_name, bkup_dir, automatic, ftp_enable, FTP_id, bak_conf, keep_backup_local):
        self._set_pg_psw_env_var()
        bkp_file = '%s_%s.sql' % (db_name, time.strftime('%Y%m%d_%H_%M_%S'))
        tar_file_name = '%s_%s.tar.gz' % (db_name, time.strftime('%Y%m%d_%H_%M_%S'))
        file_path = os.path.join(bkup_dir, bkp_file)
        tar_file_path = os.path.join(bkup_dir, tar_file_name)
        tar_obj = tarfile.open(tar_file_path, 'w:gz')
        fp = codecs.open(file_path, 'wb')
        cmd = ['pg_dump', '--format=p', '--no-owner']
        if tools.config['db_user']:
            cmd.append('--username=' + tools.config['db_user'])
        if tools.config['db_host']:
            cmd.append('--host=' + tools.config['db_host'])
        if tools.config['db_port']:
            cmd.append('--port=' + str(tools.config['db_port']))
        cmd.append(db_name)
        stdin, stdout = tools.exec_pg_command_pipe(*tuple(cmd))
        stdin.close()
        data = stdout.read()
        fp.write(data)
        fp.close()
        tar_obj.add(file_path, bkp_file)
        tar_obj.close()
        res = stdout.close()
        user_id = None
        user_name = ''
        backup_status = ''
        if not automatic:
            user_id = uid
            user_name = self.pool.get('res.users').browse(cr, uid, uid, context=None).name
        if res:
            _logger.error(u"DUMP DB: %s failed\n%s" % (db_name, data))
            for obj in self.browse(cr, uid, ids):
                self.pool.get('db.backup.line').create(cr, uid, {
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
            context = {}
            if ftp_enable:
                if FTP_id:
                    ftpbackup_obj = self.pool.get('ept.ftpbackup')
                    ept_ftp = ftpbackup_obj.browse(cr, uid, FTP_id.id, context)
                    if not ept_ftp.ept_ftp_host or not ept_ftp.ept_ftp_username or \
                            not ept_ftp.ept_ftp_password or not ept_ftp.to_ept_location:
                        for obj in self.browse(cr, uid, ids):
                            self.pool.get('db.backup.line').create(cr, uid, {
                                'backup_id': obj.id,
                                'name': tar_file_name,
                                'date_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                                'done_by': uid,
                                'message': 'Could not create back up of database. Backup Failed. Invalid FTP Credentials',
                                'automatic': automatic,
                            })
                        backup_status = 'Could not create back up of database. Backup Failed. Invalid FTP Credentials'
                        os.remove(file_path)
                        return True
                    try:
                        if ept_ftp.is_ftp_active:
                            s = ftplib.FTP(ept_ftp.ept_ftp_host, ept_ftp.ept_ftp_username, ept_ftp.ept_ftp_password)  # Connect
                            f = open(tar_file_path, 'rb')                # file to send
                            remote_file_path = os.path.join(ept_ftp.to_ept_location, tar_file_name)
                            s.storbinary('STOR ' + remote_file_path, f)         # Send the file
                            f.close()                                # Close file and FTP
                            s.quit()
                            for obj in self.browse(cr, uid, ids):
                                backup_status = 'Backup completed successfully at Remote FTP path : %s/%s.' % (ept_ftp.to_ept_location, tar_file_name)
                                self.pool.get('db.backup.line').create(cr, uid, {
                                    'backup_id': obj.id,
                                    'name': obj.name,
                                    'date_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                                    'message': backup_status,
                                    'automatic': automatic,
                                    'done_by': user_id,
                                    'path': tar_file_path,
                                    'file_size': str(os.path.getsize(tar_file_path)),
                                })
                    except Exception, e:
                        for obj in self.browse(cr, uid, ids):
                            backup_status = 'Could not create back up of database at Remote FTP path: %s/%s. Backup Failed. Exception: %s' % (e, ept_ftp.to_ept_location, tar_file_name)
                            self.pool.get('db.backup.line').create(cr, uid, {
                                'backup_id': obj.id,
                                'name': tar_file_name,
                                'date_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                                'done_by': uid,
                                'message': backup_status,
                                'automatic': automatic,
                            })
                                      
                if not keep_backup_local:
                    os.remove(tar_file_path)
            else:
                for obj in self.browse(cr, uid, ids):
                    backup_status = 'Backup completed successfully at path: %s ' % (tar_file_path)
                    self.pool.get('db.backup.line').create(cr, uid, {
                        'backup_id': obj.id,
                        'name': obj.name,
                        'date_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'message': backup_status,
                        'automatic': automatic,
                        'done_by': user_id,
                        'path': tar_file_path,
                        'file_size': str(os.path.getsize(tar_file_path)),
                    })
        self._unset_pg_psw_env_var()
        if bak_conf and bak_conf.ept_enable_email_notification:
            email_from_ids = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'auto_backup_from_email_Id')])
            
            to_user_email_ids = ''
            to_email_ids = bak_conf.email_ids
            #users = self.browse(cr, uid, bak_conf.user_ids )
            user_ids = []
            if bak_conf.user_ids:
                user_ids = [x['id'] for x in bak_conf.user_ids]
            for users in self.pool.get('res.users').browse(cr, uid, user_ids or [], context):
                if users.user_email:
                    to_user_email_ids = to_user_email_ids + users.user_email + ','
            if to_email_ids and to_email_ids.endswith(','):
                to_email_ids = to_email_ids + to_user_email_ids
            elif to_email_ids:
                to_email_ids = to_email_ids + ',' + to_user_email_ids
            else:
                to_email_ids = to_user_email_ids
            if email_from_ids:
                email_from = self.pool.get('ir.config_parameter').browse(cr, uid, email_from_ids[0], context)
                #email_to = to_email_ids
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
                            self.pool.get('mail.message').schedule_with_attach(cr, uid, email_from.value or '', [email_to], email_subject, report_body, model=model, subtype='html')
        os.remove(file_path)
        return True


class db_backup_line(osv.osv):
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
  

class Eptftpbackup(osv.osv):
    """
    This will add four fields for ftp_server(host), ftp_username, ftp_password.
    """
    _name = 'ept.ftpbackup'
    _columns = {
        'name': fields.char('Name', size=255, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'is_ftp_active': fields.boolean('Is FTP Active'),
        'ept_ftp_host': fields.char('FTP Host/Server', size=255, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'ept_ftp_username': fields.char('FTP Username', size=255, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'ept_ftp_password': fields.char('FTP Password', size=255, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'ept_ftp_location': fields.char('FTP Location', size=255, readonly=True, states={'draft': [('readonly', False)]},
                                        help="The location must contain a trailing `/`"),
        'to_ept_location': fields.char('To Directory', size=255, help="The location must contain a trailing `/`", required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], 'State', readonly=True),
    }
    
    _defaults = {
        'state': 'draft',
        'is_ftp_active': True,
    }
    
    def btn_confirm(self, cr, uid, ids, context=None):
        ftpbackup_obj = self.pool.get('ept.ftpbackup')
        ept_ftp = ftpbackup_obj.browse(cr, uid, ids[0], context)
        s = None
        try:
            s = ftplib.FTP(ept_ftp.ept_ftp_host, ept_ftp.ept_ftp_username, ept_ftp.ept_ftp_password)
        except Exception, e:
            raise osv.except_osv(_('FTP Authentication Fail!'), _('Please check the account setting for Auto FTP backup. Some details may be missing/Incorrect.'))
        if s:
            dir = ''
            try:
                dir = s.cwd(ept_ftp.to_ept_location)
            except Exception, ex:
                raise osv.except_osv(_(''), _('FTP Connection test successfully. But Specified directory is not locate.'))
            if "250 CWD" in dir:
                self.write(cr, uid, ids, {'state': 'confirmed'}, context=None)
        return True
    
    def btn_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'}, context=None)
        return True
    
    def testConnection(self, cr, uid, ids, context=None):
        ftpbackup_obj = self.pool.get('ept.ftpbackup')
        ept_ftp = ftpbackup_obj.browse(cr, uid, ids[0], context)
        s = None
        try:
            s = ftplib.FTP(ept_ftp.ept_ftp_host, ept_ftp.ept_ftp_username, ept_ftp.ept_ftp_password)
        except Exception, e:
            raise osv.except_osv(_('FTP Authentication Fail!'), _('Please check the account setting for Auto FTP backup. Some details may be missing/Incorrect.'))
        if s:
            dir = ''
            try:
                dir = s.cwd(ept_ftp.to_ept_location)
            except Exception, ex:
                raise osv.except_osv(_(''), _('FTP Connection test successfully. But Specified directory is not locate.'))
            
            if "250 CWD" in dir:
                raise osv.except_osv(_(''), _('FTP Connection test successfully.'))
