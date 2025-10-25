import {
  deleteApiGroupsGroupKeyPlayersPlayerId,
  postApiGroupsGroupKeyPlayers,
  useDeleteApiGroupsGroupKeyPlayersPlayerId,
  useGetApiGroupsGroupKey,
  useGetApiGroupsGroupKeyPlayers,
  usePostApiGroupsGroupKeyPlayers,
} from '@/api/generated/mahjongApi';
import type { PlayerCreate } from '@/api/generated/mahjongApi.schemas';
import { Mutation, useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';
import { useAlertDialog } from '@/components/common/AlertDialogProvider';

/**
 * Fetch players in a group by group key.
 *
 * @param groupKey - Group key to fetch players.
 * @returns An object containing the players data, a boolean indicating if the data is loading, and a function to refetch the data.
 */
export const useGetPlayer = (groupKey: string) => {
  const {
    data: players,
    isLoading: isLoadingPlayers,
    refetch: loadPlayers,
  } = useGetApiGroupsGroupKeyPlayers(groupKey);
  return { players, isLoadingPlayers, loadPlayers };
};
export const useCreatePlayer = (onAfterCreate?: () => void) => {
  const { alertDialog } = useAlertDialog();
  return useMutation({
    mutationFn: (data: { groupKey: string; player: PlayerCreate }) => {
      return postApiGroupsGroupKeyPlayers(data.groupKey, data.player);
    },
    onSuccess: (data) => {
      toast.success('Player created successfully');
      onAfterCreate?.();
    },
    onError: (error: any) => {
      console.error('Error creating player:', error);
      const message =
        error.body?.errors?.json?.message?.[0] ??
        error.body?.message ??
        error.statusText ??
        'Unknown error';
      alertDialog({
        title: 'Error creating player',
        description: message,
        showCancelButton: false,
      });
    },
  });
};
export const useDeletePlayer = (onAfterDelete?: () => void) => {
  const { alertDialog } = useAlertDialog();
  return useMutation({
    mutationFn: (data: { groupKey: string; playerId: number }) => {
      return deleteApiGroupsGroupKeyPlayersPlayerId(data.groupKey, data.playerId);
    },
    onSuccess: (data) => {
      toast.success('Player deleted successfully');
      onAfterDelete?.();
    },
    onError: (error: any) => {
      console.error('Error deleting player:', error);
      const message =
        error.body?.errors?.json?.message?.[0] ??
        error.body?.message ??
        error.statusText ??
        'Unknown error';
      alertDialog({
        title: 'Error deleting player',
        description: message,
        showCancelButton: false,
      });
    },
  });
};
