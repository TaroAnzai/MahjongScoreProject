import PageTitleBar from '@/components/PageTitleBar';
import { PlayerStatsTable } from '@/components/PlayerStatsTable';
import { useGetPlayerStats } from '@/hooks/useScore';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

function GroupPlayerStatsPage() {
  const location = useLocation();
  const { groupKey } = useParams();
  const { t } = useTranslation();
  if (!groupKey)
    return <div className="mahjong-container">{t('statsPage.errorInvalidGroupKey')}</div>;
  const { playerStats, isLoadingPlayerStats } = useGetPlayerStats(groupKey);

  return (
    <div className="mahjong-container">
      <PageTitleBar
        title={t('statsPage.pageTitle')}
        parentUrl={`/group/${groupKey}`}
      ></PageTitleBar>
      <div className="mahjong-section">
        {isLoadingPlayerStats || !playerStats?.players ? (
          <div>Loading...</div>
        ) : (
          <PlayerStatsTable playerStatsList={playerStats.players} />
        )}
      </div>
    </div>
  );
}

export default GroupPlayerStatsPage;
