set PATH=c:\python35\;c:\python35\scripts\;%PATH%

set REDIRECT_LINK=%~1
set OUTPUT_PATH=%~2
set FILE_NAME=%~3

python make_redirect_page.py --redirect_link "%REDIRECT_LINK%" --output_path "%OUTPUT_PATH%" --file_name "%FILE_NAME%"