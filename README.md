# Dailybackup 脚本的使用

**Dailybackup** 通过 Linux 的 **Crontab** 每日任务自动执行 **Python** 脚本，将 vManage 的配置数据库文件备份，并通过 SCP 将备份文件拷贝至服务器。

## 脚本由以下部分组成：

1. **job.sh** Shell 脚本，启动 Python 虚拟环境，并执行 Python 脚本
2. **dailaybackup.py** Python 脚本，通过调用 netmiko 模块实现 SSH 登录 vMange，并发送数据备份命令，运行 scp 将文件拷贝至备份服务器的./backupdata 目录。
3. **vmanage** 和 **vmanage.pub** 是一对 RSA 秘钥对，将 vmanage.pub 添加至 vManage 的/home/admin/.ssh/authorized_keys 中。SSH 登录使用私钥 vmanage 进行身份验证，避免使用密码。
4. **backupjob.log** 是备份任务的日志文件，记录任务的开始和结束时间，以及运行的情况。
5. **./backupdata** 是用于存放备份数据的目录。

## 脚本的使用方法：

（1）安装 Python3.7 或以上版本，并在/home/ubuntu/vmanage/ 目录中添加 venv 的虚拟环境。

```shell
python3.8 -m venv venv
source venv/bin/activate
pip install netmiko
mkdir backupdata
```

在脚本执行前，在 Linux 服务器上**至少执行一次 SSH 登录至 VManage 的命令**。
执行后，vManage 的 SSH Key 的指纹信息被存储至 **~/.ssh/known_hosts** 中，避免脚本执行过程中询问是否继续连接。

```shell
ssh -i vmanage admin@10.75.58.50
```

将 **dailybackup** 的所有脚本放在该目录，注意检查 **job.sh** 是否有可执行权限。

（2）添加 Linux 的计划任务，通过 crontab -e 编辑
计划每日 23:00 执行备份任务。

```shell
00 23 * * * cd /home/ubuntu/vmanage && ./job.sh
```

（3）脚本每天执行一次，vManage 会备份当天的数据，并将 7 天前的数据用 0 字节文件替代。

（4）将**cleanzerofile.sh**拷贝至 vmanage 的/home/admin/目录下，定期登录至 vManage 执行，可删除 0 字节文件。

## vMange 恢复过程

1、对 vManage 进行简单的配置，使其 Web Portal 可访问。

2、恢复最小化的配置

```text
system
 system-ip 1.1.1.1
 site-id 1
 sp-org "China Unicom"
 org "China Unicom"
 vbond x.x.x.x
```

3、将 vManage 设置为多租户模式（如果原来 vManage 是多租户模式的话）

4、执行 request nms configuration-db restore /home/admin/db_backup_07xx.tar.gz
等待约 15 分钟即可恢复。

5、待 vManage Web 界面恢复以后，登录检查是否 Tenant、设备白名单、Template 以及 Policy 完成恢复。

6、修改 vBond 的连接信息，因为恢复以后，vManage 上面的 vBond 连接是通过 169.254.x.x 地址进行连接，修改为 vBond 的公网地址。
重新连接到 vBond 后，即完成 vManage 的恢复。
