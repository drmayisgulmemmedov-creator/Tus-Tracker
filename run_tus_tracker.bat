@echo off
chcp 65001 >nul
title TUS Tekrar ve Test Izleyicisi
cd /d "%~dp0"

echo ==============================================================
echo   TUS Tekrar ve Test Izleyicisi ise salinir...
echo ==============================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python server.py
    goto :end
)

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py server.py
    goto :end
)

if exist "%LocalAppData%\Programs\Python\Python312\python.exe" (
    "%LocalAppData%\Programs\Python\Python312\python.exe" server.py
    goto :end
)

echo.
echo [XETA] Python tapilmadi.
echo Zehmet olmasa Python-un yuklendiyini yoxlayin.
echo Birbasa index.html faylini brauzerde acmaqla da proqramdan istifade ede bilersiniz.
echo.
pause

:end
