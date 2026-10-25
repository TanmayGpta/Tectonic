"""Telegram push notifications for the senior on-call engineer.

Used by CI after the CLI runs:
    python -m notifier.telegram fix --summary tectonic_summary.json --pr-url <url> --run-url <url>
    python -m notifier.telegram escalate --summary tectonic_summary.json --run-url <url>

Never raises: a missing token or a Telegram outage must not break the pipeline.
"""
import os
import sys
import json
import html
import argparse
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://api.telegram.org/bot{token}/{method}"
MAX_SNIPPET = 600  # Telegram caps messages at 4096 chars; keep alerts glanceable


def telegram_api(method, payload, timeout=15):
    """Calls a Bot API method. Returns the parsed response, or None on any failure."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("⚠️ [Notifier]: TELEGRAM_BOT_TOKEN not set, skipping Telegram call.")
        return None
    try:
        resp = requests.post(API_URL.format(token=token, method=method), json=payload, timeout=timeout)
        data = resp.json()
        if not data.get("ok"):
            print(f"⚠️ [Notifier]: Telegram rejected '{method}': {data.get('description')}")
            return None
        return data
    except Exception as e:
        print(f"⚠️ [Notifier]: Telegram call '{method}' failed: {e}")
        return None


def send_message(text, buttons=None, chat_id=None):
    """Sends an HTML message. `buttons` is a list of rows of InlineKeyboardButton dicts."""
    chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
    if not chat_id:
        print("⚠️ [Notifier]: TELEGRAM_CHAT_ID not set, skipping notification.")
        return None
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    if buttons:
        payload["reply_markup"] = {"inline_keyboard": buttons}
    return telegram_api("sendMessage", payload)


def _snippet(text, limit=MAX_SNIPPET):
    text = (text or "").strip()
    if len(text) > limit:
        text = text[:limit].rstrip() + "\n…"
    return html.escape(text)


def _root_cause(explanation):
    """First meaningful line of the XAI markdown, stripped of markdown noise."""
    for line in (explanation or "").splitlines():
        line = line.strip().lstrip("#*->` ").strip()
        if len(line) > 20:
            return line
    return "See PR for the full diagnostic audit."


def build_fix_message(summary, pr_url, run_url=None):
    pr_number = pr_url.rstrip("/").rsplit("/", 1)[-1]
    text = (
        "✅ <b>Tectonic auto-healed an outage</b>\n\n"
        f"📄 <b>File:</b> <code>{html.escape(summary.get('file', '?'))}</code>\n"
        f"🧪 <b>Sandbox:</b> passed after {summary.get('attempts', '?')} attempt(s)\n"
        f"🧠 <b>Root cause:</b> {_snippet(_root_cause(summary.get('explanation')), 300)}\n\n"
        f"<b>Diff:</b>\n<pre>{_snippet(summary.get('diff'))}</pre>\n"
        f"Review required on PR #{html.escape(pr_number)}."
    )
    buttons = [
        [{"text": "✅ Approve & Merge", "callback_data": f"merge:{pr_number}"},
         {"text": "❌ Reject", "callback_data": f"close:{pr_number}"}],
        [{"text": "🔍 View PR", "url": pr_url},
         {"text": "📝 View Diff", "url": f"{pr_url.rstrip('/')}/files"}],
    ]
    if run_url:
        buttons.append([{"text": "⚙️ CI Run", "url": run_url}])
    return text, buttons


def build_escalation_message(summary, run_url=None):
    reason = summary.get("rejection_reason") or "Sandbox validation kept failing after all retries."
    text = (
        "🚨 <b>HUMAN NEEDED: auto-remediation failed</b>\n\n"
        f"📄 <b>File:</b> <code>{html.escape(summary.get('file', '?'))}</code>\n"
        f"🔁 <b>Attempts:</b> {summary.get('attempts', 0)}\n"
        f"🛑 <b>Reason:</b> {_snippet(reason, 300)}\n\n"
        f"<b>Original error:</b>\n<pre>{_snippet(summary.get('error_logs'))}</pre>"
    )
    if summary.get("sandbox_logs"):
        text += f"\n<b>Last sandbox output:</b>\n<pre>{_snippet(summary.get('sandbox_logs'), 400)}</pre>"
    buttons = [[{"text": "⚙️ Open CI Run", "url": run_url}]] if run_url else None
    return text, buttons


def _load_summary(path, fallback_file=None):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        # CLI crashed before writing a summary; still page the engineer
        return {"file": fallback_file or "?", "rejection_reason": "Tectonic CLI crashed before producing a summary."}


def main():
    parser = argparse.ArgumentParser(description="Tectonic Telegram notifier")
    parser.add_argument("event", choices=["fix", "escalate"])
    parser.add_argument("--summary", default="tectonic_summary.json")
    parser.add_argument("--file", help="Target file, used if the summary is missing")
    parser.add_argument("--pr-url")
    parser.add_argument("--run-url")
    args = parser.parse_args()

    summary = _load_summary(args.summary, args.file)
    if args.event == "fix":
        if not args.pr_url:
            print("⚠️ [Notifier]: --pr-url is required for 'fix'.")
            return
        text, buttons = build_fix_message(summary, args.pr_url, args.run_url)
    else:
        text, buttons = build_escalation_message(summary, args.run_url)

    if send_message(text, buttons):
        print(f"📱 [Notifier]: '{args.event}' alert pushed to Telegram.")


if __name__ == "__main__":
    main()
    sys.exit(0)
