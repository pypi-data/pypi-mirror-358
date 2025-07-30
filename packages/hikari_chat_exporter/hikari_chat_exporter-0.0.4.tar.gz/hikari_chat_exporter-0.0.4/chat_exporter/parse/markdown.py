import html
import re
from typing import Any, Optional

from chat_exporter.ext.emoji_convert import convert_emoji


class ParseMarkdown:
    # Precompiled regex patterns
    CODE_BLOCK_PATTERN: re.Pattern[str] = re.compile(r"```(.*?)```")
    INLINE_CODE_DOUBLE_PATTERN: re.Pattern[str] = re.compile(r"``(.*?)``")
    INLINE_CODE_PATTERN: re.Pattern[str] = re.compile(r"`(.*?)`")
    LINK_PATTERN: re.Pattern[str] = re.compile(r"\[(.+?)]\((.+?)\)")
    URL_PATTERN: re.Pattern[str] = re.compile(r"https?://[^\s>`\"*]*")
    SILENT_LINK_PATTERN: re.Pattern[str] = re.compile(r"&lt;(https?:\/\/.*?)&gt;")
    MARKDOWN_PATTERNS: list[tuple[re.Pattern[str], str]] = [
        (re.compile(r"__(.*?)__", re.M), '<span style="text-decoration: underline">%s</span>'),
        (re.compile(r"\*\*(.*?)\*\*", re.M), "<strong>%s</strong>"),
        (re.compile(r"\*(.*?)\*", re.M), "<em>%s</em>"),
        (re.compile(r"~~(.*?)~~", re.M), '<span style="text-decoration: line-through">%s</span>'),
        (re.compile(r"^###\s(.*?)\n", re.M), "<h3>%s</h3>"),
        (re.compile(r"^##\s(.*?)\n", re.M), "<h2>%s</h2>"),
        (re.compile(r"^#\s(.*?)\n", re.M), "<h1>%s</h1>"),
        (
            re.compile(r"\|\|(.*?)\|\|", re.M),
            '<span class="spoiler spoiler--hidden" onclick="showSpoiler(event, this)"> <span '
            'class="spoiler-text">%s</span></span>',
        ),
    ]
    MARKDOWN_LANGUAGES: list[str] = [
        "asciidoc",
        "autohotkey",
        "bash",
        "coffeescript",
        "cpp",
        "cs",
        "css",
        "diff",
        "fix",
        "glsl",
        "ini",
        "json",
        "md",
        "ml",
        "prolog",
        "py",
        "tex",
        "xl",
        "xml",
        "js",
        "html",
    ]

    def __init__(self, content: str) -> None:
        self.content: str = content
        self.code_blocks_content: list[str] = []

    async def standard_message_flow(self) -> str:
        """Process standard message content flow."""
        self.parse_code_block_markdown()
        self.https_http_links()
        self.parse_normal_markdown()

        await self.parse_emoji()
        self.reverse_code_block_markdown()
        return self.content

    async def link_embed_flow(self) -> None:
        """Process link embed content flow."""
        self.parse_embed_markdown()
        await self.parse_emoji()

    async def standard_embed_flow(self) -> str:
        """Process standard embed content flow."""
        self.parse_code_block_markdown()
        self.https_http_links()
        self.parse_embed_markdown()
        self.parse_normal_markdown()

        await self.parse_emoji()
        self.reverse_code_block_markdown()
        return self.content

    async def special_embed_flow(self) -> str:
        """Process special embed content flow."""
        self.https_http_links()
        self.parse_code_block_markdown()
        self.parse_normal_markdown()

        await self.parse_emoji()
        self.reverse_code_block_markdown()
        return self.content

    async def message_reference_flow(self) -> str:
        """Process message reference content flow."""
        self.strip_preserve()
        self.parse_code_block_markdown(reference=True)
        self.parse_normal_markdown()
        self.reverse_code_block_markdown()
        self.parse_br()

        return self.content

    async def special_emoji_flow(self) -> str:
        """Process only emoji content."""
        await self.parse_emoji()
        return self.content

    def parse_br(self) -> None:
        """Replace <br> tags with spaces."""
        self.content = self.content.replace("<br>", " ")

    async def parse_emoji(self) -> None:
        """Convert Discord emoji syntax to HTML."""
        emoji_patterns: list[tuple[str, str]] = [
            (
                r"&lt;:.*?:(\d*)&gt;",
                '<img class="emoji emoji--small" src="https://cdn.discordapp.com/emojis/%s.png">',
            ),
            (
                r"&lt;a:.*?:(\d*)&gt;",
                '<img class="emoji emoji--small" src="https://cdn.discordapp.com/emojis/%s.gif">',
            ),
            (
                r"<:.*?:(\d*)>",
                '<img class="emoji emoji--small" src="https://cdn.discordapp.com/emojis/%s.png">',
            ),
            (
                r"<a:.*?:(\d*)>",
                '<img class="emoji emoji--small" src="https://cdn.discordapp.com/emojis/%s.gif">',
            ),
        ]

        self.content = await convert_emoji([word for word in self.content])

        for pattern, replacement in emoji_patterns:
            compiled_pattern: re.Pattern[str] = re.compile(pattern)
            match: re.Match[str] | None = re.search(compiled_pattern, self.content)
            while match is not None:
                emoji_id: str | Any = match.group(1)
                self.content = self.content.replace(
                    self.content[match.start() : match.end()], replacement % emoji_id
                )
                match = re.search(compiled_pattern, self.content)

    def strip_preserve(self) -> None:
        """Strip preservation spans."""
        pattern = r'<span class="chatlog__markdown-preserve">(.*)</span>'
        compiled_pattern: re.Pattern[str] = re.compile(pattern)
        match: re.Match[str] | None = re.search(compiled_pattern, self.content)
        while match is not None:
            affected_text: str | Any = match.group(1)
            self.content = self.content.replace(
                self.content[match.start() : match.end()], affected_text
            )
            match = re.search(compiled_pattern, self.content)

    def order_list_markdown_to_html(self) -> None:
        """Convert markdown lists to HTML ordered/unordered lists."""
        lines: list[str] = self.content.split("\n")
        html_content: list[Any] = []
        indent_stack: list[int] = [0]
        in_list = False

        for line in lines:
            match: re.Match[str] | None = re.match(r"^(\s*)([-*])\s+(.+)$", line)
            if match:
                indent, _, content = match.groups()
                indent = len(indent)

                if not in_list:
                    html_content.append(
                        '<ul class="markup" style="padding-left: 20px;margin: 0 !important">'
                    )
                    in_list = True

                # Adjust indentation
                while indent < indent_stack[-1]:
                    html_content.append("</ul>")
                    indent_stack.pop()

                if indent > indent_stack[-1]:
                    html_content.append('<ul class="markup">')
                    indent_stack.append(indent if indent % 2 == 0 else indent + 1)

                html_content.append(f'<li class="markup">{content.strip()}</li>')
            else:
                # Close any open lists
                while len(indent_stack) > 1:
                    html_content.append("</ul>")
                    indent_stack.pop()

                if in_list:
                    html_content.append("</ul>")
                    in_list = False

                html_content.append(line)

        # Close any remaining open lists
        while len(indent_stack) > 1:
            html_content.append("</ul>")
            indent_stack.pop()

        self.content = "\n".join(html_content)

    def process_blockquotes(self, content: str, quote_marker: str) -> str:
        """Process blockquotes in content."""
        lines: list[str] = content.split("<br>" if quote_marker == "&gt;" else "\n")

        # Quick return for single line
        if len(lines) == 1:
            quote_pattern: re.Pattern[str] = re.compile(f"^{quote_marker}\\s(.+)")
            if re.search(quote_pattern, lines[0]):
                return f'<div class="quote">{lines[0][len(quote_marker) + 1 :]}</div>'
            return lines[0]

        current_quote: str = ""
        new_content: list[Any] = []
        quote_pattern = re.compile(f"^{quote_marker}\\s(.+)")
        separator = "<br>" if quote_marker == "&gt;" else "\n"

        for line in lines:
            match: re.Match[str] | None = re.search(quote_pattern, line)
            if match and current_quote is not None:
                current_quote += separator + line[len(quote_marker) + 1 :]
            elif current_quote is None:
                if match:
                    current_quote: str = line[len(quote_marker) + 1 :]
                else:
                    new_content.append(line)
            else:
                new_content.append(f'<div class="quote">{current_quote}</div>')
                new_content.append(line)
                current_quote = ""

        if current_quote:
            new_content.append(f'<div class="quote">{current_quote}</div>')

        return separator.join(new_content)

    def parse_normal_markdown(self) -> None:
        """Convert standard markdown to HTML."""
        self.order_list_markdown_to_html()

        # Process standard markdown patterns
        for pattern, replacement in self.MARKDOWN_PATTERNS:
            match: re.Match[str] | None = re.search(pattern, self.content)
            while match is not None:
                affected_text: str | Any = match.group(1)
                self.content = self.content.replace(
                    self.content[match.start() : match.end()], replacement % affected_text
                )
                match = re.search(pattern, self.content)

        # Process blockquotes
        self.content = self.content.replace("\n", "<br>")
        self.content = self.process_blockquotes(self.content, "&gt;")

    def parse_code_block_markdown(self, reference: bool = False) -> None:
        """Convert code blocks to HTML."""
        self.content = re.sub(r"\n", "<br>", self.content)

        # ```code```
        match: re.Match[str] | None = re.search(self.CODE_BLOCK_PATTERN, self.content)
        while match is not None:
            language_class = "nohighlight"
            affected_text: str | Any = match.group(1)

            for language in self.MARKDOWN_LANGUAGES:
                if affected_text.lower().startswith(language):
                    language_class: str = f"language-{language}"
                    _, _, affected_text = affected_text.partition("<br>")

            affected_text = self.return_to_markdown(affected_text)
            affected_text = re.sub(r"^<br>|<br>$", "", affected_text)
            while (
                "<br>" in affected_text
                and affected_text.startswith("<br>")
                or affected_text.endswith("<br>")
            ):
                affected_text = re.sub(r"^<br>|<br>$", "", affected_text)

            affected_text = re.sub("  ", "&nbsp;&nbsp;", affected_text)

            self.code_blocks_content.append(affected_text)
            placeholder = f"%s{len(self.code_blocks_content)}"

            if not reference:
                replacement = (
                    f'<div class="pre pre--multiline {language_class}">{placeholder}</div>'
                )
            else:
                replacement = f'<span class="pre pre-inline">{placeholder}</span>'

            self.content = self.content.replace(
                self.content[match.start() : match.end()], replacement
            )
            match = re.search(self.CODE_BLOCK_PATTERN, self.content)

        # Process ``code`` and `code`
        for pattern in [self.INLINE_CODE_DOUBLE_PATTERN, self.INLINE_CODE_PATTERN]:
            match = re.search(pattern, self.content)
            while match is not None:
                affected_text = match.group(1)
                affected_text = self.return_to_markdown(affected_text)
                self.code_blocks_content.append(affected_text)
                placeholder: str = f"%s{len(self.code_blocks_content)}"
                replacement: str = f'<span class="pre pre-inline">{placeholder}</span>'
                self.content = self.content.replace(
                    self.content[match.start() : match.end()], replacement
                )
                match = re.search(pattern, self.content)

        self.content = re.sub(r"<br>", "\n", self.content)

    def reverse_code_block_markdown(self) -> None:
        """Replace placeholders with actual code blocks."""
        for i, code_block in enumerate(self.code_blocks_content):
            self.content = self.content.replace(f"%s{i + 1}", code_block)

    def parse_embed_markdown(self) -> None:
        """Convert embed markdown to HTML."""
        # [Message](Link)
        match: re.Match[str] | None = re.search(self.LINK_PATTERN, self.content)
        while match is not None:
            affected_text: str | Any = match.group(1)
            affected_url: str | Any = match.group(2)
            self.content = self.content.replace(
                self.content[match.start() : match.end()],
                f'<a href="{affected_url}">{affected_text}</a>',
            )
            match = re.search(self.LINK_PATTERN, self.content)

        # Process blockquotes in embeds (using > instead of &gt;)
        self.content = self.process_blockquotes(self.content, ">")

    def return_to_markdown(self, content: str) -> str:
        """Convert HTML back to markdown format."""
        patterns: list[tuple[str, str]] = [
            (r"<strong>(.*?)</strong>", "**%s**"),
            (r"<em>([^<>]+)</em>", "*%s*"),
            (r"<h1>([^<>]+)</h1>", "# %s"),
            (r"<h2>([^<>]+)</h2>", "## %s"),
            (r"<h3>([^<>]+)</h3>", "### %s"),
            (r'<span style="text-decoration: underline">([^<>]+)</span>', "__%s__"),
            (r'<span style="text-decoration: line-through">([^<>]+)</span>', "~~%s~~"),
            (r'<div class="quote">(.*?)</div>', "> %s"),
            (
                r'<span class="spoiler spoiler--hidden" onclick="showSpoiler\(event, this\)"> <span '
                r'class="spoiler-text">(.*?)<\/span><\/span>',
                "||%s||",
            ),
            (
                r'<span class="unix-timestamp" data-timestamp=".*?" raw-content="(.*?)">.*?</span>',
                "%s",
            ),
        ]

        for pattern, replacement in patterns:
            compiled_pattern: re.Pattern[str] = re.compile(pattern)
            match: re.Match[str] | None = re.search(compiled_pattern, content)
            while match is not None:
                affected_text: str | Any = match.group(1)
                content = content.replace(
                    content[match.start() : match.end()], replacement % html.escape(affected_text)
                )
                match = re.search(compiled_pattern, content)

        # Process links
        link_pattern: re.Pattern[str] = re.compile(r'<a href="(.*?)">(.*?)</a>')
        match = re.search(link_pattern, content)
        while match is not None:
            affected_url: str | Any = match.group(1)
            affected_text = match.group(2)
            if affected_url != affected_text:
                content = content.replace(
                    content[match.start() : match.end()], f"[{affected_text}]({affected_url})"
                )
            else:
                content = content.replace(content[match.start() : match.end()], affected_url)
            match = re.search(link_pattern, content)

        return content.strip()

    def https_http_links(self) -> None:
        """Parse HTTP and HTTPS links in content."""
        content: str = re.sub(r"\n", "<br>", self.content)
        if "http://" not in content and "https://" not in content or "](" in content:
            return

        def remove_silent_link(url: str, raw_url: Optional[str] = None) -> str:
            if raw_url:
                pattern: str = rf"`.*{raw_url}.*`"
            else:
                pattern = r"`.*http.*`"
            match: re.Match[str] | None = re.search(pattern, self.content)

            if "&lt;" in url and "&gt;" in url and not match:
                return url.replace("&lt;", "").replace("&gt;", "")
            return url

        words: list[Any] = []
        for word in content.replace("<br>", " <br>").split():
            if "http" not in word:
                words.append(word)
                continue

            # Handle silent links <https://...>
            silent_match: re.Match[str] | None = re.search(self.SILENT_LINK_PATTERN, word)
            if silent_match:
                match_url: str | Any = silent_match.group(1)
                url: str = f'<a href="{match_url}">{match_url}</a>'
                word: str = word.replace(match_url, url)
                words.append(remove_silent_link(word, match_url))
                continue

            # Handle regular URLs
            url_match: re.Match[str] | None = re.search(self.URL_PATTERN, word)
            if url_match:
                url = url_match.group()
                # Skip if URL is part of Markdown syntax
                if url.endswith(")"):
                    words.append(word)
                    continue

                word = word.replace(url, f'<a href="{url}">{url}</a>')

            words.append(remove_silent_link(word))

        self.content = re.sub("<br>", "\n", " ".join(words))
