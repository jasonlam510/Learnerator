# Tab Group Manager Module

A JavaScript module for creating tab groups in Chrome extensions.

## 🎯 What This Is

- **`tabGroupModule.js`** - The main module for developers
- **Demo Extension** - Working example showing integration

## 🚀 Quick Start

### 1. Include the Module
```javascript
importScripts('tabGroupModule.js');
```

### 2. Use the Module
```javascript
const result = await TabGroupManager.createTabGroupWithTabs({
  groupName: "Development Tools",
  urls: ["https://github.com", "https://stackoverflow.com"]
});

if (result.success) {
  console.log(`Created: ${result.groupTitle}`);
}
```

## 📁 Files

```
├── tabGroupModule.js      # 🎯 MAIN MODULE
├── background.js          # 📖 Example integration
├── popup.html/js          # 📖 Example UI
├── manifest.json          # 📖 Example config
└── icons/                 # 📖 Example icons
```

## 🔧 API

### `createTabGroupWithTabs(input)`
Creates a tab group with multiple URLs.

**Parameters:** `{ groupName: string, urls: string[] }`

**Returns:** `{ success: boolean, groupId: number, groupTitle: string, tabIds: number[], message: string }`

### `validateInput(input)`
Validates input object structure.

## 📋 Required Permissions
```json
{
  "permissions": ["tabs", "tabGroups"]
}
```

## 🧪 Test the Module
Load the demo extension in Chrome to see it in action.

## 🐛 Troubleshooting
- Ensure `tabGroupModule.js` is in your extension directory
- Include required permissions in manifest.json
- Verify URLs are valid and accessible

---

**Note**: This is function 1 of 3. More functions coming soon.
