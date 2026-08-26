// src/components/TableScoreBoard.jsx
import type { Game, Player, ScoreInput, Table } from '@/api/generated/mahjongApi.schemas';
import React, { useState } from 'react';
import { Button } from './ui/button';
import { useTranslation } from 'react-i18next';
import { toast } from 'sonner';

interface TableScoreBoardProps {
  table: Table;
  players: readonly Player[];
  games: Game[];
  onUpdateGame: (gameId: number | null, scres: ScoreInput[]) => void;
  disabled?: boolean;
}
const cellClass = 'max-w-game-cell overflow-hidden text-ellipsis whitespace-nowrap border border-table-border p-2 text-center';
const tableClass = "mt-4 w-full min-w-full border-separate border-spacing-0 [&_th]:rounded-small [&_th]:border [&_th]:border-[var(--color-border-subtle)] [&_th]:bg-[linear-gradient(135deg,rgba(34,139,34,0.3),rgba(0,100,0,0.2))] [&_th]:px-2 [&_th]:py-3 [&_th]:font-semibold [&_th]:text-[#90ee90] [&_th]:[text-shadow:0_1px_2px_rgba(0,0,0,0.5)] [&_td]:border [&_td]:border-[rgba(144,238,144,0.1)] [&_td]:bg-[linear-gradient(145deg,rgba(34,139,34,0.1),rgba(0,100,0,0.05))] [&_td]:px-2 [&_td]:py-3.5 [&_td]:font-medium [&_td]:text-[#e0ffe0] [&_tbody_tr]:transition-all [&_tbody_tr]:duration-300 [&_tbody_tr:hover]:scale-[1.02]";
function TableScoreBoard({
  table,
  players,
  games,
  onUpdateGame,
  disabled = false,
}: TableScoreBoardProps) {
  const { t } = useTranslation();
  if (!table || !players || !games) return null;
  const [editingGameIndex, setEditingGameIndex] = useState<number | null>(null);
  const [editingScores, setEditingScores] = useState<Record<number, string>>({});
  const [rowTotal, setRowTotal] = useState(0);
  const extraEmptyRows = 1;
  const isChipTable = table.type === 'CHIP';
  // プレイヤー列の準備 4名以下の場合はダミーを追加
  const displayPlayers = [...players];
  if (!isChipTable) {
    while (displayPlayers.length < 4) {
      displayPlayers.push({ id: (displayPlayers.length + 1) * -1, name: '', group_id: 0 });
    }
  }

  // ゲーム行の準備
  const displayGames: (Game | null)[] = [...games];
  if (!isChipTable) {
    let targetLength;
    if (games.length <= 3) {
      targetLength = 4; // 常に4行表示
    } else {
      targetLength = games.length + extraEmptyRows; // それ以上は追加分も表示
    }

    while (displayGames.length < targetLength) {
      displayGames.push(null);
    }
  } else {
    if (games.length === 0) {
      displayGames.push(null);
    }
  }
  const handleRowClick = (index: number) => {
    if (editingGameIndex === index) return; // ← 編集中なら無視
    if (disabled) return; // ← 編集不可なら無視

    const game = displayGames[index];
    const initialScores: Record<number, string> = {};
    displayPlayers.forEach((player) => {
      const scoreEntry = game?.scores?.find((s) => s.player_id === player.id);
      initialScores[player.id] = scoreEntry?.score ? String(scoreEntry.score) : '';
    });
    setEditingGameIndex(index);
    setEditingScores(initialScores);

    const initialTotal = Object.values(initialScores).reduce((acc, val) => {
      const num = parseFloat(val);
      return acc + (isNaN(num) ? 0 : num);
    }, 0);
    setRowTotal(initialTotal ?? 0);
  };

  const handleConfirm = () => {
    if (editingGameIndex === null) return;
    const game = displayGames[editingGameIndex];
    const formatted = Object.entries(editingScores)
      .filter(([, score]) => score !== '')
      .map(([playerId, score]) => ({
        player_id: parseInt(playerId),
        score: Number(score),
      }));
    const gameId = game?.id ?? null;
    if (formatted.length === 0) return;
    onUpdateGame(gameId, formatted);
    setEditingGameIndex(null);
    setEditingScores({});
  };

  const handleCancel = () => {
    setEditingGameIndex(null);
    setEditingScores({});
  };

  const totalScores: Record<number, number> = {};
  displayPlayers.forEach((player) => {
    totalScores[player.id] = 0;
  });

  displayGames.forEach((game) => {
    if (game?.scores) {
      game.scores.forEach(({ player_id, score }) => {
        if (totalScores[player_id] !== undefined) {
          totalScores[player_id] += score;
        }
      });
    }
  });
  const handleScoreChange = (playerId: number, value: string) => {
    console.log('handleScoreChange', playerId, value);
    // 数値・マイナス・小数点・空欄以外は無視
    if (value !== '' && !/^-?\d*\.?\d*$/.test(value)) {
      toast.error(t('scoreBoard.errorInvalidScore'));
      return;
    }
    console.log('handleScoreChange valid', playerId, value);
    setEditingScores((prev) => {
      const newScores = { ...prev, [playerId]: value };

      // 有効な数値だけ合計に含める
      const total = Object.values(newScores).reduce((acc: number, val) => {
        const num = parseFloat(val);
        return acc + (isNaN(num) ? 0 : num);
      }, 0);

      setRowTotal(total);
      return newScores;
    });
  };
  return (
    <div className="mt-4 overflow-x-auto">
      <table className={tableClass}>
        <thead>
          <tr>
            <th className={cellClass}>{t('scoreBoard.gameTitle')}</th>
            {displayPlayers.map((player) => (
              <th key={player.id} className={cellClass}>
                {player.name}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {displayGames.map((game, index) => (
            <React.Fragment key={game?.id ?? `row-${index}`}>
              <tr onClick={() => handleRowClick(index)}>
                <td className={cellClass}>
                  {isChipTable ? t('Common.chip') : t('scoreBoard.gameLabel', { index: index + 1 })}
                </td>
                {displayPlayers.map((player) => (
                  <td key={`${index}-${player.id}`} className={cellClass}>
                    {editingGameIndex === index && player.id > 0 ? (
                      <input
                        type="text"
                        inputMode="numeric"
                        className="score-input box-border m-0 h-full w-full overflow-hidden text-ellipsis border-0 bg-score-input-background p-0.5 text-center text-inherit text-score-input focus:border focus:border-[#4caf50] focus:shadow-[0_0_3px_rgba(76,175,80,0.5)] disabled:cursor-default disabled:border-0 disabled:bg-transparent disabled:text-white"
                        value={editingScores[player.id] ?? ''}
                        onClick={(e) => e.stopPropagation()}
                        onChange={(e) => {
                          handleScoreChange(player.id, e.target.value);
                        }}
                      />
                    ) : (
                      (game?.scores?.find((s) => s.player_id === player.id)?.score ?? '')
                    )}
                  </td>
                ))}
              </tr>
              {editingGameIndex === index && (
                <>
                  <tr className="bg-none hover:transform-none">
                    <td
                      className="text-right font-bold"
                      colSpan={displayPlayers.length + 1}
                    >
                      {t('scoreBoard.totalLabel')}: {rowTotal}
                    </td>
                  </tr>
                  <tr className="border border-table-border bg-none hover:transform-none">
                    <td colSpan={displayPlayers.length + 1} className="p-2 text-center">
                      <div className="flex items-center justify-center gap-4">
                        <Button
                          onClick={handleConfirm}
                          variant="mahjong"
                          disabled={rowTotal !== 0 && table.type === 'NORMAL'}
                        >
                          {t('Common.Confirmed')}
                        </Button>
                        <Button
                          onClick={handleCancel}
                          variant="mahjong"
                        >
                          {t('Common.Cancel')}
                        </Button>
                      </div>
                    </td>
                  </tr>
                </>
              )}
            </React.Fragment>
          ))}
          {!isChipTable && (
            <tr className="font-bold">
              <td className={cellClass}>{t('scoreBoard.totalLabel')}</td>
              {displayPlayers.map((player) => (
                <td key={`total-${player.id}`} className={cellClass}>
                  {totalScores[player.id] ?? 0}
                </td>
              ))}
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default TableScoreBoard;
