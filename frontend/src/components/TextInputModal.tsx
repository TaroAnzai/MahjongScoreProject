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
import { Label } from './ui/label';

interface TextInputModalProps {
  open: boolean;
  onComfirm: (inputText: string, inputText2?: string) => void;
  onClose: () => void;
  value?: string;
  title?: string;
  discription?: string;
  InputLabel?: string;
  twoInput?: boolean;
  twoInputLabel?: string;
}
export const TextInputModal = ({
  open,
  onComfirm,
  onClose,
  value,
  title,
  discription,
  InputLabel,
  twoInput = false,
  twoInputLabel = '',
}: TextInputModalProps) => {
  const [inputText, setInputText] = useState(value || '');
  const [inputText2, setInputText2] = useState(value || '');

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent showCloseButton={false}>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>{discription}</DialogDescription>
        </DialogHeader>
        <Label htmlFor="primaryInput">{InputLabel}</Label>
        <Input
          id="primaryInput"
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
        />
        {twoInput && (
          <>
            <Label htmlFor="twoInput">{twoInputLabel}</Label>
            <Input
              id="twoInput"
              type="text"
              value={inputText2}
              onChange={(e) => setInputText2(e.target.value)}
            />
          </>
        )}
        <DialogFooter>
          <Button onClick={() => onClose()}>キャンセル</Button>
          <Button onClick={() => onComfirm(inputText, inputText2)}>OK</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
