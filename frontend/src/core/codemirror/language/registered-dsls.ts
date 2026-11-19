/* Copyright 2026 Marimo. All rights reserved. */

import { atom } from "jotai";
import { store } from "@/core/state/jotai";

export interface RegisteredDSL {
  name: string;
  callNames: string[];
}

const registeredDslsAtom = atom<ReadonlyMap<string, RegisteredDSL>>(new Map());

/**
 * Record a DSL registered via `register_cell_dsl` (backend notification
 * `"dsl-registered"`). Dedupes by name, keeping the latest.
 */
export function addRegisteredDsl(dsl: RegisteredDSL): void {
  const prev = store.get(registeredDslsAtom);
  const next = new Map(prev);
  next.set(dsl.name, dsl);
  store.set(registeredDslsAtom, next);
}

export const registeredDslListAtom = atom((get) => [
  ...get(registeredDslsAtom).values(),
]);
