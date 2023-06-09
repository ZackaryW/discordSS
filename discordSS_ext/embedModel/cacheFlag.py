
import typing
import uuid

from discord import Embed  

class CacheFlag:
    def create_new(self) -> str:
        pass

    def bake(self, dictdata : dict) -> typing.Tuple[dict,str]:
        pass

    def retrieve_id(self, embed : Embed) -> str:
        pass


class FOOTER_CACHE(CacheFlag):
    def create_new(self) -> str:
        return str(uuid.uuid4())

    def bake(self, dictdata : dict) -> typing.Tuple[dict,str]:
        if "footer/text" in dictdata:
            raise ValueError("footer/text already exists in dictdata")
        id : str = self.create_new()
        dictdata["footer/text"] = id
        return dictdata,id


    def retrieve_id(self, embed : Embed) -> str:
        return embed.footer.text