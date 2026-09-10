import { appButtonVariants, containerVariants } from '@/components/ui/mahjong';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Spinner } from '@/components/ui/spinner';
import { useAlertDialog } from '@/components/common/AlertDialogProvider';
import { useAdminLogin, useCheckAdmin } from '@/hooks/useAdmin';
import { Eye, EyeOff } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

export function AdminLogin() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [show, setShow] = useState(false);
  const { alertDialog } = useAlertDialog();
  const { mutate: login, isPending } = useAdminLogin();
  const { isAdmin } = useCheckAdmin();

  useEffect(() => {
    if (isAdmin) {
      navigate('/admin/groups');
    }
  }, [isAdmin]);
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isPending) return;

    login(
      { username, password },
      {
        onError: (error) => {
          const isAuthenticationError =
            typeof error === 'object' &&
            error !== null &&
            'status' in error &&
            error.status === 401;

          void alertDialog({
            title: 'ログインに失敗しました',
            description: isAuthenticationError
              ? 'ユーザー名またはパスワードを確認してください。'
              : 'サーバーとの通信に失敗しました。しばらくしてから再度お試しください。',
            showCancelButton: false,
          });
        },
      }
    );
  };
  return (
    <div className={containerVariants()}>
      <h2 className="mb-5">AdminLogin</h2>
      <form className="flex flex-col gap-3" onSubmit={handleSubmit}>
        <Input
          type="text"
          placeholder="ユーザー名"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <div className="relative">
          <Input
            type={show ? 'text' : 'password'}
            placeholder="パスワード"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="pr-10"
          />

          <Button
            type="button"
            onClick={() => setShow(!show)}
            variant="ghost"
            size="icon"
            className="absolute right-2 top-1/2 -translate-y-1/2"
          >
            {show ? <EyeOff size={18} /> : <Eye size={18} />}
          </Button>
        </div>
        <button className={appButtonVariants()} type="submit" disabled={isPending}>
          {isPending ? (
            <span className="flex items-center justify-center gap-2">
              <Spinner />
              ログイン中...
            </span>
          ) : (
            'ログイン'
          )}
        </button>
      </form>
    </div>
  );
}
