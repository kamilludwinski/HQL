PRAGMA foreign_keys = ON;

CREATE TABLE customers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  phone TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE addresses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER NOT NULL,
  street TEXT NOT NULL,
  city TEXT NOT NULL,
  postcode TEXT NOT NULL,
  country TEXT NOT NULL,
  type TEXT CHECK(type IN ('billing','shipping')),
  FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  parent_id INTEGER,
  FOREIGN KEY (parent_id) REFERENCES categories(id)
);

CREATE TABLE products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  description TEXT,
  price REAL NOT NULL,
  category_id INTEGER,
  active INTEGER DEFAULT 1,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE inventory (
  product_id INTEGER PRIMARY KEY,
  quantity INTEGER NOT NULL DEFAULT 0,
  last_updated TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer_id INTEGER NOT NULL,
  status TEXT DEFAULT 'pending',
  total REAL DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE order_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL,
  price REAL NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(id),
  FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE payments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER NOT NULL,
  amount REAL NOT NULL,
  payment_method TEXT,
  status TEXT,
  paid_at TEXT,
  FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE shipments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER NOT NULL,
  address_id INTEGER NOT NULL,
  carrier TEXT,
  tracking_number TEXT,
  shipped_at TEXT,
  delivered_at TEXT,
  FOREIGN KEY (order_id) REFERENCES orders(id),
  FOREIGN KEY (address_id) REFERENCES addresses(id)
);

CREATE TABLE reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id INTEGER NOT NULL,
  customer_id INTEGER NOT NULL,
  rating INTEGER CHECK(rating BETWEEN 1 AND 5),
  comment TEXT,
  created_at TEXT DEFAULT (datetime('now')),
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
(1,34.49,'card','paid','2025-01-15');

INSERT INTO reviews (product_id, customer_id, rating, comment) VALUES
(1,1,5,'Great product'),
(2,2,4,'Very useful'),
(3,3,3,'Good but could improve');