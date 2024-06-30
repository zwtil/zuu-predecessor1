import copy
from typing import TypedDict
import typing
import discord
import json
import hashlib

cache_var_literal = typing.Literal["no", "footer", "description"]


class FooterDict(TypedDict):
    """A dictionary representing a footer in a Discord embed."""

    text: str
    icon_url: str


class ImageDict(TypedDict):
    """A dictionary representing an image in a Discord embed."""

    url: str
    proxy_url: str
    height: int
    width: int


class ThumbnailDict(TypedDict):
    """A dictionary representing a thumbnail in a Discord embed."""

    url: str
    proxy_url: str
    height: int
    width: int


class AuthorDict(TypedDict):
    """A dictionary representing an author in a Discord embed."""

    name: str
    url: str
    icon_url: str


class FieldDict(TypedDict):
    """A dictionary representing a field in a Discord embed."""

    name: str
    value: str
    inline: bool


class EmbedDict(TypedDict, total=False):
    """A dictionary representing a Discord embed."""

    title: str
    description: str
    color: int
    url: str
    timestamp: str
    footer: FooterDict
    image: ImageDict
    thumbnail: ThumbnailDict
    author: AuthorDict
    fields: list[FieldDict]


class EmbedFactoryMeta(TypedDict):
    """A dictionary representing metadata for an EmbedFactory."""

    locs: dict
    isformat: bool
    cache_var: str
    embed: EmbedDict


class EmbedFactory:
    """A factory class for creating Discord embeds."""

    __meta_dicts: dict[str, EmbedDict] = {}
    __meta_fcache: dict[str, dict] = {}
    __cache_vars: dict[str, dict] = {}

    @classmethod
    def perfect(cls, embed: EmbedDict):
        """Modifies the embed dictionary to include an inline field for each field that does not have it."""
        if "fields" in embed:
            for field in embed["fields"]:
                if "inline" not in field:
                    field["inline"] = False
        return embed

    @classmethod
    def compute_hash(cls, data: typing.Union[dict, discord.Embed]) -> str:
        """Compute SHA256 hash of the dictionary."""
        if isinstance(data, discord.Embed):
            data = data.to_dict()
            data.pop("type")

        json_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_string.encode()).hexdigest()

    @staticmethod
    def check_format_strings(data: EmbedDict) -> dict:
        """Check for format strings in the dictionary and return their locations."""
        locations = {}
        for key, value in data.items():
            if isinstance(value, str):
                locations[key] = "{" in value and "}" in value
            elif isinstance(value, dict):
                result = EmbedFactory.check_format_strings(value)
                if result:
                    locations[key] = result
            elif isinstance(value, list) and all(
                isinstance(item, dict) for item in value
            ):
                for index, item in enumerate(value):
                    result = EmbedFactory.check_format_strings(item)
                    if result:
                        locations[f"{key}[{index}]"] = result
        return locations

    @classmethod
    def __cache_embed(cls, embed_dict: EmbedDict, cache_var: str):
        embed_hash = cls.compute_hash(embed_dict)
        has_format_strings = cls.check_format_strings(embed_dict)
        cls.__meta_dicts[embed_hash] = dict(**embed_dict)
        cls.__meta_fcache[embed_hash] = {
            "locs": has_format_strings,
            "isformat": bool(has_format_strings),
            "cache_var": cache_var,
        }

    @classmethod
    def __cache_var(cls, vars: dict, embed: EmbedDict, cache_var: str) -> str:
        varhash = cls.compute_hash(vars)
        cls.__cache_vars[varhash] = dict(**vars)
        match cache_var:
            case "footer":
                embed["footer"] = FooterDict(text=varhash)
            case "description":
                embed["description"] = varhash
        cls.__cache_vars[cls.compute_hash(embed)] = varhash

    @classmethod
    def simple_create(cls, embed_dict: EmbedDict):
        embed = discord.Embed()
        for key, value in embed_dict.items():
            if key == "fields" and isinstance(value, list):
                for field in value:
                    embed.add_field(
                        name=field["name"],
                        value=field["value"],
                        inline=field.get("inline", False),
                    )
            elif key == "footer":
                embed.set_footer(
                    text=value["text"], icon_url=value.get("icon_url", None)
                )
            elif key == "image":
                embed.set_image(url=value["url"])
            elif key == "thumbnail":
                embed.set_thumbnail(url=value["url"])
            elif key == "author":
                embed.set_author(
                    name=value["name"],
                    url=value.get("url", None),
                    icon_url=value.get("icon_url", None),
                )
            elif key == "color":
                embed.color = discord.Color(value)
            elif hasattr(embed, key):
                setattr(embed, key, value)
        return embed

    @classmethod
    def __format_embed_dict(cls, embed: EmbedDict, vars: dict, hash: str) -> EmbedDict:
        """
        Format the embed dictionary using provided variables based on pre-determined format string locations.

        Args:
            embed (EmbedDict): The dictionary representing the embed.
            vars (dict): The dictionary of variables to be used for formatting.
            hash (str): The hash of the embed.

        Returns:
            EmbedDict: The formatted embed dictionary.
        """

        # Recursively apply formatting to the dictionary based on locations of format strings.
        def apply_formatting(data: dict, locs: dict):
            for key, value in data.items():
                if key in locs:
                    current_locs = locs[key]
                    data[key] = format_based_on_type(value, current_locs, vars)
                elif any(k.startswith(key + "[") for k in locs):
                    if isinstance(value, list):
                        handle_list_formatting(value, locs, key, vars)
            return data

        # Format the value based on its type.
        def format_based_on_type(value, locs, vars):
            if isinstance(value, str) and locs is True:
                return value.format(**vars)
            elif isinstance(value, dict):
                apply_formatting(value, locs)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        apply_formatting(item, locs)
            return value

        # Handle formatting within lists.
        def handle_list_formatting(list_value, locs, base_key, vars):
            for idx, item in enumerate(list_value):
                indexed_key = f"{base_key}[{idx}]"
                if indexed_key in locs:
                    format_based_on_type(item, locs[indexed_key], vars)

        return apply_formatting(embed.copy(), cls.__meta_fcache[hash]["locs"])

    @classmethod
    def create(
        cls,
        embed: typing.Union[str, EmbedDict],
        vars: dict = None,
        cache_dict: bool = True,
        cache_var: cache_var_literal = "no",
    ) -> discord.Embed:
        """
        Creates a Discord embed object based on the given embed dictionary or hash.

        Args:
            embed (Union[str, EmbedDict]): The embed dictionary or hash.
            vars (dict, optional): The dictionary of variables to be used for formatting. Defaults to None.
            cache_dict (bool, optional): Whether to cache the embed dictionary. Defaults to True.
            cache_var (cache_var_literal, optional): The cache variable to be used. Defaults to "no".

        Returns:
            discord.Embed: The created Discord embed object.

        Raises:
            ValueError: If the embed hash is not found in the cache.

        """
        if isinstance(embed, str):
            embed_hash = embed
            if embed_hash not in cls.__meta_dicts:
                raise ValueError("Embed hash not found in cache")
            embed = cls.__meta_dicts[embed_hash]
            cache_var = cls.__meta_fcache[embed_hash]["cache_var"]
        else:
            embed = cls.perfect(embed)
            if cache_dict:
                cls.__cache_embed(embed, cache_var)
            embed_hash = cls.compute_hash(embed)

        embed = copy.deepcopy(embed)
        # format
        if vars and cls.__meta_fcache[embed_hash]["isformat"]:
            embed = cls.__format_embed_dict(embed, vars, embed_hash)

        # apply cache
        if cache_var != "no":
            cls.__cache_var(vars, embed, cache_var)

        # Finally create the discord.Embed object
        return cls.simple_create(embed)

    @classmethod
    def recall_vars(
        cls,
        embed: typing.Union[str, discord.Embed, EmbedDict],
        cache_var: cache_var_literal = None,
    ) -> dict:
        """
        Recalls the variables associated with the given embed.

        Args:
            embed (typing.Union[str, discord.Embed, EmbedDict]): The embed to recall variables for.
            cache_var (cache_var_literal, optional): The cache variable to use. Defaults to None.

        Returns:
            dict: The variables associated with the given embed.

        This function retrieves the variables associated with the given embed. If the embed is a string, it is assumed to be an embed hash and the corresponding variables are retrieved from the cache. If the embed is a discord.Embed object, the function checks if a cache_var is provided. If so, it retrieves the corresponding variable from the embed based on the cache_var. If no cache_var is provided, the function computes the hash of the embed and retrieves the variables from the cache. If the embed is an EmbedDict object, the function retrieves the corresponding variable from the dict based on the cache_var. If no cache_var is provided, the function computes the hash of the dict and retrieves the variables from the cache. If the embed is neither a string nor a discord.Embed or EmbedDict object, the function computes the hash of the perfected version of the embed and retrieves the variables from the cache.

        The function returns the variables associated with the given embed. If the retrieved value is a string, it is assumed to be an embed hash and the corresponding variables are retrieved from the cache.
        """

        if isinstance(embed, str):
            embed_hash = embed
        elif isinstance(embed, discord.Embed) and cache_var:
            match cache_var:
                case "footer":
                    embed_hash = embed.footer.text
                case "description":
                    embed_hash = embed.description
        elif isinstance(embed, discord.Embed):
            embed = embed.to_dict()
            embed.pop("type")
            embed_hash = cls.compute_hash(embed)
        elif isinstance(embed, EmbedDict) and cache_var:
            match cache_var:
                case "footer":
                    embed_hash = embed["footer"]["text"]
                case "description":
                    embed_hash = embed["description"]
        else:
            embed_hash = cls.compute_hash(cls.perfect(embed))

        val = cls.__cache_vars.get(embed_hash, None)
        if isinstance(val, str):
            return cls.__cache_vars[val]
        return val

    @classmethod
    def recall_type(cls, embed: typing.Union[str, EmbedDict]):
        """
        Returns the cache variable associated with the given embed.

        Args:
            embed (Union[str, EmbedDict]): The embed to recall the cache variable for.

        Returns:
            str: The cache variable associated with the given embed.

        This function takes an embed, which can be either a string or an EmbedDict object, and returns the cache variable associated with it. If the embed is a string, it is assumed to be an embed hash and the corresponding cache variable is retrieved from the __meta_fcache dictionary. If the embed is an EmbedDict object, the function computes the hash of the perfected version of the embed and retrieves the cache variable from the __meta_fcache dictionary.

        Example:
            >>> EmbedFactory.recall_type("abc123")
            "footer"
            >>> embed_dict = {"type": 0, "title": "Test Embed", "description": "This is a test embed."}
            >>> EmbedFactory.recall_type(embed_dict)
            "no"
        """
        if isinstance(embed, str):
            embed_hash = embed
        else:
            embed_hash = cls.compute_hash(cls.perfect(embed))
        return cls.__meta_fcache[embed_hash]["cache_var"]
