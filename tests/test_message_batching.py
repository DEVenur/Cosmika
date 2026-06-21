"""
Tests for message batching helpers in chat_commands.
"""

from types import SimpleNamespace


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
