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
