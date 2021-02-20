# $1 - Remote host
# $2 - Remote path

rsync -rvzclm --stats $1:$2 .
ssh $1 "rm -rf $2"
