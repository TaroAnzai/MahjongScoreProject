import React from 'react';
import styles from './ButtonGridSection.module.css';
interface ButtonGridSectionProps {
  children?: React.ReactNode;
}
function ButtonGridSection({ children }: ButtonGridSectionProps) {
  return (
    <div className={`${styles.gridSection} mahjong-section`}>
      {React.Children.map(children, (child, index) => (
        <div className={styles.gridItem} key={index}>
          {child}
        </div>
      ))}
    </div>
  );
}

export default ButtonGridSection;
