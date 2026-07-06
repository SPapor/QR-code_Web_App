import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    // ui.ts pulls in i18n, which reads localStorage/navigator at import time
    environment: 'happy-dom',
  },
});
