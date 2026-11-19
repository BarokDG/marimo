/* Copyright 2026 Marimo. All rights reserved. */

import type { Extension } from "@codemirror/state";
import { EditorView } from "@codemirror/view";
import {
  type DSLMetadata,
  type DSLParserOptions,
  GenericDSLParser,
} from "@marimo-team/smart-cells";
import type { LanguageAdapter } from "../types";

export type DSLLanguageAdapterMetadata = DSLMetadata;

/**
 * Language adapter for a custom cell DSL registered via `register_cell_dsl`.
 *
 * There's no known grammar for an arbitrary DSL, so unlike Markdown/SQL this
 * only offers plain-text editing (no syntax highlighting or completions) --
 * the language panel already falls back to showing just the adapter's `type`
 * for adapters it doesn't specifically recognize.
 */
export class DSLLanguageAdapter
  implements LanguageAdapter<DSLLanguageAdapterMetadata>
{
  private parser: GenericDSLParser;

  public readonly type: string;
  public readonly defaultCode: string;
  public readonly defaultMetadata: DSLLanguageAdapterMetadata;

  public constructor(options: DSLParserOptions) {
    this.parser = new GenericDSLParser(options);
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
    return [EditorView.lineWrapping];
  }
}
