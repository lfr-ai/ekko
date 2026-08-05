import "@testing-library/jest-dom/vitest";

// Radix UI primitives rely on browser APIs that happy-dom does not implement.
// These no-op polyfills let Checkbox/Switch/Select render and interact in tests.
if (!Element.prototype.hasPointerCapture) {
  Element.prototype.hasPointerCapture = () => false;
}
if (!Element.prototype.setPointerCapture) {
  Element.prototype.setPointerCapture = () => undefined;
}
if (!Element.prototype.releasePointerCapture) {
  Element.prototype.releasePointerCapture = () => undefined;
}
if (!Element.prototype.scrollIntoView) {
  Element.prototype.scrollIntoView = () => undefined;
}
if (!("ResizeObserver" in globalThis)) {
  class ResizeObserverStub {
    observe(): void {
      // no-op: happy-dom has no layout engine
    }
    unobserve(): void {
      // no-op: happy-dom has no layout engine
    }
    disconnect(): void {
      // no-op: happy-dom has no layout engine
    }
  }
  globalThis.ResizeObserver = ResizeObserverStub as unknown as typeof ResizeObserver;
}
