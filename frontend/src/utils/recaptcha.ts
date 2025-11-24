declare global {
  interface Window {
    grecaptcha: {
      enterprise: {
        ready: (cb: () => void) => void;
        execute: (siteKey: string, options: { action: string }) => Promise<string>;
      };
    };
  }
}

export async function getRecaptchaToken(action: string): Promise<string> {
  const siteKey = import.meta.env.VITE_RECAPTCHA_SITE_KEY;

  return new Promise((resolve) => {
    const wait = () => {
      if (window.grecaptcha?.enterprise?.execute) {
        window.grecaptcha.enterprise.ready(async () => {
          const token = await window.grecaptcha.enterprise.execute(siteKey, { action });
          resolve(token);
        });
      } else {
        setTimeout(wait, 50);
      }
    };

    wait();
  });
}
