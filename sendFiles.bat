set SOURCE=%1
set REMOTE_HOST=admin@172.30.23.112
set REMOTE_ROOT=/home/admin/Server/storage.rpr/www/html
set REMOTE_DIR=%2
set REMOTE_PATH=%REMOTE_ROOT%/%REMOTE_DIR%

bash.exe -c 'ssh %REMOTE_HOST% "mkdir -p %REMOTE_PATH%"'

rem c:\\JN\\bash.exe -c 'scp -r %SOURCE% %REMOTE_HOST%:%REMOTE_PATH%'

bash.exe -c 'rsync -rvzW %SOURCE% %REMOTE_HOST%:%REMOTE_PATH%'
