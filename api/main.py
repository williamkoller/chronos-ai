import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
from datetime import datetime

app = FastAPI(
    title="CHRONOS AI API",
    description="Intelligent Time Orchestrator API",
    version="1.0.0"
)

# Modelos Pydantic para API
class TaskCreate(BaseModel):
    title: str
    category: str
    priority: str
    estimated_time: int
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    due_date: Optional[str] = None

class FeedbackSubmit(BaseModel):
    task_id: str
    rating: int
    comment: Optional[str] = None
    actual_execution_time: Optional[str] = None
    productivity_level: Optional[str] = None
    user_action: Optional[str] = None

class ScheduleOptimize(BaseModel):
    date: str
    preferences: Optional[Dict] = None

# Configuração global
config = {
    'notion_token': os.getenv('NOTION_TOKEN'),
    'database_id': os.getenv('DATABASE_ID'), 
    'claude_api_key': os.getenv('CLAUDE_API_KEY')
}

# Inicializa CHRONOS
try:
    from core.scheduler import ChronosCore
    chronos = ChronosCore(config)
    print("✅ CHRONOS inicializado com sucesso")
except Exception as e:
    print(f"❌ Erro ao inicializar CHRONOS: {e}")
    chronos = None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "CHRONOS AI - Intelligent Time Orchestrator",
        "version": "1.0.0",
        "status": "active"
    }

@app.post("/schedule/task")
async def schedule_task(task: TaskCreate):
    """Agenda uma nova tarefa com IA"""
    try:
        task_data = task.model_dump()
        
        # Verificar se chronos foi inicializado
        if not chronos:
            raise HTTPException(status_code=500, detail="CHRONOS não foi inicializado corretamente")
        
        result = chronos.orchestrate_schedule(task_data)
        
        return {
            "success": True,
            "task_id": result.get('suggestion', {}).get('task_id'),
            "scheduled_time": result.get('suggestion', {}).get('scheduled_datetime'),
            "confidence": result.get('confidence'),
            "reasoning": result.get('reasoning'),
            "alternatives": result.get('alternatives', [])
        }
        
    except ValueError as e:
        print(f"📋 Dados inválidos recebidos: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Dados da tarefa inválidos: {str(e)}")
    except KeyError as e:
        print(f"🔑 Campo obrigatório ausente: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Campo obrigatório ausente: {str(e)}")
    except ConnectionError as e:
        print(f"🔌 Erro de conectividade: {str(e)}")
        raise HTTPException(status_code=503, detail="Serviços externos indisponíveis")
    except TimeoutError as e:
        print(f"⏱️ Timeout na operação: {str(e)}")
        raise HTTPException(status_code=504, detail="Timeout ao processar requisição")
    except Exception as e:
        error_type = type(e).__name__
        print(f"⚠️ Erro inesperado [{error_type}]: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor [{error_type}]")

@app.post("/feedback/submit")
async def submit_feedback(feedback: FeedbackSubmit, background_tasks: BackgroundTasks):
    """Submete feedback do usuário"""
    try:
        feedback_data = feedback.model_dump()
        
        # Processa feedback em background
        background_tasks.add_task(process_feedback_async, feedback_data)
        
        return {
            "success": True,
            "message": "Feedback recebido e sendo processado",
            "feedback_id": feedback_data.get('task_id')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar feedback: {str(e)}")

@app.get("/schedule/optimize/{date}")
async def optimize_daily_schedule(date: str):
    """Otimiza cronograma de um dia específico"""
    try:
        target_date = datetime.fromisoformat(date)
        optimization = chronos.claude.optimize_daily_schedule([], {})
        
        return {
            "success": True,
            "date": date,
            "optimization": optimization,
            "workload_analysis": optimization.get('workload_analysis', {}),
            "recommendations": optimization.get('recommendations', [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na otimização: {str(e)}")

@app.get("/patterns/user")
async def get_user_patterns():
    """Retorna padrões aprendidos do usuário"""
    try:
        patterns = chronos.analyzer.get_current_patterns()
        
        return {
            "success": True,
            "patterns": patterns,
            "pattern_count": len(patterns),
            "last_analysis": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar padrões: {str(e)}")

@app.get("/analytics/performance")
async def get_performance_analytics():
    """Retorna analytics de performance"""
    try:
        feedback_trends = chronos.feedback.calculate_feedback_trends()
        recent_performance = chronos.analyzer.get_recent_performance()
        
        return {
            "success": True,
            "feedback_trends": feedback_trends,
            "recent_performance": recent_performance,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro em analytics: {str(e)}")

async def process_feedback_async(feedback_data: Dict):
    """Processa feedback de forma assíncrona"""
    try:
        chronos.feedback.process_feedback(feedback_data)
        print(f"✅ Feedback processado: {feedback_data.get('task_id')}")
    except Exception as e:
        print(f"❌ Erro no processamento do feedback: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)