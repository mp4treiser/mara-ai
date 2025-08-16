import React, { useState, useEffect } from 'react';
import { walletAPI, WalletResponse, WalletBalanceResponse } from '../api/wallet';

const WalletComponent: React.FC = () => {
  const [wallets, setWallets] = useState<WalletResponse[]>([]);
  const [balances, setBalances] = useState<Record<string, WalletBalanceResponse>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatingWallet, setGeneratingWallet] = useState(false);

  // Загрузка кошельков пользователя
  const loadWallets = async () => {
    try {
      setLoading(true);
      setError(null);
      const userWallets = await walletAPI.getMyWallets();
      setWallets(userWallets);
      
      // Загружаем балансы для каждого кошелька
      const balancePromises = userWallets.map(async (wallet) => {
        try {
          const balance = await walletAPI.getWalletBalance(wallet.network);
          return { [wallet.network]: balance };
        } catch (err) {
          console.error(`Failed to load balance for ${wallet.network}:`, err);
          return { [wallet.network]: null };
        }
      });
      
      const balanceResults = await Promise.all(balancePromises);
      const newBalances: Record<string, WalletBalanceResponse> = {};
      balanceResults.forEach(result => {
        Object.assign(newBalances, result);
      });
      setBalances(newBalances);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки кошельков');
    } finally {
      setLoading(false);
    }
  };

  // Генерация нового кошелька
  const generateWallet = async (network: string = 'APTOS') => {
    try {
      setGeneratingWallet(true);
      setError(null);
      
      // Проверяем, есть ли уже кошелек в этой сети
      const existingWallet = wallets.find(w => w.network === network);
      if (existingWallet) {
        setError(`Кошелек в сети ${network} уже существует`);
        return;
      }
      
      const newWallet = await walletAPI.generateWallet({ network });
      setWallets(prev => [...prev, newWallet]);
      
      // Загружаем баланс для нового кошелька
      try {
        const balance = await walletAPI.getWalletBalance(network);
        setBalances(prev => ({ ...prev, [network]: balance }));
      } catch (err) {
        console.error('Failed to load balance for new wallet:', err);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка генерации кошелька');
    } finally {
      setGeneratingWallet(false);
    }
  };

  // Обновление баланса
  const refreshBalance = async (network: string) => {
    try {
      const balance = await walletAPI.getWalletBalance(network);
      setBalances(prev => ({ ...prev, [network]: balance }));
    } catch (err) {
      console.error(`Failed to refresh balance for ${network}:`, err);
    }
  };

  useEffect(() => {
    loadWallets();
  }, []);

  if (loading && wallets.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '20px' }}>
        <div>Загрузка кошельков...</div>
      </div>
    );
  }

  return (
    <div style={{ 
      width: '100%', 
      maxWidth: 800, 
      background: '#fff', 
      padding: 24, 
      borderRadius: 12, 
      boxShadow: '0 2px 16px rgba(0,0,0,0.07)' 
    }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: 24 
      }}>
        <h2 style={{ color: '#2d3748', margin: 0 }}>Кошелек</h2>
        <button
          onClick={() => generateWallet('APTOS')}
          disabled={generatingWallet || wallets.some(w => w.network === 'APTOS')}
          style={{
            background: wallets.some(w => w.network === 'APTOS') ? '#a0aec0' : '#3182ce',
            color: '#fff',
            border: 'none',
            borderRadius: 6,
            padding: '10px 20px',
            fontSize: 14,
            fontWeight: 500,
            cursor: wallets.some(w => w.network === 'APTOS') ? 'not-allowed' : 'pointer',
            transition: 'background 0.2s',
            opacity: wallets.some(w => w.network === 'APTOS') ? 0.6 : 1
          }}
        >
          {generatingWallet ? 'Генерация...' : 'Создать APTOS кошелек'}
        </button>
      </div>

      {error && (
        <div style={{ 
          marginBottom: 16, 
          padding: 12, 
          background: '#fed7d7', 
          borderRadius: 6, 
          border: '1px solid #feb2b2',
          color: '#c53030'
        }}>
          {error}
        </div>
      )}

      {wallets.length === 0 ? (
        <div style={{ 
          textAlign: 'center', 
          padding: 40, 
          color: '#718096',
          background: '#f7fafc',
          borderRadius: 8,
          border: '2px dashed #e2e8f0'
        }}>
          <div style={{ fontSize: 18, marginBottom: 8 }}>Кошельки не найдены</div>
          <div style={{ fontSize: 14 }}>Создайте кошелек в сети APTOS для начала работы</div>
        </div>
      ) : (
        <div>
          {wallets.map((wallet) => (
            <div key={wallet.id} style={{ 
              marginBottom: 20, 
              padding: 20, 
              background: '#f7fafc', 
              borderRadius: 8, 
              border: '1px solid #e2e8f0' 
            }}>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center', 
                marginBottom: 16 
              }}>
                <div>
                  <h3 style={{ margin: '0 0 8px 0', color: '#2d3748' }}>
                    Кошелек {wallet.network}
                  </h3>
                  <div style={{ 
                    fontSize: 12, 
                    color: '#718096', 
                    fontFamily: 'monospace',
                    background: '#edf2f7',
                    padding: '4px 8px',
                    borderRadius: 4,
                    wordBreak: 'break-all'
                  }}>
                    {wallet.address}
                  </div>
                </div>
                <button
                  onClick={() => refreshBalance(wallet.network)}
                  style={{
                    background: '#38a169',
                    color: '#fff',
                    border: 'none',
                    borderRadius: 4,
                    padding: '6px 12px',
                    fontSize: 12,
                    cursor: 'pointer',
                    transition: 'background 0.2s'
                  }}
                >
                  Обновить
                </button>
              </div>

              {balances[wallet.network] ? (
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: '1fr 1fr', 
                  gap: 16 
                }}>
                  <div style={{ 
                    padding: 12, 
                    background: '#fff', 
                    borderRadius: 6, 
                    border: '1px solid #e2e8f0' 
                  }}>
                    <div style={{ fontSize: 12, color: '#718096', marginBottom: 4 }}>
                      USDT Баланс
                    </div>
                    <div style={{ fontSize: 18, fontWeight: 600, color: '#2d3748' }}>
                      {balances[wallet.network].usdt_balance.toFixed(6)}
                    </div>
                  </div>
                  <div style={{ 
                    padding: 12, 
                    background: '#fff', 
                    borderRadius: 6, 
                    border: '1px solid #e2e8f0' 
                  }}>
                    <div style={{ fontSize: 12, color: '#718096', marginBottom: 4 }}>
                      USD Эквивалент
                    </div>
                    <div style={{ fontSize: 18, fontWeight: 600, color: '#2d3748' }}>
                      ${balances[wallet.network].usd_equivalent.toFixed(2)}
                    </div>
                  </div>
                </div>
              ) : (
                <div style={{ 
                  padding: 12, 
                  background: '#fff', 
                  borderRadius: 6, 
                  border: '1px solid #e2e8f0',
                  textAlign: 'center',
                  color: '#718096'
                }}>
                  Баланс не загружен
                </div>
              )}

              <div style={{ 
                marginTop: 12, 
                fontSize: 12, 
                color: '#718096' 
              }}>
                Создан: {new Date(wallet.created_at).toLocaleDateString('ru-RU')}
                {wallet.last_checked && (
                  <span style={{ marginLeft: 16 }}>
                    Последняя проверка: {new Date(wallet.last_checked).toLocaleDateString('ru-RU')}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default WalletComponent;
