import React from 'react';
import styles from './ButtonGridSection.module.css';

function ButtonGridSection({ children }) {
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
