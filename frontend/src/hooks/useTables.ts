import {
  deleteApiTablesTableKey,
  deleteApiTablesTableKeyPlayersPlayerId,
  getApiTablesTableKeyGames,
  getGetApiTablesTableKeyPlayersQueryKey,
  getGetApiTablesTableKeyPlayersQueryOptions,
  getGetApiTablesTableKeyQueryOptions,
  postApiTablesTableKeyPlayers,
  postApiTournamentsTournamentKeyTables,
  putApiTablesTableKey,
  useGetApiTablesTableKey,
  useGetApiTablesTableKeyPlayers,
  useGetApiTournamentsTournamentKeyTables,
} from '@/api/generated/mahjongApi';
import type { TableCreate, TablePlayerItem, TableUpdate } from '@/api/generated/mahjongApi.schemas';
import { useAlertDialog } from '@/components/common/AlertDialogProvider';
import { Mutation, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { useDeleteGame } from './useGames';

export const useGetTables = (tournamentKey: string) => {
  const {
    data: tables,
    isLoading: isLoadingTables,
    refetch: loadTables,
  } = useGetApiTournamentsTournamentKeyTables(tournamentKey);
  return { tables, isLoadingTables, loadTables };
};

export const useCreateTable = () => {
  const { alertDialog } = useAlertDialog();
  const navigate = useNavigate();
  return useMutation({
    mutationFn: (data: { tournamentKey: string; tableCreate: TableCreate }) => {
      return postApiTournamentsTournamentKeyTables(data.tournamentKey, data.tableCreate);
    },
    onSuccess: (data, variables) => {
      toast.success('Table created successfully');
      // 遷移
      navigate(`/table/${data.edit_link}`);
    },
    onError: (error: any) => {
      console.error('Error creating table:', error);
      const message =
        error.body?.errors?.json?.message?.[0] ??
        error.body?.message ??
        error.statusText ??
        'Unknown error';
      alertDialog({
        title: 'Error creating table',
        description: message,
        showCancelButton: false,
      });
    },
  });
};

export const useUpdateTable = () => {
  const { alertDialog } = useAlertDialog();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { tableKey: string; tableUpdate: TableUpdate }) => {
      return putApiTablesTableKey(data.tableKey, data.tableUpdate);
    },
    onSuccess: (data, variables) => {
      toast.success('Table updated successfully');
      // キャッシュ更新
      const queryKey = getGetApiTablesTableKeyQueryOptions(variables.tableKey).queryKey;
      queryClient.invalidateQueries({ queryKey });
    },
    onError: (error: any) => {
      console.error('Error updating table:', error);
      const message =
        error.body?.errors?.json?.message?.[0] ??
        error.body?.message ??
        error.statusText ??
        'Unknown error';
      alertDialog({
        title: 'Error updating table',
        description: message,
        showCancelButton: false,
      });
    },
  });
};

export const useGetTable = (tableKey: string, optins?: Object) => {
  const {
    data: table,
    isLoading: isLoadingTable,
    refetch: loadTable,
  } = useGetApiTablesTableKey(tableKey, optins);
  return { table, isLoadingTable, loadTable };
};

export const useDeleteTable = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { alertDialog } = useAlertDialog();
  return useMutation({
    mutationFn: (data: { tableKey: string }) => {
      return deleteApiTablesTableKey(data.tableKey);
    },
    onSuccess: (data, variables) => {
      toast.success('Table deleted successfully');
    },
    onError: (error: any) => {
      console.error('Error deleting table:', error);
      const message =
        error.body?.errors?.json?.message?.[0] ??
        error.body?.message ??
        error.statusText ??
        'Unknown error';
      alertDialog({
        title: 'Error deleting table',
        description: message,
        showCancelButton: false,
      });
    },
  });
};

export const useGetTablePlayer = (tableKey: string, optins?: Object) => {
  const {
    data,
    isLoading: isLoadingPlayers,
    refetch: loadPlayers,
  } = useGetApiTablesTableKeyPlayers(tableKey, optins);
  const players = data?.table_players;
  return { players, isLoadingPlayers, loadPlayers };
};

export const useAddTablePlayer = () => {
  const { alertDialog } = useAlertDialog();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { tableKey: string; tablePlayersItem: TablePlayerItem[] }) => {
      return postApiTablesTableKeyPlayers(data.tableKey, { players: data.tablePlayersItem });
    },
    onSuccess: (data, variables) => {
      toast.success('Players added to table successfully');
      // キャッシュ更新
      const queryKey = getGetApiTablesTableKeyPlayersQueryKey(variables.tableKey);
      queryClient.invalidateQueries({ queryKey });
    },
    onError: (error: any) => {
      console.error('Error adding players to table:', error);
      const message =
        error.body?.errors?.json?.message?.[0] ??
        error.body?.message ??
        error.statusText ??
        'Unknown error';
      alertDialog({
        title: 'Error adding players to table',
        description: message,
        showCancelButton: false,
      });
    },
  });
};

export const useDeleteTablePlayer = () => {
  const { alertDialog } = useAlertDialog();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { tableKey: string; playerId: number }) => {
      return deleteApiTablesTableKeyPlayersPlayerId(data.tableKey, data.playerId);
    },
    onSuccess: (data, variables) => {
      toast.success('Players removed from table successfully');
      // キャッシュ更新
      const queryKey = getGetApiTablesTableKeyPlayersQueryKey(variables.tableKey);
      queryClient.invalidateQueries({ queryKey });
    },
    onError: (error: any) => {
      console.error('Error removing players from table:', error);
      const message =
        error.body?.errors?.json?.message?.[0] ??
        error.body?.message ??
        error.statusText ??
        'Unknown error';
      alertDialog({
        title: 'Error removing players from table',
        description: message,
        showCancelButton: false,
      });
    },
  });
};

export const usedDeleteChipTableWithScores = () => {
  // チップテーブルのスコアデータとテーブル自体を削除する。
  const { mutateAsync: deleteScores } = useDeleteGame();

  return useMutation({
    mutationFn: async (tableKey: string) => {
      // 1. まず、該当テーブルの全ゲームを取得
      const games = await getApiTablesTableKeyGames(tableKey);
      // 2. 各ゲームを削除
      for (const game of games) {
        if (game.id) {
          await deleteScores({ tableKey, gameId: game.id });
        }
      }
      // 3. 最後にテーブル自体を削除
      return deleteApiTablesTableKey(tableKey);
    },
    onSuccess: () => {
      toast.success('Table deleted successfully');
    },
    onError: (error: any) => {
      console.error('Error deleting table:', error);
      const message =
        error.body?.errors?.json?.message?.[0] ??
        error.body?.message ??
        error.statusText ??
        'Unknown error';
      toast.error(message);
    },
  });
};
