#!/usr/bin/env python3
# -*- coding: utf8 -*-
# @Author  : Mr.wang_xi！！
import requests
import logging
from open_ldap2.config.configuration_file import *


class DolphinScheduler:
    """
    @param 变化参数：测试集群，正式集群，账号，hive密码和描述信息，Token
    @param 用户判断正式环境和测试环境的变量：1.正式 2.测试 变量名：ds_choice  传参version
    @param 测试环境：test_ds
    @param 正式环境：formal_ds
    @param 账号：user(用户自己来定)
    @param 邮箱：mail(用户自己来定)
    @param 密码：passwd(需要用户输入正确的hive密码)
    @param 描述信息：description(对蓝鲸用户的作用进行描述)
    """
    def __init__(self, version):
        if version == "formal":
            self.ds_choice = choice[0]
            self.ds_token = token[0]
            self.headers = {'token': self.ds_token}
        elif version == "test":
            self.ds_choice = choice[1]
            self.ds_token = token[1]
            self.headers = {'token': self.ds_token}
        else:
            print('未知错误！')

    def check_tenant(self, user):  # 1.查询租户是否存在
        try:
            check_tenant = self.ds_choice + '/dolphinscheduler/tenant/list-paging'
            params = {'pageNo': 1,
                      'pageSize': 20,
                      'searchVal': '{}'.format(user)}
            results = requests.get(check_tenant, headers=self.headers, params=params).json()
            if results['data']['totalList']:
                tenant_id = results['data']['totalList'][0]['id']
                return True, tenant_id
            else:
                return False
        except BaseException as err:
            logging.error(err)

    def create_tenant(self, user, description):  # 2.创建租户
        try:
            create_tenant_url = self.ds_choice + '/dolphinscheduler/tenant/create'
            params = {'queueId': '1',
                      'tenantCode': user,
                      'tenantName': user,
                      'description': description}
            create = requests.post(create_tenant_url, headers=self.headers,
                                   params=params).json()
            if create['msg'] == 'success':
                logging.info("创建租户成功")
                return True
            else:
                logging.error("创建租户失败")
                return False
        except BaseException as err:
            logging.error(err)

    def check_user(self, user):  # 1.查询用户是否存在
        try:
            check_tenant = self.ds_choice + '/dolphinscheduler/users/list-paging'
            params = {'pageNo': 1,
                      'pageSize': 20,
                      'searchVal': '{}'.format(user)}
            results = requests.get(check_tenant, headers=self.headers, params=params).json()
            print(results)
            if results['data']['totalList']:
                user_id = results['data']['totalList'][0]['id']
                return True, user_id
            else:
                return False
        except BaseException as err:
            logging.error(err)

    def create_user(self, user, password, tenant_id, user_mail):  # 2.创建用户
        try:
            create_user_url = self.ds_choice + '/dolphinscheduler/users/create'
            params = {'userName': user,
                      'userPassword': password,
                      'tenantId': tenant_id,
                      'email': user_mail}
            create = requests.post(create_user_url, headers=self.headers,
                                   params=params).json()
            if create['msg'] == 'success':
                logging.info("创建用户成功")
                return True
            else:
                logging.error("创建用户失败")
                return False
        except BaseException as err:
            logging.error(err)

    def check_alert_group(self, user):  # 1.查询告警组
        try:
            check_tenant = self.ds_choice + '/dolphinscheduler/alert-group/list-paging'
            params = {'pageNo': 1,
                      'pageSize': 20,
                      'searchVal': '{}'.format(user)}
            results = requests.get(check_tenant, headers=self.headers, params=params).json()
            print(results)
            if results['data']['totalList']:
                alert_id = results['data']['totalList'][0]['id']
                return True, alert_id
            else:
                return False
        except BaseException as err:
            logging.error(err)

    def create_alert_group(self, user, group_type="EMAIL"):  # 2.创建告警组
        try:
            create_alert_url = self.ds_choice + '/dolphinscheduler/alert-group/create'
            params = {'groupName': user,
                      'groupType': group_type}
            create = requests.post(create_alert_url, headers=self.headers,
                                   params=params).json()
            if create['msg'] == 'success':
                logging.info("创建告警组成功")
                return True
            else:
                logging.error("创建告警组失败")
                return False
        except BaseException as err:
            logging.error(err)

    def grant_alert_user(self, alert_id, user_id):  # 3.授权告警组
        try:
            grant_alert_user = self.ds_choice + '/dolphinscheduler/alert-group/grant-user'
            params = {'alertgroupId': alert_id,
                      'id': alert_id,
                      'userIds': user_id}
            create = requests.post(grant_alert_user, headers=self.headers,
                                   params=params).json()
            if create['msg'] == 'success':
                logging.info("授权成功")
                return True
            else:
                logging.error("授权失败")
                return False
        except BaseException as err:
            logging.error(err)

    def check_project(self, user):  # 查询项目
        try:
            check_project = self.ds_choice + '/dolphinscheduler/projects/list-paging'
            params = {'pageNo': 1,
                      'pageSize': 20,
                      'searchVal': '{}'.format(user)}
            results = requests.get(check_project, headers=self.headers, params=params).json()
            print(results)
            if results['data']['totalList']:
                alert_id = results['data']['totalList'][0]['id']
                return True, alert_id
            else:
                return False
        except BaseException as err:
            logging.error(err)

    def create_project(self, user):  # 创建项目
        try:
            create_project = self.ds_choice + '/dolphinscheduler/projects/create'
            params = {'projectName': user}
            create = requests.post(create_project, headers=self.headers,
                                   params=params).json()
            if create['msg'] == 'success':
                logging.info("创建账号成功")
                return True
            else:
                logging.error("创建账号成功")
                return False
        except BaseException as err:
            logging.error(err)

    def grant_project(self, project_id, user_id):  # 1. 授权用户资源
        try:
            grant_project = self.ds_choice + '/dolphinscheduler/users/grant-project'
            params = {'projectIds': project_id,
                      'userId': user_id}
            create = requests.post(grant_project, headers=self.headers,
                                   params=params).json()
            if create['msg'] == 'success':
                logging.info("授权项目成功")
                return True
            else:
                logging.error("授权项目失败")
                return False
        except BaseException as err:
            logging.error(err)


if __name__ == '__main__':
    pass


