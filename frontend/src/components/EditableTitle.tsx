// src/components/EditableTitle.jsx
import React, { useState } from 'react';
import styles from './EditableTitle.module.css';

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
    <div className={`${styles.wrapper} ${className}`} onClick={handleStartEdit}>
      {editing ? (
        <input
          type="text"
          className={styles.input}
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
