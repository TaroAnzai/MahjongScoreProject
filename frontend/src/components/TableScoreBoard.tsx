// src/components/TableScoreBoard.jsx
import type { Game, Player, ScoreInput, Table } from '@/api/generated/mahjongApi.schemas';
import styles from './TableScoreBoard.module.css';
import React, { useState } from 'react';
import { Button } from './ui/button';

interface TableScoreBoardProps {
  table: Table;
  players: readonly Player[];
  games: Game[];
  onUpdateGame: (gameId: number | null, scres: ScoreInput[]) => void;
  disabled?: boolean;
}
function TableScoreBoard({
  table,
  players,
  games,
  onUpdateGame,
  disabled = false,
}: TableScoreBoardProps) {
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
    // 数値・マイナス・小数点・空欄以外は無視
    if (value !== '' && !/^-?\d*\.?\d*$/.test(value)) return;

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
    <div className={styles.scoreWrapper}>
      <table className={`${styles.scoreTable} table`}>
        <thead>
          <tr>
            <th className={styles.header}>回</th>
            {displayPlayers.map((player) => (
              <th key={player.id} className={styles.header}>
                {player.name}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {displayGames.map((game, index) => (
            <React.Fragment key={game?.id ?? `row-${index}`}>
              <tr onClick={() => handleRowClick(index)}>
                <td className={styles.cell}>{isChipTable ? 'チップ' : `第${index + 1}回`}</td>
                {displayPlayers.map((player) => (
                  <td key={`${index}-${player.id}`} className={styles.cell}>
                    {editingGameIndex === index && player.id > 0 ? (
                      <input
                        type="text"
                        inputMode="numeric"
                        className={styles.input}
                        value={editingScores[player.id] ?? ''}
                        onChange={(e) => {
                          handleScoreChange(player.id, e.target.value);
                        }}
                      />
                    ) : (
                      game?.scores?.find((s) => s.player_id === player.id)?.score ?? ''
                    )}
                  </td>
                ))}
              </tr>
              {editingGameIndex === index && (
                <>
                  <tr className={styles.sumRow}>
                    <td
                      className={styles.totalCell}
                      colSpan={displayPlayers.length + 1}
                      style={{ textAlign: 'right', fontWeight: 'bold' }}
                    >
                      合計: {rowTotal}
                    </td>
                  </tr>
                  <tr className={styles.confirmRow}>
                    <td colSpan={displayPlayers.length + 1} className={styles.confirmCell}>
                      <div className={styles.confirmBtnRow}>
                        <Button
                          onClick={handleConfirm}
                          className={`${styles.addButton} mahjong-button`}
                          disabled={rowTotal !== 0 && table.type === 'NORMAL'}
                        >
                          確定
                        </Button>
                        <Button
                          onClick={handleCancel}
                          className={`${styles.addButton} mahjong-button`}
                          style={{ marginLeft: '1rem' }}
                        >
                          キャンセル
                        </Button>
                      </div>
                    </td>
                  </tr>
                </>
              )}
            </React.Fragment>
          ))}
          {!isChipTable && (
            <tr className={styles.totalRow}>
              <td className={styles.header}>合計</td>
              {displayPlayers.map((player) => (
                <td key={`total-${player.id}`} className={styles.cell}>
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
