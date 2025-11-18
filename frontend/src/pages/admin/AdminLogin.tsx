import { Input } from '@/components/ui/input';
import { useAdminLogin } from '@/hooks/useAdmin';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export function AdminLogin() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { mutate: login, isPending } = useAdminLogin();
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('AdminLogin', username, password);
    login({ username: username, password: password });
  };
  return (
    <div className="mahjong-container">
      <h2>AdminLogin</h2>
      <form className="flex flex-col gap-2" onSubmit={handleSubmit}>
        <Input
          type="text"
          placeholder="ユーザー名"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <Input
          type="password"
          placeholder="パスワード"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button className="mahjong-button" type="submit">
          ログイン
        </button>
      </form>
    </div>
  );
}
