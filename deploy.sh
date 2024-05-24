#!/bin/bash

set -e

function Usage() {
    echo ""
    echo "Usage: $0 <ENV> [DEST] [USERNAME] [VERSION] [TAG]"
    echo ""
    echo "ENV部署的环境"
    echo ""
    python -c "import config;config.help()"

    echo ""
    echo "（可选参数）SERVER默认推送到的服务器"
    echo ""
    echo "  local: 本地"
    echo " devtool: 开发网"
    echo " idctool: 外网"

    echo ""
    echo "（可选参数）USERNAME: 部署人姓名"

    echo ""
    echo "（可选参数）VERSION版本号: 点分十进制表示"
}

ROOT_DIR=$(git rev-parse --show-toplevel)

function GenProtobuf() {
    cd ${ROOT_DIR}
    ./scripts/genpb.sh
    echo "generate protobuf for python"
}

function GenLocal() {
    echo ${LOCAL_PATH}
    rm -rf $LOCAL_PATH
    mkdir -p $LOCAL_PATH
    rsync -avz $ROOT_DIR/* ${LOCAL_PATH}/ --delete
}

function GenVersionInfo() {
    ## git
    if [ "$TAG" == "" ]; then
        TAG=$(git symbolic-ref --short -q HEAD)
    fi
    commit=$(git log --pretty=format:'%h' -n 1)
    deployer="${USERNAME} at $(date "+%Y-%m-%d %H:%M:%S")"
    # replace some fields
    sed -i "s#_VERSION_#${TAG}\ ${commit}#g" ${LOCAL_PATH}/template/header.html
    sed -i "s#_DEPLOYER_#${deployer}#g" ${LOCAL_PATH}/template/header.html
}

function GenAll() {
    cd $(dirname $0)
    GenProtobuf
    GenLocal $LOCAL_PATH
    GenVersionInfo
    sed -i "/VENV_NAME/s/unknown/${DEPLOY_ENV}/g" ${LOCAL_PATH}/config.py
}

function TarTgz() {
    cd $ROOT_DIR/.tmp/
    if [ -x "$(command -v pigz)" ]; then
        echo "--use-compress-program=pigz"
        tar cavfh - ${DEPLOY_NAME} | pigz >${TGZ_NAME}
    else
        tar cavfh ${TGZ_NAME} ${DEPLOY_NAME}
    fi
}

function PushRemote() {
    cd $(dirname $0)
    echo ${DEST_IP} ${DEST_PATH}
    # TODO
}

#################### main ####################
# color
COLOR_RED='\033[0;31m'
COLOR_RESET='\033[0m'

# default global conf
DEPLOY_ENV="dev"
DEST="local"
VERSION=""
TAG=""
USERNAME="${USER}"

dev_envs=("dev" "test" "lab")

# parse params
if [ $# -eq 1 ]; then
    DEPLOY_ENV="$1"
    # auto decide deploy destination
    DEST="local"
    for env in ${dev_envs[@]}; do
        if [ $DEPLOY_ENV == $env ]; then
            DEST="local"
            break
        fi
    done

elif [ $# -ge 2 ]; then
    DEPLOY_ENV="$1"
    DEST="$2"

    if [ $# -ge 3 ]; then
        USERNAME="$3"
    fi

    if [ $# -ge 4 ]; then
        VERSION="$4"
    fi

    if [ $# -ge 5 ]; then
        TAG="$5"
    fi

    if [[ $DEST != "local" && $DEST != "devtool" && $DEST != "idctool" ]]; then
        echo "illegal DEST argument: $DEST"
        Usage
        exit 1
    fi
else
    Usage
    exit 1
fi

# set common variables
DEPLOY_NAME=${DEPLOY_ENV}_portal
LOCAL_PATH="${ROOT_DIR}/.tmp/${DEPLOY_NAME}"
DEST_PATH="/data/user00/tornado/${DEPLOY_NAME}"
DEST_IP="127.0.0.1"

# generate portal
GenAll

if [[ "$VERSION" == "" ]]; then
    TGZ_NAME="${DEPLOY_NAME}.tgz"
else
    TGZ_NAME="${DEPLOY_NAME}_${VERSION}.tgz"
fi

# deploy portal
if [[ "$DEST" == "local" ]]; then
    # TarTgz
    mkdir -p ${DEST_PATH}
    rsync -avz ${LOCAL_PATH}/* ${DEST_PATH} --delete
    cd ${DEST_PATH} && ./startstop.sh restart singleprocess && cd -
    echo -e "----- Deploy Info -----
     DEPLOY_NAME: $DEPLOY_NAME
      LOCAL_PATH: $LOCAL_PATH
         DEST_IP: local
       DEST_PATH: ${DEST_PATH}"

elif [[ "$DEST" == "devtool" ]]; then
    PushRemote $LOCAL_PATH $DEST_IP $DEST_PATH
    echo -e "----- Deploy Info -----
     DEPLOY_NAME: $DEPLOY_NAME
      LOCAL_PATH: $LOCAL_PATH
         DEST_IP: $DEST_IP
       DEST_PATH: $DEST_PATH
             URL: http://xxx.com/${DEPLOY_ENV}/"

elif [[ "$DEST" == "idctool" ]]; then
    TarTgz
    echo -e "----- Deploy Info -----
     DEPLOY_NAME: $DEPLOY_NAME
      LOCAL_PATH: $LOCAL_PATH
         DEST_IP: 127.0.0.1
       DEST_PATH: /data/home/user00/tornado
             URL: http://xxx.com/${DEPLOY_ENV}/"
fi