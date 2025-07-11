/**
 * Popup Script for Tab Group Manager Extension
 * Handles user interface interactions and communicates with background script
 */

// DOM elements
const elements = {
    groupName: document.getElementById('groupName'),
    urls: document.getElementById('urls'),
    createCustomGroup: document.getElementById('createCustomGroup'),
    loading: document.getElementById('loading'),
    status: document.getElementById('status')
};

/**
 * Initialize the popup
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('Tab Group Manager Popup loaded');
    setupEventListeners();
    showStatus('Ready to create tab groups', 'info');
});

/**
 * Set up event listeners
 */
function setupEventListeners() {
    // Custom tab group creation
    elements.createCustomGroup.addEventListener('click', handleCreateCustomGroup);
}

/**
 * Handle custom tab group creation
 */
async function handleCreateCustomGroup() {
    const groupName = elements.groupName.value.trim();
    const urlsText = elements.urls.value.trim();
    
    // Validate input
    if (!groupName) {
        showStatus('Please enter a group name', 'error');
        return;
    }
    
    if (!urlsText) {
        showStatus('Please enter at least one URL', 'error');
        return;
    }
    
    // Parse URLs
    const urls = urlsText.split('\n')
        .map(url => url.trim())
        .filter(url => url.length > 0);
    
    if (urls.length === 0) {
        showStatus('Please enter at least one valid URL', 'error');
        return;
    }
    
    // Validate URLs
    for (let i = 0; i < urls.length; i++) {
        try {
            new URL(urls[i]);
        } catch (e) {
            showStatus(`Invalid URL at line ${i + 1}: ${urls[i]}`, 'error');
            return;
        }
    }
    
    const data = { groupName, urls };
    
    showLoading(true);
    showStatus('Creating tab group...', 'info');
    
    try {
        const response = await sendMessage('createTabGroup', data);
        
        if (response.success) {
            const result = response.result;
            showStatus(`✅ ${result.message}`, 'success');
            
            // Clear form on success
            elements.groupName.value = '';
            elements.urls.value = '';
            
        } else {
            showStatus(`❌ Failed: ${response.error}`, 'error');
        }
        
    } catch (error) {
        console.error('Error creating custom tab group:', error);
        showStatus(`❌ Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

/**
 * Send message to background script
 */
function sendMessage(action, data = null) {
    return new Promise((resolve, reject) => {
        chrome.runtime.sendMessage({ action, data }, (response) => {
            if (chrome.runtime.lastError) {
                reject(new Error(chrome.runtime.lastError.message));
            } else {
                resolve(response);
            }
        });
    });
}

/**
 * Show/hide loading spinner
 */
function showLoading(show) {
    elements.loading.style.display = show ? 'block' : 'none';
}

/**
 * Show status message
 */
function showStatus(message, type = 'info') {
    elements.status.textContent = message;
    elements.status.className = `status ${type}`;
} 