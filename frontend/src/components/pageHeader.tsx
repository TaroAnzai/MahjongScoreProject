export const PageHeader = () => {
  return (
    <div className="flex items-center justify-between max-w-[500px] mx-auto">
      <div className="ml-auto">
        <LanguageSelector />
      </div>
    </div>
  );
};

import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from '@/components/ui/dropdown-menu';

export function LanguageSelector() {
  const { i18n } = useTranslation();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost">🌐Langage</Button>
      </DropdownMenuTrigger>

      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => i18n.changeLanguage('ja')}>日本語</DropdownMenuItem>
        <DropdownMenuItem onClick={() => i18n.changeLanguage('en')}>English</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
