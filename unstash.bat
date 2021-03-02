rem %1 - Remote path
rem %2 - Remote host

bash -c "rsync -rvzclm %2:%1 ."
