@echo off
setlocal EnableExtensions
rem NEW MANGA ONLY. No historical manga downloads or recovery.
rem The six supported series include Kimi no Iru Machi, Love Hina, Lovely Complex,
rem Mado kara Madoka-chan, Nisekoi and The Fairytale-like You Goes on the Assault.
rem Files are downloaded to your own private Windows output folder, NOT public Actions.

if "%~1"=="" (
    echo Usage: Download-New-Manga.cmd "C:\Manga\New" pilot
    echo        Download-New-Manga.cmd "C:\Manga\New" full
    echo.
    echo PILOT downloads Chapter 1 for six new titles so you can check English pages.
    echo FULL needs you to have already reviewed English pages and source export rights.
    exit /b 2
)
set "DEST=%~1"
set "MODE=%~2"
if "%MODE%"=="" set "MODE=pilot"
if /I not "%MODE%"=="pilot" if /I not "%MODE%"=="full" (
  echo ERROR: Mode must be pilot or full.
  exit /b 2
)
where py >nul 2>&1
if errorlevel 1 (
  echo ERROR: Install Python 3.12 first.
  exit /b 2
)
where manga-downloader >nul 2>&1
if errorlevel 1 (
  echo ERROR: Install Manga Downloader v25.3.0 and add it to PATH.
  echo https://github.com/elboletaire/manga-downloader/releases/tag/v25.3.0
  exit /b 2
)
if not exist "%DEST%" mkdir "%DEST%"
if errorlevel 1 (
  echo ERROR: Could not create destination.
  exit /b 2
)
if /I "%MODE%"=="full" (
  echo Full download means you have checked both the source's applicable terms
  echo and that chapter page text is English. Review your pilot output first.
  choice /C YN /M "Have you verified permission and the English chapter pages"
  if errorlevel 2 exit /b 2
  py -3.12 -m scripts.local_url_manga_bulk --mode full --slugs all --workers 2 --output-root "%DEST%" --acknowledge-local-rights --confirm-english-reviewed
) else (
  py -3.12 -m scripts.local_url_manga_bulk --mode pilot --slugs all --workers 2 --output-root "%DEST%" --acknowledge-local-rights
)
if errorlevel 1 (
  echo Some manga failed. Check "%DEST%\manga-bulk-status.json" and rerun to retry incomplete batches.
  exit /b 1
)
echo NEW manga downloads and image integrity checks finished.
echo Files: "%DEST%"
exit /b 0
