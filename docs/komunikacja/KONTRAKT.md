# KONTRAKT Box <-> aplikacja
**Wersja kontraktu: 1.1 (2026-10-17)**  |  Właściciel: BOX  |  Odpowiada firmware 0.7.0 (0.7.0 tylko napisane: nieskompilowane, niesprawdzone na sprzęcie; 0.6.3 sprawdzone przez APP)

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
0 RS-485 (UART1) | 1 CAN (TWAI, tylko nasłuch/nadawanie wg konfiguracji) | 2 RS-232 (UART2) | 3 USB host (Hitachi WL200/WJ200)
4 krokowiec | 5 Ethernet W5500 | 0xFF = komunikaty ogólne (INFO/TEXT).

## Kody statusu (ST_*, w ACK i odpowiedziach)
0 OK | 1 BAD_PARAM | 2 LOCKED | 3 NOT_OPEN | 4 NOT_IMPL | 5 TIMEOUT | 6 BAD_CRC (zła suma / za krótka odpowiedź) | 7 WRONG_MODE | 8 BUSY

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

## Tryb FC (Danfoss)
- Kanał ustawiony SET_CFG trybem 3 (np. 9600 8E1). W tym trybie Box odrzuca ruch na magistrali poza zapytaniami (brak RX_DATA).
- Telegram musi mieć STX 0x02 i długość = LGE + 2. Odpowiedź Box składa sam wg LGE i sprawdza BCC (XOR wszystkich bajtów oprócz ostatniego); do 2 powtórek w Boxie.
- Statusy w FC_RSP: 0 OK, 5 brak odpowiedzi, 6 zły BCC / za krótka. Błędy przed dotknięciem magistrali (1, 2, 3, 7, 8) idą jako ACK komendy.
- FC_BATCH: cała paczka jest sprawdzana przed wysłaniem; błąd = ACK z kodem i nic nie wysłane. Zakończenie = ACK(0x11, OK) po ostatnim FC_RSP.

## Tekst INFO (T_TEXT, ch=0xFF) – pola `klucz=wartość` oddzielone spacją
`fw`, `proto` (PROTO_VER 1), `chip`, `ap`, `ip`, `tcp`, `ble`, `ch0` (RS485 lub FC), `ch1..ch5`, `usb`, `job=1` (zlecenie zapisu),
**`fc=1`** (FC_REQ), **`fcb=1`** (FC_BATCH), **`fcjob=1`** (FCJ), `fc_n`/`fc_retry`/`fc_fail` (liczniki), `write` (OPEN | locked | UNLOCKED),
`net=1 eth=... eth_ip ...` (Ethernet). Aplikacja używa funkcji tylko, gdy flaga jest w INFO: `fcb=1` -> batch, inaczej `fc=1` -> FC_REQ, inaczej raw bridge.

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
