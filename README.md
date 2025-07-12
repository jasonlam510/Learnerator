# Learning Plan Generator with Ollama

A JavaScript-based learning plan generator that uses Ollama and local LLMs to create structured, comprehensive learning plans for any topic.

## Features

- 🎯 **Topic-based Learning Plans**: Generate personalized learning plans for any subject
- 🔍 **Search Keywords**: Each stage includes relevant keywords for online research
- 📚 **Structured Output**: Uses Zod schemas for type-safe, validated responses
- 🤖 **Local LLM**: Powered by Ollama - no API keys required
- 📊 **Progress Tracking**: Each stage includes status tracking
- 🎨 **Beautiful Console Output**: Formatted display with emojis and clear structure

## Prerequisites

1. **Node.js** (v18 or higher)
2. **Ollama** installed and running locally
3. A compatible model (e.g., `llama3.1`, `llama2`, `mistral`)

### Installing Ollama

Visit [ollama.ai](https://ollama.ai) and follow the installation instructions for your platform.

After installation, pull a model:
```bash
ollama pull llama3.1
```

## Installation

1. Clone or download this project
2. Navigate to the `plan_generation` directory
3. Install dependencies:

```bash
npm install
```

## Usage

### Basic Usage

Run the script with a default example:
```bash
npm start
```

### Programmatic Usage

```javascript
import { generateLearningPlan, displayLearningPlan } from './process.js';

// Generate a learning plan
const plan = await generateLearningPlan("machine learning fundamentals");
console.log(plan);

// Or display it with formatting
await displayLearningPlan("web development with React");
```

### Custom Model

```javascript
// Use a different Ollama model
const plan = await generateLearningPlan("python programming", "llama2");
```

## API Reference

### `generateLearningPlan(topic, model)`

Generates a structured learning plan for the given topic.

**Parameters:**
- `topic` (string): The learning topic to generate a plan for
- `model` (string, optional): The Ollama model to use (default: 'llama3.1')

**Returns:**
- `Promise<Object>`: The generated learning plan

**Example:**
```javascript
const plan = await generateLearningPlan("machine learning fundamentals");
```

### `displayLearningPlan(topic, model)`

Generates and displays a learning plan with formatted console output.

**Parameters:**
- `topic` (string): The learning topic
- `model` (string, optional): The Ollama model to use (default: 'llama3.1')

**Returns:**
- `Promise<Object>`: The generated learning plan

## Response Format

The API returns a structured learning plan with the following format:

```json
{
  "topic_name": "Machine Learning Fundamentals",
  "stages": [
    {
      "header": "Introduction to Machine Learning",
      "details": "Learn the basic concepts and types of machine learning algorithms",
      "keywords": ["machine learning basics", "ML algorithms", "supervised learning"],
      "status": "pending"
    },
    {
      "header": "Data Preprocessing",
      "details": "Understand data cleaning, normalization, and feature engineering",
      "keywords": ["data preprocessing", "feature engineering", "data cleaning"],
      "status": "pending"
    }
  ]
}
```

### Response Fields

- **topic_name**: Refined and properly formatted topic name
- **stages**: Array of learning stages (typically 5-10 stages), each containing:
  - **header**: Concise title for the learning stage
  - **details**: Detailed description of what the stage covers
  - **keywords**: List of 3-5 relevant search terms for online research
  - **status**: Current status (always "pending" for new plans)

## Example Output

```
🎯 Generating learning plan for: "machine learning fundamentals"
📚 Using model: llama3.1
⏳ Please wait...

📖 Learning Plan: Machine Learning Fundamentals
==================================================

1. Introduction to Machine Learning
   📝 Learn the basic concepts and types of machine learning algorithms
   🔍 Keywords: machine learning basics, ML algorithms, supervised learning
   📊 Status: pending

2. Data Preprocessing
   📝 Understand data cleaning, normalization, and feature engineering
   🔍 Keywords: data preprocessing, feature engineering, data cleaning
   📊 Status: pending

✅ Learning plan generated successfully!
```

## Error Handling

The module includes comprehensive error handling:

- **Empty Topic**: Throws an error if the topic is empty or only whitespace
- **Ollama Connection**: Handles connection errors to the Ollama service
- **Invalid Response**: Validates the LLM response using Zod schemas
- **JSON Parsing**: Handles malformed JSON responses

## Customization

### Modifying the Schema

You can customize the learning plan structure by modifying the Zod schemas:

```javascript
const Stage = z.object({
    header: z.string(),
    details: z.string(),
    keywords: z.array(z.string()),
    status: z.string().default("pending"),
    // Add custom fields here
    difficulty: z.enum(["beginner", "intermediate", "advanced"]).optional(),
    estimatedTime: z.string().optional()
});
```

### Changing the Prompt

Modify the prompt in the `generateLearningPlan` function to customize the output style or add specific requirements.

## Development

### Running in Development Mode

```bash
npm run dev
```

This uses Node.js's `--watch` flag to automatically restart when files change.

### Testing

Create custom test cases by modifying the `main()` function or create a separate test file.

## Dependencies

- **ollama**: JavaScript client for Ollama
- **zod**: TypeScript-first schema validation
- **zod-to-json-schema**: Convert Zod schemas to JSON Schema for structured output

## License

MIT License - feel free to use and modify as needed.

## Contributing

1. Fork the project
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Troubleshooting

### Common Issues

1. **Ollama not running**: Make sure Ollama is installed and running (`ollama serve`)
2. **Model not found**: Pull the required model (`ollama pull llama3.1`)
3. **Connection refused**: Check if Ollama is running on the default port (11434)
4. **Out of memory**: Try using a smaller model or increase system memory

### Getting Help

- Check the [Ollama documentation](https://github.com/jmorganca/ollama)
- Review the error messages - they usually provide clear guidance
- Ensure your Node.js version is 18 or higher 