'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

const index = require('./index-c74a2cd5.js');
const types = require('./types-e0f92974.js');

var __decorate$1 = (undefined && undefined.__decorate) || function (decorators, target, key, desc) {
  var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
  if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
  else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
  return c > 3 && r && Object.defineProperty(target, key, r), r;
};
let EsignCommand = class EsignCommand {
};
EsignCommand = __decorate$1([
  types.Command({
    id: 'limepkg_scrive.esign',
  })
], EsignCommand);

class EsignHandler {
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

var __decorate = (undefined && undefined.__decorate) || function (decorators, target, key, desc) {
  var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
  if (typeof Reflect === "object" && typeof Reflect.decorate === "function")
    r = Reflect.decorate(decorators, target, key, desc);
  else
    for (var i = decorators.length - 1; i >= 0; i--)
      if (d = decorators[i])
        r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
  return c > 3 && r && Object.defineProperty(target, key, r), r;
};
const Loader = class {
  constructor(hostRef) {
    index.registerInstance(this, hostRef);
  }
  connectedCallback() { }
  componentWillLoad() {
    const language = this.session.language;
    const handler = new EsignHandler(this.notificationService, this.config.limepkg_scrive, language);
    this.commandBus.register(EsignCommand, handler);
  }
  componentWillUpdate() { }
  disconnectedCallback() { }
  get notificationService() {
    return this.platform.get(types.PlatformServiceName.Notification);
  }
  get commandBus() {
    return this.platform.get(types.PlatformServiceName.CommandBus);
  }
};
__decorate([
  types.SelectConfig({})
], Loader.prototype, "config", void 0);
__decorate([
  types.SelectSession()
], Loader.prototype, "session", void 0);

exports.lwc_limepkg_scrive_loader = Loader;
