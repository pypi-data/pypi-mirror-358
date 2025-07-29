import { CommandHandler, Notifications } from '@limetech/lime-web-components';
import { EsignCommand } from './esign.command';
export declare class EsignHandler implements CommandHandler {
  private notifications;
  constructor(notifications: Notifications);
  handle(command: EsignCommand): void;
}
