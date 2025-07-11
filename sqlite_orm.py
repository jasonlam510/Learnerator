from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from example_model import Base, User, Post, Category
from typing import List, Optional
import os

class SQLiteORM:
    def __init__(self, db_path: str = "demo.db"):
        self.db_path = db_path
        self.engine = None
        self.SessionLocal = None
        self.setup_database()
    
    def setup_database(self):
        """Initialize the database connection and create tables"""
        try:
            # Create engine
            self.engine = create_engine(f'sqlite:///{self.db_path}', echo=False)
            
            # Create session factory
            self.SessionLocal = sessionmaker(bind=self.engine)
            
            # Create all tables
            Base.metadata.create_all(self.engine)
            
            print(f"Database initialized successfully at: {self.db_path}")
            
        except SQLAlchemyError as e:
            print(f"Error setting up database: {e}")
            raise
    
    def get_session(self):
        """Get a new database session"""
        return self.SessionLocal()
    
    def close_connection(self):
        """Close the database connection"""
        if self.engine:
            self.engine.dispose()
    
    # User operations
    def create_user(self, username: str, email: str) -> Optional[User]:
        """Create a new user"""
        session = self.get_session()
        try:
            user = User(username=username, email=email)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error creating user: {e}")
            return None
        finally:
            session.close()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            return user
        except SQLAlchemyError as e:
            print(f"Error getting user: {e}")
            return None
        finally:
            session.close()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            return user
        except SQLAlchemyError as e:
            print(f"Error getting user: {e}")
            return None
        finally:
            session.close()
    
    def get_all_users(self) -> List[User]:
        """Get all users"""
        session = self.get_session()
        try:
            users = session.query(User).all()
            return users
        except SQLAlchemyError as e:
            print(f"Error getting users: {e}")
            return []
        finally:
            session.close()
    
    # Category operations
    def create_category(self, name: str, description: str = None) -> Optional[Category]:
        """Create a new category"""
        session = self.get_session()
        try:
            category = Category(name=name, description=description)
            session.add(category)
            session.commit()
            session.refresh(category)
            return category
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error creating category: {e}")
            return None
        finally:
            session.close()
    
    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        session = self.get_session()
        try:
            category = session.query(Category).filter(Category.id == category_id).first()
            return category
        except SQLAlchemyError as e:
            print(f"Error getting category: {e}")
            return None
        finally:
            session.close()
    
    def get_all_categories(self) -> List[Category]:
        """Get all categories"""
        session = self.get_session()
        try:
            categories = session.query(Category).all()
            return categories
        except SQLAlchemyError as e:
            print(f"Error getting categories: {e}")
            return []
        finally:
            session.close()
    
    # Post operations
    def create_post(self, title: str, content: str, author_id: int, category_id: int) -> Optional[Post]:
        """Create a new post"""
        session = self.get_session()
        try:
            post = Post(title=title, content=content, author_id=author_id, category_id=category_id)
            session.add(post)
            session.commit()
            session.refresh(post)
            return post
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error creating post: {e}")
            return None
        finally:
            session.close()
    
    def get_post_by_id(self, post_id: int) -> Optional[Post]:
        """Get post by ID"""
        session = self.get_session()
        try:
            post = session.query(Post).filter(Post.id == post_id).first()
            return post
        except SQLAlchemyError as e:
            print(f"Error getting post: {e}")
            return None
        finally:
            session.close()
    
    def get_posts_by_user(self, user_id: int) -> List[Post]:
        """Get all posts by a specific user"""
        session = self.get_session()
        try:
            posts = session.query(Post).filter(Post.author_id == user_id).all()
            return posts
        except SQLAlchemyError as e:
            print(f"Error getting posts: {e}")
            return []
        finally:
            session.close()
    
    def get_posts_by_category(self, category_id: int) -> List[Post]:
        """Get all posts in a specific category"""
        session = self.get_session()
        try:
            posts = session.query(Post).filter(Post.category_id == category_id).all()
            return posts
        except SQLAlchemyError as e:
            print(f"Error getting posts: {e}")
            return []
        finally:
            session.close()
    
    def get_all_posts(self) -> List[Post]:
        """Get all posts"""
        session = self.get_session()
        try:
            posts = session.query(Post).all()
            return posts
        except SQLAlchemyError as e:
            print(f"Error getting posts: {e}")
            return []
        finally:
            session.close()
    
    def update_post(self, post_id: int, title: str = None, content: str = None) -> Optional[Post]:
        """Update a post"""
        session = self.get_session()
        try:
            post = session.query(Post).filter(Post.id == post_id).first()
            if post:
                if title:
                    post.title = title
                if content:
                    post.content = content
                session.commit()
                session.refresh(post)
                return post
            return None
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error updating post: {e}")
            return None
        finally:
            session.close()
    
    def delete_post(self, post_id: int) -> bool:
        """Delete a post"""
        session = self.get_session()
        try:
            post = session.query(Post).filter(Post.id == post_id).first()
            if post:
                session.delete(post)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error deleting post: {e}")
            return False
        finally:
            session.close()
    
    def search_posts(self, search_term: str) -> List[Post]:
        """Search posts by title or content"""
        session = self.get_session()
        try:
            posts = session.query(Post).filter(
                (Post.title.contains(search_term)) | 
                (Post.content.contains(search_term))
            ).all()
            return posts
        except SQLAlchemyError as e:
            print(f"Error searching posts: {e}")
            return []
        finally:
            session.close() 