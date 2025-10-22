import {
  getGetApiTablesTableKeyQueryOptions,
  postApiTournamentsTournamentKeyTables,
  putApiTablesTableKey,
  useGetApiTablesTableKey,
  useGetApiTablesTableKeyPlayers,
  useGetApiTournamentsTournamentKeyTables,
} from '@/api/generated/mahjongApi';
import type { TableCreate, TableUpdate } from '@/api/generated/mahjongApi.schemas';
import { Mutation, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

export const useGetTables = (tournamentKey: string) => {
  const {
    data: tables,
    isLoading: isLoadingTables,
    refetch: loadTables,
  } = useGetApiTournamentsTournamentKeyTables(tournamentKey);
  return { tables, isLoadingTables, loadTables };
};

export const useCreateTable = () => {
  const navigate = useNavigate();
  return useMutation({
    mutationFn: (data: { tournamentKey: string; tableCreate: TableCreate }) => {
      return postApiTournamentsTournamentKeyTables(data.tournamentKey, data.tableCreate);
    },
    onSuccess: (data, variables) => {
      toast.success('Table created successfully');
      // 遷移
      navigate(`/table/${variables.tournamentKey}`);
    },
    onError: (error) => {
      console.error('Error creating table:', error);
      toast.error('Error creating table');
    },
  });
};

export const useUpdateTable = () => {
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
    onError: (error) => {
      console.error('Error updating table:', error);
      toast.error('Error updating table');
    },
  });
};

export const useGetTable = (tableKey: string) => {
  const {
    data: table,
    isLoading: isLoadingTable,
    refetch: loadTable,
  } = useGetApiTablesTableKey(tableKey);
  return { table, isLoadingTable, loadTable };
};

export const useGetTablePlayer = (tableKey: string) => {
  const {
    data: players,
    isLoading: isLoadingPlayers,
    refetch: loadPlayers,
  } = useGetApiTablesTableKeyPlayers(tableKey);
  return { players, isLoadingPlayers, loadPlayers };
};
