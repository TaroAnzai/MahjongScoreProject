import PageTitleBar from '@/components/PageTitleBar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Spinner } from '@/components/ui/spinner';
import { Textarea } from '@/components/ui/textarea';
import { useCreateContact } from '@/hooks/useContact';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

export default function ContactPage() {
  const { t } = useTranslation();
  const { mutate: createContact, isPending } = useCreateContact();
  const [form, setForm] = useState({
    name: '',
    email: '',
    subject: '',
    message: '',
  });
  const handleChange =
    (key: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      setForm({ ...form, [key]: e.target.value });
    };
  const handleSubmit = (e: React.FormEvent) => {};
  return (
    <div className="mahjong-container">
      <PageTitleBar title={t('contactPage.title')} parentUrl="/" />
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="font-semibold">{t('contactPage.name')}</label>
          <Input value={form.name} onChange={handleChange('name')} required />
        </div>

        <div>
          <label className="font-semibold">{t('contactPage.email')}</label>
          <Input type="email" value={form.email} onChange={handleChange('email')} required />
        </div>

        <div>
          <label className="font-semibold">{t('contactPage.subject')}</label>
          <Input value={form.subject} onChange={handleChange('subject')} required />
        </div>

        <div>
          <label className="font-semibold">{t('contactPage.message')}</label>
          <Textarea value={form.message} onChange={handleChange('message')} required />
        </div>

        <Button type="submit" className="w-full" disabled={isPending}>
          {isPending ? (
            <>
              <Spinner className="mr-2 h-4 w-4" />
              {t('contactPage.sending')}
            </>
          ) : (
            t('contactPage.send')
          )}
        </Button>
      </form>
    </div>
  );
}
