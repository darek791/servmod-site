# KONTRAKT Box <-> aplikacja
**Wersja kontraktu: 1.8 (2026-11-26)**  |  Właściciel: BOX  |  Odpowiada firmware 0.9.2 (dopisek 1.7: port serwisowy Danfoss FC przez USB host ch3, NAPISANE, nieskompilowane i niesprawdzone na sprzecie) oraz 0.9.0 (NAPISANE, nieskompilowane i niesprawdzone na sprzęcie: zapis SDO w zleceniu CANJ, gniazda TCP/UDP na ch5, wymiana ISO-TP na ch1). Zlecenie odczytu CANJ z 0.8.0 sprawdzone na Lenze 8400 (397 wpisów/s).

Zmiany tylko wg PROTOKOL.md ("Zmiana interfejsu"). Podrobny opis ramek FC: ServMod\handoff\servmod-box-fc-protocol-v0.6.2.md
(nazwa pliku zostaje, treść = 0.6.3). Ethernet: ServMod\multibox\firmware\servmod_box_v0\ETHERNET_BRIEF.md.

## Transport
- Wi-Fi: Box jest AP (SSID ServMod-Box-XXXX, hasło w config.h AP_PASS), TCP 192.168.4.1:4400. BLE: GATT, ramki w kawałkach T_BLE_CHUNK, MTU ustawialne (konsola `mtu`).
- Ten sam strumień: ramki binarne albo konsola tekstowa (Box rozpoznaje po pierwszym bajcie 0xA5).
- Aplikacja łączy się z Boxem tylko przez Wi-Fi i BLE. Natywne USB-C płytki służy do falownika Hitachi (ch3), nie do telefonu.

## Ramka binarna
`A5 | type | ch | len u16 LE | ts_us u32 LE | payload (len) | CRC16 u16 LE`
CRC = CRC-16/Modbus (init 0xFFFF, poly 0xA001) liczone od bajtu `type` do końca payloadu. ts_us = mikrosekundy od startu Boxa.
PAYLOAD_MAX = 512. Wszystkie liczby wielobajtowe little-endian, o ile nie napisano inaczej.

## Kanały (ch)
0 RS-485 (UART1) | 1 CAN (TWAI, tylko nasłuch/nadawanie wg konfiguracji) | 2 RS-232 (UART2) | 3 USB host (Hitachi WL200/WJ200 albo port serwisowy Danfoss FC, HID; od 1.7)
4 krokowiec | 5 Ethernet W5500 | 0xFF = komunikaty ogólne (INFO/TEXT).

## Kody statusu (ST_*, w ACK i odpowiedziach)
0 OK | 1 BAD_PARAM | 2 LOCKED | 3 NOT_OPEN | 4 NOT_IMPL | 5 TIMEOUT | 6 BAD_CRC (zła suma / za krótka odpowiedź) | 7 WRONG_MODE | 8 BUSY | 9 NO_MEM (brak pamięci, od 1.4)

## Typy ramek
| Typ | Nazwa | Kier. | Payload |
|---|---|---|---|
| 0x01 | PING | app->Box | dowolny; Box odsyła PONG (0x81) z tym samym payloadem |
| 0x02 | GET_INFO | app->Box | brak; odpowiedź: T_TEXT ch=0xFF z tekstem INFO (patrz niżej) |
| 0x03 | SET_CFG | app->Box | baud u32 (0 = zamknij), bity u8, parzystość u8 (0 N,1 E,2 O), stop u8, tryb u8 (0 sniff, 1 modbus, 2 bridge, **3 fc**). ch1: baud = prędkość CAN |
| 0x04 | TX_RAW | app->Box | surowe bajty (ch0/2 UART; ch5 dane do gniazda drukarki) |
| 0x05 | MB_REQ | app->Box | timeout ms u16, potem PDU Modbus: slave, fc, dane (CRC dolicza Box). Odpowiedź 0x92 |
| 0x06 | UNLOCK | app->Box | u8: 1 odblokuj / 0 zablokuj (przy WRITE_LOCK 0 bez znaczenia) |
| 0x07 | SCAN | app->Box | ch0: skan adresów/baud RS-485; ch1: skan prędkości CAN |
| 0x08 | BLE_CHUNK | app->Box | kawałek ramki dla BLE |
| 0x09 | STEP | app->Box | polecenia krokowca (ch4), odpowiedź 0x95 |
| 0x0A-0x0E | JOB_BEGIN/DATA/START/STATUS/ABORT | app->Box | zlecenie ZAPISU Modbus. BEGIN: ch u8, slave u8, total u16, flags u8 (bit0 = zapis do EEPROM na końcu), timeout u16. DATA: seq u16, wpisy [addr u16 BE, n u8 (1 lub 2), n x word u16 BE]. Status: 0x96 |
| 0x0F | NET | app->Box | komendy Ethernet (ch5), odpowiedź 0x97/0x98; opis w ETHERNET_BRIEF.md |
| 0x10 | FC_REQ | app->Box | timeout ms u16 (0 = 250), pełny telegram FC (02 LGE ADR ... BCC). Odpowiedź 0x99 |
| 0x11 | **FC_BATCH** | app->Box | timeout ms u16 (na telegram, 0 = 250), count u8 (1..16), count x [len u8][telegram]. Odpowiedzi 0x99 (po jednej na telegram) + na końcu ACK |
| 0x12 | **FCJ** | app->Box | zlecenie odczytu FC, podkomendy 1 BEGIN, 2 DATA, 3 START, 4 ABORT, 5 STATUS, 6 FETCH. Opis w pliku protokołu FC. Opcjonalne, aplikacja może go nie używać |
| 0x15 | **CANJ** | app->Box (ch=1) | zlecenie odczytu SDO CANopen (od 1.4), podkomendy 1 BEGIN, 2 DATA, 3 START, 4 ABORT, 5 STATUS, 6 FETCH; opis w sekcji "Zmiany w wersji 1.4" |
| 0x16 | **SOCK_TX** | app->Box (ch=5) | dane do gniazda TCP/UDP (od 1.5): id u8, flags u8, [ip4 port u16], dane; opis w sekcji "Zmiany w wersji 1.5" |
| 0x17 | **ISOTP** | app->Box (ch=1) | żądanie ISO-TP (OBD-II/UDS) i odpowiedź (od 1.5); opis w sekcji "Zmiany w wersji 1.5" |
| 0x81 | PONG | Box->app | echo PING |
| 0x82 | INFO | Box->app | (rezerwa; INFO idzie jako T_TEXT 0x94, ch=0xFF) |
| 0x83 | ACK | Box->app | typ_komendy u8, status u8 |
| 0x90 | RX_DATA | Box->app | surowe bajty z ch (kawałki rozdzielone przerwą), ts = pierwszy bajt |
| 0x91 | CAN_FRAME | Box->app | flagi u8 (bit0 EXT, bit1 RTR), id u32, dlc u8, dane |
| 0x92 | MB_RSP | Box->app | status u8, odpowiedź Modbus z CRC |
| 0x94 | TEXT | Box->app | tekst ASCII (log, INFO) |
| 0x95 | STEP_ST | Box->app | stan krokowca |
| 0x96 | JOB_ST | Box->app | stan zlecenia zapisu: state, stop, done u16, total u16, ok u16, failed u16, store u8, lista błędów |
| 0x97 | NET_ST | Box->app | stan Ethernetu, 28 B |
| 0x98 | NET_EV | Box->app | zdarzenia Ethernet (probe, host, koniec, łącze) |
| 0x99 | **FC_RSP** | Box->app | po FC_REQ: status u8, telegram odpowiedzi. **Po FC_BATCH: idx u8 (od 0), status u8, telegram odpowiedzi** |
| 0x9A | FCJ_ST | Box->app | state u8, stop u8, done u16, total u16, ok u16, failed u16 |
| 0x9B | FCJ_RES | Box->app | from u16, n u8, n x [status u8][len u8][telegram] |
| 0x9D | **CANJ_ST** | Box->app (ch=1) | 18 B: state u8, stop u8, done u16, total u16, ok u16, aborted u16, noreply u16, other u16, bufUsed u16, bufCap u16 |
| 0x9E | **CANJ_RES** | Box->app (ch=1) | from u16, n u8, n x [status u8][len u8][dane] |
| 0x9F | **SOCK_RX** | Box->app (ch=5) | dane z gniazda TCP/UDP (od 1.5): id u8, flags u8, [ip4 port u16], dane (do 190 B) |
| 0xA0 | **ISOTP_RSP** | Box->app (ch=1) | odpowiedź ISO-TP (od 1.5): status u8, more u8, rid u32, dane |

## Tryb FC (Danfoss)
- Kanał ustawiony SET_CFG trybem 3 (np. 9600 8E1). W tym trybie Box odrzuca ruch na magistrali poza zapytaniami (brak RX_DATA).
- Telegram musi mieć STX 0x02 i długość = LGE + 2. Odpowiedź Box składa sam wg LGE i sprawdza BCC (XOR wszystkich bajtów oprócz ostatniego); do 2 powtórek w Boxie.
- Statusy w FC_RSP: 0 OK, 5 brak odpowiedzi, 6 zły BCC / za krótka. Błędy przed dotknięciem magistrali (1, 2, 3, 7, 8) idą jako ACK komendy.
- FC_BATCH: cała paczka jest sprawdzana przed wysłaniem; błąd = ACK z kodem i nic nie wysłane. Zakończenie = ACK(0x11, OK) po ostatnim FC_RSP.

## Tekst INFO (T_TEXT, ch=0xFF) – pola `klucz=wartość` oddzielone spacją
`fw`, `proto` (PROTO_VER 1), `chip`, `ap`, `ip`, `tcp`, `ble`, `ch0` (RS485 lub FC), `ch1..ch5`, `usb`, `job=1` (zlecenie zapisu),
**`fc=1`** (FC_REQ), **`fcb=1`** (FC_BATCH), **`fcjob=1`** (FCJ), `fc_n`/`fc_retry`/`fc_fail` (liczniki), `write` (OPEN | locked | UNLOCKED),
**`cansdojob=1`** (zlecenie SDO CANJ, od 1.4), `cansdow=0` (zapis SDO w zleceniu jeszcze nie ma), `net=1 eth=... eth_ip ...` (Ethernet). Aplikacja używa funkcji tylko, gdy flaga jest w INFO: `fcb=1` -> batch, inaczej `fc=1` -> FC_REQ, inaczej raw bridge.

## Timeouty (domyślne)
Modbus MB_REQ 500 ms | FC 250 ms na telegram | zlecenie zapisu 1000 ms (USB host 6500 ms) | ACK na TX_RAW do 1,5 s po stronie aplikacji.

## Znane ograniczenia
- Brak odczytu kontrolnego po zapisie (restore). WRITE_LOCK 0: zapis zawsze dozwolony.
- BLE: pojedyncza notyfikacja ograniczona MTU; duże ramki są dzielone przez aplikację/Box.

## Zmiany w wersji 1.1 (firmware 0.7.0): adapter USB-COM na porcie USB hosta, kanał 2 i T_SER_XCHG
Status: tylko napisane. Nieskompilowane, niesprawdzone na sprzęcie. Aplikacja ma zawsze używać wolniejszej ścieżki zapasowej, jeśli INFO nie ma flag poniżej.

### Zasada kanału 2 (ch2)
- Natywny port USB-C ma jedno urządzenie naraz: Hitachi (04A4, ch3) albo adapter USB-szeregowy. Adapter wpięty = Box otwiera go jako backend kanału 2.
- INFO: `ch2=USBSER` gdy adapter jest podpięty i rozpoznany, inaczej `ch2=RS232` (UART2 na płytce, wymaga modułu MAX3232). `usbser=FTDI/0403:6001` albo `usbser=none`.
- Rozpoznawane: FTDI (0403:6001/6010/6011/6014/6015) = protokół sprawdzony wg specyfikacji, CH34x (1A86:7523/5523/7522/5512), CP210x (10C4:EA60/EA70/EA71), CDC-ACM = EKSPERYMENTALNE. PL2303 nieobsługiwany.
- Backend wybiera się przy SET_CFG ch2 (ta sama ramka, co dotąd): jeśli adapter jest, SET_CFG ustawia go (baud, bity, parzystość, stop). baud=0 zamyka kanał. Wypięcie adaptera zamyka ch2 (INFO wraca do ch2=RS232).
- SET_CFG ch2: nowy opcjonalny bajt p[8]: bit0 = DTR, bit1 = RTS (1 = stan aktywny, domyślnie 0 = low). Dla OP17 zostaw 0.

### T_SER_XCHG 0x13 (app -> Box), odpowiedź T_SER_RSP 0x9C (Box -> app)
Wyślij bajty i oddaj odpowiedź, jak FC_REQ, ale ogólnie (nie tylko OP17). INFO: `xchg=1`.
Payload żądania: `timeout_ms u16` (0 = 250) | `idle_ms u8` (0 = 4 ms ciszy po ostatnim bajcie) | `framing u8` (0 = do ciszy idle, 1 = długość u16 LE na początku, liczona z całą ramką (OP17), 2 = stała liczba bajtów `expect`) | `expect u16` | `flags u8` (bit0 = ciąg dalszy TX w następnej ramce, Box tylko ACK; bit1 = wyczyść bufor TX) | bajty TX. Bufor TX 1100 B, RX 2048 B.
Odpowiedź T_SER_RSP: `status u8` (ważny gdy more=0; ST_TIMEOUT gdy brak bajtów) | `more u8` | dane (do 500 B na ramkę, kolejne ramki z more=1 aż more=0). ACK po T_SER_XCHG tylko przy błędzie albo bit0.
Czas rundy to opóźnienie łącza plus czas na przewodzie; nie ma ACK per ramka.

### INFO (zmiany)
Dodane: `ch2=USBSER|RS232`, `usbser=`, `xchg=1`, `lines=1` (DTR/RTS w SET_CFG). Usunięte z INFO (nadal w konsoli `status`): fc_n, fc_retry, fc_fail. Długość INFO < 512.

### Pinout i poziomy (APP-006 pkt 4)
Adapter użytkownika (FTDI USB-RS232) daje prawdziwe poziomy RS-232, więc moduł MAX3232 na płytce nie jest do tego potrzebny. Kabel panelu OP17 zostaje jak dotąd (patrz op17\CABLE.md). MAX3232 na UART2 (TX15/RX16) jest dopiero potrzebny, gdy nie ma adaptera.

### Konsola (do diagnostyki)
`usb` (stan i adapter), `cfg 2 9600 8N1 bridge [dtr] [rts]`, `lines <DTR> <RTS>`, `ser <ch> <timeout> <idle> <framing> <expect> <hex...>`.

### Poprawka
fcjBegin: `len < 5` (APP-004), w 0.7.0.

## Zmiany w wersji 1.2 (firmware 0.7.1): CAN nadawanie (APP-005)
Status: tylko napisane, niesprawdzone na sprzęcie. Bez flagi INFO `can_tx=1` aplikacja zostaje przy nasłuchu.

- Domyślnie CAN startuje jak dotąd: listen-only (nie nadaje, nie potwierdza ramek, bezpieczne dla magistrali).
- SET_CFG ch1: baud u32 (0 = zamknij), bits/par/stop/mode ignorowane, **opcjonalny bajt p[8]: bit0 = tryb AKTYWNY** (nadawanie, potwierdzanie ramek). Brak bajtu = listen-only. Aktywny tryb włączaj tylko przy znanej prędkości, bo przy złej wywołuje błędy na magistrali.
- **T_CAN_TX 0x14** (app -> Box, ch=1): `flags u8` (bit0 EXT 29-bit, bit1 RTR) | `id u32 LE` | `dlc u8` (0-8) | `data[dlc]` (przy RTR brak danych). Odpowiedź: T_ACK ze statusem: ST_OK (ramka w kolejce nadawczej), ST_NOT_OPEN (CAN wyłączony), ST_WRONG_MODE (CAN startował jako listen-only), ST_BAD_PARAM, ST_LOCKED, ST_TIMEOUT (kolejka pełna), ST_BUSY (magistrala w stanie bus-off, Box uruchomił odzyskiwanie, powtórz za chwilę). ST_OK nie oznacza, że ktoś ramkę potwierdził na magistrali.
- Ramki odebrane (też odpowiedzi na nasze) przychodzą jak dotąd jako T_CAN_FRAME 0x91 (flags, id u32, dlc, dane). Własne ramki nie wracają.
- Blokada: przy WRITE_LOCK 1 bez UNLOCK przechodzi tylko odczyt SDO CANopen (id 0x601..0x67F, dane[0] & 0xE0 = 0x40 lub 0x60). Przy WRITE_LOCK 0 (obecnie) przechodzi wszystko.
- INFO: `can_tx=1`; `ch1=CAN(listen-only)` zmienia się na `ch1=CAN(active)` gdy CAN działa w trybie aktywnym (prefiks `ch1=CAN(` stały).
- Konsola: `cfg 1 <bps> 1` (aktywny), `cantx <id> <ext 0|1> [hex...]`, `cansdo <node> <index> <sub>` (odczyt SDO, odpowiedź widać jako ramka 0x580+node), `canstat`.
- Sprzęt: moduł WCMCU-230 (SN65HVD230), CTX -> GPIO4, CRX -> GPIO5, brak pinu Rs (stale szybki tryb). Terminator 120 Ω na magistrali, nie ma go w module.

## Zmiany w wersji 1.3 (firmware 0.7.2): ch2 na UART2 (MAX3232) jako pełnoprawny backend (APP-007)
Status: tylko napisane, niesprawdzone na sprzęcie.
- Backend ch2 wybiera się sam przy SET_CFG ch2: jest wpięty adapter USB-szeregowy = adapter, brak adaptera = UART2 (TX GPIO15, RX GPIO16, przez moduł MAX3232). INFO `ch2=RS232` oznacza UART2, `ch2=USBSER` adapter. Z modułem MAX3232 NIE wpinaj adaptera USB-COM do portu USB-C, bo adapter przejmie kanał 2.
- SET_CFG ch2 (baud, 8N1/8E1 itd.), T_TX_RAW, T_SER_XCHG (framing idle, u16 LE, stała długość) działają tak samo na UART2 jak na adapterze (ten sam kod, ścieżka c.io). Bufor RX UART2 = 4096 B, bufor odpowiedzi T_SER_XCHG 2048 B: ramka 1044 B przy 19200 bez gubienia bajtów, o ile Box nie robi jednocześnie długiej blokującej operacji.
- DTR/RTS: bajt p[8] w SET_CFG jest ignorowany na UART2. **INFO `lines=1` tylko gdy adapter USB jest wpięty (backend USBSER), przy UART2 `lines=0`.** Aplikacja ma sprawdzać lines w chwili użycia, nie raz przy starcie.
- Okablowanie (do zweryfikowania miernikiem/pętlą, nie ze zdjęcia): moduł MAX3232 zasilany 3,3 V (nie 5 V, bo poziomy na GPIO). Sygnały logiczne: pin modułu, który WYCHODZI do mikrokontrolera (odbiór z DB9), do GPIO16 (RX); pin modułu, który WCHODZI od mikrokontrolera (nadawanie na DB9), do GPIO15 (TX). Opisy TXD/RXD na tanich modułach bywają z perspektywy mikrokontrolera albo modułu: jeśli test pętli milczy, zamień te dwa przewody (niegroźne, oba 3,3 V). GND wspólna.
- Test pętli: zewrzyj piny 2 i 3 gniazda DB9, w konsoli `cfg 2 9600 8N1 bridge`, potem `ser 2 500 0 2 1 00 00 00 00`: oczekiwana odpowiedź 00 00 00 00. Cisza = zamień przewody TX/RX modułu albo sprawdź zasilanie.
- Kabel do OP17 i falowników: moduł z gniazdem żeńskim DB9 zwykle ma układ PC (DTE): pin 2 = dane od urządzenia do Boxa, pin 3 = dane z Boxa do urządzenia, pin 5 = GND. Wtedy idzie ten sam kabel co dla zwykłego adaptera USB-RS232 (używanego dotąd z PC), a nie null-modem. Potwierdź pętlą oraz rozmową z panelem; jeśli nie odpowiada, spróbuj null-modemu (2 i 3 zamienione).

## Zmiany w wersji 1.4 (firmware 0.8.0): zlecenie odczytu SDO CANopen w Boxie (APP-012)
Status: tylko napisane, niesprawdzone na sprzęcie (składnia bloku sprawdzona, pełna kompilacja i test na Lenze 8400 przez użytkownika). Bez flagi INFO `cansdojob=1` aplikacja zostaje przy odczycie po jednej ramce (T_CAN_TX + T_CAN_FRAME).
Wymaga CAN ch1 w trybie AKTYWNYM (SET_CFG ch1 z p[8] bit0 = 1), tak jak T_CAN_TX.

**T_CANJ 0x15** (app -> Box, **ch = 1**), pierwszy bajt payloadu = podkomenda. Odpowiedź na BEGIN/DATA/START/ABORT: T_ACK(0x15, status); na STATUS: T_CANJ_ST; na FETCH: T_CANJ_RES (bez ACK).
- **1 BEGIN**: `node u8 (1..127) | total u16 (1..4096) | timeout_ms u16 (0 = 100, na obiekt i na segment) | flags u8` (flags = 0; bit0 = zlecenie zapisu, jeszcze nie ma: ST_NOT_IMPL). Statusy: OK, BAD_PARAM, NOT_OPEN (CAN wyłączony), WRONG_MODE (CAN nieaktywny), BUSY (zlecenie trwa), NO_MEM (Box nie ma 16 KB bufora wyników).
- **2 DATA**: `seq u16 (0,1,2..; powtórzony ostatni seq jest ignorowany) | wpisy` , wpis odczytu = `op u8 (=0) | index u16 | sub u8` (4 B). Op 1 (zapis: index u16, sub u8, len u8, dane) zarezerwowane, na razie ST_NOT_IMPL. Wpisów na ramkę tyle, ile mieści PAYLOAD_MAX 512 (do 127). Po komplecie `total` wpisów Box przechodzi do stanu READY.
- **3 START**: wymaga READY; Box czyści wyniki i zaczyna. **4 ABORT**. **5 STATUS** (-> CANJ_ST). Box sam wysyła CANJ_ST co 100 wpisów i na końcu.
- **6 FETCH**: `from u16`. Odpowiedź CANJ_RES: `from u16 | n u8 | n x [status u8][len u8][dane]`, następne zapytanie od from+n. Wyniki można pobierać także W TRAKCIE zlecenia (tylko wpisy poniżej `done`); BAD_PARAM gdy from >= done.
- **Status wpisu**: 0 OK (dane = wartość, 1..128 B: expedited do 4 B albo segmentowane), 1 ABORT (dane = kod abortu SDO u32 LE, np. 0x06020000 obiekt nie istnieje, 0x06090011 brak sub-indeksu; to normalny wynik), 2 BRAK ODPOWIEDZI (len 0), 3 BŁĄD PROTOKOŁU/TX (len 0), 4 OK ale ucięte do 128 B (len 128).
- **CANJ_ST**: state (0 idle, 1 loading, 2 ready, 3 run, 4 done, 5 stopped), stop (0 brak, 1 przerwane, 2 NO_NODE: 5 braków odpowiedzi z rzędu, 3 bus-off (wpis nie policzony, zacznij od nowa), 4 bufor wyników pełny (pobierz wyniki i uruchom resztę jako nowe zlecenie), 5 CAN nieaktywny), done, total, ok (OK + ucięte), aborted, noreply, other, bufUsed, bufCap (B; 16-48 KB, wpis ~6 B abort, 2 + len dane).
- Równoległość: T_CAN_TX, inne ramki CAN i sterowanie PDO działają w trakcie zlecenia (to samo TWAI). Odpowiedzi SDO 0x580+node, które należą do zlecenia, Box zużywa sam i NIE przekazuje jako T_CAN_FRAME; wszystkie inne ramki (też spóźnione odpowiedzi) idą do aplikacji jak dotąd.
- Zapis zlecenia podlega WRITE_LOCK (gdy powstanie). Odczyt przechodzi zawsze.
- Konsola do pomiaru: `canjob <node> <idx_od> <idx_do> [sub] [ms]` (np. `canjob 1 0x5E00 0x5FFF 0`) uruchamia zlecenie i po końcu wypisuje wpisów/s; `canjres [od] [n]` pokazuje wyniki.

## Zmiany w wersji 1.5 (firmware 0.9.0): zapis SDO w zleceniu (APP-013), gniazda TCP/UDP na ch5, wymiana ISO-TP na ch1
Status: tylko napisane, niesprawdzone na sprzęcie i nieskompilowane. Każda funkcja ma własną flagę INFO; bez flagi aplikacja zostaje przy wolniejszej ścieżce. Dotychczasowe ramki działają bez zmian (gniazdo drukarki NC_TCP_OPEN / T_TX_RAW na ch5 zostaje jak było).

### A. Zapis SDO w zleceniu CANJ (flaga INFO `cansdow=1`)
- BEGIN: `flags` bit0 = 1 oznacza zlecenie, które może zawierać wpisy zapisu. Przy `flags` = 0 wpis op 1 daje ST_BAD_PARAM.
- DATA: nowy wpis zapisu `op u8 (=1) | index u16 | sub u8 | len u8 (1..4) | dane[len]` (5 + len B). Wpisy odczytu (op 0, 4 B) i zapisu mogą być wymieszane w jednym zleceniu, kolejność wykonania = kolejność wpisów. Zapis tylko expedited (do 4 B; segmentowany zapis stringów NIE istnieje). Dla wpisu zapisu gdy WRITE_LOCK 1 i brak UNLOCK: ACK ST_LOCKED na całą ramkę DATA (nic nie jest zapisywane).
- Wynik wpisu zapisu w CANJ_RES: status 0 OK (len 0; węzeł potwierdził 0x60), 1 ABORT (dane = kod abortu SDO u32 LE, np. 0x06010002 próba zapisu do obiektu tylko do odczytu, 0x06090030 wartość poza zakresem), 2 BRAK ODPOWIEDZI (len 0; stan zapisu nieznany, sprawdź odczytem), 3 BŁĄD PROTOKOŁU/TX (len 0). Liczniki ok/aborted/noreply/other w CANJ_ST liczą wpisy odczytu i zapisu razem.
- Zasady stopu bez zmian: 5 braków odpowiedzi z rzędu = stop 2. Odczyt zwrotny po zapisie robi aplikacja (osobne zlecenie albo wpis odczytu po wpisie zapisu).
- Pamięć: zlecenie z wpisami zapisu ma ten sam limit total 4096; Box trzyma żądania w PSRAM, gdy jest, inaczej w RAM (NO_MEM przy braku).

### B. Gniazda TCP/UDP na ch5 (flagi INFO `sock=1 sockn=4`)
Do protokołów przemysłowych po Ethernecie, które aplikacja implementuje u siebie: Modbus TCP (502), FINS UDP (9600) i TCP, Mitsubishi MC (TCP/UDP), BACnet/IP (UDP 47808), EtherNet/IP i Logix (TCP/UDP 44818), S7comm (TCP 102), OPC UA (TCP 4840). Box tylko przekazuje bajty, nie interpretuje protokołu. Do 4 gniazd naraz (id 1..4), niezależnie od starego gniazda drukarki.
- **T_NET podkomenda 9 SOCK_OPEN** (`NC_SOCK_OPEN`): `9 | id u8 (1..4) | proto u8 (0 TCP klient, 1 UDP) | ip[4] | port u16 LE | local_port u16 LE (UDP, 0 = dowolny; przy TCP ignorowany) | flags u8 (bit0 = broadcast dozwolony, tylko UDP) | timeout ms u16 (połączenie TCP, 0 = 3000)`; razem 14 B. Dla UDP `ip:port` = domyślny adres docelowy (może być 0.0.0.0:0, jeśli każda ramka nadawcza podaje adres). Otwarcie zajętego id zamyka stare gniazdo. ACK: OK = przyjęte (wynik dla TCP przychodzi zdarzeniem), NOT_OPEN (brak łącza/IP), BAD_PARAM, BUSY (żądanie na tym id jeszcze trwa).
- **T_NET podkomenda 10 SOCK_CLOSE**: `10 | id u8` (id 0 = wszystkie). ACK OK.
- **Zdarzenie T_NET_EV (0x98, ch5) typ 5 = NE_SOCK**: `5 | id u8 | state u8`, state: 0 zamknięte (przez nas), 1 otwarte, 2 odmowa połączenia, 3 timeout, 4 błąd, 5 zamknięte przez drugą stronę. Po 2..5 gniazdo jest zwolnione.
- **T_SOCK_TX 0x16** (app -> Box, ch=5): `id u8 | flags u8 (bit0 = adres docelowy podany: ip[4] port u16 LE, tylko UDP) | dane`. Dane do 490 B w ramce. ACK: OK (przyjęte do wysłania), NOT_OPEN (gniazdo nie jest otwarte), BAD_PARAM, BUSY (bufor TCP pełny, powtórz ramkę za chwilę), TIMEOUT. Gniazdo to sam transport: Box nie sprawdza WRITE_LOCK, blokadę zapisu pilnuje aplikacja (protokół nad gniazdem).
- **T_SOCK_RX 0x9F** (Box -> app, ch=5): `id u8 | flags u8 (bit0 = źródło podane: ip[4] port u16 LE, UDP) | dane` (do 190 B w ramce, strumień TCP bywa dzielony na kawałki; granice datagramów UDP zachowane: jeden datagram dłuższy niż 190 B jest ucinany do 190 B).
- Limity: lwIP ma ograniczoną liczbę gniazd; przy otwartych gniazdach `sweep` ma ich mniej (skanuje wolniej). Gniazda zamykane przy utracie łącza (zdarzenie 4/5).
- Konsola: `sock <id> tcp|udp <ip> <port> [local]`, `ssend <id> <hex...>`, `sclose [id]`, `sstat`.

### C. Wymiana ISO-TP (ISO 15765-2) na ch1: OBD-II, UDS (flaga INFO `isotp=1`)
Wymaga CAN w trybie AKTYWNYM i znanej prędkości (500 kbit/s typowo dla OBD-II). Box składa i rozkłada wielu-ramkowe ramki (SF/FF/CF/FC), a aplikacja widzi tylko żądanie i pełną odpowiedź. Niezgodne z CANJ: gdy trwa zlecenie CANJ, ACK ST_BUSY.
- **T_ISOTP 0x17** (app -> Box, ch=1): `txid u32 LE | rxid u32 LE | flags u8 | timeout ms u16 (0 = 1000; czekanie na początek odpowiedzi) | dane żądania (1..500 B)`; nagłówek 11 B. flags: bit0 = identyfikatory 29-bitowe, bit1 = bez dopełniania (domyślnie ramki 8 B dopełnione bajtem 0x55). `rxid` = 0 oznacza adresowanie funkcjonalne OBD-II: Box przyjmuje pierwszą odpowiedź z 0x7E8..0x7EF (11 bit) albo 0x18DAF1xx (29 bit), wysyła do niej Flow Control i podaje jej id w odpowiedzi (`txid` zwykle 0x7DF albo 0x18DB33F1). Przy innych odpowiedziach z różnych ECU liczona jest tylko pierwsza.
- **Obsługa UDS**: odpowiedź `7F sid 78` (response pending) Box czeka dalej (do 20 razy po `timeout`), nie przekazując jej aplikacji. Inne odpowiedzi negatywne `7F ...` idą do aplikacji jako dane (status OK).
- **T_ISOTP_RSP 0xA0** (Box -> app, ch=1): `status u8 | more u8 | rid u32 LE (id, z którego przyszła odpowiedź) | dane` (do 490 B danych na ramkę; more = 1 gdy następna ramka T_ISOTP_RSP tej samej wymiany nadchodzi). status: 0 OK, 5 TIMEOUT (brak odpowiedzi), 6 błąd protokołu (zły numer ramki CF, FC overflow, przerwana wielu-ramkowa), 9 NO_MEM. Odpowiedź do 4095 B (bufor w Boxie 4096 B).
- ACK (bez T_ISOTP_RSP) tylko przy błędzie przed wysłaniem: BAD_PARAM, NOT_OPEN, WRONG_MODE (CAN nieaktywny), BUSY, LOCKED (WRITE_LOCK 1 bez UNLOCK).
- Konsola: `isotp <txid> <rxid> <ext 0|1> <hex...>` (np. `isotp 0x7DF 0 0 02 01 0C` obrotomierz OBD-II, `isotp 0x7E0 0x7E8 0 02 09 02` VIN z ECU 0x7E0), `obd <hex...>` skrót dla adresowania funkcjonalnego 0x7DF (rxid 0).
- J1939: nadal przez surowe T_CAN_TX i T_CAN_FRAME (osobna transport protocol BAM/RTS nie jest w 1.5).

### D. Skaner RS-485 (tylko tekst konsoli, bez zmian ramek)
`scan485` obejmuje dodatkowo 2400 i 230400 bit/s, a po znalezieniu urządzenia próbuje odczytu identyfikacji Modbus (FC 0x2B/0x0E) i wypisuje nazwę producenta i model, jeśli urządzenie je podaje. Ramki T_SCAN bez zmian.

### INFO (zmiany)
Nowe pola: `cansdow=1` (było 0), `sock=1`, `sockn=4`, `isotp=1`. INFO nadal mieści się w 504 B (limit 512 B).


## Zmiany w wersji 1.6 (2026-11-05, WWW): firmware Boxa do pobrania z serwera (tylko Pro). Box <-> aplikacja bez zmian
Nowy interfejs aplikacja <-> servmod.com (nie dotyczy ramek Box). Firmware nadal wgrywa sie kablem przez ESP32 Loader w aplikacji, bez OTA.
- **GET https://servmod.com/api/box/firmware** : manifest JSON od BOX: `version`, `build_date`, `proto`, `boxes{<id>{title, files[{file,label,sha256,bytes,offset,chip,flash_size_mb,use,verified,url}]}}`, `schematics[{file,url}]`. `url` jest wzgledny (`/api/box/firmware/<file>`), dolacz do https://servmod.com.
- **GET /api/box/firmware/<file>** : plik .bin (tylko pliki z manifestu), `Content-Disposition: attachment`. **GET /api/box/doc/<file>** : schemat (png/svg).
- Autoryzacja (tylko Pro, sprawdzana na serwerze): naglowek **`X-Licence: <kod aktywacyjny WL1...>`** (ten sam kod, ktory aplikacja ma w licencji; serwer sprawdza podpis, ze urzadzenie nie zostalo zwolnione, ze uprawnienie nie jest cofniete i ma PRO albo ALL). Strona uzywa ciasteczka sesji zamiast naglowka.
- Kody: 200 OK, 401 brak lub zly kod licencji / niezalogowany, 403 konto bez Pro (sama Subskrypcja to nie Pro), 404 firmware jeszcze nie opublikowany lub nieznany plik, 429 za duzo zapytan (60/h na kod), 503 serwer nie ma klucza do sprawdzania licencji.
- Weryfikacja po stronie aplikacji: porownac SHA-256 i `bytes` z manifestu przed wgraniem; offset 0x0 dla `*_full.bin`, 0x10000 dla `*_app.bin`. Aplikacja nie powinna pokazywac pobierania, gdy licencja nie ma PRO/ALL (serwer i tak odmowi).
- Wersje: nowa wersja firmware = nowe pliki + firmware.json od BOX w ServMod\handoff\www_assets\box_firmware, WWW wgrywa je na serwer; manifest zmienia `version`.

## Zmiany w wersji 1.7 (2026-11-14, firmware 0.9.2): port serwisowy Danfoss FC 301/302/280 przez USB host Boxa (APP-018)
**Status: NAPISANE, nieskompilowane, niesprawdzone na sprzecie.** Wersja 1.6 sie nie zmienia dla Hitachi i adapterow USB-szeregowych.
- **Rozpoznanie urzadzenia na ch3** (po VID): 04A4 = Hitachi (Modbus: MB_REQ, jobs jak dotad); **1E46 (dowolny PID) albo 134D:FC30 = Danfoss FC, HID** (nowe); inne = adapter USB-szeregowy (ch2) albo "nieobslugiwane".
- **INFO**: nowa flaga **`dfhid=1`** = firmware ma backend HID Danfoss na ch3. Pole `usb=` ma teraz wartosci: `none` | `serial` | `VID:PID` (urzadzenie gotowe na ch3; Hitachi = 04A4:xxxx, Danfoss = 1E46:xxxx lub 134D:FC30) | **`VID:PID/unsup`** (wpiete, ale Box go nie obsluguje; np. `usb=134D:FC30/unsup` gdy brak interfejsu z endpointami IN+OUT) | `error` | `off`. Bez spacji w wartosci, zeby parser kluczy `klucz=wartosc` nie zgubil tokenu. INFO dalej < 512 B (ok. 330 B).
- **Diagnostyka w konsoli** (T_TEXT): po wpieciu KAZDEGO urzadzenia Box wypisuje `USB host: device VID:PID class=.. ` oraz kazdy interfejs (klasa/podklasa/protokol) i endpoint (adres, typ, mps, interval). Konsola `usb` pokazuje stan ch3 i `status` tez.
- **FC na ch3**: te same ramki co na ch0: **FC_REQ (0x10), FC_BATCH (0x11), FCJ (0x12)** z `ch=3`; odpowiedzi T_FC_RSP (0x99), T_FCJ_ST (0x9A), T_FCJ_RES (0x9B) jak na ch0; kody 0 OK, 5 timeout, 6 zly BCC. BCC, powtorzenia (2) i liczniki w Boxie. Zapis (AK zapisowe) podlega tej samej blokadzie co na ch0 (ST_LOCKED).
- **Bez konfiguracji kanalu**: ch3 nie wymaga T_SET_CFG ani trybu `fc`; wystarczy, ze `usb=` pokazuje urzadzenie Danfoss. Brak urzadzenia = ST_NOT_OPEN (ACK albo status w odpowiedzi).
- **Ramowanie HID (w Boxie)**: raport 64 B; OUT = `04`, dlugosc, telegram FC, reszta `FF`; IN = `03`, dlugosc, telegram. Przed zapytaniem Box wyrzuca stary raport z IN; HID SET_IDLE jest wysylany przy wpieciu. Telegram do 62 B (dluzszy = ST_BAD_PARAM).
- **Odpowiedz dluzsza niz jeden raport** (np. 15-98, tekst identyfikacyjny): Box oddaje tylko pierwszy raport (dlugosc < LGE+2), status OK, **BCC nie jest sprawdzany** (tak samo jak aplikacja na USB telefonu). Aplikacja ma to obsluzyc jak dotad przy bezposrednim USB.
- **Timeout**: domyslnie 250 ms jak FC; na HID zalecane 700 ms (jak w aplikacji). Czas jest do pierwszej poprawnej odpowiedzi.
- **Modbus (MB_REQ/MBJ) na ch3 przy Danfossie** = ST_NOT_OPEN. Hitachi bez zmian.
- **Zapas**: aplikacja nadal moze uzyc USB telefonu bezposrednio (dzis dziala).
- Konsola testowa: `usb`, `fc 3 700 <hex telegramu>` (BCC dopisywany), `fcb 3 700 <hex...>`.

## Zmiany w wersji 1.8 (2026-11-26, APP): zakup przez Google Play Billing, odbior kodu aktywacyjnego z serwera (APP-031). Box <-> aplikacja bez zmian
**Status: PROJEKT, nic nie wdrozone, nic nie wyslane do Google.** Dotyczy tylko wariantu aplikacji `play` (Google Play). Wariant `web` nadal kupuje przez servmod.com (Stripe/PayPal, /api/shop/checkout + /claim bez zmian). Ten sam kod aktywacyjny WL1.payload.sig, ta sama licencja offline, te same ceny (Pro GBP 40 jednorazowo, Subscription GBP 20 rocznie).
- Produkty w Play Console (identyfikatory): **`servmod_pro`** (jednorazowy, non-consumable), **`servmod_sub`** (subskrypcja, plan podstawowy `yearly`, odnawianie automatyczne).
- Aplikacja: Play Billing Library -> `launchBillingFlow` z `setObfuscatedAccountId(<Device ID>)` (Device ID to skrot, nie dane osobowe). Po zakupie (stan PURCHASED, nie PENDING) aplikacja wola serwer. Aplikacja NIE potwierdza (acknowledge) zakupu sama: robi to serwer po wydaniu kodu.
- **POST https://servmod.com/api/shop/play/redeem** (naglowek `X-Requested-With: servmod`, JSON): `{"device_id":"XXXX-XXXX-XXXX-XXXX","product":"pro"|"sub","purchase_token":"<token Google>","package":"com.servmod.app"}`.
- Serwer: sprawdza token w Google Play Developer API (`purchases.products.get` dla pro, `purchases.subscriptionsv2.get` dla sub), czy stan = kupione (nie oczekujace, nie anulowane/zwrocone), czy zakup jest wazny (nie zwrocony). Zakup nalezy do konta Google: ten sam token mozna wykupic (redeem) na KAZDYM telefonie zalogowanym na to konto, kazdy telefon dostaje wlasny kod WL1 dla swojego Device ID (zmiana telefonu bez supportu). `obfuscatedExternalAccountId` jest tylko informacja, nie warunkiem. Serwer zapisuje liste Device ID na token; limit (limit 3 urzadzenia na zakup (decyzja uzytkownika 2026-11-26), ponad limit blad "contact support": wiecej urzadzen tylko przez support). Po wydaniu kodu potwierdza zakup w Google (acknowledge, w ciagu 3 dni, inaczej Google zwraca pieniadze). Powtorne wywolanie z tym samym tokenem i tym samym device_id jest bezpieczne (zwraca kod ponownie).
- Odpowiedz: 200 `{"status":"ready","code":"WL1...."}` (pro: funkcje PRO; sub: `SUB:<RRRRMMDD>` = data konca biezacego okresu z Google, bez dodatkowych dni; kolejne wywolanie po odnowieniu zwraca kod z nowa data) | 200 `{"status":"pending"}` (platnosc oczekuje, aplikacja ponowi) | 4xx `{"status":"error","detail":"<tekst dla uzytkownika po angielsku>"}` (zly token, zwrot pieniedzy, token zajety przez inne urzadzenie) | 429 | 503 (serwer bez dostepu do Google API).
- Przywracanie: przy starcie aplikacja (play) pyta Billing o zakupy i dla posiadanego a nieaktywowanego produktu wola redeem ponownie; przy aktywnej subskrypcji z kodem bliskim wygasniecia (7 dni) tez, zeby pobrac kod z nowa data.
- Po stronie WWW potrzebne (WYMAGA DZIALAN WLASCICIELA, nie WWW): konto serwisowe Google Cloud z dostepem do Google Play Developer API, powiazane w Play Console (Users and permissions); plik klucza zostaje TYLKO na serwerze (jak klucze Stripe), nigdy w repozytorium ani u APP.
- Zwroty i anulowania: sprawdzanie przez Voided Purchases API co dobe (lub RTDN, jesli WWW uzna za prostsze); dla pro uzyc tego samego mechanizmu cofniecia licencji, co dla firmware Box (kontrakt 1.6). Kod offline nie wygasa sam, wiec cofniecie dziala tylko dla funkcji sprawdzanych na serwerze (pobieranie firmware) - tak jak dzis.

- **Wymagania bezpieczenstwa serwera (przeglad 2026-11-26, dopisane do 1.8):** (1) produkt, pakiet i stan brac Z ODPOWIEDZI GOOGLE, nigdy z deklaracji aplikacji (token taniego/innego produktu nie moze dac Pro; pakiet musi byc com.servmod.app; stan PURCHASED, nie pending/cancelled; subskrypcja tylko ACTIVE lub CANCELED do konca okresu, nie ON_HOLD/PAUSED/EXPIRED); (2) KOLEJNOSC: najpierw acknowledge u Google, dopiero potem zwrot kodu (inaczej Google zwroci pieniadze po 3 dniach, a uzytkownik zachowa kod); jesli acknowledge sie nie uda, zwrocic blad/pending; (3) limit 3 Device ID liczony na zakup, a dla subskrypcji na lancuch linkedPurchaseToken (ponowna subskrypcja nie zeruje limitu); ten sam Device ID wielokrotnie = jedno miejsce; (4) limit zapytan na IP i na Device ID; (5) zakupy testowe (licence testers) oznaczyc w logu, nie traktowac jako przychod; (6) Voided Purchases API raz na dobe: zwrocony zakup blokuje nowe redeem i oznacza liste urzadzen; (7) subskrypcja: kod do konca okresu z Google plus 3 dni zapasu na brak internetu.
- **Zasada offline (decyzja uzytkownika 2026-11-26):** licencja dziala OFFLINE, bez pytania Google; Google/serwer tylko przy zakupie, przywracaniu i odnowieniu subskrypcji. Zdejmowanie licencji po zwrocie pieniedzy w aplikacji: NIE planowane (opcjonalnie pozniej, tylko miekko: nigdy offline, nigdy przy bledzie Billing). Zwroty obsluguje serwer (blokada nowych redeem). Uwaga: Device ID = hash ANDROID_ID, a ANDROID_ID zalezy od klucza podpisu aplikacji; wersja Play (podpis Google) ma INNY Device ID niz wersja web na tym samym telefonie, a reset do ustawien fabrycznych tez go zmienia (zuzywa miejsce w limicie 3, support).
