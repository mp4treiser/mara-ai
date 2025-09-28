// Типы для API агентов
export interface Agent {
  id: number;
  name: string;
  prompt: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  user_agent_id?: number;
  is_user_agent: boolean;
}

export interface UserAgent {
  id: number;
  user_id: number;
  agent_id: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  agent_name: string;
  agent_prompt: string;
}

export interface Document {
  id: number;
  agent_id: number;
  user_id: number;
  filename: string;
  file_type: string;
  file_size: number;
  uploaded_at: string;
  processed: boolean;
}

export interface UserAgentCreate {
  agent_id: number;
}

export interface TextAnalysisRequest {
  text: string;
}

export interface TextAnalysisResponse {
  success: boolean;
  agent_id: number;
  response: string;
  processing_time: number;
  documents_used: number;
  error_message?: string;
}

export interface AgentMetrics {
  agent_id: number;
  total_requests: number;
  unique_users: number;
  avg_processing_time: number;
  avg_documents_used: number;
  recent_requests_24h: number;
  timestamp: string;
}

export interface UserMetrics {
  user_id: number;
  connected_agents: number;
  total_requests: number;
  avg_processing_time: number;
  agent_breakdown: Array<{
    agent_id: number;
    requests: number;
    avg_processing_time: number;
    avg_documents_used: number;
  }>;
  timestamp: string;
}

export interface SystemMetrics {
  total_agents: number;
  active_connections: number;
  total_requests: number;
  recent_requests_7d: number;
  top_agents: Array<{
    agent_id: number;
    requests: number;
    avg_processing_time: number;
  }>;
  timestamp: string;
}

export interface PerformanceMetrics {
  avg_processing_time: number;
  median_processing_time: number;
  error_rate_percent: number;
  slow_requests: number;
  total_requests: number;
  timestamp: string;
}

// Базовый URL API
const API_BASE_URL = '/api/v1';

// Функция для выполнения HTTP запросов
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  // Добавляем токен авторизации
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers = {
      ...config.headers,
      'Authorization': `Bearer ${token}`,
    };
  }

  const response = await fetch(url, config);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    let errorMessage = `HTTP error! status: ${response.status}`;
    
    if (errorData.detail) {
      if (typeof errorData.detail === 'string') {
        errorMessage = errorData.detail;
      } else if (typeof errorData.detail === 'object') {
        // Извлекаем сообщение из объекта ошибки
        if (errorData.detail.message) {
          errorMessage = errorData.detail.message;
        } else if (errorData.detail.error) {
          errorMessage = errorData.detail.error;
        } else {
          errorMessage = JSON.stringify(errorData.detail);
        }
      }
    }
    
    throw new Error(errorMessage);
  }

  return response.json();
}

// API функции для агентов
export const agentsAPI = {
  // Получить список всех доступных агентов
  async getAvailableAgents(): Promise<Agent[]> {
    return apiRequest<Agent[]>('/user/agents/');
  },

  // Получить список агентов пользователя
  async getMyAgents(): Promise<UserAgent[]> {
    return apiRequest<UserAgent[]>('/user/agents/my');
  },

  // Подключиться к агенту
  async connectToAgent(agentId: number): Promise<UserAgent> {
    return apiRequest<UserAgent>('/user/agents/', {
      method: 'POST',
      body: JSON.stringify({ agent_id: agentId }),
    });
  },

  // Отключиться от агента
  async disconnectFromAgent(userAgentId: number): Promise<{ message: string }> {
    return apiRequest<{ message: string }>(`/user/agents/${userAgentId}`, {
      method: 'DELETE',
    });
  },

  // Загрузить документ для агента
  async uploadDocument(userAgentId: number, file: File): Promise<{ message: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE_URL}/user/agents/${userAgentId}/documents`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  // Анализировать текст с помощью агента
  async analyzeText(userAgentId: number, text: string): Promise<TextAnalysisResponse> {
    return apiRequest<TextAnalysisResponse>(`/user/agents/${userAgentId}/analyze`, {
      method: 'POST',
      body: JSON.stringify({ text }),
    });
  },

  // Метрики агента
  async getAgentMetrics(agentId: number): Promise<AgentMetrics> {
    return apiRequest<AgentMetrics>(`/metrics/agent/${agentId}`);
  },

  // Метрики пользователя
  async getUserMetrics(userId: number): Promise<UserMetrics> {
    return apiRequest<UserMetrics>(`/metrics/user/${userId}`);
  },

  // Мои метрики
  async getMyMetrics(): Promise<UserMetrics> {
    return apiRequest<UserMetrics>('/metrics/my');
  },

  // Системные метрики
  async getSystemMetrics(): Promise<SystemMetrics> {
    return apiRequest<SystemMetrics>('/metrics/system');
  },

  // Метрики производительности
  async getPerformanceMetrics(): Promise<PerformanceMetrics> {
    return apiRequest<PerformanceMetrics>('/metrics/performance');
  },

  // Получение списка документов агента
  async getAgentDocuments(userAgentId: number): Promise<Document[]> {
    return apiRequest<Document[]>(`/user/agents/${userAgentId}/documents`);
  },

  // Удаление отдельного документа
  async deleteDocument(documentId: number): Promise<{success: boolean, message: string}> {
    return apiRequest<{success: boolean, message: string}>(`/user/agents/documents/${documentId}`, {
      method: 'DELETE'
    });
  },

  // Очистка всех документов агента
  async clearAgentDocuments(userAgentId: number): Promise<{success: boolean, message: string}> {
    return apiRequest<{success: boolean, message: string}>(`/user/agents/${userAgentId}/documents`, {
      method: 'DELETE'
    });
  },
};
