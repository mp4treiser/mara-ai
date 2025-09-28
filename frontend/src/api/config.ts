// API конфигурация
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Таймауты для запросов
export const API_TIMEOUT = 10000; // 10 секунд

// Коды ошибок
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500,
} as const;

// Типы ошибок
export interface ApiError {
  detail: string | { error: string; message: string; [key: string]: any };
  status_code?: number;
}

// Утилиты для работы с API
export const handleApiError = (error: any): string => {
  if (error.response?.data?.detail) {
    const detail = error.response.data.detail;
    if (typeof detail === 'string') {
      return detail;
    } else if (typeof detail === 'object' && detail.message) {
      return detail.message;
    }
  }
  
  if (error.message) {
    return error.message;
  }
  
  return 'Произошла неизвестная ошибка';
};
