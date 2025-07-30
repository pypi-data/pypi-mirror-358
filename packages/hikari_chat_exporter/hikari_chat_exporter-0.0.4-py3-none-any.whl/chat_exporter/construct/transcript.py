import html
import re
import traceback
from datetime import datetime
from zoneinfo import ZoneInfo

import hikari

from chat_exporter.construct.assets.component import Component
from chat_exporter.construct.attachment_handler import AttachmentHandler
from chat_exporter.construct.message import gather_messages
from chat_exporter.ext.cache import clear_cache
from chat_exporter.ext.discord_utils import DiscordUtils
from chat_exporter.ext.html_generator import (
    PARSE_MODE_HTML_SAFE,
    PARSE_MODE_NONE,
    channel_subject,
    channel_topic,
    fancy_time,
    fill_out,
    meta_data_temp,
    total,
)
from chat_exporter.parse.mention import pass_bot


class TranscriptDAO:
    html: str

    def __init__(
        self,
        channel: hikari.TextableGuildChannel,
        limit: int | None,
        messages: list[hikari.Message] | None,
        zoneinfo: ZoneInfo,
        military_time: bool,
        fancy_times: bool,
        before: datetime | None,
        after: datetime | None,
        support_dev: bool,
        bot: hikari.GatewayBot | hikari.RESTBot | None,
        attachment_handler: AttachmentHandler | None,
    ):
        self.channel: hikari.TextableGuildChannel = channel
        self.messages: list[hikari.Message] | None = messages
        self.limit: int | None = int(limit) if limit else None
        self.military_time: bool = military_time
        self.fancy_times: bool = fancy_times
        self.before: datetime | None = before
        self.after: datetime | None = after
        self.support_dev: bool = support_dev
        self.zoneinfo: ZoneInfo = zoneinfo
        self.attachment_handler: AttachmentHandler | None = attachment_handler

        if bot:
            pass_bot(bot)

    async def build_transcript(self):
        guild: hikari.Guild | None = self.channel.get_guild()

        if guild is None:
            return

        message_html, meta_data = await gather_messages(
            self.messages,
            guild,
            self.zoneinfo,
            self.military_time,
            self.attachment_handler,
        )
        await self.export_transcript(message_html, meta_data)
        clear_cache()
        Component.menu_div_id = 0
        return self

    async def export_transcript(self, message_html: str, meta_data: dict):
        guild: hikari.Guild | None = self.channel.get_guild()

        if guild is None:
            return

        guild_icon = (
            guild.make_icon_url()
            if (guild.make_icon_url() and len(str(guild.make_icon_url())) > 2)
            else DiscordUtils.default_avatar
        )

        guild_name = html.escape(guild.name)

        if self.military_time:
            time_now = datetime.now(self.zoneinfo).strftime("%e %B %Y at %H:%M:%S (%Z)")
        else:
            time_now = datetime.now(self.zoneinfo).strftime("%e %B %Y at %I:%M:%S %p (%Z)")

        meta_data_html: str = ""
        for data in meta_data:
            creation_time = meta_data[int(data)][1].astimezone(self.zoneinfo).strftime("%b %d, %Y")
            joined_time = (
                meta_data[int(data)][5].astimezone(self.zoneinfo).strftime("%b %d, %Y")
                if meta_data[int(data)][5]
                else "Unknown"
            )

            pattern = r"^#\d{4}"
            discrim = str(meta_data[int(data)][0][-5:])
            user = str(meta_data[int(data)][0])

            meta_data_html += await fill_out(
                guild,
                meta_data_temp,
                [
                    ("USER_ID", str(data), PARSE_MODE_NONE),
                    (
                        "USERNAME",
                        user[:-5] if re.match(pattern, discrim) else user,
                        PARSE_MODE_NONE,
                    ),
                    ("DISCRIMINATOR", discrim if re.match(pattern, discrim) else ""),
                    ("BOT", str(meta_data[int(data)][2]), PARSE_MODE_NONE),
                    ("CREATED_AT", str(creation_time), PARSE_MODE_NONE),
                    ("JOINED_AT", str(joined_time), PARSE_MODE_NONE),
                    ("GUILD_ICON", str(guild_icon), PARSE_MODE_NONE),
                    ("DISCORD_ICON", str(DiscordUtils.logo), PARSE_MODE_NONE),
                    ("MEMBER_ID", str(data), PARSE_MODE_NONE),
                    ("USER_AVATAR", str(meta_data[int(data)][3]), PARSE_MODE_NONE),
                    ("DISPLAY", str(meta_data[int(data)][6]), PARSE_MODE_NONE),
                    ("MESSAGE_COUNT", str(meta_data[int(data)][4])),
                ],
            )

        if self.military_time:
            channel_creation_time = self.channel.created_at.astimezone(self.zoneinfo).strftime(
                "%b %d, %Y (%H:%M:%S)"
            )
        else:
            channel_creation_time = self.channel.created_at.astimezone(self.zoneinfo).strftime(
                "%b %d, %Y (%I:%M:%S %p)"
            )

        raw_channel_topic = "TOPIC"
        channel_topic_html = ""
        if raw_channel_topic:
            channel_topic_html = await fill_out(
                guild,
                channel_topic,
                [("CHANNEL_TOPIC", html.escape(raw_channel_topic))],
            )

        limit = "start"
        if self.limit:
            limit = f"latest {self.limit} messages"

        subject = await fill_out(
            guild,
            channel_subject,
            [
                ("LIMIT", limit, PARSE_MODE_NONE),
                ("CHANNEL_NAME", self.channel.name),
                ("RAW_CHANNEL_TOPIC", str(raw_channel_topic)),
            ],
        )

        sd = (
            (
                '<div class="meta__support">    <a href="patreon.com/user?u=54005804">DONATE</a></div>'
            )
            if self.support_dev
            else ""
        )

        _fancy_time = ""

        if self.fancy_times:
            if self.military_time:
                time_format = "HH:mm"
            else:
                time_format = "hh:mm A"

            _fancy_time = await fill_out(
                guild,
                fancy_time,
                [
                    ("TIME_FORMAT", time_format, PARSE_MODE_NONE),
                    ("TIMEZONE", str(self.zoneinfo), PARSE_MODE_NONE),
                ],
            )

        self.html = await fill_out(
            guild,
            total,
            [
                ("SERVER_NAME", f"{guild_name}"),
                ("GUILD_ID", str(guild.id), PARSE_MODE_NONE),
                ("SERVER_AVATAR_URL", str(guild_icon), PARSE_MODE_NONE),
                ("CHANNEL_NAME", f"{self.channel.name}"),
                ("MESSAGE_COUNT", str(len(self.messages or []))),
                ("MESSAGES", message_html, PARSE_MODE_NONE),
                ("META_DATA", meta_data_html, PARSE_MODE_NONE),
                ("DATE_TIME", str(time_now)),
                ("SUBJECT", subject, PARSE_MODE_NONE),
                ("CHANNEL_CREATED_AT", str(channel_creation_time), PARSE_MODE_NONE),
                ("CHANNEL_TOPIC", str(channel_topic_html), PARSE_MODE_NONE),
                ("CHANNEL_ID", str(self.channel.id), PARSE_MODE_NONE),
                ("MESSAGE_PARTICIPANTS", str(len(meta_data)), PARSE_MODE_NONE),
                ("FANCY_TIME", _fancy_time, PARSE_MODE_NONE),
                ("SD", sd, PARSE_MODE_NONE),
                ("SERVER_NAME_SAFE", f"{guild_name}", PARSE_MODE_HTML_SAFE),
                (
                    "CHANNEL_NAME_SAFE",
                    f"{html.escape(self.channel.name or '')}",
                    PARSE_MODE_HTML_SAFE,
                ),
            ],
        )


class Transcript(TranscriptDAO):
    async def export(self):
        if not self.messages:
            self.messages = [
                message
                async for message in self.channel.fetch_history(
                    before=self.before if self.before is not None else hikari.UNDEFINED,
                    after=self.after if self.after is not None else hikari.UNDEFINED,
                )
            ]

        if not self.after:
            self.messages.reverse()

        try:
            return await super().build_transcript()
        except Exception:
            self.html = "Whoops! Something went wrong..."
            traceback.print_exc()
            print(
                "Please send a screenshot of the above error to https://www.github.com/h4ckd0tm3/DiscordChatExporterPy-hikari"
            )
            return self
