// src/pages/TournamentPage.jsx
// React 関連
import React, { useEffect, useState } from 'react';
import { useParams, useSearchParams, useNavigate, useLocation } from 'react-router-dom';

// API 関連

// コンポーネント
import PageTitleBar from '../components/PageTitleBar';
import ButtonGridSection from '../components/ButtonGridSection';
import ScoreTable from '../components/ScoreTable';
import SelectorModal from '../components/SelectorModal';
import MultiSelectorModal from '../components/MultiSelectorModal';
import EditTournamentModal from '../components/EditTournamentModal';

// ユーティリティ
import {
  useAddTournamentPlayer,
  useDeleteTounamentsPlayer,
  useDeleteTournament,
  useGetTournament,
  useGetTournamentPlayers,
  useUpdateTournament,
} from '@/hooks/useTournaments';
import {
  useAddTablePlayer,
  useCreateTable,
  usedDeleteChipTableWithScores,
  useDeleteTable,
  useGetTables,
} from '@/hooks/useTables';
import { useGetTournamentScore, useGetTournamentScoreMap } from '@/hooks/useScore';
import { useGetPlayer } from '@/hooks/usePlayers';
import {
  TableType,
  type Player,
  type TablePlayerItem,
  type Tournament,
  type TournamentScoreMap,
  type TournamentUpdate,
} from '@/api/generated/mahjongApi.schemas';
import { useAlertDialog } from '@/components/common/AlertDialogProvider';
import { useDeleteApiTournamentsTournamentKey } from '@/api/generated/mahjongApi';
import { useDeleteGame } from '@/hooks/useGames';
import { getAccessLevelstring } from '@/utils/accessLevel_utils';
import { Spinner } from '@/components/ui/spinner';

const isChipTableNonZero = (scoreMap: TournamentScoreMap | undefined) => {
  const chipTableIds =
    scoreMap?.tables?.filter((t) => t.type === TableType.CHIP).map((t) => t.id) ?? [];
  return chipTableIds.some((tableId) => {
    const tableTotal = scoreMap?.players.reduce((sum, player) => {
      return sum + (player.scores?.[tableId] ?? 0);
    }, 0);
    return tableTotal !== 0;
  });
};
//CHPテーブルにスコアデータが入っているか確認
const hasChipTableScore = (scoreMap: TournamentScoreMap | undefined) => {
  const chipTableIds =
    scoreMap?.tables?.filter((t) => t.type === TableType.CHIP).map((t) => t.id) ?? [];
  return chipTableIds.some((tableId) => {
    return scoreMap?.players.some((player) => {
      const score = player.scores?.[tableId] ?? 0;
      return score !== 0;
    });
  });
};

function TournamentPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { alertDialog } = useAlertDialog();
  const { tournamentKey } = useParams();
  if (!tournamentKey) {
    return <div className="mahjong-container">大会キーが指定されていません</div>;
  }
  //Query系フック設定
  const { tournament, isLoadingTournament, loadTournament } = useGetTournament(tournamentKey);
  const groupKey =
    tournament?.parent_group_link.edit_link ?? tournament?.parent_group_link.view_link ?? '';
  const { players, isLoadingPlayers, loadPlayers } = useGetTournamentPlayers(tournamentKey);
  const { tables, isLoadingTables, loadTables } = useGetTables(tournamentKey);
  const { scoreMap, isLoadingScoreMap, loadScoreMap } = useGetTournamentScoreMap(tournamentKey);
  const { players: groupPlayers, isLoadingPlayers: isLoadingGroupPlayers } = useGetPlayer(groupKey);
  //Mutation系フック
  const { mutateAsync: addTournamentPlayer } = useAddTournamentPlayer();
  const { mutateAsync: deleteTournamentPlayer } = useDeleteTounamentsPlayer();
  const { mutate: createTable } = useCreateTable();
  const { mutate: updateTournament } = useUpdateTournament();
  const { mutate: deleteTournament } = useDeleteTournament();
  const { mutate: addTablePlayer } = useAddTablePlayer();
  const { mutateAsync: deleteChipTable } = usedDeleteChipTableWithScores();

  //ローカルステート

  const [showAddPlayerModal, setShowAddPlayerModal] = useState(false);

  const [isEditingRate, setIsEditingRate] = useState(false);
  const [editedRate, setEditedRate] = useState<number | ''>(tournament?.rate || 1);
  const [showDeletePlayerModal, setShowDeletePlayerModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [accessLevel, setAccessLevel] = useState('');
  useEffect(() => {
    setAccessLevel(getAccessLevelstring(tournament?.tournament_links));
  }, [tournament?.tournament_links]);
  useEffect(() => {
    sessionStorage.setItem('tournamentPage', location.pathname);
  }, [location.pathname]);
  const handleOpenAddPlayerModal = async () => {
    if (!groupPlayers || groupPlayers.length === 0) {
      alert('追加可能な参加者がいません');
      return;
    }
    setShowAddPlayerModal(true);
  };

  const handleAddPlayer = async (selectedPlayers: Player[]) => {
    setShowAddPlayerModal(false);
    const result = await addTournamentPlayer({
      tournamentKey: tournamentKey!,
      players: selectedPlayers,
    });
    //CHIPテーブルにも追加する。
    const chipTables = tables?.filter((t) => t.type === 'CHIP');
    chipTables?.forEach((table) => {
      const tableKey = table.edit_link;
      if (!tableKey) return;
      const tablePlayers = selectedPlayers.map<TablePlayerItem>((player) => ({
        player_id: player.id,
      }));
      addTablePlayer({ tableKey: tableKey, tablePlayersItem: tablePlayers });
    });
  };
  const handleCreateTable = () => {
    // 既存の卓名から使用済み番号を抽出
    const existingNames = tables?.map((t) => t.name);
    let index = 1;
    let newName = `卓${index}`;
    while (existingNames?.includes(newName)) {
      index++;
      newName = `卓${index}`;
    }

    // 卓を作成
    const newTable = createTable({
      tournamentKey: tournamentKey,
      tableCreate: {
        name: newName,
      },
    });
  };
  const handleRateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;

    // 入力中は空文字も許容（UIが消えるのを防ぐため文字列のまま保持）
    if (value === '') {
      setEditedRate(''); // 型を number | '' にする
      return;
    }

    const num = Number(value);
    if (!Number.isNaN(num)) {
      setEditedRate(num);
    }
  };
  const handleRateBlur = () => {
    setIsEditingRate(false);

    // 空文字やNaN、0以下の場合はフォールバック
    if (editedRate === '' || Number.isNaN(Number(editedRate)) || Number(editedRate) <= 0) {
      setEditedRate(tournament?.rate ?? 1); // ← 元の値に戻す
      return;
    }

    const newRate = Number(editedRate);
    if (newRate !== tournament?.rate) {
      updateTournament({
        tournamentKey: tournamentKey!,
        tournament: { rate: newRate },
      });
    }
  };

  const handleRateKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.currentTarget.blur();
    }
  };
  const handleOpenDeletePlayerModal = () => {
    if (!players?.length) {
      alertDialog({ title: 'Error Delete Player', description: '削除対象の参加者がいません' });
      return;
    }
    setShowDeletePlayerModal(true);
  };
  const handleDeletePlayer = async (player: Player) => {
    const confirmed = await alertDialog({
      title: 'Delete Player',
      description: `${player.name} を削除してよいですか？`,
    });
    //
    if (!confirmed) return;
    const payload = { tournamentKey: tournamentKey!, playerId: player.id };
    deleteTournamentPlayer(payload);

    setShowDeletePlayerModal(false);
  };
  const handleTitleChange = (newName: string) => {
    updateTournament({ tournamentKey: tournamentKey, tournament: { name: newName } });
  };
  const handleUpdateTournament = (updates: TournamentUpdate) => {
    const result = updateTournament({ tournamentKey: tournamentKey!, tournament: updates });
    setShowEditModal(false);
  };
  const handleTableClick = (table_id: number) => {
    if (!tables) return;
    const table = tables.find((t) => t.id === table_id);
    if (!table) return;
    const table_key = table.edit_link ?? table.view_link ?? '';
    navigate(`/table/${table_key}`);
  };
  const TitleWithModal = ({ onClick }: { onClick?: () => void }) => (
    <div className="mahjong-editable-title pointer-events-auto cursor-pointer" onClick={onClick}>
      {tournament?.name}
    </div>
  );
  const handleDeleteTournament = async () => {
    //テーブルがあればエラーにする。
    const nomalTables = tables?.filter((t) => t.type === TableType.NORMAL);
    if (nomalTables && nomalTables.length > 0) {
      alertDialog({
        title: 'Error deleting tournament',
        description: '記録表が存在するため、大会を削除できません。記録表を先に削除してください。',
        showCancelButton: false,
      });
      return;
    }
    //CHIPテーブルにデータが入っていたら確認後に削除する。
    const chipTables = tables?.filter((t) => t.type === TableType.CHIP);
    if (hasChipTableScore(scoreMap)) {
      const chipTableConfirmed = await alertDialog({
        title: 'Delete Tournament',
        description:
          'チップ記録表にスコアデータが存在します。大会を削除するとチップ記録表とそのスコアデータも削除されます。本当に削除してよいですか？',
      });
      if (!chipTableConfirmed) return;
    }
    const confirmed = await alertDialog({
      title: 'Delete Tournament',
      description: 'Are you sure you want to delete this tournament?',
    });
    if (!confirmed) return;

    //CHIPテーブルのスコアデータとテーブル自体を削除
    if (chipTables && chipTables.length > 0) {
      for (const table of chipTables) {
        const tableKey = table.edit_link;
        if (tableKey) {
          await deleteChipTable(tableKey);
        }
      }
    }
    await deleteTournament({ tournamentKey: tournamentKey! });
    navigate(`/group/${groupKey}`);
  };

  return (
    <div className="mahjong-container">
      <PageTitleBar
        title={tournament ? tournament.name : 'Loading...'}
        shareLinks={tournament?.tournament_links}
        onTitleClick={() => setShowEditModal(true)}
        onTitleChange={handleTitleChange}
        TitleComponent={TitleWithModal}
        parentUrl={sessionStorage.getItem('groupPage')}
      />
      <div
        id="rate-display"
        className="mahjong-rate-display"
        onClick={() => setIsEditingRate(true)}
      >
        レート:{' '}
        {isEditingRate ? (
          <input
            type="number"
            value={editedRate}
            step="1"
            min="1"
            onChange={handleRateChange}
            onBlur={handleRateBlur}
            onKeyDown={handleRateKeyDown}
            style={{ width: '60px' }}
            autoFocus
          />
        ) : (
          <span id="rate-value">{tournament?.rate.toFixed(1)}</span>
        )}
      </div>

      <ButtonGridSection>
        <button
          className="mahjong-button"
          disabled={accessLevel == 'VIEW'}
          onClick={handleOpenAddPlayerModal}
        >
          参加者を追加
        </button>
        <button
          className="mahjong-button"
          disabled={accessLevel == 'VIEW'}
          onClick={handleOpenDeletePlayerModal}
        >
          参加者を削除
        </button>
        <button
          className="mahjong-button"
          disabled={accessLevel == 'VIEW'}
          onClick={handleCreateTable}
        >
          記録用紙を新規作成
        </button>
        <button
          className="mahjong-button"
          disabled={accessLevel == 'VIEW'}
          onClick={handleDeleteTournament}
        >
          大会を削除
        </button>
      </ButtonGridSection>

      <div className="mahjong-section">
        <h3>大会成績</h3>
        {isChipTableNonZero(scoreMap) && (
          <p className="text-sm text-red-500">チップの合計が０になっていません。</p>
        )}
        {scoreMap ? (
          <ScoreTable scoreMap={scoreMap} onClick={handleTableClick} />
        ) : (
          <div>
            <Spinner />
            Loading...
          </div>
        )}
      </div>

      {showAddPlayerModal && (
        <MultiSelectorModal
          title="参加者を選択"
          items={groupPlayers ?? []}
          onConfirm={handleAddPlayer}
          onClose={() => setShowAddPlayerModal(false)}
        />
      )}

      {showDeletePlayerModal && (
        <SelectorModal
          title="削除する参加者を選択"
          open={showDeletePlayerModal}
          items={players ?? []}
          onSelect={handleDeletePlayer}
          onClose={() => setShowDeletePlayerModal(false)}
        />
      )}

      {showEditModal && tournament && (
        <EditTournamentModal
          tournament={tournament}
          onConfirm={handleUpdateTournament}
          onClose={() => setShowEditModal(false)}
        />
      )}
    </div>
  );
}

export default TournamentPage;
