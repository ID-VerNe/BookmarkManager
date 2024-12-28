import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
from config import *
import chardet

def get_webpage_info(url):
    """Get webpage title and favicon"""
    headers = {'User-Agent': USER_AGENT}
    
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        # 检测内容编码
        raw_content = response.content
        detected = chardet.detect(raw_content)
        encoding = detected['encoding'] if detected['confidence'] > 0.5 else 'utf-8'
        
        # 使用检测到的编码解码内容
        try:
            html_content = raw_content.decode(encoding)
        except (UnicodeDecodeError, TypeError):
            # 如果解码失败，尝试使用 utf-8
            html_content = raw_content.decode('utf-8', errors='ignore')
        
        # 使用 BeautifulSoup 解析页面
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 获取标题
        title_tag = soup.find('title')
        title = title_tag.string.strip() if title_tag else urlparse(url).netloc
        
        # 获取网站图标
        favicon_path = get_favicon(url, html_content)
        
        return {
            'title': title,
            'favicon_path': favicon_path
        }
    except Exception as e:
        print(f"Error fetching webpage info: {str(e)}")
        # 返回默认值
        return {
            'title': urlparse(url).netloc,
            'favicon_path': DEFAULT_FAVICON
        }

def get_favicon(url, html_content):
    """Get favicon from webpage"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        base_url = urlparse(url)
        
        # 查找网站图标链接
        favicon_link = None
        
        # 1. 先找 link 标签中的图标
        for link in soup.find_all('link'):
            rel = link.get('rel', [])
            if isinstance(rel, str):
                rel = [rel]
            if 'icon' in rel or 'shortcut icon' in rel:
                favicon_link = link.get('href')
                break
        
        # 2. 如果没找到，使用默认路径 /favicon.ico
        if not favicon_link:
            favicon_link = '/favicon.ico'
        
        # 处理相对路径
        if not favicon_link.startswith(('http://', 'https://')):
            if favicon_link.startswith('//'):
                favicon_link = f'https:{favicon_link}'
            elif favicon_link.startswith('/'):
                favicon_link = f'{base_url.scheme}://{base_url.netloc}{favicon_link}'
            else:
                favicon_link = f'{base_url.scheme}://{base_url.netloc}/{favicon_link}'
        
        # 下载图标
        favicon_response = requests.get(favicon_link, headers={'User-Agent': USER_AGENT}, timeout=REQUEST_TIMEOUT)
        favicon_response.raise_for_status()
        
        # 生成文件名
        favicon_filename = f"favicon_{hash(url)}.ico"
        favicon_path = os.path.join('static', 'favicons', favicon_filename)
        
        # 保存图标
        with open(favicon_path, 'wb') as f:
            f.write(favicon_response.content)
        
        return f'/{favicon_path}'
    except Exception as e:
        print(f"Error getting favicon: {str(e)}")
        return DEFAULT_FAVICON 