import sys
import logging
from open_ldap2.config.password import bastionhost
from alibabacloud_yundun_bastionhost20191209.client import Client as Yundun_bastionhost20191209Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_yundun_bastionhost20191209 import models as yundun_bastionhost_20191209_models



class BastionHost:
    logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='## %Y-%m-%d %H:%M:%S')
    logging.getLogger().setLevel(logging.INFO)

    def __init__(self, version):
        """
        @param: 如果重新导入堡垒机服务器，请将version替换成对应ID
        """
        self.InstanceId = bastionhost[2]
        if version == "test":
            self.hostid = "11"
        elif version == "formal":
            self.hostid = "10"

    @staticmethod
    def __create_client():
        """
        使用AK&SK初始化账号Client
        @return: Client
        @throws Exception

        """
        config = open_api_models.Config(
            # 您的AccessKey ID,
            access_key_id=bastionhost[0],
            # 您的AccessKey Secret,1
            access_key_secret=bastionhost[1]
        )
        # 访问的域名
        config.endpoint = 'yundun-bastionhost.aliyuncs.com'
        return Yundun_bastionhost20191209Client(config)

    def list_host_accounts(self, hosts_username):
        """
         查找主机账户
         @param hosts_username:主机账号名称
         return HostAccountId:主机账号id和 HostId:主机id
         """
        client = BastionHost.__create_client()
        list_host_accounts_request = yundun_bastionhost_20191209_models.ListHostAccountsRequest(
            instance_id=self.InstanceId,
            host_id=self.hostid,
            host_account_name=hosts_username
        )
        # 复制代码运行请自行打印 API 的返回值
        request = eval(str(client.list_host_accounts(list_host_accounts_request)))
        if request['body']['TotalCount'] == 0:
            logging.info("No hostname in host_accounts ")
            return None
        else:
            return [True, request['body']['HostAccounts'][0]['HostId'],
                    request['body']['HostAccounts'][0]['HostAccountId']]

    def create_host_account(self, username, password):
        """
        添加主机账户
        @param username:主机账户
        @param password:主机账户密码
        return 是否拥有和实例ID号
        """
        try:
            client = BastionHost.__create_client()
            create_host_account_request = yundun_bastionhost_20191209_models.CreateHostAccountRequest(
                instance_id=self.InstanceId,
                host_id=self.hostid,
                protocol_name='SSH',
                host_account_name=username,
                password=password
            )
            request = eval(str(client.create_host_account(create_host_account_request)))
            return True, request['body']['HostAccountId']
        except Exception as err:
            logging.error(err)
            return None

    def list_hosts(self, hostname):
        """
        检查堡垒机是否存在实例
        @param hostname:实例名称
        return 是否拥有和实例ID号
        """
        client = BastionHost.__create_client()
        list_hosts_request = yundun_bastionhost_20191209_models.ListHostsRequest(
            host_name=hostname,
            instance_id=self.InstanceId
        )
        # 复制代码运行请自行打印 API 的返回值
        request = eval(str(client.list_hosts(list_hosts_request)))
        if request['body']['TotalCount'] == 0:
            logging.error("{},No hostname in fortress machine ".format(hostname))
            return False
        else:
            return True, request['body']['Hosts'][0]['HostId']

    def check_user(self, username):
        """
        查询堡垒机是否有用户
        @param username:堡垒机用户名
        return 是否拥有和堡垒机用户id
        """
        client = BastionHost.__create_client()
        list_users_request = yundun_bastionhost_20191209_models.ListUsersRequest(
            instance_id=self.InstanceId,
            user_name=username
        )
        # 复制代码运行请自行打印 API 的返回值
        request = eval(str(client.list_users(list_users_request)))
        if request['body']['TotalCount'] == 0:
            logging.info("BastionHost is no user")
            return None
        else:
            return True, request['body']['Users'][0]['UserId']

    def attach_host_accounts_user(self, user_id, host_account_id):
        """
        用户授权主机和主机账户
        @param user_id:用户id
        @param host_account_id:主机账户id
        return 是否拥有和实例ID号
        """
        client = BastionHost.__create_client()
        attach_host_accounts_to_user_request = yundun_bastionhost_20191209_models.AttachHostAccountsToUserRequest(
            instance_id=self.InstanceId,
            user_id=user_id,
            hosts='[{"HostId": "%s", "HostAccountIds": ["%s"]}]' % (self.hostid, host_account_id))
        # 复制代码运行请自行打印 API 的返回值
        attach_host = client.attach_host_accounts_to_user(attach_host_accounts_to_user_request)
        # print(eval(str(attach_host))['body']['Results'][0]['HostAccounts'][0][['Code']])
        if eval(str(attach_host))['body']['Results'][0]['HostAccounts'][0]['Code'] == "OK":
            return [True, eval(str(attach_host))['body']['Results'][0]['HostAccounts'][0]['HostAccountId']]
        else:
            logging.info("The user failed to authorize the host and host account，Please contact smartops1@huan.tv")


if __name__ == '__main__':
    pass
