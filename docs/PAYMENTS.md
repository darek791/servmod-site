# Payments and automatic activation codes (built 2026-10-25)

Flow: pricing page -> `/api/shop/checkout` -> Stripe Checkout (hosted, we never see cards) -> Stripe calls `/api/pay/stripe` (signed webhook) -> `shop.fulfil()` grants Pro / Subscription on the buyer's e-mail account -> e-mail with the activation code (when the buyer typed a Device ID at checkout) or with sign-in steps (code appears on the account page).
The shop is CLOSED until `/etc/servmod/pay.env` contains `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` (`GET /api/shop/config` shows `open`).

## One-time setup (owner, on the PC)
1. Stripe dashboard (start in TEST mode): Developers > Webhooks > add endpoint `https://servmod.com/api/pay/stripe`, events `checkout.session.completed`, `checkout.session.async_payment_succeeded`, `charge.refunded`, `charge.dispute.created`. Copy the signing secret (`whsec_...`).
2. Settings > Payment methods: turn on PayPal (if offered for the UK account) and wallets.
3. Double-click `tools\install_payment_keys.cmd` (copy is in `web\install_backend\`): type the secret key, the signing secret and the prices in pence. The keys go to `/etc/servmod/pay.env` on the server only.
4. Licence key on the server: `install_licence_key.cmd` (already exists). The server signs codes with it.
5. Test with a Stripe test card (4242 4242 4242 4242), then switch to live keys by running the script again.

## Rules in the code
- Products and prices (pence, env): `pro` `PRICE_PRO_PENCE` (default 4000), `sub` `PRICE_SUB_PENCE` (default 2000, +365 days from today or from the current end date).
- One shop entitlement per account (`source='shop'`): features `PRO` and/or `SUB:YYYYMMDD`; 1 seat (one device), moves limited by `MOVES_PER_YEAR`.
- Idempotent: table `orders` has UNIQUE(provider, ext_id), so a repeated webhook does nothing.
- A changed plan re-signs the code for an already activated device the next time the account page requests it.
- Refund or dispute events only e-mail the admins and write the audit log; revoke the licence by hand in the account admin panel.
- `/api/pay/*` skips the CSRF header (the provider signature, 5 minute tolerance, protects it).

## Not done
- PayPal as a separate integration (only if PayPal cannot be enabled inside Stripe Checkout).
- UK VAT / tax handling and invoices; legal texts (Terms, Refunds) need the owner's approval before real sales.

## Zakup z aplikacji (od 2026-10-25)
Aplikacja generuje sekret zakupu (16-128 znaków), wywołuje `POST /api/shop/checkout` z `{product, device_id, claim}` i otwiera zwrócony adres Stripe w Custom Tab. W sesji Stripe lądują `metadata[device_id]` i `metadata[claim]` (sam hash SHA-256, po stronie serwera zapisany w `orders.note` jako `claim:<hash>`); pole Device ID w formularzu Stripe jest wtedy wyłączone. Webhook wydaje kod (`issuing.issue`), a aplikacja odpytuje `GET /api/shop/claim?device=&token=` (`pending` / `ready`+`code` / `error`). Mail z paragonem zostaje jako kopia. Zakup ze strony (bez aplikacji) działa jak dotąd: Device ID opcjonalnie w formularzu Stripe, inaczej przez konto.
Zadanie dla APP: WWW-001 w `_komunikacja/inbox/APP.md`.

## PayPal (od 2026-10-25, osobna integracja, bo Stripe konta UK nie pokazuje PayPal)
- `POST /api/shop/checkout` przyjmuje `"provider":"stripe"|"paypal"` (domyślnie stripe). PayPal: tworzy zamówienie Orders v2 (GBP), zapisuje `pending_orders`, zwraca adres zatwierdzenia.
- Po zatwierdzeniu PayPal przekierowuje na `/api/pay/paypal/return?token=<order>`; serwer sam robi capture, sprawdza status COMPLETED i dopiero wtedy `fulfil("paypal", ...)` (to samo co Stripe: licencja, kod dla Device ID, mail, `/api/shop/claim`). Błąd capture = mail do admina i `#paid=problem`.
- Klucze: `tools\install_paypal_keys.cmd` (tryb sandbox lub live, Client ID i Secret wpisywane tylko w oknie na PC; dopisuje do /etc/servmod/pay.env, linie Stripe zostają).
- Strona: przy każdym planie dwa przyciski (karta, PayPal), gdy oba włączone. Zwroty i spory PayPal: ręcznie w panelu PayPal (bez webhooka).
