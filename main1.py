#!/usr/bin/env python3
# -*- coding: utf8 -*-
# @Author  : Mr.wang_xi！！
from open_ldap2.tool.mail import *
from open_ldap2.tool.hadoop_mongodb_createuser import *
from open_ldap2.tool.create_passwd import generate_password
from open_ldap2.Open_ldap import *
from open_ldap2.new_dolphinscheduler import DolphinScheduler
from open_ldap2.bastionhost import BastionHost

logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='## %Y-%m-%d %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

"""
测试环境    正式环境
项目账号    个人账号
项目账号名称  赋权项目组
申请人
需要海豚账号  不需要海豚账号
申请原因
"""


def dolphinscheduler(username: str, password: str, open_env: str, remark: str, mail_user: str):
    """
       :param open_env: 环境变量
       :param username: 用户名称
       :param mail_user: 邮箱地址
       :param remark : 备注
       :return: 相关记录信息 or False
    """
    dolphin = DolphinScheduler(open_env)
    if not dolphin.check_tenant(username) and not dolphin.check_user(username):  # 查看租户和用户是否存在
        if dolphin.create_tenant(username, remark):  # 创建租户
            tenant_id = dolphin.check_tenant(username)[1]  # 创建租户生成的pid
            if dolphin.create_user(username, password, tenant_id, mail_user):  # 创建用户
                if dolphin.create_alert_group(username):  # 创建报警组
                    if dolphin.check_alert_group(username):  # 查看组是否创建成功
                        alert_id = dolphin.check_alert_group(username)[1]  # 报警组生成的ID
                        user_id = dolphin.check_user(username)[1]  # 用户生成的ID
                        if dolphin.grant_alert_user(alert_id, user_id):  # 授权告警组
                            if dolphin.create_project(username):  # 创建项目
                                project_id = dolphin.check_project(username)[1]  # 查看项目ID
                                if dolphin.grant_project(project_id, user_id):  # 授权项目
                                    logging.info("{}海豚账号{}开通完毕".format(open_env, username))
    elif dolphin.check_tenant(username) and dolphin.check_user(username):
        logging.info("{}海豚账号已拥有".format(open_env))


def bastion_host(username, bastion_name, password):
    if Bastion.list_host_accounts(username):
        logging.info("堡垒机用户已拥有主机账号")
        # print(Bastion.list_host_accounts("user_name"))
        if Bastion.attach_host_accounts_user(Bastion.check_user(bastion_name)[1],
                                             Bastion.list_host_accounts(username)[2]):
            logging.info("堡垒机已授权用户")
        else:
            sys.exit(1)
    else:
        if Bastion.create_host_account(username, password):
            if Bastion.list_host_accounts(username):
                logging.info("堡垒机已拥有主机账号")
                # print(Bastion.list_host_accounts("user_name"))
                if Bastion.attach_host_accounts_user(Bastion.check_user(bastion_name)[1],
                                                     Bastion.list_host_accounts(username)[2]):
                    logging.info("堡垒机已授权用户")
                else:
                    sys.exit(1)
            else:
                sys.exit(1)
        else:
            sys.exit(1)


def Overall_logic(open_env: str, username: str, mail_user: str, remark: str, bastion_name: str, dolphin: str,
                  add_group: str, project_type: str):
    """
       :param open_env: 环境变量
       :param username: 用户名称
       :param mail_user: 邮箱地址
       :param remark : 备注
       :return: 相关记录信息 or False
    """
    try:
        ldap = Open_Ldap(open_env)
        gid = ldap.group_gid_number()
        uid = ldap.user_uid_number()
        password = generate_password()
        project = Project_Open_Ldap(open_env)
        mongo_name = 'bastionhost_user_manager'
        hap = hadoop_list[open_env]
        if project_type == 'project':  # 判断是否是项目账号 如果是项目账号 username == 填写的username
            username = username
        else:
            username = mail_user.split("@")[0]  # 如果是个人账号按照邮箱前缀截取用户名

        if ldap.check_group(username) and ldap.check_user(username):  # 查看用户和组是否存在
            logging.info("已存在{}环境Open-ldap账号".format(open_env))  # 已经添加过账号和组 可能是添加新的项目组或者添加堡垒机账号
            if BluekingMongoDB().find_user_record(open_env, username):  # 查看MongoDB是否有存储用户信息
                password = BluekingMongoDB().find_user_record(open_env, username)[1]  # 抓取MongoDB数据库存储代码
                if project_type == 'project':
                    if project.check_group(username):  # 查询_select账号项目组是否创建
                        logging.info("已拥有{}_select用户组".format(username))
                    else:
                        project.add_group(username)
                else:
                    ldap.add_group_to_user(username, add_group)  # 个人账号添加项目组给账号，
                if dolphin == "yes":
                    dolphinscheduler(username, password, open_env, remark, mail_user)
                else:
                    logging.info("用户{}不需要海豚调度权限".format(username))
                logging.info("堡垒机用户名：{},服务器用户名:{},服务器密码:{}".format(username, bastion_name, password))
                bastion_host(username, bastion_name, password)
                logging.info("已添加用户：{}到堡垒机".format(bastion_name))
                BluekingMongoDB(collection=mongo_name).update_record_linux(username,
                                                                           hap[2], hap[1], hap[0],
                                                                           bastion_name)
                if dolphin == "yes":
                    dolphinscheduler(username, password, open_env, remark, mail_user)
                    success_mail(mail_user, username, password, open_env)
                else:
                    success(mail_user, username, password, open_env)
            else:
                logging.info("open—ldap已存在{}用户，但是mongoDB库里面没有密码".format(username))
                failed_mail(mail_user, "open—ldap已存在{}用户，但是mongoDB库里面没有密码".format(username))
        elif not ldap.check_group(username) and not ldap.check_user(username):
            if project_type == 'project':
                ldap.add_group(username, gid)  # 创建项目组和_select组
                project.add_group(username)
            else:
                ldap.add_group(username, gid)
            if ldap.check_group(username):  # 查看组是否添加成功
                ldap.add_user(username, uid, gid, password)  # 创建用户
                if ldap.check_user(username):  # 查看用户是否创建成功
                    if project_type == "project":
                        logging.info("{}项目用户,不添加其他组权限".format(username))
                    else:
                        ldap.add_group_to_user(username, add_group)  # 用户添加到组里面
                        # if ldap.check_default_group(username):  # 查看组里是否有用户
                    bastion_host(username, bastion_name, password)
                    logging.info("已添加用户：{}到堡垒机".format(username))
                    if not BluekingMongoDB().find_user_record(open_env, username):
                        BluekingMongoDB().insert(username, password, open_env, mail_user)
                        BluekingMongoDB(collection=mongo_name).update_record_linux(username,
                                                                                   hap[2],
                                                                                   hadoop_list[
                                                                                       open_env]
                                                                                   [1],
                                                                                   hadoop_list[
                                                                                       open_env]
                                                                                   [0],
                                                                                   bastion_name)
                    elif BluekingMongoDB().find_user_record(open_env, username) == "no_hadoop_env":
                        BluekingMongoDB().update_record(username, open_env, password)
                        BluekingMongoDB(collection=mongo_name).update_record_linux(username,
                                                                                   hadoop_list[
                                                                                       open_env]
                                                                                   [2],
                                                                                   hadoop_list[
                                                                                       open_env]
                                                                                   [1],
                                                                                   hadoop_list[
                                                                                       open_env]
                                                                                   [0],
                                                                                   bastion_name)
                    if dolphin == "yes":
                        dolphinscheduler(username, password, open_env, remark, mail_user)
                        success_mail(mail_user, username, password, open_env)
                    else:
                        success(mail_user, username, password, open_env)
        elif ldap.check_group(username) and not ldap.check_user(username):
            gid = ldap.check_group(username)[1]
            if project_type == 'project':
                if not project.check_group(username):
                    project.add_group(username)
            ldap.add_user(username, uid, gid, password)
            if ldap.check_user(username):
                if project_type == "project":
                    logging.info("{}项目用户,不添加其他组权限".format(username))
                else:
                    ldap.add_group_to_user(username, add_group)
                # if ldap.check_default_group(username):
                bastion_host(username, bastion_name, password)
                logging.info("已添加用户：{}到堡垒机".format(username))
                if not BluekingMongoDB().find_user_record(open_env, username):
                    BluekingMongoDB().insert(username, password, open_env, mail_user)
                    BluekingMongoDB(collection=mongo_name).update_record_linux(username,
                                                                               hap
                                                                               [2],
                                                                               hap
                                                                               [1],
                                                                               hap
                                                                               [0],
                                                                               bastion_name)
                elif BluekingMongoDB().find_user_record(open_env, username) == "no_hadoop_env":
                    BluekingMongoDB().update_record(username, open_env, password)
                    BluekingMongoDB(collection=mongo_name).update_record_linux(username,
                                                                               hap
                                                                               [2],
                                                                               hap
                                                                               [1],
                                                                               hap
                                                                               [0],
                                                                               bastion_name)
                if dolphin == "yes":
                    dolphinscheduler(username, password, open_env, remark, mail_user)
                    success_mail(mail_user, username, password, open_env)
                else:
                    success(mail_user, username, password, open_env)
        elif not ldap.check_group(username) and ldap.check_user(username):
            if BluekingMongoDB().find_user_record(open_env, username):
                password = BluekingMongoDB().find_user_record(open_env, username)[1]
                if project_type == 'project':
                    ldap.add_group(username, gid)  # 创建组
                    project.add_group(username)
                else:
                    ldap.add_group(username, gid)
                if ldap.check_group(username):
                    if project_type == "project":
                        logging.info("{}项目用户,不添加其他组权限".format(username))
                    else:
                        ldap.add_group_to_user(username, add_group)  # 项目用户添加到组里面
                    # if ldap.check_default_group(username):  # 查看组里是否有用户
                    bastion_host(username, bastion_name, password)
                    logging.info("已添加用户：{}到堡垒机".format(username))
                    if dolphin == "yes":
                        dolphinscheduler(username, password, open_env, remark, mail_user)
                    else:
                        logging.info("用户{}不需要海豚调度权限".format(username))
                    BluekingMongoDB(collection=mongo_name).update_record_linux(username,
                                                                               hap
                                                                               [2],
                                                                               hap
                                                                               [1],
                                                                               hap
                                                                               [0],
                                                                               bastion_name)
                    if dolphin == "yes":
                        dolphinscheduler(username, password, open_env, remark, mail_user)
                        success_mail(mail_user, username, password, open_env)
                    else:
                        success(mail_user, username, password, open_env)
    except Exception as err:
        failed_mail(mail_user, err)
        logging.info(err)


if __name__ == '__main__':
    username = sys.argv[1]
    open_env = sys.argv[2]
    mail_user = sys.argv[3]
    remark = sys.argv[4]
    dolphin = sys.argv[5]
    add_group = sys.argv[6]
    project_type = sys.argv[7]
    bastion_name = mail_user.split("@")[0]
    Bastion = BastionHost(open_env)
    if Bastion.check_user(bastion_name):
        Overall_logic(open_env, username, mail_user, remark, bastion_name, dolphin, add_group, project_type)
    else:
        logging.info("没有堡垒机用户无法添加堡垒机，请先创建堡垒机用户")
        failed_mail(mail_user, "没有堡垒机用户无法添加堡垒机，请先创建堡垒机用户")
        sys.exit(1)
