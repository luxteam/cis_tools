# $1 - Source
# $2 - Remote path
# $3 - Remote host

ssh $3 "mkdir -p $2"

rsync -rvzcmW $1 $3:$2
