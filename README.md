# Bookmark Manager

A simple, clean, and efficient bookmark manager built with Flask. It allows you to organize your bookmarks into collections and provides an intuitive drag-and-drop interface.

## Features

- 📚 Organize bookmarks into collections
- 🎯 Drag and drop bookmarks between collections
- 🔍 Auto-fetch website titles and favicons
- 🖼️ Custom favicon upload support
- 💾 Remember last used collection
- 🎨 Clean and responsive UI
- 🌐 Support for international characters and encodings

## Installation

1. Clone the repository:

```
bash
git clone https://github.com/yourusername/bookmark-manager.git
cd bookmark-manager
```


2. Create a virtual environment and activate it:
```
bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```


3. Install dependencies:
```
bash
pip install -r requirements.txt
```


4. Initialize the database:
```
bash
python app.py
```

## Usage

1. Start the server:
```
bash
python app.py
```


2. Open your browser and navigate to `http://localhost:5000`

3. Add bookmarks:
   - Click the + button in the bottom right corner
   - Enter the URL (title will be fetched automatically)
   - Select or create a collection
   - Click "Add Bookmark"

4. Manage bookmarks:
   - Drag and drop bookmarks between collections
   - Right-click a bookmark for options:
     - Edit bookmark
     - Change favicon
     - Move to another collection
     - Delete bookmark
   - Right-click a collection header to delete the collection

## Dependencies

- Flask
- BeautifulSoup4
- Requests
- Chardet
- SQLite3

## Project Structure

```
bookmark-manager/
├── app.py              # Main application file
├── config.py           # Configuration settings
├── database.py         # Database operations
├── utils.py            # Utility functions
├── static/
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript files
│   ├── images/         # Default images
│   └── favicons/       # Stored favicons
├── templates/          # HTML templates
└── bookmarks.db        # SQLite database
```



## Configuration

Edit `config.py` to customize:
- Default collection name
- Maximum collections
- Maximum bookmarks per collection
- File upload settings
- Database path
- Other application settings

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge


## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Icons and favicons are fetched from respective websites
- Default favicon provided for sites without icons

