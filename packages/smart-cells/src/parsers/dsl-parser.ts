/* Copyright 2026 Marimo. All rights reserved. */

import { pythonLanguage } from "@codemirror/lang-python";
import dedent from "string-dedent";
import type {
  FormatResult,
  LanguageParser,
  ParseResult,
  QuotePrefixKind,
} from "../types.js";
import { QUOTE_PREFIX_KINDS } from "../types.js";
import { splitQuotePrefix, unescapeQuotes } from "../utils/index.js";

export interface DSLMetadata {
  quotePrefix: QuotePrefixKind;
}

export interface DSLParserOptions {
  /** DSL short name, e.g. "wordmath". Becomes the parser's `type`. */
  name: string;
  /** Bare call name, e.g. "wordmath" -- an ordinary Python name, not a
   * module attribute. */
  callName: string;
}

const quoteKinds = [
  ['"""', '"""'],
  ["'''", "'''"],
  ['"', '"'],
  ["'", "'"],
] as const;

function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function buildRegexes(callName: string) {
  const pairs = QUOTE_PREFIX_KINDS.flatMap((prefix) =>
    quoteKinds.map(([start, end]) => [prefix + start, end] as const),
  );

  return pairs.map(
    ([start, end]) =>
      [
        start,
        new RegExp(
          `^${escapeRegex(callName)}\\(\\s*${escapeRegex(start)}(.*)${escapeRegex(end)}\\s*\\)$`,
          "s",
        ),
      ] as const,
  );
}

/**
 * Generic parser for a custom cell DSL whose widget was announced via
 * `register_dsl_widget`.
 *
 * Converts between Python code like `wordmath(r"""one plus two""")` and
 * the DSL's raw surface syntax, e.g. `one plus two`. This mirrors
 * `MarkdownParser`'s wrapping convention: a single positional
 * string/f-string argument to a bare Python name call.
 */
export class GenericDSLParser implements LanguageParser<DSLMetadata> {
  readonly type: string;
  readonly defaultCode: string;
  readonly defaultMetadata: DSLMetadata = { quotePrefix: "r" };

  private readonly callName: string;
  private readonly regexes: ReadonlyArray<readonly [string, RegExp]>;

  constructor(options: DSLParserOptions) {
    this.type = options.name;
    this.callName = options.callName;
    this.regexes = buildRegexes(options.callName);
    this.defaultCode = `${options.callName}(r"""\n""")`;
  }

  transformIn(pythonCode: string): ParseResult<DSLMetadata> {
    pythonCode = pythonCode.trim();

    const metadata: DSLMetadata = { ...this.defaultMetadata };

    // Empty string
    if (pythonCode === "") {
      return { code: "", offset: 0, metadata };
    }

    // Try to match against all known patterns
    for (const [start, regex] of this.regexes) {
      const match = pythonCode.match(regex);
      if (match) {
        const innerCode = match[1];
        const [quotePrefix, quoteType] = splitQuotePrefix(start);
        metadata.quotePrefix = quotePrefix;
        const unescapedCode = unescapeQuotes(innerCode, quoteType);

        const offset = pythonCode.indexOf(innerCode);
        // string-dedent expects the first and last line to be empty / contain
        // only whitespace, so we pad with \n
        return {
          code: dedent(`\n${unescapedCode}\n`).trim(),
          offset,
          metadata,
        };
      }
    }

    // No match - return original code
    return { code: pythonCode, offset: 0, metadata };
  }

  transformOut(code: string, metadata: DSLMetadata): FormatResult {
    // Empty string
    if (code === "") {
      // Need at least a space, otherwise the output will be 6 quotes
      code = " ";
    }

    const { quotePrefix } = metadata;

    // We always transform back with triple quotes, as to avoid needing to
    // escape single quotes.
    // We escape only 2 because 4 quotes in a row would end the string.
    // We escape the second quote to avoid leading backslashes escaping the
    // first quote.
    const escapedCode = code.replaceAll('""', String.raw`"\"`);

    const start = `${this.callName}(${quotePrefix}"""\n`;
    const end = `\n""")`;
    return { code: start + escapedCode + end, offset: start.length + 1 };
  }

  isSupported(pythonCode: string): boolean {
    pythonCode = pythonCode.trim();

    // Empty strings are supported
    if (pythonCode === "") {
      return true;
    }

    // Must start with <callName>(
    if (!pythonCode.startsWith(`${this.callName}(`)) {
      return false;
    }

    // Empty function calls are supported
    if (pythonCode === `${this.callName}()`) {
      return true;
    }

    // Parse the code using Lezer and check for the exact match of the
    // <callName>(...) call signature. `callName` is a bare Python name
    // (e.g. "wordmath"), so the callee is a plain VariableName -- not a
    // MemberExpression like "mo.wordmath" would parse to.
    const tree = pythonLanguage.parser.parse(pythonCode);

    const enterOrder: Array<{ match: string | RegExp; stop?: boolean }> = [
      { match: "Script" },
      { match: "ExpressionStatement" },
      { match: "CallExpression" },
      { match: "VariableName" },
      { match: "ArgList" },
      { match: "(" },
      { match: /String|FormatString/, stop: true },
      { match: ")" },
    ];

    let isValid = true;

    tree.iterate({
      enter: (node) => {
        const current = enterOrder.shift();
        if (current === undefined) {
          // If our list is empty, but we are still going
          // then this is not a valid call
          isValid = false;
          return false;
        }

        const match = current.match;

        if (typeof match === "string") {
          isValid = isValid && match === node.name;
          return isValid && !current.stop;
        }

        if (!match.test(node.name)) {
          isValid = false;
          return isValid && !current.stop;
        }

        return isValid && !current.stop;
      },
    });

    return isValid;
  }
}
