/**
 * Tab Group Manager Module
 * Creates tab groups and opens multiple tabs in the specified order
 * Based on official Chrome API documentation
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
    
    // Check if chrome.tabs.group is available (this is how groups are created)
    if (typeof chrome.tabs.group !== 'function') {
      console.error('❌ TabGroupManager: chrome.tabs.group is not a function');
      return false;
    }
    
    // Check tabGroups methods
    if (typeof chrome.tabGroups.update !== 'function') {
      console.error('❌ TabGroupManager: chrome.tabGroups.update is not a function');
      return false;
    }
    
    if (typeof chrome.tabGroups.get !== 'function') {
      console.error('❌ TabGroupManager: chrome.tabGroups.get is not a function');
      return false;
    }
    
    console.log('✅ TabGroupManager: All required APIs are available');
    return true;
  }

  /**
   * Creates a tab group and opens multiple tabs with the specified URLs
   * Following official Chrome API documentation
   * @param {Object} input - The input object containing groupName and urls
   * @param {string} input.groupName - The name of the tab group
   * @param {string[]} input.urls - Array of URLs to open in new tabs
   * @returns {Promise<Object>} - Promise that resolves with the created group and tab IDs
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
      
      // Group the tabs using chrome.tabs.group (this is the correct way according to docs)
      console.log('🔍 TabGroupManager: Grouping tabs using chrome.tabs.group...');
      
      try {
        // Use chrome.tabs.group to create a group with the tabs
        // According to docs: "To group and ungroup tabs, or to query what tabs are in groups, use the chrome.tabs API"
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
        
        // Verify all tabs are in the group using chrome.tabs.query
        const tabsInGroup = await chrome.tabs.query({ groupId: groupId });
        console.log('🔍 TabGroupManager: Tabs in group', tabsInGroup);
        
        if (tabsInGroup.length !== tabIds.length) {
          console.warn('⚠️ TabGroupManager: Not all tabs are in the group!', {
            expected: tabIds.length,
            actual: tabsInGroup.length,
            tabIds,
            tabsInGroup: tabsInGroup.map(t => t.id)
          });
        }
        
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
        
        // If grouping fails, at least return the tabs that were created
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
  

  
  /**
   * Debug function to check tab group status
   * Following official API documentation
   */
  static async debugTabGroups() {
    try {
      console.log('🔍 TabGroupManager: Debugging tab groups...');
      
      // Check API availability first
      const apiAvailable = this.checkAPIs();
      
      // Get all windows
      const windows = await chrome.windows.getAll({ populate: true });
      console.log('🔍 TabGroupManager: All windows', windows);
      
      // Get all tab groups using chrome.tabGroups.query
      let groups = [];
      if (apiAvailable) {
        try {
          groups = await chrome.tabGroups.query({});
          console.log('🔍 TabGroupManager: All tab groups', groups);
        } catch (groupError) {
          console.error('❌ TabGroupManager: Error querying tab groups:', groupError);
        }
      }
      
      // Get all tabs using chrome.tabs.query
      const tabs = await chrome.tabs.query({});
      console.log('🔍 TabGroupManager: All tabs', tabs);
      
      // Check which tabs are grouped using chrome.tabs.TAB_ID_NONE
      let groupedTabs = [];
      let ungroupedTabs = [];
      
      if (apiAvailable) {
        groupedTabs = tabs.filter(tab => tab.groupId !== chrome.tabs.TAB_ID_NONE);
        ungroupedTabs = tabs.filter(tab => tab.groupId === chrome.tabs.TAB_ID_NONE);
      } else {
        // If API not available, assume all tabs are ungrouped
        ungroupedTabs = tabs;
      }
      
      console.log('🔍 TabGroupManager: Grouped tabs', groupedTabs);
      console.log('🔍 TabGroupManager: Ungrouped tabs', ungroupedTabs);
      
      return {
        apiAvailable: apiAvailable,
        windows: windows.length,
        groups: groups.length,
        totalTabs: tabs.length,
        groupedTabs: groupedTabs.length,
        ungroupedTabs: ungroupedTabs.length
      };
      
    } catch (error) {
      console.error('❌ TabGroupManager: Error debugging tab groups:', error);
      return { error: error.message };
    }
  }
  
  /**
   * Validates the input object structure
   * @param {Object} input - The input object to validate
   * @returns {boolean} - True if valid, false otherwise
   */
  static validateInput(input) {
    return input && 
           typeof input === 'object' && 
           typeof input.groupName === 'string' && 
           input.groupName.trim() !== '' &&
           Array.isArray(input.urls) && 
           input.urls.length > 0;
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = TabGroupManager;
} 