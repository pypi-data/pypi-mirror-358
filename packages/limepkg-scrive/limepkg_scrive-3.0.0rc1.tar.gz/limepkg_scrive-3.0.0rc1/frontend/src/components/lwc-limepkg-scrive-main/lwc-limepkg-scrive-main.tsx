import {
    LimeWebComponent,
    LimeWebComponentContext,
    LimeWebComponentPlatform,
    PlatformServiceName,
    SelectConfig,
    SelectCurrentLimeObject,
    SelectSession,
    Session,
} from '@limetech/lime-web-components';
import { Component, h, Prop, State } from '@stencil/core';

type File = {
    extension: string,
    filename: string,
    size: number;
}

@Component({
    tag: 'lwc-limepkg-scrive-main',
    shadow: true,
    styleUrl: 'lwc-limepkg-scrive-main.scss',
})
export class Main implements LimeWebComponent {
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

    @SelectCurrentLimeObject()
    @State()
    private document: any = {}

    @SelectSession()
    @State()
    private session: Session;

    @SelectConfig({})
    @State()
    private config: any = {
        limepkg_scrive: {
            scriveHost: "https://lime.scrive.com",
        },
    }

    @State()
    public includePerson = true;
    @State()
    public includeCoworker = true;
    @State()
    private cloneDocument = true;
    @State()
    private isOpen = false;

    private goToScrive(id: number, scriveDocId?: string) {
        const host = this.config?.limepkg_scrive?.scriveHost;
        const lang = this.session.language;
        window.open(`${host}/public/?limeDocId=${id}&lang=${lang}&usePerson=${this.includePerson}&useCoworker=${this.includeCoworker}&cloneDocument=${this.cloneDocument}&scriveDocId=${scriveDocId}`);
    }

    private files(): File[] {
        const fileMap = this.document?._files || {};
        const fileIds = Object.keys(fileMap);
        return fileIds.map(id => fileMap[id]);
    }

    private allowedExtensions = Object.freeze(["PDF", "DOC", "DOCX"]);
    private isSignable(file: File): boolean {
        return this.allowedExtensions.includes((file.extension || "").toUpperCase())
    }

    private setCloneDocument = (event: CustomEvent<boolean>) => {
        event.stopPropagation();
        this.cloneDocument = event.detail;
    };

    private openDialog = () => {
        this.isOpen = true;
    };

    private closeDialog = () => {
        this.isOpen = false;
    };

    public render() {
        if (this.context.limetype !== 'document') {
            return;
        }
        const signableFiles = this.files().filter(this.isSignable, this);
        const noSignableFiles = signableFiles.length === 0;
        const tooManySignableFiles = signableFiles.length > 1
        if (noSignableFiles || tooManySignableFiles) {
            return;
        }

        const translate = this.platform.get(PlatformServiceName.Translate);
        const esignLabel = translate.get("limepkg_scrive.primary_action")
        const cloneLabel = translate.get("limepkg_scrive.clone_document")
        const cloneHintLabel = translate.get("limepkg_scrive.clone_hint")
        const cloneInfoLabel = translate.get("limepkg_scrive.clone_info")
        const okLabel = translate.get("limepkg_scrive.ok")

        return (
            <section>
                <limel-button
                    id="scrive_esign_button"
                    label={esignLabel}
                    outlined={true}
                    icon="signature"
                    onClick={() =>
                        this.goToScrive(this.context.id, this.document?.scrive_document_id)
                    }
                />
                <p>
                    <limel-flex-container justify="start">
                        <limel-checkbox
                            label={cloneLabel}
                            checked={this.cloneDocument}
                            onChange={this.setCloneDocument}
                        />
                        <limel-icon-button
                            icon="question_mark"
                            label={cloneHintLabel}
                            onClick={this.openDialog}
                        />
                    </limel-flex-container>
                </p>
                <limel-dialog open={this.isOpen} onClose={this.closeDialog}>
                    <p>{cloneInfoLabel}</p>
                    <limel-button
                        label={okLabel}
                        onClick={this.closeDialog}
                        slot="button"
                    />
                </limel-dialog>
            </section>
        );
    }
}
