"""A standalone, importable marimo custom-DSL extension.

`DrawMathDSL` implements `CellDSL` with a draw-to-input custom widget
instead of a text box -- click or drag across cells on a tiny pixel grid
to draw a digit, recognized against a handful of hardcoded templates --
deliberately the simplest thing that can draw and recognize digits, not
real digit recognition.

Editing this file requires restarting the notebook's kernel to pick up
changes (Python caches imports) -- there's no reload mechanism wired up
here.
"""

from marimo._ast.dsl import CellDSL


class DrawMathDSL(CellDSL):
    """Sums digits drawn one at a time on a tiny pixel grid, e.g.
    drawing `4` then `8` -> `12`."""

    def execute(self, source: str) -> int:
        digits = source.strip().split()
        return sum(int(d) for d in digits)

    def input_widget_esm(self) -> str:
        return _DRAWMATH_WIDGET_ESM


_DRAWMATH_WIDGET_ESM = """
const COLS = 3;
const ROWS = 5;

// A tiny 3x5 pixel font for 0-9, read row-major. Recognition is
// just "which template has the most matching cells" -- no
// threshold/rejection, no ML, by design.
const TEMPLATES = {
  "0": "###" + "#.#" + "#.#" + "#.#" + "###",
  "1": ".#." + "##." + ".#." + ".#." + "###",
  "2": "###" + "..#" + "###" + "#.." + "###",
  "3": "###" + "..#" + "###" + "..#" + "###",
  "4": "#.#" + "#.#" + "###" + "..#" + "..#",
  "5": "###" + "#.." + "###" + "..#" + "###",
  "6": "###" + "#.." + "###" + "#.#" + "###",
  "7": "###" + "..#" + "..#" + "..#" + "..#",
  "8": "###" + "#.#" + "###" + "#.#" + "###",
  "9": "###" + "#.#" + "###" + "..#" + "###",
};

function recognize(cells) {
  let best = "0";
  let bestScore = -1;
  for (const [digit, pattern] of Object.entries(TEMPLATES)) {
    let score = 0;
    for (let i = 0; i < cells.length; i++) {
      if ((pattern[i] === "#") === cells[i]) score++;
    }
    if (score > bestScore) {
      bestScore = score;
      best = digit;
    }
  }
  return best;
}

class DrawmathWidget extends HTMLElement {
  connectedCallback() {
    const shadow = this.attachShadow({ mode: "open" });

    const style = document.createElement("style");
    style.textContent = `
      .drawmath-widget {
        font-family: monospace;
        display: flex;
        flex-direction: column;
        gap: 8px;
        padding: 10px;
      }
      .drawmath-digits {
        min-height: 1.2em;
      }
      .drawmath-grid {
        display: grid;
        grid-template-columns: repeat(${COLS}, 20px);
        grid-template-rows: repeat(${ROWS}, 20px);
        gap: 2px;
      }
      .drawmath-cell {
        border: 1px solid #888;
        cursor: pointer;
      }
      .drawmath-cell.on {
        background: #333;
      }
      .drawmath-row {
        display: flex;
        gap: 6px;
      }
      button {
        padding: 4px 10px;
        cursor: pointer;
      }
    `;

    const digits = this.code
      ? this.code.trim().split(/\\s+/).filter(Boolean)
      : [];
    let cells = new Array(COLS * ROWS).fill(false);

    const container = document.createElement("div");
    container.className = "drawmath-widget";

    const digitsLine = document.createElement("div");
    digitsLine.className = "drawmath-digits";
    const updateDigitsLine = () => {
      digitsLine.textContent = digits.length
        ? digits.join(" ")
        : "(no digits yet)";
    };
    updateDigitsLine();

    // Click toggles one cell; press-and-drag paints a whole
    // stroke with whatever value the first cell toggled to.
    let isPointerDown = false;
    let paintValue = true;
    const paintCell = (i, cellEl) => {
      cells[i] = paintValue;
      cellEl.classList.toggle("on", paintValue);
    };

    const grid = document.createElement("div");
    grid.className = "drawmath-grid";
    const cellEls = cells.map((_, i) => {
      const cellEl = document.createElement("div");
      cellEl.className = "drawmath-cell";
      cellEl.addEventListener("mousedown", (e) => {
        e.preventDefault(); // avoid dragging a text selection
        isPointerDown = true;
        paintValue = !cells[i];
        paintCell(i, cellEl);
      });
      cellEl.addEventListener("mouseenter", () => {
        if (isPointerDown) paintCell(i, cellEl);
      });
      grid.append(cellEl);
      return cellEl;
    });

    const onMouseUp = () => {
      isPointerDown = false;
    };
    document.addEventListener("mouseup", onMouseUp);
    this._cleanup = () =>
      document.removeEventListener("mouseup", onMouseUp);

    const resetGrid = () => {
      cells = cells.map(() => false);
      cellEls.forEach((cellEl) => cellEl.classList.remove("on"));
    };

    const row = document.createElement("div");
    row.className = "drawmath-row";

    const addButton = document.createElement("button");
    addButton.type = "button";
    addButton.textContent = "Add digit";
    addButton.onclick = () => {
      digits.push(recognize(cells));
      this.setCode(digits.join(" "));
      updateDigitsLine();
      resetGrid();
    };

    const clearButton = document.createElement("button");
    clearButton.type = "button";
    clearButton.textContent = "Clear";
    clearButton.onclick = () => {
      digits.length = 0;
      this.setCode("");
      updateDigitsLine();
      resetGrid();
    };

    row.append(addButton, clearButton);
    container.append(digitsLine, grid, row);
    shadow.replaceChildren(style, container);
  }

  disconnectedCallback() {
    this._cleanup?.();
  }
}

export default DrawmathWidget;
export const tagName = "drawmath-widget";
"""
