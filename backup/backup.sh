#!/bin/bash
ip1="10.5.1.127"
passwd1="qwe-123"
appnames1='erp mes mneuron oa'
appdbs1='meserp mneuron oa-db xc'

ip2="10.5.1.128"
passwd2="qwe-123"
appnames2='fpc-mes iot smes'
appdbs2='fpcmes iot smes'

ip3="10.5.1.129"
passwd3="qwe-123"
appnames3='dnc-cloud iot-registry platform-service rabbitmq sso'
appdbs3='dnc-cloud-db kong-db sso-db'


DATE=`date +%F-%H%M%S`
for i in 1 2 3
do
    eval ip='$'"ip$i "
    eval passwd='$'"passwd$i"
    eval appnames='$'"appnames$i"
    eval appdbs='$'"appdbs$i"
    # app部分
    for appname in ${appnames}
    do
        echo ${appnames}
        sudo mkdir -p /backup/app/$appname

        /usr/bin/expect <<-EOF
            set time 30
            spawn sudo scp -r root@$ip:/srv/docker/app/$appname /backup/app/$appname
            expect {
            "*yes/no" { send "yes\r";exp_continue}
            "*password" { send "$passwd\r" }
            }
            set timeout 3000
            expect eof
        EOF
    done
    for appname in $appnames
    do
        echo $appname
        cd /backup/app/$appname/ && tar czvf ${appname}_backup_${DATE}_$ip.tar.gz $appname && rm -r $appname &
    done

    # db部分
    for appdb in $appdbs
    do
        sudo mkdir -p /backup/db/$appdb
        /usr/bin/expect <<-EOF
            set time 30
            spawn sudo scp -r root@$ip:/srv/docker/db/$appdb /backup/db/$appdb
            expect {
            "*yes/no" { send "yes\r";exp_continue}
            "*password" { send "$passwd\r" }
            }
            set timeout 3000
            expect eof
        EOF
    done
    for appdb in $appdbs
    do
        echo $appdb
        cd /backup/db/$appdb/ && tar czvf ${appdb}_backup_${DATE}_$ip.tar.gz $appdb && rm -r $appdb &
    done
done
wait
echo "backup success"