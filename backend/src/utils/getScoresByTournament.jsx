// src/utils/getScoresByTournament.jsx
import { getTablesByTournament } from '../api/table_api';
import { getTableGames } from '../api/game_api';
import { getPlayerTotalScores } from '../api/tournament_api';
/**
 * トーナメントに紐づく各テーブルのスコアを集計し、
 * getPlayerTotalScores で取得した合計点/換算点を合成して返す
 * @param {Object} tournament - トーナメントオブジェクト（idを含む）
 * @returns {Promise<Object>} playerId をキーとした scoreMap
 */
export async function getScoresByTournament(tournament) {
  const tables = await getTablesByTournament(tournament.id);
  const totalScores = await getPlayerTotalScores(tournament.id); // { [playerId]: { raw, converted } }
  const scoreMap = {};

  for (const table of tables) {
    const games = await getTableGames(table.id);
    for (const game of games) {
      for (const score of game.scores) {
        const pid = score.player_id;
        if (!scoreMap[pid]) scoreMap[pid] = {};

        const key = `table_${table.id}`;
        if (!scoreMap[pid][key]) scoreMap[pid][key] = 0;

        scoreMap[pid][key] += score.score;
      }
    }
  }
  // 合計・換算点のマージ
  for (const pid in totalScores) {
    if (!scoreMap[pid]) scoreMap[pid] = {};
    scoreMap[pid].raw = totalScores[pid].raw ?? 0;
    scoreMap[pid].converted = totalScores[pid].converted ?? 0;
  }

  return scoreMap;
}