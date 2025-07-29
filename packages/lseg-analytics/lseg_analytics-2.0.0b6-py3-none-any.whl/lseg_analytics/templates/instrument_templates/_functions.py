import copy
import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from lseg_analytics._client.client import Client
from lseg_analytics.common._resource_base import ResourceBase
from lseg_analytics.exceptions import (
    LibraryException,
    ResourceNotFound,
    check_and_raise,
    check_exception_and_raise,
    check_id,
)
from lseg_analytics_basic_client.models import (
    AdjustableDate,
    AmortizationDefinition,
    AmortizationTypeEnum,
    Amount,
    AsianDefinition,
    AsianOtcOptionTemplate,
    AsianTypeEnum,
    AverageTypeEnum,
    BarrierDefinition,
    BarrierModeEnum,
    BinaryDefinition,
    BinaryTypeEnum,
    BusinessDayAdjustmentDefinition,
    CallPutEnum,
    CapFloorDefinition,
    CapFloorTypeEnum,
    CompoundingModeEnum,
    CouponReferenceDateEnum,
    CrossCurrencySwapTemplateDefinition,
    CurrencyBasisSwapTemplateDefinition,
    Date,
    DatedRate,
    DatedValue,
    DateMovingConvention,
    DayCountBasis,
    DepositDefinition,
    DepositDefinitionTemplate,
    Description,
    DirectionEnum,
    DoubleBarrierOtcOptionTemplate,
    DoubleBinaryOtcOptionTemplate,
    EndOfMonthConvention,
    ExerciseDefinition,
    ExerciseStyleEnum,
    FixedRateDefinition,
    FloatingRateDefinition,
    FraDefinition,
    FraDefinitionTemplate,
    FrequencyEnum,
    FxForwardDefinition,
    FxForwardTemplateDefinition,
    FxRate,
    FxSpotDefinition,
    FxSpotTemplateDefinition,
    IndexCompoundingDefinition,
    IndexObservationMethodEnum,
    InOrOutEnum,
    InstrumentTemplateDefinition,
    InstrumentTemplateInfo,
    InterestRateDefinition,
    InterestRateLegDefinition,
    InterestRateLegTemplateDefinition,
    InterestRateSwapTemplateDefinition,
    IrSwapDefinition,
    Location,
    OffsetDefinition,
    OptionDefinition,
    PartyEnum,
    Payment,
    PaymentTypeEnum,
    PrincipalDefinition,
    Rate,
    ReferenceDate,
    RelativeAdjustableDate,
    ResetDatesDefinition,
    ScheduleDefinition,
    SettlementDefinition,
    SettlementType,
    SingleBarrierOtcOptionTemplate,
    SingleBinaryOtcOptionTemplate,
    SingleInterestRatePaymentDefinition,
    SortingOrderEnum,
    SpreadCompoundingModeEnum,
    StepRateDefinition,
    StubIndexReferences,
    StubRuleEnum,
    TenorBasisSwapTemplateDefinition,
    UnderlyingBond,
    UnderlyingBondFuture,
    UnderlyingCommodity,
    UnderlyingDefinition,
    UnderlyingEquity,
    UnderlyingFx,
    UnderlyingIrs,
    UnitEnum,
)

from ._instrument_template import InstrumentTemplate
from ._logger import logger

__all__ = [
    "AmortizationDefinition",
    "AmortizationTypeEnum",
    "Amount",
    "AsianDefinition",
    "AsianOtcOptionTemplate",
    "AsianTypeEnum",
    "AverageTypeEnum",
    "BarrierDefinition",
    "BarrierModeEnum",
    "BinaryDefinition",
    "BinaryTypeEnum",
    "BusinessDayAdjustmentDefinition",
    "CallPutEnum",
    "CapFloorDefinition",
    "CapFloorTypeEnum",
    "CompoundingModeEnum",
    "CouponReferenceDateEnum",
    "CrossCurrencySwapTemplateDefinition",
    "CurrencyBasisSwapTemplateDefinition",
    "DatedRate",
    "DatedValue",
    "DepositDefinition",
    "DepositDefinitionTemplate",
    "DirectionEnum",
    "DoubleBarrierOtcOptionTemplate",
    "DoubleBinaryOtcOptionTemplate",
    "ExerciseDefinition",
    "ExerciseStyleEnum",
    "FixedRateDefinition",
    "FloatingRateDefinition",
    "FraDefinition",
    "FraDefinitionTemplate",
    "FxForwardDefinition",
    "FxForwardTemplateDefinition",
    "FxRate",
    "FxSpotDefinition",
    "FxSpotTemplateDefinition",
    "InOrOutEnum",
    "IndexCompoundingDefinition",
    "IndexObservationMethodEnum",
    "InstrumentTemplateDefinition",
    "InstrumentTemplateInfo",
    "InterestRateDefinition",
    "InterestRateLegDefinition",
    "InterestRateLegTemplateDefinition",
    "InterestRateSwapTemplateDefinition",
    "IrSwapDefinition",
    "OffsetDefinition",
    "OptionDefinition",
    "PartyEnum",
    "Payment",
    "PaymentTypeEnum",
    "PrincipalDefinition",
    "Rate",
    "ResetDatesDefinition",
    "ScheduleDefinition",
    "SettlementDefinition",
    "SingleBarrierOtcOptionTemplate",
    "SingleBinaryOtcOptionTemplate",
    "SingleInterestRatePaymentDefinition",
    "SpreadCompoundingModeEnum",
    "StepRateDefinition",
    "StubIndexReferences",
    "TenorBasisSwapTemplateDefinition",
    "UnderlyingBond",
    "UnderlyingBondFuture",
    "UnderlyingCommodity",
    "UnderlyingDefinition",
    "UnderlyingEquity",
    "UnderlyingFx",
    "UnderlyingIrs",
    "UnitEnum",
    "delete",
    "load",
    "search",
]


def load(
    *,
    resource_id: Optional[str] = None,
    name: Optional[str] = None,
    space: Optional[str] = None,
):
    """
    Load a InstrumentTemplate using its name and space

    Parameters
    ----------
    resource_id : str, optional
        The InstrumentTemplate id. Or the combination of the space and name of the resource with a slash, e.g. 'HOME/my_resource'.
        Required if name is not provided.
    name : str, optional
        The InstrumentTemplate name.
        Required if resource_id is not provided. The name parameter must be specified when the object is first created. Thereafter it is optional.
    space : str, optional
        The space where the InstrumentTemplate is stored. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

    Returns
    -------
    InstrumentTemplate
        The InstrumentTemplate instance.

    Examples
    --------


    """
    if not isinstance(resource_id, (str, type(None))):
        raise TypeError(f"Expected resource_id as a string, got {resource_id!r}")
    if resource_id:
        if name or space:
            logger.warn("resource_id argument received, name & space arguments are ignored")
        return _load_by_id(resource_id)
    if not name:
        raise ValueError("Either resource_id or name argument should be provided")
    logger.info(f"Load InstrumentTemplate {name} from space={space!r}")
    spaces = [space] if space else None
    result = search(names=[name], spaces=spaces)
    if not result:
        logger.error(f"InstrumentTemplate {name} not found in space={space!r}")
        raise ResourceNotFound(f"Resource InstrumentTemplate not found by identifier name={name} space={space}")
    elif not isinstance(result, list):
        raise LibraryException(f"Expected list of results, got {result}")
    elif len(result) > 1:
        logger.warn(f"Found more than one result for name={name!r} and space={space!r}, returning the first one")
    return _load_by_id(result[0].id)


def delete(
    *,
    resource_id: Optional[str] = None,
    name: Optional[str] = None,
    space: Optional[str] = None,
):
    """
    Delete InstrumentTemplate instance from the server.

    Parameters
    ----------
    resource_id : str, optional
        The InstrumentTemplate resource ID.
        Required if name is not provided.
    name : str, optional
        The InstrumentTemplate name.
        Required if resource_id is not provided.
    space : str, optional
        The space where the InstrumentTemplate is stored. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

    Returns
    -------
    ServiceErrorResponse, optional
        Error response, if applicable, otherwise None

    Examples
    --------


    """
    if not isinstance(resource_id, (str, type(None))):
        raise TypeError(f"Expected resource_id as a string, got {resource_id!r}")
    if resource_id:
        if name or space:
            logger.warn("resource_id argument received, name & space arguments are ignored")
        return _delete_by_id(resource_id)
    if not name:
        raise ValueError("Either resource_id or name argument should be provided")
    logger.info(f"Delete InstrumentTemplate {name} from space={space!r}")
    spaces = [space] if space else None
    result = search(names=[name], spaces=spaces)
    if not result:
        logger.error(f"InstrumentTemplate {name} not found in space={space!r}")
        raise ResourceNotFound(f"Resource InstrumentTemplate not found by identifier name={name} space={space}")
    elif not isinstance(result, list):
        raise LibraryException(f"Expected list of results, got {result}")
    return _delete_by_id(result[0].id)


def _delete_by_id(template_id: str) -> bool:
    """
    Delete a InstrumentTemplate that exists in the platform.

    Parameters
    ----------
    template_id : str
        A sequence of textual characters.

    Returns
    --------
    bool


    Examples
    --------


    """

    try:
        logger.info(f"Deleting InstrumentTemplate with id: {template_id}")
        check_and_raise(Client().instrument_template_resource.delete(template_id=template_id))
        logger.info(f"Deleted InstrumentTemplate with id: {template_id}")

        return True
    except Exception as err:
        logger.error(f"Error deleting InstrumentTemplate with id: {template_id}")
        check_exception_and_raise(err)


def _load_by_id(template_id: str, fields: Optional[str] = None) -> InstrumentTemplate:
    """
    Access a InstrumentTemplate existing in the platform (read).

    Parameters
    ----------
    template_id : str
        A sequence of textual characters.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    InstrumentTemplate


    Examples
    --------


    """

    try:
        logger.info(f"Opening InstrumentTemplate with id: {template_id}")

        response = check_and_raise(Client().instrument_template_resource.read(template_id=template_id, fields=fields))

        output = InstrumentTemplate(response.data.definition, response.data.description)

        output._id = response.data.id

        output._location = response.data.location

        return output
    except Exception as err:
        logger.error(f"Error opening InstrumentTemplate: {err}")
        check_exception_and_raise(err)


def search(
    *,
    item_per_page: Optional[int] = None,
    page: Optional[int] = None,
    spaces: Optional[List[str]] = None,
    names: Optional[List[str]] = None,
    space_name_sort_order: Optional[Union[str, SortingOrderEnum]] = None,
    tags: Optional[List[str]] = None,
    fields: Optional[str] = None,
) -> List[InstrumentTemplateInfo]:
    """
    List the InstrumentTemplates existing in the platform (depending on permissions)

    Parameters
    ----------
    item_per_page : int, optional
        A parameter used to select the number of items allowed per page. The valid range is 1-500. If not provided, 50 will be used.
    page : int, optional
        A parameter used to define the page number to display.
    spaces : List[str], optional
        A parameter used to search for platform resources stored in a given space. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space.
        If space is not specified, it will search within all spaces.
    names : List[str], optional
        A parameter used to search for platform resources with given names.
    space_name_sort_order : Union[str, SortingOrderEnum], optional
        A parameter used to sort platform resources by name based on a defined order.
    tags : List[str], optional
        A parameter used to search for platform resources with given tags.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    List[InstrumentTemplateInfo]
        A model template defining the partial description of the resource returned by the GET list service.

    Examples
    --------


    """

    try:
        logger.info("Calling search")

        response = check_and_raise(
            Client().instrument_templates_resource.list(
                item_per_page=item_per_page,
                page=page,
                spaces=spaces,
                names=names,
                space_name_sort_order=space_name_sort_order,
                tags=tags,
                fields=fields,
            )
        )

        output = response.data
        logger.info("Called search")

        return output
    except Exception as err:
        logger.error(f"Error search. {err}")
        check_exception_and_raise(err)
