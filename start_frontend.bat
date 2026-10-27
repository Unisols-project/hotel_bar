@echo off
cd /d "%~dp0frontend"
set PYTHON_EXE=python
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe
if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python310\python.exe
"%PYTHON_EXE%" serve.py
