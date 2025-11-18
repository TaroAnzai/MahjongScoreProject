import { Navigate, Outlet } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useCheckAdmin } from '@/hooks/useAdmin';

export function AdminProtected() {
  const { isAdmin, isLoading } = useCheckAdmin();

  // --- API確認が終わるまで待つ ---
  if (isLoading) {
    return <div className="p-4">Checking admin session...</div>;
  }
  console.log('AdminProtected', isAdmin);
  // --- 管理者ではない場合 ---
  if (!isAdmin || isAdmin.is_admin === false) {
    return <Navigate to="/admin/login" replace />;
  }
  console.log('AdminProtected OK');
  // --- OK → 子ルートを表示 ---
  return <Outlet />;
}
