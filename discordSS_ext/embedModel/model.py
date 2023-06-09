
from functools import cached_property
from string import Formatter
import typing
from discord import Embed as DiscordEmbed
from pydantic import BaseModel, Field as F

from discordSS.utils import is_fstring

class ExtendedModel(BaseModel):
    def __iter_list_element(self,data:list, parent :str):
        for i, v in enumerate(data):
            if isinstance(v, dict):
                for k, vv in v.items():
                    yield parent + f"/[{i}]/{k}", vv
            
    def iter(self, parent : str = ""):
        for key, value in self.dict().items():
            if isinstance(value, list):
                yield from self.__iter_list_element(value, parent+key)
            if isinstance(value, ExtendedModel):
                value : ExtendedModel
                yield from value.iter(parent + key)
            else:
                yield parent + key, value

    def toIterDict(self):
        return dict(self.iter())

class Embed(ExtendedModel):
    """
    mutable pydantic model for discord embeds
    """
    class Author(ExtendedModel):
        name: str
        url: str = None
        icon_url: str = None
        
    class Field(ExtendedModel):
        name: str
        value: str
        inline: bool = False
        
    class Video(ExtendedModel):
        url: str
        height: int
        width: int
    
    class Footer(ExtendedModel):
        text: str
        icon_url: str = None

    title :str = None
    description: str = None
    color: int = None
    url: str = None
    author : Author = None
    fields: typing.List[Field] = F(default_factory=list)
    thumbnail: str = None
    image: str = None
    footer: Footer = None
    timestamp: str = None
    video: Video = None
    
    class Config:
        keep_untouched = (cached_property,)
    
    @classmethod
    def fromDiscordEmbed(cls, embed: DiscordEmbed):
        embed_dict = embed.to_dict()
        return cls(**embed_dict)
    
    def toDiscordEmbed(self):
        embed_dict = self.dict()
        return DiscordEmbed.from_dict(embed_dict)
    
    def toImmutable(self):
        return ImmutableEmbed(**self.dict())
    
    

    @classmethod
    def fromIterDict(cls, embed_dict: dict):
        """
        this method parses dict from iter method
        """

        def _handler_field(k, v, target: dict):
            # it is a field
            raw = k.split("[", 1)[1]
            index, fieldname = raw.split("]/", 1)
            index = int(index)  
            if index not in target:
                target[index] = {}
            target[index][fieldname] = v

        field_dict = {}
        target_dict = {}
        for k, v in embed_dict.items():
            pk = None
            if "[" in k:
                _handler_field(k, v, field_dict)
                continue

            if "/" in k:
                pk, k = k.split("/", 1)
            if pk is None:
                target_dict[k] = v
                continue
            if pk not in target_dict or not isinstance(target_dict[pk], dict):
                target_dict[pk] = {}
            target_dict[pk][k] = v

        # sort field dict by key and insert
        target_dict["fields"] = []
        for k, v in sorted(field_dict.items(), key=lambda x: x[0]):
            target_dict["fields"].append(v)

        return cls(**target_dict)
        
                
    
class ImmutableEmbed(Embed):
    """
    immutable pydantic model for discord embeds
    """
    
    class Config:
        allow_mutation = False
        frozen = True
        keep_untouched = (cached_property,)
    
    def toMutable(self):
        return Embed(**self.dict())

    @cached_property
    def fstring_flap_map(self):
        """
        this property is used to store fstring flags
        """
        flags = {}
        for k, v in self.iter():
            if not isinstance(v, str):
                continue
            if not is_fstring(v):
                continue
            flags[k] = v

        return flags
    
    @cached_property
    def fstring_params_map(self):
        params = {}
        for k,v in self.fstring_flap_map.items():
            fieldnames = [fname for _, fname, _, _ in Formatter().parse(v) if fname]
            params[k] = fieldnames

        return params
    
    def __hash__(self):
        return hash(self.json())
    
    @cached_property
    def _toIterDict(self):
        data= {}
        for k, v in self.iter():
            data[k] = v
        return data

    def toIterDict(self):
        return self._toIterDict

