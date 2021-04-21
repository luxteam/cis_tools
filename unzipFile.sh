# $1 - Remote path
# $2 - Remote archive path
# $3 - Remote target path
# $4 - Remove archive

ssh $1 "7z x -aoa \"$2\" -o\"$3\""

if [ "$4" = "true" ]
then
    ssh $1 "rm \"$2\""
fi
