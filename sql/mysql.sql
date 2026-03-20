-- Same schema and data as sql/sqlite.sql, adapted for MySQL

SET FOREIGN_KEY_CHECKS = 0;

CREATE TABLE IF NOT EXISTS customers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(255) NOT NULL,
  last_name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  phone VARCHAR(50),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS addresses (
  id INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT NOT NULL,
  street VARCHAR(255) NOT NULL,
  city VARCHAR(255) NOT NULL,
  postcode VARCHAR(20) NOT NULL,
  country VARCHAR(255) NOT NULL,
  type VARCHAR(20) CHECK (type IN ('billing','shipping')),
  FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL UNIQUE,
  parent_id INT,
  FOREIGN KEY (parent_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  price DECIMAL(10,2) NOT NULL,
  category_id INT,
  active TINYINT DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS inventory (
  product_id INT PRIMARY KEY,
  quantity INT NOT NULL DEFAULT 0,
  last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT NOT NULL,
  status VARCHAR(50) DEFAULT 'pending',
  total DECIMAL(10,2) DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS order_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT NOT NULL,
  product_id INT NOT NULL,
  quantity INT NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(id),
  FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS payments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  payment_method VARCHAR(50),
  status VARCHAR(50),
  paid_at DATETIME,
  FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE IF NOT EXISTS shipments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT NOT NULL,
  address_id INT NOT NULL,
  carrier VARCHAR(100),
  tracking_number VARCHAR(255),
  shipped_at DATETIME,
  delivered_at DATETIME,
  FOREIGN KEY (order_id) REFERENCES orders(id),
  FOREIGN KEY (address_id) REFERENCES addresses(id)
);

CREATE TABLE IF NOT EXISTS reviews (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  customer_id INT NOT NULL,
  rating INT CHECK (rating BETWEEN 1 AND 5),
  comment TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (product_id) REFERENCES products(id),
  FOREIGN KEY (customer_id) REFERENCES customers(id)
);

INSERT INTO customers (first_name, last_name, email, phone) VALUES
('Alice','Smith','alice@example.com','555-1111'),
('Bob','Jones','bob@example.com','555-2222'),
('Carol','White','carol@example.com','555-3333');

INSERT INTO addresses (customer_id, street, city, postcode, country, type) VALUES
(1,'10 High Street','London','SW1A1AA','UK','shipping'),
(2,'22 Baker Street','London','NW16XE','UK','shipping'),
(3,'5 Market Road','Manchester','M12AB','UK','shipping');

INSERT INTO categories (name) VALUES
('Electronics'),
('Accessories'),
('Home');

INSERT INTO products (name, description, price, category_id) VALUES
('Widget','Basic widget',9.99,2),
('Gadget','Advanced gadget',24.50,1),
('Gizmo','Multi-purpose gizmo',14.00,1);

INSERT INTO inventory (product_id, quantity) VALUES
(1,100),
(2,50),
(3,75);

INSERT INTO orders (customer_id, status, total) VALUES
(1,'completed',34.49),
(2,'pending',24.50),
(3,'processing',14.00);

INSERT INTO order_items (order_id, product_id, quantity, price) VALUES
(1,1,1,9.99),
(1,2,1,24.50),
(2,2,1,24.50),
(3,3,1,14.00);

INSERT INTO payments (order_id, amount, payment_method, status, paid_at) VALUES
(1,34.49,'card','paid','2025-01-15 00:00:00');

INSERT INTO reviews (product_id, customer_id, rating, comment) VALUES
(1,1,5,'Great product'),
(2,2,4,'Very useful'),
(3,3,3,'Good but could improve');

SET FOREIGN_KEY_CHECKS = 1;
