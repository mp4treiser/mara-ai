// Типы для API подписок и планов
export interface PlanSchema {
  id: number;
  name: string;
  days: number;
  price: number;
  discount_percent?: number;
  description?: string;
  is_active: boolean;
}

export interface CreatePlanSchema {
  name: string;
  days: number;
  price: number;
  discount_percent?: number;
  description?: string;
}

export interface UpdatePlanSchema {
  name?: string;
  days?: number;
  price?: number;
  discount_percent?: number;
  description?: string;
  is_active?: boolean;
}

export interface SubscriptionCreate {
  plan_id: number;
  payment_method: string;
}

export interface SubscriptionResponse {
  id: number;
  user_id: number;
  plan_id: number;
  start_date: string;
  end_date: string;
  is_active: boolean;
  total_paid: number;
  created_at: string;
  updated_at: string;
}

// Базовый URL API - используем относительные пути для nginx прокси
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

  // Добавляем токен авторизации, если он есть
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
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

// API функции для планов
export const planAPI = {
  // Получение всех планов
  async getAllPlans(): Promise<PlanSchema[]> {
    return apiRequest<PlanSchema[]>('/plans/');
  },

  // Получение активных планов
  async getActivePlans(): Promise<PlanSchema[]> {
    return apiRequest<PlanSchema[]>('/plans/active');
  },

  // Получение плана по ID
  async getPlanById(planId: number): Promise<PlanSchema> {
    return apiRequest<PlanSchema>(`/plans/${planId}`);
  },

  // Создание плана (только для админов)
  async createPlan(planData: CreatePlanSchema): Promise<PlanSchema> {
    return apiRequest<PlanSchema>('/plans/', {
      method: 'POST',
      body: JSON.stringify(planData),
    });
  },

  // Обновление плана (только для админов)
  async updatePlan(planId: number, planData: UpdatePlanSchema): Promise<PlanSchema> {
    return apiRequest<PlanSchema>(`/plans/${planId}`, {
      method: 'PUT',
      body: JSON.stringify(planData),
    });
  },

  // Удаление плана (только для админов)
  async deletePlan(planId: number): Promise<void> {
    return apiRequest<void>(`/plans/${planId}`, {
      method: 'DELETE',
    });
  },

  // Деактивация плана (только для админов)
  async deactivatePlan(planId: number): Promise<PlanSchema> {
    return apiRequest<PlanSchema>(`/plans/${planId}/deactivate`, {
      method: 'PATCH',
    });
  },
};

// API функции для подписок
export const subscriptionAPI = {
  // Создание подписки
  async createSubscription(planId: number): Promise<SubscriptionResponse> {
    return apiRequest<SubscriptionResponse>('/subscriptions/', {
      method: 'POST',
      body: JSON.stringify({ plan_id: planId }),
    });
  },

  // Получение всех подписок пользователя
  async getUserSubscriptions(): Promise<SubscriptionResponse[]> {
    return apiRequest<SubscriptionResponse[]>('/subscriptions/my');
  },

  // Получение активных подписок пользователя
  async getActiveSubscriptions(): Promise<SubscriptionResponse[]> {
    return apiRequest<SubscriptionResponse[]>('/subscriptions/my/active');
  },

  // Отмена подписки
  async cancelSubscription(subscriptionId: number): Promise<void> {
    return apiRequest<void>(`/subscriptions/${subscriptionId}`, {
      method: 'DELETE',
    });
  },
};
