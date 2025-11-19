import { Input } from '@/components/ui/input';
import { useAdminLogin } from '@/hooks/useAdmin';
import { Eye, EyeOff } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

export function AdminLogin() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [show, setShow] = useState(false);
  const { mutate: login, isPending, isSuccess } = useAdminLogin();

  useEffect(() => {
    if (isSuccess) {
      console.log('Admin login success');
      navigate('/admin/groups');
    }
  }, [isSuccess]);
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login({ username: username, password: password });
  };
  return (
    <div className="mahjong-container">
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

          <button
            type="button"
            onClick={() => setShow(!show)}
            className="absolute right-2 top-1/2 -translate-y-1/2
             p-0 m-0 bg-transparent border-none shadow-none
             text-gray-500 hover:text-gray-700
             focus:outline-none"
          >
            {show ? <EyeOff size={18} /> : <Eye size={18} />}
          </button>
        </div>
        <button className="mahjong-button" type="submit">
          ログイン
        </button>
      </form>
    </div>
  );
}
