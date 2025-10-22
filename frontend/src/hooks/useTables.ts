import {
  postApiTournamentsTournamentKeyTables,
  useGetApiTournamentsTournamentKeyTables,
} from '@/api/generated/mahjongApi';
import type { TableCreate } from '@/api/generated/mahjongApi.schemas';
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
