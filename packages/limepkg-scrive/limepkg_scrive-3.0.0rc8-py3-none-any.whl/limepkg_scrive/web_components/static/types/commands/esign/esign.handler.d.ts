import { CommandHandler, Notifications } from '@limetech/lime-web-components';
import { EsignCommand } from './esign.command';
import { OurAwesomePackageConfig } from 'src/types';
export declare class EsignHandler implements CommandHandler {
  private notifications;
  private config;
  private language;
  constructor(notifications: Notifications, config: OurAwesomePackageConfig, language: string);
  handle(command: EsignCommand): void;
}
