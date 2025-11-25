import { useTranslation } from 'react-i18next';
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from '@/components/ui/dropdown-menu';
import { Link } from 'react-router-dom';
export const PageHeader = () => {
  const { t } = useTranslation();
  return (
    <div className="flex items-center justify-between max-w-[500px] mx-auto mb-1">
      <div className="ml-auto flex items-center">
        <Link
          to="/contact" // コンタクトページへのリンク
          className="cursor-pointer  hover:underline mr-4 text-sm" // リンクとして見せるためのスタイル
        >
          {t('contactPage.title')}
        </Link>
        <LanguageSelector />
      </div>
    </div>
  );
};

export function LanguageSelector() {
  const { i18n } = useTranslation();

  const changeLanguage = (lang: string) => {
    i18n.changeLanguage(lang);
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <span className="cursor-pointer select-none">🌐Language</span>
      </DropdownMenuTrigger>

      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => changeLanguage('ja')}>日本語</DropdownMenuItem>
        <DropdownMenuItem onClick={() => changeLanguage('en')}>English</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
