@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
  echo Usage: Download-ReLIFE.cmd pilot^|full "C:\Manga\ReLIFE"
  echo The pilot retrieves chapters 1-2. Full selects numbered chapters 1-222.
  echo Check the MangaDex and scanlation-group rules before continuing.
  exit /b 2
)
if "%~2"=="" (
  echo Missing destination directory.
  exit /b 2
)
echo Source permissions remain your responsibility. Do not redistribute any downloads.
set /p CONSENT=Have you checked MangaDex and scanlation group rules for personal downloading? [Y/N] 
if /I not "%CONSENT%"=="Y" exit /b 2
py -3.12 -m manga_retriever.relife --mode "%~1" --output "%~2" --acknowledge-rights
if errorlevel 1 (
  echo Download or verification incomplete. See above; no public files were uploaded.
  exit /b 1
)
echo Private ReLIFE CBZ audit complete. See relife_quality_audit.json next to the download folder.
