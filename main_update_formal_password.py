#!/usr/bin/env python3
# -*- coding: utf8 -*-
# @Author  : Mr.wang_xi！！
from open_ldap2.tool.mail import *
from open_ldap2.tool.hadoop_mongodb_createuser import *
from open_ldap2.tool.create_passwd import generate_password
from open_ldap2.Open_ldap import *
from open_ldap2.bastionhost import BastionHost


def bastion_host(ldap_user, bastion_name, password):
    if Bastion.list_host_accounts(ldap_user):
        print("已拥有主机账号")
        # print(Bastion.list_host_accounts("user_name"))
        if Bastion.attach_host_accounts_user(Bastion.check_user(bastion_name)[1],
                                             Bastion.list_host_accounts(ldap_user)[2]):
            print("已授权用户")
        else:
            sys.exit(1)
    else:
        if Bastion.create_host_account(ldap_user, password):
            if Bastion.list_host_accounts(ldap_user):
                print("已拥有主机账号")
                # print(Bastion.list_host_accounts("user_name"))
                if Bastion.attach_host_accounts_user(Bastion.check_user(bastion_name)[1],
                                                     Bastion.list_host_accounts(ldap_user)[2]):
                    print("已授权用户")
                else:
                    sys.exit(1)
            else:
                sys.exit(1)
        else:
            sys.exit(1)


if __name__ == "__main__":
    # 修改open-ldap正式环境用户账号密码
    ldap = Open_Ldap("formal")
    Bastion = BastionHost("formal")
    for i in open("config/user.txt"):
        password = generate_password()
        user = i.split()
        ldap_user = user[0]
        mail_user = user[1]
        print(ldap_user, password, mail_user)
        ldap.grant_password(ldap_user, password)
        if not BluekingMongoDB().find_user_record("formal", ldap_user):
            BluekingMongoDB().insert(ldap_user, password, "formal", mail_user)
        elif BluekingMongoDB().find_user_record("formal", ldap_user) == "no_hadoop_env":
            BluekingMongoDB().update_record(ldap_user, "formal", password)
        success(mail_user, user, password, "formal")
