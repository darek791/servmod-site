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
2026-10-17 | BOX | Kontrakt 1.2, firmware 0.7.1: CAN nadawanie. SET_CFG ch1 p[8] bit0 = tryb aktywny (domyślnie listen-only), T_CAN_TX 0x14, INFO can_tx=1 i ch1=CAN(active|listen-only), konsola cantx/cansdo | APP-005 (Lenze 8400 SDO). Tylko napisane, niesprawdzone
2026-10-17 | APP | Zadanie APP-008 dla BOX: pendrive w USB-A Boxa jako zdalne urzadzenie blokowe (MSC raw) dla USB Tools; najpierw ocena wykonalnosci | Uzytkownik dolozyl gniazdo USB-A; firmware nie ma MSC
2026-10-17 | APP | APP-008 zawezone: czesciowa obsluga pendrive (tylko odczyt plikow FAT) w tym samym porcie USB co Hitachi/USB-COM; cel: pliki z pendrive do Lenze po CAN lub do drukarki bez telefonu w torze danych | Wyjasnienia uzytkownika
2026-10-17 | APP | APP-008 obnizone do najnizszego priorytetu: obsluga pendrive (odczyt plikow) tylko jako zapasowa mozliwosc, bez przypisanej funkcji | Decyzja uzytkownika
2026-10-17 | BOX | Kontrakt 1.3, firmware 0.7.2: ch2 na UART2 (MAX3232) jako pełnoprawny backend, INFO lines=1 tylko gdy podłączony jest adapter USB; bez zmian ramek | APP-007. Niesprawdzone na sprzęcie
2026-10-18 | BOX | Firmware 0.7.3: polecenie konsoli lt [len] [count] (test pętli ch2, błędy i czas), status pokazuje write OPEN przy WRITE_LOCK 0; bez zmian w kontrakcie | APP-009 (OP17 przez UART2 + MAX3232: błąd 3 na drugiej ramce). Niesprawdzone
2026-10-18 | BOX | Firmware 0.7.4: canstat z nazwą stanu, deduplikacja powtarzanych ramek CAN w konsoli, komenda cantest (NO_ACK + samoodbiór); bez zmian w kontrakcie | APP-010 (TX CAN nie dochodzi na magistralę Lenze 8400). Niesprawdzone
2026-10-18 | BOX | Firmware 0.7.5: komenda canpin (test okablowania CTX/CRX bez kontrolera CAN); cantest 0.7.4 dał FAIL, tx_err=40, 0/5 odczytanych | APP-010, podejrzenie sprzętu CTX. Bez zmian w kontrakcie
2026-10-18 | BOX | Firmware 0.7.6: canpin z fazą szybkości; canpin 0.7.5 PASS, cantest FAIL, więc podejrzenie szybkości toru lub konfiguracji TWAI | APP-010. Bez zmian w kontrakcie
2026-10-18 | BOX | Firmware 0.7.7: canpin mierzy opóźnienie pętli CTX->CRX (ns) | cantest FAIL mimo canpin PASS i szybkości 20/20 (APP-010). Bez zmian w kontrakcie
2026-10-18 | BOX | cantest PASS na fw 0.7.7 (0.7.4 dawał FAIL); tor TX CAN sprawny, następny test na magistrali Lenze 8400 | APP-010. Bez zmian w kontrakcie
2026-10-18 | BOX | Test na Lenze 8400: Box active, 0 błędów, ACK działa; lawina 0x701 trwa, brak odpowiedzi SDO 0x581 na indeks 0x5EA1 | APP-010; diagnoza po stronie falownika. Bez zmian w kontrakcie
2026-10-18 | BOX | Firmware 0.7.8: canhold, czytelniejsze komunikaty BUS_OFF; pomiary: CG połączone, terminacja 60 ohm, a Lenze nadal bez ACK | APP-010. Bez zmian w kontrakcie
2026-10-18 | BOX | Przyczyna APP-010 (podejrzenie): pin Rs modułu SN65HVD230 na 2,2 V zamiast ok. 0 V, nadajnik nie steruje magistralą; do naprawy na module. Bez zmian w firmware i kontrakcie | Pomiary użytkownika
2026-10-18 | BOX | Korekta: pin Rs = 0 V (high-speed), hipoteza Rs odrzucona; APP-010 dalej otwarte, następny pomiar na pinach 1/6/7 układu w trakcie canhold | Poprawiony pomiar użytkownika

- 2026-10-19 00:25 BOX: firmware 0.7.9 (nieskompilowane) - nowa komenda konsoli `canburst [s]`: strumien prawdziwych ramek CAN (NO_ACK), do pomiaru sredniego napiecia CANH/CANL multimetrem. Powod: `canhold` (D nisko 15 s) pokazywal tylko krotki skok do ok. 1 V - podejrzenie limitu czasu dominanta w transceiverze. Brak zmian w kontrakcie.

- 2026-10-19 00:45 BOX: APP-010 wynik sprzętowy: w `canburst 15` (fw 0.7.9) CANH i CANL = 1,5 V zarówno na zaciskach modułu, jak i na pinach 6/7 układu (bez falownika), choć canpin PASS (pętla D->R 208/300 ns). Wniosek: nadajnik układu CAN nie steruje magistrali -> uszkodzony/niesprawny moduł (lub klon). Następny krok: wymiana modułu CAN i powtórzenie canburst, potem test z Lenze 8400. Brak zmian w kontrakcie.

- 2026-10-19 01:15 BOX: APP-010 przyczyna sprzetowa potwierdzona opinia klientow listingu: moduly CAN z podrobka SN65HVD230 (nadajnik nie steruje magistrali, RXD powtarza TXD) - to samo co u nas (canburst: CANH=CANL=1,5 V na pinach 6/7). Firmware i kontrakt bez zmian. Kupic modul od sprawdzonego dostawcy (TI/Microchip, np. MCP2551 5 V + dzielnik na CRX, lub TJA1051T/3), sprawdzic `canburst 15` bez Lenze, potem test z Lenze 8400. APP-010 nadal OTWARTE do tego testu.
2026-10-19 | APP | Rezygnacja z toru UART2 + MAX3232 (ch2 RS-232) w Boxie: urządzenia szeregowe (OP17, Omron Host Link/FINS, inne RS-232/RS-485) idą przez adapter USB-serial (w gnieździe USB hosta Boxa albo bezpośrednio w telefonie) | Decyzja użytkownika; APP-009 (błąd 3 na drugiej ramce przy MAX3232) przestaje być potrzebne | Kontrakt bez zmian (1.3), firmware może zostawić ch2 jako nieużywany

- 2026-10-19 23:55 BOX: APP-010 pomiar: w `canhold 15` bez falownika CTX na pinie modulu = 0 V (D dociera do modulu), a CANH=CANL=1,5 V na pinach 6/7 i zaciskach. Strona Boxa (IO4, przewod CTX) jest sprawna; modul CAN (dwa egzemplarze, w tym jeden z markingiem VP230) nie wystawia dominanta. Falownik Lenze po `cfg 1 500 1` nadal zalewa 0x701 (ok. 6850/s) = ACK z Boxa nie dociera. Nastepny krok: inny modul (markowy 3,3 V lub TJA1051/MCP2551 5 V + dzielnik 1k/2k na CRX); przed zakupem opcjonalnie pomiar CTX na pinie 1 ukladu (zimny lut). APP-010 OTWARTE.
2026-10-20 | APP | Lenze 8400 przez adapter OBD2 Wi-Fi (ELM327 v1.5, klon) porzucone: adapter odrzuca ramki CAN 8 B, przy 7/6 B brak odpowiedzi falownika; Lenze zostaje przy ServMod Box (APP-010). Nowy osobny moduł "OBD2 Scanner" (ELM327 po Wi-Fi/Bluetooth) w aplikacji 0.70.0 | Decyzja użytkownika; interfejs Box<->aplikacja bez zmian
2026-10-20 | APP | Użytkownik zgłasza działające połączenie CAN z Lenze 8400 przez ServMod Box z nowym modułem CAN (do potwierdzenia logiem); następny krok: test modułu Lenze w aplikacji (CanPort = ServMod Box): monitor, kody, błędy, backup | APP-010 (zamknąć po potwierdzeniu). Kontrakt bez zmian

- 2026-10-20 APP: 0.70.4: karta Lenze ma ten sam układ GUI co inne falowniki (Backup | Parameters | Control | Settings | Faults) i funkcje: rename/usuwanie backupu, tagi, fault reset, save parameters, factory reset. Bez zmian w kontrakcie Box<->aplikacja.

2026-10-23 APP: temat Lenze 8400 (CAN przez Box) zamknięty: backup, zapis do pamięci (C00002/11), compare i ręczna kontrola CAN sprawdzone na falowniku (0.70.12). Sterowanie wymaga 24 V na X5/RFR. Nie zmieniono interfejsu Box<->aplikacja.

2026-10-23 APP: zlecono BOX zadanie APP-012 (zlecenie wsadowe SDO CAN w Boxie, odczyt i potem zapis), bo odczyt Lenze po jednej ramce przez BLE/Wi-Fi jest za wolny (ok. 3200 zapytań na pełny backup). Interfejs zaprojektuje BOX (wersja kontraktu++), APP czeka na opis ramek.

2026-10-23 | BOX | Kontrakt 1.4: T_CANJ 0x15 (zlecenie odczytu SDO CANopen w Boxie, ch=1), T_CANJ_ST 0x9D, T_CANJ_RES 0x9E, status 9 NO_MEM, INFO cansdojob=1 cansdow=0; firmware 0.8.0 (nieskompilowane) | APP-012: pełny backup Lenze (ok. 3200 zapytań SDO) był za wolny przy obiegu telefon-Box na każdy obiekt; analogia do FCJ. Zapis SDO w zleceniu dopiero w etapie 2. Zadanie dla APP: BOX-013
2026-10-23 | BOX | APP-010 zamknięte: Lenze 8400 po CAN działa z modułem SN65HVD230 z innego źródła; moduł WCMCU-230 z poprzedniego zakupu (3 sztuki, jeden sprzedawca) nie wystawiał dominanta (canburst CANH=CANL=1,5 V) | Pomiary użytkownika 2026-10-19; kontrakt bez zmian

2026-10-23 APP: aplikacja 0.70.14 ma klienta CANJ (kontrakt 1.4) dla backupu i Compare Lenze, z fallbackiem. BOX-013 po stronie kodu zrobione; czekamy na kompilację firmware 0.8.0 przez użytkownika i test na falowniku. Kontrakt bez zmian.

2026-10-23 APP: test firmware 0.8.0 na Lenze 8400 (konsola, wynik użytkownika): `canjob` 512 wpisów w 1289 ms = 397 wpisów/s (291 OK, 221 abort, 0 braków odpowiedzi, bufor 2429/16384 B). Przy ok. 3200 wpisach pełny backup powinien trwać ok. 8 s. Firmware skompilowany i działa; test w aplikacji 0.70.14 jeszcze nie zgłoszony.

2026-10-23 | BOX | Rezygnacja z K-line (Webasto): bez transceivera L9637D i bez zacisku +12 V w płytce v4; GPIO39/40 wolne; UART2 tylko RS-232 | Decyzja użytkownika. Kontrakt bez zmian (K-line nie było w KONTRAKT.md). Płytka v4: gotowe moduły, DevKit + W5500 na stałe, zasilanie IP5306 (koncept w Projekcie: multibox-pcb-v4-concept)

2026-10-23 | BOX | Odłożone: jednoprzewodowe 5 V (nagrzewnice), bez konwertera BSS138 w Boxie; GPIO47 wolne. Płytka v4: budowa warstwowa (3 płytki ok. 86 x 46 mm, stos ok. 41 mm wg szacunku) | Decyzja użytkownika: Box ma być mniejszy. Interfejs Box<->aplikacja bez zmian (jednoprzewodowe nie było w kontrakcie)

2026-10-24 | BOX | Płytka v4 bez RS-232 i DB9 (OP17/ProSave odłożone); kod ch2 RS-232 w firmware zostaje, GPIO15/16 wolne w sprzęcie. Zmierzony rozstaw rzędów pinów HW-884: 20,86 mm zewn. (ok. 20,32 mm między środkami) | Decyzja użytkownika. Interfejs Box<->aplikacja bez zmian (INFO nadal może zgłaszać kanał 2; aplikacja ma obsłużyć brak sprzętu jak dotąd)

2026-10-24 | BOX | Płytka v4: jedna płytka dwustronna ok. 74 x 64 mm zamiast stosu trzech (stos wychodził grubszy i większy objętościowo) | Decyzja użytkownika. Interfejs Box<->aplikacja bez zmian

2026-10-24 | BOX | Korekta: płytka v4 NIE jest rysowana od zera; baza to kompaktowa v6_measured (85,8 x 35,4 mm, moduły pod DevKitem). Szkice "stos" i "74 x 64 mm" (artifact ServMod Box układ v4) unieważnione, były gorsze | BOX nie sprawdził wcześniej v5/v6 w folderze pcb. Zmiany do v7: W5500 20,32 mm, IP5306 zamiast TP4056 + step-up po testach, wymiary z pomiarów. Interfejs bez zmian

2026-10-24 | BOX | Płytka v7 (pcb\servmod_box_carrier_v7_w5500.kicad_pcb) = v6_measured z rozstawem rzędów W5500 20,32 mm (było 19,304), ścieżki rzędu R dopasowane, obrys 85,8 x 35,4 mm bez zmian | Pomiar HW-884 (20,86 mm na zewnątrz pinów). Nie sprawdzone w KiCadzie (DRC robi użytkownik); własna kontrola odstępów 0,2 mm w skrypcie: bez nowych naruszeń. TP4056 + step-up zostają do czasu testu IP5306. Interfejs bez zmian

2026-10-24 | BOX | USB-A host na kablu (gniazdo panelowe, 4 przewody lutowane do pól VBUS/D-/D+/GND). Płytka v8 (pcb\servmod_box_carrier_v8_usbwire.kicad_pcb) = v7 bez gniazda USB-A i bez 2 otworów montażowych (zamienione na przelotki GND). Prawa ściana wolna dla 2 USB-C DevKita (oba muszą być dostępne) | Decyzja użytkownika; obudowę drukuje po złożeniu płytki. Własna kontrola: połączenia sieci bez zmian, odstępy 0,2 mm bez naruszeń; DRC KiCada nie robiony. Interfejs bez zmian

2026-10-24 | BOX | Kontrakt 1.5 (firmware 0.9.0): (A) zapis SDO w zleceniu CANJ, wpis op 1 do 4 B, flaga `cansdow=1` (zadanie APP-013); (B) gniazda TCP/UDP na ch5 (T_NET 9/10, T_SOCK_TX 0x16, T_SOCK_RX 0x9F, zdarzenie NE_SOCK, `sock=1 sockn=4`) dla Modbus TCP, FINS, MC, BACnet/IP, Logix/CIP, S7comm; (C) wymiana ISO-TP na ch1 (T_ISOTP 0x17, T_ISOTP_RSP 0xA0, `isotp=1`) dla OBD-II i UDS; (D) skaner RS-485 szerszy (tekst konsoli) | Użytkownik: "popraw protokoły firmware aby rozszerzyć listę jak się da". Box przekazuje bajty, protokoły nad gniazdami i ISO-TP implementuje aplikacja. Stare gniazdo drukarki i wszystkie dotychczasowe ramki bez zmian. Wszystko napisane, NIESKOMPILOWANE i NIESPRAWDZONE na sprzęcie. Strona (WWW): lista obsługiwanych protokołów zmienia się dopiero po teście na sprzęcie, na razie bez zadań dla WWW

2026-10-24 | APP | Biznes: Box NIE jest sprzedawany fizycznie. Użytkownicy Pro dostają na stronie do pobrania schemat płytki i firmware Boxa do samodzielnego zbudowania na własnych podzespołach. Podział funkcji darmowych/płatnych: w trakcie ustalania (propozycja: darmowy odczyt/backup, płatny zapis/Restore/sterowanie + moduły) | Decyzja użytkownika. Zadania dla BOX (paczka do pobrania) i WWW (pobieranie dla Pro) dopiero po ustaleniu, co jest Pro i na jakiej licencji; interfejs Box<->aplikacja bez zmian

## 2026-10-24 (APP): App ID aplikacji
- DECYZJA użytkownika: docelowy App ID (applicationId) = `com.servmod.app`. Nazwa aplikacji "ServMod" wszędzie taka sama (app, strona, domena).
- Obecnie w buildach: `pl.grabowski.toolbox`. Zmiana na nowy ID = dla Androida nowa aplikacja (brak aktualizacji w miejscu, ustawienia/backupy trzeba przenieść ręcznie, sprawdzić licencje).
- Zmiana w app\build.gradle.kts dopiero przy pierwszym publicznym wydaniu (do tego czasu APK ze strony/dla testerów zostają na starym ID). Do uzgodnienia z użytkownikiem przed zmianą. Google Play odłożony; keystore wydaniowy do założenia przy tej okazji.

## 2026-10-24 (APP): miniaturki falowników = znacznik testu na sprzęcie
- DECYZJA użytkownika: przy karcie "How to connect" (wolne miejsce obok Show / Full screen) pokazujemy miniaturkę falownika. Miniaturki dodajemy STOPNIOWO, z własnych zdjęć użytkownika (zdjęcia z podręczników/internetu nie, prawa autorskie).
- Zasada: miniaturka modelu = znacznik, że ten model był fizycznie testowany/mamy go w ręku. Model bez zdjęcia = niesprawdzony na sprzęcie. Plik: assets\wiring\<klucz>_photo.png (opcjonalny; brak pliku = brak miniaturki).
- Zmiana App ID na com.servmod.app: przy następnym buildzie (0.73.1) razem z mechanizmem miniaturek, zanim ktokolwiek zainstaluje aplikację. Zmiany: applicationId w app\build.gradle.kts i ACTION_PERMISSION w HitachiUsb.kt. Po instalacji odinstalować starą 0.73.0 (nowa aplikacja dla Androida).

## 2026-10-24 (APP): 0.73.1 zrobione
- App ID zmieniony na com.servmod.app (build.gradle.kts, HitachiUsb.kt ACTION_PERMISSION). Mechanizm miniaturek: assets\wiring\<klucz>_photo.png (tap = powiększenie). Pierwsza: lenze_photo.png (Lenze 8400 StateLine C E84AVSCE3712SX0, 0.37 kW, SW 16.02, zdjęcie użytkownika).

## 2026-10-24 (APP): Lenze 8400 SPRAWDZONY na sprzęcie
- Użytkownik potwierdził: Lenze 8400 StateLine C (E84AVSCE3712SX0) działa przez CAN z ServMod Box, "wszystko działa" (zakres szczegółowo niewyliczony: do uzupełnienia, co dokładnie sprawdzono). Miniaturka lenze_photo.png = znacznik testu. Reszta marek nadal NIESPRAWDZONA.

## 2026-10-24 (APP): 0.74.0 silnik profili JSON
- DECYZJA uzytkownika: rozbudowa o nowe urzadzenia WSTRZYMANA, budujemy szkielet silnika JSON zeby pozniej dodawac urzadzenia latwiej.
- Zrobione: `mx2\DeviceProfile.kt` (parser JSON, wyrazenia, silnik komend/monitora/historii bledow), `DeviceProfiles.kt` (rejestr profili z assets\profiles). Nowy falownik Modbus RTU = profil JSON + lista parametrow, pojawia sie sam na liscie Inverters, w tagach i folderach backupow. Dokument: handoff\PROFILE_FORMAT.md, walidator: tools\validate_profile.py.
- ATV320 i V20 dzialaja juz z profili JSON (stary kod Kotlin: ServMod\_to_delete\AtvFaults.kt.0740, V20Faults.kt.0740). Klucze backupow/tagow bez zmian (atv320, v20), wiec stare backupy pasuja.
- Poza zakresem silnika (wymaga kodu): CAN (Lenze, B&R EX470 - potrzebny silnik CAN/Box), USB-HID, protokoly z wlasnymi sumami, termokontrolery ze specjalnymi trybami.
- Silnik testowany tylko symulacja (Kotlin w chmurze, pamiec Modbus udawana) i kompilacja; nie na telefonie ani falowniku.

## 2026-10-24 (APP): model platnosci - zgoda uzytkownika
- DECYZJA uzytkownika: trzy poziomy: Free, Pro (jednorazowy zakup, licencja offline jak dotad), Subscription (rocznie: nowe moduly i aktualizacje). Szczegoly podzialu funkcji (tabela) i ceny: do potwierdzenia po przedstawieniu tabeli w czacie 2026-10-24.

## 2026-10-24 (APP): podzial funkcji i ceny - DECYZJA uzytkownika
- Podzial zatwierdzony (tabela z czatu): Free = polaczenie, odczyt, monitor, historia bledow, backup do pliku, Compare, narzedzia terenowe; Pro = zapis parametrow, Restore, sterowanie reczne, reset bledow i fabryczny, pliki Boxa (schemat + firmware); Subscription = nowe moduly i marki wydane po zakupie, aktualizacje baz i profili JSON.
- NIE dzielimy na pojedyncze parametry. Pro jest na zawsze (dla wersji, ktora uzytkownik mial), subskrypcja tylko za nowe moduly i aktualizacje.
- Ceny (propozycja uzytkownika): Pro 40 GBP jednorazowo, Subscription 20 GBP rocznie. Do ustalenia: czy ceny z VAT, waluty dodatkowe, cena promocyjna na start.
- Do zrobienia w aplikacji (po decyzji o starcie sprzedazy): flagi licencji WRITE / CONTROL / SUBSCRIPTION z data wygasniecia w License.kt i tools\wl200_license.py; brak licencji = Free (zapis i sterowanie zablokowane z komunikatem).

## 2026-10-24 (APP): 0.74.1 i stan sprzetu
- 0.74.1: znaczniki polaczenia pod nazwami falownikow (dane z manuali; czesc pinoutow nadal niezweryfikowana).
- Uzytkownik: Lenze 8400 Factory reset DZIALA na sprzecie; Fault reset Lenze jeszcze nie testowany. Box ma skompilowany najnowszy firmware (wg uzytkownika; wiersz BOX w STATUS.md nalezy do BOX). Zdjecia falownikow beda dodawane stopniowo.

## 2026-10-24 (APP): Danfoss FC 280 USB dziala
- Uzytkownik: Danfoss FC 280 przez USB byl juz testowany i dziala. Poprawione: znacznik polaczenia w liscie (bez "untested"), tabela sprzetu. W kodzie od nastepnego builda (0.74.2).

## 2026-10-24 (APP): PowerFlex 525 i Hitachi WL200 w pelni sprawdzone
- Uzytkownik: wszystkie opcje PowerFlex 525 i Hitachi WL200 (USB) byly juz testowane na sprzecie i dzialaja. Tabela sprzetu poprawiona. Kandydaci na miniaturki (brak zdjec): Hitachi, PowerFlex, Danfoss FC 280, OP17.

## 2026-10-24 (APP): Hitachi WJ C1 USB przez Box
- Uzytkownik: WJ C1 przez USB DZIALA, ale tylko przez ServMod Box w trybie USB host. Bezposrednio do telefonu (OTG) nie dziala; mozliwa przyczyna: zasilanie. Hipoteza do sprawdzenia: OTG z zasilanym hubem / adapter OTG z doladowaniem. Zadanie dla BOX do rozwazenia: czy Box ma przekazywac USB C1 do aplikacji (jak obecnie) - bez zmian kontraktu.

## 2026-10-25 (APP): WJ C1 przez Box USB - wszystko dziala
- Uzytkownik: WJ C1 przez Box (USB host) - wszystkie opcje dzialaja; WL200 dziala przez USB. Zostaje tylko C1 bezposrednio do telefonu (OTG, podejrzenie zasilania) - niskie priorytet.

## 2026-10-25 (APP): Danfoss VLT 2800 w pelni sprawdzony
- Uzytkownik: VLT 2800 - zapis, Restore, sterowanie, odczyt na zywo dzialaja.

## 2026-10-25 (APP): manual Omron E5xC (H175) dodany
- Dodano inputs\manuals\Omron-E5xC-Communications-Manual-H175.pdf (E5CC, E5CC-U, E5EC, E5AC, E5DC, E5GC; 222 s.; CompoWay/F rozdz. 2-3, Modbus rozdz. 4-5, wersja H175-E1-17). Ustalenie z rozdz. 4: Modbus E5xC ma INNA mape zmiennych niz E5CN (tryb 4-bajtowy: wartosc 2 rejestry od adresu 0000, tryb 2-bajtowy od 2000) - nie jest to prosty dodatek do modulu E5CN. Rozbudowa wstrzymana; do zrobienia pozniej jako osobny profil.

## 2026-10-25 (APP): licencje Free / Pro / Subscription - 0.75.0
- Wdrozone w aplikacji: brak sciany aktywacji (Free bez kodu); cechy kodu: PRO = WRITE+CONTROL na stale, SUB:RRRRMMDD = subskrypcja do daty, ALL = wszystko (stare kody dzialaja). Nowe pliki Entitlements.kt, Gate.kt.
- Bramka Gate.deny() na: zapis parametrow, Restore (applyDiffs), bieg w przod/tyl, ustaw czestotliwosc, reset bledow, reset fabryczny, przywrocenie zrodla sterowania, zadana termoregulatora, Lenze (writesOk). Stop NIE jest blokowany.
- Nie objete bramka (do decyzji): OP17 zapis na panel, Box (pliki, firmware), pozostale moduly (wszystkie darmowe). Podzial na marki/moduly "sub" dopiero gdy pojawia sie moduly po sprzedazy.
- Kody: python tools\wl200_license.py code DEVICE-ID --name "Klient" --features PRO,SUB:20271025 (bez --days).
- Nieprzetestowane na telefonie: logika uprawnien przetestowana tylko w chmurze (testy jednostkowe), build OK.

## 2026-10-25 (APP): 0.75.1
- Decyzja uzytkownika: OP17 (zapis na panel) i Box (odblokowanie zapisu) tylko Pro. Znacznik planu FREE/PRO/FULL pod Settings (FULL = Pro + aktywna subskrypcja lub kod ALL). Autor w aplikacji: "DG". Nieprzetestowane na telefonie.

## 2026-10-25 (APP): przygotowanie pierwszego wydania
- Lista kontrolna: handoff\servmod-release-checklist.md. Zlecono WWW APP-014 (cennik, licencje reczne, teksty prawne do akceptacji, feed aktualizacji). Blokada: keystore wydaniowy (uzytkownik uruchamia make-release-keystore.bat sam, hasla tylko u niego).

## 2026-10-25 (APP): klucz wydaniowy juz istnieje
- %USERPROFILE%\.servmod\servmod-release.jks + keystore.properties (z 9.10.2026). Log Gradle: "release key FOUND", podpisanie zakonczone sukcesem, wiec hasla w pliku sa poprawne. Buildy z Android Studio (takze 0.75.x) sa podpisane tym kluczem, wiec nie trzeba odinstalowywac. Zostaje kopia offline klucza i hasel (potwierdzenie uzytkownika).

## 2026-10-25 (APP): 0.75.2 = pierwszy build release
- Wariant release w Android Studio (Build Variants), APK 22 MB, wersja 191, bez flagi debuggable. Klucz wydaniowy: odcisk SHA-256 46:B7:91:CF:12:DE:93:FE:96:3F:13:09:6A:35:68:5C:28:20:65:FB:D3:AC:CB:99:93:BF:CA:5F:E7:34:36:F1. Nieprzetestowane na telefonie. Uwaga: Android Studio ma teraz aktywny wariant release; do szybkich testow mozna wrocic do debug.

## 2026-10-25 (APP): przeglad calosci projektu na zyczenie uzytkownika
- Przeczytano STATUS, DECYZJE, inbox APP/BOX/WWW, backlog, handoff, workflow. Wnioski: inbox\APP.md ma nieaktualne statusy (MODBOX-001/002/003, BOX-004 zrobione w kodzie, BOX-013 czeka na pomiar czasu backupu Lenze, BOX-014/015/016 niezaimplementowane w aplikacji); wiersz BOX w STATUS.md (fw 0.9.0 nieskompilowane) rozjezdza sie z informacja uzytkownika (najnowszy firmware skompilowany); wiersz WWW z 17.10 (app 0.60). Szczegoly: claude/servmod-backlog-addendum-O.md. Proces: buildy robi pod-agent (kontekst glowny bez zrzutow). Pro: pobieranie schematu i firmware Boxa wymaga sprawdzenia licencji na stronie (do zaprojektowania z WWW).

## 2026-10-25 (APP): Compare jak w Lenze dla wszystkich marek - 0.75.3
- Hitachi (Vm), Mx2 / profile JSON (ATV320, V20, Delta, INVT, ABB, Inovance, Yaskawa, Mitsubishi, Omron MX2), PowerFlex 525 i Danfoss (FC 280, VLT 2800): Compare uzywa danych odczytanych wczesniej (odczyt przy polaczeniu lub "Refresh drive data"), bez ponownego czytania falownika; gdy nic nie odczytano, najpierw czyta. Na karcie Backup: "Drive data in the phone: read at HH:MM:SS" + przycisk "Refresh drive data". Pamiec podreczna kasowana przy rozlaczeniu, na poczatku kazdego odczytu i po resecie fabrycznym; zapisy aktualizuja ja same. Interfejs Box<->aplikacja bez zmian. Nieprzetestowane na sprzecie.

## 2026-10-25 (APP): opcja USB w karcie "How to connect" - 0.75.4
- Karta pokazuje linijke "USB option" tam, gdzie jest bezposrednie USB bez Boxa: Hitachi WL200 (mini-B + OTG; WJ200: USB z telefonu moze nie zasilic, uzyc Box USB host lub RS-485) i Danfoss FC 280 (VLT 2800 tylko RS-485). Interfejs Box<->aplikacja bez zmian. Nieprzetestowane na sprzecie.

## 2026-10-25 (APP): karta polaczenia w dwoch sekcjach - 0.75.5
- Na zyczenie uzytkownika "How to connect" rozdzielona: "Connect with the phone (USB, no Box)" (USB-C, OTG, adaptery USB-RS485/RS232/Ethernet, bezposrednie USB WL200 i FC 280) oraz "Connect with the ServMod Box" (na razie przewaga: CAN i lacze bezprzewodowe; Lenze 8400 tylko przez Box). Interfejs Box<->aplikacja bez zmian. Nieprzetestowane na sprzecie.

2026-10-25 | BOX | Firmware 0.9.1: mbTransact (Modbus RTU) zna oczekiwaną długość odpowiedzi dla FC 1-6, 15, 16 i nie kończy ramki przerwą 4,4 ms, gdy ramka jest niepełna (czeka do 25 ms na kolejny bajt); kompletna ramka kończy odczyt od razu | Zgłoszenie użytkownika: backup Hitachi WL200 przerwany "USB error: ServMod Box: bad CRC / short reply" (ST_BAD_CRC). Przyczyna nie potwierdzona; podejrzenie: przerwa >4,4 ms między bajtami przy obciążeniu (Wi-Fi/BLE, CAN aktywny bez węzła). Interfejs Box<->aplikacja bez zmian

2026-10-25 | BOX | Firmware 0.9.1, uzupełnienie: z logu użytkownika (przed wgraniem 0.9.1) przyczyna "bad CRC / short reply" to pojedynczy bajt szumu (FF/EF/CF) tuż po nadaniu zapytania Modbus (moduł HW-519, automatyczny kierunek), po którym Box kończył odczyt po przerwie 4,4 ms, zanim falownik zaczął odpowiadać; poprawna ramka przychodziła ok. 4 ms później. mbTransact odrzuca teraz bajty przed adresem slave'a i czeka na pełną ramkę | Interfejs Box<->aplikacja bez zmian. NIESKOMPILOWANE, NIESPRAWDZONE
2026-10-25 | WWW | Imię i nazwisko usunięte ze strony i docs, autor jako DG (stopka, About, Terms, Privacy); język docelowo "we"/zespół | Prośba użytkownika; przed otwarciem sprzedaży strony prawne potrzebują właściwej nazwy działalności i adresu
2026-10-25 | WWW | APP-011 wykonane: 20 modułów (+Thermocontrollers, OBD2 Draft), tabela sprzętu ze statusem tested/not yet tried wg servmod-hardware-verified.md, plany Free/Pro/Subscription opisane na Pricing bez cen | Zgodność strony z aplikacją 0.75
2026-10-25 | WWW | Sklep: Stripe Checkout + podpisany webhook /api/pay/stripe, tabela orders, automatyczne wystawianie kodów po płatności (Device ID z pola przy płatności lub z konta); sklep zamknięty do wpisania kluczy; główny klucz licencji na serwerze (decyzja użytkownika); ceny z env (domyślnie Pro 40 GBP, Sub 20 GBP/rok) | Prośba użytkownika o płatności i automat; interfejs aplikacji bez zmian (kod WL1 jak dotąd, features PRO i SUB:data)

## 2026-10-25 WWW
Stripe: utworzono webhook "servmod-site" w sandboxie Qubivibe (test mode) -> https://servmod.com/api/pay/stripe (checkout.session.completed, async_payment_succeeded, charge.refunded, charge.dispute.created). Klucze wpisuje wlasciciel na PC przez install_payment_keys.cmd. Kontrakt bez zmian.

## 2026-10-25 WWW
Sklep w trybie testowym: zakup Pro kartą testową przeszedł, webhook OK, mail z paragonem wysłany. Kontrakt bez zmian.

## 2026-10-25 WWW
Zmiana interfejsu WWW<->APP (poza KONTRAKT Box): zakup z aplikacji. Nowe: POST /api/shop/checkout przyjmuje device_id + claim (sekret zakupu), GET /api/shop/claim?device=&token= zwraca {status: pending|ready|error, code}. Opis w docs/PAYMENTS.md i zadaniu WWW-001 w inbox/APP.md. Aplikacja nie dostaje kodu mailem ani przez ręczne kopiowanie.

## 2026-10-25 (APP): kupno i aktywacja licencji w aplikacji - 0.76.0 (WWW-001)
- Settings > Subscription: przyciski Buy Pro / Buy Subscription. POST /api/shop/checkout (X-Requested-With: servmod, claim = 32 losowe bajty base64url), url w Chrome Custom Tab (bez biblioteki androidx.browser), potem GET /api/shop/claim co 3 s do 10 min; ready = License.activate(code); error = komunikat. Sekret zakupu w prywatnych SharedPreferences do konca zakupu/10 min. Pole recznego kodu zostaje jako zapas. APP-011 odebrane (WWW commit ac6e4af). Interfejs Box bez zmian. NIEPRZETESTOWANE end-to-end (tylko build); test: karta Stripe 4242 4242 4242 4242.

## 2026-10-25 WWW
Test end-to-end zakupu z aplikacji 0.76.0 (Pro, karta testowa Stripe): aktywacja kodu w aplikacji OK (potwierdzone przez wlasciciela). Zlecono WWW-002 (ukryc Buy Pro gdy Pro aktywne).

## 2026-10-25 (APP): WWW-002 - 0.76.1
- Settings > Subscription: gdy licencja zawiera PRO lub ALL (Entitlements.has WRITE) - "Pro active", brak przycisku Buy Pro; przycisk Subscription zostaje (przy aktywnym SUB jako "Renew Subscription (yearly)"). Bez licencji bez zmian. Nieprzetestowane na telefonie (tylko build).

## 2026-10-25 (APP): brak podwojnego zakupu Subscription - 0.76.2
- Na zyczenie uzytkownika: gdy SUB (lub ALL) jest wazne, Settings > Subscription nie pokazuje przycisku zakupu, tylko "Subscription active until <data>. Nothing to buy."; po wygasnieciu "Renew Subscription (yearly)". Odnowienie z wyprzedzeniem niedostepne. Nieprzetestowane na telefonie.

## 2026-10-25 WWW
PayPal jako osobna integracja (Stripe UK nie pokazuje PayPal): checkout z provider=paypal, capture po stronie serwera, ten sam claim. Zlecono WWW-003 (APP). Kontrakt Box bez zmian.

## 2026-10-26 WWW
PayPal (sandbox): zakup Pro ze strony kontem testowym kupujacego przeszedl (capture po stronie serwera, widok podziekowania). Do zrobienia: przycisk PayPal w aplikacji (WWW-003), klucze live Stripe i PayPal. Kontrakt bez zmian.

## 2026-10-26 WWW
Decyzja wlasciciela: ServMod zostaje na tym samym koncie Stripe co Qubivibe (klienci widza nazwe Qubivibe). PayPal osobno (WWW-003 dla APP).

## 2026-10-26 (APP): PayPal w aplikacji - 0.76.3 (WWW-003)
- Settings > Subscription: przy wejsciu GET /api/shop/config (stripe/paypal; blad = tylko karta). Gdy dostepne obie metody - wybor "Pay by card" / "PayPal" (domyslnie karta); checkout dostaje pole provider. Reszta przeplywu bez zmian. Nieprzetestowane na telefonie ani w sandboxie PayPal (tylko build).

## 2026-10-26 WWW
Stripe: utworzono webhook LIVE "servmod-site" (konto live Qubivibe) -> https://servmod.com/api/pay/stripe. Czekamy na klucze live od wlasciciela (install_payment_keys.cmd) i na PayPal live (wymaga konta Business). Blad PayPal sandbox z telefonu: odpowiedz dla APP w inbox/APP.md.

## 2026-10-26 WWW
PayPal LIVE: klucze live zainstalowane na serwerze (konto firmowe grabowski79, aplikacja ServMod); serwer tworzy zamowienia na prawdziwym PayPal. Stripe nadal na kluczach testowych do czasu wpisania sk_live i whsec z webhooka live (utworzony). Skrypt install_payment_keys zachowuje teraz linie PAYPAL_.

## 2026-10-26 WWW
Stripe LIVE wlaczony (klucz restricted rk_live z uprawnieniem Checkout Sessions Write + webhook live), PayPal LIVE wlaczony. Sklep przyjmuje prawdziwe platnosci po £40 / £20. Dodano tools\set_prices.cmd do zmiany cen bez ponownego wpisywania kluczy. Test live na £1 zaplanowany.

## 2026-10-26 WWW
Przygotowanie startu: Refunds/Licence/Privacy/Terms bez banera Draft (na polecenie wlasciciela, bez porady prawnej), zgoda na natychmiastowa dostawe w checkout Stripe i pod przyciskami na stronie; WWW-004 dla APP (zgoda w aplikacji). Do ustawienia przez wlasciciela: ceny 4000/2000 (set_prices.cmd), unlock APK, mail do listy oczekujacych.

## 2026-10-26 WWW: grafiki i strona Requests
- Strona: hero z prawdziwymi zrzutami aplikacji (tla z ComfyUI), galeria "In the app", sekcja "Cables and adapters" w Connection guides (zdjecia wlasne, wlasciciel).
- Nowa strona /requests.html z formularzem zgloszen urzadzen/protokolow/funkcji; endpoint webowy POST /api/requests (nie dla aplikacji, KONTRAKT bez zmian). Podglad zgloszen w panelu admina.
- Brak zdjecia adaptera USB-RS485 (do zrobienia przez wlasciciela). Pobieranie APK nadal zablokowane do "unlock".

## 2026-10-26 WWW: odblokowanie pobierania (decyzja uzytkownika: "unlock dowland")
- Strona: /download.html + przyciski Download w menu, hero i na stronie glownej. Do publikacji: ServMod-0.76.3-clean.apk (versionCode 198, com.servmod.app, nie debug, podpis kluczem wydaniowym).
- Publikacje wykonuje uzytkownik na PC: web\install_backend\publish_release.cmd (dry run, potem wpisuje PUBLISH). Do tego czasu feed /servmod/version.json = 404, strona pobierania pokazuje fallback.
- Mail do listy oczekujacych tylko z panelu admina i tylko po zgodzie. APP-014 zostaje OTWARTE do publikacji feedu.

### 2026-10-26 WWW: licznik odwiedzin
- Dodano wlasny licznik bez cookies (POST /api/hit, tabela hits, hash IP+przegladarki zmienny co dzien, IP nie jest zapisywany) i sekcje Visits w panelu admina. Polityka prywatnosci zaktualizowana. Zmiany w kontrakcie: nie.

## 2026-10-26 (APP): aktualizacje aplikacji dla wszystkich (opcja 3)
- Decyzja uzytkownika: na razie aktualizacje aplikacji (nowe wersje, poprawki) dostaja WSZYSTKIE telefony, bez sprawdzania licencji/subskrypcji (tak jest w kodzie: update\ nie czyta licencji, feed bez Device ID). Subskrypcja zostaje za przyszla platna zawartosc (nowe moduly/marki, bazy i profile) - egzekwowanie dopiero gdy taka zawartosc powstanie (wtedy bramka tylko na tych modulach). Blokady pobierania nowych wersji nie robimy.

## 2026-10-28 (APP): automatyczny tag NFC dla backupu - 0.77.0
- Na zyczenie uzytkownika (mniej klikania): po zapisie backupu (checkbox "Write an NFC tag after saving" lub przycisk Tag) telefon prosi o przylozenie tagu; AutoNfcDialog zapisuje URI servmod://t/<id>?m=<modul>&f=<plik> (gdy plik sie nie miesci na NTAG213: tylko ?m=), dodaje link domyslny do backupu i zamyka okno. Tag z kodem ServMod zachowuje id i dostaje nowy cel. Skan: otwiera ten backup; telefon bez wpisu w tags.json uzywa podpowiedzi z tagu; brak pliku = ramka "This backup is not on this phone". Kody kreskowe i reczne przypisanie pod "Barcode / other". Format URI zgodny wstecz (id = segment sciezki). Interfejs Box bez zmian. Nieprzetestowane na sprzecie.

## 2026-10-28 (APP): awaria po otwarciu tagiem NFC i polaczeniu z falownikiem - 0.77.1
- Zgloszenie uzytkownika (0.77.0): "ServMod keeps stopping" po otwarciu aplikacji tagiem NFC i probie polaczenia z falownikiem. Brak logu, przyczyna nieznana. 0.77.1 dodaje CrashLog (UncaughtExceptionHandler zapisuje stos do filesDir/last_crash.txt) oraz karte Last crash report w Settings > Support (Copy / Clear). Do zrobienia: uzytkownik odtwarza awarie, kopiuje raport; potem poprawka.
- (uzupelnienie 2026-10-28) Uzytkownik: awaria NIE zalezy od NFC; wystepuje przy laczeniu Boxa przez Wi-Fi na BLE (przelaczanie transportu). Na 0.77.1 jeszcze sie nie powtorzyla; test na drugim telefonie. Czekamy na Last crash report. Trop: BoxHub / BoxTransport (BLE connectGatt, skan, przelaczenie Wi-Fi<->BLE).

## 2026-10-28 (APP): poprawka awarii Lenze + Box Wi-Fi - 0.77.2
- Raport awarii (0.77.1): NetworkOnMainThreadException: LzCtl.watch (LaunchedEffect na watku glownym) -> LenzeSdo.read -> BoxCanPort.canTx -> BoxLink.send -> TcpBoxTransport.write. Poprawka: odczyt SDO w watchdogu w withContext(Dispatchers.IO). BLE nie rzucal wyjatku, ale tez blokowal UI. Pozostale sciezki Lenze (open, scanAll, live, ctl) juz w IO. Nieprzetestowane na telefonie.

## 2026-10-28 (APP): nawigacja Backup - 0.77.3
- Karta polaczenia: jeden maly zwiniety kafelek "Help - how to connect" (Show / Full screen), po rozwinieciu sekcje Phone (USB, no Box) i ServMod Box + rysunek. Backup otwarty z tagu NFC: BackupTags.tagMode chowa Help, Create backup, naglowek i opis Saved backups; widoczne tylko zielona/bursztynowa ramka i karta backupu (rozwinieta, Compare & write / Compare only). Dismiss przywraca pelny widok. Nieprzetestowane na telefonie.

## 2026-10-29 (APP): BOX-018 i WWW-004 - 0.77.4
- BOX-018: NetworkModule - hostPortError() (pusty/zly host, port poza 1-65535) przed TCP PING (Box), TCP PING, ICMP PING, Modbus TCP READ; walidacja bazy SCAN subnet; CoroutineExceptionHandler przy zadaniach przyciskow (blad = tekst zamiast zamkniecia aplikacji). WWW-004: tekst zgody + przyciski Terms / Refunds policy pod przyciskami zakupu w Settings > Subscription (widoczne gdy jest co kupic). Nieprzetestowane na telefonie.

## 2026-10-30 (APP): Lenze Parameters - wartosci Display - 0.77.5
- Przyczyna: odczyt po polaczeniu (scanAll) czyta tylko kody zapisywalne, kody Display pokazywaly "-" do otwarcia kodu; chip "Read (N)" to filtr, przycisk "Read all" na koncu rzedu chipow. Poprawka: po zwyklym odczycie (nie przy backupie) jeden Box job czyta tez kody Display do osobnej mapy dvals (nie trafia do backupu ani Compare, czyszczona z cache); kody nieistniejace dodawane do absent. Wartosci to migawka. Nieprzetestowane na telefonie.

## 2026-10-30 (APP): 0.77.6 - ulubione, historia, live, seria Hitachi
- Display nie jest juz czytany pelnym odczytem (za wolno): wiersze widoczne na ekranie odswiezane co 1,5 s (kody bez podkodow, pauza gdy dialog/busy); odczyt po polaczeniu jak dawniej (tylko Settings). Ulubione (prefs lzFav) i historia zapisow (prefs lzHist, 100 pozycji, Undo zapisuje stara wartosc) tylko w Lenze; inne marki w kolejnych wersjach. Hitachi: backup zapisuje seria (rejestr 0x1086) jako dodatkowa para; Compare ostrzega i blokuje zapis gdy seria pliku i falownika sie roznia (stare backupy bez serii: tylko ostrzezenie o mocy H003). Nieprzetestowane, niezbudowane.

## 2026-10-30 (APP): 0.78.0 - ulubione/historia/live/No motor we wszystkich markach
- Nowy plik ParamTools.kt: FavSet (prefs servmod_favs), ChangeLog (prefs servmod_hist, 100 pozycji, Undo = ponowny zapis starej wartosci przez writeOne), LiveRows (odswiezanie widocznych wierszy co 1,5 s, pauza przy dialogu/busy/historii), isMotorParam (id H0xx lub nazwa z regexem motor/rated/poles/resistance/...). Podpiete do Hitachi (Vm/Ui), Mx2 (w tym profile JSON, Mitsubishi), Pf525, Danfoss; Lenze ma wlasna wersje. Compare: przycisk "No motor"; CompareState Hitachi odznacza parametry silnika automatycznie przy innej mocy/serii. Zakres pominiety: raporty (na zyczenie uzytkownika). Nieprzetestowane i niezbudowane: menu Build w Android Studio zaslania czarny prostokat (screen zablokowany dla computer use).

## 2026-10-30 (APP): build 0.78.0
- Build release OK (wersja 206, 22 206 942 B). Pierwsza proba nie przeszla: w DfSession pole hist kolidowalo z istniejacym hist (log alarmow); zmienione na chlog (tylko Danfoss). Na stronie /update nie wydano: czekam na test uzytkownika (release.py w ServMod\web\tools, upload przez SSH). Wczesniej Studio mialo otwarty inny projekt (RadioControl) i zablokowany ekran PC; wariant trzeba bylo przelaczyc z debug na release w Build Variants.


## 2026-10-30 (APP): 0.79.0 - modul B&R System 2003 (CAN) w sekcji PLC
- Uzytkownik ma stol z B&R System 2003: kontroler CAN 7EX470.50-1 (rev. M0), adapter AF101 oraz moduly DI135 (licznik/enkoder) i AO352 (2 wyjscia analogowe). Z manuala (MASYS2-2003-E V4.0): CAN DB9 pin 7 H, pin 2 L, pin 3 GND; przelaczniki N# daja predkosc i wezel (SW1=0, SW0~4 = wezel 4, 250 kbit/s); siec klasy 0 bez mastera, stale ID, Identify_Node 2022 co 1 s.
- Aplikacja 0.79.0: nowy pakiet br (BrProto, BrSession, BrRoot), wejscie z ekranu PLC (przycisk B&R SYSTEM 2003). Funkcje: Live (dekodowanie ID i danych), Node (odczyt statusu, modulow, dekoder przelacznikow), I/O (obiekt DI135/AO352, test wyjscia analogowego, tylko Pro + UNLOCK), Commands (tylko polecenia odczytu: 0,1,2,3,10,16), Trace (kopiuj do schowka). Zapis tylko wyjscie analogowe, cyklicznie co 200 ms. Interfejs Box<->aplikacja bez zmian (T_CAN_TX, T_CAN_FRAME, SET_CFG ch1 tryb aktywny).
- Zlecone BOX: APP-015 (biala lista polecen B&R przy WRITE_LOCK 1, potwierdzenie 20/125/250/500 kbit/s, opcjonalnie filtr i koalescencja RX). Nieprzetestowane na sprzecie.

## 2026-10-30 (APP): build 0.79.0
- Build release OK za pierwszym razem (versionCode 207, 22 256 094 B, md5 226135dc34df45a630c85e6fe43e7748), releases\ServMod-0.79.0-clean.apk; w dex sa teksty modulu B&R. Na stronie /update nie wydano (czekamy na test uzytkownika 0.78.0 i 0.79.0; release.py przy wydaniu: sprawdzic wersje na kanale, 0.76.3 = kod 198).

## 2026-10-30 (APP): ESP32-S3 Super Mini - CAN sprawny
- Uzytkownik: Box na ESP32-S3 Super Mini ma wymieniony modul CAN (nowy, zamiast wadliwego WCMCU-230) i CAN dziala, sprawdzone na Lenze 8400. Wersja mini moze wiec byc uzyta do testu B&R System 2003 (APP-015 niewymagane do testu). Dla BOX: zaktualizowac wpis o minie (CAN zweryfikowany, nowy modul), podac typ modulu.

## 2026-10-30 (APP): build 0.79.1 - uproszczony modul B&R
- Na prosbe uzytkownika: CONNECT robi wszystko sam (predkosc listen-only, wybudzenie wezla i numer, odczyt modulow), rack z podswietleniem modulow (rack uzytkownika: EX470 node 5 250 kbit/s, AF101 z AO352 i 2x DI135, 2x DM465), wejscia zielone LED, wyjscia przelaczniki, AO352 suwaki, jedno ENABLE OUTPUTS. Zapis tylko obiekty wyjsc (ID 414-541, 1054-1565), polecenia tylko odczytu. versionCode 208, 22 272 478 B, md5 c6831b75b677eb373179bad431f60b23, releases\ServMod-0.79.1-clean.apk. Nie wydano na strone. NIEPRZETESTOWANE na sprzecie (nieznane: tryb packed/unpacked, skala AO352, wyjscia DM465).

## 2026-10-30 (APP): build 0.79.2 - Monitor (pasywny) + Advanced
- Log ze stolu: wezel 5 pracuje w trybie packed (DI 8 B na ID 302), alarm 226 = 5000/4221 (flaga bledu wyjscia cyfrowego, modul 2 kanal 1) = brak zasilania wyjsc DM465 (zasilanie X2 zacisk 2); po podlaczeniu 24 V wyjscia dzialaja bez mrugania (uzytkownik).
- Na prosbe uzytkownika: dwa tryby GUI. MONITOR & DIAGNOSTICS: Box wylacznie w trybie listen-only, aplikacja nic nie wysyla (BrSession.passive blokuje TX), dekoduje ramki wezlow i mastera; ADVANCED: dotychczasowy ekran stolowy. Pelna tabela modulow (BrProto.ANA, alarmText). Jesli maszyna ma master NMT z innymi ID (siec klasy 2), dekodowanie stalych ID moze nie dzialac (widac tylko trace). versionCode 209.

## 2026-10-30 (APP): build 0.79.3 - Monitor + module scan
- Uzytkownik: na maszynie na razie nie testujemy (terminator 120 ohm wlutowany na plytce CAN Boxa; do wylutowania/jumper przed uzyciem na pracujacej sieci), na stole Monitor pasywny bez mastera widzi tylko ID. Dodano tryb 3 MONITOR + MODULE SCAN (BrBench readOnly): ten sam ekran co Advanced, wyjscia i suwaki zablokowane (BrCtl.readOnly), pokazuje wyjscia zadawane przez mastera; Monitor pasywny: domyslnie wszystkie adresy, adapter/slot z ID, DI135 po dlugosci ramki 6 B. versionCode 210.

## 2026-10-31 (APP): build 0.80.0 - SMARTSTEP A: polaczenie z napedem (CN3)
- Nagrania USB (CX-Drive, USBPcap, FTDI) + plik Drive1.sdd rozkodowaly protokol: 9600 bit/s, 7 bitow, parzystosc EVEN, 1 stop; ramka ASCII 'W' + 5 bajtow hex (b0: 00 odczyt / 01 zapis, odpowiedz 00 wartosc / 01 przyjeto / 05 odrzucono; adres 16 bit = numer Pn w hex; dane 16 bit) + suma kontrolna (dopelnienie sumy do 256) + CR. Parametry cyfrowe: jedna cyfra hex na cyfre Pn (Pn001 1002 -> 0x1002).
- Dodano SsaDrive.kt (SsaLink, SsaDriveCtl, zakladka Drive): Connect (adapter USB-RS232, OTG), odczyt wszystkich 22 Pn do zestawu roboczego, zapis tylko roznic z kopia 'before-write' i odczytem zwrotnym, Compare. Bez monitora Un (adresy 0x85xx/0x87xx nie rozpoznane) i bez historii alarmow. versionCode 211, 22 321 630 B, md5 dbbc57de154b183b8ab3bf4de9d55e8e, releases\ServMod-0.80.0-clean.apk. Nie wydano na strone. NIEPRZETESTOWANE na napedzie: nieznane czy zapis zostaje po wylaczeniu zasilania (komenda 0x5005 z konca transferu CX-Drive nie jest wysylana), znaczenie zapisu 0x2002=0 przy laczeniu (pomijany).

## 2026-10-31 (APP): build 0.80.1 - SMARTSTEP A w ukladzie wspolnym
- Uzytkownik przypomnial zasade: wszystkie modele falownikow maja to samo GUI i uklad. 0.80.0 mialo osobna zakladke Drive i offline working set - odrzucone. Przebudowa: SsaRoot.kt wg Pf525Root (Backup, Parameters, Control, Settings, Faults; przycisk Connect/Disconnect u gory; backup czyta wszystkie Pn z napedu; Compare & write / Compare only; ulubione, historia z Undo, LiveRows). Nowe pliki SsaLink.kt (protokol) i SsaSession.kt (stan); SsaDrive.kt przeniesiony do ServMod\handoff\_to_delete. Stare zestawy .csv ([omronservo]) nadal sie wczytuja. Control: komunikat, ze sterowanie reczne/monitor Un niedostepne. versionCode 212, 22 321 630 B, md5 3e2da04f5b581a64fc94efd6a9f73e15, releases\ServMod-0.80.1-clean.apk. Nie wydano na strone. NIEPRZETESTOWANE na napedzie (zapis, trwalosc po wylaczeniu zasilania, cyfry Pn000.0).

## 2026-10-31 (APP): build 0.80.2 - SMARTSTEP: Control, reset fabryczny, Box
- Z nagran CX-Drive (Monitor, Test Run, Initialize): 0x2000 = 0x1000 + numer Fn wybiera funkcje (Test Run 0x1002, Initialize 0x1005), 0x2001 = polecenie (4 servo ON, 2/3 jog z powtarzaniem co ok. 0,5 s, 0 stop/servo OFF, 1 wykonaj), 0x1304 = predkosc jog; nowy typ ramki b0 = 02 (odczyt blokowy, bufory Data Trace). Napęd w alarmie przyjmowal komendy (odp. 01) mimo "Failed to start the motor / Remote mode" w CX-Drive.
- Aplikacja: zakladka Control (Pro), Restore factory defaults z automatycznym backupem, Settings > Connection: telefon USB albo ServMod Box (ch2, SET_CFG 9600 7E1 BRIDGE, T_SER_XCHG framing 2 = 14 B). Interfejs Box<->aplikacja bez zmian (kontrakt 1.5 wystarcza, firmware obsluguje 7 bitow). versionCode 213, 22 338 014 B, md5 57684c1797d4c23e8a18e0da7f5d1fa3. Nie wydano na strone. NIEPRZETESTOWANE.

## 2026-10-31 (APP): build 0.80.3 - SMARTSTEP: automatyczny wybor Box / USB
- Zasada wspolna: polaczenie Auto / USB adapter / ServMod Box jak w MX2 i Danfoss (Auto = Box gdy juz polaczony albo brak adaptera w telefonie). Reset bledow i monitor Un nie dodane: manual I533 zna tylko wejscie RESET (CN1-18), a w nagraniach nie ma resetu alarmu ani zmieniajacych sie wartosci Un; uzytkownik ma dostarczyc nagrania. versionCode 214, md5 5a078a8a41c9aea102a56b62ae1eaea8. Nie wydano na strone. NIEPRZETESTOWANE.

## 2026-10-31 (APP): build 0.80.4 - kolejnosc na liscie i QR etykiety testowej
- Zyczenie uzytkownika: SMARTSTEP A na liscie falownikow zaraz po Omron MX2; QR na etykiecie testowej PM45 ma prowadzic do pobrania wersji free ze strony ServMod. Zrobione: QR = https://servmod.com/download.html (wersja 3, ECC M, 4 punkty na modul, 130x130, ten sam rozmiar i polozenie co poprzedni; zdekodowany zxing-cpp). versionCode 215, md5 ceafbfef68bb345c905cc413ebfca7b7. Nie wydano na strone. Wydruk etykiety nieprzetestowany.

## 2026-10-31 (APP): build 0.81.0 - B&R "Add machine"
- Zyczenie uzytkownika: automat z PDF odpada; w apce miejsce na dodanie maszyny (plik JSON z opisami), plik dla EasyFry przygotowany z PDF. Zrobione: format "servmod-machine" v1 (name, node, modules: DM465 inputs/outputs 1-16 wg kolejnosci w racku; AT352/AO352 channels wg slotu AF101 i typu), import przez systemowy wybor pliku do filesDir/br-machines, panel MACHINE w BrChoice, nazwy w BrSimple (bench + monitor z skanem). Pasywny Monitor bez nazw (nie zna typow modulow). Plik: ServMod\handoff\easyfry.json (3x DM465 103N1/104N1/105N1, AT352 101N1, 2x AO352 101N5/101N7, wezel 5). Brak zmian KONTRAKT. Nieprzetestowane.

## 2026-10-31 (APP): build 0.81.1 - pliki maszyn PLC w osobnym folderze
- Zyczenie uzytkownika: pliki maszyn (json) maja miec osobny folder w backupach, zeby dalo sie je dodac w nowej apce albo wyslac na inny telefon. Zrobione: folder machines-plc w getExternalFilesDir (wchodzi do kopii aplikacji AppBackup, ktora bierze caly folder zewnetrzny), ShareProvider zna folder, SHARE przy kazdej maszynie, migracja plikow z 0.81.0 (filesDir/br-machines). Dodanie w nowej apce: ADD MACHINE. Odbior pliku wyslanego z innego telefonu przez "Share to ServMod" nie jest dodany (filtr manifestu tylko PDF) - dodajemy z pliku. Nieprzetestowane.

## 2026-10-31 (APP): build 0.82.0 - pliki maszyn w module PLC, ekran sygnalow, emulator
- Zyczenie uzytkownika: pliki maszyn maja trafiac do Add machine w PLC; wybor maszyny od razu pokazuje ekran sygnalow in/out z JSON i nasluchuje wg protokolu zaleznego od producenta/modelu PLC; prosty czytelny GUI diagnostyczny; emulator jako przyklad. Zrobione: format servmod-machine v2 (v1 nadal czytany), folder machines-plc, PlcMachineFile.kt (model, import, share, emulator), PlcLive.kt (ekran). Protokoly: demo (emulator, wbudowany plik demo-packaging-line.json = szablon), br2003 (pasywny nasluch przez Box, nazwy z modules, adresy logiczne DM465 z pola address albo kolejnosc: AF101=1, DM465 po 2), fins i logix (odczyt jak dotad, tylko czytanie). Brak zmian KONTRAKT. Nieprzetestowane na sprzecie (EasyFry: zalozona kolejnosc racka wg rysunku).

## 2026-10-31 (APP): build 0.83.0 - Machines jako osobny kafelek, B&R czysty
- Zyczenie uzytkownika: kafelek B&R / PLC = czysty program obslugi typu PLC z fabrycznymi opisami modulow i wyjsc; maszyna to osobny kafelek na zewnatrz menu B&R: polaczenie PLC danego producenta z opisami z PDF (JSON). Zrobione: nowy modul "machines" (MachinesRoot.kt) z lista plikow, ADD MACHINE FILE, ekranem sygnalow (PlcLive) i emulatorem; z PlcRoot usunieto liste plikow, z BrRoot/BrMonitor usunieto nazwy z JSON (przywrocone wersje sprzed 0.81.0), BrMachine.kt przeniesiony do handoff\_to_delete. Format v2 bez zmian, easyfry.json bez zmian. Nieprzetestowane na sprzecie.

## 2026-10-31 (APP): build 0.84.0 - SMARTSTEP alarmy
- Nagranie alarm_reset_and_alarm_trace_reset (CX-Drive, 892 ramek, sumy OK): reset alarmu = zapis 0x2000=0x2001 potem 0x2001=1 (2x); kasowanie historii alarmow = Fn006: 0x2000=0x1006, 0x2001=1 (2x), po nim 0x8500..0x8509 = 0x0099 (brak); historia przed kasowaniem: C2,10,C2,10,C2,10,C2,10,C2,99; 0x850A = C2 caly czas (aktualny alarm, zalozone). Alarm A.C2 (Phase error) kasuje sie tylko wylaczeniem zasilania, wiec po resecie wraca (potwierdza ponowny wpis C2 w historii). Kolejnosc historii (najnowszy pierwszy) i rola 0x850A zalozone. Monitor Un (Real-Time Trace) odlozony na zyczenie uzytkownika (brak silnika). Nieprzetestowane z kasowalnym alarmem.

## 2026-11-01 (APP): build 0.85.0 - jedna lista maszyn
- Zyczenie uzytkownika: nie powtarzac funkcji; w pliku JSON ma byc od razu wszystko o maszynie (PLC, protokol, adresy, oznaczenia), dodanie JSON z backupu = nowa maszyna; nowe marki PLC beda dochodzic (B&R pierwszy przetestowany). Zrobione: PLC = warstwa sterownikow (teraz B&R; Omron FINS i Logix uzywane przez maszyny), Machines = jedyna lista maszyn. Reczna maszyna FINS/Logix to ten sam plik JSON v2 (protocol fins|logix, host, node, signals[label,addr,type,scale,unit]); nowy MachineEdit.kt (+ NEW, edycja zapisuje plik na biezaco, EDIT w PlcLive tylko dla fins/logix), MachineFiles: readManual/writeManual/newManual/removeFile, migracja jednorazowa z SharedPreferences servmod_plc (flaga legacy_migrated), parse dopuszcza fins/logix bez sygnalow. Z PlcModule usunieto liste maszyn i MachineScreen. Format v2 bez zmian dla plikow istniejacych. Przy edycji pliku z ekranu EDIT tracone sa grupy i pola sim (dotyczy tylko fins/logix). Kierunek na przyszle marki: jeden sterownik na marke (nasluch/odczyt + lista sygnalow) widoczny jako protokol w pliku i jako przycisk w PLC; przycisk 'Save as machine' z ekranu B&R NIE zrobiony. Nieprzetestowane na sprzecie.

## 2026-11-01 (APP) 0.86.0 Omron Host Link
- Machines: nowy protokol hostlink (Omron, serial przez USB-RS232), tylko odczyt; backup/restore programu dopiero po tescie podgladu na sprzecie. Interfejs Box<->aplikacja bez zmian. Plik pals-line5.json (maszyna Pals Line5, CP1H) w handoff; wyjscia 104.00/104.01 niepewne wg rysunkow.

## 2026-11-01 (APP) 0.87.0 modul Omron w PLC
- Kafelek PLC: nowy sterownik OMRON (Host Link, USB-RS232) obok B&R: CONNECT/INFO/MONITOR/ERRORS/SCAN/RAW, tylko odczyt. Polaczenie Host Link 9600 7E2 jednostka 0 potwierdzone na sprzecie (CJ1M-CPU11). Okablowanie: PLC 2-2, 3-3, 9 do 5 adaptera, zwora 4-5 po stronie PLC (wczesniejsza instrukcja krzyzowania 2-3 byla bledna). Backup/restore programu dopiero po tescie.

## 2026-11-01 (APP) 0.88.0 uniwersalny ekran PLC (test Omron)
- Decyzja uzytkownika: GUI PLC jednolite dla wszystkich marek/modeli (jak falowniki), stack wykrywany od razu jak w B&R; test na Omronie, potem reszta (B&R, Schneider, AB) tym samym ukladem, jesli sie spodoba. Backup/restore programu tam, gdzie mozliwe. Ekran PlcUniversal.kt + interfejs PlcDriver, sterownik OmronDriver.kt. Poprawiono pals-line5.json (protokol hostlink).

- 2026-11-01 APP 0.88.1: PlcUniversalScreen tab bar was one scrolling row, TOOLS (backup/restore) fell off-screen; now two rows of three. Not tested on device.
- 2026-11-01 APP 0.88.2: Omron backup names the failing part; FINS 1104 on the first program block is stored as an empty program. Not tested on device.
- 2026-11-01 APP 0.88.3: PLC backup/restore parts chosen with checkboxes; restore writes only ticked parts. Omron backup verified on bench PLC (empty PLC). Restore not tested.
- 2026-11-01 APP 0.89.0: PLC screen: OPERATING MODE buttons (Omron 0402 / 0401), brand tiles like Inverters, Omron Host Link goes through the ServMod Box ch2 automatically when the phone has no USB host or no adapter. Task APP-016 to BOX (7E2 on ch2). Not tested on device.
- 2026-11-01 APP 0.89.1: removed the draft warning from the PLC tile and the machine-file chips from the PLC screen (machine files stay in Machines only). Omron backup/restore verified by the user on the bench PLC (restore reported verified). Not tested on a production machine.
- 2026-11-01 APP 0.89.2: device-profile field benchNoMotor {reg,value,name}: on "Enable Modbus control" the app sets it (ATV320: OPL reg 9611 = 0, output phase loss off, RAM only) and "Restore control source" puts the old value back. ATV320 bench test: Modbus works after power cycle (ADD=1, 19200 8E1); OPF2 seen without motor. Not tested on a motor.
- 2026-11-01 APP 0.89.3: benchNoMotor moved from "Enable Modbus control" (not shown when CD1/FR1 already Modbus) to the Forward/Reverse command: OPL set to 0 before run, put back on Stop / disconnect / leaving the screen. Not tested on a motor.

## 2026-11-01 APP 0.89.4
ATV320: keep-alive (lekki odczyt co 2 s gdy polaczono, poza ekranem Control), zeby falownik nie zglaszal SLF1 (Modbus timeout TTO 10 s). Niesprawdzone na sprzecie.

## 2026-11-01 APP 0.89.5
Odczyt parametrow dla falownikow z profilem JSON (ATV320): bloki do 100 rejestrow ze scalaniem przerw <=10 (282 -> ok. 100 zapytan); odmowa falownika -> powrot do dokladnych blokow. Niesprawdzone na sprzecie.

## 2026-11-01 ATV320 zamkniety
Uzytkownik potwierdzil: ATV320 dziala w calosci na sprzecie (polaczenie, odczyt, sterowanie, reset bledow). Wpisane do servmod-hardware-verified.md. Zdjecie modelu do dodania (assets\wiring\atv320_photo.png).

## 2026-11-01 Omron przez Box
Uzytkownik potwierdzil: Omron CJ1M (Host Link) dziala przez ServMod Box (kanal 2, 7E2). APP-016 mozna uznac za potwierdzone na sprzecie; BOX nie musi nic zmieniac.

## 2026-11-01 do zrobienia
Omron CJ1: test na PLC z programem + modul motion (NC413/MCH) - zapisane w backlogu (N2), wracamy gdy sprzet bedzie pod reka.

## 2026-11-01 APP 0.89.6
NFC: link typu Tool ma teraz cele bezposrednie: marka falownika, B&R / Omron w PLC, konkretny plik maszyny (Machines). Tag: target module, module = podcel, ref = id modulu. Niesprawdzone na sprzecie (zbudowane, nieuruchomione).

## 2026-11-01 APP 0.90.0
Uniwersalny ekran PLC: widok RACK (STACK > RACK/LIST): moduly obok siebie jak na szynie DIN, diody w ukladzie fizycznym (bez zaciskow). Omron CJ1: uklad budowany przez uzytkownika z katalogu CJ1W-ID/OD/MD/OC (CPU nie ma tablicy I/O), adresy CIO od 0 wg kolejnosci montazu. Niesprawdzone na sprzecie. Nastepnie B&R na tym samym widoku.

## 2026-11-01 APP 0.90.1
PLC: kafelek RACK PREVIEW (symulacja bez PLC) do ogladania widoku racka. Odkrycie: automatyczne budowanie racka Omron wymaga odczytu zarejestrowanej tablicy I/O (0201 8010); CJ1 na biurku jej nie ma, a format nie jest potwierdzony - potrzebna probka z PLC z tablica I/O. Pomysl: przycisk CREATE I/O TABLE (FINS 0220, tryb PROGRAM) na pustym CJ1 -> probka do dekodowania. Czeka na zgode uzytkownika.

## 2026-11-01 APP 0.90.2
Pole Search backups nad listami zapisanych backupow: falowniki (Hitachi, PowerFlex, Danfoss, Lenze, Omron servo, Mx2 i profile JSON, termoregulatory) i PLC. Szukanie po slowach w nazwie pliku, kolejnosc dowolna. Niesprawdzone na telefonie. Nastepnie B&R na uniwersalny ekran.

## 2026-11-01 APP 0.91.0
B&R System 2003 przerobiony na uniwersalny ekran PLC (BrDriver). Rack budowany automatycznie ze skanu modulow (BrCtl.scanRack): karty DI/DO/DM z LED w kolejnosci adresow, adaptery AF101 z wartosciami analogowych slotow, wyjscia sterowane dotknieciem bursztynowej LED dopiero po ENABLE OUTPUTS (Pro, potwierdzenie, UNLOCK Boxa) w TOOLS. RackView uogolniony (RackUnit: bity w obszarze IN/OUT/CIO) i obsluguje tryb auto (bez edycji) i reczny (Omron). Pasywny MONITOR (zero TX) zostaje jako osobny kafelek "B&R MONITOR (LISTEN ONLY)", bo bez nadawania nie da sie zeskanowac modulow. NIEPRZETESTOWANE na sprzecie. Do zdecydowania przez uzytkownika: przycisk CREATE I/O TABLE dla Omron (probka do auto-racka).

## 2026-11-01 APP 0.91.1
Zakladka Backup falownikow: zamiast jednej dlugiej karty (pod klawiatura nic nie bylo widac) trzy kafelki otwierajace osobne strony: Connect & help, Create backup, Restore (pole Search u gory + lista). Ten sam uklad we wszystkich markach (wspolny BackupMenu w tags\BackupPages.kt). Niesprawdzone na telefonie. PLC odlozone.

## 2026-11-01 APP 0.91.2
Strona Restore: wyjasnienie pod ikonka i (nie zaslania listy), Search pod naglowkiem. Raport PDF z backupu (przycisk PDF obok Share): data, opis, lista parametrow, opcjonalnie porownanie z wybranym innym backupem (roznice podswietlone+podkreslone, sekcja CHANGES). Dziala dla backupow CSV; Hitachi USB (.bin) i Lenze do zrobienia. Niesprawdzone na telefonie.

## 2026-11-01 APP 0.91.3
Raporty PDF: okno wyniku z Open / Share / Save as (CreateDocument, mozna wybrac Google Drive), kafelek Reports z lista raportow (Open/Share/Save as/Delete), folder reports w getExternalFilesDir (ShareProvider obsluguje, AppBackup obejmuje). Niesprawdzone na telefonie.

## 2026-11-01 APP backlog
Zapisane do zrobienia: PDF dla pozostalych modeli (Hitachi USB .bin, Lenze) + poprawka przyciskow Open/Share/Save as (Save as lamie sie w pionie). Teraz PLC.

## 2026-11-01 APP: import projektow CX-Programmer w aplikacji (0.92.0)
Uzytkownik zdecydowal: .cxp importowane w aplikacji automatycznie, budowa maszyny + GUI PLC (liczba i rodzaj modulow). Wgrywanie oryginalnego programu do PLC NIE jest realizowane (brak kodu obiektowego w .cxp); backup/restore zostaje na surowych danych. Pole "rack"/"program" w JSON maszyny (opcjonalne, kontrakt BOX bez zmian).

## 2026-11-01 APP: HMI = uniwersalny panel operatora (0.93.0)
Decyzja uzytkownika: bez kopii ekranow NS; panel z opisow pliku maszyny (z programu PLC), zapis dozwolony wlacznie ze START, safety to osobny obwod sprzetowy. Implementacja: tylko zapis Host Link/FINS (0102), Pro + CONTROL. Pole "roles" opcjonalne w JSON maszyny (kontrakt BOX bez zmian).

## 2026-11-02 APP: raport PDF dla Hitachi USB i Lenze, poprawki GUI (0.93.1)
Backupy .bin (Hitachi) i .json (Lenze) konwertowane przy tworzeniu raportu do wspolnego formatu wierszy (BackupPdf.fromHitachi/fromLenze), reszta raportu bez zmian. Bez zmian interfejsu BOX.

2026-11-02 APP: szkielet modulu "Bilwinco Q20" (0.94.0, NIESKOMPILOWANY, NIEPRZETESTOWANY): kafelek Bilwinco, ekrany Connect (Listen 30 s / Handshake 0x40/0x20 przez USB-RS232, 38400 8N1, log do pliku), Backup/Restore jako makiety (protokol ramek nieznany). Zasilanie plyty WM20/WM21 (X21) do potwierdzenia pomiarem na maszynie. Brak zmian interfejsu Box.

2026-11-02 APP: raport PDF (0.94.0): opcja "Factory settings" w oknie porownania (Hitachi USB i RS-485/Mx2, PowerFlex 525, Danfoss, SMARTSTEP; domyslne wartosci z bazy parametrow; parametry bez znanej wartosci fabrycznej pomijane). Lenze 8400 bez wartosci fabrycznych w bazie - brak opcji. Skompilowane (release), NIEPRZETESTOWANE na telefonie.

2026-11-02 APP: 0.94.1: PDF z Factory settings oznacza zgodne z fabrycznymi na zielono ("= factory", szary "-" = brak wartosci fabrycznej) + podsumowanie. Wartosci fabryczne z manuali (agenci, bez testu na sprzecie) dopisane do baz: Lenze 8400 (2595, assets/lenze/l8400_defaults.json, opcja Factory w PDF), E5CN 151, ATV320 +40, ABB ACS355 +67, Inovance +2, Yaskawa +8, VLT 2800 +21; wartosci zalezne od modelu/mocy/trybu pominiete celowo. Brak manuali: Omron MX2, PowerFlex 525, Delta MS300, Mitsubishi FR-D700, Siemens V20, FC 280. Kopie baz: handoff\defaults\assets_bak, wyniki agentow: handoff\defaults\*.json.
- 2026-11-02: nowe manuale (Manuals.zip od uzytkownika): PF520/525, Delta MS300, Omron MX2 V2, SMARTSTEP A, V20, FC280, B&R EX470/MASYS2003, GA500 full, PM45, Eurotherm 3216, WJ200/WJ-C1, ATV320 komunikacja

2026-11-02 APP: 0.94.2: wartosci fabryczne z nowych manuali dopisane do baz: Omron MX2 +448 (manual V2 I666, wersja normal; zalezne od mocy/klasy napiecia pominiete), Delta MS300 +5, Danfoss FC 280 +1; PowerFlex 525 i Siemens V20 bez zmian (ustawienia mialy juz wartosci). SMARTSTEP A: 22 parametry Pn zgodne z manualem I533 (ServMod\handoff\defaults\smartstep_check.md). Wartosci z manuali, NIEPRZETESTOWANE na falownikach. Do sprawdzenia w bazach: Delta 06-03/06-04 (zakres 0-150 vs 180 w trybie heavy), brak 02-02..02-08, Yaskawa H1-xx (hex vs dziesietne), E1-04.. (dec).

## 2026-11-02 (APP) - Nowe schematy "How to connect": osobny schemat na każdą metodę
- Stare schematy (assets\wiring\*.png) pokazywały Box połączony z telefonem kablem USB: BŁĘDNE. Box łączy się z telefonem bezprzewodowo (BLE / Wi-Fi). Drugi sposób to adaptery przy telefonie: USB-RS485, USB-RS232 (COM), USB-CAN (wkrótce).
- Decyzja użytkownika: osobny schemat dla każdej metody (Box oddzielnie, adapter oddzielnie, USB direct oddzielnie), z dokładnymi oznaczeniami terminali, wycinkiem z manuala i własnym zdjęciem tam, gdzie jest. Schemat ogólny (3 elementy) zostaje na stronę WWW i do About.
- Metody: WL200 = USB direct (mini-B), Box USB host (mini-B), adapter RS-485 (SP/SN), Box RS-485. RJ45 na klawiaturze WL200 i WJ C1 to tylko złącze zdalnego panelu, NIE komunikacja (manual C1). WJ C1: USB micro-B (przez Box działa, direct z telefonu nie), RS-485 SP/SN, terminator 120 ohm przełącznikiem na płycie, masa = L. WJ200 ma USB Mini-B. Danfoss FC280: USB-B direct, adapter, Box (68 P / 69 N). VLT2800: tylko RS-485. Lenze 8400: Box CAN (X1 CH/CL/CG), adapter USB-CAN wkrótce.
- Stan: PNG PROTO w ServMod\handoff\wiring_work\ (generatory make_*.py + wiringlib.py, wycinki z manuali w crops\ z INDEX.txt). Wygląda dobrze wg użytkownika (17:41), użytkownik przejrzy wszystkie i napisze poprawki. Brak: ABB ACS355 (brak manuala FMBA-01), Omron CJ1M (brak PDF), OP17 (czeka na zdjęcia DB9 od użytkownika). Nic z tego nie jest jeszcze w aplikacji; nie sprawdzone na sprzęcie poza tym, co oznaczono na schematach.

2026-11-02 (APP) - Wdrozenie schematow How to connect (0.95.0): uzytkownik zatwierdzil schematy ("sa w porzadku"). Wiring.kt przepisany: katalog metod per model (WIRING), dwie grupy przyciskow (Without Box / With ServMod Box), jeden obraz na metode, wybor modelu (Hitachi, Danfoss). Stare obrazy PNG przeniesione do handoff\wiring_work\_old_assets. Uzytkownik potwierdzil: Box NIE ma wbudowanego RS-232; RS-232 (Omron CJ1M, SMARTSTEP) = adapter USB-RS232 (FTDI) w USB host Boxa; natywny COM mozliwy w przyszlosci. Interfejs Box-aplikacja bez zmian (kontrakt nie ruszany). Do zrobienia: OP17 (zdjecia DB9 od uzytkownika).

2026-11-02 (APP) - 0.95.1: OP17 dostal karte How to connect z dwoma schematami i procedurami WRITE / RECORD. Uzytkownik potwierdzil ("wszystko sie zgadza") pinout panelu IF1A (DB15): pin 3 RXD, pin 4 TXD, pin 15 GND, zwora pin 5-10 (CTS-RTS); adapter DB9: 3 TX, 2 RX, 5 GND. Zrodla: strony internetowe, nie manual Siemensa. RECORD tylko z adapterem telefonu (emulator panelu), WRITE takze przez Box (adapter FTDI w USB host).

2026-11-02 (APP) - Zlecono WWW-APP-017: sekcja "How ServMod connects" w About z dwoma schematami ogolnymi (handoff\www_assets\servmod_connect_with_box.png / _without_box.png). Dodany manual Omron CJ1M W393 (inputs\manuals): potwierdza pinout RS-232C dla CPU CJ-series (str. 167-168: 2 SD, 3 RD, 9 SG, pin 6 = 5 V nie uzywac; w Host Link CPU RS 4 - CS 5 zwarte w wtyczce). Schematy CJ1M w aplikacji (0.95.x) nie pokazuja jeszcze zwory 4-5 ani wtyczki DB9 przy adapterze: do poprawy.

2026-11-02 (APP) - 0.96.0: Access: udostepnianie wpisow (jeden/wszystkie) jako plik .servmodacc (PBKDF2-HMAC-SHA256 100k + AES-256-GCM, fraza ustalana przy eksporcie; klucz Keystore telefonu nie opuszcza telefonu) lub PDF jawnym tekstem z ostrzezeniem; import z dedupem (maszyna+uzytkownik+haslo). Pliki eksportu w access-export, starsze niz 10 min kasowane przy otwarciu modulu. Schematy CJ1M poprawione (W393, zwora 4-5, DB9). Nie zmienia kontraktu Box.

2026-11-02 (APP) - 0.96.1: Access share uproszczony na zyczenie uzytkownika: zadnej frazy. Plik .servmodpw (AES-GCM, klucz wbudowany w aplikacje = tylko ukrycie, nie mocna ochrona; uzytkownik poinformowany), rozpoznawany po naglówku SMPW1; otwarcie z zewnatrz (VIEW content/file + SEND octet-stream) importuje po odblokowaniu Access. NFC: istniejacy link "Tool" w module NFC & Barcode otwiera modul Access (na tagu nie ma hasel).

2026-11-02 (APP) - 0.96.3: Access share: wlasne rozszerzenie/MIME porzucone (Gmail nie pobieral .servmodpw, aplikacje drukarek 3D lapaly plik). Teraz zwykly plik .txt (text/plain) z linia SMPW1:<base64 AES-GCM, klucz w aplikacji>; import przez OPEN FILE, PASTE lub Share > ServMod (SEND text/plain: plik lub tekst). Zadnych filtrow VIEW.

2026-11-02 (APP) - 0.96.6: Access share wraca do rozszerzenia .servmodpw z wlasnym MIME (decyzja uzytkownika: Gmail pobiera ten plik, tylko z chwila opoznienia; filtr VIEW dla wszystkich .txt przechwytywal kazdy plik tekstowy i zostal usuniety). Tresc pliku: tekst SMPW1:<base64 AES-GCM>. Import: dotkniecie pliku / Share > ServMod / OPEN FILE / PASTE.

2026-11-02 (APP) - 0.96.8: Access: przycisk PROG NFC TAG (AccessNfcDialog): tag dostaje kod servmod://t/<id> i link "module" -> access (jak Tool > Access w NFC & Barcode); tag z kodem ServMod zachowuje kod i jest przepisywany. Na tagu nie ma hasel.

2026-11-03 (APP) - 0.96.9: Lenze 8400 factory defaults: tabela z manuala TopLine nie pasuje do StateLine. Po resecie z aplikacji (StateLine C E84AVSCE3712SX0, SW 16.02, C00200 = E84AFGSC) roznilo sie 19 z 1519 porownywanych kodow (1500 zgodnych, 49 bez wartosci fabrycznej). Dodano sekcje "variants" w assets\lenze\l8400_defaults.json (klucz S = StateLine, wariant z 7. znaku C00200) z wartosciami z tego falownika; raport PDF porownuje z nimi dla StateLine. Wartosci to odczyt po resecie, nie manual StateLine (brak manuala StateLine w inputs\manuals). Warianty H/B nie dodane.

2026-11-03 (APP) - 0.97.0: ekran glowny: przycisk czytnika kodow (ikona kodu kreskowego) obok pola Search tools; uzywa istniejacego CameraScanDialog i TagRouter.onScan(kind "barcode"), wiec zachowanie jak w NFC & Barcode.

## 2026-11-03 | APP | Update-feed: kanał beta działa, 0.97.0 opublikowana
- Zgoda użytkownika na publikację nowych wersji (brak użytkowników poza jego telefonami). Opublikowano 0.97.0 (code 265, com.servmod.app) na kanale beta przez tools\publish_beta_0.97.0.cmd (release.py wymaga SSH z komputera użytkownika).
- Telefon z 0.97.0, Updates > Check now: "ServMod is up to date", Last check 09:32 (feed odczytany, nie 404). Test instalacji (pobranie, SHA-256, instalacja) czeka na następny build (0.97.1) opublikowany tym samym skryptem.
- Kanał stabilny i blokada nginx dla /servmod/version.json bez zmian.

2026-11-03 (APP) - 0.97.1: USB Tools > Recover (poprawki po tescie uzytkownika; carving dziala): (1) "Find deleted files" - wynik trafial na dol strony pod zakladka, wiec po skanie "nic sie nie dzialo"; teraz karta "Last result" i lista na gorze zakladki + automatyczne przewiniecie do gory, z licznikami (wpisy usuniete / foldery / puste) i podpowiedzia gdy 0 plikow. (2) Odzyskane pliki zapisywane domyslnie do Downloads/ServMod Recovered/<deleted|carved>-<data-godzina>/ (MediaStore, bez uprawnien), karta "Recovered files on the phone" z Open / Share / Open the folder in Files; "Save selected to another folder..." zostaje. Nie sprawdzone na sprzecie; przyczyna braku listy przy undelete (0 wpisow vs blad odczytu) do potwierdzenia po tescie. Wersja 0.97.1 (code 266).

2026-11-03 (APP) - 0.97.2: pliki backupu otwierane/udostepniane z innych aplikacji (WhatsApp, Gmail, Pliki): nowe appbackup\BackupInbox.kt rozpoznaje plik po zawartosci i kopiuje do folderu backupow wlasciwego falownika: JSON Lenze 8400 (values + ident/node) -> backups-lenze; CSV z pierwsza linia "# ServMod [klucz]" -> backups-<klucz> (Danfoss -> backups-danfoss, PowerFlex -> backups-powerflex, Omron SMARTSTEP, Mitsubishi, Delta, INVT, ABB, Inovance, Yaskawa, Omron MX2, Hitachi RS-485); Hitachi .bin (naglowek 0xAAAB/0xAAAA) -> backups. Dodane filtry VIEW i SEND dla application/json, text/csv, text/comma-separated-values, application/csv (wczesniej tylko octet-stream i PDF/tekst). Nierozpoznany plik jest przekazywany dalej (forwardView). Po imporcie okno "Backup file" z nazwa i miejscem. NIE sprawdzone na telefonie. Przyczyna: WhatsApp otwieral plik .json z typem application/json, a ServMod mial filtry tylko dla octet-stream. Wersja 0.97.2 (code 267, zawiera 0.97.1: Recover). Publikacja beta: tools\publish_beta_0.97.2.cmd.

2026-11-03 (APP) - KOREKTA wpisu "Update-feed: kanal beta dziala": zrzut z telefonu (09:32) pokazuje kanal STABILNY (brak "[test channel]"), a stabilny feed jest zamkniety na serwerze (404 = cicho "up to date"). Wiec "up to date" NIE dowodzilo, ze feed bety dziala. 0.97.2 opublikowano na beta (release.py: published; wczesniej na becie byla tylko wersja code 70, czyli 0.97.0 nigdy nie byla tam publikowana). Test: w Updates stuknac 5x w "Installed" (kanal testowy), Check now; oczekiwany baner 0.97.2 (267). Do potwierdzenia przez uzytkownika.

2026-11-03 (APP) - KOREKTA 2: kanal STABILNY NIE jest zamkniety. WWW opublikowalo feed stable 0.76.3 (code 198) i zrobilo "unlock" 2026-10-26 (inbox\WWW.md, APP-014); lokalny web\nginx\servmod.conf jest nieaktualny wzgledem serwera. Dlatego telefon na kanale stabilnym slusznie pisal "up to date" (stable 198 < zainstalowane 265), a kanal beta (267) widzi 0.97.2. Aplikacja sprawdza sama (przy uruchomieniu co 6 h + WorkManager 24 h + powiadomienie); brakowalo tylko publikacji na stable. Zlecenie uzytkownika: aktualizacja ma dzialac bez klikania 5x. Zrobione: tools\publish_stable_0.97.2.cmd (uruchomic na PC). Po publikacji wylaczyc "Test channel (beta)" na telefonie. UWAGA: strona download.html pokazuje wersje ze stable feedu. Znany drobiazg: przy kanale beta Version history czyta /servmod/beta/history.json (release.py zapisuje tylko /servmod/history.json) - do poprawy w aplikacji, niski priorytet.

2026-11-03 (APP) - 0.97.3: udostepnianie backupu falownika jako KOMPLETNY plik .servmodbk (ZIP, MIME application/x-servmod-backup): meta.json (dir, tagKey, name), backup/<plik>, note.txt, photo.jpg, tags.json (kody barcode/NFC powiazane z backupem). Dotyczy kazdego przycisku Share przy backupach w katalogach backups* (json/csv/bin) - MainActivity.share() buduje paczke (appbackup\BackupBundle.kt, folder backup-export, pliki starsze niz 10 min kasowane). Odbior: BackupInbox rozpoznaje ZIP z meta.json, zapisuje plik do wlasciwego folderu (przy kolizji nazwy dodaje -2), notatke, zdjecie (BackupPhotos) i dodaje linki tagow (TagStore.add target backup, module=tagKey, ref=nazwa pliku). Filtry manifestu: SEND/VIEW dla application/x-servmod-backup + pathPattern *.servmodbk; ShareProvider przeszukuje tez dowolny folder backups* i backup-export. NIE sprawdzone na telefonie (wymaga dwoch telefonow). Zmiana wzgledem 0.97.2: inne telefony ze starszym ServMod nie otworza .servmodbk (trzeba 0.97.3+). Wersja 0.97.3 (code 268). Publikacja: tools\publish_stable_0.97.3.cmd.

## 2026-11-03 APP: 0.97.4
- Update client: Version history czyta history.json (wspolny dla kanalow) i filtruje wpisy po polu channel (domyslnie stable); na beta widac wszystko. Interfejs serwera bez zmian.
- Schematy SMARTSTEP przerobione wg manuala I533 (CN3 8-pin Hirose: 1 /TXD, 2 /RXD, 8 GND; pinow 3 PRMU i 7 +5 V nie laczyc; wtyczka DB9 przy adapterze). Nie sprawdzone na sprzecie.
- Publikacja: tools\publish_stable_0.97.4.cmd uruchamia uzytkownik na swoim PC (SSH).
- Docs: claude/servmod-backlog-addendum-Q.md, servmod-backup-share-inbox.md, handoff odswiezony.

## 2026-11-03 APP: 0.97.5
- USB Tools Recover: lista odzyskanych plikow zwinieta domyslnie, foldery rozwijane osobno, Delete all / Delete this folder (potwierdzenie, kasuje tylko Downloads/ServMod Recovered przez MediaStore). Udostepnianie backupu z barcode/NFC potwierdzone przez uzytkownika na dwoch telefonach.

## 2026-11-03 APP: 0.97.6
- Recover: po kazdym skanie i zapisie okno pop-up (AlertDialog) z wynikiem, bo sama karta Last result na gorze byla niezauwazalna.

## 2026-11-03 APP: 0.97.7
- Schematy Inovance MD500 (RS-485): karta MD38TX1, zaciski 485+ / 485- / CGND, Fd-00 / Fd-02 / F0-02=2 wg manuala; generator handoff\wiring_work\make_inovance.py. Publikacja: jeden skrypt tools\publish_latest.cmd (najnowszy APK + releases\NOTES_latest.txt); z chmury SSH do servmod.com niedostepne.

## 2026-11-03 APP: potwierdzenia uzytkownika
- 0.97.7 opublikowany na stable przez uzytkownika (tools\publish_latest.cmd). Find deleted files (FAT) z pop-upem: uzytkownik potwierdza, ze dziala.

## 2026-11-03 APP: 0.97.8 (BOX-014)
- Lenze 8400: applyDiffs (Restore, Compare & write) uzywa BoxLink.canJobWrite gdy INFO cansdow=1 i >1 wpis o dlugosci 1..4 B; zapis pojedynczy jako zapas tylko przy CanJobSetupException (Box odmowil przed START, np. write lock). Odczyt zwrotny zapisanych wartosci zleceniem odczytu. Kontrakt bez zmian (1.5).

## 2026-11-03 APP: test 0.97.8 na Lenze 8400
- Uzytkownik: Compare & write z backupu zapisal 4 wartosci (0 odmowionych, 0 bledow), Save all parameter sets OK, odczyt zwrotny OK. Roznicy w szybkosci nie widac, bo Restore wysyla tylko roznice (kilka wartosci). Nie wiadomo, czy uzyto zlecenia CANJ czy zapisu pojedynczego (komunikat tego nie mowi).

2026-11-05 (BOX) - Aktualizacje firmware Boxa BEZ OTA przez Wi-Fi (decyzja uzytkownika: za skomplikowane). Wgrywanie plikow .bin loaderem ESP32 Loader w aplikacji (chip ESP32-S3, plik zbiorczy pod 0x0); flash dużego Boxa z telefonu zweryfikowany 2026-11-04 (fw 0.9.1 widoczny w aplikacji). Pliki .bin i schematy dla strony (tylko Pro): ServMod\handoff\www_assets\box_firmware\, zadanie BOX-020 w inbox\WWW.md. Kontrakt Box<->aplikacja bez zmian (1.5).

- 2026-11-05 WWW: KONTRAKT 1.6. Firmware Boxa (.bin) i schematy tylko dla Pro, z serwera servmod.com: GET /api/box/firmware (manifest), /api/box/firmware/<plik>, /api/box/doc/<plik>. Pro sprawdzane na serwerze: ciasteczko sesji konta (strona) albo naglowek X-Licence z kodem aktywacyjnym (aplikacja). Pliki leza poza publicznym katalogiem strony (/var/lib/servmod/box). Box <-> aplikacja bez zmian, brak OTA. Zlecenie dla APP: WWW-005. Strona: servmod.com/modbox.html. Dlaczego: uzytkownik chce, by Pro mogli sami zbudowac Box i pobierac aktualne firmware wprost z aplikacji do wgrania ESP32 Loaderem.

## 2026-11-05 APP 0.97.9: ESP32 Loader DOWNLOAD (WWW-005)
- Przycisk DOWNLOAD obok + ADD pobiera firmware Boxa z servmod.com (X-Licence, tylko Pro, KONTRAKT 1.6), weryfikuje sha256 i bytes, ustawia chip/flash/offset. Build OK, niesprawdzone end-to-end (serwer 404 do publikacji plikow) ani na telefonie.

## 2026-11-05 WWW-005 POTWIERDZONE
- Uzytkownik: caly lancuch w aplikacji dziala (Download Box firmware z servmod.com + FLASH w ESP32 Loader, APP 0.97.9). Zadanie zamkniete.

## 2026-11-05 APP 0.98.0: Bilwinco Q20 (Ghidra)
- Ghidra 12.2 (JDK 25) uruchomiona na PC uzytkownika; dekompilacja Hexf.exe/Hexf32.exe potwierdzila DTR+RTS wlaczone, brak kontroli przeplywu, 38400 8N1. Moduł Bilwinco: BwClient.kt (handshake, R/P/S/X) + Connect, Backup (tylko odczyt, raport sha256), Restore (Pro, tylko AMD flash, kopia przed zapisem, read-back). Wszystko NIEPRZETESTOWANE na plycie. Raport: inputs\bilwinco\analysis\RAPORT_bilwinco.md CZESC C.

## 2026-11-05 Narzedzia do inzynierii wstecznej w ServMod\tools\reverse
- Ghidra 12.2 + Temurin JDK 25 (Windows i Linux) + skrypt DecompAll.java + ghidra_gui.cmd / decompile_headless.cmd/.sh. README.txt w tym folderze. Uzycie tylko dla oprogramowania z legalna licencja, do wlasnej implementacji interoperacyjnej. Przetestowane headless na Linuxie (Hexf32.exe); GUI na Windows i decompile_headless.cmd niesprawdzone.

## 2026-11-05 (APP) - analiza ProDriveNext (32 bity + rozpoznawanie modelu)
Za zgoda uzytkownika (bierze ryzyko licencji); zakres tylko 32 bity i model; nic nie skopiowano do aplikacji.
- Model: ProDriveNext czyta 0x1087 (0x61 WL200 / 0x51 WJ200) i 0x16C8, 0x16F1, 0x14C7 do wersji WJ200. WJ-C1 Extended / SJ-P1 to osobny PID 0x00CF z rejestrem 0x2813. U nas brak PID 00CF w device_filter.
- 32 bity: Size=4 = 2 rejestry; nasze qty zgodne 0 rozbieznosci.
- Rozbieznosci adresow C160-C169 (WL200) i C901-C903, d090 (WJ200 v3) - do sprawdzenia na sprzecie.
- Wyniki: ServMod\tools\reverse\analysis_prodrive\WYNIKI_prodrivenext_2026-11-05.md. Nic nie przetestowane na sprzecie.

## 2026-11-05 (APP) - WL200 na stole: adresy i etykiety (0.98.1-0.98.3)
- Test na sprzecie: C160=3 -> wartosc 3 pod wire 0x14A3. ProDriveNext mial racje, nasze C160-C166 i C169 byly przesuniete; poprawione w hitachi_wl200.json (0.98.2).
- Adresy w tabeli modeli ProDriveNext to numery z instrukcji (wire = numer - 1); warunki WL200 spelnione u uzytkownika (0x1086=0x61, 0x16C7=0, 0x16F0=0).
- C021 pokazuje 62 (EDM) lub 255 (no) zaleznie od dip switch; dodane etykiety (0.98.3). Parametry widoczne tylko przy C091=1 / innym trybie (b014, b115, b116, b136, A180, C195-C198) NIE dodane - decyzja uzytkownika, brak ich na panelu.
- Otwarte: Extended mode WJ-C1 / SJ-P1 = PID 0x00CF z rejestrem 0x2813 (nasz device_filter nie ma), flaga endian z ProDriveNext (ILSpy), WJ200 C901-C903 i d090. Nic z tego nie testowane na sprzecie.

## 2026-11-05 (APP) - 0.98.4: pelne opisy funkcji WL200
Etykiety kodow funkcji wejsc (C001-C007) i wyjsc (C021, C022, C026) w hitachi_wl200.json: wlasne krotkie opisy wg manuala WJ200 Basic (brak manuala WL200 w repo); lista waznych kodow WL200 z danych ProDriveNext (fakt, ktore kody istnieja). Opisy NIE sprawdzone z manualem WL200 ani na panelu.

## 2026-11-05 (APP) - 0.98.5: opisy funkcji WL200 zweryfikowane z manualem WL200
Uzytkownik dodal Hitachi-WL200-Full-Manual.pdf (inputs\manuals). Opisy z WJ200 zgodne; poprawione ograniczenia terminali (GS1 C003, GS2 C004, PTC C005, EB C007, EDM wyjscie 11). Przelacznik Safety (GS1/GS2) i EDM na plycie przypisuja funkcje automatycznie, po wylaczeniu = "no" (255) - wyjasnia C021 62/255. Do zrobienia przy okazji z manualem WL200: opisy i zakresy innych parametrow, weryfikacja bazy.

## 2026-11-05 APP: 0.98.6 - weryfikacja bazy WL200
- Cala baza hitachi_wl200.json porownana z manualem WL200 (rejestry, App. B) i ISF ProDriveNext: adresy zgodne, domyslne/min/max zgodne poza: b910 (3->0), b150/b160/b161 (brak domyslnych, byly kind disp -> teraz wybor d-parametru, 1/1/2).
- Listy opcji ~120 parametrow uzupelnione z ISF (wczesniej tylko 1 pozycja). Znana nieDokladnosc: A082/A282 domyslne zaleza od klasy napiecia (230/400), w bazie stala 230. Parametry ukryte nadal nie dodane. Nieprzetestowane na sprzecie.

## 2026-11-05 APP: 0.98.7
- Hitachi Parameters: po filtrze Differences lista zostawala przewinieta i wiersz roznicy (b910) byl poza ekranem; dodany reset przewijania. Inne marki (Mx2, PowerFlex, Danfoss, Lenze) maja ten sam wzorzec - nie ruszane, do rozwazenia.

## 2026-11-05 APP: 0.98.8
- Ekran Hitachi RS-485 to Mx2Root (nie Ui.kt): kolumna wartosci widthIn(170dp)+ellipsis, scroll reset przy filtrach. b910 default z powrotem 3: po resecie fabrycznym WL200 daje 3 (manual/ISF: 0) - wartosci fabryczne z manuala/ISF dla WL200 moga sie mylic, weryfikowac resetem na sprzecie.

## 2026-11-05 APP: 0.98.9
- WL200 dip switche Safety/EDM: brak rejestru stanu w manualu; wykrycie z wartosci C003/C004/C013/C014 (77/78/1/1) i C021 (62) -> efektywne wartosci fabryczne (Mx2Root swOverride/effDef, BackupPdf.factoryFromDb over). Ograniczenie: reczny wpis tych wartosci przy wylaczonym switchu da bledna ocene.

## 2026-11-05 APP: 0.98.10
- DiagActivity: przycisk Scan (tylko odczyt FC03, 0x1000..0x27FF, dzielenie blokow przy wyjatku, plik regscan-*.txt w cache/share + chooser, roznice vs poprzedni skan). Cel: znalezc rejestr stanu dip switchy Safety/EDM WL200 (skan, przestawic, skan).

## 2026-11-05 APP: 0.98.11
- Rejestr dip switchy WL200 (z 6 skanow uzytkownika): wire 0x1081 bit2=Safety ON, bit3=EDM ON (wspolzmienne: 0x107F bity 0x30 i 0x1E00/0x1E03 = 0 przy Safety ON; 0x1007 i 0x1E04 bit 0x100 = oba ON). Trzeci switch (terminator) bez zmian w zakresie 0x1000-0x27FF. Mx2Session.swBits czytany po readAll tylko dla WL200; fallback wartosci. NIEPRZETESTOWANE.

## 2026-11-05 APP: potwierdzenie 0.98.11 na sprzecie
- Uzytkownik potwierdzil: log "0x1081 = 0x7: Safety ON, EDM off" zgadza sie z fizycznym stanem przelacznikow (odczyt przez adapter USB-RS485 CH34x, WL200, 412/412 param.). Rejestr 0x1081 bit2/bit3 = POTWIERDZONY na WL200. Uzytkownik zglasza: przy Safety ON falownik nie jest wykrywany przez bezposredni kabel USB (OTG), przez terminale RS-485 dziala; przyczyna nieudokumentowana w manualu, nie zbadana.

## 2026-11-06 APP: Omron MX2 przez USB (0.98.15)
- Z CX-Drive (OMRON\CX-One\CX-Drive\DRIVERS\X-Series\HUSBD64.inf, "OMRON Inverter USB Driver") wynika: USB serii X (MX2) uzywa tych samych ID co Hitachi: VID 04A4 PID 008D i PID 00CF (+ 0627:0002). To protokol Hitachi (bulk), nie wirtualny COM. CX-Drive uzywa LibUsbDotNet.
- App: ekran Omron MX2 / Hitachi RS-485 dostal transport "Drive USB" (HitachiUsbPort.kt = HitachiUsb.transact jako UsbSerialPort); Auto wybiera go, gdy jest 04A4:008D i brak adaptera szeregowego i Boxa. NIESPRAWDZONE na sprzecie (brak MX2). PID 00CF nadal nieobslugiwany.


## 2026-11-07 APP: Omron JX (0.98.16)
- Decyzja uzytkownika: dodac falownik Omron JX (3G3JX) do modulu Omron, jak kilka modeli Hitachi. Zrobione: Mx2Profile.OMRON_JX, assets/inverters/omron_jx.json (221 parametrow z manuala I558), flaga jx w Mx2Link/Mx2Session (adresy = numer z manuala minus 1, blok max 4 rejestry, brak Enter/store, brak factory reset po Modbusie). Interfejs Box<->aplikacja bez zmian. NIEPRZETESTOWANE na sprzecie; do sprawdzenia: jednostka d002 (% znamionowego), wartosci domyslne, trwalosc zapisu, teksty bledow (tabela Hitachi). APK sha256 39795d7bd40d21263be49df66f4385e79a0dff9915acd119a8dd87af21a8ecfd.

- 2026-11-07 APP 0.98.17: blad folderu backupow Omron JX (backups-omron-jx vs backups-omronjx) naprawiony; backup przeslany Share nie pojawial sie na liscie Restore.

- 2026-11-07 APP 0.98.18: Backup chmury: wspolny folder dla wielu telefonow. Pliki z losowym id telefonu, kasowanie tylko wlasnych kopii, Restore z folderu scala kopie wszystkich telefonow. Powod: stary schemat (ostatnie 3 pliki w folderze + jeden extras) pozwalal nowemu pustemu telefonowi wyprzec pelne kopie drugiego. Usuniecie na jednym telefonie nie propaguje sie na drugi (tylko dodawanie brakujacych).

- 2026-11-07 APP 0.98.19: Omron MX2 i JX w jednym wpisie listy z wyborem modelu (Settings > Model) i ostrzezeniem przy zlym modelu; osobne foldery backupow (brak zabezpieczenia modelu przy restore). Decyzja uzytkownika: bez rozdzielania listy falownikow.

- 2026-11-07 APP 0.98.20: poprawki GUI (nazwy kafelkow Hitachi/Danfoss, pasek postepu przy otwieraniu Restore w Backup).

- 2026-11-07 APP 0.98.21: ekran Backup and restore aplikacji: karta postepu/wyniku przypieta u gory (byla na dole listy, niewidoczna bez przewijania).

- 2026-11-07 APP 0.98.22: wspolna lista backupow Omron MX2 i JX (z oznaczeniem), blokada Compare/zapisu/PDF dla backupu innego modelu. Do rozwazenia: Danfoss ukrywa backupy drugiego modelu, Hitachi RS-485 CSV nie sprawdza serii.

- 2026-11-08 APP 0.98.23: listy backupów wszystkich marek: pełna lista bez połączenia, po połączeniu ★ + góra listy; inna mapa parametrów (Omron MX2<->JX, Danfoss FC280<->VLT2800) = blokada Compare/zapis/PDF; Hitachi RS-485 inna seria (WL200/WJ200, nagłówek ", series X") = blokada zapisu, Compare only dozwolone; Hitachi USB: ★/góra + ostrzeżenie o innym modelu. Niesprawdzone na sprzęcie.

- 2026-11-08 APP 0.98.24: Restore kopii aplikacji, tryb "Add what is missing": pliki tags.json, notes.json, parts.json, condition.json sa scalane (dopisywane brakujace wpisy), wczesniej pomijane w calosci gdy istnialy; licznik zdjec backupow w wyniku. Niesprawdzone na sprzecie; przyczyna braku zdjec na drugim telefonie nie ustalona.

- 2026-11-08 APP 0.98.25: nowe narzedzie Tools > IR (tester pilotow IR i podglad nadajnikow IR fotobarier, kamera telefonu, bez dodatkowego sprzetu; pilot: tylko wykrycie impulsow, kodu nie da sie odczytac; filtr programowy tylko wyroznia piksele, czysty obraz wymaga filtra IR 850 nm). Niesprawdzone na sprzecie. Pomysly na pozniej: odbiornik IR w Box (RMT), czujnik MLX90640.

- 2026-11-08 APP 0.98.26: nowe narzedzie Tools > Motion (detekcja ruchu/drgan kamera telefonu: pasmowy filtr jasnosci pikseli, kalibracja szumu, Hz w punkcie przez DFT, ograniczone do fps/2). Niesprawdzone na sprzecie.

- 2026-11-08 APP 0.98.27: Motion: kompaktowy uklad bez przewijania, ignorowanie dryfu <1 Hz w pomiarze Hz. Niesprawdzone.

- 2026-11-09 APP 0.98.28/0.98.29: Omron JX dostal schematy polaczenia (klucz omronjx w Wiring.kt, obrazy omron_jx_*.webp, generator wiring_work\make_jx.py) z wycinkiem manuala I558 s.4-77; piny potwierdzone w manualu (5 SP, 6 SN, reszta nie podlaczac, S7=485, brak terminatora). Manual: ServMod\inputs\manuals\Omron-3G3JX-I558-E1-02-UsersManual.pdf. Niesprawdzone w aplikacji na telefonie.

- 2026-11-09 APP 0.98.30: poprawka: schematy JX nie byly widoczne, bo MX2 i JX to jeden przycisk (klucz omron); WIRING["omron"] ma teraz dwa modele, omronjx mapowany do grupy omron z JX wybranym domyslnie. Niesprawdzone na telefonie.

2026-11-09 APP: 0.98.31 - dodano narzedzie Nameplate (OCR tabliczki znamionowej, ML Kit unbundled przez Play services, zeby APK miescil sie w limicie wysylki). Integracja z parametrami falownikow (WL200 najpierw: A003/A004/A082/H003/H004/b012 przez applyDiffs, tylko Pro, z potwierdzeniem) po tescie czytnika przez uzytkownika.

2026-11-09 APP: 0.98.32 - poprawki parsera Nameplate po ttescie uzytkownika. Zaplanowany Setup Maker (3 kroki: silnik, falownik, wzor; czasy i uklad sterowania siedza we wzorze; "Save current setup as template" z roznicy wzgledem fabrycznych). Start po potwierdzeniu odczytu tabliczki.

2026-11-09 APP: 0.98.33 - Nameplate dostal zaznaczanie obszaru tabliczki i powiekszanie przed OCR (po tescie uzytkownika 0.98.32). Setup Maker nadal czeka na potwierdzenie odczytu.

2026-11-09 APP: 0.98.34 - Setup Maker v1 jako osobny kafelek "Setup" (main screen). Wynik to plik backup (naglowek model 0xFFFF, rejestr 0x1086=0x61, tylko parametry setupu), wiec zapis idzie istniejacym Compare/Write (Pro, odczyt zwrotny, ochrona C003/C004). Nastepne: "Save current setup as template", MX2 i inne marki (mapa zamiaru na parametry per marka). Przyporzadkowanie terminali we wzorach to zalozenie z podrecznika, do sprawdzenia na stole.

2026-11-09 APP: 0.98.35 - Setup po uwagach uzytkownika: wszystko edytowalne, zapis dziala bez falownika, domyslnie plik "factory + zmiany" (DB defaults wg klasy 200/400 V, bez C070-C078). Przyczyna braku zapisu w 0.98.34 nieustalona (kod zapisuje do tej samej listy Backups); w 0.98.35 blad zapisu jest pokazywany.

2026-11-09 APP: 0.98.36 - przyczyna braku pliku Setup w Restore: ekran uzytkownika to Hitachi RS-485 (Mx2Session, CSV w backups-hitachi485), a Setup pisal tylko do BackupStore USB. Teraz zapis do obu. Wlasne layouty w SharedPreferences "servmod_setup". Do potwierdzenia na telefonie.

2026-11-09 APP: 0.98.37 - "moc 6" w Setup to byl kod listy H003 (06 = 1.5 kW), nie blad zapisu; pola H003/A082/H004 przyjmuja teraz prawdziwa wartosc. Dodano usuwanie silnikow.

2026-11-09 APP: 0.98.38 - Setup: wybor parametru z wyszukiwarki i listy zamiast wpisywania numeru z pamieci.

2026-11-09 APP: 0.98.39 - Setup: wlasne layouty i zapisane setupy sa edytowalne (SharedPreferences "servmod_setup", klucze layouts i setups). Wbudowane layouty tylko do odczytu (zapis jako nowy).

2026-11-09 APP: 0.98.40 - "Save changes to layout" nie obejmuje parametrow wyliczanych z silnika (A003/A004/A082/H003/H004/b012); zmiana takiego parametru zapisuje sie do layoutu przyciskiem Save przy wierszu. Wartosc z layoutu nadpisuje wyliczona z silnika.

## 2026-11-09 APP 0.98.41
Setup: ekran w rozwijanych kafelkach (Saved setups, Motor, Drive, Layout, Settings, Save) z podsumowaniem wyboru w naglowku. Tylko UI, bez zmiany interfejsu Box.

## 2026-11-09 APP 0.98.42
Setup: Save * (podswietlony) przy niezapisanej zmianie, "(unsaved edits)" w naglowku. Tylko UI.

## 2026-11-09 APP 0.98.43
Setup: Motor tile otwiera narzedzie Nameplate (PlateTab) i wraca z aktywnym silnikiem. Tylko UI.

## 2026-11-09 APP 0.98.44
Setup: nazwy edytowalne do zera; przycisk po zapisie uzywa TagRouter.open(backup) -> Inverters > Backup > Restore (hitachi USB lub hit485). Tylko UI.

## 2026-11-09 APP 0.98.45
Setup: kafelek Drive brand. Omron MX2 = te same numery co Hitachi (A082 w woltach). PF525: P031-P037, P044, P046/P047, t062/t063/t065/t066, A428, P041/P042. Pliki do backups-omron / backups-powerflex. Tylko aplikacja, bez zmiany interfejsu Box.

## 2026-11-09 APP 0.98.46
Dodano assets/inverters/equivalents.json (kopia inputs/equivalents/equivalents_draft.json, V/M/U) i ekran Equivalents w Setup. Marki: Setup ready = WL200, MX2, PF525; reszta wg liczby wpisow do sprawdzenia. Tylko aplikacja, bez zmiany interfejsu Box. Tabele rozmiarow WJ200/JX: inputs/equivalents/drive_tables_wj200_jx.txt.

## 2026-11-09 APP 0.98.47 (niesprawdzone na sprzecie, niepublikowane)
Setup: kafelek "Replace a drive (from a backup)" - wybor backupu starego falownika (dowolna marka CSV), konwersja przez tabele rownowaznikow (Convert.kt) na WL200/MX2/PF525: rampy, max freq, dane silnika jesli sa, wejscia start/stop/up/down/fwd/rev. Kopia pliku: SetupModule.kt.bak0.98.47. Tabela Equivalents zostaje tylko jako podglad.

## 2026-11-10 APP 0.98.48 (niesprawdzone na sprzecie, niepublikowane)
Setup uproszczony: tylko marki z builderem (WL200, MX2, PF525), bez tabeli Equivalents i bez kafelka zamiany. Nowy modul "Drive converter" (id convert, ConverterRoot w setup/SetupModule.kt): backup starego falownika -> marka nowego (zielone = wszystko znalezione, bursztynowe = lista brakow, marki bez zadnych odpowiednikow nie sa proponowane) -> sprawdz motor/rozmiar -> zapis pliku "Replace ... to ..." (tylko zmiany) -> Restore. Kopie: Modules.kt/Ui.kt/build.gradle.kts .bak0.98.47. Build: wariant release trzeba ustawic w Build Variants (domyslnie debug).

## 2026-11-10 APP 0.98.49 (niesprawdzone na sprzecie, niepublikowane)
Setup: kolejnosc Motor -> Brand -> Drive -> Layout -> Settings -> Save. Marki bez rozmiaru pasujacego do silnika szare; rozmiary: zielone = pasuja (napiecie, moc >= silnik, prad), szare = dotkniecie pokazuje powod; wybor rozmiaru otwiera Layout. 8 nowych marek w Setup i Drive converter (WJ200, JX, FR-D700, MS300, ACS355, GD200A, MD500, GA500): tabele rozmiarow z manuali (assets/inverters/drive_tables.txt, zrodla ServMod\inputs\equivalents\drive_tables_*.txt), 3 uklady (FWD/REV+pot, Start/Stop+Up/Down, Start/Stop+pot) budowane z tabeli rownownaznikow, z lista brakow i podpowiedzia obejscia (np. brak Up/Down -> potencjometr). Silnik wpisywany ogolnym silnikiem planGen (lista: najblizsza pozycja). Danfoss FC280/VLT2800, ATV320, V20, Lenze: tabele rozmiarow w drive_tables_groupC.txt, jeszcze nie w aplikacji (inne formaty backupu). Kopie: SetupModule.kt.bak0.98.48 (zawiera NOWA wersje), poprzednia w scratch.

- 2026-11-10 APP 0.98.50 (vc 325): Setup = Quick build (3 kafelki Motor/Drive/Layout, tabela parametrow zawsze widoczna, pasek Save file / Write to drive). Polaczenie silnika Y/Delta doradzane w sekcji Drive (przelacznik 400 V / 200 V); usuniete falszywe ostrzezenie 400 V vs 200 V. NIETESTOWANE na sprzecie, nieopublikowane.

- 2026-11-10 APP 0.98.51 (vc 326): Setup uproszczony: wybor layoutu jako pigulki pod kafelkami, parametry jako zwarte wiersze (edycja po tapnieciu jednego wiersza). Nietestowane na sprzecie.

- 2026-11-10 APP 0.98.52 (vc 327): Setup: wiersz parametru = nazwa nad wartoscia (naprawa rozciagania przy dlugich etykietach). Nietestowane na sprzecie.

- 2026-11-11 APP 0.98.53 (vc 328): Setup/ACS355: zakresy 9906/9909 w bazie to mnozniki znamionowych (0.2-2.0 x I2N, 0.2-3.0 x kW) - sprawdzane teraz wzgledem falownika, nie jako ampery/kW; falowniki >5x za duze dla silnika wyszarzone; keypad vs Up/Down nie jest konfliktem; ostrzezenia zwiniete w jedna linie. Nietestowane na sprzecie.

- 2026-11-11 APP 0.98.54 (vc 329): Setup ma DWA widoki do wyboru (przelacznik View u gory, zapamietany): "Quick build" (koncept C, jedna strona) i "Step by step" (koncept A: 5 krokow na osobnych stronach Motor > Drive brand > Drive size > Layout > Review and write, Back/Next). Ostrzezenia: parametry odpowiedzialne sa podswietlone na bursztynowo z sugerowana wartoscia i przyciskiem Use this (ACS355 9906/9909 wymuszane poza bledna baza zakresow); Save w wierszu zamyka ramke. Nietestowane na sprzecie. Opcje widoku do rozstrzygniecia po testach: zostawic jeden czy oba.

- 2026-11-11 APP 0.98.55 (vc 330): Setup: parametry wskazane w uwagach (np. b012, H004, A003) sa pomaranczowe na liscie; brakujace maja pomaranczowy wiersz z polem wartosci (b012 z sugestia procentu = prad silnika / prad falownika) i przyciskiem Add to setup; istniejace maja przycisk Looks right. Naprawiony przycisk Back w widoku krokow. Nietestowane na sprzecie.
- 2026-11-11 APP 0.98.56 (vc 331): Setup: rozpoznawanie parametrow w uwagach dziala dla wszystkich marek (np. Pr37, C003, 9906); uwagi informacyjne (display only, not needed) nie liczone jako do sprawdzenia; licznik 'to check' liczy tylko wiersze pomaranczowe. Nietestowane na sprzecie.
- 2026-11-11 APP 0.98.57 (vc 332): Setup: wszystkie parametry do sprawdzenia sa na gorze listy jako pomaranczowe wiersze z polem do edycji, wartoscia fabryczna (lub sugestia) i przyciskami Write this / Add to setup / Looks right / Remove; wartosc spoza zakresu bazy mozna zapisac swiadomie. MS300: 05-01 liczone jako procent pradu falownika, 01-02 dla klasy 400 V dopuszcza do 510 V. Nietestowane na sprzecie.
- 2026-11-11 APP 0.98.58 (vc 333): Setup: falownik za duzy dla pradu silnika (<20 procent) nie jest juz blokowany, tylko ostrzega (wybor mozliwy); dodane ostrzezenie o nieprawdopodobnym pradzie z tabliczki wzgledem kW i V (np. 0.4 A dla 0.75 kW 400 V). Poprzednia regula 20 procent szarzala wszystkie falowniki. Nietestowane na sprzecie.
- 2026-11-11 APP 0.98.59 (vc334): Setup - layouty niewykonalne dla falownika zablokowane z powodem (brak wejsc/komorek), kalkulator pradu silnika +-30 procent blokuje zly prad, usuniete ostrzezenia nie blokujace pracy. NIEPRZETESTOWANE na sprzecie, nieopublikowane.
- 2026-11-11 APP 0.98.60 (vc335): Setup - nowy layout FWD/REV + 3 predkosci stale (Hitachi WL200/MX2, PF525, WJ200, JX, FR-D700, ACS355, GD200A, MD500, GA500; MS300 zablokowany - brak wejsc w bazie), rysowany schemat polaczen przy kazdym layoucie. Dane assets/inverters/setup_multispeed.json (funkcje zweryfikowane w manualach, NIEPRZETESTOWANE na sprzecie).
- 2026-11-11 APP 0.98.61 (vc336): PRZEGLAD Setup + Converter z manualami. (1) Layouty marek generycznych przepisane na jawne tabele assets/inverters/setup_layouts.json (parametry + zaciski, kazda pozycja sprawdzona w tekscie manuala) zamiast zgadywania z equivalents; naprawia blednie zablokowane FR-D700 i MD500, GA500 (podwojny 3-wire = oPE03), ACS355 (UP/DOWN kolidowal z kierunkiem i predkosciami stalymi), FR-D700 potencjometr 0-5 V (Pr73=1), GD200A konflikt zrodel A/B. (2) Poprawki baz parametrow (tools/dbfix_0.98.61.py): GA500 zakresy hex H1-xx i skale E1-04..E1-10, E2-01; GD200A P00.11/12 zapisywalne, P02.05 w A, P00.07; MD500 rampy dec1 (F0-19=1) i F1-04 dec2; ACS355 9905 zapisywalny; MS300 wejscia 02-01..02-07 rozdzielone (wczesniej backup nie obejmowal MI2-MI7), 05-01 w amperach (cofniecie blednej zmiany na procenty); WJ200 listy A082/H003/H004. (3) planGen: moc silnika pierwsza, FR-D700 bez Pr80, JX/MX2 napiecie wg klasy, WJ200/JX b012. (4) Converter rozpoznaje standardowy layout starego falownika i daje sprawdzona liste + schemat zaciskow nowego. (5) Schemat rysowany z prawdziwymi nazwami zaciskow; layout Start/Stop + potencjometr takze dla WL200/MX2/PF525. NIEPRZETESTOWANE na sprzecie, nieopublikowane.
- 2026-11-11 APP 0.98.62 (vc337): wspolny format danych silnika (sensors/MotorCalc.kt) dla Nameplate, Setup i Convertera: kW z kropka, V calkowite, A do 2 miejsc, rpm calkowite, bieguny parzyste; bieguny wyliczane z obrotow gdy puste, typowe obroty proponowane z biegunow, sprzecznosc obroty/bieguny blokuje Setup z poprawka jednym dotknieciem; MotorStore normalizuje przy odczycie i zapisie. Setup: pole Speed rpm, na karcie layoutu pola Speed 1/2/3 (Hz, takze dla marek procentowych) i Ramp. NIEPRZETESTOWANE na telefonie i sprzecie, nieopublikowane.
- 2026-11-11 APP 0.98.63 (vc338): (1) tools/check_param_db.py - kontrola spojnosci baz parametrow i tabel Setup, uruchamiac przed kazdym wydaniem (kod wyjscia 1 = nowy blad); znane, jeszcze nie poprawione bledy w tools/check_param_db_known.txt (58 pozycji: MS300 18, MD500 16, GD200A 5, FC280 5, GA500 4, FR-D700 4, ACS355 3, V20 2, VLT2800 1). (2) Setup, marki generyczne: opcja Factory reset first (domyslnie wylaczona); po Write to drive lista Restore w Inverters pokazuje przycisk Factory reset now z potwierdzeniem albo Skip (SetupHandoff.resetFirst, Mx2Root). NIEPRZETESTOWANE, nieopublikowane.
- 2026-11-11 APP 0.98.64 (vc339): poprawki baz parametrow po przegladzie. (1) WJ200: listy wyboru uzupelnione z pelnego manuala WJ200_Instruction_NT325X.pdf (tools/wj200_labels_0.98.64.py): 156 -> 32 list z jedna pozycja; wejscia C001-C007 i wyjscia C021/C022/C026 z tabel funkcji, stany C011-C017/C031-C036, 44 listy z opisow parametrow, 60 z WL200 (ta sama rodzina, kod kontrolny zgodny). H004/H204 ograniczone do 0 (2 bieguny) - 4 (10 biegunow) wg listy rejestrow 1504h - lista z WL200 do 48P byla bledna. H003 potwierdzone 00 (0.1 kW) - 15 (18.5 kW) rejestrem 1503h. A001/A002 rozszerzone. (2) Wszystkie 58 znanych bledow z check_param_db_known.txt poprawione (tools/dbfix_0.98.64_ms300_md500.py, dbfix_0.98.64_rest.py): MS300 rozdzielone 02-13/02-16/02-17, 03-00/03-01, 03-07/03-08, skale 05-05/05-17/05-68/05-74, 08-76/08-77, 03-57/03-59/03-61, zakresy 14-70..14-73 i 02-80; MD500 skale F0-14, F0-15, F1-10, F1-36, F3-01, F8-51, Fd-08, A0-06..A0-08, A2-07/A2-10/A2-36/A2-64, Fd-06 jako lista; GD200A zakresy P00.02, P03.11, P04.01, P08.50, P17.12; FC280 1-62, 2-12, 5-90, 14-29, 33-47; GA500 E3-06/07/09, n8-49; FR-D700 Pr295, Pr69, Pr37 (skala nadal niepotwierdzona); ACS355 1504/1505/2624; V20 P2274/P2285; VLT2800 102 (moc silnika zapisywalna, kW x 100). (3) check_param_db.py: wyjatki na wartosci specjalne 8888/9999 i na zakres 0-0. Lista znanych bledow jest teraz pusta - kazdy nowy blad zatrzymuje wydanie. NIEPRZETESTOWANE na sprzecie, nieopublikowane.
- 2026-11-12 APP 0.98.65 (vc340): nowe layouty sterowania dla Hitachi WL200/WJ200, Omron MX2/JX, Allen-Bradley PF525 i Mitsubishi FR-D700 (tools/setup_layouts_0.98.65.py): jog (przycisk impulsowania), extreset (lancuch bezpieczenstwa NC + przycisk kasowania), ma420 (predkosc z czujnika 4-20 mA), twoacc (druga rampa; bez PF525), pidpump (PID z czujnikiem cisnienia 4-20 mA), modbus (sterowanie po RS-485). Wartosci sprawdzone w manualach: Hitachi JG/EXT/RS/AT/2CH wg tabeli funkcji wejsc, A038 0.5-9.99 Hz, A076 sprzezenie PID; PF525 kody wejsc 9 Jog Forward, 12 Aux Fault (blad przy rozwarciu), 13 Clear Fault, A431/A459/A460/A464; FR-D700 kody 3 RT, 4 AU, 5 JOG, 7 OH (NC, E.OHT), 62 RES, Pr15/16, Pr44/45, Pr128=20 z pomiarem na zacisku 4, Pr267. Layouty wszystkich marek (takze WL200/MX2/PF525) pochodza teraz z assets/inverters/setup_layouts.json zamiast ze sztywnych list w kodzie; rampy sa jawne w kazdym layoucie. Schemat rysuje czujnik 4-20 mA i RS-485. check_param_db.py sprawdza teraz kazdy layout z listy order. NIEPRZETESTOWANE na sprzecie, nieopublikowane.
- 2026-11-12 APP 0.98.66 (vc341): layouty dla maszyn bez biegu wstecznego (tools/setup_layouts_0.98.66.py): speed3sel (Hitachi/MX2: A019=1, wejscia SF1/SF2/SF3 = 32/33/34, osobny przelacznik na kazda predkosc), speed7 (wszystkie 6 marek: Hitachi CF1-CF3 binarnie A021-A027; PF525 zaciski 05/06/07 jako Preset Freq A411-A417; FR-D700 RL/RM/RH z kombinacjami Pr4-Pr6 i Pr24-Pr27), handauto (przelacznik recznie/auto: Hitachi wejscie AT, PF525 Speed Ref 2 z P049, FR-D700 sygnal AU). Pigulki layoutow maja teraz krotkie nazwy (klucz "shorts" w setup_layouts.json), pelna nazwa jest w opisie. Hitachi WL200/WJ200/MX2 maja 13 layoutow, JX 11, PF525 11, FR-D700 12. NIEPRZETESTOWANE na sprzecie, nieopublikowane.
- 2026-11-12 APP: analiza EzSQ z ProDriveNext (tools/reverse/analysis_ezsq/EZSQ_PROTOCOL.md). Komendy EzSQ to zwykle ramki Modbus z prywatnymi kodami funkcji, nieopisane w manualu WJ200: 0x64 Download Ready (06 + requestCode 2B + dataSize 4B), 0x41 Download Request (08 + 8 bajtow programu), 0x42 Upload Ready (02 + requestCode), 0x43 Upload Request (02 + requestCode, odpowiedz 8 bajtow), 0x46 EEPROM Request (04 + requestCode + requestParam), 0x67 Password (09 + kod 1B + haslo 8B); 0x4A connect w warstwie operatora RS-422; 0x69/0x6A trace. Zrodla: HITModbusCommunicationSchema.xml oraz IL metod MakePduReq_Ezsq* w Hitachi.ModbusComm.dll (skrypt tools/reverse/analysis_ezsq/ildump.py). Kolejnosc wgrywania: Ready -> N x Request po 8 bajtow -> EEPROM. Nic nie skopiowane do aplikacji. NIESPRAWDZONE na falowniku; pierwszy test to ramka tylko do odczytu 01 00 00 01 42 02 00 01 6D B8 w DiagActivity "Send raw".
- 2026-11-12 APP 0.98.67 (vc342): kafelek "Program" w menu falownika (tylko Hitachi WJ200/WL200 i Omron MX2, czyli falowniki z EzSQ). Prosty edytor drabinkowy: linie IF wejscie X(0x) jest ON/OFF (opcjonalnie przez N sekund) THEN wyjscie Y(0x) ON/OFF albo predkosc albo stop. Generuje listing EzSQ (do sprawdzenia w narzedziu PC) i kod bajtowy (pierwsza proba, NIEZWERYFIKOWANY). Zapis do pliku (katalog aplikacji ezsq\\). Przyciski do falownika: odczyt 0x42 (czy jest program), odczyt 0x43 (pierwsze 8 bajtow), zapis 0x64 + N x 0x41 + 0x46. Nowe pliki: ezsq/Ezsq.kt, ezsq/EzsqPage.kt; Mx2Link.vendorRaw() wysyla ramke z prywatnym kodem funkcji i zbiera cala odpowiedz; Mx2Session.ezsqRun/ezsqLog. Kodowanie instrukcji wlasne, opracowane dla interoperacyjnosci na podstawie tablicy instrukcji falownika. NIEPRZETESTOWANE na sprzecie.

## 2026-11-12 APP 0.98.68 - protokol EzSQ rozlozony i wpisany do aplikacji
- Zrzut USB z ProDriveNext (WL200) pokazal, ze gniazdo USB falownika ma DWA kanaly, rozpoznawane po
  pierwszym bajcie pakietu: 0x01 = Modbus (01 00 00 + ramka RTU), 0x02 = EzSQ (02 cmd lenLo lenHi + dane).
  Kanal EzSQ nie ma adresu slave ani CRC16. Dlatego wczesniejsza proba wyslania komend EzSQ jako kodow
  funkcji Modbus dawala "illegal function" - szla zlym kanalem.
- Komendy potwierdzone: 0x40 download ready, 0x41 ramka 32 bajty, 0x42 upload ready, 0x43 ramka upload,
  0x46 zapis do EEPROM (ok. 2,5 s), 0x4C status. Numeracja ramek od 1. Odczyt zwrocil dokladnie to,
  co wyslano - round trip bajt w bajt.
- Blok programu to 288 bajtow (9 ramek po 32): naglowek z nazwa, numerem, wersja narzedzia, datami,
  modelem, rozmiarem kodu, liczba linii i slowem kontrolnym (suma slow 16-bit BE z bajtow 0..93 i z obszaru
  kodu), potem 160 bajtow zmiennych/taskow i od bajtu 256 skompilowany kod.
- Pelna tabela instrukcji EzSQ (opcody, dlugosci, maski parametrow) znaleziona w plikach CSV ProDriveNext;
  kopia w ServMod\tools\reverse\analysis_ezsq\wl200_grammar\. Potwierdza opcody uzyte w aplikacji.
- Format pliku programu ProDriveNext to zwykly CSV UTF-8 - aplikacja moze go czytac i zapisywac.
- W aplikacji: ezsq\EzsqLink.kt (kanal 0x02), ezsq\EzsqFile.kt (blok 288 B, suma kontrolna, deasembler),
  Mx2Link.hitachi / HitachiUsbPort.usb (dostep do surowego USB). Kafelek Program: odczyt z falownika,
  klonowanie do drugiego falownika, zapis programu zbudowanego w aplikacji.
- EzSQ dziala TYLKO na gniezdzie USB falownika, nie przez przejsciowke RS-485.
- NIEPRZETESTOWANE NA SPRZECIE z poziomu aplikacji. Protokol potwierdzony ze zrzutu, aplikacja jeszcze nie.

## 2026-11-12 APP 0.98.69 - Program (EzSQ) jako kafelek, nie zakladka
- Pasek na dole wraca do pieciu pozycji (Backup, Parameters, Control, Settings, Faults).
- Program (EzSQ) jest czwartym kafelkiem w zakladce Backup, pod Restore - tak jak Connect & help,
  Create backup i Restore. Kafelek pokazuje sie tylko tam, gdzie falownik ma wlasny program.
- Przyczyna, dla ktorej zakladka w 0.98.68 sie nie pokazala: Hitachi po wlasnym USB chodzi ekranem z Ui.kt
  (Vm), a nie Mx2Root - zakladka byla dodana tylko w Mx2Root. Teraz strona jest wspolna.
- ezsq/EzsqPage.kt: MxProgram(s) to cienka nakladka na ProgramPage(model, log, run); run bierze zadanie
  i oddaje je sesji, ktora trzyma lacze. Dzieki temu ta sama strona dziala na ekranie USB i na RS-485.
- Vm.kt: ezsqLog + ezsqRun(label) - zadanie EzSQ na watku roboczym, wynik na gorze logu.
- tags/BackupPages.kt: BackupMenu(count, ezsq, open) - czwarty kafelek, strona 4.

## 2026-11-12 APP 0.98.70 - gotowe programy EzSQ + poprawka Setup
- BLAD w Setup (od wersji z kreatorem): "Save file" i "Write to drive" na dolnym pasku nic nie robily,
  jesli panel "Names and file" byl zwiniety. Oba przyciski wywoluja funkcje z tablicy actions[], a ta byla
  wypelniana WEWNATRZ panelu - Acc() sklada zawartosc tylko gdy jest otwarty, wiec przy zwinietym panelu
  obie pozycje zostawaly null. Funkcje zbudowane teraz poza panelem. Dodany pasek ze stanem zapisu nad
  przyciskami, zeby bylo widac wynik przy zwinietym panelu.
- Kafelek Program przebudowany: zamiast budowania wiersz po wierszu jest 7 gotowych programow, w ktorych
  podstawia sie tylko wartosci (wejscie, wyjscie, czas, predkosc):
  praca i przerwa w kolko / start po zwloce / dwie predkosci na jednym wejsciu / praca gdy przycisk trzymany /
  praca przez zadany czas po nacisnieciu / wyjscie po osiagnieciu predkosci / lagodne zatrzymanie drugim wejsciem.
- Programy budowane z prawdziwych zmiennych falownika wg tabeli z ProDriveNext (SET-Freq=40, ACCEL=41,
  DECEL=42, FM=44, X(00..09)=68..77, Y(00..05)=79..84, FW=118, RV=119). Listing jest zrodlem EzSQ, da sie
  go przepisac do ProDriveNext jak stoi.
- Nowy przycisk: zapis programu jako plik .csv ProDriveNext (Program > Open a program file) - do sprawdzenia
  lub skompilowania na PC.
- NIEPOTWIERDZONE: pole celu skoku w "goto" i "if ... then". Przyjete jako numer linii docelowej. Reszta
  (entry, end, stop, podstawienia) potwierdzona na skompilowanym programie z PC. Do domkniecia: skompilowac
  w ProDriveNext program z if/goto, wgrac do falownika i odczytac aplikacja - porownanie da odpowiedz.

## 2026-11-12 APP 0.98.71 - kodowanie skokow EzSQ potwierdzone
- Zmierzone kompilatorem ProDriveNext (cztery kompilacje, po jednej linii wiecej): entry, end, stop, goto,
  wait i LABEL maja 4 bajty, podstawienie i "if ... then" po 8. Linia z etykieta kosztuje dodatkowe 4 bajty,
  bo kompilator wstawia osobne slowo LABEL (0x10130000, numer etykiety w dolnych 16 bitach).
- Cel skoku to NUMER ETYKIETY, nie numer linii. Generator poprawiony; wszystkie cztery zmierzone sumy
  (40, 64, 68, 76 bajtow) zgadzaja sie co do bajta z naszym modelem.
- Poprawiony eksport do pliku ProDriveNext: podstawienie to Mnemonic "<zmienna>=" z wartoscia w Parameter3,
  "if" rozklada sie na Parameter1..5 (zmienna, znak, wartosc, "then", etykieta), "goto" i "wait" w Parameter1,
  etykieta w kolumnie Label. Wczesniejszy eksport wczytywal sie, ale edytor go nie rozumial.
- Deasembler w aplikacji zna teraz LABEL, wait, if i podstawienia oraz nazwy zmiennych po numerach.
- Zostalo do sprawdzenia na sprzecie: skala operandu "wait" (edytor dzieli wczytana liczbe przez 100).

## 2026-11-12 APP 0.98.72 - uruchamianie programu EzSQ z aplikacji
- Parametry potrzebne, zeby program cokolwiek robil (potwierdzone w naszej bazie WL200/WJ200):
  A001 = 7 (predkosc zadaje program), A002 = 1 (komenda pracy z zaciskow - tym sa FW/RV programu),
  C001..C007 = 56..62 (wejscie programu = MI1..MI7 = X(00)..X(06)),
  C021/C022/C026 = 44/45/46 (wyjscie programu = MO1..MO3 = Y(00)..Y(02)),
  A017 = 2 start programu, 0 stop.
- W kafelku Program: lista "co musi byc ustawione" liczona z wybranego wzoru (tylko uzywane zaciski),
  przycisk ustawiajacy to wszystko z utrwaleniem w EEPROM, Start / Stop programu i odczyt stanu.
- A017 = 2 oznacza takze automatyczny start programu po zaniku zasilania - napisane na ekranie.
- KIERUNEK EDYTORA (ustalone): nie robimy kanwy ze schematem logicznym. Nastepny krok to program jako
  lista krokow ("Rozpedz do 20 Hz / Pracuj 5 s / Czekaj az X(00) bedzie ON / Wroc do kroku 1"), gdzie kazdy
  krok to gotowy, zmierzony kawalek kodu EzSQ. Nie trzeba kompilatora - skladamy znane bloki, rozwiazujemy
  tylko numery etykiet. Gotowe wzory zostaja jako presety wypelniajace liste krokow.
  Uzasadnienie i katalog krokow: claude/servmod-program-editor-direction.md.

## 2026-11-12 APP 0.98.73 - program jako lista krokow, nowe wzory
- Kafelek Program przebudowany na LISTE KROKOW. Kazdy krok to jedno zdanie z liczbami do zmiany; dodawanie,
  kasowanie, przestawianie (gora/dol) i zmiana wartosci chipami. Gotowe wzory sa presetami, ktore wypelniaja
  liste - po zaladowaniu mozna dolozyc albo wyrzucic krok. Jeden model zamiast dwoch trybow.
- Rodzaje krokow (kazdy to sprawdzony kawalek EzSQ): bieg w przod / w tyl, zmiana predkosci, stop, czekaj czas,
  czekaj na wejscie, czekaj na osiagniecie predkosci, ustaw wyjscie, czas rozpedzania, czas hamowania,
  zeruj licznik, policz jeden, skok po osiagnieciu licznika, skok gdy wejscie wlaczone, powrot do kroku.
- Czekanie na wejscie realizowane jedna instrukcja: etykieta + "if X(n) = <stan przeciwny> then <ta sama
  etykieta>" - uzywa wylacznie porownania "=", ktore znamy.
- USUNIETE wzory, ktore nie potrzebuja programu (jog, dwie predkosci na jednym wejsciu, wyjscie po osiagnieciu
  predkosci jako osobny program, lagodne zatrzymanie) - to samo robi sie funkcjami zaciskow, program byl zbedny.
- NOWE wzory, ktorych bez programu zrobic sie nie da: cykl z czujnikiem i impulsem wyjscia (scenariusz
  uzytkownika), indeksowanie do czujnika z postojem, wahadlo miedzy dwoma czujnikami, pompa dwupoziomowa
  z wolnym dopelnianiem, rozruch schodkowy, odliczanie cykli z sygnalem po partii, cofniecie i ponowna proba
  przy zatorze. Zostaly tez: praca i przerwa w kolko oraz jeden przebieg na nacisniecie.
- Do generatora dolozone instrukcje inc i dec (licznik cykli).

## 2026-11-12 APP 0.98.74 - kontrola programu i emulator
- ezsq/EzsqCheck.kt: sprawdzanie programu na biezaco, jezykiem roboty a nie jezyka programu. Lapie:
  skok do nieistniejacego kroku, skok do samego siebie, brak "wroc do kroku" na koncu (program wykona sie raz),
  petle bez zadnego czekania w srodku (falownik lecialby tysiace razy na sekunde), kroki nieosiagalne,
  licznik uzyty bez zerowania, oczekiwanie na licznik bez liczenia, wyjscie wlaczane i nigdy nie wylaczane,
  silnik uruchamiany i nigdy nie zatrzymywany, predkosc ustawiana bez uruchomienia, program wiekszy niz 6144 B,
  oraz przypomnienie, ze krok "czekaj na osiagniecie predkosci" uzywa niepotwierdzonego porownania "<".
  Bledy czerwone blokuja przycisk zapisu do falownika; reszta to uwagi.
- ezsq/EzsqSim.kt: emulator. Wejscia to przelaczniki do klikania, silnik to liczba rozpedzana i hamowana
  wedlug czasow ACCEL/DECEL, sa wyjscia, licznik, czas symulacji i dziennik zdarzen. Przyciski Run / Pause /
  Skip the wait / Reset i mnozniki czasu x1, x10, x60. Aktualny krok zaznaczony strzalka na liscie krokow.
  Zabezpieczenie: 300 obrotow petli bez zadnego czekania zatrzymuje emulator z wyjasnieniem.
- Nazewnictwo banera jak w demo PLC ("EMULATOR: nothing is connected").

## 2026-11-12 APP 0.98.75 - emulator jako panel graficzny
- ezsq/EzsqPanel.kt: emulator przestal byc tekstem. Rysowane na Canvas:
  * wyswietlacze siedmiosegmentowe (TIME w sekundach, SPEED w Hz, STEP, COUNT) - zgaszone segmenty widoczne
    slabo, jak na prawdziwym wyswietlaczu;
  * diody terminali: IN X0..X6 (klikalne, zielone) i OUT Y0..Y2 (bursztynowe), z poswiata gdy wlaczone;
  * diody FWD / REV / RUN.
- Opisy krotkie, zgodne z numeracja programu: X0..X6 i Y0..Y2 (czyli X(00) to X0).
- Panel zastapil poprzedni opis tekstowy stanu; dziennik zdarzen zostaje pod panelem.

## 2026-11-12 APP 0.98.76 - kodowanie skokow poprawione i potwierdzone na sprzecie
- Falownik E43 "EzSQ invalid instruction" po wgraniu naszego programu. Przyczyna znaleziona przez odczyt
  z WL200 programu, ktory ProDriveNext tam wgral: CEL SKOKU TO OFFSET BAJTOWY INSTRUKCJI LABEL, a nie numer
  etykiety. Nasz generator dawal numer (1, 2, 3...), czyli adres niepodzielny przez 4 - skok w srodek
  instrukcji i stad blad.
- Cala reszta kodowania byla dobra CO DO BITU: entry, end, LABEL, podstawienia (0x40060000|0x00800000|(id<<8)),
  wait (0x10160000|0x00800000|wartosc), if (0x10080000|0x00800000|(znak<<25)|(id<<8)|liczba).
- Generator liczy teraz offsety w dwoch przebiegach. Sprawdzone: nasze 16 slow dla programu referencyjnego
  zgadza sie bajt w bajt z tym, co odczytano z falownika.
- Deasembler: maskowanie bitow 23 i 24 (flagi "operand jest liczba") przed rozpoznaniem kodu instrukcji -
  wczesniej pokazywal "?" przy podstawieniach, wait i if. Teraz rozpisuje nazwy zmiennych, znaki porownania
  i cele skokow.
- Eksport CSV: pole wait trzyma wartosc skompilowana (milisekundy), plik dostal BOM i konce linii CRLF jak
  pliki zapisywane przez samo ProDriveNext.
- Zostalo: fizyczne znaczenie operandu wait (stoper) i kody pozostalych znakow porownania.

## 2026-11-12 APP 0.98.77 - zapis zatrzymuje program przed wgraniem
- Objaw: odczyt programu dziala, zapis odbija sie po 14 ms ze statusem 0x06 juz na komendzie 0x40.
- Powod: falownik nie przyjmie nowego programu, gdy jego wlasny program jest uruchomiony (A017 = 2)
  albo gdy stoi trip. ProDriveNext ma przed wgraniem program zatrzymany, stad u niego to nie wychodzilo.
- Aplikacja czyta teraz A017 przed wgraniem i jesli program chodzi, zatrzymuje go (A017 = 0 + utrwalenie),
  wgrywa i ZOSTAWIA zatrzymany; start nalezy do uzytkownika. Dotyczy zapisu wzoru i klonowania.
- Statusy kanalu EzSQ tlumaczone na jezyk roboty: 0x01 nieznana komenda, 0x02 zle dane,
  0x06 zajety (program chodzi albo trip).

## 2026-11-12 APP 0.98.78 - poprawka czasu wait + pasek wysylania
- Jednostka operandu wait w EzSQ to 10 ms (nie 1 ms). Krok "wait 1 s" trwal 10 s, bo wpisywalismy slowo 1000
  (sekundy x 1000), a 1000 x 10 ms = 10 s. Poprawione: sekundy x 100. Zgodne z referencja ProDriveNext
  (edytor "20" -> kod 2000 -> 20 s).
- Emulator liczyl w prawdziwych ms i pokazywal dobry czas - nie zmieniany.
- Kafelek Program: pasek postepu podczas wysylania programu (licznik ramek z EzsqLink.download/upload),
  potwierdzenie "Sent: N frames written to the drive and stored" po sukcesie, "Not sent: <powod>" po bledzie.
  Dotyczy zapisu wzoru i klonowania.

## 2026-11-12 APP 0.98.80 - osobne timery + okno postepu na wierzchu
- Emulator: zamiast jednego okna, rzad TIMERS z osobnym okienkiem na kazdy krok wait w programie (T1, T2...).
  Kazde od razu pokazuje wartosc z programu; aktualnie odliczajacy podswietlony (bursztynowy) i liczy w dol,
  reszta przygaszona na swojej wartosci. Rzad przewijany poziomo gdy timerow duzo.
- Panel przeorganizowany: SPEED / STEP / COUNT w gornym rzedzie, diody FWD/REV/RUN pod spodem, potem TIMERS.
- Pasek postepu i komunikat wysylania przeniesione do okna dialogowego (overlay) - widoczne na wierzchu ekranu
  podczas wgrywania, niezaleznie od przewiniecia. Podczas: "Writing... %, do not unplug". Po: komunikat
  sukcesu/bledu + OK. Dotyczy zapisu wzoru i klonowania.

## 2026-11-12 APP 0.98.81 - guard polaczenia + tryb wejsc switch/push
- Zawieszenie: write/clone przy odlaczonym falowniku pokazywalo dialog "Writing 0%" ktory wisial w nieskonczonosc,
  bo run() nie wywolywalo callbacku (brak linku). Teraz Write/Read/Clone sprawdzaja polaczenie i gdy offline
  pokazuja w oknie "Connect the drive first (the Connect button at the top)" + OK, bez proby wgrania.
  ProgramPage dostal parametr connected (s.connected / vm.connected).
- Emulator, wejscia: kazde X ma maly przelacznik SW / PUSH pod dioda. SW (jak dotad) = tap przelacza i zostaje.
  PUSH = wejscie ON tylko gdy trzymane, OFF po puszczeniu (impuls, jak czujnik). Tryb per wejscie, stan w
  EzsqSim.xMomentary. Realizacja push przez detectTapGestures onPress + tryAwaitRelease.

## 2026-11-12 APP 0.98.82 - Lenze 8400 CAN przez adapter USB-CAN (nie tylko Box)
- Dodane drugie zrodlo CAN dla Lenze 8400: adapter USB-CAN wpiety bezposrednio w telefon (USB-C / OTG),
  obok dotychczasowego ServMod Box. Na ekranie Lenze u gory wybor "ServMod Box" / "USB-CAN" (zapamietywany);
  przycisk Connect dla USB otwiera port szeregowy adaptera (UsbSerialProber + zgoda USB), zaklada kanal CAN i laczy.
- Protokol adaptera: slcan (serial-line CAN, ASCII: C/S0..S8/O, M0/M1, A1/A0, tIIIL...). Nowa klasa UsbCanPort
  implementuje interfejs CanPort tak samo jak BoxCanPort, wiec LenzeSdo (CANopen SDO) dziala bez zmian.
  Odczyt parametr po parametrze (bez wsadowego "job" jak w Boxie) - wolniej, ale pelna funkcjonalnosc.
- Predkosci slcan: 20->S1, 50->S2, 125->S4, 250->S5, 500->S6 (domyslna), 1000->S8. Tylko klasyczny 11-bit CAN.
- WAZNE (niesprawdzone): adapter WeAct USB2CANFD V2 ma dwa firmware - slcan (CDC serial, nasza sciezka) oraz
  candlelight/gs_usb (bulk, NIE widziany jako port szeregowy). Dziala tylko z firmware slcan; przy candlelight
  trzeba przeflashowac na slcan. Interfejs Box<->aplikacja NIE zmieniony (KONTRAKT bez zmian).

## 2026-11-12 APP 0.98.83 - Lenze: wybor polaczenia jak w pozostalych modulach
- Uzytkownik: pozostale moduly wykrywaja automatycznie (brak adaptera USB -> szukaj Boxa); ma byc tak samo wszedzie.
- Reczny przelacznik Box/USB z 0.98.82 zastapiony standardowym wyborem trzech opcji (FilterChip):
  Automatic / USB adapter / ServMod Box, domyslnie Automatic (klucz prefs lzAdapter).
- Regula Auto taka sama jak w Danfoss (wantBoxConn): Box gdy wymuszony lub (Auto i Box juz polaczony lub brak
  adaptera USB); inaczej adapter USB-CAN. Stan onUsb pilnuje, ktory transport jest aktywny (bind/open/status/disconnect).
- Interfejs Box<->aplikacja bez zmian.

## 2026-11-12 APP 0.98.84 - EzSQ: blad wzoru z licznikiem + 9 nowych programow + trzy liczniki
- Blad: wzor "Count the cycles, then signal" (batch) mial ifCount z celem 9 (krok "Go back to step 2") zamiast 10
  (out Y0 on). Po 5 cyklach program wracal na poczatek, kroki 10-14 byly nieosiagalne (kontrola to pokazala).
  Poprawione: target = 10. Reszta presetow sprawdzona skryptem (cele skokow, nieosiagalne kroki, petle bez
  czekania, liczniki bez resetu) - czysto.
- Trzy liczniki: Step.c = 1..3 -> U(01)..U(03) (U(00) zostaje roboczy dla "wait until speed"). Wybor "Counter 1/2/3"
  w edytorze kroku; tekst kroku dopisuje "on counter N" gdy program uzywa wiecej niz jednego. Potrzebne np. w
  paletyzatorze (paczki w rzedzie + rzedy w warstwie). Kontrola EzsqCheck i emulator licza per licznik.
- Emulator: "When the count reaches N" porownuje == (jak "if U(0x) = N" w falowniku), wczesniej >=.
- Nowe wzory (EzsqSteps.presets): pallet, turner, turnsecond, holdend, wrapper, seq2, speed2, mix3, stir.
  Wszystkie zlozone z istniejacych krokow, kod bajtowy ten sam generator. Wejscia X0..X3, wyjscia Y0..Y1.
- Drugi falownik: Y0 (run) i Y1 (wybor predkosci) drugiego falownika sa podlaczone do terminali wejsciowych drugiego
  falownika; jego terminale trzeba ustawic recznie w tym falowniku. Wzor tylko steruje wyjsciami.
- Niesprawdzone: etykiet w jednym programie bywa do 11 (wrapper); limit etykiet w EzSQ nie jest znany -
  wczesniejsze wzory mialy do 3. Dluzsze wait (do 300 s) zmieszczone w polu 16-bit (30000 x 10 ms).

## 2026-11-12 APP 0.98.85: PRG jako stop, Start na IN2, wpisywanie liczb
- Test uzytkownika na WL200: terminal PRG zwarty na stale = program dziala; rozwarcie zatrzymuje program i silnik; ponowne zwarcie startuje od poczatku; po zasilaniu przy zwartym PRG program startuje sam.
- Decyzja uzytkownika: PRG na stale na terminalu 1 (X(00), C001 = 82), styk NC = Stop; Start = terminal 2 (X(01)); terminale 3..7 (X(02)..X(06)) wolne dla programu. Czujniki analogowe (XA) i porownania < > odlozone.
- A017 teraz = 1 (zamiast 2): program NIE startuje sam po zasileniu bez PRG, a przy zwartym PRG czeka na Start. 'Set the drive up' ustawia C001 = 82, A017 = 1 i C002.. dla uzywanych wejsc.
- Programy z czujnikami (sensorpulse, index, shuttle, pump, jamclear, cycle, pallet, turner, turnsecond, holdend) maja na poczatku dwa kroki: czekaj az IN2 off, czekaj az IN2 on; wszystkie ich wejscia przesuniete o +2 (IN3...). Programy typu 'start/wlacznik' (oneshot, batch, warmup, mix3, stir, seq2, speed2, wrapper) maja X0 -> IN2 (Start), reszta +1.
- Kontrola EzsqCheck: uzycie IN1 w kroku = blad; brak kroku czekajacego na Start = ostrzezenie.
- Nowy preset 'mixer' (29 krokow): IN2 start, IN3 praca ciagla, IN4 20 s/10 s, IN5 20/20, IN6 20/30, wybor czytany miedzy cyklami; stop = PRG.
- Pola liczbowe: czas 0.01..3600 s (dluzsze niz 300 s dzielone na kilka wait po max 300 s), Hz 0.5..400, liczba cykli 1..9999, wpisywane z klawiatury.
- Niesprawdzone: zachowanie wyjsc Y po rozwarciu PRG, rampa vs wybieg przy zatrzymaniu PRG, wait > 300 s (dzielone).

## 2026-11-12 APP 0.98.86: informacja zwrotna przyciskow EzSQ
- Uzytkownik potwierdzil na WL200: po "Set the drive up" program dziala (PRG zwarty, Start na IN2).
- Pasek postepu zapisu: animacja 2 s niezalezna od prawdziwego zapisu; wynik czeka na koniec animacji.
- Miganie ramek przy Set up/Start/Stop/Check wynikalo z globalnego busy (BusyBar + wylaczenie przyciskow na kilka ms). Te cztery komendy dzialaja teraz na osobnej fladze i nie ruszaja busy; zapis/odczyt/klon programu nadal przez busy.
- Nieznane: po zapisie programu A017 zostaje 0 (aplikacja wylacza program przed zapisem) - trzeba "Set the drive up"; do rozwazenia automatyczne przywrocenie A017.

## 2026-11-13 APP: 0.98.87
Write-to-drive = write + set up (A017=1 restored); animations 1 s. No interface change.

## 2026-11-13 APP: 0.98.88
New presets only (confirmed opcodes); no interface change.

2026-11-14 (APP) - Danfoss FC 301/302: aplikacja 0.99.12 laczy sie przez Box po RS-485 (ch0, tryb FC) i przez USB telefonu; Auto rozpoznaje FC 302 (15-98). USB hosta Boxa (ch3) nie obsluguje HID Danfossa (INFO usb=none przy wpietym FC 302) - zlecono BOX APP-018 (diagnostyka VID:PID + backend HID). Interfejs Box<->aplikacja bez zmian do czasu odpowiedzi BOX. Nieprzetestowane na stole.
## 2026-11-14 BOX firmware 0.9.2: Danfoss FC przez USB host (kontrakt 1.7, APP-018)
- Powod: uzytkownik wpial FC 302 do portu USB Boxa (INFO usb=none); Box rozumial tylko Hitachi (04A4) i adaptery USB-szeregowe.
- Decyzja: ch3 rozpoznaje po VID urzadzenie Danfoss (1E46 dowolny PID albo 134D:FC30) i wystawia FC_REQ/FC_BATCH/FCJ z ch=3 (HID, raporty 64 B), bez zmiany ramek i bez konfiguracji kanalu. Flaga INFO dfhid=1. usb= pokazuje VID:PID takze urzadzen nieobslugiwanych (VID:PID/unsup), konsola wypisuje deskryptory.
- Ograniczenie: odpowiedz dluzsza niz jeden raport (15-98) = tylko pierwszy raport, BCC nie sprawdzany (jak aplikacja na USB telefonu). Telegram do 62 B.
- Status: NAPISANE, nieskompilowane i niesprawdzone na sprzecie. Aplikacja ma zapas: USB telefonu.
2026-11-14 (APP) - 0.99.13: Danfoss na ch3 Boxa (BOX-021) wdrozone w aplikacji, bez zmian kontraktu; zamkniete stare zadania MODBOX-001..003 i BOX-004 w inbox/APP.md (kopia inbox/APP.md.bak20261114). Nieprzetestowane na sprzecie.
2026-11-14 (APP) - Bilwinco Q20: cel uzytkownika = nowa plyta ma dzialac (Main program + PLC, juz w Restore). Lista produktow (PROD) = dodatek, tylko jesli sie uda (wymaga nagrania zapisu na plycie bez produktow). Zapis samego RAM nie jest potrzebny (decyzja uzytkownika); backup RAM zostaje jako kopia ustawien. Bez zmian w kodzie.

## 2026-11-15 APP: Bilwinco PROD write
Protokół PROD rozkodowany z przechwytu (RAM: head@0x500, free-block ptr@0x508, size@ptr+4; rekordy na końcu wolnego bloku; komenda L 4C nn addr data). Zapis w aplikacji tylko dla płyty bez listy produktów; głowa listy ustawiana na końcu (bezpieczniej niż w oryginale). Wersja 0.99.16.

- 2026-11-16 WWW: tresc strony odswiezona do aplikacji 0.99.42 (opublikowana jest 0.97.9). Nowe funkcje z buildow 0.98-0.99 (Setup, Drive converter, EzSQ, Bilwinco, OP17 odczyt panelu, FC 302, E800, SJ200, Nameplate AI) sa na stronie z dopiskiem "next release", z etykietami wg STATUS (Draft / In field testing). Firmware Boxa na /modbox.html zostaje 0.9.1: 0.9.2 jest nieskompilowany i nieprzetestowany, nie publikujemy. Polityka prywatnosci: Nameplate "Read with AI" wysyla zdjecie do Google Gemini z kluczem uzytkownika. Bez zmian w kontrakcie.

- 2026-11-17 WWW: (1) Strona wyrownana do aplikacji 0.99.52 (opublikowana stabilna, versionCode 427); usuniete dopiski "next release". (2) Poprawka wpisow: pobieranie APK dziala od 2026-10-26, nie jest zablokowane (stare notatki "do unlock" nieaktualne). (3) SEO: 175 podstron kodow bledow + strony parametrow dla 4 falownikow, razem 222 strony. (4) Pinterest @servmodpins, domena zweryfikowana, narzedzie do pinowania w menu AI Business System [PS]. (5) Backend: /api/latest.apk ma zapasowe czytanie publicznego /servmod/version.json (404 wczesniej; przyczyna na serwerze niezweryfikowana). Zmiany w kontrakcie: nie. Zlecenie dla APP: WWW-006.

- 2026-11-17 WWW (decyzja wlasciciela): cena Pro bez zmian; Subskrypcja = dodatek tylko dla posiadaczy Pro, nie do kupienia bez Pro. Backend: /api/shop/checkout dla "sub" zwraca 403 z `detail`, gdy brak Pro (sesja z Pro albo Device ID z aktywna licencja Pro); test dodany (22 testy). Strona: cennik, Terms, Licence i teksty glowne przepisane. Odrzucona propozycja z recenzji Groka o zmianie modelu. Zlecenie dla APP: WWW-007. Zmiany w kontrakcie: nie.

- 2026-11-17 WWW (decyzja wlasciciela): Nameplate (zdjecie do Google Gemini, wlasny klucz) zostaje; strona opisuje je jako opcjonalna funkcje online obok kopii w chmurze ("Offline by default" zamiast "Nothing leaves the phone"). Cennik: usuniete nieaktualne teksty "ordering not open yet" (sklep dziala). Zlecenie dla APP: WWW-008. Zmiany w kontrakcie: nie.

- 2026-11-17 WWW: wlasciciel potwierdza, ze oba Boxy (DevKit i mini) dzialaja z firmware 0.9.2; strona zostawia Box na rowni z adapterem w schemacie "How it connects", a notka statusu na /modbox.html mowi, ze oferowane pliki to nadal 0.9.1. Zlecenie dla BOX: WWW-009 (pliki 0.9.2 + firmware.json). Zmiany w kontrakcie: nie.

## 2026-11-19 WWW: czat asystenta na stronie (Ollama przez tunel, wlaczony), firmware Box 0.9.2 przygotowany do publikacji (czeka na publish_box_firmware.cmd), /servmod/latest.apk naprawione, home/galeria/hero odswiezone. Kontrakt bez zmian.

## 2026-11-19 (APP): Google Play obok APK ze strony - kierunek
- Uzytkownik: konto osobiste (bez firmy), wariant A: ten sam applicationId (com.servmod.app) i ten sam klucz podpisu w APK ze strony i w Play (klucz do Play App Signing przez eksport PEPK - decyzja wlasciciela potwierdzic przy zakladaniu konta), wspolna numeracja versionCode.
- Wymog Play dla nowego konta osobistego: test zamkniety, 12 testerow, 14 dni z rzedu. Testerzy maja tylko byc zapisani, nie musza testowac codziennie (do potwierdzenia w Play Console).
- Kolejnosc prac: warianty web/play w buildzie, Photo Picker (SlowMo), targetSdk 36, AAB; Play Billing dopiero po decyzji o wejsciu w Play. Zmian w kontrakcie: nie. Szczegoly: claude/servmod-google-play-prep-2026-11-19.md.

## 2026-11-19 (APP): konto Google Play Console zalozone
- Uzytkownik zalozyl konto dewelopera Google Play (typ: osobiste, 17:41). Nazwa dewelopera, adres kontaktowy, tozsamosc i platnosc wpisal sam.
- Model przychodow zadeklarowany w Play: zakupy w aplikacji i subskrypcje (nie aplikacja platna z gory). Kategorie ograniczone: brak ("None of the above").
- Do zrobienia przez wlasciciela w Play Console: dokonczyc weryfikacje (tozsamosc, telefon, ewentualnie weryfikacja fizycznego urzadzenia z Androidem), zebrac 15-25 adresow Gmail testerow na test zamkniety (12 testerow, 14 dni z rzedu).
- Do zrobienia przez APP: warianty web/play, Photo Picker, targetSdk 36, AAB, potem Play Billing. Zmian w kontrakcie: nie.

## 2026-11-19 (wieczor) Google Play: wariant A potwierdzony, przygotowujemy bez publikacji
- Wlasciciel: ten sam klucz podpisu (wariant A, eksport PEPK servmod-release.jks), przygotowac wszystko, NIE publikowac w Play na razie.
- Wykonane: warianty web/play (0.99.57), targetSdk/compileSdk 36 (0.99.58), AAB wariantu play, skrypt tools\play_export_key.cmd (eksport klucza do Google; wlasciciel sam wpisuje hasla; plik jks i hasla nie opuszczaja PC), szkic karty sklepu docs\play_store_listing_draft.md, zlecenie APP-024 dla WWW (polityka prywatnosci i usuwanie danych).
- Czeka: weryfikacja tozsamosci Google; polityka prywatnosci (WWW); Play Billing (APP+WWW) dopiero po decyzji wlasciciela o wejsciu do Play; konto testerow (12 osob x 14 dni) przed produkcja.

## 2026-11-20 WWW: polityka prywatnosci i usuwanie danych pod Google Play
- Dodane strony /app-privacy.html (wersja Play) i /delete-data.html; poprawiony /privacy.html (wersja ze strony). terms.html bez zmian do decyzji wlasciciela. Kontrakt bez zmian.
- Czat na stronie: odpowiedzi tylko po angielsku (retry po CJK), fakty o APK, dluzsze odpowiedzi, endpoint rozgrzewki /api/chat/warm (nie jest czescia KONTRAKT).

- 2026-11-20 APP: DECYZJA uzytkownika: testerzy Play zostaja na 0.99.67 (442) przez caly test. 0.99.70 (445; okna edycji + wifi required=false) wgrywamy dopiero przy nastepnej aktualizacji w produkcji. Przyciski Close/Write w tytule okna zaakceptowane (zrzut z telefonu).

## 2026-11-24 (APP, decyzja uzytkownika): nowe marki i falowniki dodajemy jako profil JSON, jesli JSON jest lepszy niz Kotlin (Modbus RTU na wspolnych ekranach). Istniejacy kod Kotlin, ktory nie przeszkadza, zostaje bez zmian i nie jest przenoszony. Kotlin tylko gdy JSON nie wystarcza (CAN, USB HID, protokol FC Danfoss, FC0F, wlasne sumy kontrolne), z uzasadnieniem w STATUS. Cel: ujednolicenie kodu aplikacji, nie wygladu. Opis: claude/servmod-zasada-nowe-marki-json.md.

## 2026-11-24 (APP, decyzja uzytkownika): USB Tools zostaje dla pendrive'ow i kart SD (FAT). Sterownik NTFS/exFAT nie powstaje, zakladka Disk (SMART) bez dalszych prac. Opis: claude/servmod-status-2026-11-24.md.

## 2026-11-20 WWW: lista oczekujacych usunieta (decyzja uzytkownika)
- Wlasciciel: nikogo nie ma na liscie, usunac calosc. Usuniete: strona /waitlist.html, formularze i linki, pole w koncie, blok wysylki w panelu admina, endpointy /api/waitlist* i /api/admin/waitlist/notify, tabela waitlist (DROP przy starcie). Kontrakt bez zmian (endpointy nie byly w KONTRAKT).

## 2026-11-24 WWW: odswiezenie tresci strony (APP-027)
- Strona opisuje aplikacje 0.99.55 (feed); nowsze pozycje (FC 51, Setup VLT 2800/FC 302, Parts FIND BY PHOTO) maja etykiete Next release i "not yet tried". Brakujace opisy zlecone w WWW-011. Zmian w kontrakcie: nie.

## 2026-11-25 APP: zmiana zasady jezyka
UI aplikacji moze byc tlumaczone (start: polski, mechanizm assets/i18n/<jezyk>.json + tr()). Opisy parametrow w JSON zostaja po angielsku. Strona WWW bez zmian.

## 2026-11-26 APP: Google Play Billing (kontrakt 1.8, PROJEKT)
- Ceny bez zmian (Pro GBP 40 jednorazowo, Subscription GBP 20/rok), ten sam kod WL1 i licencja offline. Wariant `play` kupuje przez Google Play Billing; wariant `web` bez zmian (Stripe/PayPal).
- Zadnych uploadow do Google przed uzyskaniem dostepu do produkcji (nie zaklocamy trwajacego testu zamknietego). Kod i serwer przygotowane lokalnie; testy platnosci na sciezce Internal testing po dostepie do produkcji.
- Serwer servmod.com weryfikuje token zakupu i wydaje kod (APP-031 w inbox WWW). Wymaga konta serwisowego Google i konta platnika w Play Console (dzialanie wlasciciela).

## 2026-11-26 APP: Play Billing, zmiana zasady urzadzen
Zakup w Google Play jest przypisany do konta Google i mozna go przywrocic na innym telefonie (jak w innych aplikacjach). Zamiast "jeden zakup = jedno urzadzenie": ten sam zakup daje kod na kazdy telefon z tym kontem Google (limit proponowany 5). Kontrakt 1.8 i APP-031 poprawione.

## 2026-11-26 APP: limit urzadzen Play
Limit 3 urzadzenia na zakup Google Play; wiecej tylko przez support (decyzja uzytkownika). KONTRAKT 1.8 i APP-031 poprawione.

## 2026-11-26 APP: licencja Play offline
Licencja zawsze dziala offline (kod WL1 sprawdzany lokalnie). Brak odpytywania Google przy starcie w celu zdjecia licencji po zwrocie. Google/serwer tylko przy zakupie, przywracaniu, odnowieniu subskrypcji.

## 2026-11-26 WWW: FC 302 przez Box, APP-027 domkniete, APP-031 (Play redeem) lokalnie
- Wlasciciel potwierdzil: Danfoss FC 302 przez Box dziala. Strona i firmware.json poprawione (BOX musi poprawic wlasny wiersz w STATUS).
- APP-027 zamkniete (Werma, Charger, Appearance, Terminals, ICE, Setup photo w prywatnosci).
- APP-031: endpoint /api/shop/play/redeem napisany wg KONTRAKT 1.8 na galezi play-billing (nie na main), bez klucza dziala jako dry-run 503. Wdrozenie dopiero na zgode wlasciciela i po kluczu konta serwisowego Google. Zmian w kontrakcie: nie.

## 2026-11-27 WWW: APP-032 (Play Billing, przygotowanie wdrozenia)
- Potwierdzone z APP: produkty servmod_pro (buy) i servmod_sub (yearly), sub czytany z subscriptionsv2 po tokenie bez basePlanId; 3 dni zapasu zostaja; dwa kody (PRO i SUB) OK; IN_GRACE_PERIOD = nieaktywna.
- Galaz play-billing dostala tools/install_play_key.cmd (klucz JSON konta serwisowego -> /etc/servmod/play-key.json, chmod 640 root:servmod, PLAY_KEY_FILE w pay.env, restart uslugi, test 400/503). Instrukcja testowa i wycofania w inbox/WWW.md (Wynik APP-032). NIE zmergowane do main, produkcja nietknieta; merge dopiero na zgode wlasciciela po zalozeniu konta serwisowego. Zmian w kontrakcie: nie.

## 2026-11-27 (APP): Play Billing, doprecyzowanie KONTRAKT 1.8 po APP-032
- Subskrypcja Play: kod WL1 SUB:RRRRMMDD z końca okresu PLUS 3 dni zapasu offline (wymagania bezpieczeństwa pkt 7 mają pierwszeństwo przed zdaniem "bez dodatkowych dni" w opisie endpointu; PLAY_SUB_GRACE_DAYS=3). Brak zmiany interfejsu, tylko poprawka opisu.
- Play Console 2026-11-27: aktywne `servmod_pro` (UK £40.00 z VAT) i `servmod_sub` (plan `yearly`, UK £20.00 z VAT); poza UK Play dolicza lokalny podatek (decyzja właściciela: zostaje). Aplikacja 0.99.184 (Billing Library 8.0.0) na Internal testing.
- Wdrożenie serwera (gałąź `play-billing`, commit c0b4790) dopiero na "merge play" właściciela, po założeniu konta serwisowego. Klucz wgrywa właściciel przez tools\install_play_key.cmd (po merge).

## 2026-11-27 WWW: merge play-billing do main (zgoda wlasciciela: "merge play")
- Galaz play-billing zmergowana do main (commit 6ae77fa), 25 testow przechodzi, push zrobiony. Serwer pobral zmiany: POST /api/shop/play/redeem odpowiada 503 "not configured" (dry-run), /api/health 200. Brak klucza Google = nic sie nie wydaje.
- Zostaje po stronie wlasciciela: konto serwisowe Google + powiazanie w Play Console, potem tools\install_play_key.cmd. Zmian w kontrakcie: nie.

## 2026-11-27 WWW: install_play_key na PC
- Wlasciciel poprosil o kopie skryptu: install_play_key.cmd i .ps1 skopiowane do ServMod\web\install_backend\ i ServMod\web\tools\ (wzor: install_paypal_keys). Klon repo WWW lezy w kontenerze Claude (/home/claude/servmod-site, galaz main, 6ae77fa), nie na PC; na PC jest tylko katalog web\ z kopiami skryptow. Zadania APP-034 w inbox/WWW.md nie znaleziono (ostatnie to APP-033).

## 2026-11-28 WWW: panel admina na stronie uporzadkowany (prosba wlasciciela)
- /account/ (admin): zakladki Licences, Requests, Support, Visits, Grant; licencje w folderach (Web shop, Google Play, Granted, Revoked, No licence) po 25 + "Show more"; wyszukiwarka po e-mailu, Device ID, id Google Play (play-...), skrocie zakupu Play, numerze zamowienia lub numerze licencji (#12). Usuwanie: tylko odwolane licencje i konta bez licencji (zamowienia zostaja, wpis w audycie). Nowe endpointy tylko dla admina, KONTRAKT bez zmian (nie dotyczy aplikacji).
