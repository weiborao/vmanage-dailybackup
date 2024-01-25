[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/weiborao/vmanage-dailybackup)
# vManage Dailybackup script

## Summary of this script

Currently (Oct. 2020), vManage doesn't have a daily backup function through GUI. If something went wrong with vMange, for example, the virtual machine of the vManage crashed, all the configuration data, including templates, device configurations, control policies, and data policies would be lost, and the SD-WAN network cannot be managed and new configuration changes can not be done.

This Dailybackup script automatically executes Python scripts through Linux Crontab daily tasks, backs up the configuration database file of vManage, and copies the backup file to the server through SCP every day. 

The daily backup script provides an easy-to-use, low-cost, and easy-to-deploy automated data backup solution, which can effectively supplement the data backup function of vManage, helps customers to perform daily automatic backups, and eliminate the risk of data loss. You can easily recover the configuration database to a newly installed vManage.

## Components of the script

1. **job.sh** A shell script, which starts the Python virtual environment, and executes the Python script.
1. **dailaybackup.py** The Python script implements SSH login to vManage by calling the ***netmiko*** module, sends a data backup command, and runs scp to copy the file to the ./backupdata directory of the backup server.
1. **vmanage and vmanage.pub** are a pair of RSA key pairs. Add vmanage.pub to vManage server's /home/admin/.ssh/authorized_keys. SSH login uses the private key vmanage for authentication in a passless way. You can generate your own key pair through **ssh-keygen -t rsa -f .ssh/vmanage -C admin**
1. **backupjob.log** is the log file of the backup job, which records the start and end time of the job, as well as the job running status.
1. **./backupdata** is the directory for storing backup data.

## How to use the script:

(1) Git clone the code to your home directory, such as **/home/ubuntu/**

```shell
cd /home/ubuntu/
git clone https://github.com/weiborao/vmanage-dailybackup.git vmanage
cd vmanage
```
The file vmanage is the private key, **permissions 0664** for 'vmanage' are too open, you can change it to **0600**.

```shell
chmode 600 vmanage
```

(2) Install Python3.7 or above, and add the venv virtual environment in the /home/ubuntu/vmanage/ directory, or other directories.

```shell
which python3
python3 -V
python3 -m venv venv
source venv/bin/activate
pip install netmiko
```

Before executing the script, execute the SSH login command on the Linux server at least once, and add the **vmanage.pub** to **/home/admin/.ssh/authorized_keys**

In the following example, the vManage server's IP address is 10.75.58.50.

```shell
scp vmanage.pub admin@10.75.58.50:/home/admin/.ssh/authorized_keys

The authenticity of host '10.75.58.50 (10.75.58.50)' can't be established.
ECDSA key fingerprint is SHA256:rDdvfeJ0mJquMu0KiAtAkH++n3ZBS9sYEr+TRMQBNOI.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '10.75.58.50' (ECDSA) to the list of known hosts.
viptela 20.1.1

admin@10.75.58.50's password:
vmanage.pub                                  100%  559   818.7KB/s   00:00
```
**Note**: *If you have other hosts that are already in /home/admin/.ssh/authorized_keys, you can append vmanage.pub to the authorized_keys through vi editor.*

After execution, the fingerprint information of vManage's SSH Key is stored in ~/.ssh/known_hosts to avoid asking whether to continue the connection during script execution. 

```shell
ssh -i vmanage admin@10.75.58.50
viptela 20.1.1

Last login: Sat Oct 10 10:37:17 2020 from 10.75.58.5
Welcome to Viptela CLI
admin connected from 10.75.58.5 using ssh on vmanage
vmanage#
```

Pay attention to check whether **job.sh** has executable permissions.

```shell
~/vmanage$ ll job.sh
-rwxrwxr-x 1 ubuntu ubuntu 145 Oct 10 10:19 job.sh*
```

(3) Add a scheduled task for Linux, and edit it through **crontab -e** to schedule a backup task at 23:00 every day.

```shell
00 23 * * * cd /home/ubuntu/vmanage && ./job.sh
```

(4) The script is to executed once a day, vManage backs up the data of the day and replaces the backup file 7 days ago with a 0-byte file.

(5) Copy **cleanzerofile.sh** to the /home/admin/ directory of vManage server, log in to vManage regularly for execution, and it will delete 0-byte files.

## Run the script in a docker for quick test.

Here I provide a Dockerfile for quick environment setup.

You can copy the Dockerfile to your work directory, and run the commands as follows:

❯ cd docker
❯ docker build . -t ubuntu-python3

You can list the images after the build completed.

❯ docker images

❯ docker run -it ubuntu-python3
root@af441dac641f:~# git clone https://github.com/weiborao/vmanage-dailybackup.git
Cloning into 'vmanage-dailybackup'...
remote: Enumerating objects: 122, done.
remote: Counting objects: 100% (122/122), done.
remote: Compressing objects: 100% (88/88), done.
remote: Total 122 (delta 66), reused 81 (delta 30), pack-reused 0
Receiving objects: 100% (122/122), 1.38 MiB | 1.25 MiB/s, done.
Resolving deltas: 100% (66/66), done.
root@af441dac641f:~# cd vmanage-dailybackup/
root@af441dac641f:~/vmanage-dailybackup# python3 -m venv venv
root@af441dac641f:~/vmanage-dailybackup# source venv/bin/activate
(venv) root@af441dac641f:~/vmanage-dailybackup# pip3 install netmiko

(venv) root@af441dac641f:~/vmanage-dailybackup# ssh-keygen -t rsa -f vmanage -C ciscosdwan
(venv) root@af441dac641f:~/vmanage-dailybackup# scp vmanage.pub ciscosdwan@10.74.84.31:/home/ciscosdwan/.ssh/authorized_keys
(venv) root@af441dac641f:~/vmanage-dailybackup# ssh -i vmanage ciscosdwan@10.74.84.31
viptela 20.12.1
vManage1# exit

After you change the login_info to your onw vManage and Username, you can run the backup script.

root@af441dac641f:~/vmanage-dailybackup# ./job.sh
Start to backup database.
Connnected to vManage 10.74.84.31
request nms configuration-db backup path /home/ciscosdwan/confdb_backup2024-01-25
Backup config DB finished.
scp -i vmanage ciscosdwan@10.74.84.31:/home/ciscosdwan/confdb_backup2024-01-25.tar.gz ./backupdata
Backup DB file copied to the server.
touch /tmp/confdb_backup2024-01-18.tar.gz && scp -i vmanage /tmp/confdb_backup2024-01-18.tar.gz ciscosdwan@10.74.84.31:/home/ciscosdwan/ && rm /tmp/confdb_backup2024-01-18.tar.gz
Zero size file copied.
enter vshell..
rm confdb_backup2024-01-18.tar.gz -f
Zero size file deleted.
Disconnected..
 Done.
End of the job.
root@af441dac641f:~/vmanage-dailybackup# ls -al ./backupdata
total 2008
drwxr-xr-x 2 root root    4096 Jan 25 13:43 .
drwxr-xr-x 5 root root    4096 Jan 25 13:38 ..
-rwxr-xr-x 1 root root       0 Jan 25 13:38 confdb_backup.tar.gz
-rwxr-xr-x 1 root root 2044339 Jan 25 13:43 confdb_backup2024-01-25.tar.gz

root@af441dac641f:~/vmanage-dailybackup# ssh -i vmanage ciscosdwan@10.74.84.31
viptela 20.12.1

Last login: Thu Jan 25 21:43:40 CST 2024 from 10.141.77.173 on ssh
Welcome to Viptela CLI
User ciscosdwan last logged in 2024-01-25T13:42:39.86983+00:00, to vManage1, from 10.141.77.173 using cli-ssh
ciscosdwan connected from 10.141.77.173 using ssh on vManage1
vManage1# vshell
vManage1:~$ ls -al
total 6028
drwxr-x---  3 ciscosdwan users    4096 Jan 25 21:43 .
drwxr-xr-x 17 root       root     4096 Jan 23 20:23 ..
-rw-------  1 ciscosdwan users     504 Jan 25 21:43 .bash_history
-rwxr-xr-x  1 ciscosdwan users     411 Jan 23 20:23 .bashrc
-rwxr-xr-x  1 ciscosdwan users     241 Aug  9 14:45 .profile
drwx------  2 ciscosdwan users    4096 Jan 23 20:23 .ssh
-rwxrwxr-x  1 vmanage    admin 2046524 Jan 23 22:32 backupdata.tar.gz
-rwxrwxr-x  1 vmanage    admin 2044339 Jan 25 21:43 confdb_backup2024-01-25.tar.gz

## Demo Video

Please find the demo videos here, each of them is the same.

[vManage Daily Backup](./vManage_Dailybackup.mp4)

[YouTube: Cisco SDWAN vManage Configuration Database Daily backup script
](https://www.youtube.com/watch?v=Qgn4eLaLh2Y)

[Bilibili: Cisco vManage Dailybackup](https://www.bilibili.com/video/BV1Cz4y1o7Tq/)

## vMange recovery process
(1) Simply configure vManage to make its Web Portal accessible, apply and install the certificate for it, because a newly installed vManage has a different UUID.

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

(6) Modify the vBond connection information, because after restoration, the vBond connection on vManage is connected through the 169.254.x.x address. You need to modify to vBond public network address. After reconnecting to vBond, the restoration of vManage is completed.

## Acknowledgement

My teamates **Michael Tao Li**, and **Xing James Jiang** helped to build this daily backup script.