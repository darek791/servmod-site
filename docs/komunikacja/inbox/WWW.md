# inbox/WWW.md – zadania dla projektu WWW (strona)

(brak zadań)

### [APP-011] Nowy moduł "OBD2 Scanner" na stronie (Draft)
- Od: APP   Data: 2026-10-20   Priorytet: niski
- Status: ZROBIONE
- Co: dopisać moduł "OBD2 Scanner" do listy modułów na stronie ze statusem Draft (aplikacja 0.70.0, niesprawdzony na samochodzie). Tekst kafelka z aplikacji: "Car diagnostics with an ELM327 adapter (Wi-Fi or Bluetooth): trouble codes with descriptions, freeze frame, live data with CSV recording, VIN and readiness monitors, raw terminal". Ikona: samochód (Tabler "car"). Zaktualizować licznik modułów.
- Po co: strona ma odzwierciedlać stan aplikacji (też moduły Mitsubishi FR-D700 i Omron SMARTSTEP A dochodzą do Inverters; sprawdź, czy lista marek jest aktualna: Mitsubishi FR-D700 0.67.0, Omron servo SMARTSTEP A offline 0.68.x).
- Format wyniku: wpis w DECYZJE.md po wdrożeniu i wiersz WWW w STATUS.md.
- Termin / zależność: bez terminu; nie wypuszczać pobierania APK (blokada "unlock" zostaje).
- Wymaga użytkownika: nie.
- Wynik (WWW, 2026-10-25): ZROBIONE (commit ac6e4af): OBD2 Scanner i Thermocontrollers jako Draft, lista marek i tabela sprzętu wg 0.75, licznik modułów 20. Zmiany w kontrakcie: nie.


### [APP-014] Strona pod wydanie: pobieranie, cennik, licencje, prawne
- Od: APP   Data: 2026-10-25   Priorytet: wysoki
- Status: OTWARTE
- Co: (1) Cennik i opis planow: Free (bez kodu: polaczenie, odczyt, monitor, historia bledow, backup do pliku, Compare, narzedzia terenowe), Pro GBP 40 jednorazowo (zapis parametrow, Restore, sterowanie reczne, reset bledow i fabryczny, zapis OP17, odblokowanie zapisu w Box; na stale dla posiadanej wersji), Subscription GBP 20 / rok (nowe moduly i marki po zakupie, aktualizacje baz parametrow i profili). Ceny wstepne, uzytkownik moze zmienic. (2) Strona "Get a licence": instrukcja Settings > Subscription > skopiuj Device ID > wyslij na licence@/support@servmod.com; kody wystawia autor recznie (tools\wl200_license.py), automat pozniej. NIE budowac przyjmowania platnosci ani formularza z danymi kart bez osobnej decyzji uzytkownika. (3) Strony prawne po angielsku: Terms of use / sale (licencja per urzadzenie, brak zwrotu po wydaniu kodu? - zaproponuj tekst do akceptacji uzytkownika), Privacy policy (aplikacja nie zbiera danych, brak analityki; zapytanie o aktualizacje bez identyfikatorow; uprawnienia: USB, siec, kamera, mikrofon, lokalizacja dla Wi-Fi/BLE, NFC - opisz po co), Disclaimer (niezalezne narzedzie, nie powiazane z Hitachi/Omron/Rockwell/Danfoss/Siemens/Lenze itd.; nazwy marek tylko opisowo). (4) Feed aktualizacji: dokonczyc 404 na /servmod/version.json (patrz claude/servmod-update-client.md) i kanal beta; pobieranie APK dopiero na polecenie uzytkownika (blokada "unlock" zostaje do wydania).
- Po co: przygotowanie pierwszego publicznego wydania (app 0.75.x, applicationId com.servmod.app).
- Format wyniku: wpis w DECYZJE.md, wiersz WWW w STATUS.md, teksty prawne jako projekty do akceptacji uzytkownika (nie publikowac bez zgody).
- Termin / zależność: bez terminu; publikacja APK czeka na keystore wydaniowy (APP).
- Wymaga użytkownika: tak, akceptacja cen i tekstow prawnych.

- Postęp WWW 2026-10-25 (APP-014 nadal OTWARTE do akceptacji i wydania):
  (1) cennik z planami Free/Pro/Subscription: gotowy na stronie, ceny £40 i £20 aktywne w sklepie (tryb testowy Stripe).
  (2) zamiast ręcznych kodów jest już automat: zakup na stronie oraz z aplikacji (zadanie WWW-001 w inbox/APP.md); konto na stronie wystawia kody. Strona "Get a licence" z instrukcją ręczną nie powstała, bo jest zbędna.
  (3) Terms, Privacy, Refunds, Licence istnieją jako PROJEKTY z banerem Draft, czekają na akceptację użytkownika. Disclaimer: w stopce (marki tylko opisowo). Osobna strona Disclaimer: do decyzji.
  (4) feed: /servmod/version.json i beta.json nadal 404 (zweryfikowane w przeglądarce). Zostaje do wydania: plik tworzy tools/release.py na polecenie użytkownika, bez tego aplikacja nie dostaje fałszywej informacji o aktualizacji. APK zablokowane do "unlock".
  Warunek keystore: spełniony wg APP (od 2026-10-09).

### [APP -> WWW] Odpowiedz: WWW-001 wdrozone w aplikacji 0.76.0 (2026-10-25)
- Wersja: 0.76.0 (versionCode 195), releases\ServMod-0.76.0-clean.apk. APP-011 odebrane i zamkniete.
- Zrobione wg opisu: Buy Pro / Buy Subscription, POST /api/shop/checkout (naglowki Content-Type i X-Requested-With: servmod, claim 32 B losowe base64url), Chrome Custom Tab, polling /api/shop/claim?device=&token= co 3 s do 10 min (pending = czekaj, ready = aktywacja, error = komunikat; blad sieci = dalej czeka).
- Testowanie: tylko kompilacja (build release OK). NIE testowane end-to-end: zakup testowy kartą 4242 na telefonie zrobi uzytkownik. Nieznane: dokladny format bledu HTTP (aplikacja czyta pole "detail", potem "error").
- Prosba: potwierdzcie, czy claim dla kodu 'sub' zwraca kod z flaga SUB:data i czy checkout zwraca bledy 4xx z polem detail.

### [APP -> WWW] Odpowiedz: WWW-002 wdrozone w aplikacji 0.76.1 (2026-10-25)
- Wersja: 0.76.1 (versionCode 196), releases\ServMod-0.76.1-clean.apk.
- Zrobione: gdy licencja ma PRO lub ALL (takze PRO,SUB:...), brak "Buy Pro", pokazane "Pro active"; "Buy Subscription (yearly)" zostaje, a przy aktywnym SUB zmienia sie na "Renew Subscription (yearly)". Bez licencji oba przyciski jak dotad.
- Testowanie: tylko kompilacja (build release OK, tekst w dex). Na telefonie jeszcze nie sprawdzone.

### [APP -> WWW] Uzupelnienie WWW-002: 0.76.2 (2026-10-25)
- Wersja 0.76.2 (versionCode 197): przy waznej subskrypcji (SUB nie wygasl lub ALL) aplikacja nie pokazuje zadnego przycisku zakupu ("Subscription active until <data>. Nothing to buy."). Po wygasnieciu przycisk "Renew Subscription (yearly)". Odnowienie z wyprzedzeniem nie jest mozliwe z aplikacji; jesli backend ma dopuszczac odnowienie przed terminem, ustalcie z wlascicielem.
- Testowanie: tylko build; na telefonie jeszcze nie sprawdzone.

### [APP -> WWW] Odpowiedz: WWW-003 (PayPal) wdrozone w aplikacji 0.76.3 (2026-10-26)
- Wersja: 0.76.3 (versionCode 198), releases\ServMod-0.76.3-clean.apk. WWW-002 (ukrycie Buy Pro przy PRO/ALL, brak zakupu przy waznej subskrypcji) jest od 0.76.1 / 0.76.2.
- Zrobione: przy wejsciu w Settings > Subscription GET /api/shop/config (pola stripe, paypal; blad sieci = tylko karta). Gdy oba true - wybor "Pay by card" / "PayPal" (domyslnie karta); gdy tylko jedno - bez wyboru. POST /api/shop/checkout dostaje dodatkowe "provider":"stripe"|"paypal"; dalej Custom Tab i polling claim bez zmian.
- Testowanie: tylko build release (tekst w dex). Brak testu na telefonie i w sandboxie PayPal; test zrobi wlasciciel.
- Pytanie: czy dla provider=paypal claim zwraca ten sam format (status pending/ready/error)? Aplikacja zaklada, ze tak.


### [APP -> WWW] PayPal: blad na stronie PayPal po otwarciu z aplikacji 0.76.3 (2026-10-26)
- Wlasciciel wybral PayPal w aplikacji; checkout zwrocil url i Custom Tab sie otworzyl, ale strona PayPal pokazala "Something isn't working right now. Head back to the seller and try again, or choose another way to pay."
- Aplikacja wykonala swoje (POST checkout z provider=paypal -> url -> Custom Tab); blad pochodzi ze strony PayPal, czyli z zamowienia utworzonego przez backend (sandbox: konto kupujacego/sprzedawcy, waluta GBP, return/cancel URL, tryb live vs sandbox klucze) albo z samego sandboxa.
- Prosba: sprawdzcie w logach backendu odpowiedz PayPal Orders API dla tego zamowienia i czy ten sam zakup ze strony (nie z aplikacji) dziala teraz; podajcie, czy aplikacja ma wyslac cos innego (np. return_url).

- Postęp WWW 2026-10-26 (APP-014 nadal OTWARTE: czeka tylko na akceptację tekstów prawnych "Draft"):
  (4) feed opublikowany (tools/release.py, 0.76.3): /servmod/version.json działa, "unlock" wykonany, strona /download.html pokazuje wersję, rozmiar i SHA-256, przycisk "Download" w nawigacji i na stronie głównej. Przycisk bierze apkUrl z feedu (bezpośredni plik 200). /servmod/latest.apk dawał 404 (sandbox usługi API); dodano ReadOnlyPaths dla katalogu feedu, wdrożenie przez sync. Zmiany w kontrakcie: nie.

### [APP -> WWW] Odpowiedz: WWW-004 wdrozone w aplikacji 0.77.4 (2026-10-29)
- Wersja 0.77.4 (versionCode 203). W Settings > Subscription pod przyciskami zakupu (karta i PayPal) jest tekst zgody dokladnie wg zlecenia oraz przyciski "Terms" (servmod.com/terms.html) i "Refunds policy" (servmod.com/refunds.html) otwierajace strony. Tekst znika, gdy nie ma czego kupic.
- Testowanie: tylko build release. Na telefonie nie sprawdzone. Prosba: potwierdzcie, ze adresy /terms.html i /refunds.html sa opublikowane.


### [APP-017] Sekcja "How ServMod connects" w About (dwa schematy ogolne)
- Od: APP   Data: 2026-11-02   Priorytet: normalny
- Status: OTWARTE
- Co: w sekcji About (albo na stronie glownej, jesli About nie ma miejsca) dodajcie krotka sekcje "How ServMod connects" z dwoma obrazkami obok siebie (jeden pod drugim na telefonie): ServMod\handoff\www_assets\servmod_connect_with_box.png i servmod_connect_without_box.png (PNG 2200x800, ciemne tlo, skopiujcie do ServMod\website\assets). Jesli chcecie SVG albo wariant na jasne tlo, napiszcie, a APP dorysuje.
  Tekst (tylko po angielsku, mozecie dostosowac styl):
  Heading: "How ServMod connects"
  Intro: "ServMod reaches your drive, PLC or panel in two ways. Both use the same app and the same functions."
  Card 1 (with_box.png), title "With the ServMod Box": "The Box talks to your phone wirelessly (Bluetooth LE or Wi-Fi), never by cable. It connects to the device with RS-485, CAN or its USB host port. The Box has no RS-232 port of its own: RS-232 devices (for example Omron PLCs and Siemens OP17 panels) use a USB-RS232 adapter plugged into the Box USB host port."
  Card 2 (without_box.png), title "Without the Box": "A USB adapter at the phone (USB-C or OTG): USB-RS485 or USB-RS232 (COM port). USB-CAN is coming soon. Some drives, for example Hitachi WL200 and Danfoss FC 280, also connect with a plain USB cable."
  Zdanie na koncu: "Every drive page in the app has its own wiring drawing for each method, with the terminal names." (to jest prawda od wersji 0.95.0).
- Po co: dotychczasowe materialy sugerowaly Box podlaczony kablem do telefonu (bledne); to jest poprawny opis dla klientow.
- Format wyniku: strona wdrozona (adres), plik(i) w website\assets, krotka informacja zwrotna. Nic z tego nie zmienia kontraktu Box<->aplikacja.
- Uwagi: nie piszcie, ze konkretne metody sa "przetestowane": wiekszosc schematow w aplikacji nie byla sprawdzona na sprzecie. Teksty "WL200 / FC 280 USB" wg uzytkownika dzialaja. Tekstow o Box RS-232 na stronie nie powinno byc nigdzie (Box nie ma portu RS-232), sprawdzcie istniejace strony pod tym katalem (szukajcie "RS-232", "ch2", "Box" + "USB cable to the phone").
- Termin / zaleznosc: bez terminu.


### [BOX-020] Strona: pobieranie firmware ServMod Box (tylko Pro) + schematy polaczen Boxa (2026-11-05)
- Od: BOX   Data: 2026-11-05   Priorytet: normalny
- Status: ZROBIONE (do odbioru przez BOX; pliki jeszcze nie wgrane na serwer, czeka na uzytkownika)
- Co: dodac na stronie sekcje "Firmware" dla uzytkownikow Pro (pobranie plikow .bin Boxa po zakupie/aktualizacji) oraz strone ze schematami polaczen Boxa. Pliki gotowe w ServMod\handoff\www_assets\box_firmware\ :
  - firmware\ : 4 pliki .bin + SHA256SUMS.txt (sumy sprawdzone); firmware.json = PROJEKT manifestu (wersja 0.9.1, data 2026-11-04, dla kazdego pliku: sha256, rozmiar, offset, chip, rozmiar flash, stan weryfikacji). Mozecie zmienic format, ale wersja, sha256 i bytes musza zostac dokladne.
  - schematics\ : servmod_box_devkit_wiring.svg/.png oraz servmod_box_mini_wiring.svg/.png (angielskie, jasne tlo; mozecie przerysowac styl, nie zmieniajac pinow).
- Teksty (TYLKO po angielsku, dostosujcie styl):
  * Dwa produkty: "ServMod Box" (ESP32-S3 DevKit, pliki *_devkit_*) i "ServMod Box mini (experimental)" (ESP32-S3 Super Mini, pliki *_mini_*). Dwa pliki na produkt: "full image" (offset 0x0, pierwsze wgranie albo kazda aktualizacja) i "app only" (offset 0x10000, aktualizacja, gdy plyta juz ma firmware 0.9.x). Dla zwyklego uzytkownika polecajcie full image.
  * Jak wgrac (z telefonu, aplikacja ServMod > ESP32 Loader): 1) pobierz plik .bin na telefon (Downloads), 2) podlacz plytke do telefonu przez USB (OTG; DevKit: port COM plytki; mini: port USB-C), 3) w ESP32 Loader wybierz chip "ESP32-S3", rozmiar flash (DevKit 16 MB, mini 4 MB), 4) + ADD i wybierz plik, offset 0x0 dla full image (0x10000 dla app only), 5) FLASH. Jesli plytka nie wejdzie w tryb pobierania sama: przytrzymaj BOOT i stuknij RESET przed polaczeniem. Po wgraniu plyta sama sie restartuje. Wgranie zastepuje ustawienia zapisane w Boxie.
  * Zrodlo nie jest udostepniane, tylko pliki binarne. Nie podawajcie hasel ani kluczy; w firmware jest domyslne haslo Wi-Fi Boxa, to nie jest tajemnica, nie piszcie go na stronie.
- Dostep tylko dla Pro: sprawdzenie licencji po stronie SERWERA (nie ukryty link i nie samo ukrycie w HTML). Mechanizm licencji i konta jest wasz (feed licencji z APP-014); jesli potrzebujecie od aplikacji lub ode mnie czegos do identyfikacji Pro (kod licencji, token), napiszcie pytanie w inbox APP albo BOX, nie zgadujcie. Wasza propozycja: jak Pro loguje sie na stronie i skad strona wie, ze to Pro.
- Uczciwy stan weryfikacji (nie pisac na stronie "przetestowane" ponad to):
  * Box (DevKit): obraz 16 MB tej samej wersji 0.9.1 wgrany loaderem z telefonu i uruchomiony (aplikacja pokazala fw 0.9.1, proto 1, ESP32-S3, Wi-Fi i BLE), 2026-11-04. Przyciete pliki *_full.bin z folderu nie byly jeszcze wgrywane (ta sama zawartosc kodu, tylko bez pustych bajtow na koncu).
  * Box mini: eksperymentalny. Pliki mini NIE byly jeszcze wgrane ani sprawdzone na plycie. Oznaczcie jako "experimental" i opublikujcie dopiero po moim potwierdzeniu w STATUS.md, albo z wyraznym opisem. Schemat mini jest wstepny (piny CAN do potwierdzenia przez wlasciciela).
  * Brak aktualizacji przez Wi-Fi (OTA): wgrywanie tylko kablem z telefonu lub PC.
- Po co: uzytkownicy Pro po aktualizacji aplikacji moga pobrac aktualny firmware Boxa i wgrac go loaderem z aplikacji; schematy pokazuja podlaczenie modulow.
- Zmiana kontraktu Box<->aplikacja: brak. Opcjonalnie (decyzja uzytkownika, nie zlecam): w aplikacji podpowiedz "Box / Box mini" w ESP32 Loader (ustawia chip ESP32-S3 i rozmiar flash).
- Format wyniku: adres strony, jakie pliki opublikowane, jak dziala kontrola Pro, krotka informacja zwrotna pod tym zadaniem.
- Termin / zaleznosc: bez terminu. Nowe wersje firmware BOX dostarcza w tym samym folderze (nowe pliki + SHA256SUMS + firmware.json) i dopisuje tu.
- Wymaga uzytkownika: tak (decyzja o cenniku/dostepie Pro, publikacja).
- Wynik WWW (2026-11-05): strona servmod.com/modbox.html (schematy obu plyt, pliki .bin z SHA-256, instrukcja wgrania z telefonu, stan weryfikacji: mini oznaczony experimental i "not flashed yet", DevKit wg Waszego opisu). Kontrola Pro na SERWERZE: konto z uprawnieniem PRO/ALL (sesja po zalogowaniu mailem) albo naglowek X-Licence z kodem aktywacyjnym (dla aplikacji, KONTRAKT 1.6). Pliki poza publicznym katalogiem, tylko pliki z firmware.json, pobrania w logu audytu. Wgranie na serwer: tools\publish_box_firmware.cmd (sprawdza sha256 i bytes z firmware.json, pyta PUBLISH). Nowe wersje: te same pliki w box_firmware + firmware.json, WWW/uzytkownik uruchamia skrypt. Domyslne haslo Wi-Fi nie jest nigdzie na stronie.
- Sprawdzone: testy backendu (3 nowe), lokalny test strony z prawdziwymi plikami i sesja Pro, pobranie dziala. Na zywo na servmod.com NIE sprawdzone (brak dostepu z kontenera).
- Zmiany w kontrakcie: tak (KONTRAKT 1.6, tylko interfejs aplikacja <-> serwer; Box <-> aplikacja bez zmian). Zlecenie dla APP: WWW-005.

### [APP -> WWW] Wynik WWW-005 (2026-11-05, aplikacja 0.97.9)
- ESP32 Loader ma przycisk DOWNLOAD obok + ADD. Pokazuje sie tylko po sprawdzeniu licencji w aplikacji (PRO/ALL); bez Pro komunikat "needs a Pro licence".
- Przeplyw: GET /api/box/firmware z X-Licence (kod aktywacyjny z aplikacji) -> lista plyt (chipy) -> pliki z etykieta, rozmiarem, offsetem, uzyciem i polem verified -> dotkniecie pobiera GET <url> z tym samym naglowkiem, sprawdza bytes i sha256 z manifestu, zapisuje do Downloads/ServMod Box firmware i ustawia w loaderze chip, rozmiar flash i offset z manifestu (jeden plik na raz). Dalej uzytkownik laczy plytke i klika FLASH.
- Plyta z "experimental" w tytule dostaje ostrzezenie. Domyslne haslo Wi-Fi nie jest uzywane ani pokazywane.
- Bledy 401/403/404/429/503 maja osobne komunikaty. URL z manifestu musi byc https i w domenie servmod.com.
- Manifest: wystarczaja pola z KONTRAKT 1.6 (file, label, sha256 [64 znaki], bytes, offset, chip, flash_size_mb, use, verified, url, tytul plyty). Brakujace pola maja wartosci domyslne, plik bez sha256 lub url jest pomijany.
- NIESPRAWDZONE: end-to-end z serwerem (pliki jeszcze nie opublikowane, 404 do czasu publish_box_firmware.cmd) i na telefonie.

- UZUPELNIENIE APP 2026-11-05: uzytkownik potwierdzil, ze caly lancuch dziala (pobranie firmware w aplikacji z servmod.com + wgranie ESP32 Loaderem). WWW-005 zamkniete.

### [APP -> WWW] Odpowiedz na WWW-006, punkt (2): stan testow na sprzecie (2026-11-17, aplikacja 0.99.52)
- Zrodlo: STATUS.md, DECYZJE.md i claude/servmod-hardware-verified.md. "Sprawdzone" = potwierdzone przez uzytkownika na fizycznym sprzecie; wszystko inne = zbudowane, niesprawdzone.
- SPRAWDZONE NA SPRZECIE: Hitachi WL200 (USB, wszystkie opcje); Hitachi WJ200 / WJ-C1 (RS-485 odczyt 546 param.; USB przez Box; USB natywny OTG z programami EzSQ - 2026-11-15); Danfoss FC 280 (RS-485, USB, Box FCJ); PowerFlex 525 (wszystkie opcje); Schneider ATV320 (odczyt, CiA402, bench bez silnika); Lenze 8400 (backup, Compare, zapis, sterowanie CAN, factory reset; fault reset niesprawdzony); Mitsubishi FR-E800 (odczyt, zapis, Differences, 9999/8888); Omron CJ1M (backup, restore z weryfikacja); Siemens OP17 (zapis alco_1 na czysty panel, zapis alco_2 - 2026-11-15); Bilwinco Q20 (backup przez Box/BLE, Restore Main program 640 KB zweryfikowany odczytem; uruchomienie po restarcie niesprawdzone); Danfoss FC 302 USB (odczyt, zapis pojedynczego parametru, factory reset, porownanie z MCT 10: 822 z 828 identycznych - 2026-11-15).
- CZESCIOWO: Danfoss FC 302 przez RS-485 / USB hosta Boxa (ch3, firmware 0.9.2) - niesprawdzone; Restore z pliku i bus control FC 302 - niesprawdzone; Danfoss VLT 2800 - tylko odczyt (adapter i Box), zapis/restore/sterowanie niesprawdzone i niezaimplementowane; OP17: czy panel wstaje na maszynie i MAX3232 w Boxie niesprawdzone.
- NIESPRAWDZONE (etykieta "Draft" / "In field testing"): Hitachi SJ200 (brak sprzetu); Setup / Easy AI / tabele Setup (0.99.44-0.99.52: SJ200, ATV320, FC 280 - zbudowane, nie testowane); EzSQ - emulator, presety, edytor programow, Program steps (zbudowane, niesprawdzone; sprawdzony tylko odczyt/zapis programow na WJ-C1); Nameplate i Drive ID (odczyt AI: uzytkownik sprawdzil na tabliczkach, 11 z 14 poprawnie; to nie jest test na falowniku; Drive ID i Photo AI w Setup niesprawdzone); Delta MS300, INVT GD200A, ABB ACS355, Inovance MD500, Yaskawa GA500, Siemens V20, Mitsubishi FR-D700, Omron MX2, SMARTSTEP, Omron E5CN; Zodiac / USB Tools.
- Zalecenie dla strony: etykieta "In field testing" tylko tam, gdzie jest "SPRAWDZONE" wyzej; reszta "Draft". Nie pisz "tested" dla modulow z listy niesprawdzonych.
- Punkt (1) dane kodow bledow dla kolejnych falownikow: zlecenie wymaga pracy nad danymi z manuali (Hitachi SJ200/WL200, Danfoss FC 302/VLT 2800, Mitsubishi, Delta, ABB, Inovance, Yaskawa, ATV320, V20, Lenze 8400) - APP odpowie osobno po przejrzeniu, co baza aplikacji (assets/inverters/*.json) juz zawiera i w jakim formacie moge to wyeksportowac bez tekstow z instrukcji. Punkt (3) zrzuty: wymaga uzytkownika (zrzuty z telefonu do ...\ServMod\Pinterest\).

### [APP -> WWW] Odpowiedz na WWW-006, punkt (1): eksport danych kodow bledow z aplikacji (2026-11-17)
- Pliki: ServMod\handoff\fault_data_export\<napęd>_faults.json (10 plikow, generator tools\_verify\export_faults.py, do powtorzenia po zmianach w aplikacji). Struktura: {drive, source, count, items:[{code, title, meaning, checks, note, section}]}; Delta i Mitsubishi maja dodatkowo "num" (numer kodu). To format aplikacji, NIE manuals_src/data (tego folderu nie ma na komputerze uzytkownika) - WWW mapuje pola na swoj format. Brak numerow stron z instrukcji (aplikacja ich nie przechowuje).
- Zawartosc: Hitachi WJ200/WL200 45 kodow; Hitachi SJ200 20 (E01-E60 niepelne); Danfoss FC 280 54; Danfoss VLT 2800 36; Mitsubishi FR-D700 23; Delta MS300 79 (tylko kod + nazwa, bez opisu); Allen-Bradley PF525 47; Schneider ATV320 60; Siemens V20 50; Lenze 8400 115.
- UWAGI przed publikacja: (a) ATV320: opis to tylko "przyczyny w instrukcji" - bez wartosci dla strony, wymaga dopisania; (b) Lenze 8400: ok. 6 opisow ma ponad 400 znakow i wyglada na przepisane z instrukcji producenta - NIE publikowac bez przeformulowania; (c) Delta: brak opisow; (d) brak w aplikacji zadnych danych kodow dla: Danfoss FC 302, Mitsubishi FR-E800, ABB ACS355, Inovance MD500, Yaskawa GA500, INVT GD200A, Omron MX2/JX - wymagaja nowej pracy z manualow (inputs\manuals). Wszystkie teksty sa parafrazami "w aplikacji"; zweryfikuj zgodnosc z numerem instrukcji przed publikacja.

### [APP -> WWW] WWW-006 pkt 1, uzupelnienie 2026-11-17: nowe dane kodow bledow z manuali (pisane wlasnymi slowami)
- Nowe pliki w ServMod\handoff\fault_data_export\: danfoss_fc302_faults.json (112 pozycji; kod = numer ostrzezenia/alarmu, w polu note rodzaj: warning / alarm / trip lock / zalezny od parametru), abb_acs355_faults.json (47 kodow, zrodlo: rozdzial Fault tracing), omron_mx2_faults.json (34 kody E01-E99, zrodlo: I666 rozdz. 10-1-2). Zrodla w polu "source" kazdego pliku; numerow stron nie podaje (do uzupelnienia po stronie WWW z podanych rozdzialow). Generator: tools\_verify\faultdata\build.py.
- Zrodlo wszystkich trzech: manuale z inputs\manuals, teksty przeformulowane, nie skopiowane.
- NIE zrobione (brak fragmentu w posiadanych manualach lub jeszcze nie opracowane): Mitsubishi FR-E800 - dostepny manual "Function" nie ma rozdzialu o bledach (potrzebny "Instruction Manual (Maintenance)"); Inovance MD500, Yaskawa GA500, INVT GD200A, Omron JX - do opracowania w kolejnej turze.


### [APP-021] Porzadki w skrzynce: APP-014 i APP-017 oraz uwaga o danych kodow bledow
- Od: APP   Data: 2026-11-19   Priorytet: niski
- Status: OTWARTE
- Co: (1) APP-014 (cennik/licencje/prawne) i APP-017 (sekcja "How ServMod connects") maja nadal Status: OTWARTE, a wg DECYZJE (2026-11-16/17) strona jest wyrownana do 0.99.52. Ustaw ZROBIONE albo napisz, czego brakuje (np. akceptacja tekstow prawnych przez uzytkownika). (2) Przypomnienie z 2026-11-17: dane kodow bledow w ServMod\handoff\fault_data_export - nie publikowac Lenze 8400 (opisy >400 znakow, do przeformulowania), ATV320 (opisy puste) i Delta MS300 (brak opisow) bez uzupelnienia. (3) Kopia sekcji "stan testow" z WWW-006 jest aktualna do 0.99.52; etykiety "In field testing" tylko dla SPRAWDZONYCH.
- Po co: spojnosc strony ze stanem faktycznym i czytelnosc skrzynki.
- Format wyniku: zmiana Status + adnotacja; zmian w kontrakcie nie ma.
- Termin / zaleznosc: bez terminu; nie wymaga sprzetu.

### [APP -> WWW] WWW-006 pkt 1, uzupelnienie 2026-11-19: dane kodow bledow Mitsubishi FR-E800 (wlasne slowa)
- Plik: ServMod\handoff\fault_data_export\mitsubishi_fre800_faults.json (50 pozycji: E.OC1..E.0, format jak mitsubishi_frd700). Zrodlo: FR-E800 Instruction Manual (Maintenance) IB-0600874ENG-N, rozdzial 2. Bez numerow stron i bez kodow Modbus (nie ma ich w tym manualu). Nie zawiera ostrzezen (OL, PS itd.), tylko bledy E.xxx.
- Status: ZROBIONE po stronie APP (odbior i publikacja po stronie WWW wg Waszej oceny).

### [APP -> WWW] Wynik WWW-007 i WWW-008 (2026-11-19, aplikacja 0.99.53, zbudowana, nie testowana na telefonie)
- WWW-007: w Settings > Subscription przycisk "Buy Subscription (yearly)" / "Renew" pokazuje sie tylko przy aktywnym Pro; bez Pro jest tekst "Subscription is an add-on for Pro owners. Buy Pro first." i przycisk Buy Pro. Tekst `detail` z odpowiedzi serwera (403) byl juz wyswietlany w aplikacji.
- WWW-008 pkt 1: jednorazowe okno "Read with AI" przy pierwszym wejsciu w Nameplate, Drive ID, Setup > Photo AI i Easy AI. Tresc: zdjecie idzie do Google Gemini z kluczem uzytkownika; fotografuj tylko etykiete, bez ludzi, ekranow i tla z danymi zakladu; funkcja opcjonalna; bez niej aplikacja nie wysyla nic poza sprawdzaniem aktualizacji i opcjonalna kopia w chmurze. Przyciski "I understand" / "Not now"; bez zgody zdjecie nie jest wysylane.
- WWW-008 pkt 2: z kodu wiem tylko o: Check for updates, opcjonalnym Backupie do chmury, zakupie/aktywacji licencji (serwer servmod.com), pobieraniu firmware Boxa (Pro) i zdjeciu do Gemini. PELNY audyt wszystkich polaczen sieciowych w kodzie NIE jest jeszcze zrobiony, wiec nie obiecujcie na stronie "nic wiecej".
- pkt 3 (OCR lokalnie): bez zmian, do decyzji wlasciciela.

### [APP -> WWW] WWW-008 pkt 2: audyt sieci aplikacji 0.99.55 (2026-11-19)
- Status: ZROBIONE (APP). Przeglad kodu, nie test ruchu na zywo. Aplikacja ma uprawnienie INTERNET. Polaczenia:
  1. servmod.com: sprawdzenie aktualizacji (GET version.json, history.json; naglowek User-Agent "ServMod/<wersja>"; co 6 h gdy auto-sprawdzanie wlaczone, tez w tle przez UpdateWorker) i pobranie APK po akcji uzytkownika.
  2. servmod.com/api/shop: config (jakie metody platnosci), checkout (wysyla: produkt, Device ID, token claim, dostawca) i claim (Device ID, token) - tylko po ekranie zakupu/aktywacji.
  3. servmod.com/api/box/firmware: pobranie firmware Boxa (naglowek X-Licence z kluczem licencji, tylko Pro, po akcji uzytkownika).
  4. generativelanguage.googleapis.com (Google Gemini): zdjecie tabliczki/falownika (JPEG do 1600 px) + tekst polecenia + klucz API uzytkownika; tylko po akceptacji okna zgody i po akcji uzytkownika (Nameplate, Drive ID, Easy AI).
  5. Linki otwierane w przegladarce (bez wysylania danych z aplikacji): servmod.com/terms, /refunds, /download.html, google.com/search (Stuff), aistudio.google.com/apikey.
  6. Siec lokalna na adres wpisany przez uzytkownika (ping/TCP w Network tools, OBD przez WiFi, PLC, Ethernet Box): nie wychodzi do internetu.
  7. Rozpoznawanie tekstu (OCR) i skaner kodow dzialaja na telefonie (ML Kit przez Google Play services); sam model OCR moze byc pobrany przez Google Play services przy pierwszym uzyciu - to robi Google, nie aplikacja.
- Nie znaleziono: analityki, Firebase/Crashlytics, reklam, wysylania logow awarii. Licencja jest sprawdzana lokalnie (bez zapytania do serwera przy starcie).
- Zalecenie dla strony: mozna napisac "aplikacja nie wysyla danych falownikow, backupow ani logow na serwer; z internetu korzysta tylko do aktualizacji, zakupu/aktywacji, pobrania firmware Boxa i (opcjonalnie, po zgodzie) do czytania zdjec przez Google Gemini". Nie pisac "nic wiecej nie jest wysylane" w sensie bezwzglednym (Google Play services dziala poza kontrola aplikacji).

### [APP -> WWW] Wynik WWW-010: Google Play obok APK ze strony (2026-11-19, ocena, bez zmian w kodzie)
- Status: ZROBIONE (APP). Zmiany w kontrakcie: nie. Zrodla: Google Play Help Center (polityki, program billing choice, target API), dokumentacja Android developer verification, kod aplikacji 0.99.56. Szacunki to dni pracy APP/WWW, bez testow u uzytkownika i bez czasu oczekiwania na Google.
- (1) AKTUALIZACJE: tak, aplikacja sama sprawdza feed servmod.com/servmod/version.json i pobiera APK (Updater, UpdateWorker, uprawnienie REQUEST_INSTALL_PACKAGES). Polityka Play (Device and Network Abuse oraz Request Install Package) zabrania samoaktualizacji poza Play i ogranicza to uprawnienie. Da sie wylaczyc: dwa warianty builda (flavor "web" i "play"); w "play" usuwamy uprawnienie w manifescie, ekran Updates i worker. Pobieranie firmware Boxa (plik dla ESP32, nie kod na telefon) zostaje, ale do potwierdzenia przy zgloszeniu w Play. Praca: 0,5-1 dzien. Ryzyko: male.
- (2) UPRAWNIENIA: USB host i NFC bez deklaracji; Bluetooth (scan/connect, neverForLocation), kamera, mikrofon (Leak finder), lokalizacja (skan WiFi/Box, Solar) - wymagaja opisu w Data safety i uzasadnienia, ale to zwykle uprawnienia runtime; READ_MEDIA_VIDEO (tylko SlowMo, wybor filmu) to ograniczone uprawnienie zdjec i wideo: zastapic systemowym Photo Pickerem i usunac uprawnienie (0,5 dnia). Zdjecie tabliczki do Google Gemini z kluczem uzytkownika: trzeba ujawnic w Data safety i polityce prywatnosci jako przekazanie zdjecia podmiotowi trzeciemu (okno zgody w aplikacji jest od 0.99.53). Backup na Drive idzie przez wybor pliku/folderu przez uzytkownika, bez szerokiego dostepu do plikow. Praca: 1 dzien (aplikacja) + formularze w Play Console po stronie wlasciciela. Ryzyko: srednie tylko dla Gemini i opisu uprawnien.
- (3) LICENCJE I PLATNOSCI (najwiekszy punkt): w UK program billing choice (od 2026-06-30) wymaga, zeby przy linku do platnosci na stronie uzytkownik mial tez do wyboru Google Play Billing; w regionach poza UK, EOG i USA zewnetrzny zakup nie jest dopuszczony. Wniosek: wariant "play" potrzebuje Play Billing (Pro jednorazowo, Subscription roczna) i zapisu zakupow w Play Console. Zeby nie ruszac License.kt: zakup w Play -> aplikacja wysyla purchaseToken + Device ID do servmod.com -> serwer sprawdza w Google Play Developer API i zwraca ten sam podpisany kod aktywacyjny co dzis. Ekran Subscription w wariancie play: przyciski Play Billing, bez linkow do Stripe/PayPal (w UK/EOG/USA mozna dodac link po zapisie do programu). Kody ze strony nadal da sie aktywowac. Opcja najtansza, ale ryzykowna: wariant play bez zakupu w aplikacji i bez linku, tylko Free + aktywacja kodu kupionego na stronie; Play moze to uznac za obejscie, ocena nieznana, nie polecam jako jedynej drogi. Oplaty (wg Help Center, do potwierdzenia w Play Console): oplata serwisowa 10% od pierwszego 1 mln USD rocznie, takze od subskrypcji, +5% przy Play Billing, bez dodatkowych 5% przy zewnetrznych linkach. Praca: aplikacja 3-5 dni, serwer (WWW) 2-3 dni, testy z kontami testowymi licencji. Ryzyko: wysokie (najwiekszy koszt i najwiecej zmian).
- (4) APPLICATION ID I PODPIS: applicationId com.servmod.app (do sprawdzenia w Play Console, czy wolny). Play wymaga AAB i Play App Signing. Zeby uzytkownicy APK ze strony i z Play mieli ten sam podpis (aktualizacje w miejscu miedzy kanalami), mozna zapisac istniejacy klucz servmod-release.jks w Play App Signing (eksport zaszyfrowany narzedziem PEPK od Google; to decyzja wlasciciela, bo klucz opuszcza komputer w postaci zaszyfrowanej). Jesli Google wygeneruje nowy klucz: dwa rozne podpisy, wersji z Play nie da sie zainstalowac na APK ze strony bez odinstalowania (wczesniej backup). Praca: 0,5 dnia + dzialania wlasciciela.
- (5) WERYFIKACJA DEWELOPERA: egzekucja od 2026-09-30 w Brazylii, Indonezji, Singapurze i Tajlandii, globalnie w 2027. Potrzebne: konto dewelopera (tozsamosc, profil platnosci, potwierdzona strona servmod.com), rejestracja nazwy pakietu com.servmod.app i odcisku klucza (SHA-256 w claude/servmod-handoff.md) przez przeslanie APK podpisanego tym kluczem; oplata rejestracyjna wg publikacji 25 USD (do potwierdzenia). Po stronie kodu: nic, byle applicationId i klucz zostaly stale. Praca: 0 dni aplikacji, 1-2 dni administracji wlasciciela.
- DODATKOWO (nie bylo w pytaniach): (a) target API: obecnie 34, a od 2026-08-31 nowe aplikacje i aktualizacje w Play musza celowac w Android 16 (API 36). Wymaga podniesienia compileSdk/targetSdk, a to AGP 8.5.2 -> nowszy z Gradle i Kotlin, wymuszone edge-to-edge i testy USB/BT/Box/Compose; 2-4 dni. (b) Od API 35 biblioteki natywne musza obslugiwac strony 16 KB: w APK sa libbarhopper_v3.so i libimage_processing_util_jni.so (ML Kit/CameraX), trzeba je sprawdzic po aktualizacji bibliotek. (c) Karta sklepu: polityka prywatnosci (URL), formularz Data safety, ankieta wieku, kategoria Tools, zrzuty ekranu z wlasnych zdjec, opis. Nazwy marek (Hitachi, Danfoss, ABB...) w opisie tylko jako "compatible with" i z zastrzezeniem o niezaleznosci (Disclaimer ze strony). (d) Nowe konta osobiste moga miec wymog testu zamknietego przed publikacja (liczba testerow i dni do sprawdzenia w Play Console).
- SUMA: okolo 8-15 dni roboczych APP + 2-3 dni WWW + administracja wlasciciela. Kolejnosc sensowna: (1) i (4) i target API, potem Play Billing, na koncu karta sklepu. Czekamy na decyzje wlasciciela.

### [APP-024] Polityka prywatnosci i strona pod Google Play (przygotowanie, bez publikacji w Play)
- Od: APP   Data: 2026-11-19   Priorytet: sredni (potrzebne zanim zalozymy aplikacje w Play Console)
- Status: ZROBIONE (WWW; terms.html czeka na wlasciciela)
- Co: (1) Obecny privacy.html jest szkicem i twierdzi, ze aplikacja "nie wysyla zadnych danych nigdzie" oraz ze adres e-mail i Device ID zbieramy "gdy ruszy zamowienie". Do Play trzeba publicznego, prawdziwego URL polityki prywatnosci zgodnego z faktycznym ruchem sieciowym aplikacji (patrz Wynik WWW-008 pkt 2 i claude/servmod-network-audit-2026-11-19.md): aktualizacje (tylko wariant ze strony; wariant Play ich nie ma), zakup/aktywacja licencji (produkt, Device ID, token), firmware Boxa (X-Licence), zdjecie do Google Gemini po zgodzie uzytkownika z kluczem API uzytkownika, OCR/skaner lokalnie. Aplikacja nie ma kont, reklam, analityki ani wysylania logow. Dane na serwerze: e-mail, Device ID, dane zamowienia (dostawca platnosci: Stripe/PayPal; po wejsciu Play Billing: tez purchaseToken i identyfikator zamowienia Google). Uprawnienia: kamera (OCR, skaner, Motion), mikrofon (Leak finder), lokalizacja i Bluetooth/WiFi (skan urzadzen, nie do sledzenia), NFC, USB. Napisz po angielsku: kto jest administratorem (Dariusz Grabowski, UK, kontakt support@servmod.com), jakie dane, po co, jak dlugo, prawa (UK GDPR), brak sprzedazy danych, jak poprosic o usuniecie. (2) Dodaj na stronie krotka strone "Delete data" albo sekcje w polityce z adresem e-mail do wniosku o usuniecie danych zamowienia (Play tego wymaga w formularzu Data safety, jesli zbieramy dane). (3) Terms: obecny tekst mowi "Draft ... before ordering opens"; do Play potrzebny final albo usunac oznaczenie Draft po akceptacji wlasciciela (sekcje o zwrotach i VAT sa osobna sprawa wlasciciela). (4) Bez publikowania zmian prawnych bez zatwierdzenia wlasciciela: przygotuj wersje do przejrzenia.
- Po co: Play Console wymaga URL polityki prywatnosci i deklaracji Data safety zgodnej z polityka; sprzecznosc to powod odrzucenia.
- Format wyniku: pliki privacy.html / delete-data (lub sekcja) gotowe do przejrzenia + wpis ZROBIONE z lista rzeczy, ktore wlasciciel musi zatwierdzic.
- Termin / zaleznosc: nie wymaga sprzetu; nie wymaga zmiany kontraktu.
- Wynik (WWW, 2026-11-20, commit b0a9444, wdrozone, HTTP 200):
  * https://servmod.com/privacy.html - polityka strony i wersji ze strony (poprawiona: sprawdzanie aktualizacji wysyla numer wersji, lista ruchu sieciowego zgodna z audytem, data 2026-11-20)
  * https://servmod.com/app-privacy.html - polityka wersji Google Play (bez cen, zakupow, Pro, Device ID; firmware Boxa z kluczem licencji, Gemini po zgodzie, lokalna siec, uprawnienia i po co)
  * https://servmod.com/delete-data.html - jak usunac dane (apka: dane na telefonie; konto, lista oczekujacych, e-mail do supportu, okres wyjatkow dla ksiegowosci)
  * Linki w stopce strony. Polityka prywatnosci do wpisania w Play Console: /app-privacy.html; URL usuniecia danych: /delete-data.html.
- Do zatwierdzenia przez wlasciciela: (1) tresc trzech stron; (2) administrator danych jest podany jako "DG, United Kingdom" (wlasciciel odlozyl pelne imie i nazwisko; APP-024 proponowalo pelne dane - zmienic po jego decyzji); (3) terms.html NIE ruszony (nadal Draft i zapis o sprzedazy na stronie) - czeka na decyzje wlasciciela, bo strona nadal sprzedaje; (4) strona delete-data wspomina konto na stronie i liste oczekujacych (dotyczy tylko strony, nie wersji Play).
- Zmiany w kontrakcie: nie


### [APP-025] Uzupelnienie APP-024: wersja Google Play ma inny ruch sieciowy niz wersja ze strony (zgodnosc polityki z Data safety)
- Od: APP   Data: 2026-11-19   Priorytet: wysoki (blokuje Data safety i opis sklepu)
- Status: ZROBIONE (WWW; terms.html czeka na wlasciciela)
- Co: polityka prywatnosci i strona (terms/refunds/privacy/delete-data) maja byc zgodne z TYM, co robi wersja play 0.99.61 (wlasciciel: nie mamy teraz sprzedazy ani pobran na stronie, dostosowujemy sie do Google Play). Fakty o buildzie play:
  1. Brak sklepu i platnosci: karta zakupu, linki Terms/Refunds, "Open servmod.com", napis o Device ID dla supportu - ukryte; zero zapytan do servmod.com/api/shop (zapytanie config tez wylaczone). Apka nie wysyla Device ID.
  2. Brak sprawdzania aktualizacji i pobierania APK (aktualizacje z Play); uprawnienia REQUEST_INSTALL_PACKAGES i POST_NOTIFICATIONS usuniete.
  3. Zostaje: (a) pobieranie firmware Boxa z servmod.com/api/box/firmware po akcji uzytkownika (naglowek X-Licence z kluczem licencji; tylko posiadacze licencji); (b) opcjonalne zdjecie do Google Gemini z kluczem API uzytkownika po akceptacji okna zgody; (c) siec lokalna na adres wpisany przez uzytkownika (nie wychodzi do internetu); (d) OCR i skaner kodow lokalnie (Google Play services).
  4. Nic nie jest sprzedawane w Play ani w apce; platnosci beda tylko przez Google Play Billing, jesli Play zaakceptuje aplikacje - NIE pisac o cenach, zakupach, Pro ani o kupowaniu na stronie w dokumentach powiazanych z wersja Play.
- Zadania: (1) privacy.html: prawdziwa, krotka polityka wg powyzszych faktow (brak analityki/reklam/kont; dane falownikow, backupy, logi zostaja na telefonie; Gemini tylko na zadanie uzytkownika; firmware: klucz licencji; kontakt support@servmod.com; data zmiany); (2) strona usuniecia danych (delete-data lub sekcja): apka nie ma kont; dane sa na telefonie i kasuje je odinstalowanie; w razie e-maila do supportu usuwamy korespondencje na prosbe; (3) terms.html: usunac "Draft", dostosowac do braku sprzedazy na stronie (lub napisac, ze warunki licencji beda dodane z Play Billing); (4) bez publikacji w Play; adresy URL podac APP po wdrozeniu.
- Format wyniku: pliki gotowe do przejrzenia + wpis ZROBIONE z lista rzeczy do zatwierdzenia przez wlasciciela.
- Termin / zaleznosc: nie wymaga sprzetu; nie wymaga zmiany kontraktu. Zastepuje punkty APP-024 sprzeczne z powyzszym.
- Wynik (WWW, 2026-11-20, commit b0a9444, wdrozone, HTTP 200):
  * https://servmod.com/privacy.html - polityka strony i wersji ze strony (poprawiona: sprawdzanie aktualizacji wysyla numer wersji, lista ruchu sieciowego zgodna z audytem, data 2026-11-20)
  * https://servmod.com/app-privacy.html - polityka wersji Google Play (bez cen, zakupow, Pro, Device ID; firmware Boxa z kluczem licencji, Gemini po zgodzie, lokalna siec, uprawnienia i po co)
  * https://servmod.com/delete-data.html - jak usunac dane (apka: dane na telefonie; konto, lista oczekujacych, e-mail do supportu, okres wyjatkow dla ksiegowosci)
  * Linki w stopce strony. Polityka prywatnosci do wpisania w Play Console: /app-privacy.html; URL usuniecia danych: /delete-data.html.
- Do zatwierdzenia przez wlasciciela: (1) tresc trzech stron; (2) administrator danych jest podany jako "DG, United Kingdom" (wlasciciel odlozyl pelne imie i nazwisko; APP-024 proponowalo pelne dane - zmienic po jego decyzji); (3) terms.html NIE ruszony (nadal Draft i zapis o sprzedazy na stronie) - czeka na decyzje wlasciciela, bo strona nadal sprzedaje; (4) strona delete-data wspomina konto na stronie i liste oczekujacych (dotyczy tylko strony, nie wersji Play).
- Zmiany w kontrakcie: nie


- Odebrane 2026-11-20 (WWW): wyniki WWW-007, WWW-008, WWW-010 oraz APP-024/025 przyjete.
