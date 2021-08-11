#!/usr/bin/env python3
# -*- coding:utf-8 -*-


import logging
import sys
from datetime import datetime

from pymongo import MongoClient
from open_ldap2.config.password import mongo_db

# from mongodb_user_util_kit.config import bluekingMongodbInfo

'''
# if os.path.isdir(r'/hwdata/ops/logs/bk_mongodb_user_logs/') is False:
#    os.makedirs(r'/hwdata/ops/logs/bk_mongodb_user_logs/')
#
# logging.basicConfig(level=logging.INFO,
#                    filename=(r'/hwdata/ops/logs/bk_mongodb_user_logs/bk_mongodb_user_%s.log' % (datetime.now().strftime('%Y-%m-%d'))),
#                    format='[%(asctime)s] [%(levelname)s] [%(funcName)s]: %(message)s'
#                    )
'''


class BluekingMongoDB:
    def __init__(self, collection='hadoop_user'):
        self.collection = collection

    @property
    def __client(self):
        """
        连接蓝鲸平台mongodb, 运维人员使用, 用来写入记录保存至permission库
        :return: 蓝鲸平台mongodb permission.hadoop_user
        """
        user_name = mongo_db[0]
        passwd = mongo_db[1]
        instance = mongo_db[2]
        db = mongo_db[3]
        blueking_database_client = MongoClient(
            'mongodb://{user_name}:{passwd}@{instance}/?authSource={db}&authMechanism=SCRAM-SHA-1'.format(
                user_name=user_name,
                passwd=passwd,
                instance=instance,
                db=db
            ))
        blueking_permission_db = blueking_database_client.permission
        blueking_permission_collection = blueking_permission_db[self.collection]
        return blueking_permission_collection

    def insert(self, username: str, password: str, hadoop_env: str, user_mail: str):
        """
        插入记录
        @param username: 用户名
        @param password: 密码
        @param hadoop_env: hadoop环境
        @param user_mail:邮箱
        """
        now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_record_info = {
            "user_name": "{}".format(username),
            "hadoop_env":
                {"{}".format(hadoop_env): "{}".format(password)},
            "mail": "{}".format(user_mail),
            "create_time": "{}".format(now_time),
            "update_time": "{}".format(now_time)
        }
        try:
            client = self.__client
            client.insert_one(insert_record_info)
            logging.info('蓝鲸平台mongodb permission.hadoop_user新增记录成功, 记录为{}'.format(insert_record_info))
            return True
        except Exception as e:
            logging.error('程序运行错误: {}'.format(e))
            sys.exit(1)

    def find_user_record(self, hadoop_env: str, username: str):
        """
        查看文档中是否存在条件为"user_name": user, "instance_id.db": db相关记录
        :param username: 账号名
        :hadoop_env: 环境
        """
        client = self.__client
        user_info_record = client.find_one({"user_name": "{}".format(username)})
        # print(user_info_record['hadoop_env'])
        if not user_info_record:
            logging.info("mongoDB没有{}用户".format(username))
            return None
        elif hadoop_env in user_info_record['hadoop_env']:
            return True, user_info_record['hadoop_env'][hadoop_env]
        elif hadoop_env not in user_info_record['hadoop_env']:
            return "no_hadoop_env"
        else:
            pass

    @staticmethod
    def now_time():
        now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return now_time

    def update_record(self, username: str, hadoop_env: str, password):
        """
        update record value.
        :param username:
        :param hadoop_env:
        :param password:
        :return: True or False
        """
        now_time = BluekingMongoDB.now_time()
        update_record_info = (
            {'user_name': "{}".format(username)},
            {"$set": {
                "hadoop_env.{}".format(hadoop_env): "{}".format(password),
                "update_time": "{}".format(now_time)}})
        try:
            client = self.__client
            client.update_one(*update_record_info)
            logging.info('Blueking mongodb update {username} user record success.'.format(username=username))
            return True
        except Exception as error:
            logging.error('Blueking mongodb update {username} user record failed! error info: {error}'.format(
                username=username, error=error
            ))
            return False

    def update_record_linux(self, username: str, public_address: str, private_address: str, instances_id: str,
                            bastion_name: str) -> object:
        """
        update record value.
        :param username: hadoop用户名
        :param bastion_name: 堡垒机用户名
        :param public_address:
        :param private_address:
        :param instances_id:
        :return: True or False
        """
        now_time = BluekingMongoDB.now_time()
        update_record_info = (
            {'user_name': "{}".format(bastion_name),
             },
            {"$addToSet": {"instances": {instances_id: {
                "public_address": public_address,
                "private_address": private_address,
                "hadoop_user_name": username,
                "expired_time": "{}".format(now_time),
            }}}}
        )

        try:
            client = self.__client
            client.update_one(*update_record_info)
            logging.info('Blueking mongodb update {username} user record success.'.format(username=username))
            return True
        except Exception as error:
            logging.error('Blueking mongodb update {username} user record failed! error info: {error}'.format(
                username=username, error=error
            ))
            return False


if __name__ == "__main__":
    pass
    #BluekingMongoDB(collection='bastionhost_user_manager').update_record_linux()