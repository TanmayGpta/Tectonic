"""Long-polling Telegram bot that turns alert buttons into real GitHub actions.

Run alongside the console:  python -m notifier.telegram_bot
Needs TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, GITHUB_REPO (owner/repo) and a
GITHUB_TOKEN PAT with `pull_requests: write` + `contents: write` on that repo.
"""
import os
import time
import requests
from dotenv import load_dotenv

from notifier.telegram import telegram_api, send_message

load_dotenv()

GITHUB_API = "https://api.github.com/repos/{repo}/pulls/{number}"


def github_pr_action(action, pr_number):
    """Merges or closes a PR. Returns (ok, human-readable message)."""
    repo, token = os.getenv("GITHUB_REPO"), os.getenv("GITHUB_TOKEN")
    if not repo or not token:
        return False, "GITHUB_REPO / GITHUB_TOKEN not configured on the bot host."
    url = GITHUB_API.format(repo=repo, number=pr_number)
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    try:
        if action == "merge":
            resp = requests.put(f"{url}/merge", headers=headers, timeout=15,
                                json={"merge_method": "squash", "commit_title": f"Tectonic auto-heal (#{pr_number})"})
        else:
            resp = requests.patch(url, headers=headers, timeout=15, json={"state": "closed"})
    except Exception as e:
        return False, f"GitHub unreachable: {e}"
    if resp.ok:
        return True, f"PR #{pr_number} {'merged' if action == 'merge' else 'closed'}."
    return False, f"GitHub refused ({resp.status_code}): {resp.json().get('message', resp.text)[:200]}"


def handle_callback(query):
    """Handles a button tap. Only the configured on-call chat may act on PRs."""
    allowed = str(os.getenv("TELEGRAM_CHAT_ID", ""))
    chat_id = str(query.get("message", {}).get("chat", {}).get("id", ""))
    user = query.get("from", {}).get("first_name", "someone")

    if not allowed or chat_id != allowed:
        telegram_api("answerCallbackQuery", {"callback_query_id": query["id"], "text": "⛔ Not authorised."})
        return

    action, _, pr_number = query.get("data", "").partition(":")
    if action not in ("merge", "close") or not pr_number.isdigit():
        telegram_api("answerCallbackQuery", {"callback_query_id": query["id"], "text": "Unknown action."})
        return

    print(f"📲 [Telegram Bot]: {user} tapped '{action}' on PR #{pr_number}")
    ok, msg = github_pr_action(action, pr_number)
    telegram_api("answerCallbackQuery", {"callback_query_id": query["id"], "text": msg[:200], "show_alert": not ok})

    if ok:
        # Swap the action buttons for an audit stamp so the PR can't be actioned twice
        stamp = "✅ Approved & merged" if action == "merge" else "❌ Rejected & closed"
        message = query["message"]
        telegram_api("editMessageText", {
            "chat_id": message["chat"]["id"],
            "message_id": message["message_id"],
            "text": f"{message.get('text', '')}\n\n{stamp} by {user}",
        })


def handle_message(message):
    """`/start` or `/id` replies with the chat id, which is what TELEGRAM_CHAT_ID needs to be."""
    text = message.get("text", "")
    if text.startswith(("/start", "/id")):
        chat_id = message["chat"]["id"]
        send_message(f"🌋 Tectonic on-call bot online.\nYour chat id: <code>{chat_id}</code>", chat_id=chat_id)


def run():
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        print("❌ [Telegram Bot]: TELEGRAM_BOT_TOKEN not set.")
        return
    print("🤖 [Telegram Bot]: Listening for on-call actions (Ctrl+C to stop)...")
    offset = None
    while True:
        payload = {"timeout": 30, "allowed_updates": ["message", "callback_query"]}
        if offset:
            payload["offset"] = offset
        data = telegram_api("getUpdates", payload, timeout=40)
        if not data:
            time.sleep(5)
            continue
        for update in data.get("result", []):
            offset = update["update_id"] + 1
            if "callback_query" in update:
                handle_callback(update["callback_query"])
            elif "message" in update:
                handle_message(update["message"])


if __name__ == "__main__":
    run()
