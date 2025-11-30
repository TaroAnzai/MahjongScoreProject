import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';

export function AdminTop() {
  const navigate = useNavigate();
  return (
    <div className="mahjong-container max-w-1000! ">
      <h1 className="text-2xl font-bold mt-5">Admin Dashboard</h1>
      <p className="mt-3">
        Welcome to the admin dashboard. Use the navigation to manage groups and settings.
      </p>

      <div className="flex flex-col items-center mt-5">
        <div className="w-64 items-stretch space-y-2 ">
          <Button onClick={() => navigate('/admin/groups')}>Go to Groups Management</Button>
          <Button onClick={() => navigate('/admin/contact')}>Go to Contact</Button>
        </div>
      </div>
    </div>
  );
}
