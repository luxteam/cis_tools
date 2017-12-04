set REMOTE_HOST=admin@172.30.23.112
set REMOTE_ROOT=/var/data/storage.rpr/www/html

set REMOTE_SOURCE=%1
set LOCAL_DIR=%2
set REMOTE_PATH=%REMOTE_ROOT%/%REMOTE_SOURCE%

bash.exe -c 'mkdir -p %LOCAL_DIR%'

c:\\JN\\bash.exe -c 'scp -r %REMOTE_HOST%:%REMOTE_PATH% %LOCAL_DIR%'
