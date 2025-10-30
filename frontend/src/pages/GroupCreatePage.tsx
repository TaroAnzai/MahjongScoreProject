import type { Group } from '@/api/generated/mahjongApi.schemas';
import { useAlertDialog } from '@/components/common/AlertDialogProvider';
import { useCreateGroup } from '@/hooks/useGroups';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function GroupCreatePage() {
  const { alertDialog } = useAlertDialog();
  const navigate = useNavigate();
  const { mutateAsync: createGroupFromToken } = useCreateGroup();

  useEffect(() => {
    const token = new URLSearchParams(window.location.search).get('token');

    const createGroup = async () => {
      if (!token) {
        await alertDialog({
          title: 'Error',
          description: '無効なトークンです',
          showCancelButton: false,
        });
        console.error('Invalid token');
        navigate('/');
        return null;
      }
      console.log('Creating group with token:', token);
      try {
        const result = await createGroupFromToken({ token: token });
        navigate(`/groups/${result.owner_link}`);
      } catch (error) {
        navigate('/');
      }
    };
    createGroup();
  }, []);

  return <div>Creating group...</div>;
}

export default GroupCreatePage;
