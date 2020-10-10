# vManage Dailybackup script

This Dailybackup script automatically executes Python scripts through Linux Crontab daily tasks, backs up the configuration database file of vManage, and copies the backup file to the server through SCP everyday.

## Components of the scripts
1. **job.sh** A shell script, which starts the Python virtual environment, and execute the Python script
1. **dailaybackup.py** The Python script implements SSH login to vManage by calling the netmiko module, sends a data backup command, and runs scp to copy the file to the ./backupdata directory of the backup server.
1. **vmanage and vmanage.pub** are a pair of RSA key pairs. Add vmanage.pub to vManage server's /home/admin/.ssh/authorized_keys. SSH login uses the private key vmanage for authentication in a passless way.
1. **backupjob.log** is the log file of the backup job, which records the start and end time of the job, as well as the job running status.
1. **./backupdata** is the directory for storing backup data.

## How to use the script:
(1) Install Python3.7 or above, and add the venv virtual environment in the /home/ubuntu/vmanage/ directory, or other directory.

```shell
python3.8 -m venv venv
source venv/bin/activate
pip install netmiko
mkdir backupdata
```

Before executing the script, execute the SSH login command on the Linux server at least once. After execution, the fingerprint information of vManage's SSH Key is stored in ~/.ssh/known_hosts to avoid asking whether to continue the connection during script execution.

```shell
ssh -i vmanage admin@10.75.58.50
```

Put all the dailybackup scripts in this directory, and pay attention to check whether **job.sh** has executable permissions.

(2) Add a scheduled task for Linux, and edit it through **crontab -e** to schedule a backup task at 23:00 every day.

```shell
00 23 * * * cd /home/ubuntu/vmanage && ./job.sh
```

(3) The script is to executed once a day, vManage backs up the data of the day and replace the data 7 days ago with a 0-byte file.

(4) Copy **cleanzerofile.sh** to the /home/admin/ directory of vManage server, log in to vManage regularly for execution, and it will delete 0-byte files.

## vMange recovery process
(1) Simply configure vManage to make its Web Portal accessible.

(2) Restore the minimized configuration, for example:

```shell
system
 system-ip 1.1.1.1
 site-id 1
 sp-org "China Unicom"
 org "China Unicom"
 vbond x.x.x.x
```

(3) Set vManage to multi-tenant mode (if the original vManage is multi-tenant mode)

(4)Execute **request nms configuration-db restore /home/admin/dbbackup07xx.tar.gz** and wait about 15 minutes to restore.

(5) After the vManage Web interface is restored, log in to check whether the tenant, device whitelist, template, and policy have been restored.

(6) Modify the vBond connection information, because after restoration, the vBond connection on vManage is connected through the 169.254.x.x address. You need to the modify to vBond public network address. After reconnecting to vBond, the restoration of vManage is completed.