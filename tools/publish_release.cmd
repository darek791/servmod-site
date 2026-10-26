@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0publish_release.ps1"
pause
