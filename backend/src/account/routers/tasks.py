from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from src.core.orm.database import get_db
from src.core.auth import get_current_user
from src.account.models.user import User
from src.tasks.wallet_monitor import (
    trigger_wallet_monitoring,
    trigger_deposit_processing,
    trigger_specific_wallet_monitoring
)
from src.core.celery_app import celery_app

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/monitor-wallets/trigger")
async def trigger_wallet_monitoring_task(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Запускает мониторинг кошельков вручную (только для админов)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        task_id = trigger_wallet_monitoring()
        return {
            "message": "Wallet monitoring task triggered",
            "task_id": task_id,
            "status": "PENDING"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error triggering task: {str(e)}"
        )


@router.post("/process-deposits/trigger")
async def trigger_deposit_processing_task(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Запускает обработку депозитов вручную (только для админов)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        task_id = trigger_deposit_processing()
        return {
            "message": "Deposit processing task triggered",
            "task_id": task_id,
            "status": "PENDING"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error triggering task: {str(e)}"
        )


@router.post("/monitor-wallet/{wallet_id}/trigger")
async def trigger_specific_wallet_monitoring_task(
    wallet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Запускает мониторинг конкретного кошелька (только для админов)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        task_id = trigger_specific_wallet_monitoring(wallet_id)
        return {
            "message": f"Specific wallet monitoring task triggered for wallet {wallet_id}",
            "task_id": task_id,
            "status": "PENDING"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error triggering task: {str(e)}"
        )


@router.get("/status/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """Получает статус задачи по ID"""
    try:
        task_result = celery_app.AsyncResult(task_id)
        
        response = {
            "task_id": task_id,
            "status": task_result.status,
            "info": task_result.info
        }
        
        if task_result.status == "SUCCESS":
            response["result"] = task_result.result
        elif task_result.status == "FAILURE":
            response["error"] = str(task_result.info)
        elif task_result.status == "PROGRESS":
            response["progress"] = task_result.info
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting task status: {str(e)}"
        )


@router.get("/active")
async def get_active_tasks(
    current_user: User = Depends(get_current_user)
):
    """Получает список активных задач (только для админов)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        # Получаем активные задачи
        active_tasks = celery_app.control.inspect().active()
        
        if not active_tasks:
            return {"active_tasks": []}
        
        # Форматируем результат
        formatted_tasks = []
        for worker, tasks in active_tasks.items():
            for task in tasks:
                formatted_tasks.append({
                    "worker": worker,
                    "task_id": task["id"],
                    "task_name": task["name"],
                    "started_at": task["time_start"],
                    "args": task["args"],
                    "kwargs": task["kwargs"]
                })
        
        return {"active_tasks": formatted_tasks}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting active tasks: {str(e)}"
        )


@router.get("/scheduled")
async def get_scheduled_tasks(
    current_user: User = Depends(get_current_user)
):
    """Получает список запланированных задач (только для админов)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        # Получаем запланированные задачи
        scheduled_tasks = celery_app.control.inspect().scheduled()
        
        if not scheduled_tasks:
            return {"scheduled_tasks": []}
        
        # Форматируем результат
        formatted_tasks = []
        for worker, tasks in scheduled_tasks.items():
            for task in tasks:
                formatted_tasks.append({
                    "worker": worker,
                    "task_id": task["id"],
                    "task_name": task["name"],
                    "eta": task["eta"],
                    "args": task["args"],
                    "kwargs": task["kwargs"]
                })
        
        return {"scheduled_tasks": formatted_tasks}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting scheduled tasks: {str(e)}"
        )


@router.get("/stats")
async def get_celery_stats(
    current_user: User = Depends(get_current_user)
):
    """Получает статистику Celery (только для админов)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        # Получаем статистику воркеров
        stats = celery_app.control.inspect().stats()
        
        if not stats:
            return {"stats": {}}
        
        # Форматируем статистику
        formatted_stats = {}
        for worker, worker_stats in stats.items():
            formatted_stats[worker] = {
                "total": worker_stats.get("total", {}),
                "load": worker_stats.get("load", {}),
                "processed": worker_stats.get("processed", 0),
                "active": worker_stats.get("active", 0),
                "scheduled": worker_stats.get("scheduled", 0),
                "reserved": worker_stats.get("reserved", 0)
            }
        
        return {"stats": formatted_stats}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting Celery stats: {str(e)}"
        )


@router.post("/revoke/{task_id}")
async def revoke_task(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """Отменяет задачу (только для админов)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return {
            "message": f"Task {task_id} revoked successfully",
            "task_id": task_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error revoking task: {str(e)}"
        )
