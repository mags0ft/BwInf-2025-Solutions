#!/usr/bin/python3

"""
Lösungen für die Aufgabe 1 ("Hopsitexte") des 43. Bundeswettbewerbs Informatik.
"""

import string


ALLOWED_CHARS = string.ascii_lowercase + "äöüß"


def char_value(char: str) -> int:
    if len(char) != 1:
        print(
            "Warnung: Die Funktion char_value hat nicht einen einzigen Char bekommen."
        )
        return -1

    lower_char: str = char.lower()

    if lower_char not in ALLOWED_CHARS:
        print(
            "Warnung: Die Eingabe in char_value war kein gültiger Buchstabe."
        )
        return -1

    if lower_char in "äöüß":
        # Sonderzeichen werden gesondert behandelt
        return {"ä": 27, "ö": 28, "ü": 29, "ß": 30}[lower_char]

    return ord(lower_char) - 96


class PlayersOnSameCharException(Exception):
    pass


def part_of_text(text: str, pos: int, padding: int = 20) -> str:
    """
    Extrahiert einen kleinen Teil des Textes, um ihn bei Fehlern anzeigbar zu
    machen.
    """

    left_bound: int = pos - padding
    right_bound: int = pos + padding

    if pos - padding < 0:
        left_bound = 0
    if pos + padding > (len(text) - 1):
        right_bound = len(text)

    return (
        " ... "
        + text[left_bound:right_bound]
        + " ... "
        + "\n"
        + " " * 5
        + (" " * (padding if left_bound != 0 else pos) + "^")
        + " " * 5
    )


def gametick(text: str, pos_a: int, pos_b: int) -> "tuple[int, int]":
    """
    Spielt eine Runde beider Spieler im Hopsitext und gibt deren neue Positionen zurück.
    """

    def get_new_player_pos(pos: int):
        while (pos < len(text)) and (text[pos].lower() not in ALLOWED_CHARS):
            pos += 1  # wir überspringen alles, was kein Buchstabe ist!

        # nun geben wir die derzeitige Position plus die Wertigkeit des derzeitigen
        # Buchstabens zurück.
        return pos + (char_value(text[pos]) if pos < len(text) else 1)

    new_pos_a = get_new_player_pos(pos_a)
    new_pos_b = get_new_player_pos(pos_b)

    if new_pos_a == new_pos_b:
        raise PlayersOnSameCharException(
            "Die Spieler sind auf dem selben Buchstaben im Text. Sie werden \
an der selben Stelle herausspringen. Beachte, falls dir kein Fehler auffallen \
sollte, dass unsere Spieler*innen alles, was kein Buchstabe ist, überspringen! \
Der Fehler liegt übrigens hier - ab diesem Buchstaben haben sich die \
Positionen überlappt: \n\n"
            + part_of_text(text, new_pos_a)
        )

    return (new_pos_a, new_pos_b)


def remove_non_chars(str_: str) -> str:
    """
    Entfernt alles, was kein Buchstabe ist.
    """

    return "".join(filter(lambda s: s.lower() in ALLOWED_CHARS, list(str_)))


def find_winner(text: str):
    """
    Ermittelt die/den Gewinner*in des Hopsitextes.
    """

    pos_a, pos_b = 0, 1
    text_end_index = len(text) - 1

    while (pos_a <= text_end_index) or (pos_b <= text_end_index):
        pos_a, pos_b = gametick(text, pos_a, pos_b)

    return "Spieler*in A" if (pos_a > pos_b) else "Spieler*in B"


def mainloop(current_text: "list[str]") -> str:
    """
    Code, der wiederholend ausgeführt wird, um bei der Erstellung des nächsten
    Satzes zu assistieren.
    """

    print(" --- Satz #", len(current_text) + 1, " --- ", sep="")
    text_as_string: str = remove_non_chars("".join(current_text))

    print(
        "\nFormuliere einen Satz nach deinen Wünschen. Das Programm wird ihn sich \
ansehen und überprüfen, ob es passieren kann, dass die Spieler*innen an der selben \
Stelle landen und somit auch an derselben heraushüpfen. Dann gibt dir das Programm \
Tipps, wo dieser Fehler aufgetreten ist. Dann kannst Du dir erschließen, welches \
Wort zu verändern ist."
    )

    def playthrough(text: str):
        """
        Spielt den bisherigen Text so weit durch, bis mindestens ein*e Spieler*in
        den neuen Satz, an dem wir gerade sitzen, erreicht. Denn erst dann müssen
        wir das nächstbeste Wort herausfinden.

        Gibt den Index zurück, an dem ein oder mehrere Spieler*innen angekommen
        sind, wenn sie unseren neuen Satz erreichen.
        """

        pos_a, pos_b = 0, 1
        text_end_index = len(text) - 1

        while (pos_a <= text_end_index) or (pos_b <= text_end_index):
            pos_a, pos_b = gametick(text, pos_a, pos_b)

        return (pos_a, pos_b)

    while True:
        next_sentence: str = input()

        try:
            playthrough(remove_non_chars(text_as_string + next_sentence))

            break  # Scheint alles gut zu sein!
        except PlayersOnSameCharException as e:
            print(e)
            print(
                "\nBitte versuche, einen Satz zu formulieren, bei dem \
die Spielerpositionen ab dieser Stelle nicht überlappen. \n"
            )

    return next_sentence.strip()


def main() -> None:
    """
    Die Hauptmethode des Programms.
    """

    text_result: "list[str]" = []

    print(
        """*** Willkommen beim Hopsitext-Assistenten! ***

    Dieser Assistent hilft dir bei der Erstellung eines möglichst langen Hopsitextes.
    Du kannst frei Sätze formulieren. Wenn es Kollisionen gibt, 

    Es gilt wie immer in einer Terminalanwendung: CTRL+C oder CTRL+D beenden das Programm.
    Drücke diese Tasten, wenn Du zufrieden bist, und dir wird dein Text ausgegeben.
    
        >> Bereit? Los geht's! Drücke ENTER, um zu beginnen. <<
"""
    )

    input()  # Enter abwarten

    while True:
        try:
            text_part: str = mainloop(text_result)

            if not text_part:
                continue

            text_result.append(text_part)
        except (KeyboardInterrupt, EOFError):
            print(
                "\n\nAlles klar, Du hast das Programm verlassen. Hier dein Text:\n"
            )
            print("\n".join(text_result), "\n")

            print(
                find_winner(remove_non_chars("".join(text_result))),
                "wird gewinnen.\n",
            )
            break


if __name__ == "__main__":
    main()
