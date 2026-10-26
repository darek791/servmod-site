# Publishes the newest ServMod-x.y.z-clean.apk from ServMod\releases to servmod.com (update feed + download page).
# Public action: it makes the APK downloadable by everyone. Run it only when you mean it.
$ErrorActionPreference = "Stop"
$web = Split-Path -Parent $PSScriptRoot
$rel = Join-Path (Split-Path -Parent $web) "releases"
$py  = Join-Path $web "tools\release.py"
if (-not (Test-Path $py)) { throw "release.py not found at $py" }
$apk = Get-ChildItem $rel -Filter "ServMod-*-clean.apk" | Where-Object { $_.Name -match '^ServMod-(\d+)\.(\d+)\.(\d+)-clean\.apk$' } |
       Sort-Object { $m = [regex]::Match($_.Name,'(\d+)\.(\d+)\.(\d+)'); [int]$m.Groups[1].Value*1000000 + [int]$m.Groups[2].Value*1000 + [int]$m.Groups[3].Value } | Select-Object -Last 1
if (-not $apk) { throw "no ServMod-*-clean.apk in $rel" }
Write-Host "APK to publish: $($apk.FullName)  ($([math]::Round($apk.Length/1MB,1)) MB)" -ForegroundColor Yellow
$pyexe = (Get-Command py -ErrorAction SilentlyContinue); if ($pyexe) { $pyargs = @("-3") } else { $pyexe = Get-Command python -ErrorAction SilentlyContinue; $pyargs = @() }
if (-not $pyexe) { throw "Python not found (install from python.org or the Microsoft Store)" }
$notes = "First public release;Free plan: read, save and compare drive parameters, faults, cable and wiring cheat sheets;Pro and Subscription add writing, restore and manual control (bought in the app);Some drives and modules are not yet verified on hardware"
& $pyexe.Source @pyargs $py $apk.FullName --notes $notes --dry-run
Write-Host "`nThe dry run above changed nothing on the server." -ForegroundColor Cyan
$ok = Read-Host "Type PUBLISH to make this APK public on servmod.com (anything else cancels)"
if ($ok -ne "PUBLISH") { Write-Host "Cancelled."; exit }
& $pyexe.Source @pyargs $py $apk.FullName --notes $notes
Write-Host "`nChecking the feed..." -ForegroundColor Cyan
try { (Invoke-WebRequest -UseBasicParsing "https://servmod.com/servmod/version.json").Content } catch { Write-Host "Feed check failed: $_" -ForegroundColor Red }
Write-Host "`nDone. Download page: https://servmod.com/download.html" -ForegroundColor Green
