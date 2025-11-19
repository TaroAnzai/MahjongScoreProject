import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { useAdminDeleteGroup, useAdminGetGroups, useAdminLogout } from '@/hooks/useAdmin';
import { useNavigate } from 'react-router-dom';

export function AdminGroups() {
  const navigate = useNavigate();
  const { mutate: logout, isPending } = useAdminLogout();
  const { groups, isLoading, refetch: refetchGroups } = useAdminGetGroups();
  const { mutate: deleteGroup, isSuccess } = useAdminDeleteGroup();
  const handleLogout = () => {
    logout();
    navigate('/admin/login');
  };
  const handleDelete = (GroupKey: string | undefined) => () => {
    if (!GroupKey) return;
    deleteGroup({ groupKey: GroupKey });
  };
  return (
    <div className="mahjong-container max-w-1000! ">
      <div className="flex">
        <h1 className="absolute left-1/2 -translate-x-1/2">All Groups</h1>
        <Button className="ml-auto" onClick={() => handleLogout()}>
          Logout
        </Button>
      </div>

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
