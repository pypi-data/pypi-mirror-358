import { g as getElement, r as registerInstance, h } from './index-e7f7b2d6.js';
import { P as PlatformServiceName } from './types-75a901cf.js';

function isFunction(value) {
    return typeof value === 'function';
}

function createErrorClass(createImpl) {
    const _super = (instance) => {
        Error.call(instance);
        instance.stack = new Error().stack;
    };
    const ctorFunc = createImpl(_super);
    ctorFunc.prototype = Object.create(Error.prototype);
    ctorFunc.prototype.constructor = ctorFunc;
    return ctorFunc;
}

const UnsubscriptionError = createErrorClass((_super) => function UnsubscriptionErrorImpl(errors) {
    _super(this);
    this.message = errors
        ? `${errors.length} errors occurred during unsubscription:
${errors.map((err, i) => `${i + 1}) ${err.toString()}`).join('\n  ')}`
        : '';
    this.name = 'UnsubscriptionError';
    this.errors = errors;
});

function arrRemove(arr, item) {
    if (arr) {
        const index = arr.indexOf(item);
        0 <= index && arr.splice(index, 1);
    }
}

class Subscription {
    constructor(initialTeardown) {
        this.initialTeardown = initialTeardown;
        this.closed = false;
        this._parentage = null;
        this._finalizers = null;
    }
    unsubscribe() {
        let errors;
        if (!this.closed) {
            this.closed = true;
            const { _parentage } = this;
            if (_parentage) {
                this._parentage = null;
                if (Array.isArray(_parentage)) {
                    for (const parent of _parentage) {
                        parent.remove(this);
                    }
                }
                else {
                    _parentage.remove(this);
                }
            }
            const { initialTeardown: initialFinalizer } = this;
            if (isFunction(initialFinalizer)) {
                try {
                    initialFinalizer();
                }
                catch (e) {
                    errors = e instanceof UnsubscriptionError ? e.errors : [e];
                }
            }
            const { _finalizers } = this;
            if (_finalizers) {
                this._finalizers = null;
                for (const finalizer of _finalizers) {
                    try {
                        execFinalizer(finalizer);
                    }
                    catch (err) {
                        errors = errors !== null && errors !== void 0 ? errors : [];
                        if (err instanceof UnsubscriptionError) {
                            errors = [...errors, ...err.errors];
                        }
                        else {
                            errors.push(err);
                        }
                    }
                }
            }
            if (errors) {
                throw new UnsubscriptionError(errors);
            }
        }
    }
    add(teardown) {
        var _a;
        if (teardown && teardown !== this) {
            if (this.closed) {
                execFinalizer(teardown);
            }
            else {
                if (teardown instanceof Subscription) {
                    if (teardown.closed || teardown._hasParent(this)) {
                        return;
                    }
                    teardown._addParent(this);
                }
                (this._finalizers = (_a = this._finalizers) !== null && _a !== void 0 ? _a : []).push(teardown);
            }
        }
    }
    _hasParent(parent) {
        const { _parentage } = this;
        return _parentage === parent || (Array.isArray(_parentage) && _parentage.includes(parent));
    }
    _addParent(parent) {
        const { _parentage } = this;
        this._parentage = Array.isArray(_parentage) ? (_parentage.push(parent), _parentage) : _parentage ? [_parentage, parent] : parent;
    }
    _removeParent(parent) {
        const { _parentage } = this;
        if (_parentage === parent) {
            this._parentage = null;
        }
        else if (Array.isArray(_parentage)) {
            arrRemove(_parentage, parent);
        }
    }
    remove(teardown) {
        const { _finalizers } = this;
        _finalizers && arrRemove(_finalizers, teardown);
        if (teardown instanceof Subscription) {
            teardown._removeParent(this);
        }
    }
}
Subscription.EMPTY = (() => {
    const empty = new Subscription();
    empty.closed = true;
    return empty;
})();
const EMPTY_SUBSCRIPTION = Subscription.EMPTY;
function isSubscription(value) {
    return (value instanceof Subscription ||
        (value && 'closed' in value && isFunction(value.remove) && isFunction(value.add) && isFunction(value.unsubscribe)));
}
function execFinalizer(finalizer) {
    if (isFunction(finalizer)) {
        finalizer();
    }
    else {
        finalizer.unsubscribe();
    }
}

const config = {
    onUnhandledError: null,
    onStoppedNotification: null,
    Promise: undefined,
    useDeprecatedSynchronousErrorHandling: false,
    useDeprecatedNextContext: false,
};

const timeoutProvider = {
    setTimeout(handler, timeout, ...args) {
        const { delegate } = timeoutProvider;
        if (delegate === null || delegate === void 0 ? void 0 : delegate.setTimeout) {
            return delegate.setTimeout(handler, timeout, ...args);
        }
        return setTimeout(handler, timeout, ...args);
    },
    clearTimeout(handle) {
        const { delegate } = timeoutProvider;
        return ((delegate === null || delegate === void 0 ? void 0 : delegate.clearTimeout) || clearTimeout)(handle);
    },
    delegate: undefined,
};

function reportUnhandledError(err) {
    timeoutProvider.setTimeout(() => {
        const { onUnhandledError } = config;
        if (onUnhandledError) {
            onUnhandledError(err);
        }
        else {
            throw err;
        }
    });
}

function noop() { }

const COMPLETE_NOTIFICATION = (() => createNotification('C', undefined, undefined))();
function errorNotification(error) {
    return createNotification('E', undefined, error);
}
function nextNotification(value) {
    return createNotification('N', value, undefined);
}
function createNotification(kind, value, error) {
    return {
        kind,
        value,
        error,
    };
}

function errorContext(cb) {
    {
        cb();
    }
}

class Subscriber extends Subscription {
    constructor(destination) {
        super();
        this.isStopped = false;
        if (destination) {
            this.destination = destination;
            if (isSubscription(destination)) {
                destination.add(this);
            }
        }
        else {
            this.destination = EMPTY_OBSERVER;
        }
    }
    static create(next, error, complete) {
        return new SafeSubscriber(next, error, complete);
    }
    next(value) {
        if (this.isStopped) {
            handleStoppedNotification(nextNotification(value), this);
        }
        else {
            this._next(value);
        }
    }
    error(err) {
        if (this.isStopped) {
            handleStoppedNotification(errorNotification(err), this);
        }
        else {
            this.isStopped = true;
            this._error(err);
        }
    }
    complete() {
        if (this.isStopped) {
            handleStoppedNotification(COMPLETE_NOTIFICATION, this);
        }
        else {
            this.isStopped = true;
            this._complete();
        }
    }
    unsubscribe() {
        if (!this.closed) {
            this.isStopped = true;
            super.unsubscribe();
            this.destination = null;
        }
    }
    _next(value) {
        this.destination.next(value);
    }
    _error(err) {
        try {
            this.destination.error(err);
        }
        finally {
            this.unsubscribe();
        }
    }
    _complete() {
        try {
            this.destination.complete();
        }
        finally {
            this.unsubscribe();
        }
    }
}
const _bind = Function.prototype.bind;
function bind(fn, thisArg) {
    return _bind.call(fn, thisArg);
}
class ConsumerObserver {
    constructor(partialObserver) {
        this.partialObserver = partialObserver;
    }
    next(value) {
        const { partialObserver } = this;
        if (partialObserver.next) {
            try {
                partialObserver.next(value);
            }
            catch (error) {
                handleUnhandledError(error);
            }
        }
    }
    error(err) {
        const { partialObserver } = this;
        if (partialObserver.error) {
            try {
                partialObserver.error(err);
            }
            catch (error) {
                handleUnhandledError(error);
            }
        }
        else {
            handleUnhandledError(err);
        }
    }
    complete() {
        const { partialObserver } = this;
        if (partialObserver.complete) {
            try {
                partialObserver.complete();
            }
            catch (error) {
                handleUnhandledError(error);
            }
        }
    }
}
class SafeSubscriber extends Subscriber {
    constructor(observerOrNext, error, complete) {
        super();
        let partialObserver;
        if (isFunction(observerOrNext) || !observerOrNext) {
            partialObserver = {
                next: (observerOrNext !== null && observerOrNext !== void 0 ? observerOrNext : undefined),
                error: error !== null && error !== void 0 ? error : undefined,
                complete: complete !== null && complete !== void 0 ? complete : undefined,
            };
        }
        else {
            let context;
            if (this && config.useDeprecatedNextContext) {
                context = Object.create(observerOrNext);
                context.unsubscribe = () => this.unsubscribe();
                partialObserver = {
                    next: observerOrNext.next && bind(observerOrNext.next, context),
                    error: observerOrNext.error && bind(observerOrNext.error, context),
                    complete: observerOrNext.complete && bind(observerOrNext.complete, context),
                };
            }
            else {
                partialObserver = observerOrNext;
            }
        }
        this.destination = new ConsumerObserver(partialObserver);
    }
}
function handleUnhandledError(error) {
    {
        reportUnhandledError(error);
    }
}
function defaultErrorHandler(err) {
    throw err;
}
function handleStoppedNotification(notification, subscriber) {
    const { onStoppedNotification } = config;
    onStoppedNotification && timeoutProvider.setTimeout(() => onStoppedNotification(notification, subscriber));
}
const EMPTY_OBSERVER = {
    closed: true,
    next: noop,
    error: defaultErrorHandler,
    complete: noop,
};

const observable = (() => (typeof Symbol === 'function' && Symbol.observable) || '@@observable')();

function identity(x) {
    return x;
}

function pipeFromArray(fns) {
    if (fns.length === 0) {
        return identity;
    }
    if (fns.length === 1) {
        return fns[0];
    }
    return function piped(input) {
        return fns.reduce((prev, fn) => fn(prev), input);
    };
}

class Observable {
    constructor(subscribe) {
        if (subscribe) {
            this._subscribe = subscribe;
        }
    }
    lift(operator) {
        const observable = new Observable();
        observable.source = this;
        observable.operator = operator;
        return observable;
    }
    subscribe(observerOrNext, error, complete) {
        const subscriber = isSubscriber(observerOrNext) ? observerOrNext : new SafeSubscriber(observerOrNext, error, complete);
        errorContext(() => {
            const { operator, source } = this;
            subscriber.add(operator
                ?
                    operator.call(subscriber, source)
                : source
                    ?
                        this._subscribe(subscriber)
                    :
                        this._trySubscribe(subscriber));
        });
        return subscriber;
    }
    _trySubscribe(sink) {
        try {
            return this._subscribe(sink);
        }
        catch (err) {
            sink.error(err);
        }
    }
    forEach(next, promiseCtor) {
        promiseCtor = getPromiseCtor(promiseCtor);
        return new promiseCtor((resolve, reject) => {
            const subscriber = new SafeSubscriber({
                next: (value) => {
                    try {
                        next(value);
                    }
                    catch (err) {
                        reject(err);
                        subscriber.unsubscribe();
                    }
                },
                error: reject,
                complete: resolve,
            });
            this.subscribe(subscriber);
        });
    }
    _subscribe(subscriber) {
        var _a;
        return (_a = this.source) === null || _a === void 0 ? void 0 : _a.subscribe(subscriber);
    }
    [observable]() {
        return this;
    }
    pipe(...operations) {
        return pipeFromArray(operations)(this);
    }
    toPromise(promiseCtor) {
        promiseCtor = getPromiseCtor(promiseCtor);
        return new promiseCtor((resolve, reject) => {
            let value;
            this.subscribe((x) => (value = x), (err) => reject(err), () => resolve(value));
        });
    }
}
Observable.create = (subscribe) => {
    return new Observable(subscribe);
};
function getPromiseCtor(promiseCtor) {
    var _a;
    return (_a = promiseCtor !== null && promiseCtor !== void 0 ? promiseCtor : config.Promise) !== null && _a !== void 0 ? _a : Promise;
}
function isObserver(value) {
    return value && isFunction(value.next) && isFunction(value.error) && isFunction(value.complete);
}
function isSubscriber(value) {
    return (value && value instanceof Subscriber) || (isObserver(value) && isSubscription(value));
}

const ObjectUnsubscribedError = createErrorClass((_super) => function ObjectUnsubscribedErrorImpl() {
    _super(this);
    this.name = 'ObjectUnsubscribedError';
    this.message = 'object unsubscribed';
});

class Subject extends Observable {
    constructor() {
        super();
        this.closed = false;
        this.currentObservers = null;
        this.observers = [];
        this.isStopped = false;
        this.hasError = false;
        this.thrownError = null;
    }
    lift(operator) {
        const subject = new AnonymousSubject(this, this);
        subject.operator = operator;
        return subject;
    }
    _throwIfClosed() {
        if (this.closed) {
            throw new ObjectUnsubscribedError();
        }
    }
    next(value) {
        errorContext(() => {
            this._throwIfClosed();
            if (!this.isStopped) {
                if (!this.currentObservers) {
                    this.currentObservers = Array.from(this.observers);
                }
                for (const observer of this.currentObservers) {
                    observer.next(value);
                }
            }
        });
    }
    error(err) {
        errorContext(() => {
            this._throwIfClosed();
            if (!this.isStopped) {
                this.hasError = this.isStopped = true;
                this.thrownError = err;
                const { observers } = this;
                while (observers.length) {
                    observers.shift().error(err);
                }
            }
        });
    }
    complete() {
        errorContext(() => {
            this._throwIfClosed();
            if (!this.isStopped) {
                this.isStopped = true;
                const { observers } = this;
                while (observers.length) {
                    observers.shift().complete();
                }
            }
        });
    }
    unsubscribe() {
        this.isStopped = this.closed = true;
        this.observers = this.currentObservers = null;
    }
    get observed() {
        var _a;
        return ((_a = this.observers) === null || _a === void 0 ? void 0 : _a.length) > 0;
    }
    _trySubscribe(subscriber) {
        this._throwIfClosed();
        return super._trySubscribe(subscriber);
    }
    _subscribe(subscriber) {
        this._throwIfClosed();
        this._checkFinalizedStatuses(subscriber);
        return this._innerSubscribe(subscriber);
    }
    _innerSubscribe(subscriber) {
        const { hasError, isStopped, observers } = this;
        if (hasError || isStopped) {
            return EMPTY_SUBSCRIPTION;
        }
        this.currentObservers = null;
        observers.push(subscriber);
        return new Subscription(() => {
            this.currentObservers = null;
            arrRemove(observers, subscriber);
        });
    }
    _checkFinalizedStatuses(subscriber) {
        const { hasError, thrownError, isStopped } = this;
        if (hasError) {
            subscriber.error(thrownError);
        }
        else if (isStopped) {
            subscriber.complete();
        }
    }
    asObservable() {
        const observable = new Observable();
        observable.source = this;
        return observable;
    }
}
Subject.create = (destination, source) => {
    return new AnonymousSubject(destination, source);
};
class AnonymousSubject extends Subject {
    constructor(destination, source) {
        super();
        this.destination = destination;
        this.source = source;
    }
    next(value) {
        var _a, _b;
        (_b = (_a = this.destination) === null || _a === void 0 ? void 0 : _a.next) === null || _b === void 0 ? void 0 : _b.call(_a, value);
    }
    error(err) {
        var _a, _b;
        (_b = (_a = this.destination) === null || _a === void 0 ? void 0 : _a.error) === null || _b === void 0 ? void 0 : _b.call(_a, err);
    }
    complete() {
        var _a, _b;
        (_b = (_a = this.destination) === null || _a === void 0 ? void 0 : _a.complete) === null || _b === void 0 ? void 0 : _b.call(_a);
    }
    _subscribe(subscriber) {
        var _a, _b;
        return (_b = (_a = this.source) === null || _a === void 0 ? void 0 : _a.subscribe(subscriber)) !== null && _b !== void 0 ? _b : EMPTY_SUBSCRIPTION;
    }
}

class BehaviorSubject extends Subject {
    constructor(_value) {
        super();
        this._value = _value;
    }
    get value() {
        return this.getValue();
    }
    _subscribe(subscriber) {
        const subscription = super._subscribe(subscriber);
        !subscription.closed && subscriber.next(this._value);
        return subscription;
    }
    getValue() {
        const { hasError, thrownError, _value } = this;
        if (hasError) {
            throw thrownError;
        }
        this._throwIfClosed();
        return _value;
    }
    next(value) {
        super.next((this._value = value));
    }
}

function defaultOptionFactory(options) {
    return options;
}
/**
 * Create a new state decorator
 *
 * @param options - decorator options
 * @param config - decorator configuration
 * @returns state decorator
 * @public
 */
function createStateDecorator(options, config) {
    return (target, property) => {
        const properties = getComponentProperties(target, property, options, config);
        if (properties.length === 1) {
            extendLifecycleMethods(target, properties);
        }
    };
}
const componentProperties = new WeakMap();
const componentSubscriptions = new WeakMap();
const connectedComponents = new WeakMap();
/**
 * Get properties data for a component
 *
 * @param component - the component class containing the decorator
 * @param property - name of the property
 * @param options - decorator options
 * @param config - decorator configuration
 * @returns properties data for the component
 */
function getComponentProperties(component, property, options, config) {
    let properties = componentProperties.get(component);
    if (!properties) {
        properties = [];
        componentProperties.set(component, properties);
    }
    properties.push({
        options: options,
        name: property,
        optionFactory: config.optionFactory || defaultOptionFactory,
        service: {
            name: config.name,
            method: config.method || 'subscribe',
        },
    });
    return properties;
}
/**
 * Extend the lifecycle methods on the component
 *
 * @param component - the component to extend
 * @param properties - the properties with which to extend the component
 * @returns
 */
function extendLifecycleMethods(component, properties) {
    // `componentWillLoad` and `componentDidUnload` is included for backwards
    // compatibility reasons. The correct way to setup the subscriptions is in
    // `connectedCallback` and `disconnectedCallback`, but since not all
    // plugins might implement those methods yet we still have include them
    // until we make `connectedCallback` and `disconnectedCallback` required
    // on the interface.
    component.connectedCallback = createConnectedCallback(component.connectedCallback, properties);
    component.componentWillLoad = createComponentWillLoad(component.componentWillLoad, properties);
    component.componentDidUnload = createDisconnectedCallback(component.componentDidUnload);
    component.disconnectedCallback = createDisconnectedCallback(component.disconnectedCallback);
}
function createConnectedCallback(original, properties) {
    return async function (...args) {
        connectedComponents.set(this, true);
        componentSubscriptions.set(this, []);
        await ensureLimeProps(this);
        const observable = new BehaviorSubject(this.context);
        watchProp(this, 'context', observable);
        properties.forEach((property) => {
            property.options = property.optionFactory(property.options, this);
            if (isContextAware(property.options)) {
                property.options.context = observable;
            }
            subscribe(this, property);
        });
        if (original) {
            return original.apply(this, args);
        }
    };
}
function createComponentWillLoad(original, properties) {
    return async function (...args) {
        if (connectedComponents.get(this) === true) {
            await ensureLimeProps(this);
            if (original) {
                return original.apply(this, args);
            }
            return;
        }
        const connectedCallback = createConnectedCallback(original, properties);
        return connectedCallback.apply(this, args);
    };
}
function createDisconnectedCallback(original) {
    return async function (...args) {
        let result;
        if (original) {
            result = original.apply(this, args);
        }
        unsubscribeAll(this);
        return result;
    };
}
/**
 * Check if the options are context aware
 *
 * @param options - state decorator options
 * @returns true if the options are context aware
 */
function isContextAware(options) {
    return 'context' in options;
}
/**
 * Make sure that all required lime properties are set on the web component
 *
 * @param target - the web component
 * @returns a promise that resolves when all properties are defined
 */
function ensureLimeProps(target) {
    const promises = [];
    if (!target.platform) {
        promises.push(waitForProp(target, 'platform'));
    }
    if (!target.context) {
        promises.push(waitForProp(target, 'context'));
    }
    if (!promises.length) {
        return Promise.resolve();
    }
    return Promise.all(promises);
}
/**
 * Wait for a property to be defined on an object
 *
 * @param target - the web component
 * @param property - the name of the property to watch
 * @returns a promise that will resolve when the property is set on the object
 */
function waitForProp(target, property) {
    const element = getElement(target);
    return new Promise((resolve) => {
        Object.defineProperty(element, property, {
            configurable: true,
            set: (value) => {
                delete element[property];
                element[property] = value;
                resolve();
            },
        });
    });
}
function watchProp(target, property, observer) {
    const element = getElement(target);
    const { get, set } = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(element), property);
    Object.defineProperty(element, property, {
        configurable: true,
        get: get,
        set: function (value) {
            set.call(this, value);
            observer.next(value);
        },
    });
}
/**
 * Subscribe to changes from the state
 *
 * @param component - the component instance
 * @param property - property to update when subscription triggers
 * @returns
 */
function subscribe(component, property) {
    const subscription = createSubscription(component, property);
    const subscriptions = componentSubscriptions.get(component);
    subscriptions.push(subscription);
}
/**
 * Unsubscribe to changes from the state
 *
 * @param component - the instance of the component
 * @returns
 */
function unsubscribeAll(component) {
    const subscriptions = componentSubscriptions.get(component);
    subscriptions.forEach((unsubscribe) => unsubscribe());
    componentSubscriptions.set(component, []);
}
/**
 * Get a function that accepts a state, and updates the given property
 * on the given component with that state
 *
 * @param instance - the component to augment
 * @param property - name of the property on the component
 * @returns updates the state
 */
function mapState(instance, property) {
    return (state) => {
        instance[property] = state;
    };
}
/**
 * Create a state subscription
 *
 * @param component - the component instance
 * @param property - the property on the component
 * @returns unsubscribe function
 */
function createSubscription(component, property) {
    const myOptions = Object.assign({}, property.options);
    bindFunctions(myOptions, component);
    const name = property.service.name;
    const platform = component.platform;
    if (!platform.has(name)) {
        throw new Error(`Service ${name} does not exist`);
    }
    const service = platform.get(name);
    return service[property.service.method](mapState(component, property.name), myOptions);
}
/**
 * Bind connect functions to the current scope
 *
 * @param options - options for the selector
 * @param scope - the current scope to bind to
 * @returns
 */
function bindFunctions(options, scope) {
    if (options.filter) {
        options.filter = options.filter.map((func) => func.bind(scope));
    }
    if (options.map) {
        options.map = options.map.map((func) => func.bind(scope));
    }
}

/**
 * Get the limeobject for the current context
 *
 * @param options - state decorator options
 * @returns state decorator
 * @public
 * @group Lime objects
 */
function SelectCurrentLimeObject(options = {}) {
    const config = {
        name: PlatformServiceName.LimeObjectRepository,
    };
    options.map = [currentLimeobject, ...(options.map || [])];
    options.context = null;
    return createStateDecorator(options, config);
}
function currentLimeobject(limeobjects) {
    const { limetype, id } = this.context;
    if (!limeobjects[limetype]) {
        return undefined;
    }
    return limeobjects[limetype].find((object) => object.id === id);
}

/**
 * Gets an object with all configs where key is used as key.
 *
 * @param options - state decorator options
 * @returns state decorator
 * @public
 * @group Config
 */
function SelectConfig(options) {
    const config = {
        name: PlatformServiceName.ConfigRepository,
    };
    return createStateDecorator(options, config);
}

/**
 * Get the application session
 *
 * @param options - state decorator options
 * @returns state decorator
 * @public
 * @group Application
 */
function SelectSession(options = {}) {
    const config = {
        name: PlatformServiceName.Application,
    };
    options.map = [getSession, ...(options.map || [])];
    return createStateDecorator(options, config);
}
function getSession(applicationData) {
    return applicationData.session;
}

const lwcLimepkgScriveMainCss = ".container{margin-left:1.25rem;margin-right:1.25rem}#scrive_esign_button{isolation:isolate;position:relative}#scrive_esign_button:after{content:\"\";display:block;width:1.5rem;height:1.5rem;position:absolute;z-index:1;top:0;left:0.25rem;bottom:0;margin:auto;background-image:url(\"data:image/svg+xml; utf8, <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 128.9 116.04'><defs><style>.cls-1{fill:none;}.cls-2{fill:%2327282d;}</style></defs><g id='Layer_2' data-name='Layer 2'><g id='S_Mark_Dark' data-name='S Mark Dark'><g id='S_Black' data-name='S Black'><rect class='cls-1' width='128.9' height='116.04'/><path class='cls-2' d='M65.51,65.48a29.87,29.87,0,0,1,7.76,2,7.3,7.3,0,0,1,3.62,3,8.64,8.64,0,0,1,1,4.35A10.34,10.34,0,0,1,76,80.71a12.35,12.35,0,0,1-4.64,3.53c-4.65,2.1-11.05,2.69-16.06,2.73A40.35,40.35,0,0,1,44,85.53,20.24,20.24,0,0,1,36.8,82,13.63,13.63,0,0,1,33,77.1,13.1,13.1,0,0,1,31.86,72H17.67A28.57,28.57,0,0,0,20.6,83a22,22,0,0,0,6.22,7.55,31.48,31.48,0,0,0,8.63,4.6,48.07,48.07,0,0,0,9.91,2.31,75.66,75.66,0,0,0,10.35.63c10.94,0,25-2.14,32.12-11.44A22.22,22.22,0,0,0,92.07,73.2a18,18,0,0,0-1.61-7.8A19.6,19.6,0,0,0,86,59.48a22.44,22.44,0,0,0-6.43-4,29.84,29.84,0,0,0-7.69-2.1C63.47,52.2,44.59,50.46,39.22,48A7.21,7.21,0,0,1,35.56,45a7.69,7.69,0,0,1-1-4.3,8.74,8.74,0,0,1,1.72-5.52,12.69,12.69,0,0,1,4.6-3.53,26.67,26.67,0,0,1,6.37-1.85,43.93,43.93,0,0,1,6.88-.55,34.38,34.38,0,0,1,12.25,2,17.4,17.4,0,0,1,7.35,5,11.88,11.88,0,0,1,2.67,7H90.64A27.58,27.58,0,0,0,87.9,33.17a24.4,24.4,0,0,0-6.73-8,31.92,31.92,0,0,0-11-5.19,60.15,60.15,0,0,0-15.84-1.92A52.27,52.27,0,0,0,36.22,21a25.4,25.4,0,0,0-11.67,8.24,20.92,20.92,0,0,0-4.17,13A18.17,18.17,0,0,0,26.49,56,22.45,22.45,0,0,0,32.92,60a29.63,29.63,0,0,0,7.61,2.06C48.91,63.23,57.21,64.37,65.51,65.48Z'/><path class='cls-2' d='M111.23,89.19a8.84,8.84,0,1,1-8.84-8.88A8.87,8.87,0,0,1,111.23,89.19Z'/></g></g></g></svg>\");background-color:var(--lime-elevated-surface-background-color);background-size:contain;background-repeat:no-repeat;background-position:center}";

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
const Main = class {
  constructor(hostRef) {
    registerInstance(this, hostRef);
    this.document = {};
    this.isOpen = false;
    this.allowedExtensions = Object.freeze(["PDF", "DOC", "DOCX"]);
    this.setCloneDocument = (event) => {
      event.stopPropagation();
      this.cloneDocument = event.detail;
    };
    this.openDialog = () => {
      this.isOpen = true;
    };
    this.closeDialog = () => {
      this.isOpen = false;
    };
  }
  goToScrive(id, scriveDocId) {
    var _a;
    const { scriveHost, includePerson, includeCoworker, target } = (_a = this.config) === null || _a === void 0 ? void 0 : _a.limepkg_scrive;
    const lang = this.session.language;
    window.open(`${scriveHost}/public/?limeDocId=${id}&lang=${lang}&usePerson=${includePerson}&useCoworker=${includeCoworker}&cloneDocument=${this.cloneDocument}&scriveDocId=${scriveDocId}`, target);
  }
  files() {
    var _a;
    const fileMap = ((_a = this.document) === null || _a === void 0 ? void 0 : _a._files) || {};
    const fileIds = Object.keys(fileMap);
    return fileIds.map(id => fileMap[id]);
  }
  isSignable(file) {
    return this.allowedExtensions.includes((file.extension || "").toUpperCase());
  }
  render() {
    var _a, _b;
    if (this.context.limetype !== 'document') {
      return;
    }
    const signableFiles = this.files().filter(this.isSignable, this);
    const noSignableFiles = signableFiles.length === 0;
    const tooManySignableFiles = signableFiles.length > 1;
    if (noSignableFiles || tooManySignableFiles) {
      return;
    }
    const translate = this.platform.get(PlatformServiceName.Translate);
    const esignLabel = translate.get("limepkg_scrive.primary_action");
    const cloneLabel = translate.get("limepkg_scrive.clone_document");
    const cloneHintLabel = translate.get("limepkg_scrive.clone_hint");
    const cloneInfoLabel = translate.get("limepkg_scrive.clone_info");
    const okLabel = translate.get("limepkg_scrive.ok");
    return (h("section", null, h("limel-button", { id: "scrive_esign_button", label: esignLabel, outlined: true, icon: "signature", onClick: () => { var _a; return this.goToScrive(this.context.id, (_a = this.document) === null || _a === void 0 ? void 0 : _a.scrive_document_id); } }), h("p", null, h("limel-flex-container", { justify: "start" }, h("limel-checkbox", { label: cloneLabel, checked: this.cloneDocument && ((_b = (_a = this.config) === null || _a === void 0 ? void 0 : _a.limepkg_scrive) === null || _b === void 0 ? void 0 : _b.cloneDocument), onChange: this.setCloneDocument }), h("limel-icon-button", { icon: "question_mark", label: cloneHintLabel, onClick: this.openDialog }))), h("limel-dialog", { open: this.isOpen, onClose: this.closeDialog }, h("p", null, cloneInfoLabel), h("limel-button", { label: okLabel, onClick: this.closeDialog, slot: "button" }))));
  }
};
__decorate([
  SelectCurrentLimeObject()
], Main.prototype, "document", void 0);
__decorate([
  SelectSession()
], Main.prototype, "session", void 0);
__decorate([
  SelectConfig({})
], Main.prototype, "config", void 0);
Main.style = lwcLimepkgScriveMainCss;

export { Main as lwc_limepkg_scrive_main };
