@echo off
setlocal
where gh >nul 2>&1
if errorlevel 1 (
  echo GitHub CLI is required. Install from https://cli.github.com/ and run gh auth login.
  exit /b 1
)
py -3.12 -m manga_retriever.retrieve download --directory "%~dp0downloads" %*
exit /b %errorlevel%
