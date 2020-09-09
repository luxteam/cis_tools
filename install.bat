setx -m CIS_TOOLS C:\JN\cis_tools

copy c:\Windows\System32\bash.exe c:\JN\

bash.exe -c "ssh-keygen -t rsa"
bash.exe -c "ssh-copy-id admin@172.30.23.112"


