# ------------------------------------
# Copyright (c) envbee
# Licensed under the MIT License.
# ------------------------------------

from dataclasses import dataclass


@dataclass
class Metadata:
    limit: int
    offset: int
    total: int
