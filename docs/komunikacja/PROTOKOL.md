# PROTOKÓŁ WSPÓŁPRACY MIĘDZY PROJEKTAMI

Pracujemy nad jednym zadaniem razem z trzema projektami Claude:
- APP  – aplikacja ServMod (Android, Kotlin)
- BOX  – ServMod Box: firmware ESP32-S3 + sprzęt (moduły, piny, obudowa)
- WWW  – strona internetowa

Nie masz dostępu do rozmów pozostałych projektów. Komunikujemy się wyłącznie przez pliki we wspólnym folderze
`_komunikacja` (na komputerze użytkownika: `C:\Users\grabo\Desktop\Arduino\ServMod\_komunikacja`).
Folder czytasz i zapisujesz przez połączenie z komputerem użytkownika. Jeśli tego połączenia nie ma, napisz to użytkownikowi
i nie zgaduj stanu plików.

TWOJA ROLA: [APP / BOX / WWW]   (wpisz jedną w instrukcjach projektu)

## Struktura
- PROTOKOL.md       – ten plik (zasady współpracy)
- CEL.md            – wspólny cel i definicja "gotowe" (czytaj, nie zmieniaj bez zgody użytkownika)
- KONTRAKT.md       – jedyne źródło prawdy o interfejsach: ramki Box <-> aplikacja, typy, kody, pola INFO, kanały, timeouty
- DECYZJE.md        – dziennik ustaleń (tylko dopisujesz na końcu)
- inbox/APP.md, inbox/BOX.md, inbox/WWW.md – skrzynki zadań

Pliki spoza tej struktury (np. ServMod\handoff\*.md, ServMod\multibox\firmware\...) są materiałem pomocniczym.
Liczy się to, co jest w KONTRAKT.md; jeśli coś jest tylko w innym pliku, zleć dopisanie do kontraktu.

## Na starcie każdej sesji (obowiązkowo)
1. Przeczytaj CEL.md, KONTRAKT.md i końcówkę DECYZJE.md.
2. Przeczytaj swój plik inbox/<TWOJA_ROLA>.md i wykonaj zadania ze statusem OTWARTE.
3. Dopiero potem zacznij własną pracę.

## Zlecanie zadania innemu projektowi
Dopisz na końcu jego pliku inbox/<ROLA>.md:

### [ID] krótki tytuł
- Od: <twoja rola>   Data: <data>   Priorytet: wysoki/normalny/niski
- Status: OTWARTE
- Co: konkretny opis, czego potrzebujesz
- Po co: jaki problem to rozwiązuje u Ciebie
- Format wyniku: dokładnie co ma wrócić (plik, pole w KONTRAKT.md, typ ramki, wersja firmware…)
- Termin / zależność: kiedy potrzebne albo co blokuje

ID: <ROLA_ZLECAJĄCA>-<kolejny numer>, np. APP-007. Numer = następny wolny w całym folderze (sprawdź inbox obu stron).

## Odbiór i zamknięcie zadania
Po wykonaniu zmień Status na ZROBIONE i dopisz pod zadaniem:
- Wynik: co zrobiono, gdzie leży (ścieżki plików), wersja (np. firmware 0.6.3)
- Sprawdzone: skompilowane / przetestowane na sprzęcie / tylko napisane (nie wpisuj "działa", jeśli nie było testu)
- Zmiany w kontrakcie: tak/nie
Jeśli nie możesz wykonać: Status: ODRZUCONE + powód albo pytanie zwrotne.
Zleceniodawca odbiera wynik przy następnej sesji i zmienia status na ODEBRANE (albo dopisuje uwagi i otwiera nowe zadanie).

## Zmiana interfejsu (typ ramki, pole, kod statusu, format INFO, kolejność bajtów)
1. Najpierw zaktualizuj KONTRAKT.md (zwiększ numer wersji kontraktu na górze).
2. Dopisz wpis w DECYZJE.md: data, kto, co, dlaczego.
3. Zleć zadania dostosowawcze wszystkim dotkniętym projektom.
Nigdy nie zmieniaj interfejsu "po cichu" tylko w swoim kodzie.
Numery typów ramek są wspólne dla firmware i aplikacji: sprawdź w KONTRAKT.md, czy numer jest wolny, zanim go użyjesz
(przykład kolizji: 0x11 zajęte przez T_FC_BATCH, zlecenie odczytu przeniesiono na 0x12).

## Zasady
- Edytuj tylko: własny katalog z kodem, własny plik inbox (zamykanie zadań) i pliki wspólne wyłącznie przez dopisywanie
  (KONTRAKT.md zmieniasz tylko jako właściciel interfejsu, patrz niżej). Cudzych plików nie ruszaj.
- Właściciele interfejsów: BOX = ramki Box <-> aplikacja, INFO, kody statusu, firmware; APP = ekrany i logika aplikacji,
  format zapisu kopii zapasowych; WWW = treść i adresy strony.
- Niczego nie zakładaj o stanie innego projektu. Liczy się tylko to, co jest w plikach.
- Jeśli kontrakt jest niejasny lub sprzeczny, nie zgaduj: zleć pytanie właścicielowi interfejsu i zaznacz u siebie, że czekasz.
- Użytkownik wgrywa firmware i buduje aplikację ręcznie. Zlecenie jest ZROBIONE po stronie kodu; "przetestowane na sprzęcie"
  dopisuje ten, kto test zrobił (zwykle użytkownik, podaje wynik w rozmowie).
- Na koniec każdej sesji napisz użytkownikowi krótkie podsumowanie: co zrobiłeś, jakie zadania zleciłeś komu, na co czekasz.
