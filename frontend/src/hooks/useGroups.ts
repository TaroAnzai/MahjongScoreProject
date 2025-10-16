// src/hooks/useGroupQueries.ts
import { postApiGroups, putApiGroupsGroupKey, usePostApiGroups } from '@/api/generated/mahjongApi';
import type { Group, GroupCreate, GroupUpdate } from '@/api/generated/mahjongApi.schemas';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

import { useEffect, useMemo, useState } from 'react';
import { useQueries } from '@tanstack/react-query';
import { getGetApiGroupsGroupKeyQueryOptions } from '@/api/generated/mahjongApi';

/**
 * Hook to create a new group.
 *
 * @param onAfterCreate - Callback to be executed after the group is created successfully.
 * @returns A mutation object with the group creation mutation function, onSuccess callback, and onError callback.
 *
 * Usage example:
 * const { mutate: createGroup } = useCreateGroup();
 * const createGroupData = { name: 'My Group', description: 'This is my group.' };
 * createGroup(createGroupData).then((data) => console.log(data)).catch((error) => console.error(error));
 */
export const useCreateGroup = (onAfterCreate?: () => void) => {
  return useMutation({
    mutationFn: (data: GroupCreate) => {
      return postApiGroups(data);
    },
    onSuccess: (data: Group) => {
      console.log('Group created successfully:', data);
      localStorage.setItem(`group_key_${data.owner_link}`, data.owner_link ?? '');
      onAfterCreate?.();
    },
    onError: (error) => {
      console.error('Error creating group:', error);
    },
  });
};
export const useUpdateGroup = (onAfterUpdate?: () => void) => {
  return useMutation({
    mutationFn: (data: { groupKey: string; groupUpdate: GroupUpdate }) => {
      return putApiGroupsGroupKey(data.groupKey, data.groupUpdate);
    },
    onSuccess: (data: Group) => {
      console.log('Group updated successfully:', data);
      onAfterUpdate?.();
    },
    onError: (error) => {
      console.error('Error updating group:', error);
    },
  });
};
/**
 * LocalStorageの group_key_* を全て取得し、それぞれのグループデータをuseQueriesで取得する。
 * 成功・エラー時の処理も内部で行う。
 */

export const getKeyType = (data: Group): 'OWNER' | 'EDIT' | 'VIEW' | '' => {
  if (data.owner_link) return 'OWNER';
  if (data.edit_link) return 'EDIT';
  if (data.view_link) return 'VIEW';
  return '';
};
export const useGroupQueries = () => {
  const [refetchGroups, setRefetchGroups] = useState(0);

  // LocalStorageからGroup Keyを取得
  const groupKeys = useMemo(() => {
    console.log('🔁 start refetchGroups');
    const keys: string[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('group_key_')) {
        keys.push(key.replace('group_key_', ''));
      }
    }
    return keys;
  }, [refetchGroups]);

  // 各 group_key ごとにクエリを作成
  const groupQueries = useQueries({
    queries: groupKeys.map((key) => ({
      ...getGetApiGroupsGroupKeyQueryOptions(key),
      retry: 1,
      select: (data: Group) => ({
        ...data,
        keyType: getKeyType(data),
      }),
    })),
  });

  // クエリ結果監視
  useEffect(() => {
    groupQueries.forEach((query, index) => {
      const key = groupKeys[index];

      if (query.isError) {
        console.error(`Error fetching group ${key}:`, query.error);

        // 404エラーのときLocalStorageから削除
        if ((query.error as any)?.status === 404) {
          console.warn(`Group not found: ${key}, removing from localStorage`);
          localStorage.removeItem(`group_key_${key}`);
          setRefetchGroups((prev) => prev + 1);
        }
      }
    });
  }, [groupQueries, groupKeys]);
  const refetch = () => setRefetchGroups((prev) => prev + 1);
  // 返却値
  return {
    groupQueries,
    groupKeys,
    isLoading: groupQueries.some((q) => q.isLoading),
    groups: groupQueries.filter((q) => q.isSuccess).map((q) => q.data),
    refetch,
  };
};
