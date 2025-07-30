import html
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import hikari

from chat_exporter.construct.assets import Attachment, Component, Embed, Reaction
from chat_exporter.construct.attachment_handler import AttachmentHandler
from chat_exporter.ext.cache import cache
from chat_exporter.ext.discord_utils import DiscordUtils
from chat_exporter.ext.discriminator import discriminator
from chat_exporter.ext.html_generator import (
    PARSE_MODE_MARKDOWN,
    PARSE_MODE_NONE,
    PARSE_MODE_REFERENCE,
    bot_tag,
    bot_tag_verified,
    end_message,
    fill_out,
    img_attachment,
    message_body,
    message_content,
    message_interaction,
    message_pin,
    message_reference,
    message_thread,
    message_thread_add,
    message_thread_remove,
    start_message,
)


def _gather_user_bot(author: hikari.User) -> str:
    if author.is_bot and hikari.UserFlag.VERIFIED_BOT in author.flags:
        return bot_tag_verified
    elif author.is_bot:
        return bot_tag
    return ""


def _set_edit_at(message_edited_at):
    return f'<span class="chatlog__reference-edited-timestamp" data-timestamp="{message_edited_at}">(edited)</span>'


class MessageConstruct:
    message_html: str = ""

    # Asset Types
    embeds: str = ""
    reactions: str = ""
    components: str = ""
    attachments: str = ""
    time_format: str = ""

    interaction: str = ""

    def __init__(
        self,
        message: hikari.Message,
        previous_message: hikari.Message | None,
        zoneinfo: ZoneInfo,
        military_time: bool,
        guild: hikari.Guild,
        meta_data: dict,
        message_dict: dict,
        attachment_handler: AttachmentHandler | None,
    ) -> None:
        self.message: hikari.Message = message
        self.previous_message: hikari.Message | None = previous_message
        self.zoneinfo: ZoneInfo = zoneinfo
        self.military_time: bool = military_time
        self.guild: hikari.Guild = guild
        self.message_dict: dict = message_dict
        self.attachment_handler: AttachmentHandler | None = attachment_handler
        self.time_format = "%A, %e %B %Y %I:%M %p"
        if self.military_time:
            self.time_format = "%A, %e %B %Y %H:%M"

        self.message_created_at, self.message_edited_at = self.set_time()
        self.meta_data = meta_data

    async def construct_message(
        self,
    ) -> tuple[str, dict]:
        if hikari.MessageType.CHANNEL_PINNED_MESSAGE == self.message.type:
            await self.build_pin()
        elif 18 == self.message.type:
            await self.build_thread()
        elif hikari.MessageType.RECIPIENT_REMOVE == self.message.type:
            await self.build_thread_remove()
        elif hikari.MessageType.RECIPIENT_ADD == self.message.type:
            await self.build_thread_add()
        else:
            await self.build_message()
        return self.message_html, self.meta_data

    async def build_message(self) -> None:
        await self.build_content()
        await self.build_reference()
        await self.build_interaction()
        await self.build_sticker()
        await self.build_assets()
        await self.build_message_template()
        await self.build_meta_data()

    async def build_pin(self) -> None:
        await self.generate_message_divider(channel_audit=True)
        await self.build_pin_template()

    async def build_thread(self) -> None:
        await self.generate_message_divider(channel_audit=True)
        await self.build_thread_template()

    async def build_thread_remove(self) -> None:
        await self.generate_message_divider(channel_audit=True)
        await self.build_remove()

    async def build_thread_add(self) -> None:
        await self.generate_message_divider(channel_audit=True)
        await self.build_add()

    async def build_meta_data(self) -> None:
        user_id: hikari.Snowflake = self.message.author.id

        if user_id in self.meta_data:
            self.meta_data[user_id][4] += 1
        else:
            user_name_discriminator: str = await discriminator(
                self.message.author.username, self.message.author.discriminator
            )
            user_created_at: datetime = self.message.author.created_at
            user_bot: str = _gather_user_bot(self.message.author)
            user_avatar: hikari.URL | None | str = (
                self.message.author.make_avatar_url()
                if self.message.author.make_avatar_url()
                else DiscordUtils.default_avatar
            )
            user_joined_at: datetime | None = (
                self.message.author.created_at
                if hasattr(self.message.author, "created_at")
                else None
            )
            user_display_name = (
                f'<div class="meta__display-name">{self.message.author.display_name}</div>'
                if self.message.author.display_name != self.message.author.username
                else ""
            )
            self.meta_data[user_id] = [
                user_name_discriminator,
                user_created_at,
                user_bot,
                user_avatar,
                1,
                user_joined_at,
                user_display_name,
            ]

    async def build_content(self) -> None:
        if not self.message.content:
            self.message.content = ""
            return

        if self.message_edited_at:
            self.message_edited_at: str = _set_edit_at(self.message_edited_at)

        self.message.content = html.escape(self.message.content)
        self.message.content = await fill_out(
            self.guild,
            message_content,
            [
                ("MESSAGE_CONTENT", self.message.content, PARSE_MODE_MARKDOWN),
                ("EDIT", self.message_edited_at, PARSE_MODE_NONE),
            ],
        )

    async def build_reference(self):
        if not self.message.referenced_message:
            self.message.referenced_message = None
            return

        message = self.message.referenced_message

        if not isinstance(message.author, hikari.User):
            return

        guild_member = await self._gather_member(message.author)
        display_name = guild_member.display_name if guild_member else self.message.author.username

        is_bot = _gather_user_bot(message.author)
        user_colour = await self._gather_user_color(message.author)

        if not message.content and not message.interaction_metadata:
            message.content = "Click to see attachment"
        elif not message.content and message.interaction_metadata:
            message.content = "Click to see command"

        icon = ""
        if not message.interaction_metadata and (message.embeds or message.attachments):
            icon = DiscordUtils.reference_attachment_icon
        elif message.interaction_metadata:
            icon = DiscordUtils.interaction_command_icon

        _, message_edited_timestamp = self.set_time(message)

        if message_edited_timestamp:
            message_edited_timestamp = _set_edit_at(message_edited_timestamp)

        avatar_url = (
            message.author.display_avatar_url
            if message.author.display_avatar_url
            else DiscordUtils.default_avatar
        )
        self.message.referenced_message = await fill_out(
            self.guild,
            message_reference,
            [
                ("AVATAR_URL", str(avatar_url), PARSE_MODE_NONE),
                ("BOT_TAG", is_bot, PARSE_MODE_NONE),
                (
                    "NAME_TAG",
                    "%s#%s" % (message.author.username, message.author.discriminator),
                    PARSE_MODE_NONE,
                ),
                ("NAME", str(html.escape(display_name))),
                ("USER_COLOUR", user_colour, PARSE_MODE_NONE),
                ("CONTENT", message.content, PARSE_MODE_REFERENCE),
                ("EDIT", message_edited_timestamp, PARSE_MODE_NONE),
                ("ICON", icon, PARSE_MODE_NONE),
                ("USER_ID", str(message.author.id), PARSE_MODE_NONE),
                ("MESSAGE_ID", str(self.message.referenced_message.id), PARSE_MODE_NONE),
            ],
        )

    async def build_interaction(self):
        if hasattr(self.message, "interaction_metadata"):
            if not self.message.interaction_metadata:
                self.interaction = ""
                return
            command = "a slash command"
            user = self.message.interaction_metadata.user
            interaction_id = self.message.interaction_metadata.interaction_id
        elif self.message.interaction_metadata:
            command = f"/{self.message.interaction_metadata.type}"
            user = self.message.interaction_metadata.user
            interaction_id = self.message.interaction_metadata.interaction_id
        else:
            self.interaction = ""
            return

        is_bot = _gather_user_bot(user)
        user_colour = await self._gather_user_color(user)
        avatar_url = (
            user.make_avatar_url() if user.make_banner_url() else DiscordUtils.default_avatar
        )

        self.interaction = await fill_out(
            self.guild,
            message_interaction,
            [
                ("AVATAR_URL", str(avatar_url), PARSE_MODE_NONE),
                ("BOT_TAG", is_bot, PARSE_MODE_NONE),
                (
                    "NAME_TAG",
                    await discriminator(user.username, user.discriminator),
                    PARSE_MODE_NONE,
                ),
                ("NAME", str(html.escape(user.display_name or user.username))),
                ("COMMAND", str(command), PARSE_MODE_NONE),
                ("USER_COLOUR", user_colour, PARSE_MODE_NONE),
                ("FILLER", "used ", PARSE_MODE_NONE),
                ("USER_ID", str(user.id), PARSE_MODE_NONE),
                ("INTERACTION_ID", str(interaction_id), PARSE_MODE_NONE),
            ],
        )

    async def build_sticker(self):
        if not self.message.stickers or not hasattr(self.message.stickers[0], "url"):
            return

        sticker_image_url = self.message.stickers[0].make_url()

        self.message.content = await fill_out(
            self.guild,
            img_attachment,
            [
                ("ATTACH_URL", str(sticker_image_url), PARSE_MODE_NONE),
                ("ATTACH_URL_THUMB", str(sticker_image_url), PARSE_MODE_NONE),
            ],
        )

    async def build_assets(self):
        for e in self.message.embeds:
            self.embeds += await Embed(e, self.guild).flow()

        for a in self.message.attachments:
            if self.attachment_handler and isinstance(self.attachment_handler, AttachmentHandler):
                a: hikari.Attachment = await self.attachment_handler.process_asset(a)
            self.attachments += str(await Attachment(a, self.guild).flow())

        for c in self.message.components:
            if isinstance(c, hikari.ActionRowComponent):
                self.components += await Component(c, self.guild).flow()

        for r in self.message.reactions:
            self.reactions += str(await Reaction(r, self.guild).flow())

        if self.reactions:
            self.reactions = f'<div class="chatlog__reactions">{self.reactions}</div>'

    async def build_message_template(self):
        started = await self.generate_message_divider()

        if started:
            return self.message_html

        self.message_html += await fill_out(
            self.guild,
            message_body,
            [
                ("MESSAGE_ID", str(self.message.id)),
                ("MESSAGE_CONTENT", self.message.content, PARSE_MODE_NONE),
                ("EMBEDS", self.embeds, PARSE_MODE_NONE),
                ("ATTACHMENTS", self.attachments, PARSE_MODE_NONE),
                ("COMPONENTS", self.components, PARSE_MODE_NONE),
                ("EMOJI", self.reactions, PARSE_MODE_NONE),
                ("TIMESTAMP", self.message_created_at, PARSE_MODE_NONE),
                ("TIME", self.message_created_at.split(maxsplit=4)[4], PARSE_MODE_NONE),
            ],
        )

        return self.message_html

    def _generate_message_divider_check(self):
        return bool(
            self.previous_message is None
            or self.message.referenced_message != ""
            or self.previous_message.type is not hikari.MessageType.DEFAULT
            or self.interaction != ""
            or self.previous_message.author.id != self.message.author.id
            or self.message.webhook_id is not None
            or self.message.created_at > (self.previous_message.created_at + timedelta(minutes=4))
        )

    async def generate_message_divider(self, channel_audit=False):
        if channel_audit or self._generate_message_divider_check():
            if self.previous_message is not None:
                self.message_html += await fill_out(self.guild, end_message, [])

            if channel_audit:
                self.audit = True
                return

            followup_symbol = ""
            is_bot = _gather_user_bot(self.message.author)
            avatar_url = (
                self.message.author.make_avatar_url()
                if self.message.author.make_avatar_url()
                else DiscordUtils.default_avatar
            )

            if self.message.message_reference != "" or self.interaction:
                followup_symbol = "<div class='chatlog__followup-symbol'></div>"

            time = self.message.created_at
            if not self.message.created_at.tzinfo:
                time = time.replace(tzinfo=ZoneInfo("UTC"))

            if self.military_time:
                default_timestamp = time.astimezone(self.zoneinfo).strftime("%d-%m-%Y %H:%M")
            else:
                default_timestamp = time.astimezone(self.zoneinfo).strftime("%d-%m-%Y %I:%M %p")

            self.message_html += await fill_out(
                self.guild,
                start_message,
                [
                    ("REFERENCE_SYMBOL", followup_symbol, PARSE_MODE_NONE),
                    (
                        "REFERENCE",
                        self.message.referenced_message
                        if self.message.referenced_message
                        else self.interaction,
                        PARSE_MODE_NONE,
                    ),
                    ("AVATAR_URL", str(avatar_url), PARSE_MODE_NONE),
                    (
                        "NAME_TAG",
                        await discriminator(
                            self.message.author.username, self.message.author.discriminator
                        ),
                        PARSE_MODE_NONE,
                    ),
                    ("USER_ID", str(self.message.author.id)),
                    ("USER_COLOUR", await self._gather_user_color(self.message.author)),
                    (
                        "USER_ICON",
                        await self._gather_user_icon(self.message.author),
                        PARSE_MODE_NONE,
                    ),
                    (
                        "NAME",
                        str(
                            html.escape(
                                self.message.author.display_name or self.message.author.username
                            )
                        ),
                    ),
                    ("BOT_TAG", str(is_bot), PARSE_MODE_NONE),
                    ("TIMESTAMP", str(self.message_created_at)),
                    ("DEFAULT_TIMESTAMP", str(default_timestamp), PARSE_MODE_NONE),
                    ("MESSAGE_ID", str(self.message.id)),
                    ("MESSAGE_CONTENT", self.message.content, PARSE_MODE_NONE),
                    ("EMBEDS", self.embeds, PARSE_MODE_NONE),
                    ("ATTACHMENTS", self.attachments, PARSE_MODE_NONE),
                    ("COMPONENTS", self.components, PARSE_MODE_NONE),
                    ("EMOJI", self.reactions, PARSE_MODE_NONE),
                ],
            )

            return True

    async def build_pin_template(self):
        self.message_html += await fill_out(
            self.guild,
            message_pin,
            [
                ("PIN_URL", DiscordUtils.pinned_message_icon, PARSE_MODE_NONE),
                ("USER_COLOUR", await self._gather_user_color(self.message.author)),
                (
                    "NAME",
                    str(
                        html.escape(
                            self.message.author.display_name or self.message.author.username
                        )
                    ),
                ),
                (
                    "NAME_TAG",
                    await discriminator(
                        self.message.author.username, self.message.author.discriminator
                    ),
                    PARSE_MODE_NONE,
                ),
                ("MESSAGE_ID", str(self.message.id), PARSE_MODE_NONE),
                (
                    "REF_MESSAGE_ID",
                    str(self.message.referenced_message.id)
                    if self.message.referenced_message
                    else "",
                    PARSE_MODE_NONE,
                ),
            ],
        )

    async def build_thread_template(self):
        self.message_html += await fill_out(
            self.guild,
            message_thread,
            [
                ("THREAD_URL", DiscordUtils.thread_channel_icon, PARSE_MODE_NONE),
                ("THREAD_NAME", self.message.content, PARSE_MODE_NONE),
                ("USER_COLOUR", await self._gather_user_color(self.message.author)),
                (
                    "NAME",
                    str(
                        html.escape(
                            self.message.author.display_name or self.message.author.username
                        )
                    ),
                ),
                (
                    "NAME_TAG",
                    await discriminator(
                        self.message.author.username, self.message.author.discriminator
                    ),
                    PARSE_MODE_NONE,
                ),
                ("MESSAGE_ID", str(self.message.id), PARSE_MODE_NONE),
            ],
        )

    async def build_remove(self):
        member_mentions = self.message.get_member_mentions()
        removed_member: hikari.Member | None = (
            list(member_mentions.values())[0] if member_mentions else None
        )

        if not removed_member:
            return

        self.message_html += await fill_out(
            self.guild,
            message_thread_remove,
            [
                ("THREAD_URL", DiscordUtils.thread_remove_recipient, PARSE_MODE_NONE),
                ("USER_COLOUR", await self._gather_user_color(self.message.author)),
                (
                    "NAME",
                    str(
                        html.escape(
                            self.message.author.display_name or self.message.author.username
                        )
                    ),
                ),
                (
                    "NAME_TAG",
                    await discriminator(
                        self.message.author.username, self.message.author.discriminator
                    ),
                    PARSE_MODE_NONE,
                ),
                ("RECIPIENT_USER_COLOUR", await self._gather_user_color(removed_member)),
                ("RECIPIENT_NAME", str(html.escape(removed_member.display_name))),
                (
                    "RECIPIENT_NAME_TAG",
                    await discriminator(removed_member.username, removed_member.discriminator),
                    PARSE_MODE_NONE,
                ),
                ("MESSAGE_ID", str(self.message.id), PARSE_MODE_NONE),
            ],
        )

    async def build_add(self):
        member_mentions = self.message.get_member_mentions()
        removed_member: hikari.Member | None = (
            list(member_mentions.values())[0] if member_mentions else None
        )

        if not removed_member:
            return

        self.message_html += await fill_out(
            self.guild,
            message_thread_add,
            [
                ("THREAD_URL", DiscordUtils.thread_add_recipient, PARSE_MODE_NONE),
                ("USER_COLOUR", await self._gather_user_color(self.message.author)),
                (
                    "NAME",
                    str(
                        html.escape(
                            self.message.author.display_name or self.message.author.username
                        )
                    ),
                ),
                (
                    "NAME_TAG",
                    await discriminator(
                        self.message.author.username, self.message.author.discriminator
                    ),
                    PARSE_MODE_NONE,
                ),
                ("RECIPIENT_USER_COLOUR", await self._gather_user_color(removed_member)),
                ("RECIPIENT_NAME", str(html.escape(removed_member.display_name))),
                (
                    "RECIPIENT_NAME_TAG",
                    await discriminator(removed_member.username, removed_member.discriminator),
                    PARSE_MODE_NONE,
                ),
                ("MESSAGE_ID", str(self.message.id), PARSE_MODE_NONE),
            ],
        )

    @cache()
    async def _gather_member(self, author: hikari.User):
        member = self.guild.get_member(author.id)

        if member:
            return member

        try:
            return self.guild.get_member(author.id)
        except Exception:
            return None

    async def _gather_user_color(self, author: hikari.User):
        member = await self._gather_member(author)
        user_colour = (
            member.accent_colour if member and str(member.accent_colour) != "#000000" else "#FFFFFF"
        )
        return f"color: {user_colour};"

    async def _gather_user_icon(self, author: hikari.User):
        member = await self._gather_member(author)

        if not member:
            return ""

        if hasattr(member, "make_avatar_url") and member.make_avatar_url():
            return (
                f"<img class='chatlog__role-icon' src='{member.make_avatar_url()}' alt='Role Icon'>"
            )
        elif hasattr(member, "get_top_role") and callable(member.get_top_role):
            top_role = member.get_top_role()
            if top_role and hasattr(top_role, "make_icon_url") and callable(top_role.make_icon_url):
                return f"<img class='chatlog__role-icon' src='{top_role.make_icon_url()}' alt='Role Icon'>"
        return ""

    def set_time(self, message: hikari.PartialMessage | None = None):
        message = message if message else self.message
        created_at_str = self.to_local_time_str(message.created_at)
        edited_at_str = (
            self.to_local_time_str(message.edited_timestamp) if message.edited_timestamp else ""
        )

        return created_at_str, edited_at_str

    def to_local_time_str(self, time):
        if not self.message.created_at.tzinfo:
            time = time.replace(tzinfo=ZoneInfo("UTC"))

        local_time = time.astimezone(self.zoneinfo)

        return local_time.strftime(self.time_format)


async def gather_messages(
    messages: list[hikari.Message] | None,
    guild: hikari.Guild,
    zoneinfo: ZoneInfo,
    military_time: bool,
    attachment_handler: AttachmentHandler | None,
) -> tuple[str, dict]:
    if messages is None:
        return "", {}

    message_html: str = ""
    meta_data: dict = {}
    previous_message: hikari.Message | None = None

    message_dict = {message.id: message for message in messages}

    for message in messages:
        content_html, meta_data = await MessageConstruct(
            message,
            previous_message,
            zoneinfo,
            military_time,
            guild,
            meta_data,
            message_dict,
            attachment_handler,
        ).construct_message()

        message_html += content_html
        previous_message = message

    message_html += "</div>"
    return message_html, meta_data
