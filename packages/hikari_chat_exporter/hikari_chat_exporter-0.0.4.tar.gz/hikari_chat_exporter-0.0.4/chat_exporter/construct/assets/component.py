from typing import Sequence

import hikari

from chat_exporter.ext.discord_utils import DiscordUtils
from chat_exporter.ext.html_generator import (
    PARSE_MODE_EMOJI,
    PARSE_MODE_MARKDOWN,
    PARSE_MODE_NONE,
    component_button,
    component_menu,
    component_menu_options,
    component_menu_options_emoji,
    fill_out,
)


class Component:
    styles: dict[str, str] = {
        "PRIMARY": "#5865F2",
        "SECONDARY": "#4F545C",
        "SUCCESS": "#2D7D46",
        "DANGER": "#D83C3E",
        "BLURPLE": "#5865F2",
        "GREY": "#4F545C",
        "GRAY": "#4F545C",
        "GREEN": "#2D7D46",
        "RED": "#D83C3E",
        "LINK": "#4F545C",
    }

    components: str = ""
    menus: str = ""
    buttons: str = ""
    menu_div_id: int = 0

    def __init__(self, component: hikari.ActionRowComponent, guild: hikari.Guild) -> None:
        self.component: hikari.ActionRowComponent = component
        self.guild: hikari.Guild = guild

    async def build_component(
        self, c: hikari.ButtonComponent | hikari.TextSelectMenuComponent
    ) -> None:
        if isinstance(c, hikari.ButtonComponent):
            await self.build_button(c)
        elif isinstance(c, hikari.TextSelectMenuComponent):
            await self.build_menu(c)
            Component.menu_div_id += 1

    async def build_button(self, c: hikari.ButtonComponent) -> None:
        if c.url:
            url: str = str(c.url)
            target: str = " target='_blank'"
            icon: str = str(DiscordUtils.button_external_link)
        else:
            url: str = "javascript:;"
            target: str = ""
            icon: str = ""

        label: str = str(c.label) if c.label else ""
        style: str = self.styles[str(c.style)]
        emoji: str = str(c.emoji) if c.emoji else ""

        self.buttons += await fill_out(
            self.guild,
            component_button,
            [
                (
                    "DISABLED",
                    "chatlog__component-disabled" if c.is_disabled else "",
                    PARSE_MODE_NONE,
                ),
                ("URL", url, PARSE_MODE_NONE),
                ("LABEL", label, PARSE_MODE_MARKDOWN),
                ("EMOJI", emoji, PARSE_MODE_EMOJI),
                ("ICON", icon, PARSE_MODE_NONE),
                ("TARGET", target, PARSE_MODE_NONE),
                ("STYLE", style, PARSE_MODE_NONE),
            ],
        )

    async def build_menu(self, c: hikari.TextSelectMenuComponent) -> None:
        placeholder: str = c.placeholder if c.placeholder else ""
        options: Sequence[hikari.SelectMenuOption] = c.options
        content: str = ""

        if not c.is_disabled:
            content = await self.build_menu_options(options)

        self.menus += await fill_out(
            self.guild,
            component_menu,
            [
                (
                    "DISABLED",
                    "chatlog__component-disabled" if c.is_disabled else "",
                    PARSE_MODE_NONE,
                ),
                ("ID", str(self.menu_div_id), PARSE_MODE_NONE),
                ("PLACEHOLDER", str(placeholder), PARSE_MODE_MARKDOWN),
                ("CONTENT", str(content), PARSE_MODE_NONE),
                ("ICON", DiscordUtils.interaction_dropdown_icon, PARSE_MODE_NONE),
            ],
        )

    async def build_menu_options(self, options: Sequence[hikari.SelectMenuOption]) -> str:
        content: list[str] = []
        for option in options:
            if option.emoji:
                content.append(
                    await fill_out(
                        self.guild,
                        component_menu_options_emoji,
                        [
                            ("EMOJI", str(option.emoji), PARSE_MODE_EMOJI),
                            ("TITLE", str(option.label), PARSE_MODE_MARKDOWN),
                            (
                                "DESCRIPTION",
                                str(option.description) if option.description else "",
                                PARSE_MODE_MARKDOWN,
                            ),
                        ],
                    )
                )
            else:
                content.append(
                    await fill_out(
                        self.guild,
                        component_menu_options,
                        [
                            ("TITLE", str(option.label), PARSE_MODE_MARKDOWN),
                            (
                                "DESCRIPTION",
                                str(option.description) if option.description else "",
                                PARSE_MODE_MARKDOWN,
                            ),
                        ],
                    )
                )

        if content:
            html_content = f'<div id="dropdownMenu{self.menu_div_id}" class="dropdownContent">{"".join(content)}</div>'
            return html_content

        return ""

    async def flow(self) -> str:
        for c in self.component.components:
            await self.build_component(c)

        if self.menus:
            self.components += f'<div class="chatlog__components">{self.menus}</div>'

        if self.buttons:
            self.components += f'<div class="chatlog__components">{self.buttons}</div>'

        return self.components
