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
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { useAlertDialog } from '@/components/common/AlertDialogProvider';

export const useCreateGame = () => {
  const { alertDialog } = useAlertDialog();
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
    onError: (error: any) => {
      console.error('Error creating game:', error);
      const message =
        error.body?.errors?.json?.message?.[0] ??
        error.body?.message ??
        error.statusText ??
        'Unknown error';
      alertDialog({
        title: 'Error creating game',
        description: message,
        showCancelButton: false,
      });
    },
  });
};
export const useGetTableGames = (tableKey: string, optins?: Object) => {
  const { data: games, isLoading: isLoadingGames } = useGetApiTablesTableKeyGames(tableKey, optins);
  return { games, isLoadingGames };
};
export const useUpdateGame = () => {
  const { alertDialog } = useAlertDialog();
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
    onError: (error: any) => {
      console.error('Error updating game:', error);
      const message =
        error.body?.errors?.json?.message?.[0] ??
        error.body?.message ??
        error.statusText ??
        'Unknown error';
      alertDialog({
        title: 'Error updating game',
        description: message,
        showCancelButton: false,
      });
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
    onError: (error: any) => {
      console.error('Error deleting game:', error);
      const message =
        error.body?.errors?.json?.message?.[0] ??
        error.body?.message ??
        error.statusText ??
        'Unknown error';
      alertDialog({
        title: 'Error deleting game',
        description: message,
        showCancelButton: false,
      });
    },
  });
};
