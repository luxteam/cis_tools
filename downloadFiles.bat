set REMOTE_SOURCE=%1
set LOCAL_DIR=%2
set REMOTE_HOST=%3

bash -c "mkdir -p %LOCAL_DIR%"
bash -c "rsync -rvzc %REMOTE_HOST%:%REMOTE_SOURCE% %LOCAL_DIR%"
