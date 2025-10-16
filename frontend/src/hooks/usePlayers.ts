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
  return useMutation({
    mutationFn: (data: { groupKey: string; player: PlayerCreate }) => {
      return postApiGroupsGroupKeyPlayers(data.groupKey, data.player);
    },
    onSuccess: (data) => {
      console.log('Player created, reloading players...');
      onAfterCreate?.();
    },
    onError: (error) => {
      console.error('Error creating player:', error);
    },
  });
};
export const useDeletePlayer = (onAfterDelete?: () => void) => {
  return useMutation({
    mutationFn: (data: { groupKey: string; playerId: number }) => {
      return deleteApiGroupsGroupKeyPlayersPlayerId(data.groupKey, data.playerId);
    },
    onSuccess: (data) => {
      onAfterDelete?.();
    },
    onError: (error) => {
      console.error('Error deleting player:', error);
    },
  });
};
