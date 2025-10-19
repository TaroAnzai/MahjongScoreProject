import type { Table } from '@/api/generated/mahjongApi.schemas';

/**
 * Given a list of tables and total scores, build a score map that contains each player's scores by table and total scores.
 * @param {Table[]} tables - a list of tables
 * @param {Object} totalScores - an object of total scores by player id
 * @returns {Object} a score map that contains each player's scores by table and total scores
 */
export async function makeScoreMap(table:Table, totalScores:) {
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
