import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Check, Copy } from 'lucide-react';
import { QRCodeSVG } from 'qrcode.react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';

interface ShareUrlDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  shareUrl: string;
  typeName: string;
}

function ShareUrlDialog({ open, onOpenChange, shareUrl, typeName }: ShareUrlDialogProps) {
  const { t } = useTranslation();
  const [copyError, setCopyError] = useState('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (open) {
      setCopyError('');
      setCopied(false);
    }
  }, [open, shareUrl]);

  const copyUrl = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setCopyError('');
    } catch (error) {
      setCopied(false);
      setCopyError(error instanceof Error ? error.message : t('titleBar.shareCopyError'));
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent showCloseButton={false}>
        <DialogHeader>
          <DialogTitle>{t('titleBar.shareDialogTitle', { typeName })}</DialogTitle>
          <DialogDescription>{t('titleBar.shareDialogDescription')}</DialogDescription>
        </DialogHeader>

        <div className="flex justify-center rounded-md bg-white p-4">
          <QRCodeSVG
            value={shareUrl}
            size={220}
            level="M"
            title={t('titleBar.shareQrCodeTitle', { typeName })}
          />
        </div>

        <div className="flex gap-2">
          <Input value={shareUrl} readOnly aria-label={t('titleBar.shareUrlLabel')} />
          <Button
            type="button"
            variant="outline"
            size="icon"
            onClick={copyUrl}
            title={t('titleBar.copyUrl')}
          >
            {copied ? <Check /> : <Copy />}
            <span className="sr-only">{t('titleBar.copyUrl')}</span>
          </Button>
        </div>
        {copyError && <p className="text-destructive text-sm">{copyError}</p>}

        <DialogFooter>
          <Button type="button" onClick={() => onOpenChange(false)}>
            {t('Common.close')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default ShareUrlDialog;
