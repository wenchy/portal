#!/usr/bin/bash
########################################################
### @brief    startstop switch for tornado app
### @depend
### @author   wenchyzhu(wenchyzhu@gmail.com)
### @date     2018-05-07
########################################################
function Usage()
{
    echo "Usage: $0 [start|stop|restart] [singleprocess|multiprocess]"
}

OPERATION='stop'
START_MODE="singleprocess"

# parse params
if [ $# -eq 1 ]; then
    OPERATION="$1"
elif [ $# -ge 2 ]; then
    OPERATION="$1"
    START_MODE="$2"
else
    Usage
    exit -1
fi

function GetEnv()
{
    env_dir=`pwd  | awk -F "/" '{print $NF}'`
    # %_* 表示从右边开始查找，删除第一个找到的`_`及右边的字符
    env=${env_dir%_*}
    echo $env
}

function TailLog()
{
    if [[ ! -f "app.log" ]]; then
        echo "--------------------"
        tail app.log
        echo ""
        echo "--------------------"
    fi
}

function Start()
{
    echo "----- Start modifier app -----"
    cd $(dirname $0)
    env=`GetEnv`
    case ${env} in
        dev)
          START_MODE="multiprocess"
          ;;
        *)
          echo "not specified env: ${env}, use start mode: ${START_MODE}"
    esac
    echo "env: $env, start mode: $START_MODE"
    echo "starting..."

    nohup python app.py $START_MODE ${env} > nohup.log 2>&1 &
    echo $! > .app.pid
    sleep 5 # sleep for 5 seconds, and then check if process has started successfully
    PID=`cat .app.pid`
    eval $(ps -ejf | awk -v PID=$PID -F" " '{if ($2 == PID) printf("PGID=%s", $4)}')
    if [[ $PGID == "" ]]; then
        echo "PID: $PID, PGID: not found"
        echo "Start Failed"
        exit -1
    else
        echo "PID: $PID, PGID: $PGID"
        echo "Start Success"
    fi
}

function Stop()
{
    echo "----- Stop modifier app -----"
    cd $(dirname $0)
    # kill process id, only for tornado single-process mod
    # kill -TERM `cat .app.pid`

    # kill process group id, for both tornado multi-process and single-process mode
    PID=`cat .app.pid`
    eval $(ps -ejf | awk -v PID=$PID -F" " '{if ($2 == PID) printf("PGID=%s", $4)}')
    if [[ $PGID == "" ]]; then
        echo "PID: $PID, PGID: not found"
        echo "Stop Failed"
    else
        echo "PID: $PID, PGID: $PGID"
        kill -TERM -- -$PGID
        # sleep 3 # sleep for 5 seconds
        echo "Stop Success"
    fi
}

# avoid inappropriate Language Configuration
export LC_ALL="en_US.UTF-8"

case ${OPERATION} in
    start)
        Start
        ;;
    stop)
        Stop
        ;;
    restart)
        Stop
        Start
        ;;
    *)
        echo "invalid args!"
        Usage
        exit -1
esac
