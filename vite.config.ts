import { defineConfig } from 'vite-plus';

export default defineConfig({
  fmt: {
    ignorePatterns: ['node_modules/**'],
    printWidth: 100,
    semi: true,
    singleQuote: true,
    sortPackageJson: true,
  },
});
