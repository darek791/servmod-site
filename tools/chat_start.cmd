@echo off
rem Starts the ServMod chat gateway and the Cloudflare tunnel (hidden-ish, minimized) and installs itself in the Windows Startup folder.
cd /d "%~dp0"
set "SU=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\servmod_chat_start.cmd"
> "%SU%" echo @echo off
>> "%SU%" echo call "%~dp0chat_start.cmd" run
if /i "%1"=="run" goto go
echo Autostart installed: %SU%
:go
rem the gateway: skip if something already answers on port 11500
curl -s http://127.0.0.1:11500/health >nul 2>&1 || start "ServMod chat gateway" /min python "%~dp0chat_gateway.py"
tasklist /fi "imagename eq cloudflared.exe" | find /i "cloudflared.exe" >nul || start "ServMod chat tunnel" /min cloudflared tunnel --config "%USERPROFILE%\.cloudflared\config-servmod-chat.yml" run servmod-chat
timeout /t 10 >nul
curl -s http://127.0.0.1:11500/health
echo.
curl -s https://llm.servmod.com/health
echo.
if /i not "%1"=="run" pause
