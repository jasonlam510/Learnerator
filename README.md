# LearnFlow Backend API

A Node.js backend server with SQLite database for the LearnFlow Chrome extension.

## 🚀 Quick Start

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn

### Installation

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Initialize the database:**
   ```bash
   npm run init-db
   ```

4. **Start the server:**
   ```bash
   npm run dev
   ```

The server will start on `http://localhost:3000`

## 📊 Database Schema

### Tables

#### `users`
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email
- `created_at` - Timestamp

#### `learning_plans`
- `id` - Primary key
- `user_id` - Foreign key to users
- `topic` - Learning topic (e.g., "React", "Python")
- `title` - Plan title
- `created_at` - Timestamp

#### `learning_stages`
- `id` - Primary key
- `plan_id` - Foreign key to learning_plans
- `header` - Stage title
- `details` - Stage description
- `status` - "pending", "ongoing", or "finished"
- `order_index` - Stage order
- `created_at` - Timestamp

#### `user_progress`
- `id` - Primary key
- `user_id` - Foreign key to users
- `stage_id` - Foreign key to learning_stages
- `completed_at` - Completion timestamp

## 🔌 API Endpoints

### Health Check
```
GET /api/health
```
Returns server status and timestamp.

### Learning Plans

#### Create Learning Plan
```
POST /api/learning-plans
```
**Body:**
```json
{
  "topic": "React",
  "stages": [
    {
      "header": "1. JavaScript Fundamentals",
      "details": "Master ES6+ features...",
      "status": "pending"
    }
  ]
}
```

#### Get All Learning Plans
```
GET /api/learning-plans
```

#### Get Learning Plan by Topic
```
GET /api/learning-plans/:topic
```

#### Delete Learning Plan
```
DELETE /api/learning-plans/:planId
```

### Learning Stages

#### Update Stage Status
```
PUT /api/stages/:stageId/status
```
**Body:**
```json
{
  "status": "finished"
}
```

#### Mark Stage as Completed
```
POST /api/stages/:stageId/complete
```
**Body:**
```json
{
  "userId": 1
}
```

### User Progress

#### Get User Progress
```
GET /api/progress/:userId
```

## 🧪 Testing the API

### Using curl

1. **Health check:**
   ```bash
   curl http://localhost:3000/api/health
   ```

2. **Get React learning plan:**
   ```bash
   curl http://localhost:3000/api/learning-plans/React
   ```

3. **Create new learning plan:**
   ```bash
   curl -X POST http://localhost:3000/api/learning-plans \
     -H "Content-Type: application/json" \
     -d '{
       "topic": "Python",
       "stages": [
         {
           "header": "1. Python Basics",
           "details": "Learn Python syntax and basic concepts",
           "status": "pending"
         }
       ]
     }'
   ```

### Using Postman

Import the following collection:

```json
{
  "info": {
    "name": "LearnFlow API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "http://localhost:3000/api/health"
      }
    },
    {
      "name": "Get React Plan",
      "request": {
        "method": "GET",
        "url": "http://localhost:3000/api/learning-plans/React"
      }
    }
  ]
}
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
PORT=3000
NODE_ENV=development
DB_PATH=./database/learnflow.db
```

### Database Location

The SQLite database is stored in:
```
backend/database/learnflow.db
```

## 📁 Project Structure

```
backend/
├── package.json
├── server.js              # Main server file
├── init-database.js       # Database initialization
├── database/
│   └── learnflow.db      # SQLite database file
└── README.md
```

## 🚀 Deployment

### Development
```bash
npm run dev
```

### Production
```bash
npm start
```

## 🔍 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   lsof -ti:3000 | xargs kill -9
   ```

2. **Database locked:**
   - Stop the server
   - Delete the database file
   - Run `npm run init-db` again

3. **CORS issues:**
   - Ensure the Chrome extension is making requests to `http://localhost:3000`
   - Check that CORS middleware is enabled

### Logs

The server logs all requests and errors to the console. Check for:
- Database connection errors
- SQL syntax errors
- Missing required fields

## 🔐 Security Notes

- This is a development setup
- For production, consider:
  - Adding authentication
  - Using HTTPS
  - Input validation
  - Rate limiting
  - Database backups

## 📞 Support

For issues or questions:
1. Check the logs
2. Verify database initialization
3. Test API endpoints with curl or Postman
4. Ensure all dependencies are installed 