SOURCE=$1
REMOTE_HOST=admin@172.30.23.112
REMOTE_ROOT=/home/admin/Server/storage.rpr/www/html
REMOTE_DIR=$2
REMOTE_PATH=${REMOTE_ROOT}/${REMOTE_DIR}

ssh ${REMOTE_HOST} "mkdir -p ${REMOTE_PATH}"

# scp -r ${SOURCE} ${REMOTE_HOST}:${REMOTE_PATH}
rsync -rvzcl ${SOURCE} ${REMOTE_HOST}:${REMOTE_PATH}
