# DECYZJE (dziennik, tylko dopisujesz na końcu)
Format: data | kto | co | dlaczego

2026-10-17 | MODBOX | Założono folder _komunikacja (PROTOKOL, CEL, KONTRAKT 1.0, DECYZJE, inbox). Role: APP, MODBOX, WWW | Użytkownik przekazywał polecenia między projektami ręcznie
2026-10-17 | MODBOX | Tryb kanału FC (M_FC = 3), FC_REQ 0x10 / FC_RSP 0x99 (firmware 0.6.1) | Odczyt Danfoss przez surowy most był 3x wolniejszy od adaptera (0,26 s na telegram) i miał powtórzenia
2026-10-17 | APP | Pomiar na FC 280: 0.6.1 daje 106 s / 724 telegramów (adapter 48 s), 0 powtórzeń; reszta to opóźnienie łącza na każdy telegram | Wniosek z briefu servmod-box-fc-batch-brief.md
2026-10-17 | MODBOX | T_FC_BATCH = 0x11 (do 16 telegramów, odpowiedzi FC_RSP z idx, ACK na końcu), INFO fcb=1; zlecenie odczytu FCJ przeniesione z 0x11 na 0x12 | Batch jest tym, o co prosiła aplikacja; 0x11 było wolne tylko w firmware, aplikacja przydzieliła je batchowi
2026-10-17 | MODBOX | Firmware 0.6.0 dodał Ethernet ch5 (T_NET 0x0F, NET_ST 0x97, NET_EV 0x98); plik nagłówkowy to box_eth.h (nie eth.h: na Windows koliduje z <ETH.h>) | Wg ETHERNET_BRIEF.md
2026-10-17 | MODBOX | Blokada zapisu sprzętowym pinem odrzucona; WRITE_LOCK 0 zostaje | Decyzja użytkownika: za mało pożytku
2026-10-17 | APP | Test 0.59.23 + fw 0.6.3 (FC 280): FCJ BEGIN odrzucony (bad parameter), odczyt wrócił do T_FC_REQ, 106 s. Przyczyna: fcjBegin len<6 przy 5 bajtach ciała | Zadanie APP-004; aplikacja 0.59.24 dosyła bajt 0 jako obejście
2026-10-17 | APP | Test 0.59.24 + fw 0.6.3 (FC 280, Box): FCJ działa, 675 parametrów (690 telegramów) w 44,1 s, 0 powtórzeń (adapter 48 s, T_FC_REQ 106 s) | Cel z CEL.md osiągnięty; poprawka len<5 w firmware (APP-004) nadal zalecana, aplikacja działa z obecnym i poprawionym
2026-10-17 | APP | Zadanie APP-006 dla BOX: szybki tryb ramkowy RS-232 (ch2) pod Siemens OP17, opcjonalnie podsłuch | Użytkownik chce obsługi adaptera RS-232 przez Box; surowy most jest za wolny dla protokołu panelu
2026-10-17 | MODBOX | Kontrakt 1.1, firmware 0.7.0: obsługa adaptera USB-COM (FTDI sprawdzone wg specyfikacji; CH34x/CP210x/CDC eksperymentalne) jako backend ch2; nowa ramka T_SER_XCHG 0x13 / T_SER_RSP 0x9C (ogólna, framing: cisza, długość u16 LE, stała liczba); SET_CFG ch2 bajt DTR/RTS | Prośba użytkownika o pełną obsługę adaptera, nie tylko OP17 (APP-006). Tylko napisane, nieskompilowane
2026-10-17 | MODBOX | fcjBegin len<5 (APP-004) w 0.7.0; FC liczniki z INFO tylko w konsoli | Błąd zgłoszony przez APP; INFO musi mieścić się w 512 B
2026-10-17 | MODBOX | APP-006 pkt 3 (podsłuch dwóch linii) odrzucony | Płytka ma jeden RX na ch2; potrzebna zmiana sprzętu
2026-10-17 | MODBOX | Nazwa roli: instrukcja projektu mówi MODBOX, aplikacja pisze do inbox\BOX.md. Żywa skrzynka firmware = inbox\BOX.md, MODBOX.md jest wskaźnikiem | Uniknięcie rozjazdu
2026-10-17 | APP | Zadanie APP-007 dla BOX: kanal 2 na stale przez MAX3232 (UART2) zamiast adaptera USB-COM | Port USB Boxa obsluguje jedno urzadzenie (Hitachi albo dongle), do tego opoznienie USB; uzytkownik ma moduly JZK MAX3232
2026-10-17 | BOX | Rola firmware nazywa się BOX (nie MODBOX) w PROTOKOL.md, CEL.md, KONTRAKT.md i instrukcji projektu; skrzynka inbox\BOX.md; inbox\MODBOX.md to tylko wskaźnik | Zgodność z instrukcjami projektu APP
2026-10-17 | WWW | Strona odświeżona do aplikacji 0.60: moduł Backup, ServMod Box przeniesiony z Draft do In field testing (Ethernet, FC 280 44 s, WJ-C1 po RS-485), USB Tools Fake size/Recover, Hitachi WJ-C1 w tabeli sprzętu. Założono STATUS.md | Zgodność treści strony ze stanem z handoff i DECYZJE; statusy na stronie wg faktów
