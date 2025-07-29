/* eslint-env node */
module.exports = {
    env: {
        browser: true,
        es2020: true,
    },
    extends: [
        'eslint:recommended',
        'plugin:@typescript-eslint/eslint-recommended',
        'plugin:prettier/recommended',
        'plugin:sonarjs/recommended',
        'plugin:jsdoc/recommended',
    ],
    parser: '@typescript-eslint/parser',
    parserOptions: {
        ecmaVersion: 2020,
        sourceType: 'module',
    },
    plugins: [
        '@typescript-eslint',
        'prettier',
        'sonarjs',
        'jsdoc',
        'prefer-arrow',
    ],
    settings: {
        react: {
            version: '16.14',
            pragma: 'h',
        },
    },
    rules: {
        quotes: ['warn', 'single', { avoidEscape: true }],
        semi: ['warn', 'always'],
        'prettier/prettier': ['warn', { arrowParens: 'avoid' }],
        '@typescript-eslint/no-unused-vars': 'warn',
        '@typescript-eslint/array-type': [
            'warn',
            {
                default: 'array-simple',
            },
        ],
        '@typescript-eslint/consistent-type-assertions': 'warn',
        '@typescript-eslint/no-explicit-any': 'off',
        '@typescript-eslint/prefer-for-of': 'warn',
        '@typescript-eslint/prefer-function-type': 'warn',
        '@typescript-eslint/unified-signatures': 'warn',
        '@typescript-eslint/no-unused-expressions': 'warn',
        'no-unused-vars': 'off',
        camelcase: 1,
        'comma-dangle': [
            'warn',
            {
                arrays: 'always-multiline',
                functions: 'never',
                objects: 'always-multiline',
                imports: 'always-multiline',
                exports: 'always-multiline',
            },
        ],
        curly: 'warn',
        'default-case': 'warn',
        eqeqeq: ['warn', 'always'],
        'guard-for-in': 'warn',
        'id-match': 'warn',
        'jsdoc/check-indentation': 'warn',
        'jsdoc/require-jsdoc': 'off',
        'jsdoc/no-undefined-types': 'off',
        'jsdoc/check-tag-names': 'off',
        'max-classes-per-file': ['warn', 1],
        'no-bitwise': 'warn',
        'no-caller': 'warn',
        'no-console': 'warn',
        'no-duplicate-imports': 'warn',
        'no-eval': 'warn',
        'no-extra-bind': 'warn',
        '@typescript-eslint/no-magic-numbers': [
            'warn',
            {
                ignore: [-1, 0, 1],
                ignoreArrayIndexes: true,
                ignoreEnums: true,
                ignoreReadonlyClassProperties: true,
            },
        ],
        'no-new-func': 'warn',
        'no-new-wrappers': 'warn',
        'no-return-await': 'warn',
        'no-sequences': 'warn',
        'no-template-curly-in-string': 'warn',
        'no-throw-literal': 'warn',
        'no-underscore-dangle': 'warn',
        'no-var': 'warn',
        'object-shorthand': ['warn', 'never'],
        'one-var': ['warn', 'never'],
        'padding-line-between-statements': [
            'warn',
            { blankLine: 'always', prev: '*', next: 'return' },
            { blankLine: 'always', prev: '*', next: 'function' },
            {
                blankLine: 'always',
                prev: 'multiline-block-like',
                next: '*',
            },
        ],
        'prefer-arrow/prefer-arrow-functions': [
            'warn',
            {
                allowStandaloneDeclarations: true,
            },
        ],
        'prefer-const': 'warn',
        'prefer-object-spread': 'warn',
        radix: 'warn',
        'sonarjs/no-duplicate-string': 'warn',
        'sonarjs/cognitive-complexity': 'warn',
        'sonarjs/prefer-single-boolean-return': 'warn',
        'spaced-comment': [
            'warn',
            'always',
            {
                markers: ['/'],
            },
        ],
    },
    overrides: [
        {
            files: ['./*.js'],
            rules: {
                'no-unused-vars': 'warn',
                'sonarjs/no-duplicate-string': 'off',
            },
        },
        {
            files: ['src/**/*.spec.{ts,tsx}'],
            rules: {
                '@typescript-eslint/no-magic-numbers': 'off',
            },
        },
        {
            files: ['./*.ts'],
            rules: {
                'sonarjs/no-duplicate-string': 'off',
            },
        },
        {
            files: ['src/**/*.{ts,tsx}'],
            parser: '@typescript-eslint/parser',
            parserOptions: {
                parserOption: {
                    jsx: true,
                },
                project: 'tsconfig.json',
            },
            rules: {
                '@typescript-eslint/dot-notation': 'warn',
                '@typescript-eslint/no-shadow': 'warn',
                'no-console': 'off',
                'no-shadow': 'off',
            },
        },
        {
            files: [
                'src/examples/*.{ts,tsx}',
                'src/components/**/examples/*.{ts,tsx}',
                'src/components/**/examples/**/*.{ts,tsx}',
                'src/**/*.spec.{ts,tsx}',
                'src/**/*.test-wrapper.{ts,tsx}',
            ],
            parserOptions: {
                parserOption: {
                    jsx: true,
                },
                project: 'tsconfig.lint.json',
            },
            rules: {
                '@typescript-eslint/dot-notation': 'warn',
                'sonarjs/no-duplicate-string': 'off',
                'sonarjs/no-identical-functions': 'off',
                'jsdoc/require-returns': 'off',
                'jsdoc/require-param': 'off',
                'no-console': 'off',
                'no-magic-numbers': 'off',
                'prefer-arrow/prefer-arrow-functions': 'off',
            },
        },
    ],
};
