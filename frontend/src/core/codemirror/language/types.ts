/* Copyright 2026 Marimo. All rights reserved. */
/* oxlint-disable typescript/no-explicit-any */

import type { Extension } from "@codemirror/state";
import type { CellId } from "@/core/cells/ids";
import type {
  CompletionConfig,
  DiagnosticsConfig,
  LSPConfig,
} from "@/core/config/config-schema";
import type { HotkeyProvider } from "@/core/hotkeys/hotkeys";
import type { PlaceholderType } from "../config/types";

/**
 * A language adapter is a class that can transform code from one language to
 * another. For example, a Markdown language adapter can make it feel like
 * you're writing Markdown, but it will actually be transformed into Python.
 *
 * These are stateless classes that can be reused across multiple editor views.
 */
export interface LanguageAdapter<M = Record<string, any>> {
  readonly type: LanguageAdapterType;
  readonly defaultCode: string;
  readonly defaultMetadata: Readonly<M>;

  transformIn(code: string): [string, number, M];
  transformOut(code: string, metadata: M): [string, number];
  isSupported(code: string): boolean;
  getExtension(options: {
    cellId: CellId;
    completionConfig: CompletionConfig;
    hotkeys: HotkeyProvider;
    placeholderType: PlaceholderType;
    lspConfig: LSPConfig & { diagnostics?: DiagnosticsConfig };
  }): Extension[];
}

export type LanguageMetadataOf<T extends LanguageAdapter> =
  T extends LanguageAdapter<infer M> ? M : never;

// The `(string & {})` branch keeps autocomplete for the three builtins while
// still allowing a dynamically-registered DSL name (see `register_cell_dsl`).
export type LanguageAdapterType = "python" | "markdown" | "sql" | (string & {});

/**
 * Narrow an adapter type down to one the AI completion endpoints understand.
 * Those endpoints don't know about dynamically-registered DSLs, but a DSL
 * cell's code is still valid Python, so it maps to "python".
 */
export function toAiCompletionLanguage(
  type: LanguageAdapterType,
): "python" | "markdown" | "sql" {
  if (type === "markdown") {
    return "markdown";
  }
  if (type === "sql") {
    return "sql";
  }
  return "python";
}
