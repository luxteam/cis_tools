set REMOTE_ROOT=/home/admin/Server/storage.rpr/www/html

set REMOTE_SOURCE=%1
set LOCAL_DIR=%2
set REMOTE_HOST=%3
set REMOTE_PATH=%REMOTE_ROOT%/%REMOTE_SOURCE%

bash -c "rsync -rvzc --delete --include='*.json' --include='*/' --exclude='*' %REMOTE_HOST%:%REMOTE_PATH% %LOCAL_DIR%"
