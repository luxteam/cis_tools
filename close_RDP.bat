set MY_SESSION_ID=unknown
for /f "tokens=3-4" %%a in ('query session %username%') do @if "%%b"=="Active" set MY_SESSION_ID=%%a
tscon %MY_SESSION_ID% /dest:console