// src/components/SelectorModal.jsx
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { Button } from './ui/button';
import { useTranslation } from 'react-i18next';

interface SelectorModalProps {
  title: string;
  open: boolean;
  items: any[] | readonly any[] | undefined;
  onSelect: (item: any) => void;
  onClose: () => void;
  plusDisplayItem?: string | null;
  emptyMessage?: string;
}
function SelectorModal({
  title,
  items,
  open,
  onSelect,
  onClose,
  plusDisplayItem = null,
  emptyMessage,
}: SelectorModalProps) {
  const { t } = useTranslation();
  const msg = emptyMessage ?? t('Common.emptyMessage');
  return (
    <Dialog open={open}>
      <DialogContent showCloseButton={false}>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>{t('Common.Select')}</DialogDescription>
        </DialogHeader>
        {items === undefined || items.length === 0 ? (
          <div>{msg}</div>
        ) : (
          <ul className="m-0 inline-block w-full flex-1 list-none overflow-y-auto p-0">
            {items?.map((item) => (
              <li key={item.id} className="mb-2 cursor-pointer min-h-14 rounded-control border bg-surface px-4 py-3 text-left text-base font-semibold text-foreground transition-colors duration-200 hover:bg-accent" onClick={() => onSelect(item)}>
                <div>{item.name}</div>
                {plusDisplayItem && <div>{item[plusDisplayItem]}</div>}
              </li>
            ))}
          </ul>
        )}
        <DialogFooter>
          <Button onClick={onClose}> {t('Common.close')}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default SelectorModal;
