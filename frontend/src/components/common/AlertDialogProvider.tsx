// src/components/common/AlertDialogProvider.tsx
'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogCancel,
  AlertDialogAction,
} from '@/components/ui/alert-dialog';

type AlertDialogOptions = {
  title?: string;
  description?: string;
  confirmText?: string;
  cancelText?: string;
  showCancelButton?: boolean;
};

type AlertDialogContextType = {
  alertDialog: (options: AlertDialogOptions) => Promise<boolean>;
};

const AlertDialogContext = createContext<AlertDialogContextType | undefined>(undefined);

export const AlertDialogProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [options, setOptions] = useState<AlertDialogOptions>({});
  const [resolver, setResolver] = useState<(value: boolean) => void>(() => () => {});

  const alertDialog = useCallback((opts: AlertDialogOptions) => {
    setOptions(opts);
    setIsOpen(true);
    return new Promise<boolean>((resolve) => {
      setResolver(() => resolve);
    });
  }, []);

  const handleConfirm = () => {
    setIsOpen(false);
    resolver(true);
  };

  const handleCancel = () => {
    setIsOpen(false);
    resolver(false);
  };

  return (
    <AlertDialogContext.Provider value={{ alertDialog }}>
      {children}
      <AlertDialog open={isOpen} onOpenChange={setIsOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{options.title ?? '確認'}</AlertDialogTitle>
            <AlertDialogDescription>{options.description ?? ''}</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            {options.showCancelButton !== false && (
              <AlertDialogCancel onClick={handleCancel}>
                {options.cancelText ?? 'キャンセル'}
              </AlertDialogCancel>
            )}
            <AlertDialogAction onClick={handleConfirm}>
              {options.confirmText ?? 'OK'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </AlertDialogContext.Provider>
  );
};

export const useAlertDialog = () => {
  const ctx = useContext(AlertDialogContext);
  if (!ctx) throw new Error('useAlertDialog must be used within AlertDialogProvider');
  return ctx;
};
