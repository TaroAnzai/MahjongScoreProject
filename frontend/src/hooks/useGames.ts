import {
  deleteApiTablesTableKeyGamesGameId,
  getGetApiTablesTableKeyGamesQueryKey,
  getGetApiTablesTableKeyGamesQueryOptions,
  postApiTablesTableKeyGames,
  putApiTablesTableKeyGamesGameId,
  useDeleteApiTablesTableKeyGamesGameId,
  useGetApiTablesTableKeyGames,
} from '@/api/generated/mahjongApi';
import type { GameCreate, GameUpdate } from '@/api/generated/mahjongApi.schemas';
import { useAlertDialog } from '@/components/common/AlertDialogProvider';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

export const useCreateGame = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { tableKey: string; gameCreate: GameCreate }) => {
      return postApiTablesTableKeyGames(data.tableKey, data.gameCreate);
    },
    onSuccess: (data, variables) => {
      toast.success('New game created successfully');
      const queryKey = getGetApiTablesTableKeyGamesQueryKey(variables.tableKey);
      queryClient.invalidateQueries({ queryKey });
    },
    onError: (error) => {
      console.error('Error creating game:', error);
      toast.error('Error creating game');
    },
  });
};
export const useGetTableGames = (tableKey: string) => {
  const { data: games, isLoading: isLoadingGames } = useGetApiTablesTableKeyGames(tableKey);
  return { games, isLoadingGames };
};
export const useUpdateGame = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { tableKey: string; gameId: number; gameUpdate: GameUpdate }) => {
      return putApiTablesTableKeyGamesGameId(data.tableKey, data.gameId, data.gameUpdate);
    },
    onSuccess: (data, variables) => {
      toast.success('Game updated successfully');
      const queryKey = getGetApiTablesTableKeyGamesQueryKey(variables.tableKey);
      queryClient.invalidateQueries({ queryKey });
    },
    onError: (error) => {
      console.error('Error updating game:', error);
      toast.error('Error updating game');
    },
  });
};

export const useDeleteGame = () => {
  const { alertDialog } = useAlertDialog();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { tableKey: string; gameId: number }) => {
      return deleteApiTablesTableKeyGamesGameId(data.tableKey, data.gameId);
    },
    onSuccess: (data, variables) => {
      toast.success('Game deleted successfully');
      const queryKey = getGetApiTablesTableKeyGamesQueryKey(variables.tableKey);
      queryClient.invalidateQueries({ queryKey });
    },
    onError: (error) => {
      console.error('Error deleting game:', error);
      alertDialog({ title: 'Error', description: 'Error deleting game' });
    },
  });
};
