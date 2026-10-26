# ServMod app: what is in it (for WWW, read from app docs and code on 2026-10-26)

Source: wl200_android (Modules.kt), ServMod\handoff\*.md (servmod-handoff, 06_SENSORS_MODULE, servmod-licensing, servmod-hardware-verified). Read-only; the app is owned by the APP project. Current release 0.76.3. Re-check before writing new claims.

## Home screen: 20 module tiles
Inverters, Thermocontrollers, Printers, Condition, Network, Calc, Access, Notes, Parts, PLC, HMI, Manuals, NFC & Barcode, Tools, Zodiac Printers, USB Tools, Steppers, OBD2 Scanner, Siemens OP17, ESP32 Loader. Plus Settings (screen on, Backup, Subscription, Support, About with updates, terms, open-source licences) and a FREE/PRO/FULL badge.
"Tools" holds about 13 sub-tools: Level, Magnet, Tacho (camera/magnet/vibration/light/gyro), Slow-mo (frame-by-frame video, delay A to B, speed), Loupe, Strobe (LED sync), Leak finder (ultrasonic via mic), Ruler, Picture measure, Height, Colour (RAL names), Sensors explorer, Solar (panel aiming, best tilt, energy estimate). Counting tools, not tiles (drive brands count as one Inverters tool): 19 other tiles + 13 sub-tools in Tools = 32, so the site says "30+ tools".

## Inverters: every drive module has the same tabs
Backup | Parameters | Control | Settings | Faults. Also Compare, fault-cause lookup, "How to connect" per model (a thumbnail photo marks a model that was physically tested).
Verified on real hardware by the user (2026-10-23..25): Lenze 8400 over CAN via the Box (backup, save to memory, compare, manual control, factory reset; fault reset not tested), Hitachi WL200 over USB (all options), Hitachi WJ C1 over RS-485 and over the Box USB host (all options; direct phone OTG does not work, probably power), Allen-Bradley PowerFlex 525 (all options), Danfoss FC 280 (RS-485, USB, Box), Danfoss VLT 2800 (read, write, restore, control, live).
NOT verified on a drive: Omron MX2, Mitsubishi FR-D700, Schneider ATV320, Siemens V20, Delta MS300, INVT GD200A, ABB ACS355, Inovance MD500, Yaskawa GA500, Omron SMARTSTEP servo (offline only), Omron E5CN thermocontroller.
New Modbus drives are added by JSON profile (engine since 0.74.0). Expansion of devices is paused by the owner.

## Other modules, state
Ready (by site label): Calc, Access, Notes, Parts, ESP32 Loader (flash verified on CYD).
In field testing: Printers (PM45 tester + cable check), Condition, Network, Tools, USB Tools, Box, Backup.
Draft: NFC & Barcode, Zodiac Printers, Steppers, PLC (read-only, never writes), HMI (simulator only), Manuals, OBD2 (ELM327, not tried on a car), OP17 loader (spare panels only, experimental; write of alco_1 on a spare panel verified).
ServMod Box: own ESP32-S3 interface (RS-485, RS-232, CAN, USB host, Ethernet), USB / Wi-Fi / BLE, firmware 0.9.1, prototype.
App Backup: encrypted copy of app data to a chosen folder (Drive), restore on a new phone, verified.

## Licensing
Free: connect, read, monitor, fault history, backup to file, Compare, all field tools. Pro (GBP 40 once): parameter write, Restore, manual control, fault and factory reset, OP17 write, Box write unlock. Stop is never blocked. Subscription (GBP 20 per year): modules/brands released after purchase and parameter DB/profile updates. NOTE: Subscription content is not enforced yet and no "sub" content exists yet, so do not promise specific subscription-only features on the site. Features in the code are PRO and SUB:date (independent), ALL = legacy full.

## Rules when writing site text
Never say "tested" without a hardware test. Name only brands as descriptions (independent tool). GUI and site in English.
