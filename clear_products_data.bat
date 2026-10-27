@echo off
set MYSQL_EXE=mysql
if exist "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" set MYSQL_EXE=C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe
"%MYSQL_EXE%" -u root -proot hotel_bar_db -e "SET FOREIGN_KEY_CHECKS = 0; TRUNCATE TABLE open_table_items; TRUNCATE TABLE bill_items; TRUNCATE TABLE purchases; TRUNCATE TABLE bills; TRUNCATE TABLE products; TRUNCATE TABLE vendors; SET FOREIGN_KEY_CHECKS = 1; SELECT COUNT(*) AS products FROM products; SELECT COUNT(*) AS vendors FROM vendors; SELECT COUNT(*) AS bills FROM bills;"
pause
