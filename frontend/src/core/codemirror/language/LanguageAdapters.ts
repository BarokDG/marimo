/* Copyright 2026 Marimo. All rights reserved. */

import { once } from "@/utils/once";
import { MarkdownLanguageAdapter } from "./languages/markdown";
import { PythonLanguageAdapter } from "./languages/python";
import { SQLLanguageAdapter } from "./languages/sql/sql";
import type { LanguageAdapter } from "./types";

// Create cached instances
const createPythonAdapter = once(() => new PythonLanguageAdapter());
const createMarkdownAdapter = once(() => new MarkdownLanguageAdapter());
const createSqlAdapter = once(() => new SQLLanguageAdapter());

// Keyed by LanguageAdapterType, but declared as Record<string, _> since
// dynamically-registered DSL adapters (see `registerCustomLanguageAdapter`)
// aren't part of a closed literal union.
export const LanguageAdapters: Record<string, LanguageAdapter> = {
  // Getters to prevent circular dependencies
  get python() {
    return createPythonAdapter();
  },
  get markdown() {
    return createMarkdownAdapter();
  },
  get sql() {
    return createSqlAdapter();
  },
};

/**
 * Register an adapter for a dynamically-registered DSL (see
 * `register_dsl_widget`), making it available via `LanguageAdapters[type]`
 * and `getLanguageAdapters()`.
 */
export function registerCustomLanguageAdapter(adapter: LanguageAdapter): void {
  Object.defineProperty(LanguageAdapters, adapter.type, {
    value: adapter,
    writable: true,
    configurable: true,
    enumerable: true,
  });
}

export function getLanguageAdapters(): LanguageAdapter[] {
  return Object.values(LanguageAdapters);
}
