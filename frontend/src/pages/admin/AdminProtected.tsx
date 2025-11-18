import { Navigate, Outlet } from 'react-router-dom';
import { useEffect, useState } from 'react';

export function AdminProtected() {
  const [checking, setChecking] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    const checkAdmin = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/admin/auth/check`, {
          method: 'GET',
          credentials: 'include', // ← 管理者セッション必須
        });

        if (!res.ok) {
          setIsAdmin(false);
        } else {
          const data = await res.json();
          // data.admin === true のような形式を想定
          setIsAdmin(data.is_admin === true);
        }
      } catch (err) {
        console.error('Failed to verify admin session', err);
        setIsAdmin(false);
      } finally {
        setChecking(false);
      }
    };

    checkAdmin();
  }, []);

  // --- API確認が終わるまで待つ ---
  if (checking) {
    return <div className="p-4">Checking admin session...</div>;
  }

  // --- 管理者ではない場合 ---
  if (!isAdmin) {
    return <Navigate to="/admin/login" replace />;
  }

  // --- OK → 子ルートを表示 ---
  return <Outlet />;
}
