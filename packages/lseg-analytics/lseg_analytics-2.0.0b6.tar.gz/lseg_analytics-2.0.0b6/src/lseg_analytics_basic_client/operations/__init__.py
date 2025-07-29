# coding=utf-8


from ._operations import (
    YieldBookRestOperations,
    calendarResourceOperations,
    calendarsResourceOperations,
    floatingRateIndexResourceOperations,
    floatingRateIndicesResourceOperations,
    fxForwardCurveResourceOperations,
    fxForwardCurvesResourceOperations,
    fxForwardResourceOperations,
    fxForwardsResourceOperations,
    fxSpotResourceOperations,
    fxSpotsResourceOperations,
    instrumentTemplateResourceOperations,
    instrumentTemplatesResourceOperations,
    irSwapResourceOperations,
    irSwapsResourceOperations,
)
from ._patch import *  # pylint: disable=unused-wildcard-import
from ._patch import __all__ as _patch_all
from ._patch import patch_sdk as _patch_sdk

__all__ = [
    "calendarsResourceOperations",
    "calendarResourceOperations",
    "fxForwardCurvesResourceOperations",
    "fxForwardCurveResourceOperations",
    "fxForwardsResourceOperations",
    "fxForwardResourceOperations",
    "fxSpotsResourceOperations",
    "fxSpotResourceOperations",
    "YieldBookRestOperations",
    "instrumentTemplatesResourceOperations",
    "instrumentTemplateResourceOperations",
    "irSwapsResourceOperations",
    "irSwapResourceOperations",
    "floatingRateIndicesResourceOperations",
    "floatingRateIndexResourceOperations",
]
__all__.extend([p for p in _patch_all if p not in __all__])
_patch_sdk()
