import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    proxy: {
      '/auth'    : 'http://localhost:8001',
      '/user'    : 'http://localhost:8001',
      '/qr_code' : 'http://localhost:8001',
    },
  },
});
