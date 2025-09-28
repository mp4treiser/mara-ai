import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import threading
import hashlib
import time
from functools import lru_cache

logger = logging.getLogger(__name__)


class VectorStore:
    """Сервис для работы с векторной БД ChromaDB"""
    
    _instance = None
    _lock = threading.Lock()
    _clients = {}  # Кэш клиентов по путям
    _search_cache = {}  # Кэш результатов поиска
    _cache_ttl = 300  # TTL кэша в секундах (5 минут)
    
    def __new__(cls, base_path: str = "docs"):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(VectorStore, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, base_path: str = "docs"):
        if not hasattr(self, 'initialized'):
            self.base_path = Path(base_path)
            self.base_path.mkdir(exist_ok=True)
            self.initialized = True
        
    def get_agent_vector_path(self, user_id: int, agent_id: int) -> Path:
        """Получает путь к векторной БД для конкретного агента"""
        return self.base_path / str(user_id) / str(agent_id) / "vector_store"
    
    def _get_client(self, vector_path: Path):
        """Получает или создает клиент ChromaDB для конкретного пути"""
        path_str = str(vector_path)
        
        if path_str not in self._clients:
            try:
                import chromadb
                client = chromadb.PersistentClient(path=path_str)
                self._clients[path_str] = client
                logger.info(f"Создан новый клиент ChromaDB для пути: {path_str}")
            except Exception as e:
                logger.error(f"Ошибка при создании клиента ChromaDB: {e}")
                raise
        
        return self._clients[path_str]
    
    def _get_collection(self, user_id: int, agent_id: int):
        """Получает коллекцию для агента"""
        vector_path = self.get_agent_vector_path(user_id, agent_id)
        
        # Создаем директорию если не существует
        vector_path.mkdir(parents=True, exist_ok=True)
        
        client = self._get_client(vector_path)
        collection_name = f"agent_{agent_id}_docs"
        
        logger.info(f"Получаем коллекцию {collection_name} для агента {agent_id}")
        
        try:
            collection = client.get_collection(name=collection_name)
            logger.info(f"Коллекция {collection_name} найдена, количество документов: {collection.count()}")
            return collection
        except Exception as e:
            logger.warning(f"Коллекция {collection_name} не найдена, создаем новую: {e}")
            # Если коллекция не существует, создаем её
            collection = client.get_or_create_collection(
                name=collection_name,
                metadata={"description": f"Documents for agent {agent_id}"}
            )
            logger.info(f"Создана новая коллекция {collection_name}")
            return collection
    
    def _get_cache_key(self, user_id: int, agent_id: int, query: str, n_results: int) -> str:
        """Генерирует ключ для кэша поиска"""
        cache_data = f"{user_id}_{agent_id}_{query}_{n_results}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Получает результат из кэша если он еще актуален"""
        if cache_key in self._search_cache:
            result, timestamp = self._search_cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                logger.debug(f"Результат найден в кэше для ключа: {cache_key}")
                return result
            else:
                # Удаляем устаревший результат
                del self._search_cache[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, result: List[Dict[str, Any]]):
        """Сохраняет результат в кэш"""
        self._search_cache[cache_key] = (result, time.time())
        logger.debug(f"Результат сохранен в кэш для ключа: {cache_key}")
    
    def clear_cache(self):
        """Очищает кэш поиска"""
        self._search_cache.clear()
        logger.info("Кэш поиска очищен")
    
    def create_agent_collection(self, user_id: int, agent_id: int) -> str:
        """Создает коллекцию для агента в ChromaDB"""
        try:
            import chromadb
            vector_path = self.get_agent_vector_path(user_id, agent_id)
            vector_path.mkdir(parents=True, exist_ok=True)
            
            # Создаем клиент ChromaDB
            client = chromadb.PersistentClient(path=str(vector_path))
            collection_name = f"agent_{agent_id}_docs"
            
            # Создаем или получаем коллекцию
            collection = client.get_or_create_collection(
                name=collection_name,
                metadata={"description": f"Documents for agent {agent_id}"}
            )
            
            logger.info(f"Создана коллекция {collection_name} для агента {agent_id}")
            return collection_name
            
        except ImportError:
            logger.error("ChromaDB не установлен")
            raise
        except Exception as e:
            logger.error(f"Ошибка при создании коллекции для агента {agent_id}: {e}")
            raise
    
    def add_documents(self, user_id: int, agent_id: int, documents: List[Dict[str, Any]]) -> bool:
        """Добавляет документы в векторную БД агента"""
        try:
            # Получаем коллекцию (создается автоматически если не существует)
            collection = self._get_collection(user_id, agent_id)
            
            # Подготавливаем данные для добавления
            texts = []
            metadatas = []
            ids = []
            
            for i, doc in enumerate(documents):
                texts.append(doc['text'])
                metadatas.append({
                    'filename': doc['filename'],
                    'file_type': doc['file_type'],
                    'uploaded_at': str(doc['uploaded_at'])
                })
                ids.append(f"doc_{doc['id']}_{i}")
            
            # Добавляем документы в коллекцию
            collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Добавлено {len(documents)} документов в коллекцию agent_{agent_id}_docs")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при добавлении документов в векторную БД: {e}")
            return False
    
    def search_similar(self, user_id: int, agent_id: int, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Ищет похожие документы по запросу"""
        try:
            # Проверяем кэш
            cache_key = self._get_cache_key(user_id, agent_id, query, n_results)
            cached_result = self._get_cached_result(cache_key)
            if cached_result is not None:
                return cached_result
            
            vector_path = self.get_agent_vector_path(user_id, agent_id)
            logger.info(f"Ищем векторную БД по пути: {vector_path}")
            logger.info(f"Путь существует: {vector_path.exists()}")
            
            if not vector_path.exists():
                logger.warning(f"Векторная БД для агента {agent_id} не найдена по пути: {vector_path}")
                return []
            
            # Получаем коллекцию (создается автоматически если не существует)
            collection = self._get_collection(user_id, agent_id)
            
            # Сначала пробуем точный поиск по названию алерта
            exact_results = self._search_exact_alert(collection, query)
            if exact_results:
                logger.info(f"Найден точный алерт: {exact_results[0].get('text', '')[:100]}...")
                self._cache_result(cache_key, exact_results)
                return exact_results
            
            # Если точный поиск не дал результатов, ищем по смыслу
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Форматируем результаты и приоритизируем первую строку
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    doc_text = results['documents'][0][i]
                    first_line = self._get_first_line(doc_text)
                    
                    # Проверяем, есть ли совпадение в первой строке
                    has_first_line_match = False
                    if first_line:
                        # Извлекаем ключевые слова из запроса
                        query_keywords = self._extract_keywords_from_alert(query)
                        for keyword in query_keywords:
                            if keyword.lower() in first_line.lower():
                                has_first_line_match = True
                                break
                    
                    formatted_results.append({
                        'text': doc_text,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0.0,
                        'first_line': first_line,
                        'has_first_line_match': has_first_line_match
                    })
                
                # Сортируем результаты: сначала те, где есть совпадение в первой строке
                formatted_results.sort(key=lambda x: (not x['has_first_line_match'], x['distance']))
            
            # Сохраняем результат в кэш
            self._cache_result(cache_key, formatted_results)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Ошибка при поиске похожих документов: {e}")
            return []
    
    def _search_exact_alert(self, collection, query: str) -> List[Dict[str, Any]]:
        """Умный поиск алертов - извлекает все алерты из текста и ищет точные совпадения в первой строке"""
        try:
            # Извлекаем все возможные алерты из запроса
            alerts = self._extract_alerts_from_text(query)
            logger.info(f"Найдено алертов в тексте: {alerts}")
            
            if not alerts:
                return []
            
            # Получаем все документы из коллекции
            all_docs = collection.get()
            
            if not all_docs or not all_docs.get('documents'):
                return []
            
            # Ищем точные совпадения для каждого алерта, приоритизируя первую строку
            for alert in alerts:
                for i, doc_text in enumerate(all_docs['documents']):
                    # Сначала проверяем первую строку документа
                    first_line = self._get_first_line(doc_text)
                    if first_line and self._is_exact_match(alert, first_line):
                        logger.info(f"Найдено точное совпадение в первой строке для '{alert}': {first_line}")
                        return [{
                            'text': doc_text,
                            'metadata': {
                                'filename': all_docs['metadatas'][i].get('filename', 'unknown') if all_docs.get('metadatas') else 'unknown',
                                'file_type': all_docs['metadatas'][i].get('file_type', 'unknown') if all_docs.get('metadatas') else 'unknown',
                                'uploaded_at': all_docs['metadatas'][i].get('uploaded_at', 'unknown') if all_docs.get('metadatas') else 'unknown',
                                'match_type': 'first_line'
                            }
                        }]
            
            # Если в первой строке не найдено, ищем в остальном тексте
            for alert in alerts:
                for i, doc_text in enumerate(all_docs['documents']):
                    if self._is_exact_match(alert, doc_text):
                        logger.info(f"Найдено точное совпадение в тексте для '{alert}': {doc_text[:200]}...")
                        return [{
                            'text': doc_text,
                            'metadata': {
                                'filename': all_docs['metadatas'][i].get('filename', 'unknown') if all_docs.get('metadatas') else 'unknown',
                                'file_type': all_docs['metadatas'][i].get('file_type', 'unknown') if all_docs.get('metadatas') else 'unknown',
                                'uploaded_at': all_docs['metadatas'][i].get('uploaded_at', 'unknown') if all_docs.get('metadatas') else 'unknown',
                                'match_type': 'full_text'
                            }
                        }]
            
            return []
            
        except Exception as e:
            logger.error(f"Ошибка при точном поиске алерта: {e}")
            return []
    
    def _extract_alerts_from_text(self, text: str) -> List[str]:
        """Извлекает все алерты из текста пользователя"""
        import re
        alerts = []
        
        # Паттерны для разных типов алертов
        patterns = [
            r'\[Alerting\]\s+([^\n]+?)(?:\s+alert)?',  # [Alerting] Memory OpenApi IS/CS alert
            r'z\d+[a-z]?\s+([^\n]+?)(?:\s+alert)?',    # z735 Инвалидные пакеты в MTBDM
            r'c\d+[a-z]?\s+([^\n]+?)(?:\s+alert)?',    # c217 <10% свободного места
            r'[A-Z]\d+[a-z]?\s+([^\n]+?)(?:\s+alert)?', # C214. Не работает MTBank Moby
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                alert_name = match.strip()
                if alert_name and len(alert_name) > 3:  # Фильтруем слишком короткие совпадения
                    alerts.append(alert_name)
        
        # Дополнительно извлекаем ключевые слова из алерта
        alert_keywords = self._extract_keywords_from_alert(text)
        alerts.extend(alert_keywords)
        
        # Убираем дубликаты
        return list(set(alerts))
    
    def _extract_keywords_from_alert(self, text: str) -> List[str]:
        """Извлекает ключевые слова из алерта для улучшенного поиска"""
        import re
        keywords = []
        
        # Извлекаем название алерта из [Alerting] блока
        alerting_match = re.search(r'\[Alerting\]\s+([^\n]+?)(?:\s+alert)?', text, re.IGNORECASE)
        if alerting_match:
            alert_name = alerting_match.group(1).strip()
            keywords.append(alert_name)
            
            # Разбиваем название на отдельные слова
            words = re.findall(r'\b\w+\b', alert_name.lower())
            keywords.extend([w for w in words if len(w) > 2])
        
        # Извлекаем коды алертов
        code_matches = re.findall(r'\b[zZcC]\d+[a-z]?\b', text)
        keywords.extend(code_matches)
        
        # Извлекаем метрики
        metrics_match = re.search(r'Metrics?:\s*([^\n]+)', text, re.IGNORECASE)
        if metrics_match:
            metrics = metrics_match.group(1).strip()
            keywords.append(metrics)
            
            # Разбиваем метрики на части
            metric_parts = re.findall(r'\b\w+\b', metrics.lower())
            keywords.extend([p for p in metric_parts if len(p) > 2])
        
        # Убираем дубликаты и пустые строки
        return list(set([k.strip() for k in keywords if k.strip() and len(k.strip()) > 1]))
    
    def _get_first_line(self, text: str) -> str:
        """Извлекает первую строку из текста документа"""
        if not text:
            return ""
        
        # Разбиваем на строки и берем первую непустую
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line:  # Первая непустая строка
                return line
        
        return ""
    
    def _is_exact_match(self, alert: str, table_row: str) -> bool:
        """Проверяет точное совпадение алерта в строке таблицы"""
        # Нормализуем строки для сравнения
        alert_normalized = alert.lower().strip()
        row_normalized = table_row.lower().strip()
        
        # Проверяем различные варианты совпадения
        if alert_normalized in row_normalized:
            return True
        
        # Для алертов типа z735 проверяем по номеру
        if alert_normalized.startswith('z') and alert_normalized[1:].isdigit():
            alert_number = alert_normalized
            if alert_number in row_normalized:
                return True
        
        # Для алертов типа [Alerting] проверяем по названию
        if alert_normalized.startswith('[') and 'alerting' in alert_normalized:
            # Извлекаем название без [Alerting] и alert
            name_part = alert_normalized.replace('[alerting]', '').replace('alert', '').strip()
            if name_part and name_part in row_normalized:
                return True
        
        return False
    
    def delete_agent_collection(self, user_id: int, agent_id: int) -> bool:
        """Удаляет коллекцию агента"""
        try:
            vector_path = self.get_agent_vector_path(user_id, agent_id)
            if vector_path.exists():
                import shutil
                shutil.rmtree(vector_path)
                logger.info(f"Удалена векторная БД для агента {agent_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка при удалении векторной БД агента {agent_id}: {e}")
            return False
