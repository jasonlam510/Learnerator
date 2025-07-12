from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .models import Base, User, LearningPlan, LearningStage, UserProgress
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
    
    # Learning Plan operations
    def create_learning_plan(self, user_id: int, topic: str, title: str) -> Optional[LearningPlan]:
        """Create a new learning plan"""
        session = self.get_session()
        try:
            learning_plan = LearningPlan(user_id=user_id, topic=topic, title=title)
            session.add(learning_plan)
            session.commit()
            session.refresh(learning_plan)
            return learning_plan
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error creating learning plan: {e}")
            return None
        finally:
            session.close()
    
    def get_learning_plan_by_id(self, plan_id: int) -> Optional[LearningPlan]:
        """Get learning plan by ID"""
        session = self.get_session()
        try:
            plan = session.query(LearningPlan).filter(LearningPlan.id == plan_id).first()
            return plan
        except SQLAlchemyError as e:
            print(f"Error getting learning plan: {e}")
            return None
        finally:
            session.close()
    
    def get_learning_plans_by_user(self, user_id: int) -> List[LearningPlan]:
        """Get all learning plans for a specific user"""
        session = self.get_session()
        try:
            plans = session.query(LearningPlan).filter(LearningPlan.user_id == user_id).all()
            return plans
        except SQLAlchemyError as e:
            print(f"Error getting learning plans: {e}")
            return []
        finally:
            session.close()
    
    def get_learning_plans_by_topic(self, topic: str) -> List[LearningPlan]:
        """Get all learning plans for a specific topic"""
        session = self.get_session()
        try:
            plans = session.query(LearningPlan).filter(LearningPlan.topic == topic).all()
            return plans
        except SQLAlchemyError as e:
            print(f"Error getting learning plans by topic: {e}")
            return []
        finally:
            session.close()
    
    def get_all_learning_plans(self) -> List[LearningPlan]:
        """Get all learning plans"""
        session = self.get_session()
        try:
            plans = session.query(LearningPlan).all()
            return plans
        except SQLAlchemyError as e:
            print(f"Error getting learning plans: {e}")
            return []
        finally:
            session.close()
    
    def delete_learning_plan(self, plan_id: int) -> bool:
        """Delete a learning plan"""
        session = self.get_session()
        try:
            plan = session.query(LearningPlan).filter(LearningPlan.id == plan_id).first()
            if plan:
                session.delete(plan)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error deleting learning plan: {e}")
            return False
        finally:
            session.close()
    
    # Learning Stage operations
    def create_learning_stage(self, plan_id: int, header: str, details: str, order_index: int, status: str = "pending") -> Optional[LearningStage]:
        """Create a new learning stage"""
        session = self.get_session()
        try:
            stage = LearningStage(
                plan_id=plan_id,
                header=header,
                details=details,
                order_index=order_index,
                status=status
            )
            session.add(stage)
            session.commit()
            session.refresh(stage)
            return stage
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error creating learning stage: {e}")
            return None
        finally:
            session.close()
    
    def get_learning_stage_by_id(self, stage_id: int) -> Optional[LearningStage]:
        """Get learning stage by ID"""
        session = self.get_session()
        try:
            stage = session.query(LearningStage).filter(LearningStage.id == stage_id).first()
            return stage
        except SQLAlchemyError as e:
            print(f"Error getting learning stage: {e}")
            return None
        finally:
            session.close()
    
    def get_learning_stages_by_plan(self, plan_id: int) -> List[LearningStage]:
        """Get all learning stages for a specific plan"""
        session = self.get_session()
        try:
            stages = session.query(LearningStage).filter(LearningStage.plan_id == plan_id).order_by(LearningStage.order_index).all()
            return stages
        except SQLAlchemyError as e:
            print(f"Error getting learning stages: {e}")
            return []
        finally:
            session.close()
    
    def update_stage_status(self, stage_id: int, status: str) -> Optional[LearningStage]:
        """Update learning stage status"""
        session = self.get_session()
        try:
            stage = session.query(LearningStage).filter(LearningStage.id == stage_id).first()
            if stage:
                stage.status = status
                session.commit()
                session.refresh(stage)
                return stage
            return None
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error updating stage status: {e}")
            return None
        finally:
            session.close()
    
    # User Progress operations
    def create_user_progress(self, user_id: int, stage_id: int) -> Optional[UserProgress]:
        """Create a new user progress record"""
        session = self.get_session()
        try:
            progress = UserProgress(user_id=user_id, stage_id=stage_id)
            session.add(progress)
            session.commit()
            session.refresh(progress)
            return progress
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error creating user progress: {e}")
            return None
        finally:
            session.close()
    
    def get_user_progress(self, user_id: int) -> List[UserProgress]:
        """Get all progress records for a specific user"""
        session = self.get_session()
        try:
            progress = session.query(UserProgress).filter(UserProgress.user_id == user_id).all()
            return progress
        except SQLAlchemyError as e:
            print(f"Error getting user progress: {e}")
            return []
        finally:
            session.close()
    
    def mark_stage_completed(self, user_id: int, stage_id: int) -> Optional[UserProgress]:
        """Mark a learning stage as completed for a user"""
        session = self.get_session()
        try:
            # Check if progress already exists
            existing_progress = session.query(UserProgress).filter(
                UserProgress.user_id == user_id,
                UserProgress.stage_id == stage_id
            ).first()
            
            if existing_progress:
                return existing_progress
            
            # Create new progress record
            progress = UserProgress(user_id=user_id, stage_id=stage_id)
            session.add(progress)
            
            # Update stage status to finished
            stage = session.query(LearningStage).filter(LearningStage.id == stage_id).first()
            if stage:
                stage.status = "finished"
            
            session.commit()
            session.refresh(progress)
            return progress
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error marking stage completed: {e}")
            return None
        finally:
            session.close()
    
    def get_completed_stages_for_user(self, user_id: int) -> List[LearningStage]:
        """Get all completed learning stages for a specific user"""
        session = self.get_session()
        try:
            completed_stages = session.query(LearningStage).join(UserProgress).filter(
                UserProgress.user_id == user_id
            ).all()
            return completed_stages
        except SQLAlchemyError as e:
            print(f"Error getting completed stages: {e}")
            return []
        finally:
            session.close()
    
    def create_learning_plan_with_stages(self, user_id: int, topic: str, title: str, stages_data: List[dict]) -> Optional[LearningPlan]:
        """Create a learning plan with multiple stages in a single transaction"""
        session = self.get_session()
        try:
            # Create the learning plan
            learning_plan = LearningPlan(user_id=user_id, topic=topic, title=title)
            session.add(learning_plan)
            session.flush()  # Get the ID without committing
            
            # Create the stages
            for i, stage_data in enumerate(stages_data):
                stage = LearningStage(
                    plan_id=learning_plan.id,
                    header=stage_data['header'],
                    details=stage_data['details'],
                    order_index=i + 1,
                    status=stage_data.get('status', 'pending')
                )
                session.add(stage)
            
            session.commit()
            session.refresh(learning_plan)
            return learning_plan
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error creating learning plan with stages: {e}")
            return None
        finally:
            session.close()
    
    def get_learning_plan_with_stages(self, plan_id: int) -> Optional[dict]:
        """Get a learning plan with all its stages"""
        session = self.get_session()
        try:
            plan = session.query(LearningPlan).filter(LearningPlan.id == plan_id).first()
            if not plan:
                return None
            
            stages = session.query(LearningStage).filter(
                LearningStage.plan_id == plan_id
            ).order_by(LearningStage.order_index).all()
            
            return {
                'plan': plan,
                'stages': stages
            }
        except SQLAlchemyError as e:
            print(f"Error getting learning plan with stages: {e}")
            return None
        finally:
            session.close()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.email == email).first()
            return user
        except SQLAlchemyError as e:
            print(f"Error getting user by email: {e}")
            return None
        finally:
            session.close()
    
    def create_user_if_not_exists(self, username: str, email: str) -> Optional[User]:
        """Create a user if they don't already exist"""
        session = self.get_session()
        try:
            # Check if user already exists
            existing_user = session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                return existing_user
            
            # Create new user
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
    
    def check_database_health(self) -> dict:
        """Check database connection and health"""
        try:
            session = self.get_session()
            try:
                # Test 1: Check if we can connect and query
                result = session.execute(text("SELECT COUNT(*) FROM sqlite_master WHERE type='table'"))
                table_count = result.scalar()
                
                # Test 2: Check if our tables exist
                tables = ['users', 'learning_plans', 'learning_stages', 'user_progress']
                existing_tables = []
                for table in tables:
                    result = session.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"))
                    if result.scalar():
                        existing_tables.append(table)
                
                return {
                    "connected": True,
                    "table_count": table_count,
                    "expected_tables": tables,
                    "existing_tables": existing_tables,
                    "all_tables_exist": len(existing_tables) == len(tables),
                    "database_path": self.db_path
                }
                
            except Exception as e:
                return {
                    "connected": False,
                    "error": str(e),
                    "database_path": self.db_path
                }
            finally:
                session.close()
                
        except Exception as e:
            return {
                "connected": False,
                "error": f"Failed to get database session: {str(e)}",
                "database_path": self.db_path
            } 