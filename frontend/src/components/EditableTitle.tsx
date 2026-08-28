// src/components/EditableTitle.jsx
import React, { useState } from 'react';
import { cn } from '@/lib/utils';

interface EditableTitleProps {
  value: string;
  onChange?: (newValue: string) => void;
  className?: string;
}
function EditableTitle({ value, onChange, className = '' }: EditableTitleProps) {
  const [editing, setEditing] = useState(false);
  const [tempValue, setTempValue] = useState(value);

  const handleStartEdit = () => {
    setTempValue(value);
    setEditing(true);
  };

  const handleFinishEdit = () => {
    setEditing(false);
    if (tempValue.trim() && tempValue !== value) {
      onChange?.(tempValue.trim());
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleFinishEdit();
    if (e.key === 'Escape') setEditing(false);
  };

  return (
    <div className={cn('pointer-events-auto cursor-pointer', className)} onClick={handleStartEdit}>
      {editing ? (
        <input
          type="text"
          className="box-border w-full px-1.5 py-0.5 text-[1em]"
          value={tempValue}
          onChange={(e) => setTempValue(e.target.value)}
          onBlur={handleFinishEdit}
          onKeyDown={handleKeyDown}
          autoFocus
        />
      ) : (
        value
      )}
    </div>
  );
}

export default EditableTitle;
