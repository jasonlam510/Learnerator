/**
 * Background Service Worker for Tab Group Manager Extension
 * Handles the core functionality for creating tab groups
 */

// Import the tab group module
importScripts('tabGroupModule.js');

/**
 * Handle messages from popup or other parts of the extension
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Background received message:', request);
  
  switch (request.action) {
    case 'createTabGroup':
      handleCreateTabGroup(request.data, sendResponse);
      return true; // Indicates async response
      
    default:
      sendResponse({
        success: false,
        error: 'Unknown action'
      });
  }
});

/**
 * Handle tab group creation request
 */
async function handleCreateTabGroup(data, sendResponse) {
  try {
    console.log('Creating tab group with data:', data);
    
    const result = await TabGroupManager.createTabGroupWithTabs(data);
    
    sendResponse({
      success: true,
      result: result
    });
    
  } catch (error) {
    console.error('Error in handleCreateTabGroup:', error);
    sendResponse({
      success: false,
      error: error.message
    });
  }
}

/**
 * Extension installation handler
 */
chrome.runtime.onInstalled.addListener((details) => {
  console.log('Tab Group Manager Extension installed:', details.reason);
  
  if (details.reason === 'install') {
    console.log('First time installation - extension is ready to use');
  }
});

/**
 * Extension startup handler
 */
chrome.runtime.onStartup.addListener(() => {
  console.log('Tab Group Manager Extension started');
});

// Log that background script is loaded
console.log('Tab Group Manager Background Script loaded'); 