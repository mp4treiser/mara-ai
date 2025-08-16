// Типы для API
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserProfile {
  id: number;
  email: string;
  company: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
}

export interface RegisterRequest {
  email: string;
  password: string;
  confirm_password: string;
  company: string;
  first_name: string;
  last_name: string;
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

// API функции для аутентификации
export const authAPI = {
  // Вход в систему
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    return apiRequest<LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  },

  // Регистрация
  async register(userData: RegisterRequest): Promise<UserProfile> {
    return apiRequest<UserProfile>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  // Получение профиля пользователя
  async getProfile(): Promise<UserProfile> {
    return apiRequest<UserProfile>('/user/me/profile');
  },

  // Выход из системы
  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_profile');
  },
};

// Утилиты для работы с токенами
export const tokenUtils = {
  // Сохранение токена
  saveToken(token: string): void {
    localStorage.setItem('access_token', token);
  },

  // Получение токена
  getToken(): string | null {
    return localStorage.getItem('access_token');
  },

  // Проверка наличия токена
  hasToken(): boolean {
    return !!this.getToken();
  },

  // Сохранение профиля пользователя
  saveProfile(profile: UserProfile): void {
    localStorage.setItem('user_profile', JSON.stringify(profile));
  },

  // Получение профиля пользователя
  getProfile(): UserProfile | null {
    const profile = localStorage.getItem('user_profile');
    return profile ? JSON.parse(profile) : null;
  },
}; 