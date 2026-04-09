$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
.\.venv\Scripts\python.exe .\scripts\build_db.py
Set-Location .\backend
..\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000