@echo off
chcp 65001 >nul
cd /d "%~dp0"
py -3 collector.py --config config.json
if errorlevel 1 (
  echo.
  echo 收集失败，请查看上面的错误信息。
  pause
)
