set REMOTE_HOST=admin@172.30.23.112
set REMOTE_ROOT=/home/admin/Server/storage.rpr/www/html

set REMOTE_SOURCE=${options.PRJ_ROOT}/${options.PRJ_NAME}/CoreAssets/
set LOCAL_DIR=%1
set REMOTE_PATH=%REMOTE_ROOT%/%REMOTE_SOURCE%

bash -c 'rsync -rvzc --delete --include='*.json' --include='*/' --exclude='*' %REMOTE_HOST%:%REMOTE_PATH% %LOCAL_DIR%''
