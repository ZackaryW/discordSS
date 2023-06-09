import unittest

import discord
from discordSS_ext.embedModel import Embed
from discord.embeds import EmbedProxy
from discordSS_ext.embedModel.format import EmbedDataFormat, EDFMeta #  # noqa: F401
from discordSS_ext.embedModel.model import ImmutableEmbed



class t_embedmodel(unittest.TestCase):
    def setUp(self):
        self.e1 = ImmutableEmbed(
            title = "this is a {title}",
            description="this is a {description}",
            url = "https://example.com/{url}",
            color = 0x000000,
        )
        class t1(EmbedDataFormat):
            model = self.e1
            title :str
            description :str
            url :str

        self.t1 = t1

    def test_model_1(self):
        e1 = Embed(
            title = "title",
            description = "description",
            url = "https://example.com",
            color = 0x000000,
            timestamp = "2021-01-01T00:00:00.000Z",
            footer = {
                "text": "footer text",
                "icon_url": "https://example.com"
            },
            image = "https://example.com",
            thumbnail = "https://example.com",
            fields=[
                {
                    "name": "field name",
                    "value": "field value",
                    "inline": True
                }
            ]
        )
        te1 = e1.toDiscordEmbed()
        self.assertEqual(te1.title, "title")
        self.assertIsInstance(te1, discord.Embed)
        self.assertIsInstance(te1.footer, EmbedProxy)

    def test_format_1(self):
        self.assertIsInstance(self.e1, ImmutableEmbed)
        
        ins_t1 = self.t1.formatEmbed(
            title = "1",
            description = "2",
            url = "3"
        )
        self.assertIsInstance(ins_t1, ImmutableEmbed)
        self.assertEqual(ins_t1.title, "this is a 1")
        self.assertEqual(ins_t1.description, "this is a 2")
        self.assertEqual(ins_t1.url, "https://example.com/3")
        self.assertIsInstance(ins_t1.toDiscordEmbed(), discord.Embed)

    def test_cache(self):
        self.t1.CACHE_TOGGLE = True
        self.t1.CACHE_MAX_SIZE =50
        for i in range(100):
            x1 = self.t1.formatEmbed(
                title = i,
                description = "2",
                url = "3"
            )
            self.assertIsInstance(x1, ImmutableEmbed)
            self.assertTrue(hasattr(x1.footer, "text"))
            print(x1.footer.text)

        t1data = self.t1.fromCache(x1)  
        self.assertIsInstance(t1data, self.t1)
        self.assertEqual(t1data.title, "99")
        pass

    def test_extract(self):
        e2 = ImmutableEmbed(
            title = "title {a}",
            description = "description {b}",
            url = "https://example.com",
            color = 0x000000,
            timestamp = "2021-01-01T00:00:00.000Z",
            footer = {
                "text": "footer text",
                "icon_url": "https://example.com"
            },
            image = "https://example.com/",
            thumbnail = "https://example.com",
            fields=[
                {
                    "name": "field {k}",
                    "value": "field {k}",
                    "inline": True
                }
            ]
        )

        class t2(EmbedDataFormat):
            model = e2
            a :str
            b :str
            k :str

        w2 = t2.formatEmbed(
            a = "1",
            b = "2",
            k = "3"
        ).toDiscordEmbed()

        self.assertEqual(w2.title, "title 1")
        self.assertEqual(w2.description, "description 2")
        self.assertEqual(w2.fields[0].name, "field 3")
        self.assertEqual(w2.fields[0].value, "field 3")
        t2.extract(w2)