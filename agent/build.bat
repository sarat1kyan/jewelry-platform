@echo off
cd /d %~dp0
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller

rem Clean previous build
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q SLSAgent.spec 2>nul

rem Build: include the whole sls_agent package
python -m PyInstaller ^
  --noconsole ^
  --onefile ^
  --name SLSAgent ^
  --collect-submodules sls_agent ^
  sls_agent\agent.py

echo.
echo Build complete: dist\SLSAgent.exe
