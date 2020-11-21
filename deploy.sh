#!/bin/bash
########################################################
### @brief    deploy modifier
### @depend   tools/common/gen_proto.sh
### @author   wenchyzhu(wenchyzhu@gmail.com)
### @date     2018-05-01
########################################################

function Usage()
{
    echo ""
    echo "Usage: $0 <ENV> [DESTINATION] [XLS_CONF_DIR] [USERNAME] [VERSION] [VERSION_NAME]"
    echo ""
    echo "ENV部署的环境"
    echo ""
    python -c "import config;config.help()"

    echo ""
    echo "（可选参数）SERVER默认推送到的服务器"
    echo ""
    echo "  local: 本地"
    echo " devnet: 开发网"
    echo " idcnet: 外网"

    echo ""
    echo "（可选参数）XLS_CONF_DIR: 策划配置目录"

    echo ""
    echo "（可选参数）USERNAME: 部署人姓名"

    echo ""
    echo "（可选参数）VERSION版本号: 点分十进制表示"
}

function GenXls()
{
    if [[ "$XLS_CONF_DIR" == "" ]]; then
        echo "未设置xls目录，不拉取策划配置表了"
        return
    fi
    cd $(dirname $0)
    CUR_ABS_PATH=$(cd `dirname $0`; pwd)
    XLS_DIR=${CUR_ABS_PATH}/static/xls
    if [[ -d $XLS_DIR ]];then
        rm -rfv $XLS_DIR
    fi
    mkdir ${XLS_DIR}
    # TODO(wenchyzhu): 依据环境来拉取对应的策划配置
    # 暂时都默认使用：开发环境配置，后续如果确有需要依据环境来拉取配置再做处理
    if [[ "$DESTINATION" == "local" ]]; then
        cp -rfv ${CUR_ABS_PATH}/../config_maker/xls/*xls* ${XLS_DIR}
        echo "copy design conf from ${CUR_ABS_PATH}/../config_maker/xls"
    else
        $URL=svn.xxx.com
        svn export --force $URL/${XLS_CONF_DIR} ${XLS_DIR}
        echo "export design conf"
    fi
    echo "生成xls目录"
}

function GenVersionInfo()
{
    ## svn
    # version_name=`svn info | grep '^URL:' | egrep -o '(tags|branches)/[^/]+|trunk' | egrep -o '[^/]+$'`
    # version_revision=r`svn info | grep -E '最后修改的版本|Last Changed Rev' | cut -d ':' -f 2 |  tr -d [:space:]`

    ## git
    if [ "$VERSION_NAME" == "" ]; then
        VERSION_NAME=`git symbolic-ref --short -q HEAD`
    fi
    version_revision=`git log --pretty=format:'%h' -n 1`

    deployer="${USERNAME} at `date "+%Y-%m-%d %H:%M:%S"`"
    # replace some fields
    sed -i "s#_VERSION_#${VERSION_NAME}\ ${version_revision},\ ${XLS_CONF_DIR}#g" ${LOCAL_PATH}/template/header.tpl
    sed -i "s#_DEPLOYER_#${deployer}#g" ${LOCAL_PATH}/template/header.tpl
}

function GenProtobuf()
{
    cd $(dirname $0)
    CUR_ABS_PATH=$(cd `dirname $0`; pwd)
    ${CUR_ABS_PATH}/../common/gen_proto.sh || exit -1
    echo "生成python的common库目录"
}

function GenLocal()
{
    cd $(dirname $0)
    echo ${LOCAL_PATH}
    if [ ! -d $LOCAL_PATH ];then
        mkdir -p $LOCAL_PATH
    fi
    rsync -avz ../common ${LOCAL_PATH}/ --delete
    rsync -avz ./* ${LOCAL_PATH}/ --delete
    # 生成版本信息
    GenVersionInfo
}

function GenAll()
{
    cd $(dirname $0)
    GenProtobuf
    GenXls
    GenLocal $LOCAL_PATH
    sed -i "/VENV_NAME/s/unknown/${DEPLOY_ENV}/g" ${LOCAL_PATH}/config.py
}

function PushRemote()
{
    cd $(dirname $0)
    echo ${DEST_IP} ${DEST_PATH}
    # stop
    bifrost_cmd ${DEST_IP} "cd ${DEST_PATH} && ./startstop.sh stop"
    bifrost_rsync ${DEST_IP} ${LOCAL_PATH}/ ${DEST_PATH}/
    # start
    bifrost_cmd ${DEST_IP} "cd ${DEST_PATH} && ./startstop.sh start"
}

#################### main ####################
# color
COLOR_RED='\033[0;31m'
COLOR_RESET='\033[0m'

# default global conf
LOCAL_PATH="$(dirname $0)/../.tmp/lab_modifier"
DEST_IP="10.125.52.45"
DEST_PATH="/data/home/user00/tornado/lab_modifier"
DEPLOY_ENV="lab"
DESTINATION="devnet"
XLS_CONF_DIR="开发环境配置表"
VERSION=""
VERSION_NAME=""
USERNAME="${USER}"

dev_envs=("lab" "dev" "large_dev" "lab2")

# parse params
if [ $# -eq 1 ]; then
    DEPLOY_ENV="$1"
    # auto decide deploy destination
    DESTINATION="idcnet"
    for env in ${dev_envs[@]}
    do
        if [ $DEPLOY_ENV == $env ]
        then
            DESTINATION="devnet"
            break
        fi
    done

elif [ $# -ge 2 ]; then
    DEPLOY_ENV="$1"
    DESTINATION="$2"

    if [ $# -ge 3 ]; then
        XLS_CONF_DIR="$3"
    fi

    if [ $# -ge 4 ]; then
        USERNAME="$4"
    fi

    if [ $# -ge 5 ]; then
        VERSION="$5"
    fi

    if [ $# -ge 6 ]; then
        VERSION_NAME="$6"
    fi
    
    if [[ $DESTINATION != "local" && $DESTINATION != "devnet" && $DESTINATION != "idcnet" ]]; then
        echo "illegal param: $DESTINATION"
        Usage
        exit -1
    fi
else
    Usage
    exit -1
fi

# set common variables
DEPLOY_NAME=${DEPLOY_ENV}_modifier
LOCAL_PATH="$(dirname $0)/../.tmp/${DEPLOY_NAME}"
DEST_PATH="/data/home/user00/tornado/${DEPLOY_NAME}"
DEST_IP="10.125.52.45"

# generate modifier
GenAll

if [[ "$VERSION" == "" ]]; then
    TGZ_NAME="${DEPLOY_NAME}.tgz"
else
    TGZ_NAME="${DEPLOY_NAME}_${VERSION}.tgz"
fi

# deploy modifier
if [[ "$DESTINATION" == "local" ]]; then
    cd ../.tmp/ && tar -czvf ${TGZ_NAME} ${DEPLOY_NAME} && cd -
    echo -e "----- Deploy Info -----
     DEPLOY_NAME: $DEPLOY_NAME
      LOCAL_PATH: $LOCAL_PATH
         DEST_IP: local
       DEST_PATH: ../.tmp/${TGZ_NAME}
    XLS_CONF_DIR: $XLS_CONF_DIR"

elif [[ "$DESTINATION" == "devnet" ]]; then
    PushRemote $LOCAL_PATH $DEST_IP $DEST_PATH
    echo -e "----- Deploy Info -----
     DEPLOY_NAME: $DEPLOY_NAME
      LOCAL_PATH: $LOCAL_PATH
         DEST_IP: $DEST_IP
       DEST_PATH: $DEST_PATH
    XLS_CONF_DIR: $XLS_CONF_DIR
             URL: http://xxx.com/${DEPLOY_ENV}/"

elif [[ "$DESTINATION" == "idcnet" ]]; then
    cd ../.tmp/ && tar -czvf ${TGZ_NAME} ${DEPLOY_NAME} && cd -
    echo -e "----- Deploy Info -----
     DEPLOY_NAME: $DEPLOY_NAME
      LOCAL_PATH: $LOCAL_PATH
         DEST_IP: 9.3.40.32
       DEST_PATH: /data/home/user00/tornado
    XLS_CONF_DIR: $XLS_CONF_DIR
             URL: http://xxx.com/${DEPLOY_ENV}/"
    postfile ../.tmp/TGZ_NAME
fi
