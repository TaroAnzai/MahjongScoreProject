import type { Contact } from '@/api/generated/adminApi.schemas';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { useDeleteContact, useGetContactsList } from '@/hooks/useContact';

export function AdminContact() {
  const { contactList, isLoading, refetch } = useGetContactsList();
  const { mutate: deleteContact, isSuccess } = useDeleteContact();
  const handleDelete = (contactId: number) => () => {
    deleteContact({ id: contactId });
  };
  return (
    <div className="mahjong-container max-w-1000! ">
      <h1 className="text-2xl font-bold mt-5">Contact Admin</h1>
      <div>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[100px]">ID</TableHead>
              <TableHead>ID</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Email</TableHead>
              <TableHead>Subject</TableHead>
              <TableHead>Message</TableHead>
              <TableHead>Satus</TableHead>
              <TableHead>Updated At</TableHead>
              <TableHead>Created At</TableHead>
              <TableHead>IP Address</TableHead>
              <TableHead>User Agent</TableHead>
              <TableHead>Delete</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {contactList?.map((contact: Contact) => (
              <TableRow key={contact.id}>
                <TableCell className="font-medium">{contact.id}</TableCell>
                <TableCell>{contact.id}</TableCell>
                <TableCell>{contact.name}</TableCell>
                <TableCell>{contact.email}</TableCell>
                <TableCell>{contact.subject}</TableCell>
                <TableCell>{contact.message}</TableCell>
                <TableCell>{contact.status}</TableCell>
                <TableCell>{contact.updated_at?.split('T')[0]}</TableCell>
                <TableCell>{contact.created_at?.split('T')[0]}</TableCell>
                <TableCell>{contact.ip_address}</TableCell>
                <TableCell>{contact.user_agent}</TableCell>
                <TableCell>
                  <Button size="sm" className="sm" onClick={handleDelete(contact.id!)}>
                    Delete
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
