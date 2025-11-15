import type { GroupPlayerStat } from '@/api/generated/mahjongApi.schemas';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader } from './ui/dialog';
import { DialogTitle } from '@radix-ui/react-dialog';
import { Button } from './ui/button';
import { Table, TableBody, TableCell, TableRow } from './ui/table';

export const STATS_NAME_MAP = {
  tournament_count: '大会参加回数',
  game_count: '対局数',
  total_score: '得点合計（チップ・換算含まない）',
  total_balance: '収支（チップ・換算含む）',
  average_rank: '平均順位',
  rank1_rate: '1位率',
  rank1_count: '1位回数',
  rank2_count: '2位回数',
  rank3_count: '3位回数',
  rank4_or_lower_count: '4位以下回数',
};
interface PlayerStatsModalProps {
  open: boolean;
  onClose: () => void;
  playerStats: GroupPlayerStat | null;
}

export const PlayerStatsModal = ({ open, onClose, playerStats }: PlayerStatsModalProps) => {
  if (!playerStats) return null;
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent showCloseButton={false}>
        <DialogHeader>
          <DialogTitle>プレイヤー成績</DialogTitle>
          <DialogDescription>{playerStats.player_name}さんの成績</DialogDescription>
        </DialogHeader>
        <Table>
          <TableBody>
            {Object.entries(STATS_NAME_MAP).map(([key, label]) => {
              const value = playerStats[key as keyof GroupPlayerStat];

              // null/undefined/空文字ならスキップ
              if (value === undefined || value === null || value === '') return null;

              return (
                <TableRow key={key}>
                  <TableCell className="font-medium">{label}</TableCell>
                  <TableCell className="text-right">
                    {typeof value === 'number' ? value.toLocaleString() : value}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
        <DialogFooter>
          <Button onClick={onClose}> 閉じる</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
