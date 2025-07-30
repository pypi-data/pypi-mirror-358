import html
from typing import Any

import hikari

from chat_exporter.ext.html_generator import (
    PARSE_MODE_EMBED,
    PARSE_MODE_MARKDOWN,
    PARSE_MODE_NONE,
    PARSE_MODE_SPECIAL_EMBED,
    embed_author,
    embed_author_icon,
    embed_body,
    embed_description,
    embed_field,
    embed_field_inline,
    embed_footer,
    embed_footer_icon,
    embed_image,
    embed_thumbnail,
    embed_title,
    fill_out,
)


def _gather_checker() -> hikari.Embed:
    """Return an empty Embed for comparison purposes."""
    return hikari.Embed()


class Embed:
    """Process hikari.Embed objects into HTML representation."""

    r: int
    g: int
    b: int
    title: str
    description: str
    author: str
    image: str
    thumbnail: str
    footer: str
    fields: str

    embed: hikari.Embed
    guild: hikari.Guild
    check_against: hikari.Embed

    def __init__(self, embed: hikari.Embed, guild: hikari.Guild) -> None:
        """Initialize the Embed processor.

        Args:
            embed: The hikari Embed object to process
            guild: The guild context for the embed
        """
        self.embed = embed
        self.guild = guild
        self.check_against: hikari.Embed  # Will be initialized in flow()

        # Initialize with default values
        self.r = 0x20
        self.g = 0x22
        self.b = 0x25
        self.title = ""
        self.description = ""
        self.author = ""
        self.image = ""
        self.thumbnail = ""
        self.footer = ""
        self.fields = ""

    async def flow(self) -> Any:
        """Process the embed through all building stages.

        Returns:
            The processed embed result
        """
        self.check_against = _gather_checker()

        self.build_color()
        await self.build_title()
        await self.build_description()
        await self.build_fields()
        await self.build_author()
        await self.build_image()
        await self.build_thumbnail()
        await self.build_footer()
        await self.build_embed()

        return self.embed

    def build_color(self) -> None:
        """Set RGB values from embed color or use default."""
        if self.embed.color and self.embed.color != self.check_against.color:
            self.r = self.embed.color.rgb[0]
            self.g = self.embed.color.rgb[1]
            self.b = self.embed.color.rgb[2]

    async def build_title(self) -> None:
        """Process and format the embed title."""
        if not self.embed.title:
            return

        if self.embed.title != self.check_against.title:
            escaped_title = html.escape(self.embed.title)
            self.title = await fill_out(
                self.guild, embed_title, [("EMBED_TITLE", escaped_title, PARSE_MODE_MARKDOWN)]
            )

    async def build_description(self) -> None:
        """Process and format the embed description."""
        if not self.embed.description:
            return

        if self.embed.description != self.check_against.description:
            # Using original descriptor as PARSE_MODE_EMBED will handle escaping
            self.description = await fill_out(
                self.guild,
                embed_description,
                [("EMBED_DESC", self.embed.description, PARSE_MODE_EMBED)],
            )

    async def build_fields(self) -> None:
        """Process and format the embed fields."""
        self.fields = ""
        if not self.embed.fields:
            return

        fields_html = []
        for field in self.embed.fields:
            escaped_name = html.escape(field.name)
            escaped_value = html.escape(field.value)
            template = embed_field_inline if field.is_inline else embed_field

            field_html = await fill_out(
                self.guild,
                template,
                [
                    ("FIELD_NAME", escaped_name, PARSE_MODE_SPECIAL_EMBED),
                    ("FIELD_VALUE", escaped_value, PARSE_MODE_EMBED),
                ],
            )
            fields_html.append(field_html)

        self.fields = "".join(fields_html)

    async def build_author(self) -> None:
        """Process and format the embed author information."""
        self.author = ""

        # Skip if no author information
        if not self.embed.author or not self.embed.author.name:
            return

        if self.check_against.author and self.embed.author.name == self.check_against.author.name:
            return

        # Process author name
        self.author = html.escape(self.embed.author.name)

        # Add URL if available
        if self.embed.author.url and (
            not self.check_against.author or self.embed.author.url != self.check_against.author.url
        ):
            self.author = f'<a class="chatlog__embed-author-name-link" href="{self.embed.author.url}">{self.author}</a>'

        # Handle author icon - add proper null check for icon attribute
        has_icon = (
            self.embed.author.icon
            and self.embed.author.icon.url
            and (
                not self.check_against.author
                or not self.check_against.author.icon
                or self.embed.author.icon.url != self.check_against.author.icon.url
            )
        )

        if has_icon and self.embed.author.icon:  # Ensure icon is still available
            icon_url = str(self.embed.author.icon.url)
            self.author = await fill_out(
                self.guild,
                embed_author_icon,
                [
                    ("AUTHOR", self.author, PARSE_MODE_NONE),
                    ("AUTHOR_ICON", icon_url, PARSE_MODE_NONE),
                ],
            )
        else:
            self.author = await fill_out(
                self.guild, embed_author, [("AUTHOR", self.author, PARSE_MODE_NONE)]
            )

    async def build_image(self) -> None:
        """Process and format the embed image."""
        self.image = ""

        if not self.embed.image or not self.embed.image.url:
            return

        if (
            self.check_against.image
            and self.check_against.image.url
            and self.embed.image.url == self.check_against.image.url
        ):
            return

        # Use proxy_url if available, otherwise use url
        image_url = str(self.embed.image.proxy_url or self.embed.image.url)

        self.image = await fill_out(
            self.guild,
            embed_image,
            [("EMBED_IMAGE", image_url, PARSE_MODE_NONE)],
        )

    async def build_thumbnail(self) -> None:
        """Process and format the embed thumbnail."""
        self.thumbnail = ""

        if not self.embed.thumbnail or not self.embed.thumbnail.url:
            return

        if (
            self.check_against.thumbnail
            and self.embed.thumbnail.url == self.check_against.thumbnail.url
        ):
            return

        self.thumbnail = await fill_out(
            self.guild,
            embed_thumbnail,
            [("EMBED_THUMBNAIL", str(self.embed.thumbnail.url), PARSE_MODE_NONE)],
        )

    async def build_footer(self) -> None:
        """Process and format the embed footer."""
        self.footer = ""

        if not self.embed.footer or not self.embed.footer.text:
            return

        if self.check_against.footer and self.embed.footer.text == self.check_against.footer.text:
            return

        self.footer = html.escape(self.embed.footer.text)

        # Add footer icon if available - add proper null check for icon attribute
        has_icon = (
            self.embed.footer.icon
            and self.embed.footer.icon.url
            and (
                not self.check_against.footer
                or not self.check_against.footer.icon
                or self.embed.footer.icon.url != self.check_against.footer.icon.url
            )
        )

        if (
            has_icon and self.embed.footer.icon
        ):  # Additional check to ensure icon is still available
            icon_url = str(self.embed.footer.icon.url)
            self.footer = await fill_out(
                self.guild,
                embed_footer_icon,
                [
                    ("EMBED_FOOTER", self.footer, PARSE_MODE_NONE),
                    ("EMBED_FOOTER_ICON", icon_url, PARSE_MODE_NONE),
                ],
            )
        else:
            self.footer = await fill_out(
                self.guild, embed_footer, [("EMBED_FOOTER", self.footer, PARSE_MODE_NONE)]
            )

    async def build_embed(self) -> None:
        """Build the final embed structure."""
        self.embed = await fill_out(
            self.guild,
            embed_body,
            [
                ("EMBED_R", str(self.r)),
                ("EMBED_G", str(self.g)),
                ("EMBED_B", str(self.b)),
                ("EMBED_AUTHOR", self.author, PARSE_MODE_NONE),
                ("EMBED_TITLE", self.title, PARSE_MODE_NONE),
                ("EMBED_IMAGE", self.image, PARSE_MODE_NONE),
                ("EMBED_THUMBNAIL", self.thumbnail, PARSE_MODE_NONE),
                ("EMBED_DESC", self.description, PARSE_MODE_NONE),
                ("EMBED_FIELDS", self.fields, PARSE_MODE_NONE),
                ("EMBED_FOOTER", self.footer, PARSE_MODE_NONE),
            ],
        )
