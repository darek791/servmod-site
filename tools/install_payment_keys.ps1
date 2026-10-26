# ONE-TIME: stores the payment keys on the server (/etc/servmod/pay.env). Keys are typed here, never in chat or in the repo.
$ErrorActionPreference = "Stop"
$srv = "root@167.233.108.235"; $key = "$env:USERPROFILE\.ssh\id_ed25519"
function Secret($q) { $s = Read-Host $q -AsSecureString; [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($s)) }
$sk = Secret "Stripe secret key (sk_live_... or sk_test_...)"
$wh = Secret "Stripe webhook signing secret (whsec_...)"
$pro = Read-Host "Pro price in pence [4000]";  if ([string]::IsNullOrWhiteSpace($pro)) { $pro = "4000" }
$sub = Read-Host "Subscription price in pence [2000]"; if ([string]::IsNullOrWhiteSpace($sub)) { $sub = "2000" }
if ($sk -notmatch '^sk_(live|test)_[\w]+$') { throw "that does not look like a Stripe secret key" }
if ($wh -notmatch '^whsec_[\w]+$') { throw "that does not look like a webhook signing secret" }
if ($pro -notmatch '^\d{3,6}$' -or $sub -notmatch '^\d{3,6}$') { throw "prices must be whole numbers of pence" }
$body = "STRIPE_SECRET_KEY=$sk`nSTRIPE_WEBHOOK_SECRET=$wh`nPRICE_PRO_PENCE=$pro`nPRICE_SUB_PENCE=$sub`n"
$cmd = "umask 077; touch /etc/servmod/pay.env; sed -i '/^STRIPE_/d;/^PRICE_/d' /etc/servmod/pay.env; cat >> /etc/servmod/pay.env; chown root:servmod /etc/servmod/pay.env; chmod 640 /etc/servmod/pay.env; systemctl restart servmod-api; sleep 2; systemctl is-active servmod-api; curl -fsS http://127.0.0.1:8100/api/shop/config; echo"
($body -replace "`r","") | ssh -i $key $srv $cmd
Write-Host "`nDone. Ordering is now open on servmod.com/pricing.html (use test keys first)." -ForegroundColor Green
