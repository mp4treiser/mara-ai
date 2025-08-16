// Типы для API кошельков
export interface WalletResponse {
  id: number;
  user_id: number;
  address: string;
  network: string;
  is_active: boolean;
  created_at: string;
  last_checked?: string;
}

export interface WalletCreate {
  network: string;
}

export interface WalletBalanceResponse {
  wallet_address: string;
  network: string;
  usdt_balance: number;
  usd_equivalent: number;
  last_updated: string;
}

export interface WalletDepositResponse {
  id: number;
  wallet_id: number;
  transaction_hash: string;
  amount: number;
  usd_amount: number;
  status: string;
  block_number?: number;
  created_at: string;
  processed_at?: string;
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

// API функции для кошельков
export const walletAPI = {
  // Генерация нового кошелька
  async generateWallet(walletData: WalletCreate): Promise<WalletResponse> {
    return apiRequest<WalletResponse>('/wallets/generate', {
      method: 'POST',
      body: JSON.stringify(walletData),
    });
  },

  // Получение всех кошельков пользователя
  async getMyWallets(): Promise<WalletResponse[]> {
    return apiRequest<WalletResponse[]>('/wallets/my');
  },

  // Получение кошелька по сети
  async getWalletByNetwork(network: string): Promise<WalletResponse> {
    return apiRequest<WalletResponse>(`/wallets/my/${network}`);
  },

  // Получение баланса кошелька
  async getWalletBalance(network: string): Promise<WalletBalanceResponse> {
    return apiRequest<WalletBalanceResponse>(`/wallets/my/${network}/balance`);
  },
};
