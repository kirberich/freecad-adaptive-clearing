# SPDX-License-Identifier: LGPL-2.1-or-later
#
# Python wrapper for FreeCAD's adaptive clearing algorithm by Kresimir Tusek
"""
freecad_adaptive_clearing — Standalone adaptive clearing library.

This package provides Python bindings for FreeCAD's adaptive clearing algorithm,
while avoiding having to build all of FreeCAD.

Usage:
    from freecad_adaptive_clearing import Adaptive2d, OperationType

    a2d = Adaptive2d(
        tool_diameter=5.0,
        step_over_factor=0.20,
        tolerance=0.1,
        stock_to_leave=0.0,
        force_inside_out=True,
        finishing_profile=True,
        op_type=OperationType.ClearingInside,
    )

    results = a2d.execute(stock_paths, boundary_paths, cleared_paths=[])
"""

from typing import Any, Callable

from ._freecad_adaptive_clearing import Adaptive2d as _Adaptive2d
from ._freecad_adaptive_clearing import AdaptiveOutput as _CppAdaptiveOutput
from ._freecad_adaptive_clearing import MotionType, OperationType

Coordinate = tuple[float, float]
Path = list[Coordinate]
MotionSegment = tuple[MotionType, Path]
MotionSegments = list[MotionSegment]


class AdaptiveOutput:
    """Output from processing one connected region."""

    helix_center_point: Coordinate
    start_point: Coordinate
    adaptive_paths: MotionSegments
    return_motion_type: MotionType
    cleared_area: float
    start_point_not_found: bool
    lead_path_failed: bool
    unexpected_rotate_iterations: bool
    too_many_failed_engagements: bool
    uncleared_area_remains: bool
    failed_to_set_up_finishing_pass: bool
    finishing_lead_in_failed: bool

    def __init__(self, cpp_output: _CppAdaptiveOutput | None = None) -> None:
        if cpp_output is not None:
            self.helix_center_point = (
                cpp_output.HelixCenterPoint[0],
                cpp_output.HelixCenterPoint[1],
            )
            self.start_point = (cpp_output.StartPoint[0], cpp_output.StartPoint[1])
            self.adaptive_paths = [
                (MotionType(mt), [(p[0], p[1]) for p in pts])
                for mt, pts in cpp_output.AdaptivePaths
            ]
            self.return_motion_type = MotionType(cpp_output.ReturnMotionType)
            self.cleared_area = cpp_output.ClearedArea
            self.start_point_not_found = cpp_output.StartPointNotFound
            self.lead_path_failed = cpp_output.LeadPathFailed
            self.unexpected_rotate_iterations = cpp_output.UnexpectedRotateIterations
            self.too_many_failed_engagements = cpp_output.TooManyFailedEngagements
            self.uncleared_area_remains = cpp_output.UnclearedAreaRemains
            self.failed_to_set_up_finishing_pass = cpp_output.FailedToSetUpFinishingPass
            self.finishing_lead_in_failed = cpp_output.FinishingLeadInFailed
        else:
            self.helix_center_point = (0.0, 0.0)
            self.start_point = (0.0, 0.0)
            self.adaptive_paths = []
            self.return_motion_type = MotionType.Cutting
            self.cleared_area = 0.0
            self.start_point_not_found = False
            self.lead_path_failed = False
            self.unexpected_rotate_iterations = False
            self.too_many_failed_engagements = False
            self.uncleared_area_remains = False
            self.failed_to_set_up_finishing_pass = False
            self.finishing_lead_in_failed = False


class Adaptive2d:
    """Adaptive clearing algorithm (wraps FreeCAD's C++ Adaptive2d).

    tool_diameter: float
        Diameter of the cutting tool in mm.
    step_over_factor: float
        Fraction of tool diameter to step over per pass, 0.01-1.0.
    tolerance: float
        Accuracy vs. performance, 0.01-1.0.
    stock_to_leave: float
        Radial stock to leave for finishing in mm.
    helix_ramp_target_diameter: float
        Target helix entry diameter in mm (defaults to tool_diameter).
    helix_ramp_min_diameter: float
        Minimum acceptable helix diameter in mm (defaults to tool_diameter/8).
    force_inside_out: bool
        Force plunging inside material and clearing outward.
    finishing_profile: bool
        Take a finishing profile pass at the end.
    keep_tool_down_dist_ratio: float
        Max ratio of tool-down link length to direct distance (defaults to 3.0).
    op_type : OperationType
        One of ClearingInside, ClearingOutside, ProfilingInside, ProfilingOutside.
    """

    def __init__(
        self,
        *,
        tool_diameter: float,
        step_over_factor: float,
        tolerance: float,
        stock_to_leave: float,
        force_inside_out: bool,
        finishing_profile: bool,
        op_type: OperationType,
        helix_ramp_target_diameter: float | None = None,
        helix_ramp_min_diameter: float | None = None,
        keep_tool_down_dist_ratio: float | None = None,
    ) -> None:
        self._cpp: _Adaptive2d = _Adaptive2d()
        self._cpp.toolDiameter = tool_diameter
        self._cpp.stepOverFactor = step_over_factor
        self._cpp.tolerance = tolerance
        self._cpp.stockToLeave = stock_to_leave
        self._cpp.forceInsideOut = force_inside_out
        self._cpp.finishingProfile = finishing_profile
        self._cpp.opType = op_type

        if helix_ramp_target_diameter is not None:
            self._cpp.helixRampTargetDiameter = helix_ramp_target_diameter
        if helix_ramp_min_diameter is not None:
            self._cpp.helixRampMinDiameter = helix_ramp_min_diameter
        if keep_tool_down_dist_ratio is not None:
            self._cpp.keepToolDownDistRatio = keep_tool_down_dist_ratio

    @property
    def tool_diameter(self) -> float:
        return self._cpp.toolDiameter

    @property
    def step_over_factor(self) -> float:
        return self._cpp.stepOverFactor

    @property
    def tolerance(self) -> float:
        return self._cpp.tolerance

    @property
    def stock_to_leave(self) -> float:
        return self._cpp.stockToLeave

    @property
    def helix_ramp_target_diameter(self) -> float:
        return self._cpp.helixRampTargetDiameter

    @property
    def helix_ramp_min_diameter(self) -> float:
        return self._cpp.helixRampMinDiameter

    @property
    def force_inside_out(self) -> bool:
        return self._cpp.forceInsideOut

    @property
    def finishing_profile(self) -> bool:
        return self._cpp.finishingProfile

    @property
    def keep_tool_down_dist_ratio(self) -> float:
        return self._cpp.keepToolDownDistRatio

    @property
    def op_type(self) -> OperationType:
        return self._cpp.opType

    def execute(
        self,
        stock_paths: list[Path],
        boundary_paths: list[Path],
        cleared_paths: list[Path] | None = None,
        progress_callback: Callable[[MotionSegments], bool] | None = None,
    ) -> list[AdaptiveOutput]:
        """Run the algorithm.

        stock_paths: Stock material boundary polygon(s).
        boundary_paths: Region(s) to machine - first path is outer boundary, rest are holes.
        cleared_paths: Optional pre-cleared areas for rest machining.
        progress_callback: Optional callable, called periodically. Return True to abort."""

        cpp_progress_callback: Callable[[Any], bool] | None = None
        if progress_callback is not None:

            def convert_progress_callback(cpp_paths: Any) -> bool:
                paths: MotionSegments = [
                    (MotionType(mt), [(p[0], p[1]) for p in pts])
                    for mt, pts in cpp_paths
                ]
                return progress_callback(paths)

            cpp_progress_callback = convert_progress_callback

        cpp_results = self._cpp.Execute(
            stock_paths,
            boundary_paths,
            cleared_paths or [],
            cpp_progress_callback,
        )
        return [AdaptiveOutput(r) for r in cpp_results]


__all__ = [
    "Adaptive2d",
    "AdaptiveOutput",
    "Coordinate",
    "Path",
    "MotionSegment",
    "MotionSegments",
    "OperationType",
    "MotionType",
]
