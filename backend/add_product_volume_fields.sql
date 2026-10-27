-- Run this once if your existing database already has the `products` table.
USE hotel_bar_db;

ALTER TABLE products
  ADD COLUMN volume_value DECIMAL(10,2) NULL AFTER category,
  ADD COLUMN volume_unit ENUM('ML','L') NULL AFTER volume_value;
