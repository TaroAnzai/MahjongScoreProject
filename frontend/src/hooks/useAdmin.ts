import { postApiAdminLogin, useGetApiAdminMe } from '@/api/generated/adminApi';
import { useMutation } from '@tanstack/react-query';
import { data } from 'react-router-dom';

export const useCheckAdmin = () => {
  const { data: isAdmin, isLoading, refetch } = useGetApiAdminMe();
  return { isAdmin, isLoading, refetch };
};

export const useAdminLogin = () => {
  return useMutation({
    mutationFn: (data: { username: string; password: string }) => {
      return postApiAdminLogin({ username: data.username, password: data.password });
    },
    onSuccess: () => {
      console.log('Admin login successful');
    },
    onError: (error) => {
      console.log('Admin login failed', error);
    },
  });
};
