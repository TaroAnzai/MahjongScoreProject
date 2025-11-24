// src/pages/GroupPage.jsx
import { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';

// API

// コンポーネント
import PageTitleBar from '../components/PageTitleBar';
import ButtonGridSection from '../components/ButtonGridSection';
import SelectorModal from '../components/SelectorModal';
import { useGetApiGroupsGroupKey } from '@/api/generated/mahjongApi';
import { useCreatePlayer, useDeletePlayer, useGetPlayer } from '@/hooks/usePlayers';
import { useCreateTournament, useGetTournaments } from '@/hooks/useTournaments';
import { useUpdateGroup } from '@/hooks/useGroups';
import type { Player } from '@/api/generated/mahjongApi.schemas';
import { TextInputModal } from '@/components/TextInputModal';
import { useAlertDialog } from '@/components/common/AlertDialogProvider';
import { useCreateTable } from '@/hooks/useTables';
import { getAccessLevelstring } from '@/utils/accessLevel_utils';
import { Spinner } from '@/components/ui/spinner';
import { useTranslation } from 'react-i18next';
function GroupPage() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { alertDialog } = useAlertDialog();
  const location = useLocation();
  const { groupKey } = useParams();
  if (!groupKey) return <div className="mahjong-container">{t('groupPage.groupKeyNotFound')}</div>;
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showTournamentModal, setShowTournamentModal] = useState(false);
  const [isCreateTournamentModalOpen, setIsCreateTournamentModalOpen] = useState(false);
  const [isCreatePlayerModalOpen, setIsCreatePlayerModalOpen] = useState(false);

  const { data: group, refetch: refetchGroup } = useGetApiGroupsGroupKey(groupKey);
  const { mutate: updateGroup } = useUpdateGroup(refetchGroup);
  const { players, isLoadingPlayers, loadPlayers } = useGetPlayer(groupKey);
  const { mutate: createPlayer } = useCreatePlayer(loadPlayers);

  const { mutate: deletePlayer } = useDeletePlayer(loadPlayers);
  const { mutateAsync: createTournament } = useCreateTournament();
  const { mutateAsync: createChipTable } = useCreateTable();
  const { tournaments } = useGetTournaments(groupKey);
  const [accessLevel, setAccessLevel] = useState('');
  useEffect(() => {
    setAccessLevel(getAccessLevelstring(group?.group_links));
  }, [group?.group_links]);
  useEffect(() => {
    sessionStorage.setItem('groupPage', location.pathname);
  }, [location.pathname]);

  const handleAddPlayer = (name: string) => {
    if (!name) return;
    createPlayer({ groupKey: groupKey, player: { name: name } });
    setIsCreatePlayerModalOpen(false);
  };

  const handleDeletePlayer = (player: Player) => {
    if (!player || player.id === undefined) return;
    deletePlayer({ groupKey: groupKey, playerId: player.id });
  };
  const handleCreateTournament = async (name: string) => {
    if (!name) return;
    const payload = { groupKey: groupKey, tournament: { name: name } };
    const data = await createTournament(payload);
    //CHIPテーブルを作成
    if (!data.edit_link) return;
    await createChipTable({
      tournamentKey: data.edit_link,
      tableCreate: { name: t('Common.chip'), type: 'CHIP' },
    });
    navigate(`/tournament/${data.edit_link}`);
  };

  const handleTitleChange = (newTitle: string) => {
    if (!newTitle) return;
    if (!groupKey) return;
    updateGroup({ groupKey: groupKey, groupUpdate: { name: newTitle } });
  };

  const handleAddGroup = async () => {
    if (!groupKey || !group) return;
    const res = await alertDialog({
      title: t('groupPage.dialogAddGroupTitle'),
      description: t('groupPage.dialogAddGroupDescription', { groupName: group.name }),
      showCancelButton: true,
    });

    if (!res) return;
    localStorage.setItem(`group_key_${groupKey}`, groupKey);
    navigate('/');
  };
  const handleRemoveGroup = async () => {
    if (!groupKey || !group) return;
    const confirmed = await alertDialog({
      title: t('groupPage.dialogRemoveGroupTitle'),
      description: t('groupPage.dialogRemoveGroupDescription', { groupName: group.name }),
      showCancelButton: true,
    });
    if (!confirmed) return;
    localStorage.removeItem(`group_key_${groupKey}`);
    navigate(`/`);
  };

  return (
    <div className="mahjong-container">
      <PageTitleBar
        title={group ? group.name : 'Loading...'}
        shareLinks={group ? group.group_links : []}
        onTitleChange={handleTitleChange}
        parentUrl="/"
      />

      <ButtonGridSection>
        <button
          className="mahjong-button"
          disabled={accessLevel === 'VIEW'}
          onClick={() => setIsCreatePlayerModalOpen(true)}
        >
          {t('groupPage.buttonAddPlayer')}
        </button>
        <button
          className="mahjong-button"
          disabled={accessLevel === 'VIEW'}
          onClick={() => setShowDeleteModal(true)}
        >
          {t('groupPage.buttonDeletePlayer')}
        </button>
        <button
          className="mahjong-button"
          disabled={accessLevel === 'VIEW'}
          onClick={() => setIsCreateTournamentModalOpen(true)}
        >
          {t('groupPage.buttonCreateTournament')}
        </button>
        <button className="mahjong-button" onClick={() => setShowTournamentModal(true)}>
          {t('groupPage.buttonSelectTournament')}
        </button>
        <button className="mahjong-button" onClick={handleAddGroup}>
          {t('groupPage.buttonSaveToBrowser')}
        </button>
        <button className="mahjong-button" onClick={handleRemoveGroup}>
          {t('groupPage.buttonRemoveFromBrowser')}
        </button>
        <button className="mahjong-button" onClick={() => navigate(`/group/stats/${groupKey}`)}>
          {t('groupPage.buttonStats')}
        </button>
      </ButtonGridSection>

      <div className="mahjong-section">
        <h3 className="mahjong-subtitle">{t('groupPage.sectionMemberList')}</h3>
        {isLoadingPlayers ? (
          <div className="flex items-center justify-center gap-2">
            <Spinner />
            <span>Loading...</span>
          </div>
        ) : (
          <ul className="mahjong-list">
            {players?.map((player) => (
              <li key={player.id} className="mahjong-list-item">
                {player.name}
              </li>
            ))}
          </ul>
        )}
      </div>

      {showDeleteModal && (
        <SelectorModal
          title={t('groupPage.modalDeletePlayerTitle')}
          open={showDeleteModal}
          items={players}
          onSelect={(player: Player) => {
            handleDeletePlayer(player);
          }}
          onClose={() => setShowDeleteModal(false)}
        />
      )}
      {showTournamentModal && (
        <SelectorModal
          title={t('groupPage.modalSelectTournamentTitle')}
          open={showTournamentModal}
          items={tournaments?.map((t) => ({
            ...t,
            plusDisplayItem:
              t.created_at &&
              new Date(t.started_at ?? t.created_at).toLocaleDateString('ja-JP', {
                timeZone: 'Asia/Tokyo',
              }),
          }))}
          plusDisplayItem={'plusDisplayItem'}
          onSelect={(tournament) => {
            if (tournament) {
              const tournament_key = tournament.edit_link ?? tournament.view_link;
              navigate(`/tournament/${tournament_key}`);
            }
            setShowTournamentModal(false);
          }}
          onClose={() => setShowTournamentModal(false)}
          emptyMessage={t('groupPage.modalSelectTournamentEmpty')}
        />
      )}
      <TextInputModal
        open={isCreatePlayerModalOpen}
        onComfirm={handleAddPlayer}
        onClose={() => setIsCreatePlayerModalOpen(false)}
        value=""
        title={t('groupPage.modalCreatePlayerTitle')}
        discription={t('groupPage.modalCreatePlayerDescription')}
      />
      <TextInputModal
        open={isCreateTournamentModalOpen}
        onComfirm={handleCreateTournament}
        onClose={() => setIsCreateTournamentModalOpen(false)}
        title={t('groupPage.modalCreateTournamentTitle')}
        discription={t('groupPage.modalCreateTournamentDescription')}
      />
    </div>
  );
}

export default GroupPage;
