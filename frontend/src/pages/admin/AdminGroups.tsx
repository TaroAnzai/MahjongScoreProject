import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  useAdminDeleteGroup,
  useAdminGetGroups,
  useAdminLogout,
  useCheckAdmin,
} from '@/hooks/useAdmin';
import { useNavigate } from 'react-router-dom';
import { is } from 'zod/v4/locales';

export function AdminGroups() {
  const { groups, isLoading, refetch: refetchGroups } = useAdminGetGroups();
  const { mutate: deleteGroup, isSuccess } = useAdminDeleteGroup();

  const handleDelete = (GroupKey: string | undefined) => () => {
    if (!GroupKey) return;
    deleteGroup({ groupKey: GroupKey });
  };
  return (
    <div className="mahjong-container max-w-1000! ">
      <Table className="mt-5">
        <TableHeader>
          <TableRow>
            <TableHead className="w-[100px]">ID</TableHead>
            <TableHead>Group Name</TableHead>
            <TableHead>Created At</TableHead>
            <TableHead>Last Updated</TableHead>
            <TableHead>Email</TableHead>
            <TableHead>Delete</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {groups?.map((group) => (
            <TableRow key={group.id}>
              <TableCell className="font-medium">{group.id}</TableCell>
              <TableCell>{group.name}</TableCell>
              <TableCell>{group.created_at?.split('T')[0]}</TableCell>
              <TableCell>{group.last_updated_at?.split('T')[0]}</TableCell>
              <TableCell>{group.email}</TableCell>
              <TableCell>
                <Button
                  size="sm"
                  className="sm"
                  onClick={handleDelete(
                    group.group_links?.find((link) => link.access_level === 'OWNER')?.short_key
                  )}
                >
                  Delete
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
