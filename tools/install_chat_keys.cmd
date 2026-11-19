@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_chat_keys.ps1" %1
pause
