# CEL (wspólny)

Dariusz (inżynier utrzymania ruchu) buduje narzędzie serwisowe do maszyn: aplikację ServMod na telefon oraz skrzynkę
ServMod Box (ESP32-S3), która zastępuje osobne adaptery do każdej maszyny.

## ServMod Box
- Zasilana z baterii LiPo + przetwornica 5 V. Z telefonem rozmawia WYŁĄCZNIE bezprzewodowo: Wi-Fi (własny AP, TCP 4400) i BLE.
- Strona maszyny: RS-485 (ch0), CAN listen-only (ch1), RS-232 (ch2), USB host do Hitachi WL200/WJ200 (ch3),
  krokowiec (ch4), Ethernet W5500 (ch5). Bez wejść 12/24 V, bez Profibus/MPI, bez czujników PT100.
- Zapis jest domyślnie dozwolony (WRITE_LOCK 0); CAN może też nadawać; po przywróceniu kopii bez odczytu kontrolnego.
- Moduły aplikacji (Hitachi, Danfoss, Lenze, ...) działają przez Box tak jak przez adapter USB; moduły nie wiedzą, którędy idą dane.

## Gotowe, gdy
- Odczyt/zapis Modbus (Hitachi WJ200) i FC (Danfoss VLT 2800 / FC 280) przez Box w czasie zbliżonym do adaptera USB.
- Backup i restore parametrów przez Box nie przerywa się przy utracie łącza z telefonem (zlecenia wykonywane w Boxie).
- Ethernet (ch5): sprawdzanie portów/ping/sweep i wysyłka do drukarek przez Box.
- Własna płytka i obudowa (później). Nazwa i sprzedaż osobno od aplikacji: decyzja otwarta.
