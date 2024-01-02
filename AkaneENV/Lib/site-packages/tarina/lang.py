from __future__ import annotations

import contextlib
import json
import locale
import os
import sys
from pathlib import Path
from typing import Any, Final, TypedDict, final

from typing_extensions import NotRequired, Self

root_dir: Final[Path] = Path(__file__).parent / "i18n"
WINDOWS = sys.platform.startswith("win") or (sys.platform == "cli" and os.name == "nt")


class _LangDict(TypedDict):
    default: NotRequired[str]
    frozen: NotRequired[list[str]]
    require: NotRequired[list[str]]


def _get_win_locale_with_ctypes() -> str | None:
    import ctypes

    kernel32 = ctypes.windll.kernel32
    lcid: int = kernel32.GetUserDefaultUILanguage()
    return locale.windows_locale.get(lcid)


def _get_win_locale_from_registry() -> str | None:
    import winreg  # noqa

    with contextlib.suppress(Exception):
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"Control Panel\International"
        ) as key:
            if lcid := winreg.QueryValueEx(key, "Locale")[0]:
                return locale.windows_locale.get(int(lcid, 16))


if WINDOWS:
    try:
        import ctypes

        _get_win_locale = _get_win_locale_with_ctypes
    except ImportError:
        _get_win_locale = _get_win_locale_from_registry


def get_locale() -> str | None:
    if WINDOWS:
        return _get_win_locale()

    return locale.getlocale(locale.LC_MESSAGES)[0]


def _get_config(root: Path) -> dict[str, Any]:
    if not (root / ".config.json").exists():
        return {}
    with (root / ".config.json").open("r", encoding="utf-8") as f:
        return json.load(f)


def _get_scopes(root: Path) -> list[str]:
    return [
        i.stem for i in root.iterdir() if i.is_file() and not i.name.startswith(".")
    ]


def _get_lang(root: Path, _type: str) -> dict[str, dict[str, str]]:
    with (root / f"{_type}.json").open("r", encoding="utf-8") as f:
        return json.load(f)


def merge(source: dict, target: dict, ignore: list[str] | None = None) -> dict:
    ignore = ignore or []
    for key, value in source.items():
        if key in target and key in ignore:
            continue
        if isinstance(value, dict):
            target[key] = merge(value, target.get(key, {}))
        elif isinstance(value, list):
            target[key] = value + target.get(key, [])
        else:
            target[key] = value
    return target


@final
class _LangConfig:
    def __init__(self):
        __config = _get_config(root_dir)
        self.__scope: str = __config["default"]
        self.__frozen: list[str] = __config["frozen"]
        self.__require: list[str] = __config["require"]
        self.__langs = {t.replace("_", "-"): _get_lang(root_dir, t) for t in _get_scopes(root_dir)}
        self.__scopes = set(self.__langs.keys())
        self.select_local()

    @property
    def scopes(self):
        return self.__scopes

    @property
    def current(self):
        return self.__scope

    def select_local(self):
        """
        依据系统语言尝试自动选择语言
        """
        if (lc := get_locale()) and lc.replace("_", "-") in self.__langs:
            self.__scope = lc.replace("_", "-")
        return self

    def select(self, item: str) -> Self:
        item = item.replace("_", "-")
        if item not in self.__langs:
            raise ValueError(self.require("lang", "scope_error").format(target=item))
        self.__scope = item
        return self

    def save(self, root: Path | None = None):
        _root = root or root_dir
        config = _get_config(_root)
        config["default"] = self.__scope
        with (_root / ".config.json").open("w+", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def load_data(self, scope: str, data: dict[str, dict[str, str]]):
        if scope in self.__langs:
            self.__langs[scope] = merge(
                data, self.__langs[scope], self.__frozen
            )
        else:
            self.__scopes.add(scope)
            self.__langs[scope] = data
        for key in self.__require:
            parts = key.split(".", 1)
            t = parts[0]
            n = parts[1] if len(parts) > 1 else None
            if t not in self.__langs[scope]:
                raise KeyError(
                    self.require("lang", "miss_require_type", scope).format(
                        scope=scope, target=t
                    )
                )
            if n and n not in self.__langs[scope][t]:
                raise KeyError(
                    self.require("lang", "miss_require_name", scope).format(
                        scope=scope, type=t, target=n
                    )
                )

    def load_file(self, filepath: Path):
        return self.load_data(filepath.stem, _get_lang(filepath.parent, filepath.stem))

    def load_config(self, config: _LangDict):
        self.__scope = config.get("default", self.__scope)
        self.__frozen.extend(config.get("frozen", []))
        self.__require.extend(config.get("require", []))
        self.select_local()

    def load(self, root: Path):
        self.load_config(_get_config(root))
        for i in root.iterdir():
            if not i.is_file() or i.name.startswith("."):
                continue
            self.load_file(i)

    def require(self, _type: str, _name: str, scope: str | None = None) -> str:
        scope = scope or self.__scope
        if scope not in self.__langs:
            raise ValueError(
                self.__langs[self.__scope]["lang"]["scope_error"].format(target=scope)
            )
        if _type in self.__langs[scope]:
            _types = self.__langs[scope][_type]
        elif _type in self.__langs[self.__scope]:
            _types = self.__langs[self.__scope][_type]
        elif _type in self.__langs[(default := _get_config(root_dir)["default"])]:
            _types = self.__langs[default][_type]
        else:
            raise ValueError(
                self.__langs[scope]["lang"]["type_error"].format(
                    target=_type, scope=scope
                )
            )
        if _name in _types:
            return _types[_name]
        elif _name in self.__langs[self.__scope][_type]:
            return self.__langs[self.__scope][_type][_name]
        elif _name in self.__langs[(default := _get_config(root_dir)["default"])][_type]:
            return self.__langs[default][_type][_name]
        else:
            raise ValueError(
                self.__langs[scope]["lang"]["name_error"].format(
                    target=_name, scope=scope, type=_type
                )
            )

    def set(self, _type: str, _name: str, content: str, scope: str | None = None):
        scope = scope or self.__scope
        if scope not in self.__langs:
            raise ValueError(
                self.__langs[self.__scope]["lang"]["scope_error"].format(target=scope)
            )
        if _type in self.__frozen:
            raise ValueError(
                self.__langs[scope]["lang"]["type_error"].format(
                    target=_type, scope=scope
                )
            )
        self.__langs[scope].setdefault(_type, {})[_name] = content

    def __repr__(self):
        return f"<LangConfig: {self.__scope}>"


lang: _LangConfig = _LangConfig()

__all__ = ["lang"]
