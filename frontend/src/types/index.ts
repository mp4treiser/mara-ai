// Общие типы для приложения

export interface User {
  id: number;
  email: string;
  company: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
