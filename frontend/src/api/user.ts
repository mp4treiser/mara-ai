import { API_BASE_URL } from './config';

export interface UserBalanceResponse {
  balance: number;
  currency: string;
  user_id: number;
}

export interface UserProfileResponse {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  company: string;
  is_active: boolean;
  balance: number;
  is_superuser: boolean;
}

export interface UpdateProfileRequest {
  first_name?: string;
  last_name?: string;
  company?: string;
}

class UserAPI {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }

  async getUserBalance(): Promise<UserBalanceResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/user/balance`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to get user balance: ${response.statusText}`);
    }

    return response.json();
  }

  async getUserProfile(): Promise<UserProfileResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/user/me/profile`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to get user profile: ${response.statusText}`);
    }

    return response.json();
  }

  async updateUserProfile(profileData: UpdateProfileRequest): Promise<UserProfileResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/user/profile`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(profileData),
    });

    if (!response.ok) {
      throw new Error(`Failed to update user profile: ${response.statusText}`);
    }

    return response.json();
  }
}

export const userAPI = new UserAPI();
