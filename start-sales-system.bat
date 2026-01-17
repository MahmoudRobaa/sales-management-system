@echo off
chcp 65001 >nul
title Sales Management System - نظام إدارة المبيعات

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║      Sales Management System - نظام إدارة المبيعات          ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo [خطأ] Docker غير مشغل!
    echo.
    echo Please start Docker Desktop first.
    echo يرجى تشغيل Docker Desktop أولاً.
    echo.
    pause
    exit /b 1
)

echo [OK] Docker is running...
echo [✓] Docker يعمل...
echo.

:: Navigate to script directory
cd /d "%~dp0"

echo Starting services... / جاري تشغيل الخدمات...
echo This may take a few minutes on first run.
echo قد يستغرق هذا بضع دقائق في المرة الأولى.
echo.

:: Start docker compose
docker-compose -f docker-compose.prod.yml up -d --build

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start services!
    echo [خطأ] فشل في تشغيل الخدمات!
    echo.
    pause
    exit /b 1
)

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    SUCCESS! / تم بنجاح!                      ║
echo ╠══════════════════════════════════════════════════════════════╣
echo ║                                                              ║
echo ║   Open in browser / افتح في المتصفح:                        ║
echo ║                                                              ║
echo ║          http://localhost:8888                               ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Wait a few seconds for services to fully start
timeout /t 5 /nobreak >nul

:: Open browser
start http://localhost:8888

echo Press any key to close this window...
echo اضغط أي مفتاح لإغلاق هذه النافذة...
pause >nul
