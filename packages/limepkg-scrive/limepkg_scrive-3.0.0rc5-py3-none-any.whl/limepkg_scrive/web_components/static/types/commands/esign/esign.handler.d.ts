import { CommandHandler, Notifications } from '@limetech/lime-web-components';
import { EsignCommand } from './esign.command';
import { OurAwesomePackageConfig } from 'src/types';
export declare class EsignHandler implements CommandHandler {
  private notifications;
  private config;
  constructor(notifications: Notifications, config: OurAwesomePackageConfig);
  handle(command: EsignCommand): void;
}
