# PowerShell build script for Windows (PyInstaller)
# Usage: Run in repository root in a PowerShell prompt.
#   .\build_exe.ps1
# This script creates a virtual environment, installs requirements and pyinstaller,
# and builds a bundled folder using PyInstaller including `leaderboard.json`.

$ErrorActionPreference = 'Stop'

Write-Host "Creating/updating virtual environment..."
python -m venv .venv

Write-Host "Activating venv..."
# Activate the venv for the current script
. .\.venv\Scripts\Activate.ps1

Write-Host "Upgrading pip and installing requirements..."
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

Write-Host "Building with PyInstaller (onedir, includes leaderboard.json)..."
# --add-data on Windows uses this format: "src;dest"
pyinstaller --noconfirm --clean --onedir --add-data "leaderboard.json;." --name "AvoidTheBlock" main.py

Write-Host "Build finished. Output dir: dist\AvoidTheBlock"
Write-Host "If you want a single-file executable change --onedir to --onefile in this script (note: larger startup time)."

Write-Host "Done. To run the built game, open: .\dist\AvoidTheBlock\AvoidTheBlock.exe"