# ONE-TIME: installs the ServMod API on the server. Asks a few questions, nothing is stored in the repo.
$ErrorActionPreference = "Stop"
$srv = "root@167.233.108.235"; $key = "$env:USERPROFILE\.ssh\id_ed25519"
$root = Split-Path -Parent $PSScriptRoot
function Ask($q, $def) { $a = Read-Host "$q [$def]"; if ([string]::IsNullOrWhiteSpace($a)) { $def } else { $a.Trim() } }
$admin = Ask "Your admin e-mail (you will sign in with it)" "dardiag@gmail.com"
$from  = Ask "Sender address for e-mails" "ServMod <no-reply@servmod.com>"
$rk    = Read-Host "Resend API key (leave empty for now; sign-in codes then go to the server log)"
$lic   = Read-Host "Path to license_private.key (leave empty if you do not have it yet)"
if ($admin -notmatch '^[\w.+-]+@[\w.-]+\.\w+$') { throw "bad e-mail" }
if ($from -notmatch '^[\w .<>@+-]+$') { throw "bad sender" }
if ($rk -and $rk -notmatch '^[\w-]+$') { throw "bad key characters" }
$mode = if ($rk) { "resend" } else { "log" }
if ($lic) {
  if (-not (Test-Path $lic)) { throw "key file not found: $lic" }
  ssh -i $key $srv "mkdir -p /etc/servmod"
  scp -i $key $lic "${srv}:/etc/servmod/license_private.key"
}
scp -i $key "$root\server\servmod-sync.sh" "${srv}:/tmp/servmod-sync.sh"
$hdr = "export ADMIN_EMAILS='$admin' MAIL_FROM='$from' MAIL_MODE='$mode' RESEND_API_KEY='$rk'`n"
$boot = (Get-Content -Raw "$root\server\bootstrap_backend.sh") -replace "`r", ""
$sync = "sed -i 's/\r$//' /tmp/servmod-sync.sh`n"
($sync + $hdr + $boot) | ssh -i $key $srv "bash -s"
Write-Host "`nDone. Open https://servmod.com/account/ and sign in." -ForegroundColor Green
