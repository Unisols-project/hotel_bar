@echo off
cd /d "%~dp0backend"
set MYSQL_EXE=mysql
if exist "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" set MYSQL_EXE=C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe
"%MYSQL_EXE%" -u root -proot < database.sql
