import { cva } from 'class-variance-authority';

export const containerVariants = cva(
  'relative mx-auto box-border w-full max-w-content min-w-0 px-2 py-4 text-center text-foreground'
);

export const sectionVariants = cva(
  'mb-6 items-center justify-between rounded-panel border bg-surface-strong p-4'
);

export const appButtonVariants = cva(
  'relative my-[5px] block w-full cursor-pointer overflow-hidden min-h-12 rounded-control border border-transparent bg-action px-5 py-3 text-base font-semibold text-white shadow-control transition-colors duration-200 hover:opacity-90 active:opacity-75 disabled:cursor-not-allowed disabled:border-white/20 disabled:bg-action-disabled disabled:text-[var(--color-disabled-text)] disabled:opacity-60 disabled:shadow-none disabled:transition-none'
);

export const appInputVariants = cva(
  'box-border h-full w-full overflow-hidden text-ellipsis min-h-12 rounded-control border bg-surface px-3 py-2 text-inherit text-foreground focus:border-ring disabled:cursor-default disabled:border-0 disabled:bg-transparent disabled:text-foreground'
);

export const appListVariants = cva('m-0 flex w-full list-none flex-col gap-3 p-0');
export const appListItemVariants = cva('min-h-14 overflow-hidden rounded-control border bg-surface px-4 py-3 text-left text-list font-semibold text-foreground');
