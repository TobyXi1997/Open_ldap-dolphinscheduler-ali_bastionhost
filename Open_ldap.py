from ldap3 import *
from ldap3 import Server, Connection, ALL, SUBTREE
import random
import sys
import logging

from open_ldap2.config.configuration_file import *
from open_ldap2.config.password import ldap_password
from ldap3.utils.hashed import hashed


class Open_Ldap(object):
    """
     @param user_name用户名和组名称
     @param uid_num 用户必须生成的uid不允许重复
     @param gid_num 生成组必须要的id生成以后必须要讲uid绑定在gid里面，不允许重复
     @param password 自动生成密码
     @param 连接open-ldap生成uid和gid以后查询组是否存在——>查询用户是否存在
     @param 默认直接加入default组里
     @param 密码默认是明文，uid登录只能看到自己的密码，看不到别人的密码
     @param open_env 正式环境还是测试环境
     @param 如果要修改Open_ldap代码一定也要修改代码库代码，不然会出问题
     """
    logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='## %Y-%m-%d %H:%M:%S')
    logging.getLogger().setLevel(logging.DEBUG)

    def __init__(self, open_env):  # 初始化登录open-ldap服务器
        try:
            self.host = ldap[open_env]  # ad host
            self.user = ldap_user  # 管理员
            self.password = ldap_password  # 密码
            self.server, self.conn = self._connect()
        except Exception as err:
            logging.error(err)
            sys.exit(1)

    def _connect(self):  # 连接AD
        try:
            server = Server(self.host, get_info=ALL)
            conn = Connection(server, user=self.user, password=self.password, auto_bind=True)
            if not conn.bind():
                logging.error('error in bind', conn.result)
            else:
                return server, conn
        except Exception as err:
            logging.error(err)
            sys.exit(1)

    def add_user(self, user_name: str, uid_num: int, gid_num: int, password: str):  # 添加用户
        try:
            hashed_password = hashed(HASHED_SALTED_MD5, password)
            self.conn.add('uid={},ou=People,dc=hadoop,dc=com'.format(user_name),
                          ['inetOrgPerson', 'posixAccount', 'shadowAccount', 'top'],
                          {'uid': '{}'.format(user_name),
                           'sn': '{}'.format(user_name),
                           'homeDirectory': '/home/{}'.format(user_name),
                           'loginShell': '/bin/bash',
                           'cn': '{}'.format(user_name),
                           'uidNumber': '{}'.format(uid_num),
                           'gidNumber': '{}'.format(gid_num),
                           'userPassword': hashed_password,
                           'displayName': '{}'.format(user_name),
                           'shadowFlag': '0',
                           'shadowMin': '0',
                           'shadowMax': '99999',
                           'shadowInactive': '99999',
                           'shadowLastChange': '12011',
                           'shadowExpire': '99999'
                           })
            # self.conn.extend.microsoft.modify_password('uid={},ou=People,dc=ygyg,dc=cn'.format(user),
            # "adfWQSAD.df124")
        except Exception as err:
            logging.error(err)
            sys.exit(1)

    def add_group(self, user_name: str, gid_num):  # 添加组用户
        try:
            self.conn.add('cn={},'
                          'ou=Group,'
                          'dc=hadoop,'
                          'dc=com'.format(user_name),
                          ['posixGroup', 'top'],
                          {'cn': user_name, 'gidNumber': gid_num, 'memberUid': [user_name]})
            logging.info("已创建{}组，用户是项目用户".format(user_name, user_name))
        except Exception as err:
            logging.error(err)
            sys.exit(1)

    def add_group_to_user(self, user_name: str, add_group: str):  # 增加用户到Group组下，默认添加default别的组用户自己填写
        try:
            group = ["default"]
            if add_group != "None":
                group.extend(add_group.split(","))
                for i in group:
                    if i == "default":
                        dn = ['CN={},OU=Group,DC=hadoop,DC=com'.format(i)]
                        attribute = 'memberUid'
                        self.conn.modify(dn, {attribute: [(MODIFY_ADD, [user_name])]})
                    else:
                        dn = ['CN={}_select,OU=Group,DC=hadoop,DC=com'.format(i)]
                        attribute = 'memberUid'
                        self.conn.modify(dn, {attribute: [(MODIFY_ADD, [user_name])]})
                        logging.info("Open_ldap已授权{}_select组".format(i))
            else:
                dn = ['CN={},OU=Group,DC=hadoop,DC=com'.format("default")]
                attribute = 'memberUid'
                self.conn.modify(dn, {attribute: [(MODIFY_ADD, [user_name])]})
        except Exception as err:
            logging.error(err)
            sys.exit(1)

    def user_uid_number(self):  # 随机生成一个open-ldap里面没有的uid
        try:
            entry_list = self.conn.extend.standard.paged_search(search_base='ou=People,dc=hadoop,dc=com',
                                                                search_filter='(objectClass=posixAccount)',
                                                                search_scope=SUBTREE,
                                                                attributes=['uidNumber'],
                                                                paged_size=None,
                                                                generator=False)
            while True:
                list_0 = [entry['attributes']['uidNumber'] for entry in entry_list]
                num = random.randint(1, 999999)
                if num in list_0:
                    continue
                else:
                    return num
        except BaseException as err:
            logging.error(err)
            sys.exit(1)

    def group_gid_number(self):  # 随机生成一个open-ldap里面没有的gid
        try:
            entry_list = self.conn.extend.standard.paged_search(search_base='ou=People,dc=hadoop,dc=com',
                                                                search_filter='(objectClass=posixAccount)',
                                                                search_scope=SUBTREE,
                                                                attributes=['gidNumber'],
                                                                paged_size=None,
                                                                generator=False)
            while True:
                list_0 = [entry['attributes']['gidNumber'] for entry in entry_list]
                num = random.randint(1, 999999)
                if num in list_0:
                    continue
                else:
                    return num
        except Exception as err:
            logging.error(err)
            sys.exit(1)

    def check_group(self, user_name: str):  # 查看组是否存在
        try:
            entry_list = self.conn.extend.standard.paged_search(search_base='ou=Group,dc=hadoop,dc=com',
                                                                search_filter='(objectClass=posixGroup)',
                                                                search_scope=SUBTREE,
                                                                attributes=['cn', 'gidNumber', 'memberUid'],
                                                                paged_size=None,
                                                                generator=False)
            list_0 = [entry['attributes']['cn'][0] for entry in entry_list]
            list_1 = [entry['attributes']['gidNumber'] for entry in entry_list]
            # print(entry_list[0])
            dictionary = dict(zip(list_0, list_1))
            # print(dictionary)
            if user_name in dictionary:
                logging.info("Group下已拥有{}组，返回组gid".format(user_name))
                return True, dictionary[user_name]
            else:
                logging.info("Group组下未用{}组，准备添加")
                return False
        except Exception as err:
            logging.error(err)
            sys.exit(1)

    def check_default_group(self, user_name: str):  # 查看default组里面是否拥有用户
        try:
            entry_list = self.conn.extend.standard.paged_search(search_base='cn=default,ou=Group,dc=hadoop,dc=com',
                                                                search_filter='(objectClass=posixGroup)',
                                                                search_scope=SUBTREE,
                                                                attributes=['memberUid'],
                                                                paged_size=None,
                                                                generator=False)
            list_0 = [entry['attributes']['memberUid'] for entry in entry_list]
            if user_name in list_0[0]:
                logging.info("Default组里已拥有{}账号".format(user_name))
                return True
            else:
                logging.error("Default组里未拥有{}账号".format(user_name))
                sys.exit(1)
        except Exception as err:
            logging.error(err)
            sys.exit(1)

    def check_user(self, user_name: str):  # 查看user用户是否存在
        try:
            entry_list = self.conn.extend.standard.paged_search(search_base='ou=People,dc=hadoop,dc=com',
                                                                search_filter='(objectClass=posixAccount)',
                                                                search_scope=SUBTREE,
                                                                attributes=['uid'],
                                                                paged_size=None,
                                                                generator=False)
            list_0 = [entry['attributes']['uid'][0] for entry in entry_list]
            if user_name in list_0:
                logging.info("查询用户：{}已存在People组里".format(user_name))
                return True
            else:
                logging.info("查询用户：{}不存在People组里,准备开始添加用户".format(user_name))
                return False
        except Exception as err:
            logging.error(err)
            sys.exit(1)

    def grant_password(self, username, password):  # 修改密码操作
        hashed_password = hashed(HASHED_SALTED_MD5, password)
        self.conn.modify('uid={},ou=People,dc=hadoop,dc=com'.format(username),
                         {'userPassword': [(MODIFY_REPLACE, ['{}'.format(hashed_password)])]})
        print("{} password updated and the password is {}".format(username, password))


class Project_Open_Ldap(Open_Ldap):
    """
    @param: 以下两个方法是重构方法
    """
    def __init__(self, open_env):
        """
        @param open_env 环境变量
        """
        super(Project_Open_Ldap, self).__init__(open_env)
        # self._connect()
        self.group_gid_number()

    def add_group(self, user_name: str, *args):  # 添加Select组用户
        """
        @param user_name 用户名
        @param 如果是项目组默认添加_select用户
        """
        try:
            self.conn.add('cn={}_select,'
                          'ou=Group,'
                          'dc=hadoop,'
                          'dc=com'.format(user_name),
                          ['posixGroup', 'top'],
                          {'cn': user_name + '_select', 'gidNumber': self.group_gid_number()})
            logging.info("已创建{}组和{}_select组，用户是项目用户".format(user_name, user_name))
        except Exception as err:
            logging.error(err)
            sys.exit(1)

    def check_group(self, user_name: str):  # 查看组是否存在
        try:
            entry_list = self.conn.extend.standard.paged_search(search_base='ou=Group,dc=hadoop,dc=com',
                                                                search_filter='(objectClass=posixGroup)',
                                                                search_scope=SUBTREE,
                                                                attributes=['cn', 'gidNumber', 'memberUid'],
                                                                paged_size=None,
                                                                generator=False)
            list_0 = [entry['attributes']['cn'][0] for entry in entry_list]
            list_1 = [entry['attributes']['gidNumber'] for entry in entry_list]
            # print(entry_list[0])
            dictionary = dict(zip(list_0, list_1))
            # print(dictionary)
            if user_name + '_select' in dictionary:
                logging.info("Group下已拥有{}_select组，返回组gid".format(user_name))
                return True, dictionary[user_name]
            else:
                logging.info("Group组下未用{}_select组，准备添加")
                return False
        except Exception as err:
            logging.error(err)
            sys.exit(1)


if __name__ == '__main__':
    pass

