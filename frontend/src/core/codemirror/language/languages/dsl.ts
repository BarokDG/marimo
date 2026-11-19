/* Copyright 2026 Marimo. All rights reserved. */

import type { Extension } from "@codemirror/state";
import { StateField } from "@codemirror/state";
import {
  Decoration,
  type DecorationSet,
  EditorView,
  WidgetType,
} from "@codemirror/view";
import {
  type DSLMetadata,
  type DSLParserOptions,
  GenericDSLParser,
} from "@marimo-team/smart-cells";
import type { LanguageAdapter } from "../types";
import {
  type DSLWidgetRenderOptions,
  loadDslWidgetModule,
} from "./dsl-widget-loader";

export type DSLLanguageAdapterMetadata = DSLMetadata;

export interface DSLLanguageAdapterOptions extends DSLParserOptions {
  /** Where to load this DSL's custom input-widget ESM module from. */
  inputWidgetEsmSpec?: { url: string; hash: string };
}

class DSLWidgetType extends WidgetType {
  private readonly spec: { url: string; hash: string };
  private readonly doc: string;

  public constructor(spec: { url: string; hash: string }, doc: string) {
    super();
    this.spec = spec;
    this.doc = doc;
  }

  public override eq(other: DSLWidgetType): boolean {
    return this.spec.hash === other.spec.hash && this.doc === other.doc;
  }

  public override toDOM(view: EditorView): HTMLElement {
    const el = document.createElement("div");
    el.className = "mo-dsl-widget";
    const opts: DSLWidgetRenderOptions = {
      el,
      code: this.doc,
      setCode: (next) => {
        view.dispatch({
          changes: { from: 0, to: view.state.doc.length, insert: next },
        });
      },
    };
    loadDslWidgetModule(this.spec)
      .then((render) => render(opts))
      .catch((error: unknown) => {
        el.textContent = `Failed to load DSL widget: ${String(error)}`;
      });
    return el;
  }

  public override ignoreEvent(): boolean {
    // Let the widget's own DOM handle its events directly.
    return true;
  }
}

/** Installs a whole-document decoration replacing plain-text editing with a custom widget. */
function buildInputWidgetExtension(spec: {
  url: string;
  hash: string;
}): Extension {
  const buildDecorations = (doc: string): DecorationSet => {
    // A zero-length range still carries the widget -- this is what makes
    // the widget show even for a brand-new, empty cell.
    return Decoration.set([
      Decoration.replace({
        widget: new DSLWidgetType(spec, doc),
        block: true,
      }).range(0, doc.length),
    ]);
  };
  const field = StateField.define<DecorationSet>({
    create(state) {
      return buildDecorations(state.doc.toString());
    },
    update(decorations, tr) {
      if (!tr.docChanged) {
        return decorations;
      }
      return buildDecorations(tr.state.doc.toString());
    },
    provide: (f) => EditorView.decorations.from(f),
  });
  return [
    field,
    // `theme()`, not `baseTheme()`: baseTheme's generated class is shared
    // globally across every `baseTheme()` call in the app and added to
    // every `.cm-editor` unconditionally, so its rules apply to ALL cells
    // regardless of extensions. `theme()` generates a fresh class per call,
    // only added to editors whose config actually includes this extension
    // -- the only one of the two that's genuinely scoped to this cell.
    EditorView.theme({
      // Cancel out `.marimo-cell .cm-editor`'s own padding (and
      // `.cm-content`'s default padding) so the widget can span the full
      // cell box edge-to-edge on top/left/right, instead of sitting inset
      // within it. Bottom padding is kept -- flush there looked worse.
      // Scoped to editors with this extension active, so other cell types
      // are unaffected.
      "&": {
        padding: "0 !important",
        paddingBottom: "3px !important",
      },
      ".cm-content": {
        padding: "0 !important",
        paddingBottom: "3px !important",
      },
      // CodeMirror's own cursor and gutter still render underneath the
      // widget (the underlying editor is still live) -- hide both.
      ".cm-cursorLayer": {
        display: "none !important",
      },
      ".cm-gutters": {
        display: "none !important",
      },
      ".mo-dsl-widget": {
        display: "block",
        width: "100%",
        boxSizing: "border-box",
      },
    }),
  ];
}

/**
 * Language adapter for a custom cell DSL registered via `register_cell_dsl`.
 *
 * There's no known grammar for an arbitrary DSL, so by default this only
 * offers plain-text editing (no syntax highlighting or completions) -- the
 * language panel already falls back to showing just the adapter's `type`
 * for adapters it doesn't specifically recognize. A DSL can opt into a
 * custom input widget (`inputWidgetEsmSpec`) replacing plain-text editing.
 */
export class DSLLanguageAdapter implements LanguageAdapter<DSLLanguageAdapterMetadata> {
  private parser: GenericDSLParser;
  private inputWidgetEsmSpec: { url: string; hash: string } | undefined;

  public readonly type: string;
  public readonly defaultCode: string;
  public readonly defaultMetadata: DSLLanguageAdapterMetadata;

  public constructor(options: DSLLanguageAdapterOptions) {
    this.parser = new GenericDSLParser(options);
    this.inputWidgetEsmSpec = options.inputWidgetEsmSpec;
    this.type = this.parser.type;
    this.defaultCode = this.parser.defaultCode;
    this.defaultMetadata = this.parser.defaultMetadata;
  }

  public transformIn(
    pythonCode: string,
  ): [string, number, DSLLanguageAdapterMetadata] {
    const result = this.parser.transformIn(pythonCode);
    return [result.code, result.offset, result.metadata];
  }

  public transformOut(
    code: string,
    metadata: DSLLanguageAdapterMetadata,
  ): [string, number] {
    const result = this.parser.transformOut(code, metadata);
    return [result.code, result.offset];
  }

  public isSupported(pythonCode: string): boolean {
    return this.parser.isSupported(pythonCode);
  }

  public getExtension(): Extension[] {
    const extensions: Extension[] = [EditorView.lineWrapping];

    if (this.inputWidgetEsmSpec) {
      extensions.push(buildInputWidgetExtension(this.inputWidgetEsmSpec));
    }

    return extensions;
  }
}
