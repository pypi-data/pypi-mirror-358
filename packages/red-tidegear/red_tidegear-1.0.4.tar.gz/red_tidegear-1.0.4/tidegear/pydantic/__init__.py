# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# © 2025 cswimr

from importlib.util import find_spec

if not find_spec("pydantic"):
    raise ImportError(
        "pydantic is not installed, but the `cogutils.pydantic` module was imported! Did you install cogutils with the `pydantic` extra?"
    )

from .basemodel import BaseModel, CogModel
from .httpurl import HttpUrl

__all__ = ["BaseModel", "CogModel", "HttpUrl"]
