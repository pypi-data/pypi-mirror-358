import {
    LimePluginLoader,
    LimeWebComponentContext,
    LimeWebComponentPlatform,
    PlatformServiceName,
} from '@limetech/lime-web-components';
import { Component, Prop } from '@stencil/core';
import { EsignCommand } from 'src/commands/esign/esign.command';
import { EsignHandler } from 'src/commands/esign/esign.handler';

// NOTE: Do NOT remove this component, it is required to run the plugin correctly.
// However, if your plugin has any code that should run only once when the application
// starts, you are free to use the component lifecycle methods below to do so.
// The component should never render anything, so do NOT implement a render method.

@Component({
    // ⚠️ WARNING! Do not change the tag name of this component unless you also
    // change the name of the package. The tag name should be
    // lwc-<package-name>-loader, e.g. lwc-limepkg-scrive-loader
    tag: 'lwc-limepkg-scrive-loader',
    shadow: true,
})
export class Loader implements LimePluginLoader {
    /**
     * @inherit
     */
    @Prop()
    public platform: LimeWebComponentPlatform;

    /**
     * @inherit
     */
    @Prop()
    public context: LimeWebComponentContext;

    public connectedCallback() {}

    public componentWillLoad() {
        const helloHandler = new EsignHandler(this.notificationService);
        this.commandBus.register(EsignCommand, helloHandler);
    }

    public componentWillUpdate() {}

    public disconnectedCallback() {}

    private get notificationService() {
        return this.platform.get(PlatformServiceName.Notification);
    }

    private get commandBus() {
        return this.platform.get(PlatformServiceName.CommandBus);
    }
}
