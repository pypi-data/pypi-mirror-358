import { EsignHandler } from './esign.handler';
import { EsignCommand } from './esign.command';

describe('EsignHandler', () => {
    it('runs', () => {
        const handler = new EsignHandler();

        handler.handle(new EsignCommand());
    });
});
