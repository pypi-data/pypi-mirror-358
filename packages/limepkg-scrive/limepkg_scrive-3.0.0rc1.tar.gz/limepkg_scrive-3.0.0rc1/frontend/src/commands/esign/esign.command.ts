import { Command, Expression, LimeWebComponentContext } from '@limetech/lime-web-components';

@Command({
    id: 'limepkg_scrive.esign',
})
export class EsignCommand {
    public context: LimeWebComponentContext;
    public filter?: Expression;
    // https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/a#target
    public target: '_self' | '_blank' | '_parent' | '_top' | '_unfencedTop' = '_blank';
}
