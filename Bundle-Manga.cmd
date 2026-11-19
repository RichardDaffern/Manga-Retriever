@echo off
setlocal
py -3.12 -m manga_retriever.retrieve bundle --exports "%~dp0downloads" --output "%~dp0manga-exports.zip" %*
exit /b %errorlevel%
