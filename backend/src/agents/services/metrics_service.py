import logging
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from ..models.agent_log import AgentLog
from ..models.user_agent import UserAgent
from ..models.agent import Agent

logger = logging.getLogger(__name__)


class MetricsService:
    """Сервис для сбора и анализа метрик использования агентов"""
    
    def __init__(self):
        pass
    
    async def get_agent_usage_stats(self, agent_id: int, db_session: AsyncSession) -> Dict[str, Any]:
        """Получает статистику использования агента"""
        try:
            # Общее количество запросов к агенту
            total_requests = await db_session.execute(
                select(func.count(AgentLog.id)).where(AgentLog.agent_id == agent_id)
            )
            total_requests = total_requests.scalar() or 0
            
            # Количество уникальных пользователей
            unique_users = await db_session.execute(
                select(func.count(func.distinct(AgentLog.user_id))).where(AgentLog.agent_id == agent_id)
            )
            unique_users = unique_users.scalar() or 0
            
            # Среднее время обработки
            avg_processing_time = await db_session.execute(
                select(func.avg(AgentLog.processing_time)).where(AgentLog.agent_id == agent_id)
            )
            avg_processing_time = avg_processing_time.scalar() or 0
            
            # Среднее количество используемых документов
            avg_documents_used = await db_session.execute(
                select(func.avg(AgentLog.documents_used)).where(AgentLog.agent_id == agent_id)
            )
            avg_documents_used = avg_documents_used.scalar() or 0
            
            # Статистика за последние 24 часа
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_requests = await db_session.execute(
                select(func.count(AgentLog.id)).where(
                    and_(AgentLog.agent_id == agent_id, AgentLog.created_at >= yesterday)
                )
            )
            recent_requests = recent_requests.scalar() or 0
            
            return {
                "agent_id": agent_id,
                "total_requests": total_requests,
                "unique_users": unique_users,
                "avg_processing_time": round(avg_processing_time, 2),
                "avg_documents_used": round(avg_documents_used, 2),
                "recent_requests_24h": recent_requests,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Ошибка при получении статистики агента {agent_id}: {e}")
            return {"error": str(e)}
    
    async def get_user_agent_usage_stats(self, user_id: int, db_session: AsyncSession) -> Dict[str, Any]:
        """Получает статистику использования агентов пользователем"""
        try:
            # Количество подключенных агентов
            connected_agents = await db_session.execute(
                select(func.count(UserAgent.id)).where(
                    and_(UserAgent.user_id == user_id, UserAgent.is_active == True)
                )
            )
            connected_agents = connected_agents.scalar() or 0
            
            # Общее количество запросов пользователя
            total_requests = await db_session.execute(
                select(func.count(AgentLog.id)).where(AgentLog.user_id == user_id)
            )
            total_requests = total_requests.scalar() or 0
            
            # Среднее время обработки
            avg_processing_time = await db_session.execute(
                select(func.avg(AgentLog.processing_time)).where(AgentLog.user_id == user_id)
            )
            avg_processing_time = avg_processing_time.scalar() or 0
            
            # Статистика по агентам
            agent_stats = await db_session.execute(
                select(
                    AgentLog.agent_id,
                    func.count(AgentLog.id).label('requests'),
                    func.avg(AgentLog.processing_time).label('avg_time'),
                    func.avg(AgentLog.documents_used).label('avg_docs')
                ).where(AgentLog.user_id == user_id)
                .group_by(AgentLog.agent_id)
            )
            
            agent_breakdown = []
            for row in agent_stats:
                agent_breakdown.append({
                    "agent_id": row.agent_id,
                    "requests": row.requests,
                    "avg_processing_time": round(row.avg_time or 0, 2),
                    "avg_documents_used": round(row.avg_docs or 0, 2)
                })
            
            return {
                "user_id": user_id,
                "connected_agents": connected_agents,
                "total_requests": total_requests,
                "avg_processing_time": round(avg_processing_time, 2),
                "agent_breakdown": agent_breakdown,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Ошибка при получении статистики пользователя {user_id}: {e}")
            return {"error": str(e)}
    
    async def get_system_metrics(self, db_session: AsyncSession) -> Dict[str, Any]:
        """Получает общую статистику системы"""
        try:
            # Общее количество агентов
            total_agents = await db_session.execute(
                select(func.count(Agent.id)).where(Agent.is_active == True)
            )
            total_agents = total_agents.scalar() or 0
            
            # Общее количество активных связей пользователь-агент
            active_connections = await db_session.execute(
                select(func.count(UserAgent.id)).where(UserAgent.is_active == True)
            )
            active_connections = active_connections.scalar() or 0
            
            # Общее количество запросов
            total_requests = await db_session.execute(
                select(func.count(AgentLog.id))
            )
            total_requests = total_requests.scalar() or 0
            
            # Статистика за последние 7 дней
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_requests = await db_session.execute(
                select(func.count(AgentLog.id)).where(AgentLog.created_at >= week_ago)
            )
            recent_requests = recent_requests.scalar() or 0
            
            # Топ агентов по использованию
            top_agents = await db_session.execute(
                select(
                    AgentLog.agent_id,
                    func.count(AgentLog.id).label('requests'),
                    func.avg(AgentLog.processing_time).label('avg_time')
                ).group_by(AgentLog.agent_id)
                .order_by(func.count(AgentLog.id).desc())
                .limit(5)
            )
            
            top_agents_list = []
            for row in top_agents:
                top_agents_list.append({
                    "agent_id": row.agent_id,
                    "requests": row.requests,
                    "avg_processing_time": round(row.avg_time or 0, 2)
                })
            
            return {
                "total_agents": total_agents,
                "active_connections": active_connections,
                "total_requests": total_requests,
                "recent_requests_7d": recent_requests,
                "top_agents": top_agents_list,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Ошибка при получении системной статистики: {e}")
            return {"error": str(e)}
    
    async def get_performance_metrics(self, db_session: AsyncSession) -> Dict[str, Any]:
        """Получает метрики производительности"""
        try:
            # Среднее время обработки по всем запросам
            avg_processing_time = await db_session.execute(
                select(func.avg(AgentLog.processing_time))
            )
            avg_processing_time = avg_processing_time.scalar() or 0
            
            # Медианное время обработки
            median_processing_time = await db_session.execute(
                select(func.percentile_cont(0.5).within_group(AgentLog.processing_time))
            )
            median_processing_time = median_processing_time.scalar() or 0
            
            # Количество запросов с ошибками
            error_requests = await db_session.execute(
                select(func.count(AgentLog.id)).where(AgentLog.processing_time > 30.0)  # > 30 сек считаем ошибкой
            )
            error_requests = error_requests.scalar() or 0
            
            # Общее количество запросов для расчета процента ошибок
            total_requests = await db_session.execute(
                select(func.count(AgentLog.id))
            )
            total_requests = total_requests.scalar() or 0
            
            error_rate = (error_requests / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "avg_processing_time": round(avg_processing_time, 2),
                "median_processing_time": round(median_processing_time, 2),
                "error_rate_percent": round(error_rate, 2),
                "slow_requests": error_requests,
                "total_requests": total_requests,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Ошибка при получении метрик производительности: {e}")
            return {"error": str(e)}
