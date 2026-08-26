import { appButtonVariants } from '@/components/ui/mahjong';
// src/components/MultiSelectorModal.jsx
import React, { useState } from 'react';
import Modal from './Modal';
import { useTranslation } from 'react-i18next';

interface multiSelectorModalProps<T extends { id: number | string }> {
  title: string;
  items: T[];
  onConfirm: (selectedItems: any[]) => void;
  onClose: () => void;
}

function MultiSelectorModal<T extends { id: number; name: string }>({
  title,
  items,
  onConfirm,
  onClose,
}: multiSelectorModalProps<T>) {
  const { t } = useTranslation();
  const [selectedIds, setSelectedIds] = useState<number[]>([]);

  const toggleSelect = (id: number) => {
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  };

  const handleConfirm = () => {
    const selectedItems = items.filter((item) => selectedIds.includes(item.id));
    onConfirm(selectedItems);
  };

  return (
    <Modal
      title={title}
      onClose={onClose}
      footer={
        <>
          <button
            className={$appButtonVariants()}
            onClick={handleConfirm}
            disabled={selectedIds.length === 0}
          >
            OK
          </button>
          <button className={$appButtonVariants()} onClick={onClose}>
            {' '}
            {t('Common.Cancel')}
          </button>
        </>
      }
    >
      <div className="flex-1 overflow-y-auto">
        {items.length === 0 && <p>{t('Common.emptyMessage')}</p>}
        <ul className="m-0 inline-block w-full flex-1 list-none overflow-y-auto p-0">
          {items.map((item) => (
            <li key={item.id} className="mb-4 text-list-large text-white">
              <label className="cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedIds.includes(item.id)}
                  onChange={() => toggleSelect(item.id)}
                />{' '}
                {item.name}
              </label>
            </li>
          ))}
        </ul>
      </div>
    </Modal>
  );
}

export default MultiSelectorModal;
