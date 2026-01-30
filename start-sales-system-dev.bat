@echo off
chcp 65001 >nul
title Sales Management System - Development Mode

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║   Sales Management System - Development Mode                 ║
echo ║   نظام إدارة المبيعات - وضع التطوير                          ║
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

echo Starting services in DEVELOPMENT mode...
echo جاري تشغيل الخدمات في وضع التطوير...
echo.
echo ⚡ Hot-reload enabled - Changes reflect instantly!
echo ⚡ إعادة التحميل التلقائي مفعّل - التغييرات تظهر فوراً!
echo.

:: Start docker compose in development mode
docker-compose up -d --build

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
echo ║              SUCCESS! / تم بنجاح!                            ║
echo ╠══════════════════════════════════════════════════════════════╣
echo ║                                                              ║
echo ║   Frontend (with hot-reload):                                ║
echo ║   http://localhost:5173                                      ║
echo ║                                                              ║
echo ║   Backend API:                                               ║
echo ║   http://localhost:8000                                      ║
echo ║                                                              ║
echo ║   Database Admin (PgAdmin):                                  ║
echo ║   http://localhost:5050                                      ║
echo ║   Email: admin@admin.com / Pass: admin123                    ║
echo ║                                                              ║
echo ╠══════════════════════════════════════════════════════════════╣
echo ║                                                              ║
echo ║   💡 Any changes you make to the code will                   ║
echo ║      automatically reflect in the browser!                   ║
echo ║   💡 أي تغييرات في الكود ستظهر تلقائياً!                    ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Wait a few seconds for services to fully start
timeout /t 5 /nobreak >nul

:: Open browser
start http://localhost:5173

echo.
echo To stop all services / لإيقاف جميع الخدمات:
echo docker-compose down
echo.
echo To view logs / لعرض السجلات:
echo docker-compose logs -f
echo.
echo Press any key to close this window...
echo اضغط أي مفتاح لإغلاق هذه النافذة...
pause >nul
