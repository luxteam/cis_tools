# $1 - Remote host
# $2 - Remote path
# $3 - rsync parameters

ssh $1 "mkdir -p $2"

rsync -rvzcmW --stats $3 . $1:$2
