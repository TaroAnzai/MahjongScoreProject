import { useGetApiAdminMe } from '@/api/generated/adminApi';

export const useCheckAdmin = () => {
  const {} = useGetApiAdminMe();
};
