// src/components/SelectorModal.jsx
import React from 'react';
import Modal from './Modal';
import styles from './SelectorModal.module.css';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { Button } from './ui/button';

interface SelectorModalProps {
  title: string;
  open: boolean;
  items: any[];
  onSelect: (item: any) => void;
  onClose: () => void;
  plusDisplayItem?: string | null;
}
function SelectorModal({
  title,
  items,
  open,
  onSelect,
  onClose,
  plusDisplayItem = null,
}: SelectorModalProps) {
  return (
    <Dialog open={open}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>選択してください</DialogDescription>
        </DialogHeader>
        <ul className={styles.list}>
          {items.map((item) => (
            <li key={item.id} className={styles.listItem} onClick={() => onSelect(item)}>
              <div>{item.name}</div>
              {plusDisplayItem && <div>{item[plusDisplayItem]}</div>}
            </li>
          ))}
        </ul>
        <DialogFooter>
          <Button onClick={onClose}> 閉じる</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default SelectorModal;
