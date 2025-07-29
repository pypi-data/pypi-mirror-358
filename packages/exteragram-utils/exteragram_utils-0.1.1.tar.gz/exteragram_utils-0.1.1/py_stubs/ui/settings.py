from android.view import View as View
from com.exteragram.messenger.plugins import PluginsConstants
from dataclasses import dataclass, field
from typing import Any, Callable

@dataclass
class Switch:
    key: str
    text: str
    default: bool
    subtext: str = ...
    icon: str = ...
    on_change: Callable[[bool], None] = field(default=None, compare=False, repr=False)
    type: str = field(default=PluginsConstants.Settings.TYPE_SWITCH, init=False)

@dataclass
class Selector:
    key: str
    text: str
    default: int
    items: list[str]
    icon: str = ...
    on_change: Callable[[int], None] = field(default=None, compare=False, repr=False)
    type: str = field(default=PluginsConstants.Settings.TYPE_SELECTOR, init=False)

@dataclass
class Input:
    key: str
    text: str
    default: str = ...
    subtext: str = ...
    icon: str = ...
    on_change: Callable[[str], None] = field(default=None, compare=False, repr=False)
    type: str = field(default=PluginsConstants.Settings.TYPE_INPUT, init=False)

@dataclass
class Text:
    text: str
    icon: str = ...
    accent: bool = ...
    red: bool = ...
    on_click: Callable[[View], None] = field(default=None, compare=False, repr=False)
    create_sub_fragment: Callable[[], list[Any]] = field(default=None, compare=False, repr=False)
    type: str = field(default=PluginsConstants.Settings.TYPE_TEXT, init=False)

@dataclass
class Header:
    text: str
    type: str = field(default=PluginsConstants.Settings.TYPE_HEADER, init=False)

@dataclass
class Divider:
    text: str = ...
    type: str = field(default=PluginsConstants.Settings.TYPE_DIVIDER, init=False)
