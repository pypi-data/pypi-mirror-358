import re
from datetime import datetime
from time import gmtime
from typing import Match
from zoneinfo import ZoneInfo

import hikari

from chat_exporter.parse.markdown import ParseMarkdown

bot: hikari.GatewayBot | hikari.RESTBot | None = None


def pass_bot(_bot: hikari.GatewayBot | hikari.RESTBot | None) -> None:
    # Bot is used to fetch a user who is no longer inside a guild
    # This will stop the user from appearing as 'Unknown' which some people do not want
    global bot
    bot = _bot


class ParseMention:
    REGEX_ROLES: str = r"&lt;@&amp;([0-9]+)&gt;"
    REGEX_ROLES_2: str = r"<@&([0-9]+)>"
    REGEX_EVERYONE: str = r"@(everyone)(?:[$\s\t\n\f\r\0]|$)"
    REGEX_HERE: str = r"@(here)(?:[$\s\t\n\f\r\0]|$)"
    REGEX_MEMBERS: str = r"&lt;@!?([0-9]+)&gt;"
    REGEX_MEMBERS_2: str = r"<@!?([0-9]+)>"
    REGEX_CHANNELS: str = r"&lt;#([0-9]+)&gt;"
    REGEX_CHANNELS_2: str = r"<#([0-9]+)>"
    REGEX_EMOJIS: str = r"&lt;a?(:[^\n:]+:)[0-9]+&gt;"
    REGEX_EMOJIS_2: str = r"<a?(:[^\n:]+:)[0-9]+>"
    REGEX_TIME_HOLDER: tuple[list[str], ...] = (
        [r"&lt;t:([0-9]{1,13}):t&gt;", "%H:%M"],
        [r"&lt;t:([0-9]{1,13}):T&gt;", "%T"],
        [r"&lt;t:([0-9]{1,13}):d&gt;", "%d/%m/%Y"],
        [r"&lt;t:([0-9]{1,13}):D&gt;", "%e %B %Y"],
        [r"&lt;t:([0-9]{1,13}):f&gt;", "%e %B %Y %H:%M"],
        [r"&lt;t:([0-9]{1,13}):F&gt;", "%A, %e %B %Y %H:%M"],
        [r"&lt;t:([0-9]{1,13}):R&gt;", "%e %B %Y %H:%M"],
        [r"&lt;t:([0-9]{1,13})&gt;", "%e %B %Y %H:%M"],
    )
    REGEX_SLASH_COMMAND: str = r"&lt;\/([\w]+ ?[\w]*):[0-9]+&gt;"

    ESCAPE_LT: str = "______lt______"
    ESCAPE_GT: str = "______gt______"
    ESCAPE_AMP: str = "______amp______"

    def __init__(self, content: str, guild: hikari.Guild) -> None:
        self.content: str = content
        self.guild: hikari.Guild = guild
        self.code_blocks_content: list[str] = []

    async def flow(self) -> str:
        markdown: ParseMarkdown = ParseMarkdown(self.content)
        markdown.parse_code_block_markdown()
        self.content = str(markdown.content)
        await self.escape_mentions()
        await self.unescape_mentions()
        await self.channel_mention()
        await self.member_mention()
        await self.role_mention()
        await self.time_mention()
        await self.slash_command_mention()
        markdown.content = self.content
        markdown.reverse_code_block_markdown()
        self.content = markdown.content
        return self.content

    async def escape_mentions(self) -> None:
        for match in re.finditer(
            "(%s|%s|%s|%s|%s|%s|%s|%s)"
            % (
                self.REGEX_ROLES,
                self.REGEX_MEMBERS,
                self.REGEX_CHANNELS,
                self.REGEX_EMOJIS,
                self.REGEX_ROLES_2,
                self.REGEX_MEMBERS_2,
                self.REGEX_CHANNELS_2,
                self.REGEX_EMOJIS_2,
            ),
            self.content,
        ):
            pre_content: str = self.content[: match.start()]
            post_content: str = self.content[match.end() :]
            match_content: str = self.content[match.start() : match.end()]

            match_content = match_content.replace("<", self.ESCAPE_LT)
            match_content = match_content.replace(">", self.ESCAPE_GT)
            match_content = match_content.replace("&", self.ESCAPE_AMP)

            self.content = pre_content + match_content + post_content

    async def unescape_mentions(self) -> None:
        self.content = self.content.replace(self.ESCAPE_LT, "<")
        self.content = self.content.replace(self.ESCAPE_GT, ">")
        self.content = self.content.replace(self.ESCAPE_AMP, "&")

    async def channel_mention(self) -> None:
        holder: tuple[str, str] = self.REGEX_CHANNELS, self.REGEX_CHANNELS_2
        for regex in holder:
            match: Match[str] | None = re.search(regex, self.content)
            while match is not None:
                channel_id: int = int(match.group(1))
                channel: hikari.GuildChannel | None = self.guild.get_channel(channel_id)

                if channel is None:
                    replacement: str = "#deleted-channel"
                else:
                    replacement = '<span class="mention" title="%s">#%s</span>' % (
                        channel.id,
                        channel.name,
                    )
                self.content = self.content.replace(
                    self.content[match.start() : match.end()], replacement
                )

                match = re.search(regex, self.content)

    async def role_mention(self) -> None:
        holder: tuple[str, str] = self.REGEX_EVERYONE, self.REGEX_HERE
        for regex in holder:
            match: Match[str] | None = re.search(regex, self.content)
            while match is not None:
                role_name: str = match.group(1)
                replacement: str = '<span class="mention" title="%s">@%s</span>' % (
                    str(role_name),
                    str(role_name),
                )

                self.content = self.content.replace(
                    self.content[match.start() : match.end()], replacement
                )
                match = re.search(regex, self.content)

        holder = self.REGEX_ROLES, self.REGEX_ROLES_2
        for regex in holder:
            match = re.search(regex, self.content)
            while match is not None:
                role_id: int = int(match.group(1))
                role: hikari.Role | None = self.guild.get_role(role_id)

                if role is None:
                    replacement: str = "@deleted-role"
                else:
                    if role.color.rgb[0] == 0 and role.color.rgb[1] == 0 and role.color.rgb[2] == 0:
                        colour: str = "#dee0fc"
                    else:
                        colour = "#%02x%02x%02x" % (
                            role.color.rgb[0],
                            role.color.rgb[1],
                            role.color.rgb[2],
                        )
                    replacement = '<span style="color: %s;">@%s</span>' % (colour, role.name)

                self.content = self.content.replace(
                    self.content[match.start() : match.end()], replacement
                )
                match = re.search(regex, self.content)

    async def slash_command_mention(self) -> None:
        match: Match[str] | None = re.search(self.REGEX_SLASH_COMMAND, self.content)
        while match is not None:
            slash_command_name: str = match.group(1)
            replacement: str = '<span class="mention" title="%s">/%s</span>' % (
                slash_command_name,
                slash_command_name,
            )
            self.content = self.content.replace(
                self.content[match.start() : match.end()], replacement
            )

            match = re.search(self.REGEX_SLASH_COMMAND, self.content)

    async def member_mention(self) -> None:
        holder: tuple[str, str] = self.REGEX_MEMBERS, self.REGEX_MEMBERS_2
        for regex in holder:
            match: Match[str] | None = re.search(regex, self.content)
            while match is not None:
                member_id: int = int(match.group(1))

                member: hikari.Member | hikari.User | None = None
                try:
                    member = self.guild.get_member(member_id)
                    if member is None and bot is not None:
                        member = await bot.rest.fetch_user(member_id)
                    member_name: str | None = getattr(member, "display_name", None) or getattr(
                        member, "username", str(member)
                    )
                except AttributeError:
                    member_name = str(member) if member is not None else "Unknown User"

                if member is not None:
                    replacement: str = '<span class="mention" title="%s">@%s</span>' % (
                        str(member_id),
                        str(member_name),
                    )
                else:
                    replacement = '<span class="mention" title="%s">&lt;@%s></span>' % (
                        str(member_id),
                        str(member_id),
                    )
                self.content = self.content.replace(
                    self.content[match.start() : match.end()], replacement
                )

                match = re.search(regex, self.content)

    async def time_mention(self) -> None:
        holder = self.REGEX_TIME_HOLDER

        for p in holder:
            regex: str
            strf: str
            regex, strf = p
            match: Match[str] | None = re.search(regex, self.content)
            while match is not None:
                timestamp: int = int(match.group(1)) - 1
                time_stamp = gmtime(timestamp)
                datetime_stamp: datetime = datetime(2010, *time_stamp[1:6], tzinfo=ZoneInfo("UTC"))
                ui_time: str = datetime_stamp.strftime(strf)
                ui_time = ui_time.replace(str(datetime_stamp.year), str(time_stamp[0]))
                tooltip_time: str = datetime_stamp.strftime("%A, %e %B %Y at %H:%M")
                tooltip_time = tooltip_time.replace(str(datetime_stamp.year), str(time_stamp[0]))
                original: str = match.group().replace("&lt;", "<").replace("&gt;", ">")
                replacement: str = (
                    f'<span class="unix-timestamp" data-timestamp="{tooltip_time}" raw-content="{original}">'
                    f"{ui_time}</span>"
                )

                self.content = self.content.replace(
                    self.content[match.start() : match.end()], replacement
                )

                match = re.search(regex, self.content)
