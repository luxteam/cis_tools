rem %1 - Remote host
rem %2 - Remote path
rem %3 - rsync parameters

bash -c "ssh %1 'mkdir -p %2'"

bash -c "rsync -rvzcmW --info=stats2 %3 . %1:%2"
