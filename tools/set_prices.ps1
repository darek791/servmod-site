# Changes only the prices on the server (pence). Stripe and PayPal keys stay as they are.
$ErrorActionPreference = "Stop"
$srv = "root@167.233.108.235"; $key = "$env:USERPROFILE\.ssh\id_ed25519"
$pro = Read-Host "Pro price in pence (type 100 for a GBP 1 test, 4000 for the real price)"
$sub = Read-Host "Subscription price in pence [2000]"; if ([string]::IsNullOrWhiteSpace($sub)) { $sub = "2000" }
if ($pro -notmatch '^\d{3,6}$' -or $sub -notmatch '^\d{3,6}$') { throw "prices must be whole numbers of pence, at least 100" }
$body = "PRICE_PRO_PENCE=$pro`nPRICE_SUB_PENCE=$sub`n"
$cmd = "umask 077; sed -i '/^PRICE_/d' /etc/servmod/pay.env; cat >> /etc/servmod/pay.env; systemctl restart servmod-api; sleep 2; systemctl is-active servmod-api; curl -fsS http://127.0.0.1:8100/api/shop/config; echo"
($body -replace "`r","") | ssh -i $key $srv $cmd
Write-Host "`nDone." -ForegroundColor Green
