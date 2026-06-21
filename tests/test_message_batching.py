"""
Tests for message batching helpers in chat_commands.
"""

import asyncio as _real_asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock


def _fake_message(content="", attachments=None, stickers=None, embeds=None):
    """Lightweight stand-in for discord.Message with the attrs the builders read."""
    author = SimpleNamespace(
        id=123,
        display_name="Alice",
        roles=[],
        guild_permissions=[],
    )
    channel = SimpleNamespace(id=456, name="general")
    return SimpleNamespace(
        author=author,
        channel=channel,
        id=789,
        clean_content=content,
        content=content,
        embeds=embeds or [],
        attachments=attachments or [],
        stickers=stickers or [],
        mentions=[],
        role_mentions=[],
        guild=None,
        created_at=SimpleNamespace(isoformat=lambda: "2026-01-01T00:00:00"),
        type="default",
    )


def _fake_sticker(name, fmt):
    return SimpleNamespace(name=name, url=f"https://cdn/{name}.png", format=SimpleNamespace(name=fmt))


class TestMergeBurstMessages:
    def test_single_message_unchanged(self):
        from dango.commands.chat_commands import _merge_burst_messages

        data = _merge_burst_messages([_fake_message("hello")], bot_user_id=999)
        assert data["content"] == "hello"

    def test_contents_joined_in_order(self):
        from dango.commands.chat_commands import _merge_burst_messages

        msgs = [_fake_message("part one"), _fake_message("part two"), _fake_message("part three")]
        data = _merge_burst_messages(msgs, bot_user_id=999)
        assert data["content"] == "part one\npart two\npart three"

    def test_empty_followup_skipped(self):
        from dango.commands.chat_commands import _merge_burst_messages

        # second message has no text (e.g. image-only) — no blank line injected
        msgs = [_fake_message("question"), _fake_message("")]
        data = _merge_burst_messages(msgs, bot_user_id=999)
        assert data["content"] == "question"

    def test_stickers_unioned_across_burst(self):
        from dango.commands.chat_commands import _merge_burst_messages

        msgs = [
            _fake_message("hi", stickers=[_fake_sticker("wave", "png")]),
            _fake_message("again", stickers=[_fake_sticker("party", "apng")]),
        ]
        data = _merge_burst_messages(msgs, bot_user_id=999)
        names = [s["name"] for s in data["stickers"]]
        assert names == ["wave", "party"]


# ── Debounce behaviour, proven against a virtual clock (no Discord, no wall time) ──

AUTHOR_ID = 111
CHANNEL_ID = 222
KEY = (CHANNEL_ID, AUTHOR_ID)


class _Typing:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


def _cog_message(mid: int, content: str):
    """A discord.Message-like object that survives _build_message_data + the cog path."""
    author = SimpleNamespace(id=AUTHOR_ID, display_name="Alice", roles=[], guild_permissions=[])
    channel = SimpleNamespace(id=CHANNEL_ID, name="general", typing=lambda: _Typing())
    return SimpleNamespace(
        author=author,
        channel=channel,
        id=mid,
        clean_content=content,
        content=content,
        embeds=[],
        attachments=[],
        stickers=[],
        mentions=[],
        role_mentions=[],
        guild=None,
        reference=None,
        created_at=SimpleNamespace(isoformat=lambda: "2026-01-01T00:00:00"),
        type="default",
    )


class _Clock:
    """Virtual monotonic clock advanced only by (fake) sleeps."""

    def __init__(self):
        self.t = 0.0

    def monotonic(self):
        return self.t


def _install_virtual_time(monkeypatch, cc, window, max_wait, on_sleep=None):
    """Replace the module's time + asyncio.sleep with a deterministic virtual clock.

    create_task stays real so the debounce task actually runs on the loop; only
    the passage of time is simulated, so the sliding-window / max-wait maths is
    exercised exactly, with zero wall-clock dependence (and zero flakiness).
    """
    clock = _Clock()

    async def fake_sleep(duration):
        clock.t += duration
        if on_sleep:
            on_sleep()
        await _real_asyncio.sleep(0)  # yield so concurrent appends interleave

    monkeypatch.setattr(cc, "time", SimpleNamespace(monotonic=clock.monotonic))
    monkeypatch.setattr(
        cc, "asyncio", SimpleNamespace(sleep=fake_sleep, create_task=_real_asyncio.create_task)
    )
    monkeypatch.setattr(cc, "ENABLE_MESSAGE_BATCHING", True)
    monkeypatch.setattr(cc, "MESSAGE_BATCH_WINDOW", window)
    monkeypatch.setattr(cc, "MESSAGE_BATCH_MAX_WAIT", max_wait)
    return clock


def _make_cog(arun_mock):
    from dango.commands.chat_commands import ChatCog

    bot = SimpleNamespace(user=SimpleNamespace(id=999, mentioned_in=lambda m: False))
    workflow = SimpleNamespace(arun=arun_mock)
    runtime = SimpleNamespace(
        allowed_users=set(),
        allowed_channels={CHANNEL_ID},
        history_limit=10,
        timezone="UTC",
    )
    return ChatCog(bot, workflow, "sys", runtime)


def _sent_contents(arun_mock):
    return [call.kwargs["input"]["content"] for call in arun_mock.await_args_list]


class TestDebounceBehaviour:
    def test_rapid_messages_merge_into_one_run(self, monkeypatch):
        """Three messages within the window → one workflow run, contents joined."""
        import dango.commands.chat_commands as cc

        _install_virtual_time(monkeypatch, cc, window=1.0, max_wait=5.0)
        arun = AsyncMock()
        cog = _make_cog(arun)

        async def scenario():
            await cog.on_message(_cog_message(1, "a"))
            task = cog._bursts[KEY]["task"]
            # arrive before the debounce task gets a turn to run → folded in
            await cog.on_message(_cog_message(2, "b"))
            await cog.on_message(_cog_message(3, "c"))
            await task

        _real_asyncio.run(scenario())

        assert arun.await_count == 1
        assert _sent_contents(arun) == ["a\nb\nc"]

    def test_spaced_messages_run_separately(self, monkeypatch):
        """Each burst that fully fires before the next message → separate runs."""
        import dango.commands.chat_commands as cc

        _install_virtual_time(monkeypatch, cc, window=1.0, max_wait=5.0)
        arun = AsyncMock()
        cog = _make_cog(arun)

        async def scenario():
            await cog.on_message(_cog_message(1, "a"))
            await cog._bursts[KEY]["task"]          # let the first burst fire
            await cog.on_message(_cog_message(2, "b"))
            await cog._bursts[KEY]["task"]          # and the second

        _real_asyncio.run(scenario())

        assert arun.await_count == 2
        assert _sent_contents(arun) == ["a", "b"]

    def test_max_wait_caps_nonstop_typing(self, monkeypatch):
        """A user who never pauses still gets answered once the cap is hit."""
        import dango.commands.chat_commands as cc

        state = {"cog": None, "n": 0}

        def keep_typing():
            # Simulate a new message landing during every sleep window.
            if state["n"] >= 20:
                return
            state["n"] += 1
            burst = state["cog"]._bursts.get(KEY)
            if burst:
                burst["messages"].append(_cog_message(100 + state["n"], f"x{state['n']}"))
                burst["dirty"] = True

        _install_virtual_time(monkeypatch, cc, window=1.0, max_wait=2.5, on_sleep=keep_typing)
        arun = AsyncMock()
        cog = _make_cog(arun)
        state["cog"] = cog

        async def scenario():
            await cog.on_message(_cog_message(1, "start"))
            await cog._bursts[KEY]["task"]

        _real_asyncio.run(scenario())

        # Cap fired exactly once despite endless input (didn't hang on the slide).
        assert arun.await_count == 1
        lines = _sent_contents(arun)[0].split("\n")
        assert lines[0] == "start"
        # window 1.0 / max_wait 2.5 → folds in the messages from the 3 sleeps before the cap.
        assert lines == ["start", "x1", "x2", "x3"]
