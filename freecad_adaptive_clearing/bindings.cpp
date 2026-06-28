// SPDX-License-Identifier: LGPL-2.1-or-later
//
// Python bindings for FreeCAD's adaptive clearing algorithm.
// Original algorithm: Copyright (c) 2018 Kresimir Tusek
// Python bindings:    Copyright (c) 2024 freecad_adaptive_clearing contributors
//
// Uses FreeCAD's own Adaptive.cpp/Adaptive.hpp source files unchanged.

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include "Adaptive.hpp"

namespace py = pybind11;
using namespace AdaptivePath;

PYBIND11_MODULE(_freecad_adaptive_clearing, m) {
    m.doc() = "Adaptive clearing (trochoidal milling) toolpath generation";

    py::enum_<MotionType>(m, "MotionType")
        .value("Cutting", MotionType::mtCutting)
        .value("LinkClear", MotionType::mtLinkClear)
        .value("LinkNotClear", MotionType::mtLinkNotClear)
        .export_values();

    py::enum_<OperationType>(m, "OperationType")
        .value("ClearingInside", OperationType::otClearingInside)
        .value("ClearingOutside", OperationType::otClearingOutside)
        .value("ProfilingInside", OperationType::otProfilingInside)
        .value("ProfilingOutside", OperationType::otProfilingOutside)
        .export_values();

    py::class_<AdaptiveOutput>(m, "AdaptiveOutput")
        .def(py::init<>())
        .def_readwrite("HelixCenterPoint", &AdaptiveOutput::HelixCenterPoint)
        .def_readwrite("StartPoint", &AdaptiveOutput::StartPoint)
        .def_readwrite("AdaptivePaths", &AdaptiveOutput::AdaptivePaths)
        .def_readwrite("ReturnMotionType", &AdaptiveOutput::ReturnMotionType)
        .def_readwrite("ClearedArea", &AdaptiveOutput::ClearedArea)
        .def_readwrite("StartPointNotFound", &AdaptiveOutput::StartPointNotFound)
        .def_readwrite("LeadPathFailed", &AdaptiveOutput::LeadPathFailed)
        .def_readwrite("UnexpectedRotateIterations", &AdaptiveOutput::UnexpectedRotateIterations)
        .def_readwrite("TooManyFailedEngagements", &AdaptiveOutput::TooManyFailedEngagements)
        .def_readwrite("UnclearedAreaRemains", &AdaptiveOutput::UnclearedAreaRemains)
        .def_readwrite("FailedToSetUpFinishingPass", &AdaptiveOutput::FailedToSetUpFinishingPass)
        .def_readwrite("FinishingLeadInFailed", &AdaptiveOutput::FinishingLeadInFailed);

    py::class_<Adaptive2d>(m, "Adaptive2d")
        .def(py::init<>())
        .def_readwrite("toolDiameter", &Adaptive2d::toolDiameter)
        .def_readwrite("helixRampTargetDiameter", &Adaptive2d::helixRampTargetDiameter)
        .def_readwrite("helixRampMinDiameter", &Adaptive2d::helixRampMinDiameter)
        .def_readwrite("stepOverFactor", &Adaptive2d::stepOverFactor)
        .def_readwrite("tolerance", &Adaptive2d::tolerance)
        .def_readwrite("stockToLeave", &Adaptive2d::stockToLeave)
        .def_readwrite("forceInsideOut", &Adaptive2d::forceInsideOut)
        .def_readwrite("finishingProfile", &Adaptive2d::finishingProfile)
        .def_readwrite("keepToolDownDistRatio", &Adaptive2d::keepToolDownDistRatio)
        .def_readwrite("opType", &Adaptive2d::opType)
        .def("Execute",
             [](Adaptive2d& self, const DPaths& stockPaths, const DPaths& paths,
                const DPaths& clearedPaths,
                const std::optional<std::function<bool(TPaths)>>& progressCallbackFn) {
                 auto cb = progressCallbackFn.value_or(
                     [](const TPaths&) { return false; });
                 return self.Execute(stockPaths, paths, clearedPaths, cb);
             },
             py::arg("stockPaths"),
             py::arg("paths"),
             py::arg("clearedPaths"),
             py::arg("progressCallbackFn") = py::none());
}
