@echo off
title Event Management System - DBMS Full-Stack Project
echo ========================================================
echo   EVENT MANAGEMENT SYSTEM - College DBMS Project
echo ========================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Virtual environment not found. Creating .venv...
    py -m venv .venv
    echo [INFO] Installing required dependencies...
    .\.venv\Scripts\pip install -r requirements.txt
)

echo [INFO] Starting Event Management System Server...
echo [INFO] Database configuration loaded from .env
echo.
echo Website will be available at: http://127.0.0.1:5000
echo.
start http://127.0.0.1:5000
.\.venv\Scripts\python run.py
pause
