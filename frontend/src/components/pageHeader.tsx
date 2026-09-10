import { useTranslation } from 'react-i18next';
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from '@/components/ui/dropdown-menu';
import { Link, useLocation } from 'react-router-dom';
import { Globe, House, UserCog } from 'lucide-react';
import { useAdminLogout, useCheckAdmin } from '@/hooks/useAdmin';
export const PageHeader = () => {
  const { t } = useTranslation();
  const { pathname } = useLocation();
  const isAdminPage = pathname === '/admin' || pathname.startsWith('/admin/');
  const NavigationIcon = isAdminPage ? House : UserCog;
  const { isAdmin } = useCheckAdmin();
  const { mutate: logout, isPending } = useAdminLogout();

  const handleLogout = () => {
    logout();
  };
  return (
    <div className="flex items-center justify-between max-w-content mx-auto mb-2 min-h-12 px-2">
      <div className="flex items-center gap-2">
        <Link
          to={isAdminPage ? "/" : "/admin/"}
          aria-label={isAdminPage ? t("notFound.toHome") : t("navigation.admin")}
        >
          <NavigationIcon className="w-4 h-4 text-primary hover:text-link-hover" />
        </Link>
        {isAdmin && (
          <p
            className="cursor-pointer text-primary hover:text-link-hover hover:underline mr-4 text-sm"
            onClick={handleLogout}
          >
            Logout
          </p>
        )}
      </div>
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
        <span className="cursor-pointer select-none text-primary hover:text-link-hover text-sm leading-none flex items-center">
          <Globe className="inline-block w-4 h-4 mr-1" />
          Language
        </span>
      </DropdownMenuTrigger>

      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => changeLanguage('ja')}>日本語</DropdownMenuItem>
        <DropdownMenuItem onClick={() => changeLanguage('en')}>English</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
