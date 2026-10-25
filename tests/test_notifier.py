import notifier.telegram as telegram
import notifier.telegram_bot as bot
from notifier.telegram import build_fix_message, build_escalation_message, send_message


def test_fix_message_has_approve_buttons_and_escapes_html():
    summary = {"file": "main.tf", "attempts": 2, "diff": "-a <b>\n+b", "explanation": "## Root cause: missing closing brace in resource block"}
    text, buttons = build_fix_message(summary, "https://github.com/o/r/pull/42", "https://run")
    assert "&lt;b&gt;" in text  # diff content must not break Telegram HTML parsing
    assert "missing closing brace" in text
    assert buttons[0][0]["callback_data"] == "merge:42"
    assert buttons[0][1]["callback_data"] == "close:42"
    assert buttons[1][1]["url"].endswith("/pull/42/files")


def test_escalation_message_falls_back_to_generic_reason():
    text, buttons = build_escalation_message({"file": "docker-compose.yml", "attempts": 3}, None)
    assert "HUMAN NEEDED" in text
    assert "all retries" in text
    assert buttons is None


def test_send_message_is_noop_without_credentials(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    monkeypatch.setattr(telegram.requests, "post", lambda *a, **k: (_ for _ in ()).throw(AssertionError("network call")))
    assert send_message("hi") is None


def test_callback_from_unknown_chat_cannot_merge(monkeypatch):
    calls = []
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "111")
    monkeypatch.setattr(bot, "telegram_api", lambda method, payload, **k: calls.append(method))
    monkeypatch.setattr(bot, "github_pr_action", lambda *a: (_ for _ in ()).throw(AssertionError("must not merge")))
    bot.handle_callback({"id": "q1", "data": "merge:42", "message": {"chat": {"id": 999}}, "from": {}})
    assert calls == ["answerCallbackQuery"]


def test_callback_from_oncall_chat_merges_and_stamps(monkeypatch):
    calls = []
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "111")
    monkeypatch.setattr(bot, "telegram_api", lambda method, payload, **k: calls.append((method, payload)))
    monkeypatch.setattr(bot, "github_pr_action", lambda action, n: (True, f"PR #{n} merged."))
    msg = {"chat": {"id": 111}, "message_id": 7, "text": "alert"}
    bot.handle_callback({"id": "q1", "data": "merge:42", "message": msg, "from": {"first_name": "Senior"}})
    assert [c[0] for c in calls] == ["answerCallbackQuery", "editMessageText"]
    assert "merged by Senior" in calls[1][1]["text"]
