import { Config } from '@stencil/core';
import { OutputTargetDist } from '@stencil/core/internal';
import { sass } from '@stencil/sass';

const targetDist: OutputTargetDist = {
    type: 'dist',
    copy: [],
};

export const config: Config = {
    namespace: 'limepkg-scrive-lwc-components',
    outputTargets: [targetDist],
    plugins: [sass()],
    testing: {
        browserArgs: ['--no-sandbox', '--disable-setuid-sandbox'],
    },
};
