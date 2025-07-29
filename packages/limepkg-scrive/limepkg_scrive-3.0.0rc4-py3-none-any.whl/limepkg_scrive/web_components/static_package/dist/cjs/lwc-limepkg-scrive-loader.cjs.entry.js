'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

const index = require('./index-c74a2cd5.js');
const types = require('./types-3c8a0ef0.js');

var __decorate = (undefined && undefined.__decorate) || function (decorators, target, key, desc) {
  var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
  if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
  else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
  return c > 3 && r && Object.defineProperty(target, key, r), r;
};
let EsignCommand = class EsignCommand {
  constructor() {
    // https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/a#target
    this.target = '_blank';
  }
};
EsignCommand = __decorate([
  types.Command({
    id: 'limepkg_scrive.esign',
  })
], EsignCommand);

class EsignHandler {
  constructor(notifications) {
    this.notifications = notifications;
  }
  handle(command) {
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

const Loader = class {
  constructor(hostRef) {
    index.registerInstance(this, hostRef);
  }
  connectedCallback() { }
  componentWillLoad() {
    const helloHandler = new EsignHandler(this.notificationService);
    this.commandBus.register(EsignCommand, helloHandler);
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

exports.lwc_limepkg_scrive_loader = Loader;
