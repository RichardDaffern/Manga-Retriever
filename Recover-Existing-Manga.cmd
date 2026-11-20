@echo off
setlocal EnableExtensions
rem Download previously generated GitHub Actions manga artifacts to this computer.
rem Requires Python 3.12, installed Manga Retriever, and authenticated GitHub CLI.
rem This launcher NEVER uploads manga or writes to Hugging Face.

if "%~1"=="" (
    echo Usage: Recover-Existing-Manga.cmd "C:\Manga\Recovered" [all^|relife,love-so-life,last-game,maid-sama,onizuka-sawarida,kainushi-wa-akuma] [workers 1-3]
    exit /b 2
)
set "DEST=%~1"
set "TITLES=%~2"
set "WORKERS=%~3"
if "%TITLES%"=="" set "TITLES=all"
if "%WORKERS%"=="" set "WORKERS=3"

py -3.12 -m scripts.recover_existing_manga --output-root "%DEST%" --titles "%TITLES%" --workers "%WORKERS%"
exit /b %ERRORLEVEL%
