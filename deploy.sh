#!/bin/bash

set -e

function Usage() {
    echo ""
    echo "Usage: $0 <ENV> [DEST] [USERNAME] [VERSION] [TAG]"

    echo ""
    echo ""
    echo "optional DEST local, remote"

    echo ""
    echo "optional USERNAM"

    echo ""
    echo "optional VERSION"
}

ROOT_DIR=$(git rev-parse --show-toplevel)

function GenProtobuf() {
    echo "generating protobuf"
    cd ${ROOT_DIR}
    ./scripts/genpb.sh
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
    sed -i "s#_VERSION_#${TAG}\ ${commit}#g" ${LOCAL_PATH}/templates/header.html
    sed -i "s#_DEPLOYER_#${deployer}#g" ${LOCAL_PATH}/templates/header.html
}

function GenAll() {
    cd $(dirname $0)
    GenProtobuf
    GenLocal $LOCAL_PATH
    GenVersionInfo
    sed -i "/VENV_NAME/s/dev/${DEPLOY_ENV}/g" ${LOCAL_PATH}/config.py
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

# default global conf
DEPLOY_ENV="dev"
DEST="local"
VERSION=""
TAG=""
USERNAME="${USER}"

dev_envs=("lab" "dev" "test")

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

    if [[ $DEST != "local" && $DEST != "remote" ]]; then
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

elif [[ "$DEST" == "remote" ]]; then
    TarTgz
    echo -e "----- Deploy Info -----
     DEPLOY_NAME: $DEPLOY_NAME
      LOCAL_PATH: $LOCAL_PATH
         DEST_IP: $DEST_IP
       DEST_PATH: $DEST_PATH
             URL: http://xxx.com/${DEPLOY_ENV}/"
fi