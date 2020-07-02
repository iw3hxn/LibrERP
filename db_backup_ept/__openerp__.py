# -*- coding: utf-8 -*-
# © 2014 Emipro Technologies (www.emiprotechnologies.com)
# © 2015-2018 Didotech srl (www.didotech.com)

{
    "name": "Database Auto-Backup & Backup Auto-Transfer to FTP server",
    "version": "6.2.2.2",
    "author": "Emipro Technologies",
    "website": "http://www.emiprotechnologies.com",
    "category": "Generic Modules",
    "description": """
    
        Key feature of this module includes,
        
        -- Automatic database backup based on scheduler
        -- Manual database backup
        -- Database backup log
        -- FTP server configuration & Automatic transfer of database backup to remote location
        -- Email Notification of database notification to fix email address or Users of ERP system
        -- Email Alert to particular person when someone has manually taken database backup
        
        For feedback, please contact us on info@emiprotechnologies.com
        
        For support in OpenERP, please contact us on support@emiprotechnologies.com
        
        For more modules of OpenERP developments, please visit on following link,
        
        https://code.launchpad.net/~emiprotech-launchpad/emipro-technologies/openerp-6.1
        
        For our video's of OpenERP please visit following link,
        
        http://www.emiprotechnologies.com/OpenERP/Video
        
    """,

    "depends": [
        "base"
    ],
    "data": [
        "view/bkp_conf_view.xml",
        "security/db_backup_security.xml",
        "security/backup_data.xml",
        "wizard/manual_db_backup_view.xml",
        "view/ftp_view.xml",
        "security/ir.model.access.csv",
        "cron.xml",
    ],
    "active": False,
    "installable": True,
    'application': True,
}
