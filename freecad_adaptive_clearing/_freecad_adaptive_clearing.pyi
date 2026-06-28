from collections.abc import Callable
from enum import IntEnum

Coordinate = tuple[float, float]
Path = list[Coordinate]
CppMotionSegment = tuple[int, Path]
CppMotionSegments = list[CppMotionSegment]

class MotionType(IntEnum):
    Cutting = 0
    LinkClear = 1
    LinkNotClear = 2

class OperationType(IntEnum):
    ClearingInside = 0
    ClearingOutside = 1
    ProfilingInside = 2
    ProfilingOutside = 3

class AdaptiveOutput:
    HelixCenterPoint: Coordinate
    StartPoint: Coordinate
    AdaptivePaths: CppMotionSegments
    ReturnMotionType: int
    ClearedArea: float
    StartPointNotFound: bool
    LeadPathFailed: bool
    UnexpectedRotateIterations: bool
    TooManyFailedEngagements: bool
    UnclearedAreaRemains: bool
    FailedToSetUpFinishingPass: bool
    FinishingLeadInFailed: bool

    def __init__(self) -> None: ...

class Adaptive2d:
    toolDiameter: float
    helixRampTargetDiameter: float
    helixRampMinDiameter: float
    stepOverFactor: float
    tolerance: float
    stockToLeave: float
    forceInsideOut: bool
    finishingProfile: bool
    keepToolDownDistRatio: float
    opType: OperationType

    def __init__(self) -> None: ...
    def Execute(
        self,
        stockPaths: list[Path],
        paths: list[Path],
        clearedPaths: list[Path] | None = None,
        progressCallbackFn: Callable[[CppMotionSegments], bool] | None = None,
    ) -> list[AdaptiveOutput]: ...
