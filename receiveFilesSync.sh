REMOTE_ROOT=/home/admin/Server/storage.rpr/www/html

REMOTE_SOURCE=$1
LOCAL_DIR=$2
REMOTE_HOST=$3
REMOTE_PATH=${REMOTE_ROOT}/${REMOTE_SOURCE}

mkdir -p ${LOCAL_DIR}
rsync -rvzc --delete ${REMOTE_HOST}:${REMOTE_PATH} ${LOCAL_DIR}
