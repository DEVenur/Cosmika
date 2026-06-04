"""
Send the LLM response (text + table images + table files) to Discord.
"""

import os

import discord
from agno.workflow import StepInput, StepOutput

from ..utils.discord_helpers import split_message


async def send_discord_response(step_input: StepInput, _bot=None) -> StepOutput:
    """Send text and image attachments to the Discord channel."""
    data = step_input.previous_step_content
    message_data = data["message_data"]
    bot = message_data["_bot"]

    channel_id = message_data["channel_id"]
    message_id = message_data.get("message_id")

    if data.get("error"):
        response_text = data.get("error_message", "An error occurred while processing your message.")
        table_images = []
        extracted_tables_files = []
    else:
        response_text = data.get("response_text") or data.get("llm_response", "No response generated")
        table_images = data.get("table_images", [])
        extracted_tables_files = data.get("extracted_tables_files", [])

    print(
        f"📤 [send_discord_response] Sending to channel {channel_id}, {len(table_images)} images"
    )

    channel = bot.get_channel(channel_id)
    if not channel:
        try:
            channel = await bot.fetch_channel(channel_id)
        except (discord.NotFound, discord.Forbidden) as e:
            print(f"❌ [send_discord_response] Cannot access channel: {e}")
            return StepOutput(content="failed")

    try:
        files = []
        for img_data in table_images:
            files.append(discord.File(img_data["buffer"], filename=img_data["filename"]))
        for table_file in extracted_tables_files:
            if os.path.exists(table_file):
                files.append(discord.File(table_file, filename=os.path.basename(table_file)))

        message_chunks = split_message(response_text)

        original_message = None
        if message_id:
            try:
                original_message = await channel.fetch_message(message_id)
            except (discord.NotFound, discord.Forbidden):
                pass

        if not message_chunks:
            if files:
                if original_message:
                    await original_message.reply(files=files)
                else:
                    await channel.send(files=files)
        elif len(message_chunks) == 1:
            if original_message:
                await original_message.reply(content=message_chunks[0], files=files)
            else:
                await channel.send(content=message_chunks[0], files=files)
        else:
            if original_message:
                await original_message.reply(message_chunks[0])
            else:
                await channel.send(message_chunks[0])
            for chunk in message_chunks[1:-1]:
                await channel.send(chunk)
            await channel.send(content=message_chunks[-1], files=files)

        # Fallback sysinfo — sent as a separate message after the main response.
        fallback_sysinfo = data.get("fallback_sysinfo")
        if fallback_sysinfo:
            await channel.send(fallback_sysinfo)

        # Clean up temp table files
        for table_file in extracted_tables_files:
            try:
                if os.path.exists(table_file):
                    os.remove(table_file)
            except Exception:
                pass

        print("✅ [send_discord_response] Message sent successfully")
        return StepOutput(content="sent")

    except (discord.Forbidden, discord.HTTPException) as e:
        print(f"❌ [send_discord_response] Failed to send message: {e}")
        return StepOutput(content="failed")
