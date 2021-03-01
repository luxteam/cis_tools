# $1 - Remote path
# $2 - Remote host

rsync -rvzclm $2:$1 .
