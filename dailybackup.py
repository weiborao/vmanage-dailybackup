#!/venv/bin/ python3

from netmiko import ConnectHandler
import datetime as DT
import subprocess
import sys


keyfile = 'vmanage'
logfile = 'backupjob.log'
backup_path = './backupdata'

login_info = {
    'device_type': 'linux',
    'host':   '10.75.58.50',
    'username': 'admin',
    'use_keys': True,
    'key_file': keyfile
}

jobstart = str(DT.datetime.now())

net_connect = ConnectHandler(**login_info)

date = str(DT.date.today())
backupreturn = net_connect.send_command(
    'request nms configuration-db backup path /home/admin/confdb_backup' + date)

# print(backupreturn)

runcmd1 = 'scp -i ' + keyfile + ' ' + login_info['username'] + '@' + \
    login_info['host'] + ':' + '/home/admin/confdb_backup' + \
    date + '.tar.gz ' + backup_path

ret1 = subprocess.run(runcmd1, shell=True, stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE, encoding="utf-8", timeout=1)

# print(uploadfile)

net_connect.disconnect()

# zero size the backup file one week ago.
week_ago = DT.datetime.today() - DT.timedelta(days=7)
week_ago = str(week_ago.date())
zerofile = "/tmp/confdb_backup" + week_ago + ".tar.gz"

runcmd2 = 'touch ' + zerofile + ' && ' + 'scp -i vmanage ' + zerofile + \
    ' admin@' + login_info['host'] + \
    ':/home/admin/' + ' && ' + 'rm ' + zerofile

ret2 = subprocess.run(runcmd2, shell=True, stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE, encoding="utf-8", timeout=1)

# print(ret)

ret1 = str(ret1)
ret2 = str(ret2)

jobend = str(DT.datetime.now())

logtitle = '\n\n' + '='*15 + 'Day of ' + date + '='*15 + '\n'
logdata = logtitle + jobstart + ' Job started...\n' + backupreturn + \
    '\n' + ret1 + '\n' + ret2 + '\n' + jobend + ' Job ended...\n'

with open(logfile, 'a') as fobj:
    fobj.write(logdata)

sys.exit(0)
