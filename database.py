import sqlite3
from config import DATABASE_PATH

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # Create tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP DEFAULT NULL,
            FOREIGN KEY (collection_id) REFERENCES collections (id)
        )
    ''')
    
    # 添加 url_history 表
    c.execute('''
        CREATE TABLE IF NOT EXISTS url_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id TEXT,  -- 预留用户ID字段,支持多用户
            UNIQUE(url, user_id)
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
    """Get all bookmarks ordered by sort_order"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT b.id, b.url, b.title, b.favicon_path, b.collection_id, c.name, b.sort_order
        FROM bookmarks b
        LEFT JOIN collections c ON b.collection_id = c.id
        ORDER BY b.collection_id, b.sort_order, b.id
    ''')
    bookmarks = c.fetchall()
    conn.close()
    return bookmarks

def update_bookmark(bookmark_id, url, title, collection_name):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # Get or create collection
    c.execute('INSERT OR IGNORE INTO collections (name) VALUES (?)', (collection_name,))
    c.execute('SELECT id FROM collections WHERE name = ?', (collection_name,))
    collection_id = c.fetchone()[0]
    
    # Update bookmark
    c.execute('''
        UPDATE bookmarks 
        SET url = ?, title = ?, collection_id = ?
        WHERE id = ?
    ''', (url, title, collection_id, bookmark_id))
    
    conn.commit()
    conn.close()

def delete_bookmark_by_id(bookmark_id):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    c.execute('DELETE FROM bookmarks WHERE id = ?', (bookmark_id,))
    
    conn.commit()
    conn.close()

def update_bookmark_order(bookmark_id, new_order):
    """Update bookmark sort order"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE bookmarks 
        SET sort_order = ?
        WHERE id = ?
    ''', (new_order, bookmark_id))
    conn.commit()
    conn.close() 

def get_changes_since(timestamp):
    """获取指定时间戳之后的所有变更"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    changes = {
        'collections': [],
        'bookmarks': [],
        'deleted_bookmarks': []
    }
    
    # 获取新增或更新的集合
    c.execute('''
        SELECT * FROM collections 
        WHERE updated_at > ?
    ''', (timestamp,))
    changes['collections'] = c.fetchall()
    
    # 获取新增或更新的书签
    c.execute('''
        SELECT * FROM bookmarks 
        WHERE updated_at > ? AND deleted_at IS NULL
    ''', (timestamp,))
    changes['bookmarks'] = c.fetchall()
    
    # 获取删除的书签
    c.execute('''
        SELECT * FROM bookmarks 
        WHERE deleted_at > ?
    ''', (timestamp,))
    changes['deleted_bookmarks'] = c.fetchall()
    
    conn.close()
    return changes 

def save_url_history(url, user_id=None):
    """保存URL访问历史"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT OR REPLACE INTO url_history (url, user_id, visited_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (url, user_id))
        conn.commit()
    except Exception as e:
        print(f"Error saving URL history: {e}")
    finally:
        conn.close()

def get_url_history(user_id=None, limit=100):
    """获取URL访问历史"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    try:
        if user_id:
            c.execute('''
                SELECT url FROM url_history 
                WHERE user_id = ? 
                ORDER BY visited_at DESC 
                LIMIT ?
            ''', (user_id, limit))
        else:
            c.execute('''
                SELECT url FROM url_history 
                ORDER BY visited_at DESC 
                LIMIT ?
            ''', (limit,))
            
        urls = [row[0] for row in c.fetchall()]
        return urls
    finally:
        conn.close() 