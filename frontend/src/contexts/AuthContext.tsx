import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authAPI, tokenUtils, UserProfile, LoginRequest } from '../api/auth';

interface AuthContextType {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Проверяем аутентификацию при загрузке приложения
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Проверяем, есть ли токен
        if (tokenUtils.hasToken()) {
          // Пытаемся получить профиль пользователя
          await refreshProfile();
        }
      } catch (error) {
        console.error('Ошибка инициализации аутентификации:', error);
        // Если токен недействителен, очищаем его
        authAPI.logout();
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // Обновление профиля пользователя
  const refreshProfile = async () => {
    try {
      const profile = await authAPI.getProfile();
      setUser(profile);
      tokenUtils.saveProfile(profile);
    } catch (error) {
      console.error('Ошибка получения профиля:', error);
      throw error;
    }
  };

  // Вход в систему
  const login = async (credentials: LoginRequest) => {
    try {
      setIsLoading(true);
      
      // Выполняем вход
      const response = await authAPI.login(credentials);
      
      // Сохраняем токен
      tokenUtils.saveToken(response.access_token);
      
      // Получаем профиль пользователя
      await refreshProfile();
    } catch (error) {
      console.error('Ошибка входа в AuthContext:', error);
      // Перебрасываем ошибку с правильным сообщением
      if (error instanceof Error) {
        throw error;
      } else {
        throw new Error("Ошибка входа в систему");
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Выход из системы
  const logout = () => {
    authAPI.logout();
    setUser(null);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    refreshProfile,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Хук для использования контекста аутентификации
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 