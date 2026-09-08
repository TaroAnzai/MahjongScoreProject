import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { expect, it, vi } from 'vitest';
import { AdminProtected } from '@/pages/admin/AdminProtected';
import { useCheckAdmin } from '@/hooks/useAdmin';

vi.mock('@/hooks/useAdmin', () => ({ useCheckAdmin: vi.fn() }));

it.each([
  { isLoading: true, isAdmin: undefined, expected: 'Checking admin session...' },
  { isLoading: false, isAdmin: false, expected: 'ログイン画面' },
  { isLoading: false, isAdmin: undefined, expected: 'ログイン画面' },
  { isLoading: false, isAdmin: true, expected: '管理データ' },
])('セッション状態に応じて表示を制御する: $expected', ({ isLoading, isAdmin, expected }) => {
  vi.mocked(useCheckAdmin).mockReturnValue({ isLoading, isAdmin, refetch: vi.fn() });
  render(<MemoryRouter initialEntries={['/admin/groups']}>
    <Routes>
      <Route path="/admin/login" element={<div>ログイン画面</div>} />
      <Route element={<AdminProtected />}>
        <Route path="/admin/groups" element={<div>管理データ</div>} />
      </Route>
    </Routes>
  </MemoryRouter>);
  expect(screen.getByText(expected)).toBeInTheDocument();
  if (!isAdmin) expect(screen.queryByText('管理データ')).not.toBeInTheDocument();
});
