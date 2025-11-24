import type { GroupPlayerStat } from '@/api/generated/mahjongApi.schemas';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader } from './ui/dialog';
import { DialogTitle } from '@radix-ui/react-dialog';
import { Button } from './ui/button';
import { Table, TableBody, TableCell, TableRow } from './ui/table';
import { useTranslation } from 'react-i18next';

export const STATS_NAME_MAP = {
  tournament_count: 'tournament_count',
  game_count: 'game_count',
  total_score: 'total_score',
  total_balance: 'total_balance',
  average_rank: 'average_rank',
  rank1_rate: 'rank1_rate',
  rank1_count: 'rank1_count',
  rank2_count: 'rank2_count',
  rank3_count: 'rank3_count',
  rank4_or_lower_count: 'rank4_or_lower_count',
};
interface PlayerStatsModalProps {
  open: boolean;
  onClose: () => void;
  playerStats: GroupPlayerStat | null;
}

export const PlayerStatsModal = ({ open, onClose, playerStats }: PlayerStatsModalProps) => {
  const { t } = useTranslation();
  if (!playerStats) return null;
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent showCloseButton={false}>
        <DialogHeader>
          <DialogTitle>{t('statsPage.dialogTitle')}</DialogTitle>
          <DialogDescription>
            {t('statsPage.dialogDescription', { playerName: playerStats.player_name })}
          </DialogDescription>
        </DialogHeader>
        <Table>
          <TableBody>
            {Object.entries(STATS_NAME_MAP).map(([key, label]) => {
              const value = playerStats[key as keyof GroupPlayerStat];

              // null/undefined/空文字ならスキップ
              if (value === undefined || value === null || value === '') return null;

              return (
                <TableRow key={key}>
                  <TableCell className="font-medium">
                    {t(`statsPage.statsNameMap.${label}`)}
                  </TableCell>
                  <TableCell className="text-right">
                    {typeof value === 'number' ? value.toLocaleString() : value}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
        <DialogFooter>
          <Button onClick={onClose}> {t('Common.close')}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
