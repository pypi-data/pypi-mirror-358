import { LimePluginLoader, LimeWebComponentContext, LimeWebComponentPlatform } from '@limetech/lime-web-components';
export declare class Loader implements LimePluginLoader {
  /**
   * @inherit
   */
  platform: LimeWebComponentPlatform;
  /**
   * @inherit
   */
  context: LimeWebComponentContext;
  private config;
  connectedCallback(): void;
  componentWillLoad(): void;
  componentWillUpdate(): void;
  disconnectedCallback(): void;
  private get notificationService();
  private get commandBus();
}
