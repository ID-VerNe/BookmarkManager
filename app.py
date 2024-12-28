from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import init_db, add_bookmark, get_collections, get_bookmarks, update_bookmark, delete_bookmark_by_id
import sqlite3
from config import *
from utils import get_webpage_info
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = SECRET_KEY

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'ico'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_app():
    """Initialize application directories and database"""
    # Create required directories
    directories = [
        os.path.join('static', 'images'),
        os.path.join('static', 'favicons'),
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # Create default favicon if it doesn't exist
    default_favicon_path = DEFAULT_FAVICON.lstrip('/')
    if not os.path.exists(default_favicon_path):
        # Create a simple default favicon (1x1 transparent pixel)
        with open(default_favicon_path, 'wb') as f:
            f.write(bytes.fromhex('00000100010000000000000000000000'))
    
    # Initialize database
    init_db()

@app.route('/')
def index():
    collections = get_collections()
    bookmarks = get_bookmarks()
    return render_template('index.html', 
                         collections=collections, 
                         bookmarks=bookmarks,
                         DEFAULT_COLLECTION=DEFAULT_COLLECTION)

@app.route('/add_bookmark', methods=['POST'])
def add_new_bookmark():
    url = request.form.get('url')
    title = request.form.get('title')
    create_new = request.form.get('new_collection')
    
    if not url:
        flash(ERROR_URL_REQUIRED, 'error')
        return redirect(url_for('index'))
    
    try:
        # Get webpage info
        webpage_info = get_webpage_info(url)
        
        # 使用用户输入的标题或自动获取的标题
        final_title = title if title else webpage_info['title']
        
        # 处理集合
        if create_new:
            collection_name = create_new.strip()
            if not collection_name:
                flash('集合名称不能为空', 'error')
                return redirect(url_for('index'))
                
            # 检查集合是否已存在
            conn = sqlite3.connect(DATABASE_PATH)
            c = conn.cursor()
            c.execute('SELECT id FROM collections WHERE name = ?', (collection_name,))
            if c.fetchone():
                conn.close()
                flash('集合已存在', 'error')
                return redirect(url_for('index'))
                
            # 创建新集合
            c.execute('INSERT INTO collections (name) VALUES (?)', (collection_name,))
            conn.commit()
            conn.close()
        else:
            collection_name = request.form.get('collection', DEFAULT_COLLECTION)
        
        # Add bookmark with fetched info
        add_bookmark(
            url=url,
            title=final_title,
            favicon_path=webpage_info['favicon_path'],
            collection_name=collection_name
        )
        
        flash('Bookmark added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding bookmark: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/edit_bookmark', methods=['POST'])
def edit_bookmark():
    try:
        bookmark_id = request.form.get('id')
        url = request.form.get('url')
        title = request.form.get('title')
        collection = request.form.get('collection')
        
        # 获取新的网页信息（如果URL改变）
        webpage_info = get_webpage_info(url)
        
        # 更新数据库
        update_bookmark(
            bookmark_id=bookmark_id,
            url=url,
            title=title,
            favicon_path=webpage_info['favicon_path'],
            collection_name=collection
        )
        
        flash('Bookmark updated successfully!', 'success')
        return '', 204
    except Exception as e:
        flash(f'Error updating bookmark: {str(e)}', 'error')
        return str(e), 400

@app.route('/delete_bookmark/<int:bookmark_id>', methods=['DELETE'])
def delete_bookmark(bookmark_id):
    try:
        delete_bookmark_by_id(bookmark_id)
        return '', 204
    except Exception as e:
        return str(e), 400

@app.route('/add_collection', methods=['POST'])
def add_collection():
    try:
        data = request.get_json()
        collection_name = data.get('name', '').strip()
        
        if not collection_name:
            return '集合名称不能为空', 400
            
        # 检查集合是否已存在
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('SELECT id FROM collections WHERE name = ?', (collection_name,))
        if c.fetchone():
            conn.close()
            return 'Collection already exists', 400
            
        # 创建新集合
        c.execute('INSERT INTO collections (name) VALUES (?)', (collection_name,))
        conn.commit()
        conn.close()
        
        return '', 204
    except Exception as e:
        return f'创建集合失败: {str(e)}', 400

@app.route('/move_bookmark', methods=['POST'])
def move_bookmark():
    try:
        data = request.get_json()
        bookmark_id = data.get('bookmark_id')
        collection_name = data.get('collection_name')
        
        print(f"Moving bookmark {bookmark_id} to collection {collection_name}")
        
        if not bookmark_id or not collection_name:
            print("Missing required fields")
            return 'Bookmark ID and collection name are required', 400
            
        # 获取书签当前信息
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        
        # 获取目标集合ID
        c.execute('SELECT id FROM collections WHERE name = ?', (collection_name,))
        collection_result = c.fetchone()
        if not collection_result:
            print(f"Collection {collection_name} not found")
            conn.close()
            return 'Collection not found', 404
        
        collection_id = collection_result[0]
        
        # 更新书签的集合ID
        c.execute('''
            UPDATE bookmarks 
            SET collection_id = ?
            WHERE id = ?
        ''', (collection_id, bookmark_id))
        
        if c.rowcount == 0:
            print(f"No bookmark updated for id {bookmark_id}")
        else:
            print(f"Successfully updated bookmark {bookmark_id}")
        
        conn.commit()
        conn.close()
        
        return '', 204
    except Exception as e:
        print(f"Error moving bookmark: {str(e)}")
        return str(e), 400

@app.route('/get_collections_html')
def get_collections_html():
    collections = get_collections()
    bookmarks = get_bookmarks()
    return render_template('collections_partial.html', 
                         collections=collections, 
                         bookmarks=bookmarks)

@app.route('/upload_icon', methods=['POST'])
def upload_icon():
    try:
        bookmark_id = request.form.get('bookmark_id')
        if 'icon' not in request.files:
            return 'No file uploaded', 400
            
        file = request.files['icon']
        if file.filename == '':
            return 'No file selected', 400
            
        if file and allowed_file(file.filename):
            # 生成安全的文件名
            filename = secure_filename(f"custom_icon_{bookmark_id}_{file.filename}")
            filepath = os.path.join('static', 'favicons', filename)
            
            # 保存文件
            file.save(filepath)
            
            # 更新数据库中的图标路径
            conn = sqlite3.connect(DATABASE_PATH)
            c = conn.cursor()
            c.execute('''
                UPDATE bookmarks 
                SET favicon_path = ?
                WHERE id = ?
            ''', (os.path.join('/', filepath), bookmark_id))
            conn.commit()
            conn.close()
            
            return '', 204
        else:
            return 'Invalid file type', 400
            
    except Exception as e:
        print(f"Error uploading icon: {str(e)}")
        return str(e), 400

@app.route('/preview_title', methods=['POST'])
def preview_title():
    try:
        data = request.get_json()
        url = data.get('url')
        if not url:
            return jsonify({'error': 'URL is required'}), 400
            
        # 获取网页信息
        webpage_info = get_webpage_info(url)
        return jsonify({'title': webpage_info['title']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_collection', methods=['POST'])
def delete_collection():
    try:
        data = request.get_json()
        collection_name = data.get('name', '').strip()
        
        if not collection_name:
            return '集合名称不能为空', 400
            
        if collection_name == DEFAULT_COLLECTION:
            return '默认集合不能删除', 400
            
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        
        # 获取集合ID
        c.execute('SELECT id FROM collections WHERE name = ?', (collection_name,))
        collection_result = c.fetchone()
        if not collection_result:
            conn.close()
            return '集合不存在', 404
            
        collection_id = collection_result[0]
        
        # 删除该集合下的所有书签
        c.execute('DELETE FROM bookmarks WHERE collection_id = ?', (collection_id,))
        
        # 删除集合
        c.execute('DELETE FROM collections WHERE id = ?', (collection_id,))
        
        conn.commit()
        conn.close()
        
        return '', 204
    except Exception as e:
        return f'删除集合失败: {str(e)}', 400

if __name__ == '__main__':
    init_app()
    app.run(debug=True) 