import { useEffect, useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { Input } from './ui/input';
import { Button } from './ui/button';

interface TextInputModalProps {
  open: boolean;
  onComfirm: (inputText: string) => void;
  onClose: () => void;
  value?: string;
  title?: string;
  discription?: string;
}
export const TextInputModal = ({
  open,
  onComfirm,
  onClose,
  value,
  title,
  discription,
}: TextInputModalProps) => {
  const [inputText, setInputText] = useState(value || '');
  useEffect(() => {
    setInputText(value || '');
  }, [value]);
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent showCloseButton={false}>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>{discription}</DialogDescription>
        </DialogHeader>
        <Input type="text" value={inputText} onChange={(e) => setInputText(e.target.value)} />
        <DialogFooter>
          <Button onClick={() => onClose()}>キャンセル</Button>
          <Button onClick={() => onComfirm(inputText)}>OK</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
