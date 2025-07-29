import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [vue()],
    build: {
        outDir: "build",
        rollupOptions: {
            input: "index.html",
            output: {
                entryFileNames: "bundle.js",
                assetFileNames: (assetInfo) => {
                    const info = assetInfo.name!.split(".");
                    const extType = info[info.length - 1];
                    if (/\.(css)$/.test(assetInfo.name!)) return "bundle.css";
                    return `[name].${extType}`;
                },
            },
        },
        target: "es2015",
    },
    define: {
        global: "globalThis",
    },
    server: {
        port: 3001,
    },
    base: "./", // This ensures relative paths in the built HTML
});
