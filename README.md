# PuyoTeX

A small LaTeX package for quickly typesetting board states of Puyo Puyo games.

Supports large and small boards with arbitrary shape, hidden rows, current and next puyos, labels and move planning markers. Source code available for download on [GitHub](https://github.com/amosborne/puyotex) or your favorite TeX repository. Package requires a working [Python3](https://www.python.org/) environment in support of [PythonTeX](https://github.com/gpoore/pythontex) with packages [Pygments](https://pygments.org/) and [Numpy](https://numpy.org/). The user will need to configure their TeX build commands to include the PythonTeX mid-processing routine.

Please see the concise PuyoTeX documentation for more details on usage, installation, and known limitations.

Created by [terramyst](https://twitter.com/terramyst1).

```tex
% Example usage.
\begin{puyotikz}[\puyosmallscale]
    \puyoboard{rg/rgr/br/g}{rr/rb/gg}
    \puyomarker{e1rA/e2rA/f1bB/f2rB}
\end{puyotikz}

\puyogrid[nrows=4, ncols=4]{bbb/rrrb/gggr/yyyg}
```
