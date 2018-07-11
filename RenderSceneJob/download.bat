set REMOTE_SOURCE=%2
set NAME=%1

bash -c 'wget -O %NAME% %REMOTE_SOURCE%'
