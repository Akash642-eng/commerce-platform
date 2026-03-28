CREATE TABLE users (
    id UUID PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(150) UNIQUE,
    phone VARCHAR(20),
    password_hash TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE
);

CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    permission_name VARCHAR(100) UNIQUE
);

CREATE TABLE user_roles (
    user_id UUID REFERENCES users(id),
    role_id INT REFERENCES roles(id),
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    description TEXT,
    price DECIMAL(10,2),
    category_id INT REFERENCES categories(id),
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory (
    product_id INT PRIMARY KEY REFERENCES products(id),
    quantity INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE carts (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INT REFERENCES carts(id),
    product_id INT REFERENCES products(id),
    quantity INT
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    total_amount DECIMAL(10,2),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id),
    product_id INT REFERENCES products(id),
    quantity INT,
    price DECIMAL(10,2)
);

