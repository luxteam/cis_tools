# $1 - Remote host
# $2 - Remote path

rsync -rzclw --info=stats2 $1:$2 .
ssh $1 "rm -rf $2"
