# ONE-TIME: puts the Google Play service-account key on the server and switches Play purchase checking on.
# The JSON key stays on the PC and goes only to /etc/servmod/play-key.json on the server (never into the repo or the chat).
# Run it ONLY after the play-billing branch has been merged into main and the server has deployed it (about 1 minute after the push).
$ErrorActionPreference = "Stop"
$srv = "root@167.233.108.235"; $key = "$env:USERPROFILE\.ssh\id_ed25519"
$path = (Read-Host "Full path of the downloaded service-account JSON key file").Trim('"').Trim()
if (-not (Test-Path $path)) { throw "file not found: $path" }
$j = Get-Content -Raw $path | ConvertFrom-Json
if ($j.type -ne "service_account" -or -not $j.client_email -or -not $j.private_key) { throw "this is not a Google service-account key file" }
Write-Host "Service account: $($j.client_email)"
scp -i $key $path "${srv}:/etc/servmod/play-key.json"
$cmd = "chown root:servmod /etc/servmod/play-key.json; chmod 640 /etc/servmod/play-key.json; touch /etc/servmod/pay.env; sed -i '/^PLAY_KEY_FILE=/d' /etc/servmod/pay.env; echo 'PLAY_KEY_FILE=/etc/servmod/play-key.json' >> /etc/servmod/pay.env; chown root:servmod /etc/servmod/pay.env; chmod 640 /etc/servmod/pay.env; systemctl restart servmod-api; sleep 3; systemctl is-active servmod-api; ls -l /etc/servmod/play-key.json; curl -s -o /dev/null -w 'redeem check (expect 400, not 503): %{http_code}\n' -X POST http://127.0.0.1:8100/api/shop/play/redeem -H 'Content-Type: application/json' -H 'X-Requested-With: servmod' -d '{`"product`":`"pro`",`"purchase_token`":`"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`",`"device_id`":`"AAAAAAAAAAAAAAAA`",`"package`":`"com.servmod.app`"}'"
ssh -i $key $srv $cmd
Write-Host "`nDone. 503 above = key not readable/not configured; 400 = Google was asked and did not know the fake token (that is the good result)." -ForegroundColor Green
