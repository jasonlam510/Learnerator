# Learning Resource Pipeline 🎓

An AI-powered learning resource discovery and analysis system that automatically finds, processes, and organizes educational content into an interactive dashboard.

## Features ✨

- **🔍 Intelligent Resource Discovery**: Automatically finds relevant web articles and YouTube videos
- **🧠 AI-Powered Analysis**: Uses LLMs to extract key concepts and generate summaries
- **💾 Vector Database Storage**: Stores content for semantic search and RAG capabilities
- **🎨 Interactive Dashboard**: Generates beautiful HTML dashboards with knowledge maps
- **📝 Quiz Generation**: Creates quizzes based on learned content
- **🌐 Local Server**: Serves dashboards on localhost for easy viewing

## Quick Start 🚀

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Setup
Create a `.env` file with your API keys:
```env
TOGETHER_API_KEY=your_together_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_custom_search_engine_id_here
YOUTUBE_API_KEY=your_youtube_api_key_here
```

### 3. Run the Pipeline

#### Option A: Easy Launcher (Recommended)
```bash
python launch_pipeline.py
```
Choose from preset learning paths or create custom topics.

#### Option B: Direct Pipeline
```bash
python main_pipeline.py
```
Follow the prompts to enter topics and configuration.

#### Option C: Quick Test
```bash
python quick_test_pipeline.py
```
Runs a minimal test with Python basics.

### 4. View Dashboard
Open your browser to `http://localhost:8000` to explore your learning dashboard!

## How It Works 🔧

### Pipeline Steps

1. **Resource Collection** 📚
   - Searches Google for web articles
   - Finds relevant YouTube videos
   - Extracts content and metadata

2. **Content Processing** 🧠
   - Extracts text from web pages and video transcripts
   - Generates embeddings using SentenceTransformer
   - Stores in Milvus vector database

3. **AI Analysis** 🤖
   - Analyzes content using Together AI LLMs
   - Extracts key concepts and relationships
   - Generates practical examples and summaries

4. **Dashboard Generation** 🎨
   - Creates interactive HTML dashboard
   - Builds knowledge relationship maps
   - Generates quizzes based on content

5. **Local Serving** 🌐
   - Starts HTTP server on localhost:8000
   - Auto-opens browser to view dashboard

### Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   URL Module    │───▶│   RAG Module    │───▶│ Summary Module  │
│                 │    │                 │    │                 │
│ • Resource      │    │ • Vector DB     │    │ • Content       │
│   Finder        │    │ • Embeddings    │    │   Analyzer      │
│ • Web Scraping  │    │ • Milvus        │    │ • HTML Gen      │
│ • YouTube API   │    │ • RAG Chat      │    │ • Dashboard     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Dashboard Features 📊

### Interactive Knowledge Map
- **D3.js Visualization**: Interactive node-link diagram
- **Concept Relationships**: Shows how topics connect
- **Hover Details**: Concept information and connections
- **Zoom & Pan**: Navigate large knowledge graphs

### Resource Cards
- **Rich Summaries**: AI-generated content summaries
- **Practical Examples**: Real-world application examples
- **Key Concepts**: Tagged topic categories
- **Source Links**: Direct links to original content

### Generated Quizzes
- **Multiple Choice**: Questions based on learned content
- **Progress Tracking**: Visual progress indicators
- **Detailed Results**: Explanation for each answer
- **Topic Coverage**: Questions span all collected topics

### Navigation
- **Topic Clusters**: Organized by subject areas
- **Learning Paths**: Suggested progression routes
- **Search & Filter**: Find specific content quickly

## Configuration Options ⚙️

### Environment Variables
- `TOGETHER_API_KEY`: Together AI API key for LLM analysis
- `GOOGLE_API_KEY`: Google API key for web search
- `GOOGLE_CSE_ID`: Custom Search Engine ID
- `YOUTUBE_API_KEY`: YouTube Data API key

### Pipeline Parameters
- `max_results_per_topic`: Number of resources per topic (1-10)
- `include_quiz`: Generate quizzes (True/False)
- `auto_open_browser`: Auto-open dashboard (True/False)

## Preset Learning Paths 🎯

1. **Web Development Fundamentals**
   - HTML & CSS basics
   - JavaScript fundamentals  
   - React introduction

2. **Python Programming**
   - Python basics
   - Object-oriented programming
   - Data structures

3. **Data Science Essentials**
   - Python data analysis
   - Machine learning basics
   - Data visualization

4. **DevOps & Cloud**
   - Docker containers
   - Kubernetes basics
   - AWS fundamentals

5. **AI & Machine Learning**
   - ML algorithms
   - Deep learning
   - Natural language processing

## File Structure 📁

```
Learning Resource Pipeline/
├── main_pipeline.py          # Main pipeline orchestrator
├── launch_pipeline.py        # Easy launcher with presets
├── quick_test_pipeline.py    # Quick test script
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── .env                     # Environment variables (create this)
│
├── url_module/              # Resource discovery
│   └── learning_resource_finder.py
│
├── rag_module/              # Vector database & RAG
│   ├── vector_database.py
│   ├── rag_chatbot.py
│   └── chatbot_api.py
│
├── summary_module/          # Analysis & dashboard
│   ├── content_analyzer.py
│   ├── html_generator.py
│   └── html_components/     # Modular HTML generators
│       ├── knowledge_diagram.py
│       ├── content_cards.py
│       ├── quiz_interface.py
│       ├── navigation.py
│       └── styles.py
│
└── utils/                   # Shared utilities
    └── schema.py           # Data models
```

## API Keys Setup 🔑

### Together AI (Required for LLM analysis)
1. Sign up at [together.ai](https://together.ai)
2. Get your API key from the dashboard
3. Add to `.env`: `TOGETHER_API_KEY=your_key_here`

### Google APIs (Optional - enables web search)
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Enable Custom Search API
3. Create API key and Custom Search Engine
4. Add to `.env`:
   ```
   GOOGLE_API_KEY=your_api_key
   GOOGLE_CSE_ID=your_cse_id
   ```

### YouTube API (Optional - enables video search)
1. Enable YouTube Data API v3 in Google Cloud
2. Add to `.env`: `YOUTUBE_API_KEY=your_youtube_key`

## Troubleshooting 🔧

### Common Issues

**No resources found**
- Check API keys in `.env` file
- Verify internet connection
- Try different search topics

**Dashboard not loading**
- Ensure server started successfully
- Check `http://localhost:8000` in browser
- Look for `learning_dashboard.html` file

**Import errors**
- Run `pip install -r requirements.txt`
- Check Python version (3.8+ required)

**Vector database errors**
- Ensure Milvus is installed and running
- Check Docker setup if using containerized Milvus

### Mock Mode
If APIs are unavailable, the system automatically falls back to mock data to demonstrate dashboard functionality.

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `quick_test_pipeline.py`
5. Submit a pull request

## License 📄

MIT License - see LICENSE file for details.

---

**Happy Learning! 🎓✨**
