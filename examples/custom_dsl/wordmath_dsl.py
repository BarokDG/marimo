# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo",
# ]
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Custom DSL cells: a word-math example

    This notebook demos an **in-progress, unshipped** mechanism for
    registering custom non-SQL "DSL cells" -- generalizing the way
    `mo.sql(...)` cells work today so other DSLs can plug in the same
    way, without marimo core needing to special-case each one.

    `CellDSL` and `register_cell_dsl` live in **private** modules
    (`marimo._ast.dsl`, `marimo._ast.dsl_registry`) and are **not** a
    public API yet -- this notebook is for trying the mechanism out,
    not a feature to build on.
    """)


@app.cell
def _():
    from marimo._ast.dsl import CellDSL
    from marimo._ast.dsl_registry import register_cell_dsl

    _WORD_TO_NUM = {
        "zero": 0,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
    }
    _NUM_TO_WORD = {v: k for k, v in _WORD_TO_NUM.items()}

    class WordMathDSL(CellDSL):
        """Sums whitespace-separated number-words, e.g.

        `"one two three"` -> `"six"`. No cross-cell refs/defs, so it uses
        `CellDSL`'s no-op defaults for everything except `name`/`execute`.
        """

        @property
        def name(self) -> str:
            return "wordmath"

        def execute(self, source: str) -> str:
            tokens = source.strip().split()
            total = sum(_WORD_TO_NUM[token] for token in tokens)
            return _NUM_TO_WORD[total]

        def input_widget_esm(self) -> str:
            return """
            const STYLE = `
              .wordmath-text-widget {
                display: flex;
                flex-direction: column;
                gap: 8px;
                padding: 12px 14px;
                border: 1px solid #0f0;
                border-radius: 2px;
                background: #000;
                box-shadow: 0 0 10px rgba(0, 255, 65, 0.35), inset 0 0 20px rgba(0, 255, 65, 0.05);
                font-family: "Courier New", Consolas, monospace;
              }
              .wordmath-text-widget .wordmath-code {
                font-family: inherit;
                font-size: 13px;
                color: #00ff41;
                text-shadow: 0 0 6px rgba(0, 255, 65, 0.8);
                background: #000;
                border: 1px dashed rgba(0, 255, 65, 0.4);
                border-radius: 2px;
                padding: 6px 10px;
                min-height: 1.2em;
              }
              .wordmath-text-widget .wordmath-code::before {
                content: "> ";
                opacity: 0.7;
              }
              .wordmath-text-widget .wordmath-code.is-empty {
                color: rgba(0, 255, 65, 0.4);
                font-style: italic;
                text-shadow: none;
              }
              .wordmath-text-widget .wordmath-row {
                display: flex;
                gap: 6px;
              }
              .wordmath-text-widget input {
                flex: 1;
                min-width: 0;
                padding: 6px 10px;
                font-size: 13px;
                font-family: inherit;
                color: #00ff41;
                caret-color: #00ff41;
                background: #000;
                border: 1px solid #0f0;
                border-radius: 2px;
                outline: none;
              }
              .wordmath-text-widget input::placeholder {
                color: rgba(0, 255, 65, 0.35);
              }
              .wordmath-text-widget input:focus {
                box-shadow: 0 0 8px rgba(0, 255, 65, 0.9);
              }
              .wordmath-text-widget button {
                padding: 6px 14px;
                font-size: 13px;
                font-weight: 700;
                font-family: inherit;
                letter-spacing: 0.05em;
                text-transform: uppercase;
                border-radius: 2px;
                cursor: pointer;
                border: 1px solid #0f0;
                background: #000;
                color: #00ff41;
                transition: background 0.1s, color 0.1s;
              }
              .wordmath-text-widget button:hover {
                background: #00ff41;
                color: #000;
                box-shadow: 0 0 10px rgba(0, 255, 65, 0.8);
              }
              .wordmath-text-widget button.wordmath-clear {
                border-color: rgba(0, 255, 65, 0.4);
                color: rgba(0, 255, 65, 0.6);
              }
            `;

            class WordmathWidget extends HTMLElement {
              connectedCallback() {
                const shadow = this.attachShadow({ mode: "open" });
                const words = this.code
                  ? this.code.trim().split(/\\s+/).filter(Boolean)
                  : [];

                const style = document.createElement("style");
                style.textContent = STYLE;

                const container = document.createElement("div");
                container.className = "wordmath-text-widget";

                const list = document.createElement("div");
                list.className = "wordmath-code";

                const updateList = () => {
                  const hasWords = words.length > 0;
                  list.textContent = hasWords ? words.join(" ") : "(empty)";
                  list.classList.toggle("is-empty", !hasWords);
                };
                updateList();

                const row = document.createElement("div");
                row.className = "wordmath-row";

                const input = document.createElement("input");
                input.type = "text";
                input.placeholder = "type a number word, e.g. one";

                const addWord = () => {
                  const value = input.value.trim();
                  if (!value) return;
                  words.push(value);
                  this.setCode(words.join(" "));
                  input.value = "";
                  updateList();
                };

                input.addEventListener("keydown", (e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    addWord();
                  }
                });

                const addButton = document.createElement("button");
                addButton.type = "button";
                addButton.className = "wordmath-add";
                addButton.textContent = "Add";
                addButton.onclick = addWord;

                const clearButton = document.createElement("button");
                clearButton.type = "button";
                clearButton.className = "wordmath-clear";
                clearButton.textContent = "Clear";
                clearButton.onclick = () => {
                  words.length = 0;
                  this.setCode("");
                  updateList();
                };

                row.append(input, addButton, clearButton);
                container.append(list, row);
                shadow.replaceChildren(style, container);
              }
            }

            export default WordmathWidget;
            export const tagName = "wordmath-widget";
            """

    register_cell_dsl(WordMathDSL())


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    Try editing the string below (e.g. to `"four five"`) and watch the
    cell -- and the one after it -- react, exactly like any other
    Python cell.
    """)


@app.cell
def _(mo):
    mo.wordmath(r"""
    two = 'three'
    """)


@app.cell
def _(mo, two):
    mo.wordmath(f"one {two} four")


if __name__ == "__main__":
    app.run()
