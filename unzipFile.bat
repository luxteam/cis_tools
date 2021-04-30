rem %1 - Remote host
rem %2 - Remote archive path
rem %3 - Remote target path
rem %4 - Remove archive

bash -c "ssh %1 '7z x -aoa %~2 -o%~3'"

if "%4" == "true" (bash -c "ssh %1 'rm %~2'")
