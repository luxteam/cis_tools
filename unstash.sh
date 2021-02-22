# $1 - Remote host
# $2 - Remote path

rsync -rzclm --stats $1:$2 .
ssh $1 "rm -rf $2"
