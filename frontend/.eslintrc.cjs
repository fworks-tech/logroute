module.exports = {
  root: true,
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint', 'tsdoc'],
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
  ],
  rules: {
    'tsdoc/syntax': 'warn',
  },
  ignorePatterns: [
    'dist',
    'node_modules',
    '*.config.ts',
    '.eslintrc.cjs',
    'src/lib/api-client',
    'src/**/*.test.*',
    'src/**/*.spec.*',
  ],
  env: {
    browser: true,
    es2022: true,
  },
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module',
  },
};
