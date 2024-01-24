#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime as DT
import subprocess
import sys

from netmiko import ConnectHandler

keyfile = "vmanage"
logfile = "backupjob.log"
backup_path = "./backupdata"

login_info = {
    "device_type": "linux",
    "host": "10.74.84.31",
    "username": "ciscosdwan",
    "use_keys": True,
    "key_file": keyfile,
}

date = str(DT.date.today())
week_ago = DT.datetime.today() - DT.timedelta(days=7)
week_ago = str(week_ago.date())
zerofile = "/tmp/confdb_backup" + week_ago + ".tar.gz"
logtitle = "=" * 15 + "Day of " + date + "=" * 15 + "\n"


class SSHjob:
    """SSHjob defines a class for a job running through SSH by
    calling the module netmiko.
    ...

    Attributes
    ----------
    net_connect : netmiko return object.
    backup_ret : str
        The return of running backup on vmanage.
    ret1 : str
        The first return, copy backup file.
    ret2 : str
        The second return, copy zero size file.

    Methods
    -------
    connect():
        Call the netmiko to connect.
    run_backup():
        Run backup request on vmanage.
    copy_backup_file():
        Copy backup file through scp.
    copy_zero_file():
        Copy zero size file to vmanage.
    disconnect():
        Disconnect vmanage
    """

    def __init__(self):
        self.net_connect = None
        self.backup_ret = None
        self.ret1 = None
        self.ret2 = None

    def connect(self):
        self.net_connect = ConnectHandler(**login_info)

    def run_backup(self):
        backup_cmd = (
            "request nms configuration-db backup path \
                 /home/"
            + login_info["username"]
            + "/confdb_backup"
            + date
        )
        self.backup_ret = self.net_connect.send_command(command_string=backup_cmd,expect_string=r'Successfully',read_timeout=120)

    def copy_backup_file(self):
        runcmd = (
            "scp -i "
            + keyfile
            + " "
            + login_info["username"]
            + "@"
            + login_info["host"]
            + ":"
            + "/home/"
            + login_info["username"]
            + "/confdb_backup"
            + date
            + ".tar.gz "
            + backup_path
        )
        self.ret1 = str(
            subprocess.run(
                runcmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                timeout=600,
            )
        )

    def copy_zero_file(self):
        runcmd = (
            "touch "
            + zerofile
            + " && "
            + "scp -i "
            + keyfile
            + " "
            + zerofile
            + " "
            + login_info["username"]
            + "@"
            + login_info["host"]
            + ":/home/"
            + login_info["username"]
            + "/"
            + " && "
            + "rm "
            + zerofile
        )
        self.ret2 = str(
            subprocess.run(
                runcmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                timeout=600,
            )
        )

    def disconnect(self):
        self.net_connect.disconnect()


def main():
    jobstart = str(DT.datetime.now())
    backup_job = SSHjob()
    backup_job.connect()
    backup_job.run_backup()
    backup_job.copy_backup_file()
    backup_job.copy_zero_file()
    backup_job.disconnect()
    jobend = str(DT.datetime.now())

    logdata = (
        logtitle
        + jobstart
        + " Job started...\n"
        + backup_job.backup_ret
        + "\n"
        + backup_job.ret1
        + "\n"
        + backup_job.ret2
        + "\n"
        + jobend
        + " Job ended...\n"
    )

    with open(logfile, "a") as fobj:
        fobj.write(logdata)

    sys.exit(0)


if __name__ == "__main__":
    main()
