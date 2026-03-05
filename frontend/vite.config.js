import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'node:url';
export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url)),
        },
    },
    build: {
        target: 'es2020',
        rollupOptions: {
            output: {
                manualChunks: function (id) {
                    if (id.includes('node_modules/vue/') || id.includes('node_modules/vue-router/') || id.includes('node_modules/pinia/'))
                        return 'vue-vendor';
                    if (id.includes('node_modules/naive-ui/'))
                        return 'naive-ui';
                    return undefined;
                },
                chunkFileNames: 'assets/[name]-[hash].js',
                entryFileNames: 'assets/[name]-[hash].js',
                assetFileNames: 'assets/[name]-[hash][extname]',
            },
        },
        minify: 'esbuild',
        cssCodeSplit: true,
    },
    server: {
        port: 5173,
        proxy: {
            // 必须优先代理 /api（含 POST），避免被 SPA fallback 拦截导致 405
            '/api': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
                configure: function (proxy) {
                    proxy.on('error', function (err, req, res) {
                        console.warn('[Vite proxy] /api error:', err.message);
                    });
                },
            },
        },
    },
});
