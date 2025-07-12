from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User model representing users in the LearnFlow system"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    learning_plans = relationship("LearningPlan", back_populates="user")
    user_progress = relationship("UserProgress", back_populates="user")
    
    def __repr__(self):
        return f'<User {self.username}>'

class LearningPlan(Base):
    """Learning plan model representing a user's learning plan for a specific topic"""
    __tablename__ = 'learning_plans'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    topic = Column(String(100), nullable=False)  # e.g., "React", "Python"
    title = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="learning_plans")
    learning_stages = relationship("LearningStage", back_populates="learning_plan", order_by="LearningStage.order_index")
    
    def __repr__(self):
        return f'<LearningPlan {self.topic}: {self.title}>'

class LearningStage(Base):
    """Learning stage model representing individual stages within a learning plan"""
    __tablename__ = 'learning_stages'
    
    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey('learning_plans.id'), nullable=False)
    header = Column(String(200), nullable=False)  # Stage title
    details = Column(Text, nullable=False)  # Stage description
    status = Column(String(20), default="pending")  # "pending", "ongoing", or "finished"
    order_index = Column(Integer, nullable=False)  # Stage order
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    learning_plan = relationship("LearningPlan", back_populates="learning_stages")
    user_progress = relationship("UserProgress", back_populates="learning_stage")
    
    def __repr__(self):
        return f'<LearningStage {self.header} (Status: {self.status})>'

class UserProgress(Base):
    """User progress model tracking completion of learning stages"""
    __tablename__ = 'user_progress'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    stage_id = Column(Integer, ForeignKey('learning_stages.id'), nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="user_progress")
    learning_stage = relationship("LearningStage", back_populates="user_progress")
    
    def __repr__(self):
        return f'<UserProgress User:{self.user_id} Stage:{self.stage_id}>' 