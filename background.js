/**
 * Background script for LearnFlow Chrome Extension
 * Handles cross-origin API requests to Ollama FastAPI server
 */

// API Configuration
const OLLAMA_API_URL = 'http://localhost:8000';
const BACKEND_API_URL = 'http://localhost:3000/api';

/**
 * Tab Group Manager Class
 * Creates tab groups and opens multiple tabs in the specified order
 */
class TabGroupManager {
    /**
     * Check if required APIs are available
     */
    static checkAPIs() {
        console.log('🔍 TabGroupManager: Checking API availability...');
        
        if (typeof chrome === 'undefined') {
            console.error('❌ TabGroupManager: Chrome API not available');
            return false;
        }
        
        if (!chrome.tabs) {
            console.error('❌ TabGroupManager: chrome.tabs not available');
            return false;
        }
        
        if (!chrome.tabGroups) {
            console.error('❌ TabGroupManager: chrome.tabGroups not available');
            return false;
        }
        
        if (typeof chrome.tabs.group !== 'function') {
            console.error('❌ TabGroupManager: chrome.tabs.group is not a function');
            return false;
        }
        
        if (typeof chrome.tabGroups.update !== 'function') {
            console.error('❌ TabGroupManager: chrome.tabGroups.update is not a function');
            return false;
        }
        
        console.log('✅ TabGroupManager: All required APIs are available');
        return true;
    }

    /**
     * Creates a tab group and opens multiple tabs with the specified URLs
     */
    static async createTabGroupWithTabs(input) {
        try {
            const { groupName, urls } = input;
            
            console.log('🔍 TabGroupManager: Starting tab group creation', { groupName, urls });
            
            // Check if APIs are available
            if (!this.checkAPIs()) {
                throw new Error('Required APIs are not available. Please ensure you have the correct permissions and Chrome version (89+).');
            }
            
            // Validate input
            if (!groupName || typeof groupName !== 'string') {
                throw new Error('groupName must be a non-empty string');
            }
            
            if (!Array.isArray(urls) || urls.length === 0) {
                throw new Error('urls must be a non-empty array');
            }
            
            // Validate URLs
            for (let i = 0; i < urls.length; i++) {
                if (!urls[i] || typeof urls[i] !== 'string') {
                    throw new Error(`URL at index ${i} must be a non-empty string`);
                }
                try {
                    new URL(urls[i]);
                } catch (e) {
                    throw new Error(`Invalid URL at index ${i}: ${urls[i]}`);
                }
            }
            
            // Get current window to ensure tabs are created in the right window
            const currentWindow = await chrome.windows.getCurrent();
            console.log('🔍 TabGroupManager: Current window', currentWindow);
            
            // Create tabs in sequence
            const tabIds = [];
            
            console.log('🔍 TabGroupManager: Creating tabs...');
            for (let i = 0; i < urls.length; i++) {
                console.log(`🔍 TabGroupManager: Creating tab ${i + 1}/${urls.length}: ${urls[i]}`);
                
                const tab = await chrome.tabs.create({
                    url: urls[i],
                    active: false, // Don't activate each tab as it's created
                    windowId: currentWindow.id // Ensure tabs are created in current window
                });
                
                console.log(`🔍 TabGroupManager: Created tab ${tab.id} for ${urls[i]}`);
                tabIds.push(tab.id);
            }
            
            console.log('🔍 TabGroupManager: All tabs created', tabIds);
            
            // Wait a moment for tabs to fully load
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // Group the tabs using chrome.tabs.group
            console.log('🔍 TabGroupManager: Grouping tabs using chrome.tabs.group...');
            
            try {
                const groupId = await chrome.tabs.group({
                    tabIds: tabIds
                });
                
                console.log('🔍 TabGroupManager: Tabs grouped with ID', groupId);
                
                // Update the group title using chrome.tabGroups.update
                await chrome.tabGroups.update(groupId, {
                    title: groupName
                });
                
                console.log('🔍 TabGroupManager: Group title updated');
                
                // Get the group details using chrome.tabGroups.get
                const group = await chrome.tabGroups.get(groupId);
                console.log('🔍 TabGroupManager: Group details', group);
                
                // Activate the first tab
                console.log('🔍 TabGroupManager: Activating first tab', tabIds[0]);
                await chrome.tabs.update(tabIds[0], { active: true });
                
                const result = {
                    success: true,
                    groupId: groupId,
                    groupTitle: group.title || groupName,
                    tabIds: tabIds,
                    message: `Successfully created tab group "${groupName}" with ${tabIds.length} tabs`
                };
                
                console.log('🔍 TabGroupManager: Success!', result);
                return result;
                
            } catch (groupError) {
                console.error('❌ TabGroupManager: Error grouping tabs:', groupError);
                
                return {
                    success: false,
                    error: `Failed to group tabs: ${groupError.message}`,
                    message: `Created ${tabIds.length} tabs but failed to group them`,
                    tabIds: tabIds,
                    groupError: groupError.message
                };
            }
            
        } catch (error) {
            console.error('❌ TabGroupManager: Error creating tab group with tabs:', error);
            return {
                success: false,
                error: error.message,
                message: 'Failed to create tab group with tabs'
            };
        }
    }
}

/**
 * Handle cross-origin HTTP requests using Fetch API
 * Possible parameters for request:
 *  action: "xhttp" for a cross-origin HTTP request
 *  method: Default "GET"
 *  url   : required, but not validated
 *  data  : data to send in a POST request
 *  headers: optional headers object
 *
 * The callback function is called upon completion of the request
 */
chrome.runtime.onMessage.addListener(function(request, sender, callback) {
    if (request.action === "xhttp") {
        handleFetchRequest(request, callback);
        return true; // prevents the callback from being called too early on return
    }
    
    // Handle tab group creation
    if (request.action === "createTabGroup") {
        createTabGroupWithTabs(request, callback);
        return true;
    }
    
    // Handle specific API actions
    if (request.action === "generateLearningPlan") {
        generateLearningPlan(request.topic, request.model, callback);
        return true;
    }
    
    if (request.action === "checkOllamaHealth") {
        checkOllamaHealth(callback);
        return true;
    }
    
    if (request.action === "checkBackendHealth") {
        checkBackendHealth(callback);
        return true;
    }
});

/**
 * Handle HTTP requests using Fetch API
 */
async function handleFetchRequest(request, callback) {
    try {
        const method = request.method ? request.method.toUpperCase() : 'GET';
        const url = request.url;
        
        // Prepare fetch options
        const fetchOptions = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                ...request.headers
            }
        };
        
        // Add body for POST requests
        if (method === 'POST' && request.data) {
            fetchOptions.body = request.data;
        }
        
        console.log('🔍 Background: Making fetch request', { method, url, options: fetchOptions });
        
        // Make the fetch request with timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
        
        fetchOptions.signal = controller.signal;
        
        const response = await fetch(url, fetchOptions);
        clearTimeout(timeoutId);
        
        console.log('🔍 Background: Fetch response', { status: response.status, ok: response.ok });
        
        // Parse response
        let data;
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            data = await response.text();
        }
        
        callback({
            success: response.ok,
            status: response.status,
            data: data
        });
        
    } catch (error) {
        console.error('❌ Background: Fetch error:', error);
        
        let errorMessage = 'Network error';
        let status = 0;
        
        if (error.name === 'AbortError') {
            errorMessage = 'Request timeout';
            status = 408;
        } else if (error.message) {
            errorMessage = error.message;
        }
        
        callback({
            success: false,
            error: errorMessage,
            status: status
        });
    }
}

/**
 * Create tab group with tabs using TabGroupManager
 */
async function createTabGroupWithTabs(request, callback) {
    try {
        console.log('🔍 Background: Creating tab group with tabs', request);
        
        const result = await TabGroupManager.createTabGroupWithTabs({
            groupName: request.groupName,
            urls: request.urls
        });
        
        console.log('🔍 Background: Tab group creation result', result);
        callback(result);
        
    } catch (error) {
        console.error('❌ Background: Error creating tab group:', error);
        callback({
            success: false,
            error: error.message,
            message: 'Failed to create tab group'
        });
    }
}

/**
 * Generate learning plan using Ollama API
 */
async function generateLearningPlan(topic, model = 'llama2', callback) {
    try {
        console.log(`🤖 Background: Generating learning plan for "${topic}" using model: ${model}`);
        
        // Make direct fetch request to Ollama API
        const response = await fetch(`${OLLAMA_API_URL}/generate-plan`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                topic: topic,
                model: model
            })
        });
        
        console.log('🔍 Background: API response status:', response.status);
        console.log('🔍 Background: API response ok:', response.ok);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        // Parse the JSON response
        const data = await response.json();
        console.log('🔍 Background: Parsed API response:', data);
        
        // Validate response structure
        if (!data.topic_name || !data.stages || !Array.isArray(data.stages)) {
            throw new Error('Invalid API response structure');
        }
        
        console.log('✅ Background: Learning plan generated successfully');
        console.log('🔍 Background: Topic:', data.topic_name);
        console.log('🔍 Background: Number of stages:', data.stages.length);
        
        // Return the response in the expected format
        callback({
            success: true,
            data: {
                topic_name: data.topic_name,
                stages: data.stages
            }
        });
        
    } catch (error) {
        console.error('❌ Background: Error generating learning plan:', error);
        callback({
            success: false,
            error: error.message
        });
    }
}

/**
 * Check if Ollama API is available
 */
async function checkOllamaHealth(callback) {
    try {
        const response = await makeRequest({
            method: 'GET',
            url: `${OLLAMA_API_URL}/health`
        });
        
        if (response.success && response.status === 200) {
            callback({
                success: true,
                available: response.data.ollama_status === 'connected',
                data: response.data
            });
        } else {
            callback({
                success: false,
                available: false,
                error: 'Health check failed'
            });
        }
        
    } catch (error) {
        console.error('❌ Background: Ollama health check failed:', error);
        callback({
            success: false,
            available: false,
            error: error.message
        });
    }
}

/**
 * Check if backend is available
 */
async function checkBackendHealth(callback) {
    try {
        const response = await makeRequest({
            method: 'GET',
            url: `${BACKEND_API_URL}/health`
        });
        
        callback({
            success: response.success,
            available: response.success && response.status === 200,
            data: response.data
        });
        
    } catch (error) {
        console.error('❌ Background: Backend health check failed:', error);
        callback({
            success: false,
            available: false,
            error: error.message
        });
    }
}

/**
 * Helper function to make HTTP requests using Fetch API
 */
async function makeRequest(options) {
    try {
        const method = options.method || 'GET';
        const url = options.url;
        
        // Prepare fetch options
        const fetchOptions = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };
        
        // Add body for POST requests
        if (method === 'POST' && options.data) {
            fetchOptions.body = typeof options.data === 'string' 
                ? options.data 
                : JSON.stringify(options.data);
        }
        
        console.log('🔍 Background: Making request', { method, url });
        
        // Make the fetch request with timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
        
        fetchOptions.signal = controller.signal;
        
        const response = await fetch(url, fetchOptions);
        clearTimeout(timeoutId);
        
        console.log('🔍 Background: Response received', { status: response.status, ok: response.ok });
        
        // Parse response
        let data;
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            data = await response.text();
        }
        
        return {
            success: response.ok,
            status: response.status,
            data: data
        };
        
    } catch (error) {
        console.error('❌ Background: Request error:', error);
        
        let errorMessage = 'Network error';
        let status = 0;
        
        if (error.name === 'AbortError') {
            errorMessage = 'Request timeout';
            status = 408;
        } else if (error.message) {
            errorMessage = error.message;
        }
        
        return {
            success: false,
            error: errorMessage,
            status: status
        };
    }
}

// Log when background script loads
console.log('🚀 LearnFlow Background Script Loaded');
console.log(`📡 Ready to handle API requests to:`);
console.log(`   - Ollama API: ${OLLAMA_API_URL}`);
console.log(`   - Backend API: ${BACKEND_API_URL}`);
console.log(`🔗 Tab Group Manager ready for learning resource organization`);
console.log(`✨ Using modern Fetch API for all HTTP requests`); 


