import sqlite3
from config import DATABASE_PATH

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # Create tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT NOT NULL,
            favicon_path TEXT,
            collection_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (collection_id) REFERENCES collections (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_bookmark(url, title, favicon_path, collection_name):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # Get or create collection
    c.execute('INSERT OR IGNORE INTO collections (name) VALUES (?)', (collection_name,))
    c.execute('SELECT id FROM collections WHERE name = ?', (collection_name,))
    collection_id = c.fetchone()[0]
    
    # Add bookmark
    c.execute('''
        INSERT INTO bookmarks (url, title, favicon_path, collection_id)
        VALUES (?, ?, ?, ?)
    ''', (url, title, favicon_path, collection_id))
    
    conn.commit()
    conn.close()

def get_collections():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM collections')
    collections = c.fetchall()
    conn.close()
    return collections

def get_bookmarks():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT 
            b.id,
            b.url,
            b.title,
            b.favicon_path,
            b.collection_id,
            c.name as collection_name,
            b.created_at
        FROM bookmarks b 
        JOIN collections c ON b.collection_id = c.id
        ORDER BY c.name, b.created_at DESC
    ''')
    bookmarks = c.fetchall()
    conn.close()
    return bookmarks 

def update_bookmark(bookmark_id, url, title, favicon_path, collection_name):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # Get or create collection
    c.execute('INSERT OR IGNORE INTO collections (name) VALUES (?)', (collection_name,))
    c.execute('SELECT id FROM collections WHERE name = ?', (collection_name,))
    collection_id = c.fetchone()[0]
    
    # Update bookmark
    c.execute('''
        UPDATE bookmarks 
        SET url = ?, title = ?, favicon_path = ?, collection_id = ?
        WHERE id = ?
    ''', (url, title, favicon_path, collection_id, bookmark_id))
    
    conn.commit()
    conn.close()

def delete_bookmark_by_id(bookmark_id):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    c.execute('DELETE FROM bookmarks WHERE id = ?', (bookmark_id,))
    
    conn.commit()
    conn.close() 