from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator

class PracticeExerciseTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
    difficulty: str
    objective: Optional[str] = None
    development: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

class PracticeExerciseBase(BaseModel):
    id: UUID
    exercise_description = Optional[PracticeExerciseTypeBase] = None
    
    
    
    # TODO: terminar esto