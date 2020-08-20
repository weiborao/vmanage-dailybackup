#!/venv/bin/ python3

from netmiko import ConnectHandler
import datetime as DT
import subprocess
import sys


keyfile = 'vmanage'
logfile = 'backupjob.log'

login_info = {
    'device_type': 'linux',
    'host':   '10.75.58.50',
    'username': 'admin',
    'use_keys': True,
    'key_file': keyfile
}

ftp_user = 'sammy'
ftp_password = '123456'
ftp_server = '10.75.58.5'

jobstart = str(DT.datetime.now())

net_connect = ConnectHandler(**login_info)

date = str(DT.date.today())
backupreturn = net_connect.send_command(
    'request nms configuration-db backup path /home/admin/confdb_backup' + date)

# print(backupreturn)

uploadfile = net_connect.send_command(
    'request upload ftp://' + ftp_user + ':' + ftp_password +
    '@' + ftp_server + '/upload/confdb_backup' + date
    + '.tar.gz' + ' confdb_backup' + date + '.tar.gz')

# print(uploadfile)

net_connect.disconnect()

# zero size the backup file one week ago.
week_ago = DT.datetime.today() - DT.timedelta(days=7)
week_ago = str(week_ago.date())
zerofile = "/tmp/confdb_backup" + week_ago + ".tar.gz"

runcmd = 'touch ' + zerofile + ' && ' + 'scp -i vmanage ' + zerofile + \
    ' admin@' + login_info['host'] + \
    ':/home/admin/' + ' && ' + 'rm ' + zerofile

ret = subprocess.run(runcmd, shell=True, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE, encoding="utf-8", timeout=1)

# print(ret)

ret = str(ret)

jobend = str(DT.datetime.now())

logtitle = '\n\n' + '='*15 + 'Day of ' + date + '='*15 + '\n'
logdata = logtitle + jobstart + ' Job started...\n' + backupreturn + \
    uploadfile + '\n' + ret + '\n' + jobend + ' Job ended...\n'

with open(logfile, 'a') as fobj:
    fobj.write(logdata)

sys.exit(0)
