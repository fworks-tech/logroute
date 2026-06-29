// @ts-nocheck
export class CancelError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'CancelError';
  }
}

type OnCancel = (cancelFn: () => void) => void;

export class CancelablePromise<T> implements Promise<T> {
  private _isResolved: boolean;
  private _isRejected: boolean;
  private _isCancelled: boolean;
  private readonly _resolveCallbacks: ((value: T) => void)[];
  private readonly _rejectCallbacks: ((reason?: any) => void)[];
  private readonly _cancelCallbacks: (() => void)[];
  private _result: T | undefined;
  private _error: any;

  constructor(
    executor: (resolve: (value: T | PromiseLike<T>) => void, reject: (reason?: any) => void, onCancel: OnCancel) => void
  ) {
    this._isResolved = false;
    this._isRejected = false;
    this._isCancelled = false;
    this._resolveCallbacks = [];
    this._rejectCallbacks = [];
    this._cancelCallbacks = [];

    const resolve = (value: T | PromiseLike<T>) => {
      if (this._isCancelled || this._isResolved || this._isRejected) return;
      this._isResolved = true;
      if (value instanceof Promise) {
        value.then(
          (v) => { this._result = v; this._resolveCallbacks.forEach((cb) => cb(v)); },
          (e) => { this._error = e; this._rejectCallbacks.forEach((cb) => cb(e)); }
        );
      } else {
        this._result = value;
        this._resolveCallbacks.forEach((cb) => cb(value));
      }
    };

    const reject = (reason?: any) => {
      if (this._isCancelled || this._isResolved || this._isRejected) return;
      this._isRejected = true;
      this._error = reason;
      this._rejectCallbacks.forEach((cb) => cb(reason));
    };

    const onCancel = (cancelFn: () => void) => {
      this._cancelCallbacks.push(cancelFn);
    };

    try {
      executor(resolve, reject, onCancel);
    } catch (error) {
      reject(error);
    }
  }

  get then() {
    return this._promise.then.bind(this._promise);
  }

  get catch() {
    return this._promise.catch.bind(this._promise);
  }

  get finally() {
    return this._promise.finally.bind(this._promise);
  }

  cancel(): void {
    if (this._isResolved || this._isRejected || this._isCancelled) return;
    this._isCancelled = true;
    this._cancelCallbacks.forEach((cb) => cb());
  }

  get isCancelled(): boolean {
    return this._isCancelled;
  }

  private get _promise(): Promise<T> {
    return new Promise<T>((resolve, reject) => {
      if (this._isResolved) { resolve(this._result!); return; }
      if (this._isRejected) { reject(this._error); return; }
      this._resolveCallbacks.push(resolve);
      this._rejectCallbacks.push(reject);
    });
  }
}
