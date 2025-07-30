# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# © 2025 cswimr

from typing import Any, Literal

from typing_extensions import override


class _MissingSentinel:
    __slots__ = ()

    @override
    def __eq__(self, other) -> bool:
        return False

    def __bool__(self) -> bool:
        return False

    @override
    def __hash__(self) -> int:
        return 0

    @override
    def __repr__(self) -> Literal["..."]:
        return "..."


MISSING: Any = _MissingSentinel()
