import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { useAdminDeleteGroup, useAdminGetGroups } from '@/hooks/useAdmin';
import type { ShareLink } from '@/api/generated/adminApi.schemas';
import { Copy, Share2 } from 'lucide-react';
import { QRCodeSVG } from 'qrcode.react';
import { useState } from 'react';
import { toast } from 'sonner';

const accessLevels = [
  { value: 'OWNER', label: 'Owner' },
  { value: 'EDIT', label: 'Edit' },
  { value: 'VIEW', label: 'View' },
] as const;

function buildGroupUrl(shortKey: string) {
  const shareOrigin = import.meta.env.DEV ? 'mahjongapp-dev:' : window.location.origin;

  return `${shareOrigin}${import.meta.env.BASE_URL}/group/${shortKey}`.replace(
    /([^:]\/)\/+/g,
    '$1'
  );
}

function ShareGroupButton({
  groupName,
  shareLinks = [],
}: {
  groupName: string;
  shareLinks?: readonly ShareLink[];
}) {
  const [selectedAccessLevel, setSelectedAccessLevel] = useState('VIEW');
  const selectedLink =
    shareLinks.find((link) => link.access_level === selectedAccessLevel) ?? shareLinks[0];

  if (!selectedLink) {
    return (
      <Button size="sm" variant="outline" disabled>
        <Share2 />
        Share
      </Button>
    );
  }

  const shareUrl = buildGroupUrl(selectedLink.short_key);
  const accessLabel =
    accessLevels.find((accessLevel) => accessLevel.value === selectedLink.access_level)?.label ??
    selectedLink.access_level;

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      toast.success('Link copied to clipboard');
    } catch {
      toast.error('Failed to copy link');
    }
  };

  const shareLink = async () => {
    try {
      await navigator.share({ title: `${groupName} (${accessLabel})`, url: shareUrl });
    } catch (error) {
      if (error instanceof DOMException && error.name === 'AbortError') return;
      toast.error('Failed to share link');
    }
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button size="sm" variant="outline">
          <Share2 />
          Share
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Share {groupName}</DialogTitle>
          <DialogDescription>
            Select an access level, then copy the link or scan the QR code.
          </DialogDescription>
        </DialogHeader>

        <div className="grid grid-cols-3 gap-2" aria-label="Access level">
          {accessLevels.map(({ value, label }) => {
            const hasLink = shareLinks.some((link) => link.access_level === value);
            return (
              <Button
                key={value}
                type="button"
                variant={selectedLink.access_level === value ? 'default' : 'outline'}
                disabled={!hasLink}
                onClick={() => setSelectedAccessLevel(value)}
              >
                {label}
              </Button>
            );
          })}
        </div>

        <div className="flex justify-center rounded-md bg-white p-4">
          <QRCodeSVG
            value={shareUrl}
            size={220}
            level="M"
            title={`${groupName} ${accessLabel} QR code`}
          />
        </div>

        <div className="flex gap-2">
          <Input value={shareUrl} readOnly aria-label={`${groupName} share link`} />
          <Button type="button" variant="outline" size="icon" onClick={copyLink} title="Copy link">
            <Copy />
            <span className="sr-only">Copy link</span>
          </Button>
        </div>

        {typeof navigator.share === 'function' && (
          <DialogFooter>
            <Button type="button" onClick={shareLink}>
              <Share2 />
              Share link
            </Button>
          </DialogFooter>
        )}
      </DialogContent>
    </Dialog>
  );
}

export function AdminGroups() {
  const { groups } = useAdminGetGroups();
  const { mutate: deleteGroup } = useAdminDeleteGroup();

  const handleDelete = (GroupKey: string | undefined) => () => {
    if (!GroupKey) return;
    deleteGroup({ groupKey: GroupKey });
  };
  return (
    <div className="relative mx-auto box-border w-full max-w-[1000px]! overflow-hidden rounded-container border-2 bg-surface p-2.5 text-center shadow-panel backdrop-blur-[var(--blur-surface)]">
      <Table className="mt-5">
        <TableHeader>
          <TableRow>
            <TableHead className="w-[100px]">ID</TableHead>
            <TableHead>Group Name</TableHead>
            <TableHead>Created At</TableHead>
            <TableHead>Last Updated</TableHead>
            <TableHead>Email</TableHead>
            <TableHead>Share</TableHead>
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
                <ShareGroupButton groupName={group.name} shareLinks={group.group_links} />
              </TableCell>
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
