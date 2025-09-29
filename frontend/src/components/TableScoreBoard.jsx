// src/components/TableScoreBoard.jsx
import styles from './TableScoreBoard.module.css';
import React, { useState } from 'react';

function TableScoreBoard({ table, players, games, onUpdateGame }) {
  const [editingGameIndex, setEditingGameIndex] = useState(null);
  const [editingScores, setEditingScores] = useState({});
  const [rowTotal, setRowTotal] = useState(0);
  const extraEmptyRows = 1;

  const isChipTable = table?.type === 'chip';
  // プレイヤー列の準備
  const displayPlayers = [...players];
  if (!isChipTable) {
    while (displayPlayers.length < 4) {
      displayPlayers.push({ id: `empty-${displayPlayers.length}`, name: '' });
    }
  }

  // ゲーム行の準備
  const displayGames = [...games];
  if (!isChipTable) {
    let targetLength;
    if (games.length <= 3) {
      targetLength = 4;  // 常に4行表示
    } else {
      targetLength = games.length + extraEmptyRows;  // それ以上は追加分も表示
    }

    while (displayGames.length < targetLength) {
      displayGames.push(null);
    }
  } 
const handleRowClick = (index) => {
  if (editingGameIndex === index) return; // ← 編集中なら無視

  const game = displayGames[index];
  const initialScores = {};
  displayPlayers.forEach(player => {
    const scoreEntry = game?.scores?.find((s) => s.player_id === player.id);
    initialScores[player.id] = scoreEntry?.score ?? '';
  });
  setEditingGameIndex(index);
  setEditingScores(initialScores);

  const initialTotal = Object.values(initialScores).reduce((acc, val) => {
    const num = parseFloat(val);
    return acc + (isNaN(num) ? 0 : num);
  }, 0);
  setRowTotal(initialTotal);
};

  const handleConfirm = async () => {
    const game = displayGames[editingGameIndex];
    const formatted = Object.entries(editingScores).map(([playerId, score]) => ({
      player_id: parseInt(playerId),
      score: parseFloat(score),
    }));
    const gameId = game?.game_id ?? null;
    const res = await onUpdateGame?.(editingGameIndex, gameId, formatted);
    if(res){
      setEditingGameIndex(null);
      setEditingScores({});
    }
  };

  const handleCancel = () => {
    setEditingGameIndex(null);
    setEditingScores({});
  };

  const totalScores = {};
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

  return (
    <div className={styles.scoreWrapper}>
      <table className={`${styles.scoreTable} table`} >
        <thead>
          <tr>
            <th className={styles.header}>回</th>
            {displayPlayers.map((player) => (
              <th key={player.id} className={styles.header}>{player.name}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {displayGames.map((game, index) => (
            <React.Fragment key={game?.game_id ?? `row-${index}`}>
              <tr onClick={() => handleRowClick(index)}>
                <td className={styles.cell}>
                  {isChipTable ? 'チップ' : `第${index + 1}回`}
                </td>
                {displayPlayers.map((player) => (
                  <td key={`${index}-${player.id}`} className={styles.cell}>
                    {editingGameIndex === index ? (
                      <input
                        type="number"
                        className={styles.input}
                        value={editingScores[player.id] ?? ''}
                        onChange={(e) =>{
                          const newScores = { ...editingScores, [player.id]: e.target.value };
                          setEditingScores(newScores);

                          const total = Object.values(newScores).reduce((acc, val) => {
                            const num = parseFloat(val);
                            return acc + (isNaN(num) ? 0 : num);
                          }, 0);
                          setRowTotal(total);
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
                      <td className={styles.totalCell} colSpan={displayPlayers.length + 1} style={{ textAlign: 'right', fontWeight: 'bold' }}>
                        合計: {rowTotal}
                      </td>
                    </tr>
                  <tr className={styles.confirmRow}>
                    <td colSpan={displayPlayers.length + 1} className={styles.confirmCell}>
                      <div className={styles.confirmBtnRow}>
                        <button onClick={handleConfirm} className={`${styles.addButton} mahjong-button`}>確定</button>
                        <button onClick={handleCancel} className={`${styles.addButton} mahjong-button`} style={{ marginLeft: '1rem' }}>キャンセル</button>
                      </div>
                    </td>
                  </tr>
                </> 
              )}
            </React.Fragment>
          ))}
          {!isChipTable &&(
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
