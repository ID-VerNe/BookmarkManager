const MAX_URL_HISTORY = 9999;  // 最多保存100条历史记录

// 初始化URL历史记录
function getUrlHistory() {
    return JSON.parse(localStorage.getItem('urlHistory') || '[]');
}

// 保存URL到历史记录
function saveToUrlHistory(url) {
    let history = getUrlHistory();
    // 如果已存在，先删除旧的
    history = history.filter(item => item !== url);
    // 添加到开头
    history.unshift(url);
    // 限制数量
    if (history.length > MAX_URL_HISTORY) {
        history = history.slice(0, MAX_URL_HISTORY);
    }
    localStorage.setItem('urlHistory', JSON.stringify(history));
}

// 处理导航
function handleNavigation(input, isSearch = false) {
    let url = input.trim();
    const searchPrefixes = {
        google: ['?gg ', '？gg '],
        baidu: ['?bd ', '？bd ', '?', '？'],
        bing: ['?bi ', '？bi '],
    };
    const searchUrls = {
        google: 'https://www.google.com/search?q=',
        baidu: 'https://www.baidu.com/s?wd=',
        bing: 'https://www.bing.com/search?q=', // 确保Bing的URL是正确的
    };
    let selectedSearchEngine = null;

    for (const engine in searchPrefixes) {
        for (const prefix of searchPrefixes[engine]) {
            if (url.startsWith(prefix)) {
                selectedSearchEngine = engine;
                url = url.replace(prefix, '');
                break;
            }
        }
        if (selectedSearchEngine) {
            break; // Exit outer loop once an engine is found
        }
    }

    if (selectedSearchEngine) {
        // Perform search with the selected engine
        const searchUrl = searchUrls[selectedSearchEngine];
        const a = document.createElement('a');
        a.href = `${searchUrl}${encodeURIComponent(url)}`;
        a.target = '_blank';
        a.rel = 'noopener';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    } else if (url) {
        if (!isSearch && isValidUrl(url)) {
            // Is a valid URL, open in new tab
            const fullUrl = url.startsWith('http') ? url : `https://${url}`;
            saveToUrlHistory(fullUrl);
            const a = document.createElement('a');
            a.href = fullUrl;
            a.target = '_blank';
            a.rel = 'noopener';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        } else {
            // Not a valid URL or isSearch, default to Baidu search
            const searchUrl = searchUrls.baidu;
            const a = document.createElement('a');
            a.href = `${searchUrl}${encodeURIComponent(url)}`;
            a.target = '_blank';
            a.rel = 'noopener';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }
    }
}

// 检查是否是有效的URL
function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        // 尝试添加https://再检查一次
        try {
            new URL(`https://${string}`);
            return true;
        } catch (_) {
            return false;
        }
    }
}

// 显示添加书签对话框
function showAddBookmarkDialog() {
    const dialog = document.getElementById('addBookmarkDialog');
    const urlInput = document.getElementById('bookmarkUrl');
    const collectionSelect = document.getElementById('collectionSelect');
    
    // 设置上次选择的集合
    const lastCollection = getLastCollection();
    const option = Array.from(collectionSelect.options)
        .find(opt => opt.value === lastCollection);
    
    if (option) {
        collectionSelect.value = lastCollection;
    }
    
    dialog.style.display = 'block';
    urlInput.focus();
}

// 关闭添加书签对话框
function closeAddBookmarkDialog() {
    const dialog = document.getElementById('addBookmarkDialog');
    const form = dialog.querySelector('form');
    const checkbox = document.getElementById('createNewCollection');
    
    dialog.style.display = 'none';
    form.reset();
    checkbox.checked = false;
    toggleNewCollectionInput();
}

// 获取最后选择的集合
function getLastCollection() {
    return localStorage.getItem('lastSelectedCollection') || document.querySelector('#collectionSelect option').value;
}

// 保存最后选择的集合
function saveLastCollection(collectionName) {
    localStorage.setItem('lastSelectedCollection', collectionName);
}

// 切换新建集合输入框的显示状态
function toggleNewCollectionInput() {
    const checkbox = document.getElementById('createNewCollection');
    const inputArea = document.getElementById('newCollectionInputArea');
    const select = document.getElementById('collectionSelect');
    
    inputArea.style.display = checkbox.checked ? 'block' : 'none';
    select.disabled = checkbox.checked;
    
    if (checkbox.checked) {
        document.getElementById('newCollectionName').focus();
    }
}

// Handle bookmark form submission
document.addEventListener('DOMContentLoaded', function() {
    // Auto-generate title from URL if title is empty
    const urlInput = document.querySelector('input[name="url"]');
    const titleInput = document.querySelector('input[name="title"]');

    urlInput.addEventListener('blur', function() {
        if (urlInput.value && !titleInput.value) {
            try {
                const url = new URL(urlInput.value);
                titleInput.value = url.hostname.replace('www.', '');
            } catch (e) {
                console.log('Invalid URL');
            }
        }
    });

    // Flash message handling
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 3000);
    });

    // Collection collapsing
    const collections = document.querySelectorAll('.collection h3');
    collections.forEach(header => {
        header.addEventListener('click', function() {
            const bookmarks = this.nextElementSibling;
            bookmarks.style.display = bookmarks.style.display === 'none' ? 'block' : 'none';
        });
    });

    // 添加书签表单提交事件监听
    const addBookmarkForm = document.querySelector('#addBookmarkDialog form');
    if (addBookmarkForm) {
        addBookmarkForm.addEventListener('submit', function() {
            const collectionSelect = document.getElementById('collectionSelect');
            const createNewCollection = document.getElementById('createNewCollection');
            
            // 只有在不是创建新集合时才保存选择
            if (!createNewCollection.checked) {
                saveLastCollection(collectionSelect.value);
            }
        });
    }

    // 搜索导航功能
    const searchNav = document.getElementById('searchNav');
    const suggestions = document.getElementById('urlSuggestions');
    let selectedIndex = -1;

    // 自动聚焦
    searchNav.focus();

    searchNav.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleNavigation(this.value, e.shiftKey);  // 添加 shift 键检测
        } else if (e.key === 'Tab') {
            e.preventDefault();
            if (suggestions.firstChild) {
                // 只获取 URL 文本内容
                const urlText = suggestions.firstChild.querySelector('.url-text');
                this.value = urlText.textContent;
                suggestions.innerHTML = '';
            }
        } else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
            e.preventDefault();
            const items = suggestions.children;
            if (items.length > 0) {
                if (e.key === 'ArrowDown') {
                    selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
                } else {
                    selectedIndex = Math.max(selectedIndex - 1, 0);
                }
                // 只获取 URL 文本内容
                const urlText = items[selectedIndex].querySelector('.url-text');
                this.value = urlText.textContent;
            }
        }
    });

    searchNav.addEventListener('input', function() {
        const input = this.value.trim().toLowerCase();
        if (input) {
            const history = getUrlHistory();
            const matches = history.filter(url => 
                url.toLowerCase().includes(input)
            ).slice(0, 5); // 最多显示5个建议

            suggestions.innerHTML = '';
            matches.forEach(url => {
                const div = document.createElement('div');
                div.className = 'url-suggestion-item';
                
                // 创建URL文本容器
                const urlText = document.createElement('span');
                urlText.textContent = url;
                urlText.className = 'url-text';
                urlText.onclick = () => {
                    searchNav.value = url;
                    suggestions.innerHTML = '';
                    handleNavigation(url, false);
                };
                
                // 创建删除按钮
                const deleteBtn = document.createElement('span');
                deleteBtn.textContent = '×';
                deleteBtn.className = 'delete-history';
                deleteBtn.onclick = (e) => {
                    e.stopPropagation(); // 阻止事件冒泡
                    removeFromHistory(url);
                    div.remove();
                };
                
                div.appendChild(urlText);
                div.appendChild(deleteBtn);
                suggestions.appendChild(div);
            });
        } else {
            suggestions.innerHTML = '';
        }
        selectedIndex = -1;
    });

    // 点击其他地方时隐藏建议
    document.addEventListener('click', function(e) {
        if (!searchNav.contains(e.target) && !suggestions.contains(e.target)) {
            suggestions.innerHTML = '';
        }
    });
});

// Add drag and drop functionality
let draggedItem = null;

// 初始化事件监听器函数
function initializeEventListeners() {
    document.querySelectorAll('.bookmark').forEach(bookmark => {
        bookmark.addEventListener('dragstart', function(e) {
            if (e.target.tagName.toLowerCase() === 'a') {
                e.preventDefault();
                return;
            }
            draggedItem = this;
            this.classList.add('dragging');
        });

        bookmark.addEventListener('dragend', function(e) {
            this.classList.remove('dragging');
            draggedItem = null;
        });
    });

    document.querySelectorAll('.bookmarks').forEach(bookmarksContainer => {
        bookmarksContainer.addEventListener('dragover', function(e) {
            e.preventDefault();
            const afterElement = getDragAfterElement(this, e.clientY);
            const draggable = document.querySelector('.dragging');
            if (afterElement == null) {
                this.appendChild(draggable);
            } else {
                this.insertBefore(draggable, afterElement);
            }
        });

        bookmarksContainer.addEventListener('drop', async function(e) {
            e.preventDefault();
            if (!draggedItem) return;

            const bookmarks = Array.from(this.querySelectorAll('.bookmark'));
            const orders = bookmarks.map((bookmark, index) => ({
                id: bookmark.dataset.id,
                order: index
            }));

            // 更新所有受影响的书签顺序
            for (const {id, order} of orders) {
                try {
                    await fetch('/update_bookmark_order', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            bookmark_id: id,
                            new_order: order
                        })
                    });
                } catch (error) {
                    console.error('Error updating bookmark order:', error);
                }
            }
        });
    });
}

// 添加辅助函数来确定拖拽位置
function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.bookmark:not(.dragging)')];

    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
});

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Alt + N to open new bookmark form
    if (e.altKey && e.key === 'n') {
        e.preventDefault();
        document.querySelector('input[name="url"]').focus();
    }
    
    // Alt + F to focus search
    if (e.altKey && e.key === 'f') {
        e.preventDefault();
        document.querySelector('.search-input').focus();
    }
});

let currentBookmark = null;

// 显示右键菜单
function showContextMenu(event, bookmarkElement) {
    event.preventDefault();
    // 保存当前书签元素
    currentBookmark = bookmarkElement;
    
    const contextMenu = document.getElementById('contextMenu');
    
    // First make the menu visible but hidden to calculate dimensions
    contextMenu.style.visibility = 'hidden';
    contextMenu.style.display = 'block';
    
    // Get viewport dimensions
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;
    
    // Get menu dimensions after making it visible
    const menuHeight = contextMenu.offsetHeight;
    const menuWidth = contextMenu.offsetWidth;
    
    // Calculate positions
    let posX = event.clientX;
    let posY = event.clientY;
    
    // Check if menu would go below viewport
    if (posY + menuHeight > viewportHeight) {
        posY = viewportHeight - menuHeight - 10; // 10px padding from bottom
    }
    
    // Check if menu would go beyond right edge
    if (posX + menuWidth > viewportWidth) {
        posX = viewportWidth - menuWidth - 10; // 10px padding from right
    }
    
    // Set the position
    contextMenu.style.left = `${posX}px`;
    contextMenu.style.top = `${posY}px`;
    
    // Finally make the menu visible
    contextMenu.style.visibility = 'visible';
}

// 编辑书签
function editBookmark() {
    const bookmarkId = currentBookmark.dataset.id;
    const url = currentBookmark.querySelector('a').href;
    const title = currentBookmark.querySelector('a').textContent;
    const collection = currentBookmark.closest('.collection').querySelector('h3').textContent;
    
    // 填充编辑表单
    document.getElementById('editBookmarkId').value = bookmarkId;
    document.getElementById('editUrl').value = url;
    document.getElementById('editTitle').value = title;
    document.getElementById('editCollection').value = collection;
    
    // 显示编辑对话框
    document.getElementById('editDialog').style.display = 'block';
    document.getElementById('contextMenu').style.display = 'none';
}

// 提交编辑
async function submitEdit(event) {
    event.preventDefault();
    
    const formData = new FormData(document.getElementById('editForm'));
    
    try {
        const response = await fetch('/edit_bookmark', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            // 更新成功才刷新页面
            window.location.reload();
        } else {
            // 更新失败只关闭对话框
            closeEditDialog();
        }
    } catch (error) {
        console.error('Error:', error);
        // 发生错误也只关闭对话框
        closeEditDialog();
    }
}

// 关闭编辑对话框
function closeEditDialog() {
    document.getElementById('editDialog').style.display = 'none';
}

// 删除书签
async function deleteBookmark() {
    if (confirm('确定要删除这个书签吗？')) {
        const bookmarkId = currentBookmark.dataset.id;
        
        try {
            const response = await fetch(`/delete_bookmark/${bookmarkId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                currentBookmark.remove();
            } else {
                alert('Failed to delete bookmark');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error deleting bookmark');
        }
    }
    document.getElementById('contextMenu').style.display = 'none';
}

// 点击其他地方关闭右键菜单
document.addEventListener('click', function(event) {
    const contextMenu = document.getElementById('contextMenu');
    if (!contextMenu.contains(event.target)) {
        contextMenu.style.display = 'none';
    }
});

// 阻止默认右键菜单
document.addEventListener('contextmenu', function(event) {
    if (!event.target.closest('.bookmark')) {
        return;
    }
    event.preventDefault();
});

// 处理集合选择
function handleCollectionSelect(selectElement) {
    const collectionInput = document.getElementById('collectionInput');
    
    if (selectElement.value === "") {
        // 选择了"新建集合"选项
        collectionInput.style.display = 'block';
        collectionInput.value = '';
        collectionInput.focus();
    } else {
        // 选择了现有集合
        collectionInput.style.display = 'none';
        collectionInput.value = selectElement.value;
    }
}

// 显示新建集合对话框
function showNewCollectionDialog() {
    document.getElementById('newCollectionDialog').style.display = 'block';
    document.getElementById('newCollectionName').focus();
}

// 关闭新建集合对话框
function closeNewCollectionDialog() {
    document.getElementById('newCollectionDialog').style.display = 'none';
    document.getElementById('newCollectionName').value = '';
}

// 提交新建集合
async function submitNewCollection(event) {
    event.preventDefault();
    const collectionName = document.getElementById('newCollectionName').value;
    
    try {
        const response = await fetch('/add_collection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: collectionName })
        });
        
        if (response.ok) {
            // 添加新选项到下拉列表
            const select = document.getElementById('collectionSelect');
            const option = new Option(collectionName, collectionName);
            select.add(option);
            select.value = collectionName;
            
            // 关闭对话框
            closeNewCollectionDialog();
        } else {
            const error = await response.text();
            alert(error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error creating collection');
    }
}

// 显示上传图标对话框
function uploadIcon() {
    const bookmarkId = currentBookmark.dataset.id;
    document.getElementById('iconBookmarkId').value = bookmarkId;
    document.getElementById('iconPreview').style.display = 'none';
    document.getElementById('uploadIconDialog').style.display = 'block';
    document.getElementById('contextMenu').style.display = 'none';
}

// 关闭上传对话框
function closeUploadDialog() {
    document.getElementById('uploadIconDialog').style.display = 'none';
    document.getElementById('iconFile').value = '';
}

// 预览选择的图标
document.getElementById('iconFile').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('iconPreview');
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
});

// 提交新图标
async function submitIcon(event) {
    event.preventDefault();
    
    const formData = new FormData(document.getElementById('uploadIconForm'));
    
    try {
        const response = await fetch('/upload_icon', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            // 获取更新后的集合内容
            const collectionsResponse = await fetch('/get_collections_html');
            if (collectionsResponse.ok) {
                const html = await collectionsResponse.text();
                document.querySelector('.collections').innerHTML = html;
                initializeEventListeners();
            }
            closeUploadDialog();
        } else {
            const error = await response.text();
            alert(error);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// 点击其他地方关闭对话框
document.addEventListener('click', function(event) {
    const dialog = document.getElementById('addBookmarkDialog');
    const button = document.querySelector('.add-bookmark-button');
    if (event.target === dialog) {
        closeAddBookmarkDialog();
    }
});

// 内联提交新集合
async function submitNewCollectionInline() {
    const collectionName = document.getElementById('newCollectionName').value.trim();
    
    if (!collectionName) {
        alert('请输入集合名称');
        return;
    }
    
    try {
        const response = await fetch('/add_collection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: collectionName })
        });
        
        if (response.ok) {
            // 获取更新后的集合内容
            const collectionsResponse = await fetch('/get_collections_html');
            if (collectionsResponse.ok) {
                const html = await collectionsResponse.text();
                document.querySelector('.collections').innerHTML = html;
                initializeEventListeners();
            }
            
            // 更新下拉列表
            const select = document.getElementById('collectionSelect');
            const option = new Option(collectionName, collectionName);
            select.add(option);
            select.value = collectionName;
            
            // 清空输入框并隐藏
            document.getElementById('newCollectionName').value = '';
            document.getElementById('newCollectionInputArea').style.display = 'none';
        } else {
            const error = await response.text();
            if (error.includes('already exists')) {
                alert('该集合名称已存在');
            } else {
                alert(error);
            }
        }
    } catch (error) {
        console.error('Error:', error);
        alert('创建集合失败，请重试');
    }
}

// 预览书签标题
async function previewBookmarkTitle(url) {
    if (!url) return;
    
    try {
        const response = await fetch('/preview_title', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });
        
        if (response.ok) {
            const data = await response.json();
            const titleInput = document.getElementById('bookmarkTitle');
            if (!titleInput.value) {  // 只有当用户没有输入标题时才自动填充
                titleInput.value = data.title;
                titleInput.placeholder = data.title;
            }
        }
    } catch (error) {
        console.error('Error fetching title:', error);
    }
}

let currentCollection = null;

// 显示集合右键菜单
function showCollectionMenu(event, collectionElement) {
    event.preventDefault();
    
    // 保存当前集合元素
    currentCollection = collectionElement;
    
    const contextMenu = document.getElementById('collectionMenu');
    contextMenu.style.display = 'block';
    contextMenu.style.left = event.pageX + 'px';
    contextMenu.style.top = event.pageY + 'px';
}

// 删除集合
async function deleteCollection() {
    const collectionName = currentCollection.textContent.trim();
    const isDefault = currentCollection.closest('.collection').dataset.isDefault === 'true';
    
    if (isDefault) {
        alert('默认集合不能删除');
        document.getElementById('collectionMenu').style.display = 'none';
        return;
    }
    
    if (confirm(`确定要删除集合"${collectionName}"及其所有书签吗？此操作不可恢复！`)) {
        try {
            const response = await fetch('/delete_collection', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: collectionName })
            });
            
            if (response.ok) {
                // 获取更新后的集合内容
                const collectionsResponse = await fetch('/get_collections_html');
                if (collectionsResponse.ok) {
                    const html = await collectionsResponse.text();
                    document.querySelector('.collections').innerHTML = html;
                    initializeEventListeners();
                }
            } else {
                const error = await response.text();
                alert(error);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('删除集合失败，请重试');
        }
    }
    document.getElementById('collectionMenu').style.display = 'none';
}

// 修改点击其他地方关闭右键菜单的处理
document.addEventListener('click', function(event) {
    const contextMenu = document.getElementById('contextMenu');
    const collectionMenu = document.getElementById('collectionMenu');
    
    if (!contextMenu.contains(event.target)) {
        contextMenu.style.display = 'none';
    }
    if (!collectionMenu.contains(event.target)) {
        collectionMenu.style.display = 'none';
    }
});

// 切换搜索框显示状态
function toggleSearch() {
    const searchContainer = document.getElementById('searchContainer');
    const searchInput = document.getElementById('searchInput');
    
    if (searchContainer.style.display === 'none' || !searchContainer.style.display) {
        searchContainer.style.display = 'block';
        searchInput.focus();
    } else {
        searchContainer.style.display = 'none';
        searchInput.value = '';
        // 清除搜索结果，显示所有书签
        document.querySelectorAll('.bookmark').forEach(bookmark => {
            bookmark.style.display = 'block';
        });
    }
}

// 初始化搜索功能
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    
    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const bookmarks = document.querySelectorAll('.bookmark');
        
        bookmarks.forEach(bookmark => {
            const title = bookmark.querySelector('a').textContent.toLowerCase();
            const url = bookmark.querySelector('a').href.toLowerCase();
            
            if (title.includes(searchTerm) || url.includes(searchTerm)) {
                bookmark.style.display = 'block';
            } else {
                bookmark.style.display = 'none';
            }
        });
    });

    // 点击其他地方关闭搜索框
    document.addEventListener('click', function(e) {
        const searchContainer = document.getElementById('searchContainer');
        const searchButton = document.querySelector('.search-button');
        
        if (!searchContainer.contains(e.target) && !searchButton.contains(e.target)) {
            searchContainer.style.display = 'none';
            searchInput.value = '';
            // 清除搜索结果
            document.querySelectorAll('.bookmark').forEach(bookmark => {
                bookmark.style.display = 'block';
            });
        }
    });
});

// 添加从历史记录中删除URL的函数
function removeFromHistory(url) {
    let history = getUrlHistory();
    history = history.filter(item => item !== url);
    localStorage.setItem('urlHistory', JSON.stringify(history));
} 