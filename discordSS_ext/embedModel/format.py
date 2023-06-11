
import typing
import discord
from pydantic import BaseModel
from discordSS_ext.embedModel.cacheFlag import FOOTER_CACHE, CacheFlag
from discordSS_ext.embedModel.model import Embed, ImmutableEmbed
from pydantic.main import ModelMetaclass
import parse


default_cache_method = FOOTER_CACHE()

CLEAR_FLAG = object()

class EDFMeta(ModelMetaclass):
    """
    meta class for EmbedDataFormat

    it handles cache and cache configs
    """

    __instances = {}
    __toggles = {}
    __cache_flags = {}
    __max_size = 100

    def __new__(cls, name, bases, attrs):
        newClass = super().__new__(cls, name, bases, attrs)
        if name == "EmbedDataFormat":
            return newClass

        cls.__instances[newClass] = {}
        cls.__toggles[newClass] = False
        cls.__cache_flags[newClass] = default_cache_method
        
        setattr(newClass, "model", attrs.get("model"))
        return newClass
    
    
    @property
    def CACHE_TOGGLE(cls):
        return cls.__toggles[cls]
    
    @CACHE_TOGGLE.setter
    def CACHE_TOGGLE(cls, value : bool):
        if value == CLEAR_FLAG:
            cls.__instances[cls].clear()
            return

        cls.__toggles[cls] = value

    @property
    def CACHE_MAX_SIZE(cls):
        return cls.__max_size
    
    @CACHE_MAX_SIZE.setter
    def CACHE_MAX_SIZE(cls, value : int):
        if not isinstance(value, int):
            raise TypeError("value must be an int")
        cls.__max_size = value

    def _handle_cache(cls, data :dict, instance : 'EmbedDataFormat'):
        if not cls.CACHE_TOGGLE:
            return data

        if cls not in cls.__cache_flags or not cls.__cache_flags[cls]:
            raise ValueError("cache flag not set")

        flag : CacheFlag = cls.__cache_flags[cls]
        data, id = flag.bake(data)

        cls.__instances[cls][id] = instance.dict(exclude={'model'}, exclude_unset=True)
        
        # handle max size
        if len(cls.__instances[cls]) > cls.__max_size + 10:
            del_count = len(cls.__instances[cls]) - cls.__max_size
            keys = list(cls.__instances[cls].keys())[:del_count]
            for kk in keys:
                del cls.__instances[cls][kk]

        return data

    @property
    def CACHE_TYPE(cls)->CacheFlag:
        return cls.__cache_flags[cls]

    @CACHE_TYPE.setter
    def CACHE_TYPE(cls, value : CacheFlag):
        if not isinstance(value, CacheFlag):
            raise TypeError("value must be a CacheFlag")
        cls.__cache_flags[cls] = value

    @property
    def _CACHE(cls)->dict:
        return cls.__instances[cls]

class EmbedDataFormat(BaseModel, metaclass=EDFMeta):
    """
    a class that stores and handles formatting of embeds with fstrings

    Example:

    ```python
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

    ```

    """

    model : ImmutableEmbed = None
    
    class Config:
        # model excluded
        fields = {
            "model" : {
                "exclude" : True
            }
        }
    
    def format(self, return_immutable : bool = True):
        """
        formats model with the data of this instance
        """

        asdict = self.dict(exclude={'model'}, exclude_unset=True)
        newFormatDict = {}
        for varName, baseStr in self.model.iter():
            if (
                not isinstance(baseStr, str)
                or varName not in self.model.fstring_flap_map
            ):
                newFormatDict[varName] = baseStr
                continue
            
            # fstring
            newStr = baseStr.format(**asdict)
            newFormatDict[varName] = newStr

        # handle 
        newFormatDict = self.__class__._handle_cache(newFormatDict, self)

        im = ImmutableEmbed.fromIterDict(newFormatDict)
        if return_immutable:
            return im
        return im.toDiscordEmbed()
        
    @classmethod
    def fromCache(
        cls, 
        embed: typing.Union[discord.Embed, Embed, str],
        return_raw : bool = False
    ):
        """
        returns either an instance or dict based on the cache
        """

        if not cls.CACHE_TOGGLE:
            raise ValueError("cache toggle not set")
        if not isinstance(embed, str):
            id = cls.CACHE_TYPE.retrieve_id(embed)
        else:
            id = embed

        dict_data= cls._CACHE.get(id, None)
        if return_raw:
            return dict_data
        return cls(**dict_data)

    @classmethod
    def extract(self, embed : typing.Union[discord.Embed, Embed]):
        """
        extracts the data from embed fstrings using parse.parse
        """

        if isinstance(embed, discord.Embed):
            embed = ImmutableEmbed.fromDiscordEmbed(embed)

        iter_list = embed.toIterDict()
        iter_base = self.model.toIterDict()
        
        assert len(iter_list) == len(iter_base)


        parsed_dict = {}
        self.model.fstring_params_map
        for (k, v1), v2 in zip(iter_base.items(),iter_list.values()):
            if k not in self.model.fstring_flap_map:
                continue    
            
            current_scope_param_names = self.model.fstring_params_map.get(k, [])
            if all([x in parsed_dict for x in current_scope_param_names]):
                continue

            parsed_dict.update(parse.parse(v1, v2).named)
        
        return parsed_dict
        
    @classmethod
    def autoParse(
        cls, 
        obj : typing.Union[discord.Embed, Embed, str], 
        return_raw : bool = False
    ):
        """
        first tries to retrieve data from cache,
        if not found, extracts data from fstrings
        """

        trycache = cls.fromCache(obj, return_raw=return_raw)
        if trycache:
            return trycache
        
        extracted = cls.extract(obj)
        if return_raw:
            return extracted
        return cls(**extracted)

    @classmethod
    def formatEmbed(cls, __return_immutable : bool= True, **kwargs):
        """
        classmethod that formats the model with the given kwargs
        """

        return cls(**kwargs).format(return_immutable=__return_immutable)
        
    def __hash__(self):
        return hash(self.model)
    