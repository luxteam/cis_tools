rem %1 - Remote host
rem %2 - Remote path

bash -c "rsync -rzclm --stats %1:%2 ."
