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
import { useTranslation } from 'react-i18next';

interface TextInputModalProps {
  open: boolean;
  onComfirm: (inputText: string, inputText2?: string) => void;
  onClose: () => void;
  value?: string;
  title?: string;
  discription?: string;
  InputLabel?: string;
  inputType?: React.InputHTMLAttributes<HTMLInputElement>['type'];
  twoInput?: boolean;
  twoInputLabel?: string;
  twoValue?: string;
  twoInputType?: React.InputHTMLAttributes<HTMLInputElement>['type'];
}
export const TextInputModal = ({
  open,
  onComfirm,
  onClose,
  value,
  title,
  discription,
  InputLabel,
  inputType = 'text',
  twoInput = false,
  twoInputLabel = '',
  twoValue = '',
  twoInputType = 'text',
}: TextInputModalProps) => {
  const { t } = useTranslation();
  const [inputText, setInputText] = useState(value || '');
  const [inputText2, setInputText2] = useState(twoValue || '');
  const isValidEmail = (value: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  const isPrimaryInputValid = inputType !== 'email' || isValidEmail(inputText);
  const isSecondInputValid = !twoInput || twoInputType !== 'email' || isValidEmail(inputText2);
  const canConfirm =
    inputText.trim() !== '' &&
    (!twoInput || inputText2.trim() !== '') &&
    isPrimaryInputValid &&
    isSecondInputValid;
  useEffect(() => {
    setInputText(value || '');
    setInputText2(twoValue || '');
  }, [value, twoValue, open]);

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
          type={inputType}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          aria-invalid={!isPrimaryInputValid}
        />
        {inputText && !isPrimaryInputValid && (
          <span className="text-sm text-red-500">{t('Common.invalidEmail')}</span>
        )}
        {twoInput && (
          <>
            <Label htmlFor="twoInput">{twoInputLabel}</Label>
            <Input
              id="twoInput"
              type={twoInputType}
              value={inputText2}
              onChange={(e) => setInputText2(e.target.value)}
              aria-invalid={!isSecondInputValid}
            />
            {inputText2 && !isSecondInputValid && (
              <span className="text-sm text-red-500">{t('Common.invalidEmail')}</span>
            )}
          </>
        )}
        <DialogFooter>
          <Button onClick={() => onClose()}>{t('Common.Cancel')}</Button>
          <Button disabled={!canConfirm} onClick={() => onComfirm(inputText, inputText2)}>
            OK
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
