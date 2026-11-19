@echo off
setlocal
where py >nul 2>nul
if errorlevel 1 (echo Please install Python 3.12 and ensure py launcher is available.& exit /b 1)
py -3.12 -m manga_retriever import %*
endlocal
