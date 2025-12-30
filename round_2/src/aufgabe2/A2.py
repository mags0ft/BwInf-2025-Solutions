#!/usr/bin/python3

"""
Lösung für die Aufgabe 2 ("Labyrinthe") der 2. Runde des 43. Bundeswettbewerbes
Informatik.
"""

from argparse import ArgumentParser, BooleanOptionalAction, Namespace
from collections import deque
from errno import EINVAL, ENOENT
from io import TextIOWrapper
import os
import sys
import time
import traceback
from typing import List, Tuple


p = ArgumentParser(prog="labyrinthe")
p.add_argument("file", help="Die einzulesende Eingabedatei.")
p.add_argument(
    "--time",
    action=BooleanOptionalAction,
    help="Ob eine Laufzeitmessung durchgeführt werden soll.",
)


class ParseError(Exception):
    """
    Ein Fehler, der bei einer unlesbaren Eingabedatei ausgegeben wird.
    """


class InvalidMazeException(Exception):
    """
    Exception für ungültige Labyrinthzustände.
    """


# Wir fertigen uns einige Typen vor, das spart nachher Tipparbeit.
Coord = Tuple[int, int]
Direction = Tuple[int, int]
CoordPair = Tuple[Coord, Coord]
Maze = List[List[int]]
MazePair = Tuple[Maze, Maze]


# Nun die Richtungen, die wir im Labyrinth jeweils einschlagen können.
DIR_UP: Direction = (0, -1)
DIR_RIGHT: Direction = (1, 0)
DIR_DOWN: Direction = (0, 1)
DIR_LEFT: Direction = (-1, 0)


# Für die Speichereffizienz kodieren wir Richtungen in Integern statt Tupeln.
DIR_MAP: "dict[Direction, int]" = {
    DIR_UP: 0,
    DIR_RIGHT: 1,
    DIR_DOWN: 2,
    DIR_LEFT: 3,
}

DIR_MAP_INV: "dict[int, Direction]" = {v: k for k, v in DIR_MAP.items()}

# Ebenfalls ein paar bitweise Flags, die uns später sehr kosteneffizient den
# Weg weisen werden!
FLAG_WALL_UP: int = 1
FLAG_WALL_RIGHT: int = 1 << 1
FLAG_WALL_DOWN: int = 1 << 2
FLAG_WALL_LEFT: int = 1 << 3
FLAG_PIT: int = 1 << 4

# Jetzt weisen wir jeder Richtung eine Flag zu, um - dank dem Dictionary -
# später aufgrund der Eigenschaften einer Hashmap schnell und günstig zwischen
# Richtung und Flag konvertieren können.
WALL_DIR_MAPPINGS: "dict[Direction, int]" = {
    DIR_UP: FLAG_WALL_UP,
    DIR_RIGHT: FLAG_WALL_RIGHT,
    DIR_DOWN: FLAG_WALL_DOWN,
    DIR_LEFT: FLAG_WALL_LEFT,
}

# Ebenfalls anlegen tun wir uns dieses kleine Hilfs-Dictionary, das uns später
# die Richtungen in schön lesbare Zeichen umwandelt.
HUMAN_READABLE_DIRS: "dict[Direction, str]" = {
    DIR_UP: "↑",
    DIR_RIGHT: "→",
    DIR_DOWN: "↓",
    DIR_LEFT: "←",
}


def enc(t: CoordPair) -> int:
    """
    Kodiert die speicherintensiven Koordinatenpaare mit bitweiser Logik, um
    Arbeitsspeicher zu sparen. Diese Funktion sollte sehr schnell sein, da sie
    nur bitweise Operationen enthält und eine Loop von Hand unrolled ist.
    """

    r = 0b0
    r |= t[0][0]
    r |= t[0][1] << 8
    r |= t[1][0] << 16
    r |= t[1][1] << 24

    return r


def dec(n: int) -> CoordPair:
    """
    Dekodiert die speichereffizienten Integer zurück zu Koordinatenpaaren.
    """

    a = n & 0xFF
    b = (n >> 8) & 0xFF
    c = (n >> 16) & 0xFF
    d = n >> 24

    return ((a, b), (c, d))


def clamp(num: int, min_: int, max_: int):
    """
    Beschränkt eine Zahl auf einen festgelegten Bereich; sollte die Zahl
    darunter sein, wird diese auf das festgelegte Minimum limitiert - sollte
    sie darüber sein, auf das Maximum.
    """

    return min_ if num < min_ else (max_ if num > max_ else num)


def get_point_in_maze(mazes: MazePair, player: int, x: int, y: int):
    """
    Hilfsfunktion, um Verwirrung und Fehler zu vermeiden. Mag unnötig wirken,
    jedoch ist es sehr unintuitiv, dass bei einer zweidimensionalen Liste die
    y-Koordinate vor der x-Koordinate (zumindest in diesem Setup hier)
    adressiert wird. Diese Funktion abstrahiert.
    """

    return mazes[player][y][x]


def generate_next_positions(
    cur_pos: CoordPair, max_boundary: Coord, mazes: MazePair
):
    """
    Passt die Positionen beider Spieler*innen in Hinblick auf jede Richtung an.
    """

    for dir_ in [DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT]:
        next_pos = [(0, 0), (0, 0)]
        for player in [0, 1]:
            cur_player_pos = cur_pos[player]

            if (
                get_point_in_maze(
                    mazes, player, cur_player_pos[0], cur_player_pos[1]
                )
                & WALL_DIR_MAPPINGS[dir_]  # ein Wenig bitwise-Magie! :)
            ) or cur_player_pos == max_boundary:
                # Hier laufen wir gegen eine Wand oder sind bereits am Ziel -
                # also tun wir stattdessen nichts!
                next_pos[player] = cur_player_pos
                continue

            next_player_pos = (
                clamp(cur_player_pos[0] + dir_[0], 0, max_boundary[0]),
                clamp(cur_player_pos[1] + dir_[1], 0, max_boundary[1]),
            )

            if (
                get_point_in_maze(
                    mazes, player, next_player_pos[0], next_player_pos[1]
                )
                & FLAG_PIT
            ):
                # Hier fallen wir in ein Loch, also gehen wir zurück zu (0, 0)!
                next_player_pos = (0, 0)

            next_pos[player] = next_player_pos

        if tuple(next_pos) == cur_pos:
            # Hatten wir schon, müssen wir nicht in Betracht ziehen.
            continue

        yield (next_pos[0], next_pos[1]), dir_


def trace_mazes(
    mazes: MazePair,
) -> "tuple[dict[int, Tuple[int, int]], CoordPair, bool]":
    """
    Benutzt Spread-First-Suche (bzw. Breadth-First-Search, BFS), um den
    schnellstmöglichen Weg für beide Spieler*innen in den Labyrinthen zugleich
    zu ermitteln.

    Gibt dann ein Dictionary zurück, dass für jedes besuchte Koordinatenpaar
    aufzeichnet, durch welches Koordinatenpaar und welche Richtung man auf
    ebendieses kommen kann.

    Daraus lässt sich dann der Weg rekonstruieren.
    """

    # Zuerst überprüfen wir, ob die Eingabe fehlerfrei ist.
    for idx, maze in enumerate(mazes, 1):
        if len(maze) == 0 or len(maze[0]) == 0:
            raise InvalidMazeException(f"Leeres Labyrinth #{idx}.")
        if any(len(el) != len(maze[0]) for el in maze):
            raise InvalidMazeException(
                f"Ungleich lange Zeilen im Labyrinth #{idx}!"
            )

    # Ob wir das Ziel gefunden haben
    success: bool = False

    start_coords, goal_coords = (0, 0), (
        len(mazes[0][0]) - 1,
        len(mazes[0]) - 1,
    )

    goal_pos: CoordPair = (goal_coords, goal_coords)

    # für beide Spieler*innen im Labyrinth behalten wir die Positionen im Auge.
    begin_pos: CoordPair = (start_coords, start_coords)

    # Die Queue brauchen wir für unsere Spread-First-Suche
    queue: "deque[int]" = deque([enc(begin_pos)])

    # Zeichnet auf, durch welches Feld und welche Anweisung man auf ein anderes
    # Feld kommen kann. Somit können wir danach zurückverfolgen, wie unser
    # Pfad geht. Im Grunde das Gleiche wie bei vielen Wegfindungsalgorithmen,
    # nur dass hier zwei Felder zugleich (für Labyrinth 1 und 2 simultan!)
    # im Blick behalten werden.
    trace: "dict[int, Tuple[int, int]]" = {}

    while len(queue) != 0:
        cur_pos = dec(queue.popleft())

        if cur_pos == goal_pos:
            # Super! Beide Spieler*innen haben das Ziel erreicht.
            success = True
            break

        for new_pos, dir_ in generate_next_positions(
            cur_pos, goal_coords, mazes
        ):
            enc_new_pos: int = enc(new_pos)

            if enc_new_pos in trace:
                # Wir waren hier schon.
                continue

            # Jetzt packen wir alles auf die Queue, damit wir es gleich nicht
            # vergessen, auch noch zu traversieren! ;)
            queue.append(enc_new_pos)

            # Wir hinterlassen uns für später zudem die Spur:
            trace[enc_new_pos] = (enc(cur_pos), DIR_MAP[dir_])

    return trace, goal_pos, success


def reconstruct_path_from_trace(
    trace: "dict[int, Tuple[int, int]]", goal_pos: CoordPair
) -> "tuple[str, int]":
    """
    Baut aus den Aufzeichnungen zu den Koordinatenpaaren durch Rückverfolgung
    des Lösungsweges einen optimalen Pfad auf.
    """

    # Nun müssen wir nur noch zurückverfolgen, wie unser Weg war!
    optimal_path: "list[Direction]" = []
    cur_pos = enc(goal_pos)

    # Solange wir nicht wieder zurück zum Anfang gefunden haben ...
    while dec(cur_pos) != ((0, 0), (0, 0)):
        # ... verfolgen wir die Spur, die wir uns zuvor hinterlassen haben.
        cur_pos, dir_ = trace[cur_pos]
        optimal_path.insert(0, DIR_MAP_INV[dir_])

    # Jetzt wandeln wir sie in menschenlesbare Form um.
    return " ".join([HUMAN_READABLE_DIRS[step] for step in optimal_path]), len(
        optimal_path
    )


def parse_input_file(filename: str) -> MazePair:
    """
    Liest die Eingabedatei ein.
    """
    # pylint: disable=raise-missing-from,too-many-branches

    mazes: "list[Maze]" = [[], []]

    def parse_structure_line(f: TextIOWrapper):
        """
        Wandelt eine Textzeile aus der Eingabedatei in eine Liste aus Booleans
        um.
        """

        return [el == "1" for el in f.readline().strip().split()]

    with open(filename, "r", encoding="utf-8") as f:
        try:
            # Wir lesen Höhe und Breite ein.
            width, height = (int(s) for s in f.readline().strip().split())
        except ValueError:
            raise ParseError("Die Werte in der Ersten Zeile sind fehlgeformt.")

        for maze in [0, 1]:
            # Zuerst füllen wir unsere Labyrinthe mit Nullen.
            mazes[maze] = [[0 for _b in range(width)] for _a in range(height)]

            for row in range(height):
                # Das wird jetzt etwas komplizierter; für jedes Feld setzen wir
                # die entsprechenden binären Flags. Dies verschnellert später
                # unsere Ausführungsgeschwindigkeit.

                for col, is_wall in enumerate(parse_structure_line(f)):
                    if not is_wall:
                        continue
                    mazes[maze][row][col] |= FLAG_WALL_RIGHT

                    if col == width - 1:
                        continue

                    # Natürlich müssen wir die Flag auch umgekehrt in dem
                    # angrenzenden Feld setzen, wenn möglich.
                    mazes[maze][row][col + 1] |= FLAG_WALL_LEFT

            for row in range(height - 1):
                # Die gleiche Vorgehensweise noch einmal hier:
                for col, is_wall in enumerate(parse_structure_line(f)):
                    if not is_wall:
                        continue
                    mazes[maze][row][col] |= FLAG_WALL_DOWN

                    if row == height - 1:
                        continue
                    mazes[maze][row + 1][col] |= FLAG_WALL_UP

            try:
                # Nun lesen wir die Menge an Gruben aus.
                num_pits = int(f.readline().strip())
            except ValueError:
                raise ParseError("Die Anzahl der Gruben ist fehlgeformt.")

            for idx in range(num_pits):
                try:
                    pit_x, pit_y = [
                        int(c) for c in f.readline().strip().split()
                    ]
                except ValueError:
                    raise ParseError(
                        f"Die Koordinaten der {idx}. Grube sind fehlgeformt."
                    )

                # Die Flag für Gruben setzen:
                mazes[maze][pit_y][pit_x] |= FLAG_PIT

    return (mazes[0], mazes[1])


def main() -> int:
    """
    Die Hauptmethode für das Programm, welche sich um das Einlesen der Datei
    und den initialen Programmfluss kümmert.
    """

    arguments: Namespace = p.parse_args()
    filename: str = arguments.file

    # Wir versuchen, die Eingabedatei einzulesen:

    if not os.path.isfile(filename):
        print(f"{filename}: Datei oder Verzeichnis nicht gefunden")
        return -ENOENT

    try:
        mazes = parse_input_file(filename)
    except ParseError as e:
        traceback.print_exception(e)
        return -EINVAL

    print(
        "Labyrinthe werden gelöst - dies kann, abhängig von deren Größe, \
dauern und viel Arbeitsspeicher beanspruchen."
    )

    start_time: float = time.time()

    # Nun werden die Labyrinthe mit der BFS durchsucht und Traces generiert.
    trace, goal_pos, success = trace_mazes(mazes)

    if not success:
        # Geht dies nicht, weil die BFS einfach ein eine leere Queue läuft,
        # kann das Labyrinth nicht lösbar sein. Wir beenden mit EINVAL.
        print("Labyrinthpaar nicht lösbar.")
        return -EINVAL

    # Ansonsten bauen wir nun den gegangenen Pfad auf.
    path, num_steps = reconstruct_path_from_trace(trace, goal_pos)

    end_time: float = time.time()

    print(
        f"Optimaler Pfad konnte ermittelt werden ({num_steps} Schritte). \
Lösung:",
        path,
        sep="\n",
    )

    # Zu guter Letzt geben wir, wenn das entsprechende Argument vorhanden war,
    # noch die benötigte Zeit aus.
    if arguments.time:
        delta_time: float = end_time - start_time
        print(f"Benötigte Zeit: {delta_time:.3f}s")

    # Alles hat funktioniert, Exit-Code 0.
    return 0


if __name__ == "__main__":
    ret_code: int = main()
    sys.exit(ret_code)
