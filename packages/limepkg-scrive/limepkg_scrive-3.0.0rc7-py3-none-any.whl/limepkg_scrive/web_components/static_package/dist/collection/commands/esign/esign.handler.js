export class EsignHandler {
  constructor(notifications, config, language) {
    this.notifications = notifications;
    this.config = config;
    this.language = language;
    this.config = config;
  }
  handle(command) {
    const documentIds = command.filter.exp;
    console.log(command, documentIds, this.config);
    const isDocumentLimetype = command.context.limetype === 'document';
    const isInFilterExpression = command.filter && command.filter.op === 'IN' && command.filter.key === '_id';
    if (!isDocumentLimetype || !isInFilterExpression) {
      this.notifications.notify('The EsignCommand can only be run on document limetypes with a filter expression that includes _id.');
      return;
    }
    const { scriveHost, includePerson, includeCoworker, cloneDocument, target } = this.config;
    // FIXME scriveDocumentId???
    window.open(`${scriveHost}/public/?limeDocId=${documentIds.join(",")}&lang=${this.language}&usePerson=${includePerson}&useCoworker=${includeCoworker}&cloneDocument=${cloneDocument}`, target);
  }
}
