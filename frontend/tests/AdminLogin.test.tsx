import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AlertDialogProvider } from '@/components/common/AlertDialogProvider';
import { AdminLogin } from '@/pages/admin/AdminLogin';

const adminHook = vi.hoisted(() => ({
  isAdmin: false,
  isPending: false,
  login: vi.fn(),
}));

vi.mock('@/hooks/useAdmin', () => ({
  useCheckAdmin: () => ({ isAdmin: adminHook.isAdmin }),
  useAdminLogin: () => ({ mutate: adminHook.login, isPending: adminHook.isPending }),
}));

function renderLogin() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={['/admin/login']}>
        <AlertDialogProvider>
          <Routes>
            <Route path="/admin/login" element={<AdminLogin />} />
            <Route path="/admin/groups" element={<h1>管理グループ画面</h1>} />
          </Routes>
        </AlertDialogProvider>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

async function submitLogin() {
  const user = userEvent.setup();
  await user.type(screen.getByPlaceholderText('ユーザー名'), 'admin');
  await user.type(screen.getByPlaceholderText('パスワード'), 'secret');
  await user.click(screen.getByRole('button', { name: 'ログイン' }));
}

beforeEach(() => {
  adminHook.isAdmin = false;
  adminHook.isPending = false;
  adminHook.login.mockReset();
});

describe('管理者ログイン', () => {
  it('通常時はログインボタンを表示する', () => {
    renderLogin();
    expect(screen.getByRole('button', { name: 'ログイン' })).toBeEnabled();
  });

  it('送信中はSpinnerとログイン中表示を出し、ボタンを無効化する', () => {
    adminHook.isPending = true;
    renderLogin();
    expect(screen.getByRole('status', { name: 'Loading' })).toBeInTheDocument();
    expect(screen.getByText('ログイン中...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /ログイン中/ })).toBeDisabled();
  });

  it.each([
    [{ status: 401 }, 'ユーザー名またはパスワードを確認してください。'],
    [
      new TypeError('Failed to fetch'),
      'サーバーとの通信に失敗しました。しばらくしてから再度お試しください。',
    ],
    [
      { status: 500, body: { detail: 'internal information' } },
      'サーバーとの通信に失敗しました。しばらくしてから再度お試しください。',
    ],
  ])('ログイン失敗を安全なAlertDialogで通知する: %#', async (error, message) => {
    adminHook.login.mockImplementation((_credentials, options) => options.onError(error));
    renderLogin();
    await submitLogin();

    expect(screen.getByRole('alertdialog')).toHaveAccessibleName('ログインに失敗しました');
    expect(screen.getByText(message)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'キャンセル' })).not.toBeInTheDocument();
    expect(screen.queryByText('internal information')).not.toBeInTheDocument();
  });

  it('認証済みになった場合は既存の管理グループ画面へ遷移する', () => {
    adminHook.isAdmin = true;
    renderLogin();
    expect(screen.getByRole('heading', { name: '管理グループ画面' })).toBeInTheDocument();
  });
});
