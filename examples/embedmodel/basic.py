from discordSS_ext.embedModel import ImmutableEmbed, EmbedDataFormat

embed = ImmutableEmbed(
    title="template {name}",
    description="this is a template embed",
    color=0x00ff00,
    fields=[
        {
            "name": "{fn1}",
            "value": "{fv1}",
        }
    ]
)

class Format1(EmbedDataFormat):
    model = embed
    name : str 
    fn1 : str
    fv1 : int


embed1 = Format1.formatEmbed(
    name = "name",
    fn1 = "field name",
    fv1 = 123
).toDiscordEmbed()
