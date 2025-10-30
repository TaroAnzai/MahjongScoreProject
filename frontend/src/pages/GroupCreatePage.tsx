import type { Group } from '@/api/generated/mahjongApi.schemas';
import { useAlertDialog } from '@/components/common/AlertDialogProvider';
import { useCreateGroup } from '@/hooks/useGroups';
import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

function GroupCreatePage() {
  const { alertDialog } = useAlertDialog();
  const navigate = useNavigate();
  const { mutateAsync: createGroupFromToken } = useCreateGroup();
  const hasRun = useRef(false);

  useEffect(() => {
    if (hasRun.current) return; // ← 2回目はスキップ
    hasRun.current = true;
    const token = new URLSearchParams(window.location.search).get('token');

    const createGroup = async () => {
      if (!token) {
        await alertDialog({
          title: 'Error',
          description: '無効なトークンです',
          showCancelButton: false,
        });
        navigate('/');
        return null;
      }
      try {
        const result = await createGroupFromToken({ token: token });
        navigate(`/group/${result.owner_link}`);
      } catch (error) {
        navigate('/');
      }
    };
    createGroup();
  }, []);

  return <div>Creating group...</div>;
}

export default GroupCreatePage;
