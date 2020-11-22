set SOURCE=%1
set REMOTE_ROOT=/home/admin/Server/storage.rpr/www/html
set REMOTE_DIR=%2
set REMOTE_HOST=%3
set REMOTE_PATH=%REMOTE_ROOT%/%REMOTE_DIR%

bash.exe -c "ssh %REMOTE_HOST% 'mkdir -p %REMOTE_PATH%'"

bash.exe -c "rsync -rvzcW %SOURCE% %REMOTE_HOST%:%REMOTE_PATH%"
