#!/usr/bin/bash
# set -e

function Usage()
{
    echo "Usage: $0 [start|stop|restart] [singleprocess|multiprocess]"
}

OPERATION='stop'
MODE="singleprocess"

# parse params
if [ $# -eq 1 ]; then
    OPERATION="$1"
elif [ $# -ge 2 ]; then
    OPERATION="$1"
    MODE="$2"
else
    Usage
    exit 1
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
    echo "----- starting... -----"
    cd $(dirname $0)
    env=`GetEnv`
    case ${env} in
        prod)
          MODE="multiprocess"
          ;;
        *)
          echo "not specified env: ${env}, use start mode: ${MODE}"
    esac
    echo "env: $env, start mode: $MODE"

    nohup python3 app.py ${MODE} ${env} > nohup.log 2>&1 &
    echo $! > .app.pid
    sleep 1 # sleep N seconds, and then check if process already started successfully
    PID=`cat .app.pid`
    eval $(ps -ejf | awk -v PID=$PID -F" " '{if ($2 == PID) printf("PGID=%s", $4)}')
    if [[ $PGID == "" ]]; then
        echo "start failed: PID: $PID, PGID: not found"
        exit 1
    else
        echo "PID: $PID, PGID: $PGID"
        echo "start succeed"
    fi
}

function Stop()
{
    echo "----- stopping... -----"
    cd $(dirname $0)
    # kill process id, only for tornado single-process mod
    # kill -TERM `cat .app.pid`

    # kill process group id, for both tornado multiprocess and singleprocess mode
    PID=`cat .app.pid`
    eval $(ps -ejf | awk -v PID=$PID -F" " '{if ($2 == PID) printf("PGID=%s", $4)}')
    if [[ $PGID == "" ]]; then
        echo "already stopped: PID: $PID, PGID: not found"
        echo "stop succeed"
    else
        echo "PID: $PID, PGID: $PGID"
        kill -TERM -- -$PGID
        sleep 1
        echo "stop succeed"
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
        exit 1
esac
