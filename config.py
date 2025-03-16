# Database configuration
DATABASE_PATH = "bookmarks.db"

# Application configuration
SECRET_KEY = "2024年12月28日 16:01:44"

# Constants
DEFAULT_COLLECTION = "常用"
MAX_COLLECTIONS = 100
MAX_BOOKMARKS_PER_COLLECTION = 1000

# Error messages
ERROR_URL_REQUIRED = "URL is required"
ERROR_TITLE_REQUIRED = "Title is required"
ERROR_COLLECTION_LIMIT = f"Maximum {MAX_COLLECTIONS} collections allowed"
ERROR_BOOKMARK_LIMIT = f"Maximum {MAX_BOOKMARKS_PER_COLLECTION} bookmarks per collection allowed"

# Web scraping configuration
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
REQUEST_TIMEOUT = 30
DEFAULT_TITLE = "Untitled"
DEFAULT_FAVICON = "/static/images/VID_20241017_1238350-1-1.jpg"

# Context menu actions
CONTEXT_MENU_EDIT = "Edit"
CONTEXT_MENU_DELETE = "Delete"
CONTEXT_MENU_MOVE = "Move to" 

# File upload configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'ico'}
MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 限制上传大小为1MB 

# Local storage keys
STORAGE_LAST_COLLECTION = 'lastSelectedCollection' 