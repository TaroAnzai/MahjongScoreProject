import React from 'react';
interface ButtonGridSectionProps {
  children?: React.ReactNode;
}
function ButtonGridSection({ children }: ButtonGridSectionProps) {
  return (
    <div className="mb-6 grid grid-cols-2 items-center justify-between gap-3 rounded-panel border bg-surface-strong px-2.5 py-4 shadow-inset">
      {React.Children.map(children, (child, index) => (
        <div className="flex justify-center last:odd:col-span-2" key={index}>
          {child}
        </div>
      ))}
    </div>
  );
}

export default ButtonGridSection;
