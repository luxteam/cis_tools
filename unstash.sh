# $1 - Remote host
# $2 - Remote path

rsync -rzclm --stats $1:$2 .
