#!/usr/bin/env python3
"""
Demo script for SQLite ORM with SQLAlchemy
This script demonstrates creating, querying, updating, and searching data.
"""

from sqlite_orm import SQLiteORM
from example_model import User, Post, Category
import os

def print_separator(title):
    """Print a nice separator for demo sections"""
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def create_sample_data(db):
    """Create sample data for demonstration"""
    print_separator("CREATING SAMPLE DATA")
    
    # Create categories
    categories = [
        ("Technology", "Posts about technology and programming"),
        ("Travel", "Posts about travel experiences"),
        ("Food", "Posts about cooking and recipes"),
        ("Sports", "Posts about various sports activities")
    ]
    
    created_categories = []
    for name, description in categories:
        category = db.create_category(name, description)
        if category:
            created_categories.append(category)
            print(f"Created category: {category.name}")
    
    # Create users
    users = [
        ("john_doe", "john@example.com"),
        ("jane_smith", "jane@example.com"),
        ("bob_wilson", "bob@example.com"),
        ("alice_brown", "alice@example.com")
    ]
    
    created_users = []
    for username, email in users:
        user = db.create_user(username, email)
        if user:
            created_users.append(user)
            print(f"Created user: {user.username} ({user.email})")
    
    # Create posts
    posts = [
        ("Getting Started with Python", "Python is a great programming language for beginners...", 1, 1),
        ("My Trip to Paris", "Last week I visited Paris and it was amazing...", 2, 2),
        ("Best Pasta Recipe", "Here's my grandmother's secret pasta recipe...", 3, 3),
        ("Football Season Highlights", "This season has been incredible for football fans...", 4, 4),
        ("Advanced SQLAlchemy Tips", "Here are some advanced tips for using SQLAlchemy...", 1, 1),
        ("Tokyo Travel Guide", "Tokyo is a fascinating city with so much to explore...", 2, 2),
        ("Homemade Pizza", "Nothing beats homemade pizza made from scratch...", 3, 3),
        ("Basketball Analytics", "Using data analytics to improve basketball performance...", 4, 4)
    ]
    
    created_posts = []
    for title, content, author_id, category_id in posts:
        post = db.create_post(title, content, author_id, category_id)
        if post:
            created_posts.append(post)
            print(f"Created post: {post.title}")
    
    return created_users, created_categories, created_posts

def demonstrate_queries(db):
    """Demonstrate various query operations"""
    print_separator("QUERYING DATA")
    
    # Get all users
    print("\n--- All Users ---")
    users = db.get_all_users()
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")
    
    # Get user by ID
    print("\n--- User by ID (ID=1) ---")
    user = db.get_user_by_id(1)
    if user:
        print(f"Found user: {user.username} ({user.email})")
    
    # Get user by username
    print("\n--- User by Username (jane_smith) ---")
    user = db.get_user_by_username("jane_smith")
    if user:
        print(f"Found user: {user.username} ({user.email})")
    
    # Get all categories
    print("\n--- All Categories ---")
    categories = db.get_all_categories()
    for category in categories:
        print(f"ID: {category.id}, Name: {category.name}, Description: {category.description}")
    
    # Get all posts
    print("\n--- All Posts ---")
    posts = db.get_all_posts()
    for post in posts:
        print(f"ID: {post.id}, Title: {post.title}")
        print(f"  Author: {post.author.username}, Category: {post.category.name}")
        print(f"  Content: {post.content[:50]}...")
    
    # Get posts by user
    print("\n--- Posts by User (john_doe) ---")
    user = db.get_user_by_username("john_doe")
    if user:
        posts = db.get_posts_by_user(user.id)
        for post in posts:
            print(f"- {post.title}")
    
    # Get posts by category
    print("\n--- Posts in Technology Category ---")
    category = db.get_category_by_id(1)  # Technology category
    if category:
        posts = db.get_posts_by_category(category.id)
        for post in posts:
            print(f"- {post.title} by {post.author.username}")

def demonstrate_search(db):
    """Demonstrate search functionality"""
    print_separator("SEARCHING DATA")
    
    # Search posts
    search_terms = ["Python", "travel", "recipe"]
    
    for term in search_terms:
        print(f"\n--- Search Results for '{term}' ---")
        posts = db.search_posts(term)
        if posts:
            for post in posts:
                print(f"- {post.title} by {post.author.username}")
        else:
            print(f"No posts found for '{term}'")

def demonstrate_updates(db):
    """Demonstrate update operations"""
    print_separator("UPDATING DATA")
    
    # Update a post
    post = db.get_post_by_id(1)
    if post:
        print(f"Original post title: {post.title}")
        
        updated_post = db.update_post(
            post.id, 
            title="Getting Started with Python - Updated Edition",
            content="This is the updated content for the Python tutorial..."
        )
        
        if updated_post:
            print(f"Updated post title: {updated_post.title}")
            print(f"Updated content: {updated_post.content[:50]}...")

def demonstrate_relationships(db):
    """Demonstrate relationship queries"""
    print_separator("RELATIONSHIP QUERIES")
    
    # Get user and their posts using relationships
    user = db.get_user_by_id(1)
    if user:
        print(f"\n--- Posts by {user.username} (using relationships) ---")
        for post in user.posts:
            print(f"- {post.title} in {post.category.name} category")
    
    # Get category and its posts
    category = db.get_category_by_id(1)
    if category:
        print(f"\n--- Posts in {category.name} category (using relationships) ---")
        for post in category.posts:
            print(f"- {post.title} by {post.author.username}")

def demonstrate_deletion(db):
    """Demonstrate deletion operations"""
    print_separator("DELETION OPERATIONS")
    
    # Create a test post to delete
    user = db.get_user_by_id(1)
    category = db.get_category_by_id(1)
    
    if user and category:
        test_post = db.create_post(
            "Test Post for Deletion",
            "This post will be deleted to demonstrate deletion functionality",
            user.id,
            category.id
        )
        
        if test_post:
            print(f"Created test post: {test_post.title} (ID: {test_post.id})")
            
            # Delete the post
            success = db.delete_post(test_post.id)
            if success:
                print(f"Successfully deleted post with ID: {test_post.id}")
            else:
                print(f"Failed to delete post with ID: {test_post.id}")

def main():
    """Main function to run the demo"""
    print("SQLite ORM Demo with SQLAlchemy")
    print("===============================")
    
    # Clean up existing database file
    if os.path.exists("demo.db"):
        os.remove("demo.db")
        print("Removed existing database file")
    
    # Initialize database
    db = SQLiteORM("demo.db")
    
    try:
        # Create sample data
        users, categories, posts = create_sample_data(db)
        
        # Demonstrate various operations
        demonstrate_queries(db)
        demonstrate_search(db)
        demonstrate_updates(db)
        demonstrate_relationships(db)
        demonstrate_deletion(db)
        
        print_separator("DEMO COMPLETED")
        print(f"Database file: {db.db_path}")
        print("You can examine the database using SQLite browser or command line tools")
        
    except Exception as e:
        print(f"Error during demo: {e}")
    finally:
        # Clean up
        db.close_connection()

if __name__ == "__main__":
    main() 