import sqlite3
from datetime import datetime
from config import DATABASE_PATH

def update_database():
    """更新数据库结构"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    try:
        # 检查 url_history 表是否存在
        c.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='url_history'
        ''')
        if not c.fetchone():
            print("Creating url_history table...")
            c.execute('''
                CREATE TABLE url_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT,
                    UNIQUE(url, user_id)
                )
            ''')
            # 创建索引提高查询性能
            c.execute('''
                CREATE INDEX idx_url_history_visited 
                ON url_history (visited_at DESC)
            ''')
        
        # 检查 collections 表的列
        c.execute("PRAGMA table_info(collections)")
        columns = [column[1] for column in c.fetchall()]
        
        # 添加 updated_at 列到 collections 表
        if 'updated_at' not in columns:
            print("Adding updated_at column to collections table...")
            # 先添加列，不设置默认值
            c.execute('''
                ALTER TABLE collections 
                ADD COLUMN updated_at TIMESTAMP
            ''')
            
            # 然后更新现有记录
            current_time = datetime.now().isoformat()
            c.execute(f'''
                UPDATE collections 
                SET updated_at = '{current_time}'
                WHERE updated_at IS NULL
            ''')
        
        # 检查 bookmarks 表的列
        c.execute("PRAGMA table_info(bookmarks)")
        columns = [column[1] for column in c.fetchall()]
        
        # 添加新列到 bookmarks 表
        new_columns = {
            'updated_at': 'TIMESTAMP',
            'deleted_at': 'TIMESTAMP',
            'sort_order': 'INTEGER DEFAULT 0',
            'synced': 'INTEGER DEFAULT 0'  # SQLite 中用 INTEGER 存储布尔值
        }
        
        for column_name, column_type in new_columns.items():
            if column_name not in columns:
                print(f"Adding {column_name} column to bookmarks table...")
                c.execute(f'''
                    ALTER TABLE bookmarks 
                    ADD COLUMN {column_name} {column_type}
                ''')
        
        # 初始化现有记录的值
        if 'updated_at' in new_columns:
            c.execute(f'''
                UPDATE bookmarks 
                SET updated_at = created_at
                WHERE updated_at IS NULL
            ''')
        
        if 'sort_order' in new_columns:
            c.execute('''
                WITH OrderedBookmarks AS (
                    SELECT id,
                           ROW_NUMBER() OVER (PARTITION BY collection_id ORDER BY created_at) - 1 as new_order
                    FROM bookmarks
                )
                UPDATE bookmarks
                SET sort_order = (
                    SELECT new_order 
                    FROM OrderedBookmarks 
                    WHERE OrderedBookmarks.id = bookmarks.id
                )
                WHERE sort_order IS NULL
            ''')
        
        # 添加索引以提高性能
        print("Creating indexes...")
        indexes = [
            ('idx_bookmarks_collection', 'bookmarks', 'collection_id'),
            ('idx_bookmarks_updated_at', 'bookmarks', 'updated_at'),
            ('idx_bookmarks_deleted_at', 'bookmarks', 'deleted_at'),
            ('idx_bookmarks_sort_order', 'bookmarks', 'sort_order'),
            ('idx_collections_updated_at', 'collections', 'updated_at'),
            ('idx_url_history_user', 'url_history', 'user_id')
        ]
        
        for index_name, table, column in indexes:
            try:
                c.execute(f'''
                    CREATE INDEX IF NOT EXISTS {index_name}
                    ON {table} ({column})
                ''')
            except sqlite3.OperationalError as e:
                print(f"Warning: Could not create index {index_name}: {e}")
        
        # 更新数据库结构，确保新记录会自动设置时间戳
        c.execute('''
            CREATE TRIGGER IF NOT EXISTS update_collections_timestamp
            AFTER UPDATE ON collections
            BEGIN
                UPDATE collections 
                SET updated_at = DATETIME('now')
                WHERE id = NEW.id;
            END;
        ''')
        
        c.execute('''
            CREATE TRIGGER IF NOT EXISTS update_bookmarks_timestamp
            AFTER UPDATE ON bookmarks
            BEGIN
                UPDATE bookmarks 
                SET updated_at = DATETIME('now')
                WHERE id = NEW.id;
            END;
        ''')
        
        conn.commit()
        print("Database update completed successfully!")
        
    except Exception as e:
        print(f"Error updating database: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_database() 