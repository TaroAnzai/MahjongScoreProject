import {
  deleteApiAdminGroupsGroupKey,
  getGetApiAdminGroupsQueryKey,
  postApiAdminLogin,
  postApiAdminLogout,
  useGetApiAdminGroups,
  useGetApiAdminMe,
} from '@/api/generated/adminApi';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { data } from 'react-router-dom';
import { toast } from 'sonner';

export const useCheckAdmin = () => {
  const { data: isAdmin, isLoading, refetch } = useGetApiAdminMe();
  return { isAdmin, isLoading, refetch };
};

export const useAdminLogin = () => {
  return useMutation({
    mutationFn: (data: { username: string; password: string }) => {
      return postApiAdminLogin({ username: data.username, password: data.password });
    },
    onSuccess: () => {},
    onError: (error) => {
      console.log('Admin login failed', error);
    },
  });
};

export const useAdminLogout = () => {
  return useMutation({
    mutationFn: () => {
      return postApiAdminLogout();
    },
    onSuccess: () => {
      console.log('Admin logged out');
    },
    onError: (error) => {
      console.log('Admin logout failed', error);
    },
  });
};

export const useAdminGetGroups = () => {
  const { data: groups, isLoading, refetch } = useGetApiAdminGroups();
  return { groups, isLoading, refetch };
};

export const useAdminDeleteGroup = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { groupKey: string }) => {
      return deleteApiAdminGroupsGroupKey(data.groupKey);
    },
    onSuccess: () => {
      const queryKey = getGetApiAdminGroupsQueryKey();
      queryClient.invalidateQueries({ queryKey });
      toast.success('Group deleted successfully');
    },
    onError: (error) => {
      console.log('Error deleting group', error);
    },
  });
};
