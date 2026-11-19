/* Copyright 2026 Marimo. All rights reserved. */

import { asRemoteURL } from "@/core/runtime/config";
import { resolveVirtualFileURL } from "@/core/static/files";
import { isStaticNotebook } from "@/core/static/static-state";
import { isTrustedVirtualFileUrl } from "@/plugins/core/trusted-url";

export interface DSLWidgetRenderOptions {
  el: HTMLElement;
  code: string;
  setCode: (next: string) => void;
}

export type DSLWidgetRender = (opts: DSLWidgetRenderOptions) => void;

interface DSLWidgetModule {
  default: DSLWidgetRender;
}

const moduleCache = new Map<string, Promise<DSLWidgetRender>>();

/**
 * Dynamically import a DSL's input-widget ESM module (see
 * `CellDSL.input_widget_esm`), caching by content hash for the notebook's
 * lifetime. Modeled on `plugins/impl/anywidget/widget-binding.ts`'s
 * `#doImport`, reusing its exact trust-check/resolution utilities, but
 * deliberately narrower: no reference-counted disposal, no hot-reload
 * generation swap -- a DSL registration is process-lifetime, not
 * per-instance-disposed like a widget's comm.
 */
export function loadDslWidgetModule(spec: {
  url: string;
  hash: string;
}): Promise<DSLWidgetRender> {
  let entry = moduleCache.get(spec.hash);
  if (!entry) {
    entry = (async () => {
      // `EsmSpec` only ever travels on kernel-authored notifications (never
      // client-writable state), so it's exempt from the virtual-file-only
      // trust check the same way anywidget's kernel-authored URLs are.
      const trusted =
        isTrustedVirtualFileUrl(spec.url) || /^(https?:|data:)/.test(spec.url);
      if (!trusted) {
        throw new Error(
          `Refusing to load DSL widget module from untrusted URL: ${spec.url}`,
        );
      }
      const remoteUrl = asRemoteURL(spec.url).toString();
      const url = isStaticNotebook()
        ? resolveVirtualFileURL(remoteUrl)
        : remoteUrl;
      try {
        const mod = (await import(/* @vite-ignore */ url)) as DSLWidgetModule;
        if (typeof mod.default !== "function") {
          throw new Error("DSL widget module has no default export function");
        }
        return mod.default;
      } finally {
        if (url !== remoteUrl) {
          URL.revokeObjectURL(url);
        }
      }
    })();
    moduleCache.set(spec.hash, entry);
  }
  return entry;
}
