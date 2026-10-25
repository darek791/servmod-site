# ONE-TIME: stores the PayPal REST keys on the server (added to /etc/servmod/pay.env, Stripe lines are kept). Keys are typed here, never in chat or in the repo.
$ErrorActionPreference = "Stop"
$srv = "root@167.233.108.235"; $key = "$env:USERPROFILE\.ssh\id_ed25519"
function Secret($q) { $s = Read-Host $q -AsSecureString; [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($s)) }
$env_ = Read-Host "PayPal mode (sandbox or live) [sandbox]"; if ([string]::IsNullOrWhiteSpace($env_)) { $env_ = "sandbox" }
if ($env_ -notin @("sandbox","live")) { throw "mode must be sandbox or live" }
$id = Secret "PayPal Client ID"
$sec = Secret "PayPal Secret"
if ($id -notmatch '^[\w-]{20,}$' -or $sec -notmatch '^[\w-]{20,}$') { throw "that does not look like PayPal REST credentials" }
$body = "PAYPAL_ENV=$env_`nPAYPAL_CLIENT_ID=$id`nPAYPAL_SECRET=$sec`n"
$cmd = "umask 077; touch /etc/servmod/pay.env; sed -i '/^PAYPAL_/d' /etc/servmod/pay.env; cat >> /etc/servmod/pay.env; chown root:servmod /etc/servmod/pay.env; chmod 640 /etc/servmod/pay.env; systemctl restart servmod-api; sleep 2; systemctl is-active servmod-api; curl -fsS http://127.0.0.1:8100/api/shop/config; echo"
($body -replace "`r","") | ssh -i $key $srv $cmd
Write-Host "`nDone. PayPal buttons appear on servmod.com/pricing.html." -ForegroundColor Green
