set SOURCE=%1
set REMOTE_PATH=%2
set REMOTE_HOST=%3
set CUSTOM_KEYS=%~4

bash.exe -c "ssh %REMOTE_HOST% 'mkdir -p %REMOTE_PATH%'"

bash.exe -c "rsync -rvztW %CUSTOM_KEYS% %SOURCE% %REMOTE_HOST%:%REMOTE_PATH%"
