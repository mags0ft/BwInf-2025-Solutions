# Aufgabe 3: Wandertag

## Programmnutzung

So verwendet man das Programm im Terminal:

```bash
$ python3 ./wandertag.py NAME_DER_EINGABEDATEI
```

Beispiel:

```bash
$ python3 ./wandertag.py ./wandern0.txt
```

## Grundgedanken und Programmablauf

Damit wir Aufgabe 3 lösen und so viele potenzielle Teilnehmer\*innen wie möglich glücklich machen, haben wir uns für ein System entschieden, welches die möglichen Streckenlängen durchgeht und misst, wie viele Interessent\*innen sich für diese Länge finden lassen. Der Programmablauf ist wie folgt:

1. zuerst die Datei einlesen und parsen:
    1. nach Zeilenumbrüchen teilen, dann für jede Zeile:
        1. wenn die Zeile die erste ist oder leer ist: überspringen
        2. ansonsten: die Werte der Zeile an den Leerzeichen spalten und mitsamt deren Index zwischenspeichern
        3. bei Fehlern: diese an stderr ausgeben und Programm beenden
    2. Zwischengespeicherte Daten zurückgeben

2. Ausgabewerte für die Ergebnisse initialisieren und vorbereiten

3. 3 mal hintereinander für 3 verschiedene Strecken:
    1. für jede mögliche Streckenlänge von (kleinste gefundene gewünschte Streckenlänge) bis (höchste gefundene Streckenlänge):
        1. Zahl an Personen ermitteln, die an dieser Strecke teilnehmen würden:
            1. für jeden Wunsch in der oben ermittelten Liste aus der Datei: ist die Länge innerhalb des Wunschbereiches? Wenn ja: vermerken
            2. Anzahl an Matches zurückgeben
        2. ist die gefundene Zahl an Teilnehmer\*innen höher als bisher? Dann: neuen Maximalwert setzen.
    2. nach Durchlauf die Matches aus dem besten gefundenen Exemplar aus der Liste löschen und Prozess wiederholen

4. Aufbereitung am Ende und Ausgabe:
    1. für jede der drei gefundenen optimalen Strecken:
        1. alle Personen, die an der Strecke teilgenommen hätten, noch einmal ermitteln. Warum das nötig ist? Da wir zuvor die Personen schon aus der Liste gelöscht haben, um verschiedene Streckenlängen zu bekommen
    2. Ergebnisse an stdout ausgeben

## Wichtigste Teile des Quelltextes

Dieser Teil ermittelt die Anzahl an Teilnehmer\*innen bei einer gegebenen Streckenlänge:

```python
def find_people_matching(
    list_: "list[tuple[int, int, int]]", track_length: int
) -> "tuple[list[int], list[int]]":
    """
    Findet alle passenden Teilnehmer*innen, gibt einen Tupel aus einer Liste mit den matchenden Indizes der lokalen Liste
    und den matchenden Indizes der absoluten Liste (aus Eingabedatei) zurück.
    """
    matching_local = []
    matching_global = []

    for index, element in enumerate(list_):
        if element[0] <= track_length <= element[1]:
            matching_global.append(element[2])
            matching_local.append(index)

    return (matching_global, matching_local)
```

Und dieser hier nutzt das, um die drei besten Streckenlängen zu finden:

```python
values: "list[tuple[int, int, int]]" = read_file(sys.argv[1])
values_copy: "list[tuple[int, int, int]]" = deepcopy(values)
total_num_entries: int = len(values)

results: "dict[int, tuple[int, list[int]]]" = {}
# Ergebnis-Dictionary; enthält die bestmöglich Streckenlänge als Key und als Value einen Tupel aus Teilnehmer*innenanzahl und den Indizes derer.

for j in range(NUM_OF_TRACKS_WANTED):
    max_num_matches: int = -1
    best_length_found: int = -1
    participants: "list[int]" = []
    participant_local_indices: "list[int]" = []

    min_dist: int = min(values, key=lambda x: x[0])[0]
    max_dist: int = max(values, key=lambda x: x[1])[1]

    for index in range(min_dist, max_dist):
        potential_participants, matching_local_indices = find_people_matching(
            values, index
        )
        num_participants = len(potential_participants)

        if num_participants > max_num_matches:
            max_num_matches = num_participants
            participants = potential_participants
            participant_local_indices = matching_local_indices
            best_length_found = index

    results[best_length_found] = (len(participants), participants)

    if j == NUM_OF_TRACKS_WANTED - 1:
        # wir müssen nicht wieder die gematchten Personen aus der Liste entfernen, da wir fertig sind
        # und jetzt lieber das Ergebnis direkt ausgeben sollten, anstatt noch mehr kostbare Zeit
        # zu verschwenden.
        break

    for index in sorted(participant_local_indices, reverse=True):
        # Für all diese Leute wissen wir nun: Auf geht's! Sehen wir uns also im nächsten Durchlauf
        # nur die restlichen an.
        del values[index]
```

Die Schlussendliche Bearbeitung unserer Ergebnisse übernimmt dann noch dieser Schnipsel:

```python
# Nachbearbeitung: Noch die Personen eintragen, die bei unseren Top 3 auch mitkommen würden (sie können zeitgleich laufen)
for key, value in results.items():
    all_people_attending: "tuple[list[int], list[int]]" = find_people_matching(
        values_copy, key
    )[0]
    results[key] = (len(all_people_attending), all_people_attending)

total_participants: "set[int]" = set()
```

**Anmerkung**: Wir haben es uns hier erlaubt, `sorted()` zu verwenden. Für eine eigene Implementierung unseres Teams in Sache Sortieralgorithmen, siehe Aufgabe 2, "Schwierigkeiten". Wir wollten das Rad nicht zwei Mal neu erfinden ;\)


## Ausgaben des Programms

Folgend sind wieder einmal all die Ausgaben unseres Programms bei den Beispielen der BWINF-Website:

```
user@testpc:~/bwinf$ python3 ./wandertag.py ./wandern1.txt 

Beste gefundene Streckenlängen:
        1.)
         - Streckenlänge: 22 m
         - Anzahl der Teilnehmer*innen: 2
         - konkrete Indizes der Teilnehmer*innen: 1, 2
        2.)
         - Streckenlänge: 51 m
         - Anzahl der Teilnehmer*innen: 2
         - konkrete Indizes der Teilnehmer*innen: 4, 5
        3.)
         - Streckenlänge: 64 m
         - Anzahl der Teilnehmer*innen: 2
         - konkrete Indizes der Teilnehmer*innen: 6, 7

Wir konnten 6 von 7 Teilnehmer*innen (85.71%) mitnehmen!

user@testpc:~/bwinf$ python3 ./wandertag.py ./wandern2.txt 

Beste gefundene Streckenlängen:
        1.)
         - Streckenlänge: 40 m
         - Anzahl der Teilnehmer*innen: 3
         - konkrete Indizes der Teilnehmer*innen: 3, 4, 6
        2.)
         - Streckenlänge: 10 m
         - Anzahl der Teilnehmer*innen: 2
         - konkrete Indizes der Teilnehmer*innen: 5, 6
        3.)
         - Streckenlänge: 60 m
         - Anzahl der Teilnehmer*innen: 3
         - konkrete Indizes der Teilnehmer*innen: 1, 3, 4

Wir konnten 5 von 6 Teilnehmer*innen (83.33%) mitnehmen!

user@testpc:~/bwinf$ python3 ./wandertag.py ./wandern3.txt 

Beste gefundene Streckenlängen:
        1.)
         - Streckenlänge: 27 m
         - Anzahl der Teilnehmer*innen: 4
         - konkrete Indizes der Teilnehmer*innen: 2, 3, 7, 9
        2.)
         - Streckenlänge: 90 m
         - Anzahl der Teilnehmer*innen: 3
         - konkrete Indizes der Teilnehmer*innen: 1, 5, 8
        3.)
         - Streckenlänge: 19 m
         - Anzahl der Teilnehmer*innen: 3
         - konkrete Indizes der Teilnehmer*innen: 7, 9, 10

Wir konnten 8 von 10 Teilnehmer*innen (80.00%) mitnehmen!

user@testpc:~/bwinf$ python3 ./wandertag.py ./wandern4.txt 

Beste gefundene Streckenlängen:
        1.)
         - Streckenlänge: 684 m
         - Anzahl der Teilnehmer*innen: 40
         - konkrete Indizes der Teilnehmer*innen: 4, 7, 8, 9, 10, 12, 13, 14, 15, 17, 19, 20, 21, 24, 26, 27, 32, 35, 40, 43, 44, 45, 52, 55, 57, 58, 61, 65, 66, 72, 74, 75, 76, 79, 82, 83, 84, 97, 98, 99
        2.)
         - Streckenlänge: 811 m
         - Anzahl der Teilnehmer*innen: 37
         - konkrete Indizes der Teilnehmer*innen: 1, 2, 4, 5, 6, 9, 14, 15, 17, 19, 20, 21, 22, 26, 27, 28, 30, 32, 33, 35, 44, 49, 52, 54, 56, 60, 63, 65, 72, 74, 75, 76, 83, 88, 89, 97, 98
        3.)
         - Streckenlänge: 266 m
         - Anzahl der Teilnehmer*innen: 22
         - konkrete Indizes der Teilnehmer*innen: 3, 4, 12, 21, 29, 39, 41, 42, 43, 46, 53, 61, 66, 68, 69, 79, 84, 85, 86, 91, 99, 100

Wir konnten 68 von 100 Teilnehmer*innen (68.00%) mitnehmen!

user@testpc:~/bwinf$ python3 ./wandertag.py ./wandern5.txt 

Beste gefundene Streckenlängen:
        1.)
         - Streckenlänge: 45823 m
         - Anzahl der Teilnehmer*innen: 92
         - konkrete Indizes der Teilnehmer*innen: 2, 5, 6, 11, 12, 15, 18, 21, 22, 27, 30, 33, 34, 36, 38, 39, 40, 41, 43, 46, 48, 55, 64, 65, 67, 73, 74, 79, 85, 87, 88, 92, 94, 95, 96, 97, 98, 99, 103, 104, 105, 106, 107, 108, 109, 111, 112, 114, 115, 118, 119, 122, 124, 125, 128, 129, 130, 131, 132, 134, 135, 136, 138, 145, 146, 148, 152, 155, 158, 159, 162, 164, 167, 169, 171, 172, 176, 178, 179, 181, 182, 183, 187, 190, 192, 193, 195, 196, 197, 198, 199, 200
        2.)
         - Streckenlänge: 83060 m
         - Anzahl der Teilnehmer*innen: 61
         - konkrete Indizes der Teilnehmer*innen: 4, 6, 7, 11, 12, 14, 16, 17, 21, 23, 25, 26, 27, 30, 31, 34, 35, 40, 41, 43, 46, 49, 57, 58, 59, 71, 77, 78, 83, 84, 85, 91, 93, 95, 101, 106, 115, 117, 118, 129, 131, 132, 139, 142, 145, 148, 149, 151, 152, 154, 158, 166, 167, 170, 171, 174, 176, 178, 185, 187, 192
        3.)
         - Streckenlänge: 92489 m
         - Anzahl der Teilnehmer*innen: 43
         - konkrete Indizes der Teilnehmer*innen: 4, 6, 7, 9, 10, 11, 14, 16, 17, 21, 23, 27, 29, 30, 31, 35, 40, 51, 54, 57, 60, 62, 69, 77, 78, 81, 91, 95, 121, 131, 132, 140, 141, 143, 145, 148, 154, 158, 173, 176, 185, 188, 192

Wir konnten 139 von 200 Teilnehmer*innen (69.50%) mitnehmen!

user@testpc:~/bwinf$ python3 ./wandertag.py ./wandern6.txt 

Beste gefundene Streckenlängen:
        1.)
         - Streckenlänge: 55908 m
         - Anzahl der Teilnehmer*innen: 173
         - konkrete Indizes der Teilnehmer*innen: 26, 33, 34, 41, 42, 44, 46, 47, 51, 52, 53, 54, 55, 57, 59, 60, 65, 70, 71, 72, 75, 76, 81, 82, 87, 88, 95, 100, 101, 103, 106, 107, 111, 113, 114, 115, 117, 118, 121, 126, 129, 130, 133, 136, 137, 138, 143, 146, 149, 151, 153, 157, 158, 166, 170, 175, 176, 179, 180, 182, 185, 186, 189, 195, 196, 197, 198, 206, 207, 211, 212, 215, 216, 222, 224, 229, 236, 237, 238, 240, 244, 245, 249, 250, 252, 255, 256, 258, 262, 263, 269, 272, 278, 280, 284, 285, 289, 291, 294, 296, 298, 300, 301, 302, 303, 307, 308, 312, 313, 315, 319, 329, 342, 343, 344, 345, 347, 350, 352, 353, 354, 358, 359, 361, 367, 368, 369, 374, 375, 380, 381, 383, 385, 386, 387, 390, 391, 398, 399, 400, 405, 406, 412, 413, 415, 416, 417, 418, 419, 420, 425, 430, 433, 437, 439, 448, 450, 452, 457, 459, 464, 470, 471, 473, 474, 478, 479, 481, 482, 488, 491, 495, 497
        2.)
         - Streckenlänge: 83384 m
         - Anzahl der Teilnehmer*innen: 146
         - konkrete Indizes der Teilnehmer*innen: 3, 5, 8, 12, 13, 22, 24, 28, 33, 38, 43, 47, 48, 50, 52, 60, 63, 68, 71, 77, 80, 82, 92, 93, 94, 99, 102, 107, 109, 115, 116, 121, 123, 124, 132, 133, 136, 139, 141, 142, 143, 144, 146, 147, 149, 152, 155, 158, 165, 166, 172, 175, 176, 177, 179, 180, 184, 185, 187, 189, 195, 196, 198, 199, 201, 207, 210, 215, 216, 222, 227, 230, 247, 248, 269, 271, 278, 286, 288, 290, 292, 296, 298, 300, 304, 307, 312, 323, 327, 330, 331, 335, 336, 339, 341, 342, 343, 347, 350, 353, 357, 362, 365, 367, 368, 370, 372, 373, 377, 380, 382, 384, 386, 389, 390, 392, 393, 395, 398, 401, 405, 410, 411, 420, 421, 431, 435, 436, 439, 442, 444, 449, 452, 454, 456, 459, 468, 469, 470, 471, 477, 479, 481, 495, 499, 500
        3.)
         - Streckenlänge: 30937 m
         - Anzahl der Teilnehmer*innen: 124
         - konkrete Indizes der Teilnehmer*innen: 1, 6, 19, 26, 33, 34, 37, 44, 45, 47, 52, 53, 54, 55, 59, 61, 65, 67, 72, 75, 76, 82, 86, 87, 88, 89, 90, 95, 100, 101, 103, 113, 114, 126, 129, 131, 146, 150, 151, 153, 156, 159, 164, 166, 167, 168, 173, 175, 176, 182, 185, 186, 188, 190, 194, 195, 197, 198, 200, 203, 212, 216, 221, 222, 234, 236, 237, 245, 249, 250, 252, 255, 256, 258, 261, 267, 277, 279, 280, 281, 289, 300, 301, 312, 313, 316, 319, 320, 326, 329, 333, 338, 345, 359, 361, 363, 368, 369, 378, 380, 383, 385, 386, 391, 400, 413, 415, 416, 418, 422, 430, 433, 447, 452, 457, 458, 461, 470, 474, 479, 482, 488, 493, 497

Wir konnten 304 von 500 Teilnehmer*innen (60.80%) mitnehmen!

user@testpc:~/bwinf$ python3 ./wandertag.py ./wandern7.txt 

Beste gefundene Streckenlängen:
        1.)
         - Streckenlänge: 52515 m
         - Anzahl der Teilnehmer*innen: 304
         - konkrete Indizes der Teilnehmer*innen: 4, 6, 8, 9, 11, 12, 16, 17, 21, 22, 26, 27, 28, 29, 31, 33, 35, 38, 41, 42, 43, 45, 47, 51, 59, 61, 62, 64, 66, 70, 71, 74, 79, 83, 86, 88, 89, 91, 92, 95, 96, 99, 105, 107, 111, 114, 115, 116, 120, 122, 126, 127, 128, 133, 134, 135, 137, 141, 142, 148, 149, 153, 157, 158, 159, 160, 161, 163, 164, 170, 171, 174, 175, 176, 180, 181, 183, 185, 187, 191, 192, 196, 210, 211, 216, 219, 220, 225, 229, 230, 236, 238, 239, 245, 246, 252, 253, 255, 256, 262, 266, 273, 275, 277, 285, 287, 288, 292, 293, 295, 299, 302, 304, 305, 308, 310, 312, 314, 318, 320, 321, 322, 324, 326, 329, 332, 335, 343, 347, 350, 351, 357, 358, 359, 361, 364, 366, 371, 372, 373, 374, 375, 376, 380, 381, 382, 383, 385, 387, 390, 391, 394, 395, 397, 399, 404, 408, 410, 415, 422, 426, 434, 437, 441, 442, 447, 449, 450, 454, 456, 465, 467, 469, 470, 471, 472, 473, 476, 479, 480, 484, 486, 489, 491, 494, 495, 497, 499, 501, 502, 506, 512, 513, 521, 524, 525, 528, 530, 531, 532, 533, 534, 536, 538, 540, 542, 544, 546, 548, 551, 552, 553, 559, 560, 567, 568, 570, 574, 577, 578, 580, 582, 583, 584, 585, 589, 592, 593, 595, 597, 601, 602, 604, 605, 609, 610, 612, 617, 618, 619, 620, 622, 623, 624, 628, 631, 632, 634, 638, 639, 641, 646, 650, 652, 656, 658, 659, 660, 664, 666, 670, 672, 673, 676, 679, 688, 689, 696, 701, 705, 708, 709, 710, 711, 713, 724, 726, 728, 729, 733, 736, 737, 740, 742, 743, 746, 748, 751, 756, 757, 758, 760, 763, 765, 767, 768, 774, 776, 781, 783, 787, 791, 795, 798
        2.)
         - Streckenlänge: 86493 m
         - Anzahl der Teilnehmer*innen: 225
         - konkrete Indizes der Teilnehmer*innen: 9, 12, 13, 15, 21, 28, 33, 35, 37, 38, 47, 55, 57, 58, 62, 63, 65, 67, 69, 75, 80, 81, 82, 87, 92, 93, 95, 101, 102, 106, 110, 111, 112, 114, 116, 117, 119, 122, 123, 126, 131, 137, 142, 146, 151, 153, 154, 158, 165, 170, 172, 185, 186, 188, 189, 193, 195, 196, 197, 198, 203, 205, 209, 214, 218, 225, 229, 230, 232, 234, 238, 244, 249, 250, 252, 256, 258, 259, 260, 265, 271, 276, 277, 278, 282, 283, 291, 296, 300, 312, 313, 319, 328, 335, 343, 344, 347, 349, 359, 361, 367, 369, 370, 371, 376, 378, 380, 386, 392, 395, 396, 398, 406, 407, 412, 417, 418, 419, 425, 426, 428, 430, 438, 440, 455, 457, 462, 470, 476, 479, 480, 481, 488, 489, 490, 497, 499, 506, 508, 509, 514, 515, 526, 527, 539, 540, 541, 542, 545, 547, 549, 550, 551, 552, 562, 563, 566, 567, 569, 570, 575, 582, 583, 585, 592, 593, 596, 605, 606, 607, 608, 611, 622, 629, 630, 635, 637, 639, 640, 641, 645, 647, 648, 652, 654, 658, 661, 665, 668, 678, 683, 687, 696, 699, 702, 705, 707, 712, 713, 714, 716, 717, 719, 722, 730, 736, 741, 742, 749, 755, 758, 759, 763, 765, 766, 767, 771, 777, 780, 783, 784, 785, 791, 793, 795
        3.)
         - Streckenlänge: 30966 m
         - Anzahl der Teilnehmer*innen: 231
         - konkrete Indizes der Teilnehmer*innen: 3, 4, 5, 6, 9, 12, 14, 16, 17, 22, 27, 30, 38, 42, 43, 46, 59, 62, 66, 71, 77, 79, 85, 86, 88, 89, 91, 95, 96, 105, 107, 111, 113, 115, 116, 118, 124, 127, 133, 142, 143, 148, 149, 153, 155, 158, 160, 161, 162, 166, 170, 171, 174, 175, 176, 178, 180, 183, 185, 190, 191, 206, 208, 211, 213, 215, 216, 219, 230, 237, 239, 242, 245, 246, 247, 253, 255, 262, 266, 270, 277, 280, 284, 285, 287, 293, 295, 299, 302, 303, 304, 305, 309, 310, 312, 314, 320, 321, 323, 326, 332, 333, 354, 361, 364, 373, 375, 376, 380, 381, 383, 385, 387, 399, 400, 401, 404, 410, 415, 422, 426, 434, 437, 439, 442, 445, 447, 449, 450, 454, 463, 464, 470, 472, 477, 479, 486, 487, 489, 494, 497, 499, 503, 505, 506, 510, 512, 517, 518, 520, 521, 528, 529, 530, 532, 533, 540, 542, 546, 548, 551, 560, 570, 574, 577, 578, 583, 584, 589, 595, 597, 602, 604, 612, 614, 616, 618, 620, 623, 624, 628, 634, 638, 639, 641, 644, 649, 650, 652, 664, 666, 667, 669, 671, 673, 679, 680, 682, 686, 689, 701, 706, 709, 713, 718, 724, 728, 729, 731, 733, 734, 740, 742, 743, 748, 752, 757, 758, 761, 763, 767, 768, 776, 781, 783, 787, 790, 791, 795, 796, 800

Wir konnten 516 von 800 Teilnehmer*innen (64.50%) mitnehmen!
```
