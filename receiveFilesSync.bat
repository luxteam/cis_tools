set REMOTE_ROOT=/home/admin/Server/storage.rpr/www/html

set REMOTE_SOURCE=%1
set LOCAL_DIR=%2
set REMOTE_HOST=%3
set REMOTE_PATH=%REMOTE_ROOT%/%REMOTE_SOURCE%

bash -c "mkdir -p %LOCAL_DIR%"
bash -c "rsync -rvzc --delete %REMOTE_HOST%:%REMOTE_PATH% %LOCAL_DIR%"
