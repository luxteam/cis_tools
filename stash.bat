rem %1 - Source
rem %2 - Remote path
rem %3 - Remote host

bash -c "ssh %3 'mkdir -p %2'"

bash -c "rsync -rvzcmW %1 %3:%2"
