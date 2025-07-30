import io
from datetime import datetime
from zoneinfo import ZoneInfo

import hikari

from chat_exporter.construct.attachment_handler import AttachmentHandler
from chat_exporter.construct.transcript import Transcript


async def quick_export(
    channel: hikari.TextableGuildChannel,
    bot: hikari.GatewayBot | hikari.RESTBot | None = None,
) -> None | hikari.Message:
    transcript_obj: None | Transcript = await Transcript(
        channel=channel,
        limit=None,
        messages=None,
        zoneinfo=ZoneInfo("UTC"),
        military_time=True,
        fancy_times=True,
        before=None,
        after=None,
        support_dev=True,
        bot=bot,
        attachment_handler=None,
    ).export()

    if not transcript_obj:
        return None

    transcript: str = transcript_obj.html

    if not transcript:
        return None

    transcript_embed = hikari.Embed(
        description=f"**Transcript Name:** transcript-{channel.name}\n\n",
        colour=hikari.Color(0x5865F2),
    )

    transcript_file = hikari.files.Bytes(
        io.BytesIO(transcript.encode()), f"transcript-{channel.name}.html"
    )
    return await channel.send(embed=transcript_embed, attachment=transcript_file)


async def export(
    channel: hikari.TextableGuildChannel,
    limit: int | None = None,
    zoneinfo=ZoneInfo("UTC"),
    bot: hikari.GatewayBot | hikari.RESTBot | None = None,
    military_time: bool = True,
    fancy_times: bool = True,
    before: datetime | None = None,
    after: datetime | None = None,
    support_dev: bool = True,
    attachment_handler: AttachmentHandler | None = None,
) -> str | None:
    transcript_obj: None | Transcript = await Transcript(
        channel=channel,
        limit=limit,
        messages=None,
        zoneinfo=zoneinfo,
        military_time=military_time,
        fancy_times=fancy_times,
        before=before,
        after=after,
        support_dev=support_dev,
        bot=bot,
        attachment_handler=attachment_handler,
    ).export()

    if not transcript_obj:
        return None

    return transcript_obj.html


async def raw_export(
    channel: hikari.TextableGuildChannel,
    messages: list[hikari.Message],
    zoneinfo=ZoneInfo("UTC"),
    bot: hikari.GatewayBot | hikari.RESTBot | None = None,
    military_time: bool = False,
    fancy_times: bool = True,
    support_dev: bool = True,
    attachment_handler: AttachmentHandler | None = None,
) -> str | None:
    transcript_obj: None | Transcript = await Transcript(
        channel=channel,
        limit=None,
        messages=messages,
        zoneinfo=zoneinfo,
        military_time=military_time,
        fancy_times=fancy_times,
        before=None,
        after=None,
        support_dev=support_dev,
        bot=bot,
        attachment_handler=attachment_handler,
    ).export()

    if not transcript_obj:
        return None

    return transcript_obj.html
