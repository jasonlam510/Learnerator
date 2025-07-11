# SQLite ORM Demo with SQLAlchemy

## 🎯 What is this Demo?

This is a complete demonstration of how to create and use a SQLite database with SQLAlchemy ORM in Python. The demo includes:

- **Three related tables**: Users, Categories, and Posts with foreign key relationships
- **Full CRUD operations**: Create, Read, Update, Delete functionality
- **Advanced queries**: Search, filtering, and relationship-based queries
- **Best practices**: Proper session management, error handling, and database design

The demo creates sample data (users, categories, posts) and demonstrates various database operations including creating records, querying data, updating posts, and searching through content.

## 🚀 Steps to Run

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### 1. Create Virtual Environment
```bash
python3 -m venv venv
```

### 2. Activate Virtual Environment
```bash
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Demo
```bash
python main.py
```

This will create a `demo.db` file and run through all the database operations with sample data.

## 🔧 Where to Develop or Change

### Project Structure
```
.
├── example_model.py    # 📝 Define your database models here
├── sqlite_orm.py       # 🔧 Add your database operations here
├── main.py            # 🚀 Modify demo script or create your own
├── requirements.txt   # 📦 Add new dependencies here
└── demo.db           # 🗄️ SQLite database (auto-created)
```

### Key Files to Modify:

#### `example_model.py` - Database Models
- **Add new tables**: Create new classes inheriting from `Base`
- **Modify existing tables**: Add new columns, relationships, or constraints
- **Example**: Add a `Comment` table, `Profile` table, etc.

#### `sqlite_orm.py` - Database Operations
- **Add new query methods**: Create functions for specific database operations
- **Modify existing operations**: Enhance CRUD operations with more features
- **Example**: Add pagination, advanced search, bulk operations

#### `main.py` - Demo Script
- **Create your own demo**: Replace the existing demo with your use case
- **Add new test data**: Modify the sample data creation
- **Test new features**: Add demonstration code for new functionality

### Quick Development Tips:

1. **Add a new model**:
   ```python
   # In example_model.py
   class Comment(Base):
       __tablename__ = 'comments'
       id = Column(Integer, primary_key=True)
       text = Column(Text, nullable=False)
       post_id = Column(Integer, ForeignKey('posts.id'))
   ```

2. **Add corresponding operations**:
   ```python
   # In sqlite_orm.py
   def create_comment(self, text, post_id):
       # Implementation here
   ```

3. **Test your changes**:
   ```bash
   rm demo.db  # Delete old database
   python main.py  # Run with new changes
   ```

### Database Schema
The demo creates these tables:
- **Users**: id, username, email, created_at, is_active
- **Categories**: id, name, description, created_at
- **Posts**: id, title, content, created_at, updated_at, author_id, category_id

### Common Customizations:
- Add authentication/authorization
- Add image/file upload support
- Add API endpoints (Flask/FastAPI)
- Add data validation
- Add database migrations
- Add unit tests

## 📚 Learn More
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [SQLite Documentation](https://sqlite.org/docs.html)
