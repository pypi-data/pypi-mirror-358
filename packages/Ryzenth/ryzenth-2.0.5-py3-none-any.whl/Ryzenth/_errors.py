#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2019-2025 (c) Randy W @xtdevs, @xtsea
#
# from : https://github.com/TeamKillerX
# Channel : @RendyProjects
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json


class WhatFuckError(Exception):
    pass

class ParamsRequiredError(ValueError):
    pass

class ForbiddenError(Exception):
    """Custom exception for 403 Forbidden"""
    pass

class ToolNotFoundError(Exception):
    """Raised when a base URL for a requested tool cannot be found."""
    pass

class InternalError(Exception):
    """Custom exception for 500 Error"""
    pass

class RequiredError(ValueError):
    pass

class InvalidModelError(ValueError):
    pass

class UnauthorizedAccessError(ValueError):
    pass

class InvalidVersionError(ValueError):
    pass

class InvalidJSONDecodeError(json.decoder.JSONDecodeError):
    pass

class InvalidEmptyError(ValueError):
    pass

__all__ = [
    "WhatFuckError",
    "ForbiddenError",
    "InternalError",
    "ToolNotFoundError",
    "ParamsRequiredError",
    "InvalidVersionError",
    "InvalidJSONDecodeError",
    "InvalidEmptyError",
    "InvalidModelError",
    "UnauthorizedAccessError",
    "RequiredError"
]
