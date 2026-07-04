import { defineConfig } from 'vite';
import { VitePWA } from 'vite-plugin-pwa';

const apiTarget = process.env.VITE_API_TARGET ?? 'http://localhost:8000';

export default defineConfig({
  server: {
    proxy: {
      '/auth'    : apiTarget,
      '/user'    : apiTarget,
      '/qr_code' : apiTarget,
    },
  },
  plugins: [
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['icons/apple-touch-icon.png'],
      manifest: {
        name: 'qr/studio',
        short_name: 'qr/studio',
        description: 'Менеджер QR-кодов',
        lang: 'ru',
        display: 'standalone',
        start_url: '/',
        theme_color: '#14100C',
        background_color: '#FAF5EE',
        icons: [
          { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png' },
          { src: '/icons/icon-512-maskable.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        navigateFallback: '/index.html',
        // API must never be served from cache: auth tokens and QR CRUD go network-only,
        // except QR images, which are immutable per id and safe to serve stale.
        navigateFallbackDenylist: [/^\/(qr_code|auth|user)/],
        runtimeCaching: [
          {
            urlPattern: /\/qr_code\/[^/]+\/image$/,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'qr-images',
              expiration: { maxEntries: 100, maxAgeSeconds: 60 * 60 * 24 * 30 },
            },
          },
          {
            urlPattern: /\/(qr_code|auth|user)(\/|$)/,
            handler: 'NetworkOnly',
          },
          {
            urlPattern: /^https:\/\/fonts\.(googleapis|gstatic)\.com\/.*/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'google-fonts',
              expiration: { maxEntries: 30, maxAgeSeconds: 60 * 60 * 24 * 365 },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
        ],
      },
    }),
  ],
});
