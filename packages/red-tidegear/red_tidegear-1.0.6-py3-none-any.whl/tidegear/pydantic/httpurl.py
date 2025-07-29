# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# © 2025 cswimr

from typing import Optional

from discord.utils import MISSING
from pydantic import HttpUrl as PydanticHttpUrl
from typing_extensions import Self


class HttpUrl(PydanticHttpUrl):
    """
    A subclass of `pydantic.HttpUrl` that adds some useful methods and operator overloads for more ergonomic path manipulation and URL composition.

    Operations:
      - `url / "segment"`  - returns a new HttpUrl with "segment" appended to the path
      - `url /= "segment"` - in-place append of "segment" to the path

    Examples:
        >>> u = HttpUrl("https://example.com/api")
        >>> u2 = u / "v1" / "users"
        >>> print(u2)
        https://example.com/api/v1/users

        >>> u2 /= "123"
        >>> print(u2)
        https://example.com/api/v1/users/123
    """

    def __truediv__(self, other: str) -> Self:
        return self.join(other)

    def __itruediv__(self, other: str) -> Self:
        return self.__truediv__(other)

    @property
    def base(self) -> Self:
        """Wrapper around `HttpUrl.join()` that returns the base URL (scheme, host, etc.).

        Returns:
            Self: The new HttpUrl object pointing to the base URL of the source HttpUrl object.
        """
        return self.join(None, query=None, fragment=None)

    def join(self, path: Optional[str] = MISSING, /, *, query: Optional[str] = MISSING, fragment: Optional[str] = MISSING) -> Self:
        """Create a new HttpUrl object using `HttpUrl.build()`.

        Args:
            path (str): The path to add to this HttpUrl's path.
                Defaults to MISSING, will replace the original path if set to `None`.
            query (str | None): The query to replace this HttpUrl's query with.
                Defaults to MISSING, will replace the original query if set to `None`.
            fragment (str | None): The fragment to replace this HttpUrl's fragment with.
                Defaults to MISSING, will replace the original fragment if set to `None`.

        Returns:
            Self: The new HttpUrl object.
        """

        def _strip(s: str, /) -> str:
            return s.lstrip("/").rstrip("/")

        base = _strip(self.path or "")

        if path is MISSING:
            new_path = base
        elif path is None:
            new_path = ""
        else:
            seg = _strip(path)
            new_path = f"{base}/{seg}" if base else seg

        return self.build(
            scheme=self.scheme,
            username=self.username,
            password=self.password,
            host=self.host or "",
            port=self.port,
            path=new_path,
            query=self.query if query is MISSING else query,
            fragment=self.fragment if fragment is MISSING else fragment,
        )
