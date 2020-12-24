# PuyoTikZ package for LaTeX.
# Created by amosborne (GitHub) / terramyst (Twitter).
# MIT License

import numpy as np
import itertools
import string
import re


# Wraps a function which returns a string. Prints the result with a ";".
def print_tikz(func):
    def wrapper(*args, **kwargs):
        print(func(*args, **kwargs) + ";")

    return wrapper


PUYO_RADIUS, PUYO_JOIN = 0.45, 0.25
COLORS = {
    "r": "red",
    "y": "yellow",
    "g": "green",
    "b": "blue",
    "p": "purple",
    "n": "gray",
}
for key, value in COLORS.items():
    COLORS[key] = value + "puyo"


def puyoboard(cols, rows, hrows, boardpuyos, nextpuyos, label):
    if not cols > 0:
        raise UserWarning("{0} columns must be atleast 1.".format(cols))
    if not rows > 0:
        raise UserWarning("{0} rows must be atleast 1.".format(rows))
    if hrows < 0:
        raise UserWarning("{0} hidden rows must be atleast 0.".format(hrows))

    draw_board(cols, rows, hrows, boardpuyos)
    draw_nextpuyos(cols, rows, nextpuyos)
    if label:
        draw_labels(cols, rows, hrows, nextpuyos)


def puyomarker(config):
    pattern = "^([a-z]+)(\d+)([rygbpn])([A-Z])$"

    @print_tikz
    def singlemark(subconfig):
        match = re.search(pattern, subconfig)
        if match is None:
            raise UserWarning("Bad puyo marker format string.")
        else:
            colid, rowid, puyo, lid = match.groups()

        rowidx = int(rowid) - 1
        colidx = next(
            idx for idx, x in enumerate(excel_cols(upper=False)) if x == colid
        )
        pos = colidx + 0.5, rowidx + 0.5

        tikz = "\\draw[{0},thick]".format("dark" + COLORS[puyo])
        tikz += " ({0},{1}) circle ({2});".format(*pos, PUYO_RADIUS)
        tikz += " \\node[anchor=center, font=\sffamily]"
        tikz += " at ({0},{1}) {{\\small {2}}}".format(*pos, lid)
        return tikz

    subconfigs = config.split("/")
    if subconfigs == [""]:
        return
    else:
        for subconfig in subconfigs:
            singlemark(subconfig)


def draw_board(cols, rows, hrows, boardpuyos):
    # draw the board grid
    draw_grid(params=["gray", "ultra thin"], size=(cols, rows))
    draw_grid(
        params=["gray", "ultra thin", "line cap=round"],
        origin=(0, rows),
        size=(cols, hrows),
    )
    draw_grid(
        params=["black", "line cap=round"], stepsize=(cols, rows), size=(cols, rows)
    )

    # draw the puyos on the board
    draw_puyos(puyos=boardpuyos.split("/"), size=(cols, rows), nhidden=hrows)


def draw_nextpuyos(cols, rows, nextpuyos):
    nextpuyos = nextpuyos.split("/")
    if nextpuyos == [""]:
        return
    for idx, puyos in enumerate(nextpuyos):
        if not len(puyos) == 2:
            raise UserWarning("Next puyos must be of length 2.")
        draw_puyos(
            puyos=[puyos], origin=(cols + 0.75, rows - 1.5 - 3 * idx), size=(1, 2)
        )


def draw_labels(cols, rows, hrows, nextpuyos):
    @print_tikz
    def draw_label(pos, text, size="\\normalsize", style="\\rmfamily"):
        return "\\node[anchor=mid, font={4}] at ({0},{1}) {{{3} {2}}}".format(
            *pos, text, size, style
        )

    for idx in range(0, rows + hrows):
        draw_label((-0.5, 0.5 + idx), idx + 1)

    for idx, label in zip(range(0, cols), excel_cols(upper=False)):
        draw_label((0.5 + idx, -0.5), label)

    nextpuyoscount = len(nextpuyos.split("/"))
    if nextpuyos.split("/") == [""]:
        return
    for idx, label in zip(range(0, nextpuyoscount), excel_cols(upper=True)):
        draw_label((cols + 0.75, rows - 1.5 - 3 * idx), label, "\\small", "\\sffamily")


@print_tikz
def draw_grid(params=[], origin=(0, 0), stepsize=(1, 1), size=(6, 12)):
    extent = tuple([x + y for x, y in zip(origin, size)])
    tikz = "\\draw"
    tikz += "[" + ",".join(params) + "]"
    tikz += " ({0},{1})".format(*origin)
    tikz += " grid [xstep={0},ystep={1}]".format(*stepsize)
    tikz += " ({0},{1})".format(*extent)
    return tikz


def draw_puyos(puyos=[], origin=(0, 0), size=(6, 12), nhidden=0):
    # construct a 2D matrix of strings (representing puyos)
    board = np.full((size[0], size[1] + nhidden), "")
    for ridx, col in enumerate(puyos):
        for cidx, puyo in enumerate(list(col)):
            if puyo not in COLORS.keys():
                raise UserWarning(
                    "{0} is not a valid puyo identifier (rygbpn).".format(puyo)
                )
            try:
                board[ridx, cidx] = puyo
            except IndexError:
                raise UserWarning("Puyo layout string has too many rows or columns.")

    # helper function for converting true position
    def true_pos(pos):
        return tuple([x + y + 0.5 for x, y in zip(pos, origin)])

    # draw all the puyo circles
    for pos, puyo in np.ndenumerate(board):
        if puyo:
            draw_puyo(true_pos(pos), puyo)

    # connect to adjacent puyos (except nuisance and hidden row)
    for pos, puyo in np.ndenumerate(board):
        for direc in {(1, 0), (-1, 0), (0, 1), (0, -1)}:
            if not 0 <= pos[0] + direc[0] < board.shape[0]:
                continue
            elif not 0 <= pos[1] + direc[1] < board.shape[1] - nhidden:
                continue
            elif not 0 <= pos[1] < board.shape[1] - nhidden:
                continue

            other = board[pos[0] + direc[0], pos[1] + direc[1]]
            if puyo and other == puyo and puyo != "n":
                connect_puyo(true_pos(pos), direc, puyo)

    # draw all the puyo faces
    for pos, puyo in np.ndenumerate(board):
        if puyo:
            draw_face(true_pos(pos), puyo)

    # outline the puyos with a darker color
    for pos, puyo in np.ndenumerate(board):
        for direc in {(1, 0), (-1, 0), (0, 1), (0, -1)}:
            if not 0 <= pos[0] + direc[0] < board.shape[0]:
                if puyo:
                    outline_puyo(true_pos(pos), direc, puyo, join=False)
                continue
            elif not 0 <= pos[1] + direc[1] < board.shape[1] - nhidden:
                if puyo:
                    outline_puyo(true_pos(pos), direc, puyo, join=False)
                continue
            elif not 0 <= pos[1] < board.shape[1] - nhidden:
                if puyo:
                    outline_puyo(true_pos(pos), direc, puyo, join=False)
                continue

            other = board[pos[0] + direc[0], pos[1] + direc[1]]
            if puyo and other == puyo and puyo != "n":
                outline_puyo(true_pos(pos), direc, puyo, join=True)
            elif puyo:
                outline_puyo(true_pos(pos), direc, puyo, join=False)


@print_tikz
def draw_face(pos=(0, 0), puyo="r"):
    def tikz_shift(shift=(0, 0)):
        total_shift = pos[0] + shift[0], pos[1] + shift[1]
        return "[xshift={0}cm,yshift={1}cm]".format(*total_shift)

    tikz = "\\draw[white,semithick]"
    if puyo == "p":
        tikz += " ({0}150:{1}) -- ({0}-30:{1});".format(tikz_shift(), PUYO_RADIUS)
    elif puyo == "r":
        tikz += " ({0}150:{1}) -- ({0}0,0) -- ({0}30:{1});".format(
            tikz_shift(), PUYO_RADIUS
        )
    elif puyo == "g":
        tikz += " ({0}-90:{1}) arc (-90:0:{1})".format(
            tikz_shift((-PUYO_RADIUS, PUYO_RADIUS)), PUYO_RADIUS
        )
        tikz += " ({0}-90:{1}) arc (-90:-180:{1});".format(
            tikz_shift((PUYO_RADIUS, PUYO_RADIUS)), PUYO_RADIUS
        )
    elif puyo == "b":
        tikz += " ({0}180:{1}) -- ({0}90:{2}) -- ({0}0:{1});".format(
            tikz_shift(), PUYO_RADIUS, PUYO_RADIUS * np.sin(np.deg2rad(30))
        )
    elif puyo == "y":
        tikz += " ({0}150:{1}) -- ({0}30:{1});".format(tikz_shift(), PUYO_RADIUS)
    elif puyo == "n":
        tikz += " ({0}210:{1}) -- ({0}-30:{1});".format(tikz_shift(), PUYO_RADIUS)
    else:
        tikz = ""

    return tikz


@print_tikz
def draw_puyo(pos=(0, 0), puyo="r"):
    tikz = "\\draw[{0},fill={0}]".format(COLORS[puyo])
    tikz += " ({0},{1}) circle ({2})".format(*pos, PUYO_RADIUS)
    return tikz


@print_tikz
def connect_puyo(pos=(0, 0), direc=(1, 0), puyo="r"):
    phi, join1, join2 = connect_puyo_params(pos, direc)
    tikz = "\\draw[{0},fill={0}]".format(COLORS[puyo])
    tikz += " ([xshift={0}cm,yshift={1}cm]".format(*pos)
    tikz += "{0}:{2}) arc ({0}:{1}:{2})".format(phi - 45, phi + 45, PUYO_RADIUS)
    tikz += " to[out={0},in={1}] ({2},{3})".format(phi - 45, phi - 180, *join1)
    tikz += " -- ({0},{1})".format(*join2)
    tikz += " to[out={0},in={1}] cycle".format(phi - 180, phi + 45)
    return tikz


@print_tikz
def outline_puyo(pos=(0, 0), direc=(1, 0), puyo="r", join=False):
    phi, join1, join2 = connect_puyo_params(pos, direc)
    tikz = "\\draw[{0}]".format("dark" + COLORS[puyo])

    if join:
        tikz += " ([xshift={0}cm,yshift={1}cm]".format(*pos)
        tikz += "{0}:{1})".format(phi + 45, PUYO_RADIUS)
        tikz += " to[out={0},in={1}] ({2},{3})".format(phi - 45, phi - 180, *join1)
        tikz += " ({0},{1})".format(*join2)
        tikz += " to[out={0},in={1}]".format(phi - 180, phi + 45)
        tikz += " ([xshift={0}cm,yshift={1}cm]".format(*pos)
        tikz += "{0}:{1})".format(phi - 45, PUYO_RADIUS)
    else:
        tikz += " ([xshift={0}cm,yshift={1}cm]".format(*pos)
        tikz += "{0}:{2}) arc ({0}:{1}:{2})".format(phi - 45, phi + 45, PUYO_RADIUS)

    return tikz


def connect_puyo_params(pos, direc):
    """Determine the path angle and midpoint locations."""
    phi = np.rad2deg(np.arctan2(direc[1], direc[0])) % 360
    x, y1, y2 = 0.5, PUYO_JOIN, -PUYO_JOIN

    c, s = np.cos(np.deg2rad(phi)), np.sin(np.deg2rad(-phi))
    j = np.matrix([[c, s], [-s, c]])

    def rotate_point(y):
        m = np.dot(j, [x, y])
        return float(m.T[0]) + pos[0], float(m.T[1]) + pos[1]

    return phi, rotate_point(y1), rotate_point(y2)


def excel_cols(upper=True):
    n = 1
    letters = string.ascii_uppercase if upper else string.ascii_lowercase
    while True:
        yield from ("".join(group) for group in itertools.product(letters, repeat=n))
        n += 1
