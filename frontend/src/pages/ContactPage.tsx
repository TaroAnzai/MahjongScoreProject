import PageTitleBar from '@/components/PageTitleBar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Spinner } from '@/components/ui/spinner';
import { Textarea } from '@/components/ui/textarea';
import { useCreateContact } from '@/hooks/useContact';
import { getRecaptchaToken } from '@/utils/recaptcha';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { z } from 'zod';

export default function ContactPage() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { mutate: createContact, isPending, isSuccess } = useCreateContact();
  const [errors, setErrors] = useState({
    name: '',
    email: '',
    subject: '',
    message: '',
  });
  const [form, setForm] = useState({
    name: '',
    email: '',
    subject: '',
    message: '',
  });
  useEffect(() => {
    if (isSuccess) {
      navigate(-1);
    }
  }, [isSuccess]);
  const schema = z.object({
    name: z.string().min(1, t('contact.errors.nameRequired')),
    email: z.email(t('contact.errors.invalidEmail')),
    subject: z.string().min(1, t('contact.errors.subjectRequired')),
    message: z.string().min(1, t('contact.errors.messageRequired')),
  });
  const isFormValid =
    errors.name === '' &&
    errors.email === '' &&
    errors.subject === '' &&
    errors.message === '' &&
    form.name !== '' &&
    form.email !== '' &&
    form.subject !== '' &&
    form.message !== '';
  const handleChange =
    (key: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      const newForm = { ...form, [key]: e.target.value };
      setForm(newForm);

      const result = schema.safeParse(newForm);

      if (!result.success) {
        const fieldErrors = result.error.flatten().fieldErrors;
        setErrors({
          name: fieldErrors.name?.[0] ?? '',
          email: fieldErrors.email?.[0] ?? '',
          subject: fieldErrors.subject?.[0] ?? '',
          message: fieldErrors.message?.[0] ?? '',
        });
      } else {
        setErrors({
          name: '',
          email: '',
          subject: '',
          message: '',
        });
      }
    };
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = await getRecaptchaToken('create_contact');
    createContact({ ...form, recaptcha_token: token });
  };

  return (
    <div className="mahjong-container">
      <PageTitleBar title={t('contactPage.title')} showBackButton />
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="font-semibold">{t('contactPage.name')}</label>
          <Input value={form.name} onChange={handleChange('name')} required />
          {errors.name && <span className="text-red-500">{errors.name}</span>}
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

        <Button type="submit" className="w-full" disabled={isPending || !isFormValid}>
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
