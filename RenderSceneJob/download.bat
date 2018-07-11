set REMOTE_SOURCE=%1
set NAME=%2

bash -c 'wget -O %NAME% %REMOTE_SOURCE%'
