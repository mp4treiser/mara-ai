import logging
import os
from typing import List, Dict, Any, Optional
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


class OllamaService:
    """Сервис для работы с Ollama моделью"""
    
    def __init__(self, model_name: str = "llama3.2:3b", base_url: str = None):
        self.model_name = model_name
        
        # Используем переменные окружения или значения по умолчанию
        if base_url is None:
            ollama_host = os.getenv("OLLAMA_HOST", "localhost")
            ollama_port = os.getenv("OLLAMA_PORT", "11434")
            self.base_url = f"http://{ollama_host}:{ollama_port}"
        else:
            self.base_url = base_url
            
        self.llm = None
        logger.info(f"Инициализация OllamaService с URL: {self.base_url}")
        self._initialize_model()
    
    def _initialize_model(self):
        """Инициализирует модель Ollama"""
        try:
            self.llm = OllamaLLM(
                model=self.model_name,
                base_url=self.base_url,
                temperature=0.05,  # Очень низкая температура для максимально точных ответов
                timeout=60,  # Таймаут 1 минута
                top_p=0.9,  # Ограничиваем выбор токенов
                top_k=40,   # Ограничиваем количество кандидатов
                repeat_penalty=1.1  # Штраф за повторения
            )
            logger.info(f"Модель Ollama {self.model_name} инициализирована по адресу {self.base_url}")
        except Exception as e:
            logger.error(f"Ошибка при инициализации модели Ollama: {e}")
            self.llm = None
            raise
    
    def generate_response(self, prompt: str, context: str = "", user_text: str = "") -> str:
        """Генерирует ответ на основе промпта, контекста и пользовательского текста"""
        try:
            if not self.llm:
                self._initialize_model()
            
            # Валидация входных параметров
            if not prompt or not prompt.strip():
                raise ValueError("Промпт не может быть пустым")
            
            # Проверяем, есть ли контекст
            if not context or not context.strip():
                logger.warning("Контекст документации пустой")
                return "Алерт не найден в документации"
            
            # Формируем полный промпт
            full_prompt = self._build_prompt(prompt, context, user_text)
            logger.info(f"Full prompt length: {len(full_prompt)} characters")
            logger.info(f"Full prompt preview: {full_prompt[:1000]}...")
            
            # Генерируем ответ
            response = self.llm.invoke(full_prompt)
            
            # Валидация и обработка ответа
            if not response or not response.strip():
                logger.warning("Получен пустой ответ от модели")
                return "Извините, не удалось сгенерировать ответ. Попробуйте переформулировать вопрос."
            
            # Очищаем и форматируем ответ
            cleaned_response = self._clean_response(response.strip())
            
            logger.info(f"Сгенерирован ответ для модели {self.model_name}: {cleaned_response[:100]}...")
            return cleaned_response
            
        except Exception as e:
            logger.error(f"Ошибка при генерации ответа: {e}")
            # Возвращаем информативное сообщение об ошибке вместо исключения
            return f"Произошла ошибка при обработке запроса: {str(e)}"
    
    def _build_prompt(self, prompt: str, context: str = "", user_text: str = "") -> str:
        """Строит полный промпт для модели"""
        # Извлекаем ключевые слова из алерта
        alert_keywords = self._extract_alert_keywords(user_text)
        
        print(f"""{prompt}

        Документация:
        {context}

        НАИМЕНОВАНИЕ АЛЕРТА ДЛЯ ПОИСКА: {', '.join(alert_keywords)}

        ИНСТРУКЦИЯ:
        1. Найди в "Документации" раздел, соответствующий наименованию алерта.
        2. Если найден - скопируй ТОЛЬКО текст из поля "Как реагировать".
        3. Если не найден - ответь строго "Алерт не найден в документации".

        ФОРМАТ ОТВЕТА:
        - Найден: [Текст из документации]
        - Не найден: Алерт не найден в документации

        ЗАПРЕЩЕНО:
        - Добавлять слова "Анализ", "Поиск", "Результат" и т.п.
        - Объяснять свои действия.
        - Менять или перефразировать текст из документации.
        - Отвечать что-либо, кроме текста из документации или строгой фразы "Алерт не найден в документации".

        ОТВЕТ:""")

        return f"""{prompt}

        Документация:
        {context}

        НАИМЕНОВАНИЕ АЛЕРТА ДЛЯ ПОИСКА: {', '.join(alert_keywords)}

        ИНСТРУКЦИЯ:
        1. Найди в "Документации" раздел, соответствующий наименованию алерта.
        2. Если найден - скопируй ТОЛЬКО текст из поля "Как реагировать".
        3. Если не найден - ответь строго "Алерт не найден в документации".

        ФОРМАТ ОТВЕТА:
        - Найден: [Текст из документации]
        - Не найден: Алерт не найден в документации

        ЗАПРЕЩЕНО:
        - Добавлять слова "Анализ", "Поиск", "Результат" и т.п.
        - Объяснять свои действия.
        - Менять или перефразировать текст из документации.
        - Отвечать что-либо, кроме текста из документации или строгой фразы "Алерт не найден в документации".

        ОТВЕТ:"""
    
    def _extract_alert_keywords(self, user_text: str) -> List[str]:
        """Извлекает ключевые слова из текста алерта"""
        import re
        
        keywords = []
        
        # Извлекаем название алерта из [Alerting] блока
        alerting_match = re.search(r'\[Alerting\](.+?)alert', user_text, re.IGNORECASE)
        if alerting_match:
            alert_name = alerting_match.group(1).strip()
            print(alert_name)
            keywords.append(alert_name)

        logger.info(f"Извлечены ключевые слова из алерта: {keywords}")
        return keywords
    
    def _clean_response(self, response: str) -> str:
        """Очищает и форматирует ответ модели"""
        import re
        
        # Убираем лишние пробелы и переносы строк
        response = re.sub(r'\s+', ' ', response.strip())
        
        # Убираем повторяющиеся фразы
        response = re.sub(r'(.+?)\1+', r'\1', response)
        
        # Если ответ начинается с "Ответ:" или подобного, убираем это
        response = re.sub(r'^(Ответ|Response|Результат|По документаци|Найден алерт):\s*', '', response, flags=re.IGNORECASE)
        
        # Убираем типичные фразы-повторения
        response = re.sub(r'^.*?найден алерт.*?:\s*', '', response, flags=re.IGNORECASE)
        response = re.sub(r'^.*?соответствует.*?:\s*', '', response, flags=re.IGNORECASE)
        response = re.sub(r'^.*?правильный ответ.*?:\s*', '', response, flags=re.IGNORECASE)
        response = re.sub(r'^.*?окончательный ответ.*?:\s*', '', response, flags=re.IGNORECASE)
        
        # Если ответ содержит только повторение входного текста, возвращаем fallback
        if len(response) < 10 or response.lower() in ['да', 'нет', 'ok', 'хорошо']:
            return "Алерт не найден в документации"
        
        # Проверяем, не является ли ответ просто повторением входного текста
        if self._is_response_repetition(response):
            return "Алерт не найден в документации"
        
        # Проверяем на типичные паттерны повторения
        if self._is_typical_repetition(response):
            return "Алерт не найден в документации"
        
        return response
    
    def _is_response_repetition(self, response: str) -> bool:
        """Проверяет, не является ли ответ простым повторением входного текста"""
        # Простая эвристика: если ответ содержит много повторяющихся слов
        words = response.lower().split()
        if len(words) < 3:
            return True
        
        # Проверяем на повторение фраз
        word_counts = {}
        for word in words:
            if len(word) > 3:  # Игнорируем короткие слова
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Если какое-то слово повторяется слишком часто
        max_repetitions = max(word_counts.values()) if word_counts else 0
        if max_repetitions > len(words) * 0.3:  # Более 30% повторений
            return True
        
        return False
    
    def _is_typical_repetition(self, response: str) -> bool:
        """Проверяет типичные паттерны повторения в ответе"""
        response_lower = response.lower()
        
        # Проверяем на типичные фразы, которые указывают на повторение
        repetition_patterns = [
            r'\[alerting\].*?alert.*?\[alerting\].*?alert',  # Повторение [Alerting] ... alert
            r'найден алерт.*?найден алерт',  # Повторение "найден алерт"
            r'соответствует.*?соответствует',  # Повторение "соответствует"
            r'правильный ответ.*?правильный ответ',  # Повторение "правильный ответ"
            r'окончательный ответ.*?окончательный ответ',  # Повторение "окончательный ответ"
            r'ключевые слова.*?ключевые слова',  # Повторение "ключевые слова"
        ]
        
        import re
        for pattern in repetition_patterns:
            if re.search(pattern, response_lower):
                logger.info(f"Обнаружен паттерн повторения: {pattern}")
                return True
        
        # Проверяем, если ответ заканчивается точкой и содержит только название алерта
        if response_lower.endswith('.') and len(response.split()) <= 5:
            # Если это короткий ответ, который заканчивается точкой, возможно это повторение
            if any(word in response_lower for word in ['alerting', 'alert', 'moby', 'auth']):
                logger.info("Обнаружен короткий ответ с ключевыми словами алерта")
                return True
        
        return False
    
    def test_connection(self) -> bool:
        """Тестирует подключение к Ollama"""
        try:
            if not self.llm:
                self._initialize_model()
            
            # Простой тест
            test_response = self.llm.invoke("Ответь 'OK' если ты работаешь")
            return "OK" in test_response.upper()
            
        except Exception as e:
            logger.error(f"Ошибка при тестировании подключения к Ollama: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Получает информацию о модели"""
        try:
            return {
                "model_name": self.model_name,
                "base_url": self.base_url,
                "status": "connected" if self.llm else "disconnected"
            }
        except Exception as e:
            logger.error(f"Ошибка при получении информации о модели: {e}")
            return {
                "model_name": self.model_name,
                "base_url": self.base_url,
                "status": "error"
            }
