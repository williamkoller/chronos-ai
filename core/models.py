from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime

@dataclass
class Task:
    """Modelo de dados para tarefas"""
    id: str
    title: str
    category: str
    priority: str
    estimated_time: int
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    created_date: Optional[datetime] = None
    status: str = "pending"

@dataclass
class ScheduleSuggestion:
    """Modelo para sugestões de agendamento"""
    task_id: str
    suggested_datetime: datetime
    confidence_score: float
    reasoning: str
    duration_minutes: int
    alternatives: List[Dict]
    context_factors: Dict

@dataclass
class UserPattern:
    """Modelo para padrões do usuário"""
    pattern_type: str
    pattern_data: Dict
    confidence_level: float
    last_updated: datetime
    validation_count: int

@dataclass
class FeedbackData:
    """Modelo para feedback do usuário"""
    task_id: str
    suggestion_id: str
    rating: int  # 1-5
    comment: Optional[str]
    actual_execution_time: Optional[datetime]
    productivity_level: Optional[str]
    timestamp: datetime
