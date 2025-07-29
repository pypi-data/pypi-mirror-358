import { CommandHandler, Notifications } from '@limetech/lime-web-components';
import { EsignCommand } from './esign.command';

export class EsignHandler implements CommandHandler {
    constructor(private notifications: Notifications) {}
    public handle(command: EsignCommand) {
        const documentIds = command.filter.exp;
        console.log(command, documentIds);

        const isDocumentLimetype = command.context.limetype === 'document';
        const isInFilterExpression = command.filter && command.filter.op === 'IN' && command.filter.key === '_id';
        if (!isDocumentLimetype || !isInFilterExpression) {
            this.notifications.notify('The EsignCommand can only be run on document limetypes with a filter expression that includes _id.');
            return;
        }

        window.open('https://scrive.com', command.target);
    }
}
