
from osv import fields, osv
from tools.translate import _
import os

class db_backup_manual(osv.osv_memory):
    _name = "db.backup.manual.ept"
    _columns = {
       'db_id': fields.many2one('db.autobackup.ept', \
                                 'Database', \
                                 required=True,domain=[('active','=','True')],\
                                 help="Select a database for which you want to generate manual backup."),
    }

    def data_save(self, cr, uid, ids, context=None):
        data =  self.read(cr, uid, ids, context=context)
        print str(data[0]['db_id'])   
        confs = self.pool.get('db.autobackup.ept').browse(cr,uid,[data[0]['db_id'][0]])
        for rec in confs:
            db_list = self.pool.get('db.autobackup.ept').get_db_list(cr, uid, [], rec.host, rec.port)
            if rec.name in db_list:
                try:
                    if not os.path.isdir(rec.backup_dir):
                        os.makedirs(rec.backup_dir)
                except:
                    raise
                result = self.pool.get('db.autobackup.ept').ept_backup(cr, uid,[rec.id], rec.name, rec.backup_dir,False,rec.ftp_enable,rec.FTP_id,rec,rec.keep_backup_local)
        return {'type': 'ir.actions.act_window_close'}   
    
db_backup_manual()

