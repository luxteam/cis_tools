rem %1 - Remote host
rem %2 - Remote path

bash -c "rsync -rzclw --info=stats2 %1:%2 ."
bash -c "ssh %1 'rm -rf %2'"
