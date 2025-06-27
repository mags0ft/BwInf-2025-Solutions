#!/usr/bin/python3

"""
Mögliche Lösung für die Aufgabe 1 der zweiten Runde des 43. Bundeswettbewerbs
Informatik, "Schmucknachrichten".
"""

from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from collections import OrderedDict
from copy import deepcopy
from errno import EINVAL, ENOENT
from math import inf
import os
import string
import sys
import traceback
import time


# Wir bereiten unseren ArgumentParser vor, damit wir eine schöne Terminal-
# Anwendung erhalten.
p = ArgumentParser(prog="schmucknachrichten")
p.add_argument("file", help="Die einzulesende Eingabedatei.")
p.add_argument(
    "--tree",
    action=BooleanOptionalAction,
    help="Ob der generierte Huffman-Baum visualisiert werden soll.",
)
p.add_argument(
    "--verbose",
    action=BooleanOptionalAction,
    help="Ob noch weitere Informationen zusätzlich ausgegeben werden sollen.",
)
p.add_argument(
    "--time",
    action=BooleanOptionalAction,
    help="Ob eine Laufzeitmessung durchgeführt werden soll.",
)
p.add_argument(
    "--compact",
    action=BooleanOptionalAction,
    help="Ob die Ausgabe der Tabelle kompakter gehalten werden soll.",
)


# Wir geben den Perlen Namen, um sie auseinanderhalten zu können
# und die Äste im Huffman-Baum zu bezeichnen.
PEARL_NAMES = string.ascii_letters + string.digits


class ParseError(Exception):
    """
    Ein Fehler, der bei einer unlesbaren Eingabedatei ausgegeben wird.
    """


class TreeConstructionError(Exception):
    """
    Fehler, sollte der Baum unkonstruierbar sein (z.B. wenn d < 2).
    """


class HuffmanNode:
    """
    Ein Huffman-Knoten im n-ären Huffman-Baum mit ungleichen
    Encodingalphabetkosten.
    """

    # wie häufig der Knoten (Summe der Unterknoten oder Leaf-Node selbst) im
    # Text vorkommt
    frequency = 0

    # ggf. die Unterknoten des Knotens
    children = []

    # wenn Leaf Node: Buchstabe, den der Knoten repräsentiert
    char = ""

    # dem Ast, der zu diesem Knoten führt, zugewiesener Encoding-Buchstabe
    assigned_code = ""

    def is_leaf(self) -> bool:
        """
        Überprüft, ob es sich um einen Leaf Node (Endknoten) handelt.
        """

        return self.char != "" and not self.children

    def __init__(
        self,
        char: str,
        children: "list[HuffmanNode]",
        freq: int,
        assigned_code: str = "",
    ) -> None:
        """
        Initialisierungsmethode, die die Werte zuweist.
        """

        self.char: str = char
        self.children: "list[HuffmanNode]" = children
        self.frequency: int = freq
        self.assigned_code: str = assigned_code

    def __repr__(self) -> str:
        """
        Repräsentierungsmethode, die eine anschauliche Darstellung
        bereitstellt, sollte z.B. print auf das Objekt aufgerufen werden.
        """

        return f'<{self.assigned_code + "=" if self.assigned_code else ""}N \
{self.char + " " if self.char else ""}f={self.frequency} c={self.children}>'


def how_many_in_first_node(n: int, d: int) -> int:
    """
    Ermittelt die Anzahl an Leaf Nodes, die in der ersten Zusammenfassung bei
    der Konstruktion eines n-ären Huffman-Baumes vorhanden sein sollen.

    Ohne diese Berechnung riskieren wir einen suboptimalen Baumaufbau, sollte
    es uns nicht um die Kostenoptimierung gehen. Andererseits ist diese Methode
    nach meinen Beobachtungen zwar besser als eine rein zufällige Zuteilung der
    Knoten beim erstmaligen Zusammenfügen, aber eben auch nicht optimal.
    """

    # n = wie viele verschiedene Buchstaben im Text wir haben
    # d = wie viele Encoding-Buchstaben wir haben (N-arität)
    return 2 + (n - 2) % (d - 1)


def merge_nodes(
    nodes: list[HuffmanNode], n: int, alphabet: "dict[str, int]"
) -> None:
    """
    Fügt mehrere Knoten so optimal und effizient wie möglich in einen Knoten
    zusammen, indem es die Liste nodes in-place aktualisiert.
    """

    # Natürlich müssen wir gar nichts machen, wenn wir nur eine Node zu
    # verknüpfen haben, denn wirklich etwas zu "verknüpfen" hat man dann ja gar
    # nicht.
    if n == 1:
        return

    # Wir wählen uns die zusammenzufügenden Knoten aus
    nodes_to_merge: "list[HuffmanNode]" = nodes[:n]

    # Nun sortieren wir unser Encoding-Alphabet, damit die günstigsten Optionen
    # uns gleich als erste Elemente in der Liste vorliegen.
    alphabet_letters_to_assign: "OrderedDict[str, int]" = sorted_dict(alphabet)

    alphabet_letters: "list[str]" = list(alphabet_letters_to_assign.keys())

    if n > 2:
        best_permutation = nodes_to_merge
        best_cost = inf

        # Wir schauen uns nun von teuer nach günstig unsere Optionen an. Es
        # wird geguckt: Was, wenn wir die zwei eigentlichen teuersten Nodes in
        # eine günstigere zusammenfassen? Oder die drei teuersten? Oder gar
        # vier? Das Schöne: Wir machen das rekursiv - wir schauen also bis ganz
        # nach unten in den Baum, inwieweit wir die Knoten optimal zuweisen
        # können. Diese Methode ist praktisch das Herzstück des Algorithmus.
        for to_merge in range(1, min(len(alphabet), len(nodes_to_merge))):
            cost: int = 0

            # deepcopy, um die Referenzen loszuwerden
            permutation = list(reversed(deepcopy(nodes_to_merge)))

            # Wenn wir nur eine Node mergen wollen (was offensichtlich weder
            # Sinn ergibt, noch wirklich geht), skippen wir diesen Prozess
            # einfach komplett. Somit lassen wir die Möglichkeit, gar nichts zu
            # ändern, auch nicht außer Betracht. Es ist immerhin nicht
            # unmöglich, dass einfach alle zuzuweisenden Kosten recht attraktiv
            # sind!
            if to_merge > 1:
                merge_nodes(permutation, to_merge, alphabet)

            permutation = list(reversed(permutation))

            # Naiverer Ansatz zur Kostenbewertung - schneller, aber minimal
            # schlechter zur Baumoptimierung geeignet:
            #
            # for index, node in enumerate(
            #     sorted(permutation, key=lambda n: n.frequency, reverse=True)
            # ):
            #     cost += (
            #         node.frequency
            #         * list(alphabet_letters_to_assign.values())[index]
            #     )

            # Wir weisen zum Testen die Codes einmal zu:
            for index, el in enumerate(
                sorted(permutation, key=lambda el: el.frequency, reverse=True)
            ):
                el.assigned_code = alphabet_letters[index]

            # Wie teuer wäre das?
            cost = get_cost_of_combination(permutation, alphabet)

            # Ist das die beste Option bisher? Super! Dann merken wir uns
            # diese.
            if cost < best_cost:
                best_cost = cost
                best_permutation = permutation

        nodes_to_merge = best_permutation

    # Nach dem Ermitteln der besten Anordnung können wir nun die Buchstaben im
    # Encoding-Alphabet den Knoten zuweisen.
    for index, el in enumerate(
        sorted(nodes_to_merge, key=lambda el: el.frequency, reverse=True)
    ):
        el.assigned_code = alphabet_letters[index]

    # Wir erstellen die neue Node aus den Child-Nodes:
    new_node = HuffmanNode(
        "", nodes_to_merge, sum(node.frequency for node in nodes_to_merge)
    )

    # Zum Schluss werden wir die ursprünglichen Nodes, die wir ja nun
    # zusammenfassten, los - und fügen stattdessen unsere eigene ein.
    del nodes[:n]
    nodes.insert(0, new_node)


def sorted_dict(
    dict_: "dict[str, int]", reverse: bool = False
) -> "OrderedDict[str, int]":
    """
    Sortiert ein Dictionary, wie z.B. das des Encoding-Alphabets.
    """

    return OrderedDict(
        {
            i: dict_[i]
            for i in sorted(
                dict_.keys(), key=lambda x: dict_[x], reverse=reverse
            )
        }
    )


def get_cost_of_combination(
    nodes: "list[HuffmanNode]", alphabet: "dict[str, int]"
) -> int:
    """
    Ermittelt die Kosten einer Kombination innerhalb der Merge-Funktion.
    """

    cost = 0

    for node in nodes:
        cost += alphabet[node.assigned_code] * node.frequency

        if node.is_leaf():
            continue

        cost += get_cost_of_combination(node.children, alphabet)

    return cost


def construct_tree(
    occurences: "dict[str, int]",
    alphabet: "dict[str, int]",
    n_arity: int,
    override_nodes_in_first_merge: int = -1,
) -> HuffmanNode:
    """
    Konstruiert den Huffman-Baum aus drei Informationen: der Anzahl und
    Verteilung der Buchstaben im Text, dem gewichteten Encoding-Alphabet und
    der n-Arität, also der Anzahl an möglichen Buchstaben im Encoding-Alphabet
    und somit der maximalen Anzahl an Kanten, die zu Kindknoten führen, eines
    jeden Knotens.

    Der Override für die Menge an Knoten beim ersten Zusammenfügen kann auf
    -1 gesetzt werden, um diesen nicht zu nutzen.
    """

    nodes = [
        HuffmanNode(freq=v, children=[], char=k) for k, v in occurences.items()
    ]

    def sort_nodes_list(nodes: "list[HuffmanNode]") -> None:
        nodes.sort(key=lambda el: el.frequency)

    sort_nodes_list(nodes)

    if override_nodes_in_first_merge != -1:
        to_pack: int = override_nodes_in_first_merge
    else:
        # Initialer Run - wir führen die erste Zusammenfügung separat aus
        # (siehe Docstring in how_many_in_first_node für Erklärung)
        to_pack: int = how_many_in_first_node(len(occurences), len(alphabet))

    merge_nodes(nodes, to_pack, alphabet)

    # Danach geht es weiter mit dem Hauptvorgang: Wir verknüpfen unsere Nodes
    # so lange, bis nur noch ein Knoten übrig ist. Dieser ist dann die
    # "Wurzel".
    while len(nodes) > 1:
        sort_nodes_list(nodes)
        merge_nodes(nodes, n_arity, alphabet)

    return nodes[0]


def generate_encoding(root_node: HuffmanNode) -> "dict[str, str]":
    """
    Simple Methode, die schlichtweg jeden möglichen Pfad durch den Baum
    traversiert und aufzeichnet, welcher Weg für welchen Buchstaben zu gehen
    ist. Daraus wird unser präfixfreies Encoding generiert.
    """

    encoding: "dict[str, str]" = {}

    def traverse(node: HuffmanNode, cur_code: str):
        """
        Geht rekursiv durch den Baum und behält den gegangenen Weg im Auge.
        """

        if node.is_leaf():
            # Aha, wir sind am Ende angekommen.
            encoding[node.char] = cur_code
            return

        for child in node.children:
            # Wenn wir noch nicht am Ende eines Pfades angekommen sind, schauen
            # wir alle untergeordneten Knoten durch.
            traverse(child, cur_code + child.assigned_code)

    # Ursprungsaufruf zum Beginn
    traverse(root_node, "")

    return encoding


def remap_encoding(
    encoding: "dict[str, str]",
    occurences: "dict[str, int]",
    alphabet: "dict[str, int]",
) -> "dict[str, str]":
    """
    Führt einen letzten Pass über das generierte Encoding durch, indem den
    günstigsten Buchstaben Plätzen im Baum die häufigsten Buchstaben neu
    zugewiesen werden, sollte dies noch nicht passiert sein.

    Das neue dict wird zurückgegeben.
    """

    sorted_occurences = sorted_dict(occurences)
    costs: "list[tuple[str, int]]" = sorted(
        [
            (v, encode_text(k, encoding, alphabet)[1])
            for k, v in encoding.items()
        ],
        key=lambda el: el[1],
    )

    new_dict: "dict[str, str]" = {}

    for k in sorted_occurences:
        new_dict[k] = costs.pop()[0]

    return new_dict


def output_cost_analyzation(
    text: str,
    encoding: "dict[str, str]",
    alphabet: "dict[str, int]",
    occurences: "dict[str, int]",
    verbose: bool = False,
) -> None:
    """
    Gibt eine Kostenanalyse für das generierte Encoding-Alphabet, angewendet
    auf den Text, aus.
    """

    encoded, cost = encode_text(text, encoding, alphabet)

    if verbose:
        print("Der codierte Text lautet:", encoded)

    print(
        f"Textlänge: {len(text)} · Encodete Länge: {len(encoded)} Perlen · \
Gesamtkosten (∑): {cost}mm"
    )

    if not verbose:
        # Wenn wir keine Extra-Informationen ausgeben sollen, hören wir ab hier
        # auf.
        return

    # Schlussendlich geben wir auch noch einmal Auskunft über die Kosten für
    # jeden einzelnen Buchstaben.
    print("Kosten für die individuellen Buchstaben:")
    for k, v in encoding.items():
        cost = sum(alphabet[c] for c in v)
        print(f"{k}: {cost} (f = {occurences[k]})")


def encode_text(
    text: str, encoding: "dict[str, str]", alphabet: "dict[str, int]"
) -> "tuple[str, int]":
    """
    Kodiert einen Text mithilfe eines gegebenen Encodings. Gibt den codierten
    Text und die Kosten zurück.
    """

    encoded = ""
    cost = 0

    for char in text:
        # Wir gehen unseren gesamten Text durch und codieren ihn. Nebenbei
        # behalten wir im Blick, wie "teuer" das ganze wird.
        encoded_to_use = encoding[char]
        encoded += encoded_to_use
        cost += sum(alphabet[c] for c in encoded_to_use)

    return encoded, cost


def is_prefix_free(table: "dict[str, str]") -> bool:
    """
    Überprüft, ob die Codetabelle präfixfrei ist.
    """

    codes = list(table.values())

    for idx_1, (k, v) in enumerate(table.items()):
        if any(
            bool(el.startswith(v) and idx_1 != idx_2)
            for idx_2, el in enumerate(codes)
        ):
            print(f"Code für {k} nicht präfixfrei!")
            return False

    print("Überprüfung nach Präfixdopplungen beendet - Code ist präfixfrei!")
    return True


def parse_input_file(filename: str) -> "tuple[str, dict[str, int]]":
    """
    Liest die Eingabedatei ein und parst diese.
    """

    text: str = ""
    alphabet: "dict[str, int]" = {}

    with open(filename, "r", encoding="utf-8") as f:
        # Wir können mit der ersten Zeile nichts anfangen, da wir die Menge an
        # Perlen ja so oder so durch die zweite inferieren können. Also
        # überspringen wir diese kurzerhand.
        f.readline()

        try:
            # Nun lesen wir alle Perlengrößen ein und wandeln diese in Integer
            # um:
            alphabet = {
                PEARL_NAMES[index]: value
                for index, value in enumerate(
                    [int(p) for p in f.readline().strip().split()]
                )
            }

            # Der Text kommt als nächstes.
            text = f.readline().strip()
        except ValueError:
            # pylint: disable=raise-missing-from
            # Sollte die Umwandlung fehlschlagen, müssen wir einen ParseError
            # auslösen. Dieser wird von der main-Funktion weiter behandelt.
            raise ParseError("Ungültige, fehlgeformte Eingabedatei.")

    return (text, alphabet)


def render_tree_visualization(node: HuffmanNode, level: int = 0) -> None:
    """
    Gibt eine anschauliche Visualisierung des Baumes im Terminal aus.
    """

    if level == 0:
        print(
            "Folgender Huffman-Baum wurde konstruiert.",
            f"(Stammknoten n={node.frequency})",
            sep="\n",
        )

    for idx, child in enumerate(node.children):
        print(
            "  " * level,
            f"{'├' if idx < len(node.children) - 1 else '└'}\
─{child.assigned_code}─",
            (f'"{child.char}"' if child.is_leaf() else f"({child.frequency})"),
        )
        render_tree_visualization(child, level + 1)


def render_code_table(
    encoding: "dict[str, str]", compact: bool = False
) -> None:
    """
    Gibt die fertige, optimierte Codetabelle aus.
    """

    if compact:
        for k, v in encoding.items():
            print(f'│ "{k}" = {v}', end=" ")

        print("│")  # weitere Endzeile

        return

    print(
        """Den Perlen aus der Eingabedatei wurden jeweils Buchstaben \
zugewiesen, um sie zu unterscheiden. Die erste Perlenlänge in Zeile 2 der \
Eingabedatei bekommt Buchstaben a, die zweite Buchstaben b, etc.

Die optimierte Tabelle lautet:"""
    )

    max_w = max(map(len, encoding.values()))
    print("┌───┬", "─" * (max_w + 2), "┐", sep="")

    for k, v in encoding.items():
        print(f"│ {k} │ {v + ' ' * (max_w-len(v))} │")

    print("└───┴", "─" * (max_w + 2), "┘", sep="")


def main() -> int:
    """
    Die Hauptmethode für das Programm, welche sich um das Einlesen der Datei
    und den initialen Programmfluss kümmert.
    """

    # pylint: disable=too-many-locals
    # Begründung: Wir verfehlen das Ziel nur knapp und ein Refactoring in
    # weitere Teilfunktionen würde die eigentlich simple Main-Funktion noch
    # schwieriger zu durchschauen machen

    arguments: Namespace = p.parse_args()
    filename: str = arguments.file

    if not os.path.isfile(filename):
        print(f"{filename}: Datei oder Verzeichnis nicht gefunden")
        return -ENOENT

    try:
        text, alphabet = parse_input_file(filename)
    except ParseError as e:
        traceback.print_exception(e)
        return -EINVAL

    n_arity = len(alphabet)

    if n_arity < 2:
        raise TreeConstructionError(
            f"Baum kann nicht präfixfrei konstruiert werden (d < 2). Das \
Encoding-Alphabet braucht mindestens zwei Buchstaben, hat aber nur {n_arity}."
        )

    occurences = {k: text.count(k) for k in set(text)}

    best_encoding: "dict[str, str]" = {}
    best_tree: HuffmanNode = HuffmanNode("", [], 0)
    best_cost = inf

    start_time: float = time.time()

    for nodes_in_first_merge in range(2, n_arity + 1):
        # Zuerst erstellen wir den Baum...
        root_node = construct_tree(
            occurences, alphabet, n_arity, nodes_in_first_merge
        )

        # ... dann erstellen wir das Encoding ...
        enc = remap_encoding(
            generate_encoding(root_node), occurences, alphabet
        )

        # ... und bewerten die Kosten.
        _, cost = encode_text(text, enc, alphabet)
        if cost < best_cost:
            best_cost = cost
            best_encoding = enc
            best_tree = root_node

    # Optional geben wir noch den Tree visualisiert aus.
    if arguments.tree:
        render_tree_visualization(best_tree)

    end_time: float = time.time()

    # Nun geben wir die Tabelle aus
    render_code_table(best_encoding, arguments.compact)

    # Zudem analysieren wir ein letztes Mal die Kosten
    output_cost_analyzation(
        text, best_encoding, alphabet, occurences, arguments.verbose
    )

    # Und wir überprüfen, ob der Code prefixfrei ist
    is_prefix_free(best_encoding)

    # Letzte Amtshandlung: Geschwindigkeitsanalyse, wenn denn gewollt.
    if arguments.time:
        delta_time: float = end_time - start_time
        print(
            f"Benötigte Zeit: {delta_time:.3f}s",
            f"(Geschwindigkeit: {(len(text)/delta_time)/1024:.1f}KiB/s)",
        )

    # Alles hat funktioniert; Exit-Code 0.
    return 0


if __name__ == "__main__":
    ret_code: int = main()
    sys.exit(ret_code)
