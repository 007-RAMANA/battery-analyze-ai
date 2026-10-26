
@echo off
title Battery Analyze AI - Public Access
cd /d C:\BatteryAI

echo Starting Battery Analyze AI...
start "Battery Analyze AI" cmd /k "cd /d C:\BatteryAI && python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501"

timeout /t 5 /nobreak >nul

echo Starting Cloudflare Tunnel...
start "Battery AI Public Link" cmd /k "cloudflared tunnel --url http://127.0.0.1:8501"

echo.
echo Both services have been started.
echo Keep both windows open while using the public link.
pause
