# PuyoTikZ

A LaTeX package for quickly typesetting board states of Puyo Puyo games.

Supports large and small boards with arbitrary shape, hidden rows, current and next puyos, labels and move planning markers. Source code available for download on [GitHub](https://github.com/amosborne/puyotikz) or your favorite TeX repository. Package requires [Python3](https://www.python.org/) in support of scripts driven by [PythonTeX](https://github.com/gpoore/pythontex).

Please see the PuyoTikZ documentation for more details on usage, installation, and known limitations.

Created by [terramyst](https://twitter.com/terramyst1).

MIT License.

```tex
% Example usage.
\usepackage{puyotikz}

\begin{puyotikz}[\puyosmallscale]
    \puyoboard{rg/rgr/br/g}{rr/rb/gg}
    \puyomarker{e1rA/e2rA/f1bB/f2rB}
\end{puyotikz}

\puyogrid[nrows=4, ncols=4]{bbb/rrrb/gggr/yyyg}
```
