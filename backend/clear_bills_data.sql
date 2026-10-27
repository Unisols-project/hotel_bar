USE hotel_bar_db;

-- Clear bill item rows first because they reference bills through a foreign key.
DELETE FROM bill_items;
DELETE FROM bills;

-- Reset auto-increment values after rows are removed.
ALTER TABLE bill_items AUTO_INCREMENT = 1;
ALTER TABLE bills AUTO_INCREMENT = 1;

SELECT COUNT(*) AS bill_items FROM bill_items;
SELECT COUNT(*) AS bills FROM bills;
