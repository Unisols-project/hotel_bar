USE hotel_bar_db;

SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE open_table_items;
TRUNCATE TABLE bill_items;
TRUNCATE TABLE purchases;
TRUNCATE TABLE bills;
TRUNCATE TABLE products;
TRUNCATE TABLE vendors;

SET FOREIGN_KEY_CHECKS = 1;

SELECT COUNT(*) AS products FROM products;
SELECT COUNT(*) AS vendors FROM vendors;
SELECT COUNT(*) AS bills FROM bills;
