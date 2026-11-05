# Uploads the ServMod Box firmware and wiring drawings to the server (Pro-only downloads on servmod.com/modbox.html).
# Source: ServMod\handoff\www_assets\box_firmware (firmware\*.bin, schematics\*, firmware.json from the BOX project).
# Files go to /var/lib/servmod/box, NOT to the public web root: the API serves them only to Pro accounts / Pro licence codes.
$ErrorActionPreference = "Stop"
$srv = "root@167.233.108.235"; $key = "$env:USERPROFILE\.ssh\id_ed25519"
$web = Split-Path -Parent $PSScriptRoot
$src = Join-Path (Split-Path -Parent $web) "handoff\www_assets\box_firmware"
if (-not (Test-Path "$src\firmware.json")) { throw "firmware.json not found in $src" }
$m = Get-Content -Raw "$src\firmware.json" | ConvertFrom-Json
Write-Host "Firmware version $($m.version) ($($m.build_date))" -ForegroundColor Yellow
foreach ($b in $m.boxes.PSObject.Properties) { foreach ($f in $b.Value.files) {
  $p = Join-Path "$src\firmware" $f.file
  if (-not (Test-Path $p)) { throw "missing $($f.file)" }
  $h = (Get-FileHash $p -Algorithm SHA256).Hash.ToLower(); $n = (Get-Item $p).Length
  if ($h -ne $f.sha256 -or $n -ne $f.bytes) { throw "$($f.file): size or SHA-256 does not match firmware.json" }
  Write-Host "  OK $($f.file)  $n bytes" } }
Write-Host "`nThis makes the files available to every Pro account. Mini is experimental (not flashed on a board yet)." -ForegroundColor Cyan
$ok = Read-Host "Type PUBLISH to upload (anything else cancels)"
if ($ok -ne "PUBLISH") { Write-Host "Cancelled."; exit }
ssh -i $key $srv "mkdir -p /var/lib/servmod/box/firmware /var/lib/servmod/box/schematics"
scp -i $key "$src\firmware\*.bin" "${srv}:/var/lib/servmod/box/firmware/"
scp -i $key "$src\schematics\*" "${srv}:/var/lib/servmod/box/schematics/"
scp -i $key "$src\firmware.json" "${srv}:/var/lib/servmod/box/firmware.json"
ssh -i $key $srv "chown -R servmod:servmod /var/lib/servmod/box && chmod -R u=rwX,g=rX,o= /var/lib/servmod/box && ls -l /var/lib/servmod/box/firmware"
Write-Host "`nDone. Page: https://servmod.com/modbox.html (sign in with a Pro account)." -ForegroundColor Green
