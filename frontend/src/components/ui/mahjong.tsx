import { cva } from 'class-variance-authority';

export const containerVariants = cva(
  'relative mx-auto box-border w-full max-w-content overflow-hidden rounded-container border-2 bg-surface p-2.5 text-center shadow-panel backdrop-blur-[var(--blur-surface)]'
);

export const sectionVariants = cva(
  'mb-6 items-center justify-between rounded-panel border bg-surface-strong px-2.5 py-4 shadow-inset'
);

export const appButtonVariants = cva(
  'relative my-[5px] block w-full cursor-pointer overflow-hidden rounded-panel border bg-action p-2 text-base font-semibold text-white shadow-control transition-all duration-300 disabled:cursor-not-allowed disabled:border-white/20 disabled:bg-action-disabled disabled:text-[var(--color-disabled-text)] disabled:opacity-60 disabled:shadow-none disabled:transition-none'
);

export const appInputVariants = cva(
  'box-border h-full w-full overflow-hidden text-ellipsis border-2 bg-surface px-0.5 text-inherit text-white focus:border-[#4caf50] focus:shadow-[0_0_3px_rgba(76,175,80,0.5)] disabled:cursor-default disabled:border-0 disabled:bg-transparent disabled:text-white'
);

export const appListVariants = cva('m-0 list-none p-0');
export const appListItemVariants = cva('overflow-hidden text-ellipsis whitespace-nowrap text-list text-white');
