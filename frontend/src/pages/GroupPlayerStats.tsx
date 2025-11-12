import { useAlertDialog } from '@/components/common/AlertDialogProvider';
import PageTitleBar from '@/components/PageTitleBar';
import { useGetPlayerStats } from '@/hooks/useScore';
import { useLocation, useNavigate, useParams } from 'react-router-dom';

function GroupPlayerStatsPage() {
  const navigate = useNavigate();
  const { alertDialog } = useAlertDialog();
  const location = useLocation();
  const { groupKey } = useParams();
  if (!groupKey) return <div className="mahjong-container">グループキーが不明です</div>;
  const { playerStats, isLoadingPlayerStats } = useGetPlayerStats(groupKey);
  return (
    <div className="mahjong-container">
      <PageTitleBar title="プレイヤー統計" parentUrl={`/group/${groupKey}`}></PageTitleBar>
    </div>
  );
}

export default GroupPlayerStatsPage;
