rem %1 - Remote host
rem %2 - Remote path

bash -c "rsync -rvzclm --stats %1:%2 ."
