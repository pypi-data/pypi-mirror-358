# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# © 2025 cswimr

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple, Union

import orjson
from furl import furl
from typing_extensions import Self, override


@dataclass
class SemVer:
    major: int
    minor: int
    patch: int
    extra: Optional[str] = None
    commit: Optional[str] = None

    @override
    def __str__(self) -> str:
        string = f"{self.major}.{self.minor}.{self.patch}"
        if self.extra:
            string += f"{self.extra}"
        if self.commit:
            string += f"+{self.commit}"
        return string

    @classmethod
    def from_str(cls, version: str, /) -> Self:
        """
        Parse a version string of the form `MAJOR.MINOR.PATCH[EXTRA]`, where `EXTRA` is any string (often things like '-alpha.1' or '+build.123').
        """
        pattern = r"^(\d+)\.(\d+)\.(\d+)([-+].+)?$"
        m = re.match(pattern, version)
        if not m:
            msg = f"Invalid SemVer string: {version!r}"
            raise ValueError(msg)
        major, minor, patch, extra = m.groups()
        return cls(int(major), int(minor), int(patch), extra)

    @classmethod
    def from_tuple(cls, version: Union[Tuple[int, int, int, str, str], Tuple[int, int, int, str], Tuple[int, int, int]]) -> Self:
        major, minor, patch, extra, commit = (*version, None, None)[:5]
        extra = f"-{str(extra).lstrip('-')}" if extra else None
        return cls(major, minor, patch, extra, commit)  # pyright: ignore[reportArgumentType]


@dataclass
class User:
    name: str
    profile: furl

    @override
    def __str__(self) -> str:
        return self.name

    @property
    def markdown(self) -> str:
        return f"[{self.name}]({self.profile})"


@dataclass
class Repository:
    owner: str
    name: str
    url: furl

    @override
    def __str__(self) -> str:
        return self.name

    @property
    def slug(self) -> str:
        return self.name.lower()

    @property
    def issues(self) -> furl:
        return self.url / "issues"

    @property
    def markdown(self) -> str:
        return f"[{self.owner}/{self.name}]({self.url})"


@dataclass
class CogMetadata:
    name: str
    version: SemVer
    authors: List[User]
    repository: Repository
    documentation: Optional[furl] = None

    @classmethod
    def from_json(cls, cog_name: str, file: Path) -> "CogMetadata":
        """Load cog metadata from a JSON file.

        Args:
            cog_name (str): The name of the cog.
            file (Path): The file path of the JSON file to load from.

        Returns:
            CogMetadata: The constructed metadata object.
        """
        with open(file, "rb") as f:
            obj = orjson.loads(f.read())

        authors = [User(name=author["name"], profile=furl(author["url"])) for author in obj["authors"]]
        repository = Repository(owner=obj["repository"]["owner"], name=obj["repository"]["name"], url=furl(obj["repository"]["url"]))
        if (documentation := obj.get("documentation", None)) is not None:
            documentation = furl(documentation)
        version = SemVer.from_str(obj["version"])
        return cls(name=cog_name, version=version, authors=authors, repository=repository, documentation=documentation)


@dataclass
class TidegearMeta:
    version: SemVer
    repository: Repository

    @override
    def __str__(self) -> str:
        return str(self.version)

    @property
    def markdown(self) -> str:
        return f"[{self.version}]({self.repository.url})"
