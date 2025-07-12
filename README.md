# Learning Plan Generator Chrome Extension

A Chrome extension that generates personalized learning plans for any topic using an LLM server.

## Features

- **Topic Input**: Enter any topic you want to learn (e.g., React, n8n, Python, etc.)
- **Learning Plan Generation**: Generate comprehensive learning plans with multiple stages
- **Visual Timeline**: Beautiful vertical timeline showing learning stages with status indicators
- **Status Tracking**: Visual indicators for finished (green), ongoing (yellow), and pending (grey) stages

## Installation

1. **Download/Clone** this repository to your local machine

2. **Open Chrome** and navigate to `chrome://extensions/`

3. **Enable Developer Mode** by toggling the switch in the top-right corner

4. **Click "Load unpacked"** and select the folder containing this extension

5. **Pin the extension** to your toolbar for easy access

## Usage

1. **Click the extension icon** in your Chrome toolbar
2. **Enter a topic** you want to learn (e.g., "React", "n8n", "Python", "Machine Learning")
3. **Click "Generate Learning Plan"** or press Enter
4. **View your personalized learning plan** with a beautiful timeline interface

## File Structure

```
├── manifest.json      # Chrome extension configuration
├── popup.html         # Extension popup interface
├── popup.js           # JavaScript logic and API calls
├── styles.css         # Styling for the timeline and UI
└── README.md          # This file
```

## LLM Server Integration

The extension currently uses dummy data for testing. To connect to your LLM server:

1. **Open `popup.js`**
2. **Find the `callLLMServer` function** (around line 60)
3. **Replace the TODO section** with your actual LLM server implementation

### Expected API Response Format

Your LLM server should return data in this format:

```javascript
[
    {
        "header": "Stage Title",
        "details": "Detailed description of what to learn in this stage",
        "status": "finished|ongoing|pending"
    },
    // ... more stages
]
```

### Example LLM Server Implementation

```javascript
async function callLLMServer(topic) {
    try {
        const response = await fetch('YOUR_LLM_SERVER_ENDPOINT', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer YOUR_API_KEY'
            },
            body: JSON.stringify({
                topic: topic,
                prompt: `Generate a comprehensive learning plan for ${topic} with 8-10 stages. Each stage should have a header and detailed description.`
            })
        });
        
        const data = await response.json();
        return data.learningPlan;
    } catch (error) {
        console.error('Error calling LLM server:', error);
        throw error;
    }
}
```

## Testing

The extension comes with dummy data for React learning, so you can test it immediately:

1. **Load the extension** as described above
2. **Enter any topic** (e.g., "React", "n8n", "Python")
3. **Click generate** to see the timeline with dummy data
4. **Observe the different status indicators**:
   - 🟢 Green dots: Finished stages
   - 🟡 Yellow dots: Ongoing stages  
   - ⚪ Grey dots: Pending stages

## Customization

### Adding More Dummy Data

To add more dummy learning plans for testing, modify the `dummyLearningPlan` array in `popup.js`.

### Styling Changes

Modify `styles.css` to customize the appearance of the timeline, colors, and overall design.

### Timeline Status Logic

The status logic can be enhanced to:
- Track user progress
- Save progress to local storage
- Allow manual status updates
- Sync with external learning platforms

## Browser Compatibility

- Chrome 88+
- Edge 88+ (Chromium-based)
- Other Chromium-based browsers

## Troubleshooting

1. **Extension not loading**: Make sure Developer Mode is enabled
2. **Changes not appearing**: Reload the extension after making changes
3. **API errors**: Check the browser console for detailed error messages
4. **Styling issues**: Clear browser cache and reload the extension

## License

This project is open source and available under the MIT License. 