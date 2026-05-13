import sqlite3

DB_NAME = "warehouse.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Створення таблиці товарів
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            article_number TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')
    
    # Створення таблиці складів
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS warehouses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL
        )
    ''')

    # Створення таблиці транзакцій
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            warehouse_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)
        )
    ''')

    # Створення таблиці inventory
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            warehouse_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (warehouse_id) REFERENCES warehouses(id)
        )
    ''')
    
    conn.commit()
    conn.close()

class ProductManager:
    def create(self, name, article_number, price):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, article_number, price) VALUES (?, ?, ?)",
            (name, article_number, price)
        )
        conn.commit()
        product_id = cursor.lastrowid
        conn.close()
        return product_id

    def get_all(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, article_number, price FROM products")
        rows = cursor.fetchall()
        conn.close()
        
        products = []
        for row in rows:
            products.append({
                "id": row[0],
                "name": row[1],
                "article_number": row[2],
                "price": row[3]
            })
        return products

    def update(self, product_id, name, article_number, price):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE products SET name = ?, article_number = ?, price = ? WHERE id = ?",
            (name, article_number, price, product_id)
        )
        conn.commit()
        conn.close()

    def delete(self, product_id):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()


class WarehouseManager:
    def create_warehouse(self, name, address):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO warehouses (name, address) VALUES (?, ?)",
            (name, address)
        )
        conn.commit()
        warehouse_id = cursor.lastrowid
        conn.close()
        return warehouse_id

    def get_all(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, address FROM warehouses")
        rows = cursor.fetchall()
        conn.close()
        
        warehouses = []
        for row in rows:
            warehouses.append({
                "id": row[0],
                "name": row[1],
                "address": row[2]
            })
        return warehouses

    def update_warehouse(self, warehouse_id, name, address):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE warehouses SET name = ?, address = ? WHERE id = ?",
            (name, address, warehouse_id)
        )
        conn.commit()
        conn.close()

    def delete_warehouse(self, warehouse_id):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM warehouses WHERE id = ?", (warehouse_id,))
        conn.commit()
        conn.close()

class TransactionManager:
    def receive_product(self, product_id, warehouse_id, quantity):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO transactions (product_id, warehouse_id, type, quantity) VALUES (?, ?, ?, ?)",
            (product_id, warehouse_id, 'надходження', quantity)
        )
        
        cursor.execute("SELECT quantity FROM inventory WHERE product_id = ? AND warehouse_id = ?", (product_id, warehouse_id))
        row = cursor.fetchone()
        
        if row:
            new_quantity = row[0] + quantity
            cursor.execute("UPDATE inventory SET quantity = ? WHERE product_id = ? AND warehouse_id = ?", (new_quantity, product_id, warehouse_id))
        else:
            cursor.execute("INSERT INTO inventory (product_id, warehouse_id, quantity) VALUES (?, ?, ?)", (product_id, warehouse_id, quantity))
            
        conn.commit()
        conn.close()

    def sell_product(self, product_id, warehouse_id, quantity):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO transactions (product_id, warehouse_id, type, quantity) VALUES (?, ?, ?, ?)",
            (product_id, warehouse_id, 'розхід', quantity)
        )
        
        cursor.execute("SELECT quantity FROM inventory WHERE product_id = ? AND warehouse_id = ?", (product_id, warehouse_id))
        row = cursor.fetchone()
        
        if row:
            new_quantity = row[0] - quantity
            if new_quantity <= 0:
                cursor.execute("DELETE FROM inventory WHERE product_id = ? AND warehouse_id = ?", (product_id, warehouse_id))
            else:
                cursor.execute("UPDATE inventory SET quantity = ? WHERE product_id = ? AND warehouse_id = ?", (new_quantity, product_id, warehouse_id))
                
        conn.commit()
        conn.close()

    def move_product(self, product_id, from_warehouse_id, to_warehouse_id, quantity):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO transactions (product_id, warehouse_id, type, quantity) VALUES (?, ?, ?, ?)",
            (product_id, from_warehouse_id, 'переміщення_з', quantity)
        )
        cursor.execute(
            "INSERT INTO transactions (product_id, warehouse_id, type, quantity) VALUES (?, ?, ?, ?)",
            (product_id, to_warehouse_id, 'переміщення_в', quantity)
        )
        
        cursor.execute("SELECT quantity FROM inventory WHERE product_id = ? AND warehouse_id = ?", (product_id, from_warehouse_id))
        row_from = cursor.fetchone()
        
        if row_from:
            new_qty_from = row_from[0] - quantity
            if new_qty_from <= 0:
                cursor.execute("DELETE FROM inventory WHERE product_id = ? AND warehouse_id = ?", (product_id, from_warehouse_id))
            else:
                cursor.execute("UPDATE inventory SET quantity = ? WHERE product_id = ? AND warehouse_id = ?", (new_qty_from, product_id, from_warehouse_id))
                
        cursor.execute("SELECT quantity FROM inventory WHERE product_id = ? AND warehouse_id = ?", (product_id, to_warehouse_id))
        row_to = cursor.fetchone()
        
        if row_to:
            new_qty_to = row_to[0] + quantity
            cursor.execute("UPDATE inventory SET quantity = ? WHERE product_id = ? AND warehouse_id = ?", (new_qty_to, product_id, to_warehouse_id))
        else:
            cursor.execute("INSERT INTO inventory (product_id, warehouse_id, quantity) VALUES (?, ?, ?)", (product_id, to_warehouse_id, quantity))
            
        conn.commit()
        conn.close()


class InventoryManager:
    def get_all_balances(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Об'єднання таблиць inventory, products та warehouses
        query = '''
            SELECT w.name as warehouse_name, p.name as product_name, i.quantity
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            JOIN warehouses w ON i.warehouse_id = w.id
        '''
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        balances = []
        for row in rows:
            balances.append({
                "warehouse_name": row[0],
                "product_name": row[1],
                "quantity": row[2]
            })
        return balances
