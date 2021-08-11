# #!/usr/bin/env python3
# # -*- coding: utf8 -*-
# # @Author  : Mr.wang_xi！！
# from open_ldap.tool.mail import *
# from open_ldap.tool.hadoop_mongodb_createuser import *
# from open_ldap.tool.create_passwd import generate_password
# from open_ldap.Open_ldap import *
# from open_ldap.new_dolphinscheduler import DolphinScheduler
# from open_ldap.bastionhost import BastionHost
#
# logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
#                     datefmt='## %Y-%m-%d %H:%M:%S')
# logging.getLogger().setLevel(logging.DEBUG)
#
#
# def dolphinscheduler(username: str, password: str, open_env: str, remark: str, mail_user: str):
#     """
#        :param open_env: 环境变量
#        :param username: 用户名称
#        :param mail_user: 邮箱地址
#        :param remark : 备注
#        :return: 相关记录信息 or False
#     """
#     dolphin = DolphinScheduler(open_env)
#     if not dolphin.check_tenant(username) and not dolphin.check_user(username):  # 查看租户和用户是否存在
#         if dolphin.create_tenant(username, remark):  # 创建租户
#             tenant_id = dolphin.check_tenant(username)[1]  # 创建租户生成的pid
#             if dolphin.create_user(username, password, tenant_id, mail_user):  # 创建用户
#                 if dolphin.create_alert_group(username):  # 创建报警组
#                     if dolphin.check_alert_group(username):  # 查看组是否创建成功
#                         alert_id = dolphin.check_alert_group(username)[1]  # 报警组生成的ID
#                         user_id = dolphin.check_user(username)[1]  # 用户生成的ID
#                         if dolphin.grant_alert_user(alert_id, user_id):  # 授权告警组
#                             if dolphin.create_project(username):  # 创建项目
#                                 project_id = dolphin.check_project(username)[1]  # 查看项目ID
#                                 if dolphin.grant_project(project_id, user_id):  # 授权项目
#                                     logging.info("{}海豚账号{}开通完毕".format(open_env, username))
#     elif dolphin.check_tenant(username) and dolphin.check_user(username):
#         logging.info("{}海豚账号已拥有".format(open_env))
#
#
# def bastion_host(username, bastion_name, password):
#     # """
#     # @param username 用户名
#     # """
#     if Bastion.list_host_accounts(username):
#         print("已拥有主机账号")
#         print(Bastion.list_host_accounts("user_name"))
#         if Bastion.attach_host_accounts_user(Bastion.check_user(bastion_name)[1],
#                                              Bastion.list_host_accounts(username)[2]):
#             print("已授权用户")
#         else:
#             sys.exit(1)
#     else:
#         if Bastion.create_host_account(username, password):
#             if Bastion.list_host_accounts(username):
#                 print("已拥有主机账号")
#                 print(Bastion.list_host_accounts("user_name"))
#                 if Bastion.attach_host_accounts_user(Bastion.check_user(bastion_name)[1],
#                                                      Bastion.list_host_accounts(username)[2]):
#                     print("已授权用户")
#                 else:
#                     sys.exit(1)
#             else:
#                 sys.exit(1)
#         else:
#             sys.exit(1)
#
#
# def Overall_logic(open_env: str, username: str, mail_user: str, remark: str, bastion_name: str, dolphin: str,
#                   add_group: str):
#     """
#        :param open_env: 环境变量
#        :param username: 用户名称
#        :param mail_user: 邮箱地址
#        :param remark : 备注
#        :return: 相关记录信息 or False
#     """
#     try:
#         ldap = Open_Ldap(open_env)
#         gid = ldap.group_gid_number()
#         uid = ldap.user_uid_number()
#         password = generate_password()
#         if project_type == ''
#         if ldap.check_group(username) and ldap.check_user(username):  # 查看用户和组是否存在
#             logging.info("已存在{}环境Open-ldap账号".format(open_env))
#             if BluekingMongoDB().find_user_record(open_env, username):  # 查看MongoDB是否有存储用户信息
#                 password = BluekingMongoDB().find_user_record(open_env, username)[1]
#                 ldap.add_group_to_user(username, add_group)
#                 if dolphin == "yes":
#                     dolphinscheduler(username, password, open_env, remark, mail_user)
#                 else:
#                     logging.info("用户{}不需要海豚调度权限".format(username))
#                 logging.info("堡垒机用户名：{},服务器用户名:{},服务器密码:{}".format(username, bastion_name, password))
#                 bastion_host(username, bastion_name, password)
#                 logging.info("已添加用户：{}到堡垒机".format(bastion_name))
#                 BluekingMongoDB(collection='bastionhost_user_manager').update_record_linux(username,
#                                                                                            hadoop_list[open_env]
#                                                                                            [2],
#                                                                                            hadoop_list[open_env]
#                                                                                            [1],
#                                                                                            hadoop_list[open_env]
#                                                                                            [0],
#                                                                                            bastion_name)
#                 if dolphin == "yes":
#                     dolphinscheduler(username, password, open_env, remark, mail_user)
#                     success_mail(mail_user, username, password, open_env)
#                 else:
#                     success(mail_user, username, password, open_env)
#             else:
#                 logging.info("open—ldap已存在{}用户，但是mongoDB库里面没有密码".format(username))
#                 failed_mail(mail_user)
#         elif not ldap.check_group(username) and not ldap.check_user(username):
#             ldap.add_group(username, gid)  # 创建组
#             if ldap.check_group(username):  # 查看组是否添加成功
#                 ldap.add_user(username, uid, gid, password)  # 创建用户
#                 if ldap.check_user(username):  # 查看用户是否创建成功
#                     ldap.add_group_to_user(username, add_group)  # 用户添加到组里面
#                     if ldap.check_default_group(username):  # 查看组里是否有用户
#                         logging.info("已添加用户：{}到堡垒机".format(username))
#                         if not BluekingMongoDB().find_user_record(open_env, username):
#                             BluekingMongoDB().insert(username, password, open_env, mail_user)
#                             BluekingMongoDB(collection='bastionhost_user_manager').update_record_linux(username,
#                                                                                                        hadoop_list[
#                                                                                                            open_env]
#                                                                                                        [2],
#                                                                                                        hadoop_list[
#                                                                                                            open_env]
#                                                                                                        [1],
#                                                                                                        hadoop_list[
#                                                                                                            open_env]
#                                                                                                        [0],
#                                                                                                        bastion_name)
#                         elif BluekingMongoDB().find_user_record(open_env, username) == "no_hadoop_env":
#                             BluekingMongoDB().update_record(username, open_env, password)
#                             BluekingMongoDB(collection='bastionhost_user_manager').update_record_linux(username,
#                                                                                                        hadoop_list[
#                                                                                                            open_env]
#                                                                                                        [2],
#                                                                                                        hadoop_list[
#                                                                                                            open_env]
#                                                                                                        [1],
#                                                                                                        hadoop_list[
#                                                                                                            open_env]
#                                                                                                        [0],
#                                                                                                        bastion_name)
#                         if dolphin == "yes":
#                             dolphinscheduler(username, password, open_env, remark, mail_user)
#                             success_mail(mail_user, username, password, open_env)
#                         else:
#                             success(mail_user, username, password, open_env)
#         elif ldap.check_group(username) and not ldap.check_user(username):
#             gid = ldap.check_group(username)[1]
#             ldap.add_user(username, uid, gid, password)
#             if ldap.check_user(username):
#                 ldap.add_group_to_user(username, add_group)
#                 if ldap.check_default_group(username):
#                     bastion_host(username, bastion_name, password)
#                     logging.info("已添加用户：{}到堡垒机".format(username))
#                     if not BluekingMongoDB().find_user_record(open_env, username):
#                         BluekingMongoDB().insert(username, password, open_env, mail_user)
#                         BluekingMongoDB(collection='bastionhost_user_manager').update_record_linux(username,
#                                                                                                    hadoop_list[open_env]
#                                                                                                    [2],
#                                                                                                    hadoop_list[open_env]
#                                                                                                    [1],
#                                                                                                    hadoop_list[open_env]
#                                                                                                    [0],
#                                                                                                    bastion_name)
#                     elif BluekingMongoDB().find_user_record(open_env, username) == "no_hadoop_env":
#                         BluekingMongoDB().update_record(username, open_env, password)
#                         BluekingMongoDB(collection='bastionhost_user_manager').update_record_linux(username,
#                                                                                                    hadoop_list[open_env]
#                                                                                                    [2],
#                                                                                                    hadoop_list[open_env]
#                                                                                                    [1],
#                                                                                                    hadoop_list[open_env]
#                                                                                                    [0],
#                                                                                                    bastion_name)
#                     if dolphin == "yes":
#                         dolphinscheduler(username, password, open_env, remark, mail_user)
#                         success_mail(mail_user, username, password, open_env)
#                     else:
#                         success(mail_user, username, password, open_env)
#         elif not ldap.check_group(username) and ldap.check_user(username):
#             if BluekingMongoDB().find_user_record(open_env, username):
#                 password = BluekingMongoDB().find_user_record(open_env, username)[1]
#                 ldap.add_group(username, gid)  # 创建组
#                 if ldap.check_group(username):
#                     ldap.add_group_to_user(username, add_group)  # 项目用户添加到组里面
#                     if ldap.check_default_group(username):  # 查看组里是否有用户
#                         bastion_host(username, bastion_name, password)
#                         logging.info("已添加用户：{}到堡垒机".format(username))
#                         if dolphin == "yes":
#                             dolphinscheduler(username, password, open_env, remark, mail_user)
#                         else:
#                             logging.info("用户{}不需要海豚调度权限".format(username))
#                         BluekingMongoDB(collection='bastionhost_user_manager').update_record_linux(username,
#                                                                                                    hadoop_list[open_env]
#                                                                                                    [2],
#                                                                                                    hadoop_list[open_env]
#                                                                                                    [1],
#                                                                                                    hadoop_list[open_env]
#                                                                                                    [0],
#                                                                                                    bastion_name)
#                         if dolphin == "yes":
#                             dolphinscheduler(username, password, open_env, remark, mail_user)
#                             success_mail(mail_user, username, password, open_env)
#                         else:
#                             success(mail_user, username, password, open_env)
#     except Exception as err:
#         failed_mail(mail_user)
#         logging.info(err)
#
#
#
#
#
# if __name__ == '__main__':
#     username = sys.argv[1]
#     open_env = sys.argv[2]
#     mail_user = sys.argv[3]
#     remark = sys.argv[4]
#     dolphin = sys.argv[5]
#     add_group = sys.argv[6]
#     project_type = sys.argv[7]
#     bastion_name = mail_user.split("@")[0]
#     Bastion = BastionHost(open_env)
#     if Bastion.check_user(bastion_name):
#         Overall_logic(open_env, username, mail_user, remark, bastion_name, dolphin, add_group)
#     else:
#         print("没有堡垒机用户无法添加堡垒机，请先创建堡垒机用户")
#         sys.exit(1)
