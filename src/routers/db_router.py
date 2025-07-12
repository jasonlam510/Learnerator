from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from src.resources.sqlite.sqlite_orm import SQLiteORM
import os

# Initialize router
router = APIRouter(prefix="/api", tags=["LearnFlow API"])

# Initialize database
db_path = os.getenv("DB_PATH", "demo.db")
db = SQLiteORM(db_path)

# Pydantic models for request/response
class StageCreate(BaseModel):
    header: str
    details: str
    status: str = "pending"

class LearningPlanCreate(BaseModel):
    topic: str
    stages: List[StageCreate]

class LearningPlanResponse(BaseModel):
    id: int
    topic: str
    title: str
    created_at: datetime
    stages: List[dict]

    class Config:
        from_attributes = True

class StageStatusUpdate(BaseModel):
    status: str

class StageCompleteRequest(BaseModel):
    userId: int

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    message: str

class DBHealthResponse(BaseModel):
    status: str
    timestamp: datetime
    message: str
    database_connected: bool
    database_path: str

# Health Check Endpoint
@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        message="LearnFlow API is running"
    )

# Database Health Check Endpoint
@router.get("/health/db", response_model=DBHealthResponse)
async def db_health_check():
    """Database health check endpoint"""
    try:
        # Use the SQLiteORM method to check database health
        health_info = db.check_database_health()
        
        if health_info["connected"]:
            message = f"Database connection successful. Found {health_info['table_count']} tables."
            if health_info["all_tables_exist"]:
                message += " All expected tables exist."
            else:
                missing_tables = set(health_info["expected_tables"]) - set(health_info["existing_tables"])
                message += f" Missing tables: {list(missing_tables)}"
            
            return DBHealthResponse(
                status="healthy" if health_info["all_tables_exist"] else "warning",
                timestamp=datetime.utcnow(),
                message=message,
                database_connected=True,
                database_path=health_info["database_path"]
            )
        else:
            return DBHealthResponse(
                status="unhealthy",
                timestamp=datetime.utcnow(),
                message=f"Database connection failed: {health_info.get('error', 'Unknown error')}",
                database_connected=False,
                database_path=health_info["database_path"]
            )
            
    except Exception as e:
        return DBHealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            message=f"Database health check failed: {str(e)}",
            database_connected=False,
            database_path=db.db_path
        )

# Learning Plans Endpoints
@router.post("/learning-plans", response_model=LearningPlanResponse)
async def create_learning_plan(plan_data: LearningPlanCreate):
    """Create a new learning plan with stages"""
    try:
        # For now, we'll use a default user_id of 1
        # In a real app, this would come from authentication
        user_id = 1
        
        # Create the learning plan
        title = f"Learn {plan_data.topic}"
        learning_plan = db.create_learning_plan(
            user_id=user_id,
            topic=plan_data.topic,
            title=title
        )
        
        if not learning_plan:
            raise HTTPException(status_code=500, detail="Failed to create learning plan")
        
        # Create the stages
        stages = []
        for i, stage_data in enumerate(plan_data.stages):
            stage = db.create_learning_stage(
                plan_id=learning_plan.id,
                header=stage_data.header,
                details=stage_data.details,
                order_index=i + 1,
                status=stage_data.status
            )
            if stage:
                stages.append({
                    "id": stage.id,
                    "header": stage.header,
                    "details": stage.details,
                    "status": stage.status,
                    "order_index": stage.order_index
                })
        
        return LearningPlanResponse(
            id=learning_plan.id,
            topic=learning_plan.topic,
            title=learning_plan.title,
            created_at=learning_plan.created_at,
            stages=stages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating learning plan: {str(e)}")

@router.get("/learning-plans", response_model=List[LearningPlanResponse])
async def get_all_learning_plans():
    """Get all learning plans"""
    try:
        plans = db.get_all_learning_plans()
        result = []
        
        for plan in plans:
            stages = db.get_learning_stages_by_plan(plan.id)
            stage_data = [
                {
                    "id": stage.id,
                    "header": stage.header,
                    "details": stage.details,
                    "status": stage.status,
                    "order_index": stage.order_index
                }
                for stage in stages
            ]
            
            result.append(LearningPlanResponse(
                id=plan.id,
                topic=plan.topic,
                title=plan.title,
                created_at=plan.created_at,
                stages=stage_data
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting learning plans: {str(e)}")

@router.get("/learning-plans/{topic}", response_model=List[LearningPlanResponse])
async def get_learning_plans_by_topic(topic: str):
    """Get learning plans by topic"""
    try:
        plans = db.get_learning_plans_by_topic(topic)
        result = []
        
        for plan in plans:
            stages = db.get_learning_stages_by_plan(plan.id)
            stage_data = [
                {
                    "id": stage.id,
                    "header": stage.header,
                    "details": stage.details,
                    "status": stage.status,
                    "order_index": stage.order_index
                }
                for stage in stages
            ]
            
            result.append(LearningPlanResponse(
                id=plan.id,
                topic=plan.topic,
                title=plan.title,
                created_at=plan.created_at,
                stages=stage_data
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting learning plans by topic: {str(e)}")

@router.delete("/learning-plans/{plan_id}")
async def delete_learning_plan(plan_id: int):
    """Delete a learning plan"""
    try:
        success = db.delete_learning_plan(plan_id)
        if not success:
            raise HTTPException(status_code=404, detail="Learning plan not found")
        
        return {"message": "Learning plan deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting learning plan: {str(e)}")

# Learning Stages Endpoints
@router.put("/stages/{stage_id}/status")
async def update_stage_status(stage_id: int, status_update: StageStatusUpdate):
    """Update learning stage status"""
    try:
        stage = db.update_stage_status(stage_id, status_update.status)
        if not stage:
            raise HTTPException(status_code=404, detail="Learning stage not found")
        
        return {
            "id": stage.id,
            "header": stage.header,
            "status": stage.status,
            "message": "Stage status updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating stage status: {str(e)}")

@router.post("/stages/{stage_id}/complete")
async def mark_stage_completed(stage_id: int, complete_request: StageCompleteRequest):
    """Mark a learning stage as completed for a user"""
    try:
        progress = db.mark_stage_completed(complete_request.userId, stage_id)
        if not progress:
            raise HTTPException(status_code=404, detail="Learning stage not found")
        
        return {
            "message": "Stage marked as completed",
            "user_id": progress.user_id,
            "stage_id": progress.stage_id,
            "completed_at": progress.completed_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking stage completed: {str(e)}")

# User Progress Endpoints
@router.get("/progress/{user_id}")
async def get_user_progress(user_id: int):
    """Get user progress for all learning stages"""
    try:
        # Get all progress records for the user
        progress_records = db.get_user_progress(user_id)
        
        # Get completed stages
        completed_stages = db.get_completed_stages_for_user(user_id)
        
        # Get all learning plans for the user
        user_plans = db.get_learning_plans_by_user(user_id)
        
        progress_data = []
        for plan in user_plans:
            stages = db.get_learning_stages_by_plan(plan.id)
            plan_progress = {
                "plan_id": plan.id,
                "topic": plan.topic,
                "title": plan.title,
                "stages": []
            }
            
            for stage in stages:
                is_completed = any(
                    progress.stage_id == stage.id 
                    for progress in progress_records
                )
                
                plan_progress["stages"].append({
                    "id": stage.id,
                    "header": stage.header,
                    "details": stage.details,
                    "status": stage.status,
                    "order_index": stage.order_index,
                    "completed": is_completed
                })
            
            progress_data.append(plan_progress)
        
        return {
            "user_id": user_id,
            "total_completed_stages": len(completed_stages),
            "learning_plans": progress_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user progress: {str(e)}")

# Additional utility endpoints
@router.get("/users/{user_id}/learning-plans")
async def get_user_learning_plans(user_id: int):
    """Get all learning plans for a specific user"""
    try:
        plans = db.get_learning_plans_by_user(user_id)
        result = []
        
        for plan in plans:
            stages = db.get_learning_stages_by_plan(plan.id)
            stage_data = [
                {
                    "id": stage.id,
                    "header": stage.header,
                    "details": stage.details,
                    "status": stage.status,
                    "order_index": stage.order_index
                }
                for stage in stages
            ]
            
            result.append({
                "id": plan.id,
                "topic": plan.topic,
                "title": plan.title,
                "created_at": plan.created_at,
                "stages": stage_data
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user learning plans: {str(e)}")

@router.get("/stages/{stage_id}")
async def get_stage_details(stage_id: int):
    """Get details of a specific learning stage"""
    try:
        stage = db.get_learning_stage_by_id(stage_id)
        if not stage:
            raise HTTPException(status_code=404, detail="Learning stage not found")
        
        return {
            "id": stage.id,
            "plan_id": stage.plan_id,
            "header": stage.header,
            "details": stage.details,
            "status": stage.status,
            "order_index": stage.order_index,
            "created_at": stage.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stage details: {str(e)}") 