#!/usr/bin/env python3
"""Send a Bitpool marketing campaign email via Microsoft Graph, delegated sign-in.

Sends straight through Graph's REST API (`POST /me/sendMail`) rather than composing in
Outlook -- Outlook re-renders HTML through Word's engine on every send path (compose,
forward, .eml -> .oft), which mangles styling unpredictably. A pure REST call to
Exchange Online never touches that rendering engine, so the authored HTML arrives
exactly as built.

Auth: Authorization Code + PKCE, not Device Code Flow. Bitpool's tenant has a
Conditional Access policy that blocks Device Code Flow for public clients on desktop
(AADSTS53003) -- CA can only ever target resources/APIs, never a specific public
client app, so the fix is a different flow, not a policy exception. PKCE opens a real
browser and catches the redirect on a local loopback listener -- the normal
interactive flow for a desktop app, and not the transfer method the CA policy blocks.

Delegated only -- this signs in as a real user and sends Mail.Send, never an
application/client-credentials permission. There is no client secret anywhere: this is
a public client, so TENANT_ID/CLIENT_ID below are not secrets, just identifiers.

Send As (sending as a shared mailbox instead of the signed-in user): pass --send-as
<mailbox>. Requires two things already granted on this tenant's "CLI Email Sender" app
registration: Exchange "Send As" permission on the target mailbox for whoever signs
in, and the delegated Mail.Send.Shared scope (in addition to Mail.Send) with admin
consent. Without --send-as, every send goes out as whoever signs in via the browser --
whoami() prints that identity before the real send either way, so the actual From
mailbox is always confirmed, never assumed. NEVER hardcode a shared-mailbox address
as a default here or in the skill docs -- always ask the user which mailbox to send
as, every time, even on a repeat send.

Recipient isolation: every recipient gets their OWN Graph sendMail call
("toRecipients": [that one address]) -- never a shared To/Cc/Bcc list. Nobody sees
anyone else's address, and one bad address can't affect anyone else's copy.

Two modes, mutually exclusive:
  --to "Jane <jane@x.com>, bob@y.com"   Individual -- a few named recipients, no
                                         merge tokens, hardcoded content.
  --csv recipients.csv                  Batch -- one row per recipient. The template
                                         may contain {{column_name}} tokens, filled
                                         per row from that CSV column. Every row must
                                         have a non-empty 'email' column and a
                                         non-empty value for every token the template
                                         uses -- refuses to send a blank merge field.

Guard checks refuse to send if the body still contains: a data: URI image, any of
draft-marketing-email's un-rewritten local-path tokens ({{CAMPAIGN_LOCAL}} etc. --
meaning the publish rewrite was never run), a SendGrid-only merge/unsubscribe tag
(meaningless in a Graph send, rendering as broken literal text), or an unfilled
[bracket] placeholder ([Sender name], [SUBJECT LINE], etc.) left over from the
template.

Attachments: pass --attach <path>, repeatable, to attach one or more local files --
the same set is attached to every recipient's copy (there's no per-recipient
attachment variation). Combined size is capped at MAX_ATTACHMENT_BYTES (20 MB,
matching Exchange Online's typical per-message limit) -- refuses to send over it
rather than letting Graph reject it partway through.

Two different Graph mechanisms are used depending on size, picked automatically:
  - Any file <= SIMPLE_ATTACHMENT_BYTES (3 MB): embedded directly as a
    fileAttachment (base64 content inline). If EVERY attachment is this small (or
    there are none), the whole send stays on the original single-call sendMail path
    -- no behaviour change from before attachments existed.
  - Any file > SIMPLE_ATTACHMENT_BYTES: needs Graph's upload-session flow, which
    only works against an existing message resource, not sendMail directly. So the
    moment ANY attachment is "large", every recipient's send switches to: create a
    draft message (POST .../messages) -> attach each file (small ones in one call,
    large ones via createUploadSession + chunked PUT) -> send the draft
    (POST .../messages/{id}/send). Requires the delegated Mail.ReadWrite scope (own
    mailbox) and, with --send-as, Mail.ReadWrite.Shared PLUS Exchange "Full Access"
    on that mailbox (Send As alone only covers the sendMail action, not creating a
    draft inside someone else's mailbox) -- see graph-signin-and-config.md.

--check-only validates the template/CSV and reports readiness with NO sign-in, no
network call, no send -- use this to verify guards are clean before asking the user
to approve the real send.

Refuses to run without --confirm, same discipline as every send script in this
project: only pass --confirm after the user has explicitly approved this exact
recipient list, subject, and body in the conversation.

Requires: the `requests` library, importable from WSL Ubuntu's system python3 --
installed via `sudo apt-get install python3-requests`, not pip/a venv (Ubuntu's
system Python is externally-managed per PEP 668, but this is a normal packaged
library, so the apt route needs no override). See references/environment-setup.md
for the one-time setup this skill walks through.
"""
import argparse
import base64
import csv
import hashlib
import http.server
import json
import mimetypes
import os
import re
import secrets
import subprocess
import sys
import threading
import urllib.parse
import webbrowser

import requests

AUTHORITY = "https://login.microsoftonline.com"
GRAPH = "https://graph.microsoft.com/v1.0"

# Bitpool's "CLI Email Sender" app registration. Public client (Authorization Code +
# PKCE) -- there is no client secret for this app type, so these two IDs are not
# secret and are safe to commit alongside the code.
TENANT_ID = "820737d5-aa31-442a-8140-9a22577361dc"
CLIENT_ID = "2fb3c6de-8983-4d2e-a3f7-c0964a872d63"
MAIL_SEND_SCOPE = "https://graph.microsoft.com/Mail.Send"
MAIL_SEND_SHARED_SCOPE = "https://graph.microsoft.com/Mail.Send.Shared"
MAIL_READWRITE_SCOPE = "https://graph.microsoft.com/Mail.ReadWrite"
MAIL_READWRITE_SHARED_SCOPE = "https://graph.microsoft.com/Mail.ReadWrite.Shared"

# Per-file threshold: at or under this, embed directly as a fileAttachment (base64
# inline). Over this, Graph requires the createUploadSession + chunked PUT flow --
# it only works against an existing draft message, not sendMail directly.
SIMPLE_ATTACHMENT_BYTES = 3 * 1024 * 1024

# Combined cap across all --attach files for one send. 20 MB matches Exchange
# Online's typical per-message limit -- a safety cap on this script's side, not a
# guarantee; an org could have it configured lower, in which case Graph itself will
# reject the send and that error surfaces as a FAILED line, not a silent drop.
MAX_ATTACHMENT_BYTES = 20 * 1024 * 1024

# Must be a multiple of 320 KiB per Graph's upload-session docs (except the final
# chunk, which can be shorter). 3,276,800 bytes = 10 * 320 KiB.
UPLOAD_CHUNK_BYTES = 320 * 1024 * 10

TOKEN_RE = re.compile(r"\{\{(\w+)\}\}")
BRACKET_RE = re.compile(r"\[[A-Za-z][^\[\]\n]{0,60}\]")
# Email HTML routinely carries MSO conditional-comment syntax -- <!--[if mso]>,
# <!--[if !mso]><!-->, <!--[if gte mso 9]>, <![endif]--> -- which BRACKET_RE would
# otherwise flag as an unfilled placeholder. Every production template in this repo
# uses these, so without this exclusion no real send would ever pass the guard.
MSO_CONDITIONAL_RE = re.compile(r"^\[\s*(if\b.*|endif)\s*\]$", re.IGNORECASE)


def open_browser(url):
    """webbrowser.open() has no way to reach a Windows browser from inside WSL -- it
    can only see Linux-side browsers, which don't exist here. Shell out to Windows'
    own URL launcher instead, which WSL can always reach via /mnt interop.

    powershell's Start-Process is tried first: it resolves the URL directly via its
    registered protocol handler, no shell metacharacter parsing, no silent fallback
    path. Two other methods were tried and rejected during testing:
      - cmd.exe's "start" reparses its whole command line for its own metacharacters
        (&, |, ^, ...) even when invoked via subprocess's argv list, and an OAuth URL
        is full of unescaped "&" between query params -- that silently truncated the
        URL at the first "&", so Entra only ever saw client_id and dropped
        response_type/redirect_uri/scope/... entirely (AADSTS900144).
      - explorer.exe sometimes can't cleanly resolve a long query-string URL as a URI
        and silently falls back to opening a plain Explorer window at the user's
        default library folder, while still separately handing the URL to the
        browser -- a confusing side effect (a stray Explorer tab) with no benefit
        over Start-Process, so it's dropped rather than kept as a fallback.
    """
    for cmd in (
        ["powershell.exe", "-NoProfile", "-Command", f"Start-Process '{url}'"],
        ["cmd.exe", "/c", "start", "", f'"{url}"'],
    ):
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=10)
            return True
        except Exception:
            continue
    return webbrowser.open(url)


def make_pkce_pair():
    verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b"=").decode("ascii")
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")
    return verifier, challenge


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    result = {}

    def do_GET(self):
        qs = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(qs)
        _CallbackHandler.result["code"] = params.get("code", [None])[0]
        _CallbackHandler.result["state"] = params.get("state", [None])[0]
        _CallbackHandler.result["error"] = params.get("error_description", [None])[0]

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        if _CallbackHandler.result.get("code"):
            body = "<html><body>Signed in. You can close this tab and return to the terminal.</body></html>"
        else:
            body = f"<html><body>Sign-in did not return a code: {_CallbackHandler.result.get('error')}</body></html>"
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, *a):
        pass  # silence the default per-request stderr logging


def interactive_login(scope):
    verifier, challenge = make_pkce_pair()
    state = secrets.token_urlsafe(16)

    server = http.server.HTTPServer(("127.0.0.1", 0), _CallbackHandler)
    port = server.server_address[1]
    redirect_uri = f"http://localhost:{port}"

    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()

    auth_url = (
        f"{AUTHORITY}/{TENANT_ID}/oauth2/v2.0/authorize?"
        + urllib.parse.urlencode(
            {
                "client_id": CLIENT_ID,
                "response_type": "code",
                "redirect_uri": redirect_uri,
                "response_mode": "query",
                "scope": scope,
                "state": state,
                "code_challenge": challenge,
                "code_challenge_method": "S256",
                # Forces the identity platform to show the interactive account
                # picker/login instead of first attempting a silent "Windows SSO
                # broker" handshake (visible as sso_nonce/mscrid params the browser
                # adds to the redirected URL) -- that handshake was observed to hang
                # indefinitely rather than fall through to an interactive prompt.
                "prompt": "select_account",
            }
        )
    )

    print(f"Opening your browser to sign in (listening on {redirect_uri}) ...", flush=True)
    opened = open_browser(auth_url)
    if not opened:
        print("Could not auto-open a browser. Open this URL manually:", flush=True)
        print(auth_url, flush=True)

    thread.join(timeout=180)
    if thread.is_alive():
        sys.exit("Timed out waiting for the browser sign-in redirect (180s).")

    if _CallbackHandler.result.get("error"):
        sys.exit(f"Sign-in failed: {_CallbackHandler.result['error']}")
    if _CallbackHandler.result.get("state") != state:
        sys.exit("State mismatch on redirect -- possible interference, aborting.")
    code = _CallbackHandler.result.get("code")
    if not code:
        sys.exit("No authorization code received.")

    print("Got authorization code, exchanging for a token...", flush=True)
    token_resp = requests.post(
        f"{AUTHORITY}/{TENANT_ID}/oauth2/v2.0/token",
        data={
            "client_id": CLIENT_ID,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "code_verifier": verifier,
            "scope": scope,
        },
        timeout=30,
    )
    if token_resp.status_code != 200:
        sys.exit(f"Token exchange failed: {token_resp.status_code} {token_resp.text}")
    print("Signed in OK.", flush=True)
    return token_resp.json()["access_token"]


def whoami(access_token):
    resp = requests.get(
        f"{GRAPH}/me?$select=displayName,mail,userPrincipalName",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=30,
    )
    if resp.status_code != 200:
        return None
    data = resp.json()
    return data.get("mail") or data.get("userPrincipalName"), data.get("displayName")


def build_email(addr):
    """Build a Microsoft Graph `emailAddress` object -- property is `address`, NOT
    `email` (that was a copy-paste mistake from send-via-sendgrid.py's build_email(),
    which targets SendGrid's API and does use `email`). Graph's schema for this type
    is `{"address": ..., "name": ...}`."""
    addr = addr.strip()
    if "<" in addr and ">" in addr:
        name, email = addr.split("<", 1)
        return {"address": email.strip(">").strip(), "name": name.strip().strip('"')}
    return {"address": addr}


def guard_no_local_paths(html, context):
    if "data:image" in html:
        sys.exit(
            f"Refusing to send ({context}): the body contains a data: URI image. "
            "Bitpool marketing email is CDN-hosted only -- no base64 embedding, ever."
        )
    for token in ("{{CAMPAIGN_LOCAL}}", "{{COMMON_LOCAL}}", "{{COMMON_CDN}}", "{{CAMPAIGN_CDN}}", "sharepoint.com"):
        if token in html:
            sys.exit(
                f"Refusing to send ({context}): body still contains {token!r}. Run "
                "draft-marketing-email's publish rewrite first so every image points "
                "at a real cdn.bitpool.com URL."
            )
    for folder in ("email%20assets/", "email assets/", "Common%20resources/", "Common resources/"):
        for prefix in ('="', "='", "("):
            if prefix + folder in html or prefix + "../../" + folder in html:
                sys.exit(
                    f"Refusing to send ({context}): body still references the local "
                    f"{folder!r} folder, which only resolves on the machine that "
                    "drafted it. Run draft-marketing-email's publish rewrite first."
                )


def guard_no_sendgrid_tags(html, context):
    for token in ("<%asm_group_unsubscribe_raw_url%>", "<%asm_preferences_raw_url%>"):
        if token in html:
            sys.exit(
                f"Refusing to send ({context}): body contains {token!r} -- a "
                "SendGrid-only merge/unsubscribe tag with no meaning in a Graph send. "
                "It would render as broken literal text to the recipient. This looks "
                "like the SendGrid batch template was used by mistake -- use "
                "individual-template.html or graph-batch-template.html instead."
            )


def guard_no_bracket_placeholders(html, context):
    leftover = sorted(
        b for b in set(BRACKET_RE.findall(html)) if not MSO_CONDITIONAL_RE.match(b)
    )
    if leftover:
        sys.exit(
            f"Refusing to send ({context}): unfilled placeholder(s) still in the "
            f"body: {leftover}. Fill these in (or remove them) before sending."
        )


def render_row(html, row, context):
    def repl(m):
        col = m.group(1)
        if col not in row:
            sys.exit(
                f"Refusing to send ({context}): template references {{{{{col}}}}} "
                f"but the CSV has no '{col}' column. Columns found: {list(row.keys())}"
            )
        val = row[col].strip()
        if not val:
            sys.exit(
                f"Refusing to send ({context}): row for {row.get('email')} has an "
                f"empty '{col}' -- refusing to send a blank merge field."
            )
        return val

    return TOKEN_RE.sub(repl, html)


def load_recipients_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "email" not in reader.fieldnames:
            sys.exit(f"{path}: CSV must have an 'email' column. Found: {reader.fieldnames}")
        rows = list(reader)
    blank = [i + 2 for i, row in enumerate(rows) if not row.get("email", "").strip()]
    if blank:
        sys.exit(
            f"{path}: row(s) {blank} (1-indexed, header is row 1) have a blank "
            "'email' column -- refusing to send a partial batch. Fix or remove "
            "these rows."
        )
    if not rows:
        sys.exit(f"{path}: no data rows found.")
    return rows


def load_attachments(paths):
    """Returns (small, large). small: ready-to-embed fileAttachment dicts (base64
    already read into memory). large: {"path", "name", "contentType", "size"} dicts
    for files over SIMPLE_ATTACHMENT_BYTES, left unread on disk until the upload
    session actually needs them -- no point holding a 15 MB file in memory if the
    send fails a guard check first."""
    if not paths:
        return [], []
    small, large = [], []
    total = 0
    for path in paths:
        if not os.path.isfile(path):
            sys.exit(f"Refusing to send: attachment not found: {path}")
        size = os.path.getsize(path)
        total += size
        content_type, _ = mimetypes.guess_type(path)
        content_type = content_type or "application/octet-stream"
        name = os.path.basename(path)
        if size <= SIMPLE_ATTACHMENT_BYTES:
            with open(path, "rb") as f:
                content_bytes = base64.b64encode(f.read()).decode("ascii")
            small.append(
                {
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": name,
                    "contentType": content_type,
                    "contentBytes": content_bytes,
                }
            )
        else:
            large.append({"path": path, "name": name, "contentType": content_type, "size": size})
    if total > MAX_ATTACHMENT_BYTES:
        sys.exit(
            f"Refusing to send: attachments total {total / 1024 / 1024:.1f} MB, over "
            f"the {MAX_ATTACHMENT_BYTES / 1024 / 1024:.0f} MB combined cap."
        )
    return small, large


def build_message(subject, html, to_addr, reply_to, send_as):
    """Returns (message_dict, base_path). base_path is the /me or /users/{mailbox}
    root every subsequent call (draft create, attach, send, or plain sendMail) hangs
    off of."""
    message = {
        "subject": subject,
        "body": {"contentType": "HTML", "content": html},
        "toRecipients": [{"emailAddress": build_email(to_addr)}],
        # Matches the tenant's existing X-CodeTwoProcessed exclusion so the CodeTwo
        # mail-flow rule (signature stamping) skips this message -- it already has
        # its own authored signature baked into the HTML, and letting CodeTwo
        # reprocess it produced a second, corrupted copy during testing.
        "internetMessageHeaders": [{"name": "X-CodeTwoProcessed", "value": "exclude"}],
    }
    if reply_to:
        message["replyTo"] = [{"emailAddress": build_email(reply_to)}]

    if send_as:
        # /users/{mailbox}/... requires the signed-in user to hold Exchange "Send
        # As" (not "Send on Behalf") on that mailbox for the sendMail path, or
        # "Full Access" for the draft+attach+send path used with large attachments
        # -- plus the app's matching delegated scope (Mail.Send.Shared, or
        # Mail.ReadWrite.Shared). Setting "from" explicitly too, so the From header
        # is never ambiguous regardless of which path is used.
        message["from"] = {"emailAddress": build_email(send_as)}
        base_path = f"{GRAPH}/users/{send_as}"
    else:
        base_path = f"{GRAPH}/me"

    return message, base_path


def send_via_sendmail(access_token, message, base_path, small_attachments):
    """The original single-call path -- used whenever there are no large
    attachments, so behaviour for that (common) case is unchanged from before
    attachments existed at all."""
    if small_attachments:
        message = {**message, "attachments": small_attachments}
    return requests.post(
        f"{base_path}/sendMail",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        data=json.dumps({"message": message, "saveToSentItems": "true"}),
        timeout=30,
    )


def create_draft(access_token, message, base_path):
    return requests.post(
        f"{base_path}/messages",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        data=json.dumps(message),
        timeout=30,
    )


def attach_small(access_token, base_path, message_id, attachment):
    return requests.post(
        f"{base_path}/messages/{message_id}/attachments",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        data=json.dumps(attachment),
        timeout=30,
    )


def attach_large(access_token, base_path, message_id, attachment):
    session_resp = requests.post(
        f"{base_path}/messages/{message_id}/attachments/createUploadSession",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        data=json.dumps(
            {
                "AttachmentItem": {
                    "attachmentType": "file",
                    "name": attachment["name"],
                    "size": attachment["size"],
                    "contentType": attachment["contentType"],
                }
            }
        ),
        timeout=30,
    )
    if session_resp.status_code not in (200, 201):
        return session_resp

    upload_url = session_resp.json()["uploadUrl"]
    total = attachment["size"]
    resp = session_resp
    with open(attachment["path"], "rb") as f:
        start = 0
        while start < total:
            chunk = f.read(UPLOAD_CHUNK_BYTES)
            end = start + len(chunk) - 1
            # Graph's docs are explicit: do NOT send the Authorization header to
            # the upload URL itself -- it's a pre-authenticated, short-lived URL.
            resp = requests.put(
                upload_url,
                headers={
                    "Content-Length": str(len(chunk)),
                    "Content-Range": f"bytes {start}-{end}/{total}",
                },
                data=chunk,
                timeout=60,
            )
            if resp.status_code not in (200, 201, 202):
                return resp
            start += len(chunk)
    return resp


def send_draft(access_token, base_path, message_id):
    return requests.post(
        f"{base_path}/messages/{message_id}/send",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=30,
    )


def send_message(access_token, subject, html, to_addr, reply_to, send_as, small_attachments, large_attachments):
    """Returns (resp, stage). stage is None on success, or a short label
    identifying which step failed (draft creation, a specific attachment, or the
    final send) so the caller can report a precise error instead of a bare status
    code."""
    message, base_path = build_message(subject, html, to_addr, reply_to, send_as)

    if not large_attachments:
        return send_via_sendmail(access_token, message, base_path, small_attachments), None

    draft_resp = create_draft(access_token, message, base_path)
    if draft_resp.status_code not in (200, 201):
        return draft_resp, "draft creation"
    message_id = draft_resp.json()["id"]

    for attachment in small_attachments:
        resp = attach_small(access_token, base_path, message_id, attachment)
        if resp.status_code not in (200, 201):
            return resp, f"attaching {attachment['name']}"

    for attachment in large_attachments:
        resp = attach_large(access_token, base_path, message_id, attachment)
        if resp.status_code not in (200, 201):
            return resp, f"attaching {attachment['name']}"

    send_resp = send_draft(access_token, base_path, message_id)
    if send_resp.status_code != 202:
        return send_resp, "sending the draft"
    return send_resp, None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--html-file", required=True, help="Path to the published (CDN-linked) HTML body")
    parser.add_argument("--to", default="", help="Individual mode: comma-separated recipients, e.g. 'Jane <jane@x.com>, bob@y.com'")
    parser.add_argument("--csv", default="", help="Batch mode: CSV with an 'email' column plus any {{merge}} columns the template uses")
    parser.add_argument("--reply-to", default="", help="Reply-To address, if different from the signed-in mailbox")
    parser.add_argument(
        "--send-as",
        default="",
        help="Shared mailbox to send AS, e.g. partners@bitpool.com. Requires Exchange "
        "Send As on that mailbox for the signing-in user, plus Mail.Send.Shared on the "
        "app registration. ALWAYS ask the user for this address fresh -- never assume "
        "or default it, even on a repeat send.",
    )
    parser.add_argument(
        "--attach",
        action="append",
        default=[],
        help="Path to a local file to attach -- repeatable for multiple attachments. "
        "The same set is attached to every recipient's copy. Combined size is capped "
        f"at {MAX_ATTACHMENT_BYTES // (1024 * 1024)} MB; any single file over "
        f"{SIMPLE_ATTACHMENT_BYTES // (1024 * 1024)} MB switches that send to Graph's "
        "draft+upload-session flow automatically.",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Validate the template/CSV and report readiness. No sign-in, no network, no send.",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Required to actually send. Only pass after the user has explicitly approved this exact send.",
    )
    args = parser.parse_args()

    if bool(args.to) == bool(args.csv):
        sys.exit("Pass exactly one of --to (individual) or --csv (batch).")

    with open(args.html_file, encoding="utf-8") as f:
        template = f.read()

    guard_no_local_paths(template, "template")
    guard_no_sendgrid_tags(template, "template")

    if args.csv:
        rows = load_recipients_csv(args.csv)
        rendered = []
        for row in rows:
            ctx = f"row for {row['email']}"
            body = render_row(template, row, ctx)
            guard_no_bracket_placeholders(body, ctx)
            rendered.append((row["email"].strip(), body))
        recipients_desc = f"{len(rendered)} recipient(s) from {args.csv}"
    else:
        stray = sorted(set(TOKEN_RE.findall(template)))
        if stray:
            sys.exit(
                f"Refusing to send (template): merge token(s) {stray} found, but "
                "this is an individual send (--to, no --csv) -- there's no CSV to "
                "fill them from. This looks like a batch template used by mistake, "
                "or you meant to pass --csv."
            )
        guard_no_bracket_placeholders(template, "template")
        addrs = [a.strip() for a in args.to.split(",") if a.strip()]
        if not addrs:
            sys.exit("Refusing to send: no recipients in --to.")
        rendered = [(a, template) for a in addrs]
        recipients_desc = f"{len(rendered)} recipient(s): {', '.join(a for a, _ in rendered)}"

    small_attachments, large_attachments = load_attachments(args.attach)

    if args.check_only:
        send_as_desc = f" Sending as: {args.send_as}." if args.send_as else ""
        total_attach = len(small_attachments) + len(large_attachments)
        if total_attach:
            path_desc = (
                " (draft+upload-session flow, needs Mail.ReadWrite"
                + (".Shared + Exchange Full Access" if args.send_as else "")
                + ")"
                if large_attachments
                else ""
            )
            attach_desc = f" {total_attach} attachment(s), within size limit{path_desc}."
        else:
            attach_desc = ""
        print(f"OK -- {recipients_desc}.{send_as_desc}{attach_desc} Guards clean, ready for --confirm.")
        return

    if not args.confirm:
        sys.exit(
            "Refusing to send: this performs a REAL send. Re-run with --confirm only "
            "after the user has explicitly approved this exact recipient list, "
            "subject, and body."
        )

    scope_parts = [MAIL_SEND_SCOPE]
    if args.send_as:
        scope_parts.append(MAIL_SEND_SHARED_SCOPE)
    if large_attachments:
        # The draft+upload-session+send flow needs ReadWrite, not just Send --
        # creating and modifying a message resource is a different scope than the
        # sendMail action.
        scope_parts.append(MAIL_READWRITE_SCOPE)
        if args.send_as:
            scope_parts.append(MAIL_READWRITE_SHARED_SCOPE)
    scope = " ".join(scope_parts)
    access_token = interactive_login(scope)
    identity = whoami(access_token)
    if identity:
        mail, name = identity
        if args.send_as:
            print(f"Signed in as: {name} <{mail}> -- sending will be FROM {args.send_as} (Send As).", flush=True)
        else:
            print(f"Signed in as: {name} <{mail}> -- sending will be FROM this mailbox.", flush=True)
    else:
        print("Signed in, but could not confirm identity via /me.", flush=True)

    sent, failed = [], []
    for addr, body in rendered:
        resp, stage = send_message(
            access_token, args.subject, body, addr, args.reply_to, args.send_as,
            small_attachments, large_attachments,
        )
        if stage is None and resp.status_code == 202:
            sent.append(addr)
            print(f"SENT -> {addr}", flush=True)
        elif resp.status_code == 403 and args.send_as:
            failed.append((addr, resp.status_code, resp.text))
            stage_desc = f" (at: {stage})" if stage else ""
            needs = "Mail.ReadWrite.Shared + Exchange Full Access" if large_attachments else "Mail.Send.Shared"
            print(
                f"FAILED -> {addr}: 403 sending as {args.send_as}{stage_desc}. Likely "
                f"missing the right Exchange permission on that mailbox (Send As, or "
                f"Full Access if attachments are large), or the app registration is "
                f"missing delegated {needs} (with admin consent). Response: {resp.text}",
                flush=True,
            )
        else:
            failed.append((addr, resp.status_code, resp.text))
            stage_desc = f" (at: {stage})" if stage else ""
            print(f"FAILED -> {addr}{stage_desc}: {resp.status_code} {resp.text}", flush=True)

    print(f"\nDone: {len(sent)} sent, {len(failed)} failed.", flush=True)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
