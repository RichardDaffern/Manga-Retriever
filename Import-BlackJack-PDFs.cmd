@echo off
setlocal
if "%~1"=="" (
  echo Usage: Import-BlackJack-PDFs.cmd --source "C:\Manga\Official-PDFs" --output "C:\MangaExport\BlackJack" --registry "C:\MangaExport\ids.json" --official-source
  echo The --official-source flag declares that these are official Sato Manga Works PDF files.
  exit /b 2
)
py -3.12 -m manga_retriever.blackjack_pdf %*
exit /b %errorlevel%
