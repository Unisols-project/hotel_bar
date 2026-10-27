-

CREATE DATABASE IF NOT EXISTS hotel_bar_db;
USE hotel_bar_db;

CREATE TABLE IF NOT EXISTS vendors (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  phone VARCHAR(20),
  address VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL UNIQUE,
  category ENUM('Food','Liquor','Other') NOT NULL,
  volume_value DECIMAL(10,2),
  volume_unit ENUM('ML','L'),
  rate DECIMAL(10,2) NOT NULL DEFAULT 0,
  stock INT NOT NULL DEFAULT 0,
  min_stock INT NOT NULL DEFAULT 5
);

CREATE TABLE IF NOT EXISTS purchases (
  id INT AUTO_INCREMENT PRIMARY KEY,
  vendor_id INT NOT NULL,
  product_id INT NOT NULL,
  qty INT NOT NULL,
  rate DECIMAL(10,2) NOT NULL,
  total DECIMAL(10,2) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (vendor_id) REFERENCES vendors(id),
  FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS bills (
  id INT AUTO_INCREMENT PRIMARY KEY,
  bill_no VARCHAR(40) NOT NULL,
  hotel_name VARCHAR(120) NOT NULL,
  hotel_phone VARCHAR(20),
  hotel_address VARCHAR(255),
  hotel_gstin VARCHAR(30),
  hotel_fssai VARCHAR(30),
  table_no VARCHAR(30),
  customer_name VARCHAR(100),
  phone VARCHAR(20),
  food_total DECIMAL(10,2) DEFAULT 0,
  sgst DECIMAL(10,2) DEFAULT 0,
  cgst DECIMAL(10,2) DEFAULT 0,
  liquor_subtotal DECIMAL(10,2) DEFAULT 0,
  vat DECIMAL(10,2) DEFAULT 0,
  liquor_total DECIMAL(10,2) DEFAULT 0,
  other_total DECIMAL(10,2) DEFAULT 0,
  grand_total DECIMAL(10,2) DEFAULT 0,
  payment VARCHAR(30),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bill_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  bill_id INT NOT NULL,
  product_id INT NOT NULL,
  item_name VARCHAR(120) NOT NULL,
  category ENUM('Food','Liquor','Other') NOT NULL,
  qty INT NOT NULL,
  rate DECIMAL(10,2) NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (bill_id) REFERENCES bills(id),
  FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS open_tables (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(60) NOT NULL UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS open_table_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  table_id INT NOT NULL,
  product_id INT NOT NULL,
  qty INT NOT NULL DEFAULT 0,
  FOREIGN KEY (table_id) REFERENCES open_tables(id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id)
);

INSERT IGNORE INTO open_tables(name) VALUES
('Table 1'),('Table 2'),('Table 3'),('Table 4'),('Table 5'),('Table 6');
