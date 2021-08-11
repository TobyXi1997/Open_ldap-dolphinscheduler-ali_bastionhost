#!bin/bash
kerberos_user_name=$1
open_env=$2
yum -y install dos2unix &> /dev/null
dos2unix $0 &> /dev/null

if [[ ${open_env} == test ]];then
        kerberos_user_name=$1
        kadmin.local -q "addprinc -pw 156f461616 ${kerberos_user_name}"
        kadmin.local -q "xst -norandkey -k /hwdata/keytab/${kerberos_user_name}.keytab ${kerberos_user_name}@HADOOP.TEST.COM"
        ssh root@172.20.10.63 su - ${kerberos_user_name} -c "pwd"
        scp /hwdata/keytab/${kerberos_user_name}.keytab root@172.20.10.63:/home/${kerberos_user_name}/
        ssh root@172.20.10.63 "chown -R ${kerberos_user_name}:${kerberos_user_name} /home/${kerberos_user_name}"
else
        echo "${open_env}"
fi
