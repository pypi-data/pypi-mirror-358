# coding=utf-8
# pylint: disable=too-many-lines


import datetime
import decimal
import sys
from abc import ABC
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Literal,
    Mapping,
    Optional,
    Union,
    overload,
)

from .. import _model_base
from .._model_base import rest_discriminator, rest_field
from ._enums import (
    CurveTypeEnum,
    DateType,
    DurationType,
    FxConstituentEnum,
    InstrumentTemplateTypeEnum,
    InterestRateTypeEnum,
    PositionType,
    RescheduleType,
    ResourceType,
    UnderlyingTypeEnum,
)

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import (
        MutableMapping,  # type: ignore  # pylint: disable=ungrouped-imports
    )

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from .. import models as _models
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object


class When(ABC, _model_base.Model):
    """An object to determine regular annual holiday rules for the calendar.

    You probably want to use the sub-classes and not this class directly. Known sub-classes are:
    AbsolutePositionWhen, RelativePositionWhen, RelativeToRulePositionWhen


    :ivar position_type: The type of regular annual holiday rule. Possible values are:
     AbsolutePositionWhen (for fixed holidays), RelativePositionWhen (for holidays that fall on a
     particular day of the week) or RelativeToRulePositionWhen (for holidays that are set by
     reference to another date). Required. Known values are: "AbsolutePositionWhen",
     "RelativePositionWhen", and "RelativeToRulePositionWhen".
    :vartype position_type: str or ~analyticsapi.models.PositionType
    """

    __mapping__: Dict[str, _model_base.Model] = {}
    position_type: str = rest_discriminator(name="positionType")
    """The type of regular annual holiday rule. Possible values are: AbsolutePositionWhen (for fixed
     holidays), RelativePositionWhen (for holidays that fall on a particular day of the week) or
     RelativeToRulePositionWhen (for holidays that are set by reference to another date). Required.
     Known values are: \"AbsolutePositionWhen\", \"RelativePositionWhen\", and
     \"RelativeToRulePositionWhen\"."""

    @overload
    def __init__(
        self,
        position_type: str,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["position_type"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class AbsolutePositionWhen(When, discriminator="AbsolutePositionWhen"):
    """An absolute position annual holiday rule. For example, New Year holiday on 1st Jan.

    Attributes
    ----------
    position_type : str or ~analyticsapi.models.ABSOLUTE_POSITION_WHEN
        The type of regular annual holiday rule. Only AbsolutePositionWhen
        value applies. Required. A rule to determine a fixed holiday. For
        example, New Year holiday on January 1.
    day_of_month : int
        The number of the day of the month. The minimum value is 0 (a special
        case indication western Easter). The maximum value is 31. Required.
    month : str or ~analyticsapi.models.Month
        The month of the year, written in full (e.g. January). Required. Known
        values are: "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", and "December".
    observance : list[~analyticsapi.models.Observance]
        An array of objects to determine a holiday rescheduling if it falls on
        a rest day. This property is optional and only applied if explicitly
        specified. If not provided, a holidays will not be rescheduled by
        default.  The default value is None, needs to be assigned before using.
    """

    position_type: Literal[PositionType.ABSOLUTE_POSITION_WHEN] = rest_discriminator(name="positionType")  # type: ignore
    """The type of regular annual holiday rule. Only AbsolutePositionWhen value applies. Required. A
     rule to determine a fixed holiday. For example, New Year holiday on January 1."""
    day_of_month: int = rest_field(name="dayOfMonth")
    """The number of the day of the month. The minimum value is 0 (a special case indication western
     Easter). The maximum value is 31. Required."""
    month: Union[str, "_models.Month"] = rest_field()
    """The month of the year, written in full (e.g. January). Required. Known values are: \"January\",
     \"February\", \"March\", \"April\", \"May\", \"June\", \"July\", \"August\", \"September\",
     \"October\", \"November\", and \"December\"."""
    observance: Optional[List["_models.Observance"]] = rest_field()
    """An array of objects to determine a holiday rescheduling if it falls on a rest day. This
     property is optional and only applied if explicitly specified. If not provided, a holidays will
     not be rescheduled by default."""

    @overload
    def __init__(
        self,
        *,
        day_of_month: int,
        month: Union[str, "_models.Month"],
        observance: Optional[List["_models.Observance"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, position_type=PositionType.ABSOLUTE_POSITION_WHEN, **kwargs)


class Date(ABC, _model_base.Model):
    """Date.

    You probably want to use the sub-classes and not this class directly. Known sub-classes are:
    AdjustableDate, RelativeAdjustableDate

    Attributes
    ----------
    date_type : str or ~analyticsapi.models.DateType
        Required. Known values are: "AdjustableDate" and
        "RelativeAdjustableDate".
    date_moving_convention : str or ~analyticsapi.models.DateMovingConvention
        The method to adjust dates to working days. The possible values are:
        ModifiedFollowing: dates are adjusted to the next business day
        convention unless it goes into the next month. In such case, the
        previous business day convention is used, NextBusinessDay: dates are
        moved to the following working day, PreviousBusinessDay: dates are
        moved to the preceding working day, NoMoving: dates are not adjusted,
        EveryThirdWednesday: dates are moved to the third Wednesday of the
        month, or to the next working day if the third Wednesday is not a
        working day, BbswModifiedFollowing: dates are adjusted to the next
        business day convention unless it goes into the next month, or crosses
        mid-month (15th). In such case, the previous business day convention is
        used. Default is ModifiedFollowing. Known values are:
        "ModifiedFollowing", "NextBusinessDay", "PreviousBusinessDay",
        "NoMoving", "EveryThirdWednesday", and "BbswModifiedFollowing".
    calendars : list[str]
        An array of calendars that should be used for the date adjustment.
        Typically the calendars are derived based on the instruments currency
        or crossCurrency code.  The default value is None, needs to be assigned
        before using.
    """

    __mapping__: Dict[str, _model_base.Model] = {}
    date_type: str = rest_discriminator(name="dateType")
    """Required. Known values are: \"AdjustableDate\" and \"RelativeAdjustableDate\"."""
    date_moving_convention: Optional[Union[str, "_models.DateMovingConvention"]] = rest_field(
        name="dateMovingConvention"
    )
    """The method to adjust dates to working days. The possible values are:
     ModifiedFollowing: dates are adjusted to the next business day convention unless it goes into
     the next month. In such case, the previous business day convention is used,
     NextBusinessDay: dates are moved to the following working day,
     PreviousBusinessDay: dates are moved to the preceding working day, NoMoving: dates are not
     adjusted,
     EveryThirdWednesday: dates are moved to the third Wednesday of the month, or to the next
     working day if the third Wednesday is not a working day,
     BbswModifiedFollowing: dates are adjusted to the next business day convention unless it goes
     into the next month, or crosses mid-month (15th). In such case, the previous business day
     convention is used.
     Default is ModifiedFollowing. Known values are: \"ModifiedFollowing\", \"NextBusinessDay\",
     \"PreviousBusinessDay\", \"NoMoving\", \"EveryThirdWednesday\", and \"BbswModifiedFollowing\"."""
    calendars: Optional[List[str]] = rest_field()
    """An array of calendars that should be used for the date adjustment. Typically the calendars are
     derived based on the instruments currency or crossCurrency code."""

    @overload
    def __init__(
        self,
        *,
        date_type: str,
        date_moving_convention: Optional[Union[str, "_models.DateMovingConvention"]] = None,
        calendars: Optional[List[str]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class AdjustableDate(Date, discriminator="AdjustableDate"):
    """AdjustableDate.

    Attributes
    ----------
    date_moving_convention : str or ~analyticsapi.models.DateMovingConvention
        The method to adjust dates to working days. The possible values are:
        ModifiedFollowing: dates are adjusted to the next business day
        convention unless it goes into the next month. In such case, the
        previous business day convention is used, NextBusinessDay: dates are
        moved to the following working day, PreviousBusinessDay: dates are
        moved to the preceding working day, NoMoving: dates are not adjusted,
        EveryThirdWednesday: dates are moved to the third Wednesday of the
        month, or to the next working day if the third Wednesday is not a
        working day, BbswModifiedFollowing: dates are adjusted to the next
        business day convention unless it goes into the next month, or crosses
        mid-month (15th). In such case, the previous business day convention is
        used. Default is ModifiedFollowing. Known values are:
        "ModifiedFollowing", "NextBusinessDay", "PreviousBusinessDay",
        "NoMoving", "EveryThirdWednesday", and "BbswModifiedFollowing".
    calendars : list[str]
        An array of calendars that should be used for the date adjustment.
        Typically the calendars are derived based on the instruments currency
        or crossCurrency code.  The default value is None, needs to be assigned
        before using.
    date_type : str or ~analyticsapi.models.ADJUSTABLE_DATE
        The type of the Date input. Possible values are: AdjustableDate,
        RelativeAdjustableDate. Required. The date is defined as adjustable
        according the BusinessDayAdjustmentDefinition.
    date : ~datetime.date
        The date that will be adjusted based on the dateMovingConvention.The
        value is expressed in ISO 8601 format: YYYY-MM-DD (e.g. 2021-01-01).
        Required.
    """

    date_type: Literal[DateType.ADJUSTABLE_DATE] = rest_discriminator(name="dateType")  # type: ignore
    """The type of the Date input. Possible values are: AdjustableDate, RelativeAdjustableDate.
     Required. The date is defined as adjustable according the BusinessDayAdjustmentDefinition."""
    date: datetime.date = rest_field()
    """The date that will be adjusted based on the dateMovingConvention.The value is expressed in ISO
     8601 format: YYYY-MM-DD (e.g. 2021-01-01). Required."""

    @overload
    def __init__(
        self,
        *,
        date: datetime.date,
        date_moving_convention: Optional[Union[str, "_models.DateMovingConvention"]] = None,
        calendars: Optional[List[str]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, date_type=DateType.ADJUSTABLE_DATE, **kwargs)


class AdjustedDate(_model_base.Model):
    """AdjustedDate.

    Attributes
    ----------
    un_adjusted : ~datetime.date
        The unadjusted date. The value is expressed in ISO 8601 format: YYYY-
        MM-DD (e.g. 2021-01-01). Required.
    adjusted : ~datetime.date
        The date which has been used as a reference date for the provided
        tenor. Possible values are: StartDate, ValuationDate, SpotDate. The
        value is expressed in ISO 8601 format: YYYY-MM-DD (e.g. 2021-01-01).
        Required.
    date_moving_convention : str or ~analyticsapi.models.DateMovingConvention
        The method to adjust dates to working days. The possible values are:
        ModifiedFollowing: dates are adjusted to the next business day
        convention unless it goes into the next month. In such case, the
        previous business day convention is used, NextBusinessDay: dates are
        moved to the following working day, PreviousBusinessDay: dates are
        moved to the preceding working day, NoMoving: dates are not adjusted,
        EveryThirdWednesday: dates are moved to the third Wednesday of the
        month, or to the next working day if the third Wednesday is not a
        working day, BbswModifiedFollowing: dates are adjusted to the next
        business day convention unless it goes into the next month, or crosses
        mid-month (15th). In such case, the previous business day convention is
        used. Default is ModifiedFollowing. Required. Known values are:
        "ModifiedFollowing", "NextBusinessDay", "PreviousBusinessDay",
        "NoMoving", "EveryThirdWednesday", and "BbswModifiedFollowing".
    reference_date : str or ~analyticsapi.models.ReferenceDate
        The date which has been used as a reference date for the provided
        tenor. Possible values are: StartDate, ValuationDate, SpotDate. Known
        values are: "SpotDate", "StartDate", and "ValuationDate".
    date : ~datetime.date
        The date that which has been provided in the request. The value is
        expressed in ISO 8601 format: YYYY-MM-DD (e.g. 2021-01-01).
    tenor : str
        A tenor (relative date) expressed as a code indicating the period
        between referenceDate(default=startDate) to endDate of the instrument
        (e.g., '6M', '1Y').
    processing_information : str
        The error message for the calculation in case of a non-blocking error.
    """

    un_adjusted: datetime.date = rest_field(name="unAdjusted")
    """The unadjusted date. The value is expressed in ISO 8601 format: YYYY-MM-DD (e.g. 2021-01-01).
     Required."""
    adjusted: datetime.date = rest_field()
    """The date which has been used as a reference date for the provided tenor. Possible values are:
     StartDate, ValuationDate, SpotDate. The value is expressed in ISO 8601 format: YYYY-MM-DD (e.g.
     2021-01-01). Required."""
    date_moving_convention: Union[str, "_models.DateMovingConvention"] = rest_field(name="dateMovingConvention")
    """The method to adjust dates to working days. The possible values are:
     ModifiedFollowing: dates are adjusted to the next business day convention unless it goes into
     the next month. In such case, the previous business day convention is used,
     NextBusinessDay: dates are moved to the following working day,
     PreviousBusinessDay: dates are moved to the preceding working day, NoMoving: dates are not
     adjusted,
     EveryThirdWednesday: dates are moved to the third Wednesday of the month, or to the next
     working day if the third Wednesday is not a working day,
     BbswModifiedFollowing: dates are adjusted to the next business day convention unless it goes
     into the next month, or crosses mid-month (15th). In such case, the previous business day
     convention is used.
     Default is ModifiedFollowing. Required. Known values are: \"ModifiedFollowing\",
     \"NextBusinessDay\", \"PreviousBusinessDay\", \"NoMoving\", \"EveryThirdWednesday\", and
     \"BbswModifiedFollowing\"."""
    reference_date: Optional[Union[str, "_models.ReferenceDate"]] = rest_field(name="referenceDate")
    """The date which has been used as a reference date for the provided tenor. Possible values are:
     StartDate, ValuationDate, SpotDate. Known values are: \"SpotDate\", \"StartDate\", and
     \"ValuationDate\"."""
    date: Optional[datetime.date] = rest_field()
    """The date that which has been provided in the request. The value is expressed in ISO 8601
     format: YYYY-MM-DD (e.g. 2021-01-01)."""
    tenor: Optional[str] = rest_field()
    """A tenor (relative date) expressed as a code indicating the period between
     referenceDate(default=startDate) to endDate of the instrument (e.g., '6M', '1Y')."""
    processing_information: Optional[str] = rest_field(name="processingInformation")
    """The error message for the calculation in case of a non-blocking error."""

    @overload
    def __init__(
        self,
        *,
        un_adjusted: datetime.date,
        adjusted: datetime.date,
        date_moving_convention: Union[str, "_models.DateMovingConvention"],
        reference_date: Optional[Union[str, "_models.ReferenceDate"]] = None,
        date: Optional[datetime.date] = None,
        tenor: Optional[str] = None,
        processing_information: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class AmortizationDefinition(_model_base.Model):
    """An object that defines the amortization schedule.

    Attributes
    ----------
    schedule_definition : ~analyticsapi.models.ScheduleDefinition
        An object that defines a schedule of amortization dates. Required.
    reference_amount : float
        The amortization amount for each schedule date.
    residual_amount : float
        The final payment of principal to ensure that the initial amount is
        fully repaid by the end date of the instruments leg.
    type : str or ~analyticsapi.models.AmortizationTypeEnum
        The type of amortization. Required. Known values are: "Linear" and
        "Annuity".
    """

    schedule_definition: "_models.ScheduleDefinition" = rest_field(name="scheduleDefinition")
    """An object that defines a schedule of amortization dates. Required."""
    reference_amount: Optional[float] = rest_field(name="referenceAmount")
    """The amortization amount for each schedule date."""
    residual_amount: Optional[float] = rest_field(name="residualAmount")
    """The final payment of principal to ensure that the initial amount is fully repaid by the end
     date of the instruments leg."""
    type: Union[str, "_models.AmortizationTypeEnum"] = rest_field(default="None")
    """The type of amortization. Required. Known values are: \"Linear\" and \"Annuity\"."""

    @overload
    def __init__(
        self,
        *,
        schedule_definition: "_models.ScheduleDefinition",
        type: Union[str, "_models.AmortizationTypeEnum"],
        reference_amount: Optional[float] = None,
        residual_amount: Optional[float] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class Amount(_model_base.Model):
    """An object that specifies the amount and the currency in which it is expressed.

    Attributes
    ----------
    value : float
        The amount. Required.
    currency : str
        The currency in which the amount is expressed. The value is expressed
        in ISO 4217 alphabetical format (e.g., 'USD'). Required.
    """

    value: float = rest_field()
    """The amount. Required."""
    currency: str = rest_field()
    """The currency in which the amount is expressed. The value is expressed in ISO 4217 alphabetical
     format (e.g., 'USD'). Required."""

    @overload
    def __init__(
        self,
        *,
        value: float,
        currency: str,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ApimCurveShift(_model_base.Model):
    """ApimCurveShift.

    Attributes
    ----------
    year : ~decimal.Decimal
        Curve tenor to be shifted. If only one tenor is specified, the entire
        curve will be shifted by this amount (i.e. parallel shift).
    value : ~decimal.Decimal
        Shift amount, in basis points.
    """

    year: Optional[decimal.Decimal] = rest_field()
    """Curve tenor to be shifted. If only one tenor is specified, the entire curve will be shifted by
     this amount (i.e. parallel shift)."""
    value: Optional[decimal.Decimal] = rest_field()
    """Shift amount, in basis points."""

    @overload
    def __init__(
        self,
        *,
        year: Optional[decimal.Decimal] = None,
        value: Optional[decimal.Decimal] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ApimError(_model_base.Model):
    """ApimError.

    Attributes
    ----------
    code : str
    description : str
    resolution : str
    location : str
    error : str
    path : str
    """

    code: Optional[str] = rest_field()
    description: Optional[str] = rest_field()
    resolution: Optional[str] = rest_field()
    location: Optional[str] = rest_field()
    error: Optional[str] = rest_field()
    path: Optional[str] = rest_field()

    @overload
    def __init__(
        self,
        *,
        code: Optional[str] = None,
        description: Optional[str] = None,
        resolution: Optional[str] = None,
        location: Optional[str] = None,
        error: Optional[str] = None,
        path: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class AsianDefinition(_model_base.Model):
    """An object that defines an Asian option in which the final payout is based on the average price
    level of the underlying asset over a certain time period.

    Attributes
    ----------
    asian_type : str or ~analyticsapi.models.AsianTypeEnum
        The type of an Asian option based on whether the strike is fixed or
        not. Known values are: "Price" and "Strike".
    average_type : str or ~analyticsapi.models.AverageTypeEnum
        The mathematical type used to calculate the average price of the
        underlying asset. Known values are: "Arithmetic" and "Geometric".
    fixing_schedule : ~analyticsapi.models.ScheduleDefinition
        An object that defines the schedule of dates in the fixing period of an
        Asian option.
    """

    asian_type: Optional[Union[str, "_models.AsianTypeEnum"]] = rest_field(name="asianType")
    """The type of an Asian option based on whether the strike is fixed or not. Known values are:
     \"Price\" and \"Strike\"."""
    average_type: Optional[Union[str, "_models.AverageTypeEnum"]] = rest_field(name="averageType")
    """The mathematical type used to calculate the average price of the underlying asset. Known values
     are: \"Arithmetic\" and \"Geometric\"."""
    fixing_schedule: Optional["_models.ScheduleDefinition"] = rest_field(name="fixingSchedule")
    """An object that defines the schedule of dates in the fixing period of an Asian option."""

    @overload
    def __init__(
        self,
        *,
        asian_type: Optional[Union[str, "_models.AsianTypeEnum"]] = None,
        average_type: Optional[Union[str, "_models.AverageTypeEnum"]] = None,
        fixing_schedule: Optional["_models.ScheduleDefinition"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class InstrumentTemplateDefinition(ABC, _model_base.Model):
    """InstrumentTemplateDefinition.

    You probably want to use the sub-classes and not this class directly. Known sub-classes are:
    AsianOtcOptionTemplate, CrossCurrencySwapTemplateDefinition,
    CurrencyBasisSwapTemplateDefinition, DepositDefinitionTemplate, DoubleBarrierOtcOptionTemplate,
    DoubleBinaryOtcOptionTemplate, FraDefinitionTemplate, FxForwardTemplateDefinition,
    FxSpotTemplateDefinition, InterestRateLegTemplateDefinition, SingleBarrierOtcOptionTemplate,
    SingleBinaryOtcOptionTemplate, TenorBasisSwapTemplateDefinition,
    InterestRateSwapTemplateDefinition

    Attributes
    ----------
    instrument_type : str or ~analyticsapi.models.InstrumentTemplateTypeEnum
        Required. Known values are: "InterestRateLeg", "VanillaSwap",
        "TenorBasisSwap", "CrossCurrencySwap", "CurrencyBasisSwap", "FxSpot",
        "FxForward", "FxSwap", "NonDeliverableForward", "Deposit",
        "ForwardRateAgreement", "MoneyMarketFuture", "VanillaOtcOption",
        "AsianOtcOption", "SingleBarrierOtcOption", "DoubleBarrierOtcOption",
        "SingleBinaryOtcOption", and "DoubleBinaryOtcOption".
    """

    __mapping__: Dict[str, _model_base.Model] = {}
    instrument_type: str = rest_discriminator(name="instrumentType")
    """Required. Known values are: \"InterestRateLeg\", \"VanillaSwap\", \"TenorBasisSwap\",
     \"CrossCurrencySwap\", \"CurrencyBasisSwap\", \"FxSpot\", \"FxForward\", \"FxSwap\",
     \"NonDeliverableForward\", \"Deposit\", \"ForwardRateAgreement\", \"MoneyMarketFuture\",
     \"VanillaOtcOption\", \"AsianOtcOption\", \"SingleBarrierOtcOption\",
     \"DoubleBarrierOtcOption\", \"SingleBinaryOtcOption\", and \"DoubleBinaryOtcOption\"."""

    @overload
    def __init__(
        self,
        instrument_type: str,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["instrument_type"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class AsianOtcOptionTemplate(InstrumentTemplateDefinition, discriminator="AsianOtcOption"):
    """AsianOtcOptionTemplate.

    Attributes
    ----------
    instrument_type : str or ~analyticsapi.models.ASIAN_OTC_OPTION
        Required. Asian OTC Option contract.
    template : ~analyticsapi.models.OptionDefinition
        Required.
    """

    instrument_type: Literal[InstrumentTemplateTypeEnum.ASIAN_OTC_OPTION] = rest_discriminator(name="instrumentType")  # type: ignore
    """Required. Asian OTC Option contract."""
    template: "_models.OptionDefinition" = rest_field()
    """Required."""

    @overload
    def __init__(
        self,
        template: "_models.OptionDefinition",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, instrument_type=InstrumentTemplateTypeEnum.ASIAN_OTC_OPTION, **kwargs)


class Balloon(_model_base.Model):
    """Balloon.

    Attributes
    ----------
    percent : float
        Percentage expected to default.
    loss_severity : float
        Severity of the defaults.
    recovery_period : int
        Time after maturity in which the holder gets recovered principal.
    loss_type : str
        Loss type setting. Is either a Literal["PLD"] type or a Literal["CDR"]
        type.
    loss_rate : float
        Loss rate. Either rate or vector is required.
    month_to_extend : int
        Number of months cash flows extend beyond final date. 0 indicates no
        extension.
    loss_vector : ~analyticsapi.models.Vector
    """

    percent: Optional[float] = rest_field()
    """Percentage expected to default."""
    loss_severity: Optional[float] = rest_field(name="lossSeverity")
    """Severity of the defaults."""
    recovery_period: Optional[int] = rest_field(name="recoveryPeriod")
    """Time after maturity in which the holder gets recovered principal."""
    loss_type: Optional[Literal["PLD", "CDR"]] = rest_field(name="lossType")
    """Loss type setting. Is either a Literal[\"PLD\"] type or a Literal[\"CDR\"] type."""
    loss_rate: Optional[float] = rest_field(name="lossRate")
    """Loss rate. Either rate or vector is required."""
    month_to_extend: Optional[int] = rest_field(name="monthToExtend")
    """Number of months cash flows extend beyond final date. 0 indicates no extension."""
    loss_vector: Optional["_models.Vector"] = rest_field(name="lossVector")

    @overload
    def __init__(
        self,
        *,
        percent: Optional[float] = None,
        loss_severity: Optional[float] = None,
        recovery_period: Optional[int] = None,
        loss_type: Optional[Literal["PLD", "CDR"]] = None,
        loss_rate: Optional[float] = None,
        month_to_extend: Optional[int] = None,
        loss_vector: Optional["_models.Vector"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class BarrierDefinition(_model_base.Model):
    """An object that defines a barrier option which is activated or deactivated once the price of the
    underlying asset reaches a set level, known as the barrier at a specified time.

    Attributes
    ----------
    barrier_mode : str or ~analyticsapi.models.BarrierModeEnum
        The barrier mode that defines the timing and conditions under which the
        barrier level is monitored and can trigger activation. Known values
        are: "American", "European", and "Bermudan".
    in_or_out : str or ~analyticsapi.models.InOrOutEnum
        The type of a barrier option based on whether it is activated or
        deactivated when the price of the underlying asset reaches a certain
        barrier. Known values are: "In" and "Out".
    schedule : ~analyticsapi.models.ScheduleDefinition
        An object that defines the barrier schedule of a barrier option.
    level : float
        The price used as a barrier level.
    rebate_amount : ~analyticsapi.models.Amount
        The rebate provided to investors when a barrier option is not able to
        be exercised and becomes worthless. The amount is provided in the
        domestic currency.
    """

    barrier_mode: Optional[Union[str, "_models.BarrierModeEnum"]] = rest_field(name="barrierMode")
    """The barrier mode that defines the timing and conditions under which the barrier level is
     monitored and can trigger activation. Known values are: \"American\", \"European\", and
     \"Bermudan\"."""
    in_or_out: Optional[Union[str, "_models.InOrOutEnum"]] = rest_field(name="inOrOut")
    """The type of a barrier option based on whether it is activated or deactivated when the price of
     the underlying asset reaches a certain barrier. Known values are: \"In\" and \"Out\"."""
    schedule: Optional["_models.ScheduleDefinition"] = rest_field()
    """An object that defines the barrier schedule of a barrier option."""
    level: Optional[float] = rest_field()
    """The price used as a barrier level."""
    rebate_amount: Optional["_models.Amount"] = rest_field(name="rebateAmount")
    """The rebate provided to investors when a barrier option is not able to be exercised and becomes
     worthless. The amount is provided in the domestic currency."""

    @overload
    def __init__(
        self,
        *,
        barrier_mode: Optional[Union[str, "_models.BarrierModeEnum"]] = None,
        in_or_out: Optional[Union[str, "_models.InOrOutEnum"]] = None,
        schedule: Optional["_models.ScheduleDefinition"] = None,
        level: Optional[float] = None,
        rebate_amount: Optional["_models.Amount"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class BasePricingParameters(_model_base.Model):
    """An object that describes cross-asset calculation parameters.

    Attributes
    ----------
    valuation_date : ~datetime.date
        The date at which the instrument is valued. The value is expressed in
        ISO 8601 format: YYYY-MM-DD (e.g., '2021-01-01').
    report_currency : str
        The reporting currency. The value is expressed in ISO 4217 alphabetical
        format (e.g., 'GBP'). Default is USD.
    """

    valuation_date: Optional[datetime.date] = rest_field(name="valuationDate")
    """The date at which the instrument is valued. The value is expressed in ISO 8601 format:
     YYYY-MM-DD (e.g., '2021-01-01')."""
    report_currency: Optional[str] = rest_field(name="reportCurrency")
    """The reporting currency. The value is expressed in ISO 4217 alphabetical format (e.g., 'GBP').
     Default is USD."""

    @overload
    def __init__(
        self,
        *,
        valuation_date: Optional[datetime.date] = None,
        report_currency: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class BidAskMidSimpleValues(_model_base.Model):
    """An object that contains the bid, ask and mid quotes for the instrument.

    Attributes
    ----------
    bid : float
        The bid value.
    ask : float
        The ask value.
    mid : float
        The mid value.
    """

    bid: Optional[float] = rest_field()
    """The bid value."""
    ask: Optional[float] = rest_field()
    """The ask value."""
    mid: Optional[float] = rest_field()
    """The mid value."""

    @overload
    def __init__(
        self,
        *,
        bid: Optional[float] = None,
        ask: Optional[float] = None,
        mid: Optional[float] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class BidAskSimpleValues(_model_base.Model):
    """An object that contains the bid, ask quotes for the instrument.

    Attributes
    ----------
    bid : float
        The bid quote.
    ask : float
        The ask quote.
    """

    bid: Optional[float] = rest_field()
    """The bid quote."""
    ask: Optional[float] = rest_field()
    """The ask quote."""

    @overload
    def __init__(
        self,
        *,
        bid: Optional[float] = None,
        ask: Optional[float] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class BinaryDefinition(_model_base.Model):
    """An object that defines a binary option that pays an agreed amount if expires in-the-money.

    Attributes
    ----------
    binary_type : str or ~analyticsapi.models.BinaryTypeEnum
        The type of a binary option based on the trigger that activates it.
        Known values are: "OneTouch", "NoTouch", and "Digital".
    level : float
        The price used as a binary option level.
    payout_amount : ~analyticsapi.models.Amount
        The payout amount of a binary option.
    payment_type : str or ~analyticsapi.models.PaymentTypeEnum
        The type of a binary option based on when it is paid out. Known values
        are: "Immediate" and "Deferred".
    """

    binary_type: Optional[Union[str, "_models.BinaryTypeEnum"]] = rest_field(name="binaryType")
    """The type of a binary option based on the trigger that activates it. Known values are:
     \"OneTouch\", \"NoTouch\", and \"Digital\"."""
    level: Optional[float] = rest_field()
    """The price used as a binary option level."""
    payout_amount: Optional["_models.Amount"] = rest_field(name="payoutAmount")
    """The payout amount of a binary option."""
    payment_type: Optional[Union[str, "_models.PaymentTypeEnum"]] = rest_field(name="paymentType")
    """The type of a binary option based on when it is paid out. Known values are: \"Immediate\" and
     \"Deferred\"."""

    @overload
    def __init__(
        self,
        *,
        binary_type: Optional[Union[str, "_models.BinaryTypeEnum"]] = None,
        level: Optional[float] = None,
        payout_amount: Optional["_models.Amount"] = None,
        payment_type: Optional[Union[str, "_models.PaymentTypeEnum"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class BondIndicRequest(_model_base.Model):
    """BondIndicRequest.

    Attributes
    ----------
    input : list[~analyticsapi.models.IdentifierInfo]
        Single identifier or a list of identifiers to search instruments by.
        The default value is None, needs to be assigned before using.
    keywords : list[str]
        List of keywords from the MappedResponseRefData to be exposed in the
        result data set.  The default value is None, needs to be assigned
        before using.
    """

    input: Optional[List["_models.IdentifierInfo"]] = rest_field()
    """Single identifier or a list of identifiers to search instruments by."""
    keywords: Optional[List[str]] = rest_field()
    """List of keywords from the MappedResponseRefData to be exposed in the result data set."""

    @overload
    def __init__(
        self,
        *,
        input: Optional[List["_models.IdentifierInfo"]] = None,
        keywords: Optional[List[str]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class BuildResponse(_model_base.Model):
    """A model describing a single build response.

    Attributes
    ----------
    data : ~analyticsapi.models.FxForwardCurveDefinition
        Required.
    meta : ~analyticsapi.models.MetaData
    """

    data: "_models.FxForwardCurveDefinition" = rest_field()
    """Required."""
    meta: Optional["_models.MetaData"] = rest_field()

    @overload
    def __init__(
        self,
        *,
        data: "_models.FxForwardCurveDefinition",
        meta: Optional["_models.MetaData"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class BulkCompact(_model_base.Model):
    """BulkCompact.

    Attributes
    ----------
    path : str
        URL to which each individual request should be posted.i.e "/bond/py"
        for PY calculation.
    name_expr : str
        Name of each request. This can be a valid JSON path expression, i.e
        "concat($.CUSIP,"_PY")" will give each request the name CUSIP_PY. Name
        should be unique within a single job.
    body : str
        POST body associated with the calculation. This is specific to each
        request type. Refer to individual calculation section for more details.
    requests : list[dict[str, any]]
        List of key value pairs. This values provided will be used to update
        corresponding variables in the body of the request.  The default value
        is None, needs to be assigned before using.
    data_source : ~analyticsapi.models.BulkTemplateDataSource
    params : dict[str, any]
    """

    path: Optional[str] = rest_field()
    """URL to which each individual request should be posted.i.e \"/bond/py\" for PY calculation."""
    name_expr: Optional[str] = rest_field(name="nameExpr")
    """Name of each request. This can be a valid JSON path expression, i.e \"concat($.CUSIP,\"_PY\")\"
     will give each request the name CUSIP_PY. Name should be unique within a single job."""
    body: Optional[str] = rest_field()
    """POST body associated with the calculation. This is specific to each request type. Refer to
     individual calculation section for more details."""
    requests: Optional[List[Dict[str, Any]]] = rest_field()
    """List of key value pairs. This values provided will be used to update corresponding variables in
     the body of the request."""
    data_source: Optional["_models.BulkTemplateDataSource"] = rest_field(name="dataSource")
    params: Optional[Dict[str, Any]] = rest_field()

    @overload
    def __init__(
        self,
        *,
        path: Optional[str] = None,
        name_expr: Optional[str] = None,
        body: Optional[str] = None,
        requests: Optional[List[Dict[str, Any]]] = None,
        data_source: Optional["_models.BulkTemplateDataSource"] = None,
        params: Optional[Dict[str, Any]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class BulkComposite(_model_base.Model):
    """BulkComposite.

    Attributes
    ----------
    requests : list[~analyticsapi.models.BulkJsonInputItem]
        The default value is None, needs to be assigned before using.
    """

    requests: Optional[List["_models.BulkJsonInputItem"]] = rest_field()

    @overload
    def __init__(
        self,
        requests: Optional[List["_models.BulkJsonInputItem"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["requests"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class BulkDefaultSettings(_model_base.Model):  # pylint: disable=too-many-instance-attributes
    """BulkDefaultSettings.

    Attributes
    ----------
    header : bool
    separator : str
    null_value : str
    error_value : str
    number_format : str
    date_format : str
    bool_true : str
    bool_false : str
    quote_char : str
    escape_char : str
    cond_quote : bool
    footer : str
    relaxed : bool
    num_prec : int
    num_scale : int
    str_width : int
    charset : str
    precision : int
    scale : int
    bom : bool
    """

    header: Optional[bool] = rest_field()
    separator: Optional[str] = rest_field()
    null_value: Optional[str] = rest_field(name="nullValue")
    error_value: Optional[str] = rest_field(name="errorValue")
    number_format: Optional[str] = rest_field(name="numberFormat")
    date_format: Optional[str] = rest_field(name="dateFormat")
    bool_true: Optional[str] = rest_field(name="boolTrue")
    bool_false: Optional[str] = rest_field(name="boolFalse")
    quote_char: Optional[str] = rest_field(name="quoteChar")
    escape_char: Optional[str] = rest_field(name="escapeChar")
    cond_quote: Optional[bool] = rest_field(name="condQuote")
    footer: Optional[str] = rest_field()
    relaxed: Optional[bool] = rest_field()
    num_prec: Optional[int] = rest_field(name="numPrec")
    num_scale: Optional[int] = rest_field(name="numScale")
    str_width: Optional[int] = rest_field(name="strWidth")
    charset: Optional[str] = rest_field()
    precision: Optional[int] = rest_field()
    scale: Optional[int] = rest_field()
    bom: Optional[bool] = rest_field()

    @overload
    def __init__(
        self,
        *,
        header: Optional[bool] = None,
        separator: Optional[str] = None,
        null_value: Optional[str] = None,
        error_value: Optional[str] = None,
        number_format: Optional[str] = None,
        date_format: Optional[str] = None,
        bool_true: Optional[str] = None,
        bool_false: Optional[str] = None,
        quote_char: Optional[str] = None,
        escape_char: Optional[str] = None,
        cond_quote: Optional[bool] = None,
        footer: Optional[str] = None,
        relaxed: Optional[bool] = None,
        num_prec: Optional[int] = None,
        num_scale: Optional[int] = None,
        str_width: Optional[int] = None,
        charset: Optional[str] = None,
        precision: Optional[int] = None,
        scale: Optional[int] = None,
        bom: Optional[bool] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class BulkGlobalSettings(_model_base.Model):
    """BulkGlobalSettings.

    Attributes
    ----------
    sql_settings : ~analyticsapi.models.SqlSettings
    """

    sql_settings: Optional["_models.SqlSettings"] = rest_field(name="sqlSettings")

    @overload
    def __init__(
        self,
        sql_settings: Optional["_models.SqlSettings"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["sql_settings"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class BulkJsonInputItem(_model_base.Model):
    """BulkJsonInputItem.

    Attributes
    ----------
    path : str
    name : str
    priority : int
    dep : str
    visible : str
    parent_req : str
    tags : str
    body : str
    """

    path: Optional[str] = rest_field()
    name: Optional[str] = rest_field()
    priority: Optional[int] = rest_field()
    dep: Optional[str] = rest_field()
    visible: Optional[str] = rest_field()
    parent_req: Optional[str] = rest_field(name="parentReq")
    tags: Optional[str] = rest_field()
    body: Optional[str] = rest_field()

    @overload
    def __init__(
        self,
        *,
        path: Optional[str] = None,
        name: Optional[str] = None,
        priority: Optional[int] = None,
        dep: Optional[str] = None,
        visible: Optional[str] = None,
        parent_req: Optional[str] = None,
        tags: Optional[str] = None,
        body: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class BulkMeta(_model_base.Model):
    """BulkMeta.

    Attributes
    ----------
    request_id : str
    time_stamp : ~datetime.datetime
    status : str
        Is one of the following types: Literal["NEW"], Literal["WAITING"],
        Literal["PENDING"], Literal["RUNNING"], Literal["ABORTING"],
        Literal["DONE"], Literal["ERROR"], Literal["SKIPPED"],
        Literal["ABORTED"]
    correlation_id : str
    response_type : str
        Is one of the following types: Literal["BOND_INDIC"],
        Literal["BOND_SEARCH"], Literal["CURVE_POINTS"],
        Literal["MARKET_SETTINGS"], Literal["MBS_HISTORY"], Literal["PY_CALC"],
        Literal["COLLATERAL_DETAILS"], Literal["CALC_SETTINGS"],
        Literal["MORTGAGE_MODEL"], Literal["ACTUAL_VS_PROJECTED"],
        Literal["WAL_SENSITIVITY"], Literal["SCENARIO_CALC"],
        Literal["MATRIX_PY"], Literal["HISTORICAL_DATA"], Literal["CASHFLOW"],
        Literal["VOLATILITY"], Literal["TEST"], Literal["SCENARIO_SETUPS"],
        Literal["XMLAPI"], Literal["BULK_ZIP"], Literal["BULK_COMPOSITE"],
        Literal["FORWARD_PRICING"], Literal["CALC_STATUS"],
        Literal["DELIMITED"], Literal["COMPACT"], Literal["BULK"],
        Literal["FX_FWDS"], Literal["USER_CURVE"], Literal["WAIT"],
        Literal["RETURNS_CALC"], Literal["TABLE"], Literal["PREPAY_DIALS"],
        Literal["USER_VOL"], Literal["YBPORT_USER_BONDS"], Literal["ESG_PCR"]
    job_id : str
    """

    request_id: Optional[str] = rest_field(name="requestId")
    time_stamp: Optional[datetime.datetime] = rest_field(name="timeStamp", format="rfc3339")
    status: Optional[
        Literal["NEW", "WAITING", "PENDING", "RUNNING", "ABORTING", "DONE", "ERROR", "SKIPPED", "ABORTED"]
    ] = rest_field()
    """Is one of the following types: Literal[\"NEW\"], Literal[\"WAITING\"], Literal[\"PENDING\"],
     Literal[\"RUNNING\"], Literal[\"ABORTING\"], Literal[\"DONE\"], Literal[\"ERROR\"],
     Literal[\"SKIPPED\"], Literal[\"ABORTED\"]"""
    correlation_id: Optional[str] = rest_field(name="correlationId")
    response_type: Optional[
        Literal[
            "BOND_INDIC",
            "BOND_SEARCH",
            "CURVE_POINTS",
            "MARKET_SETTINGS",
            "MBS_HISTORY",
            "PY_CALC",
            "COLLATERAL_DETAILS",
            "CALC_SETTINGS",
            "MORTGAGE_MODEL",
            "ACTUAL_VS_PROJECTED",
            "WAL_SENSITIVITY",
            "SCENARIO_CALC",
            "MATRIX_PY",
            "HISTORICAL_DATA",
            "CASHFLOW",
            "VOLATILITY",
            "TEST",
            "SCENARIO_SETUPS",
            "XMLAPI",
            "BULK_ZIP",
            "BULK_COMPOSITE",
            "FORWARD_PRICING",
            "CALC_STATUS",
            "DELIMITED",
            "COMPACT",
            "BULK",
            "FX_FWDS",
            "USER_CURVE",
            "WAIT",
            "RETURNS_CALC",
            "TABLE",
            "PREPAY_DIALS",
            "USER_VOL",
            "YBPORT_USER_BONDS",
            "ESG_PCR",
        ]
    ] = rest_field(name="responseType")
    """Is one of the following types: Literal[\"BOND_INDIC\"], Literal[\"BOND_SEARCH\"],
     Literal[\"CURVE_POINTS\"], Literal[\"MARKET_SETTINGS\"], Literal[\"MBS_HISTORY\"],
     Literal[\"PY_CALC\"], Literal[\"COLLATERAL_DETAILS\"], Literal[\"CALC_SETTINGS\"],
     Literal[\"MORTGAGE_MODEL\"], Literal[\"ACTUAL_VS_PROJECTED\"], Literal[\"WAL_SENSITIVITY\"],
     Literal[\"SCENARIO_CALC\"], Literal[\"MATRIX_PY\"], Literal[\"HISTORICAL_DATA\"],
     Literal[\"CASHFLOW\"], Literal[\"VOLATILITY\"], Literal[\"TEST\"],
     Literal[\"SCENARIO_SETUPS\"], Literal[\"XMLAPI\"], Literal[\"BULK_ZIP\"],
     Literal[\"BULK_COMPOSITE\"], Literal[\"FORWARD_PRICING\"], Literal[\"CALC_STATUS\"],
     Literal[\"DELIMITED\"], Literal[\"COMPACT\"], Literal[\"BULK\"], Literal[\"FX_FWDS\"],
     Literal[\"USER_CURVE\"], Literal[\"WAIT\"], Literal[\"RETURNS_CALC\"], Literal[\"TABLE\"],
     Literal[\"PREPAY_DIALS\"], Literal[\"USER_VOL\"], Literal[\"YBPORT_USER_BONDS\"],
     Literal[\"ESG_PCR\"]"""
    job_id: Optional[str] = rest_field(name="jobId")

    @overload
    def __init__(
        self,
        *,
        request_id: Optional[str] = None,
        time_stamp: Optional[datetime.datetime] = None,
        status: Optional[
            Literal["NEW", "WAITING", "PENDING", "RUNNING", "ABORTING", "DONE", "ERROR", "SKIPPED", "ABORTED"]
        ] = None,
        correlation_id: Optional[str] = None,
        response_type: Optional[
            Literal[
                "BOND_INDIC",
                "BOND_SEARCH",
                "CURVE_POINTS",
                "MARKET_SETTINGS",
                "MBS_HISTORY",
                "PY_CALC",
                "COLLATERAL_DETAILS",
                "CALC_SETTINGS",
                "MORTGAGE_MODEL",
                "ACTUAL_VS_PROJECTED",
                "WAL_SENSITIVITY",
                "SCENARIO_CALC",
                "MATRIX_PY",
                "HISTORICAL_DATA",
                "CASHFLOW",
                "VOLATILITY",
                "TEST",
                "SCENARIO_SETUPS",
                "XMLAPI",
                "BULK_ZIP",
                "BULK_COMPOSITE",
                "FORWARD_PRICING",
                "CALC_STATUS",
                "DELIMITED",
                "COMPACT",
                "BULK",
                "FX_FWDS",
                "USER_CURVE",
                "WAIT",
                "RETURNS_CALC",
                "TABLE",
                "PREPAY_DIALS",
                "USER_VOL",
                "YBPORT_USER_BONDS",
                "ESG_PCR",
            ]
        ] = None,
        job_id: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class BulkResultItem(_model_base.Model):
    """BulkResultItem.

    Attributes
    ----------
    source : str
    id : str
    status : int
    description : str
    target : str
    priority : int
    """

    source: Optional[str] = rest_field()
    id: Optional[str] = rest_field()
    status: Optional[int] = rest_field()
    description: Optional[str] = rest_field()
    target: Optional[str] = rest_field()
    priority: Optional[int] = rest_field()

    @overload
    def __init__(
        self,
        *,
        source: Optional[str] = None,
        id: Optional[str] = None,  # pylint: disable=redefined-builtin
        status: Optional[int] = None,
        description: Optional[str] = None,
        target: Optional[str] = None,
        priority: Optional[int] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class BulkResultRequest(_model_base.Model):
    """BulkResultRequest.

    Attributes
    ----------
    default_settings : ~analyticsapi.models.BulkDefaultSettings
    global_settings : ~analyticsapi.models.BulkGlobalSettings
    fields : list[~analyticsapi.models.ColumnDetail]
        The default value is None, needs to be assigned before using.
    """

    default_settings: Optional["_models.BulkDefaultSettings"] = rest_field(name="defaultSettings")
    global_settings: Optional["_models.BulkGlobalSettings"] = rest_field(name="globalSettings")
    fields: Optional[List["_models.ColumnDetail"]] = rest_field()

    @overload
    def __init__(
        self,
        *,
        default_settings: Optional["_models.BulkDefaultSettings"] = None,
        global_settings: Optional["_models.BulkGlobalSettings"] = None,
        fields: Optional[List["_models.ColumnDetail"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class BulkTemplateDataSource(_model_base.Model):
    """BulkTemplateDataSource.

    Attributes
    ----------
    request_id : str
        Reference to data source, this can be request id or request name.
    filter : str
        This is condition that can be provided to filter data from the data
        source.
    name_prefix : str
    name_suffix : str
    """

    request_id: Optional[str] = rest_field(name="requestId")
    """Reference to data source, this can be request id or request name."""
    filter: Optional[str] = rest_field()
    """This is condition that can be provided to filter data from the data source."""
    name_prefix: Optional[str] = rest_field(name="namePrefix")
    name_suffix: Optional[str] = rest_field(name="nameSuffix")

    @overload
    def __init__(
        self,
        *,
        request_id: Optional[str] = None,
        filter: Optional[str] = None,  # pylint: disable=redefined-builtin
        name_prefix: Optional[str] = None,
        name_suffix: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class BusinessDayAdjustmentDefinition(_model_base.Model):
    """An object that defines the business day adjustment convention.

    Attributes
    ----------
    calendars : list[str]
        An array of calendar identifiers (GUID or URI) to use for the business
        days adjustment. Typically the calendars are derived based on the
        instrument currency or cross-currency code. Note that a URI must be at
        least 2 and at most 102 characters long, start with an alphanumeric
        character, and contain only alphanumeric characters, slashes and
        underscores. Required.  The default value is None, needs to be assigned
        before using.
    convention : str or ~analyticsapi.models.DateMovingConvention
        The method to adjust a date to working days when it falls on a non-
        business day. Required. Known values are: "ModifiedFollowing",
        "NextBusinessDay", "PreviousBusinessDay", "NoMoving",
        "EveryThirdWednesday", and "BbswModifiedFollowing".
    """

    calendars: List[str] = rest_field()
    """An array of calendar identifiers (GUID or URI) to use for the business days adjustment.
     Typically the calendars are derived based on the instrument currency or cross-currency code.
     Note that a URI must be at least 2 and at most 102 characters long, start with an alphanumeric
     character, and contain only alphanumeric characters, slashes and underscores. Required."""
    convention: Union[str, "_models.DateMovingConvention"] = rest_field()
    """The method to adjust a date to working days when it falls on a non-business day. Required.
     Known values are: \"ModifiedFollowing\", \"NextBusinessDay\", \"PreviousBusinessDay\",
     \"NoMoving\", \"EveryThirdWednesday\", and \"BbswModifiedFollowing\"."""

    @overload
    def __init__(
        self,
        *,
        calendars: List[str],
        convention: Union[str, "_models.DateMovingConvention"],
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class Calendar(_model_base.Model):
    """Calendar resource including calendar definition and description.

    Readonly variables are only populated by the server, and will be ignored when sending a request.

    Attributes
    ----------
    type : str or ~analyticsapi.models.CALENDAR
        Property defining the type of the resource.
    id : str
        Unique identifier of the Calendar.
    location : ~analyticsapi.models.Location
        Object defining the location of the Calendar in the platform. Required.
    description : ~analyticsapi.models.Description
        Calendar description.
    definition : ~analyticsapi.models.CalendarDefinition
        Calendar definition. Required.
    """

    type: Optional[Literal[ResourceType.CALENDAR]] = rest_field(visibility=["read"], default=ResourceType.CALENDAR)
    """Property defining the type of the resource."""
    id: Optional[str] = rest_field(visibility=["read"])
    """Unique identifier of the Calendar."""
    location: "_models.Location" = rest_field(visibility=["read", "create"])
    """Object defining the location of the Calendar in the platform. Required."""
    description: Optional["_models.Description"] = rest_field()
    """Calendar description."""
    definition: "_models.CalendarDefinition" = rest_field()
    """Calendar definition. Required."""

    @overload
    def __init__(
        self,
        *,
        location: "_models.Location",
        definition: "_models.CalendarDefinition",
        description: Optional["_models.Description"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CalendarCollectionLinks(_model_base.Model):
    """Object defining the links available for one or more Calendars.

    Attributes
    ----------
    self_property : ~analyticsapi.models.Link
        Required.
    first : ~analyticsapi.models.Link
    prev : ~analyticsapi.models.Link
    next : ~analyticsapi.models.Link
    last : ~analyticsapi.models.Link
    generate_holidays : ~analyticsapi.models.Link
        Required.
    compute_dates : ~analyticsapi.models.Link
        Required.
    generate_date_schedule : ~analyticsapi.models.Link
        Required.
    """

    self_property: "_models.Link" = rest_field(name="self")
    """Required."""
    first: Optional["_models.Link"] = rest_field()
    prev: Optional["_models.Link"] = rest_field()
    next: Optional["_models.Link"] = rest_field()
    last: Optional["_models.Link"] = rest_field()
    generate_holidays: "_models.Link" = rest_field(name="generateHolidays")
    """Required."""
    compute_dates: "_models.Link" = rest_field(name="computeDates")
    """Required."""
    generate_date_schedule: "_models.Link" = rest_field(name="generateDateSchedule")
    """Required."""

    @overload
    def __init__(
        self,
        *,
        self_property: "_models.Link",
        generate_holidays: "_models.Link",
        compute_dates: "_models.Link",
        generate_date_schedule: "_models.Link",
        first: Optional["_models.Link"] = None,
        prev: Optional["_models.Link"] = None,
        next: Optional["_models.Link"] = None,
        last: Optional["_models.Link"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CalendarCollectionResponse(_model_base.Model):
    """Object defining the paged response for a collection of Calendars.

    Attributes
    ----------
    data : list[~analyticsapi.models.CalendarInfo]
        Required.  The default value is None, needs to be assigned before
        using.
    page : int
        The page number of the current page displayed. Minimum value of this
        property is 1. Required.
    item_per_page : int
        Number of items displayed per page. Required.
    total_pages : int
        Total number of pages available for display. Required.
    total_items : int
        Total number of items available for display. Required.
    links : ~analyticsapi.models.CalendarCollectionLinks
        Links for available operations and/or resources linked to current
        response.
    """

    data: List["_models.CalendarInfo"] = rest_field()
    """Required."""
    page: int = rest_field()
    """The page number of the current page displayed. Minimum value of this property is 1. Required."""
    item_per_page: int = rest_field(name="itemPerPage")
    """Number of items displayed per page. Required."""
    total_pages: int = rest_field(name="totalPages")
    """Total number of pages available for display. Required."""
    total_items: int = rest_field(name="totalItems")
    """Total number of items available for display. Required."""
    links: Optional["_models.CalendarCollectionLinks"] = rest_field()
    """Links for available operations and/or resources linked to current response."""

    @overload
    def __init__(
        self,
        *,
        data: List["_models.CalendarInfo"],
        page: int,
        item_per_page: int,
        total_pages: int,
        total_items: int,
        links: Optional["_models.CalendarCollectionLinks"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CalendarDefinition(_model_base.Model):
    """An object to define the Calendar resource. The list type properties will not be initialized as
    empty list by default. A list of objects should be assigned first before adding new elements.

    Attributes
    ----------
    rest_days : list[~analyticsapi.models.RestDays]
        An array of objects to determine rest days for the calendar.  The
        default value is None, needs to be assigned before using.
    first_day_of_week : str or ~analyticsapi.models.WeekDay
        The first day of the week set for the calendar. Known values are:
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", and
        "Sunday".
    holiday_rules : list[~analyticsapi.models.HolidayRule]
        An array of objects to set holiday rules for the calendar.  The default
        value is None, needs to be assigned before using.
    holiday_exception_rules : list[~analyticsapi.models.HolidayRule]
        An array of objects to determine exceptions from the holiday rules set
        for the calendar.  The default value is None, needs to be assigned
        before using.
    """

    rest_days: Optional[List["_models.RestDays"]] = rest_field(name="restDays")
    """An array of objects to determine rest days for the calendar."""
    first_day_of_week: Optional[Union[str, "_models.WeekDay"]] = rest_field(name="firstDayOfWeek")
    """The first day of the week set for the calendar. Known values are: \"Monday\", \"Tuesday\",
     \"Wednesday\", \"Thursday\", \"Friday\", \"Saturday\", and \"Sunday\"."""
    holiday_rules: Optional[List["_models.HolidayRule"]] = rest_field(name="holidayRules")
    """An array of objects to set holiday rules for the calendar."""
    holiday_exception_rules: Optional[List["_models.HolidayRule"]] = rest_field(name="holidayExceptionRules")
    """An array of objects to determine exceptions from the holiday rules set for the calendar."""

    @overload
    def __init__(
        self,
        *,
        rest_days: Optional[List["_models.RestDays"]] = None,
        first_day_of_week: Optional[Union[str, "_models.WeekDay"]] = None,
        holiday_rules: Optional[List["_models.HolidayRule"]] = None,
        holiday_exception_rules: Optional[List["_models.HolidayRule"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CalendarInfo(_model_base.Model):
    """Object defining the links available on a Calendar resource.

    Readonly variables are only populated by the server, and will be ignored when sending a request.

    Attributes
    ----------
    type : str or ~analyticsapi.models.CALENDAR
        Property defining the type of the resource.
    id : str
        Unique identifier of the Calendar.
    location : ~analyticsapi.models.Location
        Object defining metadata for the Calendar. Required.
    description : ~analyticsapi.models.Description
        Object defining the Calendar.
    """

    type: Optional[Literal[ResourceType.CALENDAR]] = rest_field(visibility=["read"], default=ResourceType.CALENDAR)
    """Property defining the type of the resource."""
    id: Optional[str] = rest_field(visibility=["read"])
    """Unique identifier of the Calendar."""
    location: "_models.Location" = rest_field(visibility=["read", "create"])
    """Object defining metadata for the Calendar. Required."""
    description: Optional["_models.Description"] = rest_field()
    """Object defining the Calendar."""

    @overload
    def __init__(
        self,
        *,
        location: "_models.Location",
        description: Optional["_models.Description"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CalendarResponse(_model_base.Model):
    """Object defining the response for a single Calendar.

    Attributes
    ----------
    data : ~analyticsapi.models.Calendar
        Required.
    meta : ~analyticsapi.models.MetaData
    """

    data: "_models.Calendar" = rest_field()
    """Required."""
    meta: Optional["_models.MetaData"] = rest_field()

    @overload
    def __init__(
        self,
        *,
        data: "_models.Calendar",
        meta: Optional["_models.MetaData"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CapFloorDefinition(_model_base.Model):
    """An object that defines a cap or a floor option.

    Attributes
    ----------
    rate : ~analyticsapi.models.Rate
        An object that defines the cap or floor rate value. Required.
    effective_date : ~datetime.date
        The start date of the cap or floor period. The value is expressed in
        ISO 8601 format: YYYY-MM-DD (e.g., '2021-01-01'). Required.
    type : str or ~analyticsapi.models.CapFloorTypeEnum
        The type of a cap or floor option. Known values are: "Standard",
        "Periodic", "LifeTime", and "FirstPeriod".
    """

    rate: "_models.Rate" = rest_field()
    """An object that defines the cap or floor rate value. Required."""
    effective_date: datetime.date = rest_field(name="effectiveDate")
    """The start date of the cap or floor period. The value is expressed in ISO 8601 format:
     YYYY-MM-DD (e.g., '2021-01-01'). Required."""
    type: Optional[Union[str, "_models.CapFloorTypeEnum"]] = rest_field(default="None")
    """The type of a cap or floor option. Known values are: \"Standard\", \"Periodic\", \"LifeTime\",
     and \"FirstPeriod\"."""

    @overload
    def __init__(
        self,
        *,
        rate: "_models.Rate",
        effective_date: datetime.date,
        type: Optional[Union[str, "_models.CapFloorTypeEnum"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CapVolatility(_model_base.Model):
    """CapVolatility.

    Attributes
    ----------
    value_type : str
        Is either a Literal["ABS"] type or a Literal["REL"] type.
    values_property : list[~analyticsapi.models.CapVolItem]
        The default value is None, needs to be assigned before using.
    """

    value_type: Optional[Literal["ABS", "REL"]] = rest_field(name="valueType")
    """Is either a Literal[\"ABS\"] type or a Literal[\"REL\"] type."""
    values_property: Optional[List["_models.CapVolItem"]] = rest_field(name="values")

    @overload
    def __init__(
        self,
        *,
        value_type: Optional[Literal["ABS", "REL"]] = None,
        values_property: Optional[List["_models.CapVolItem"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CapVolItem(_model_base.Model):
    """CapVolItem.

    Attributes
    ----------
    expiration : ~decimal.Decimal
    value : ~decimal.Decimal
    """

    expiration: Optional[decimal.Decimal] = rest_field()
    value: Optional[decimal.Decimal] = rest_field()

    @overload
    def __init__(
        self,
        *,
        expiration: Optional[decimal.Decimal] = None,
        value: Optional[decimal.Decimal] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CashflowFloaterSettings(_model_base.Model):
    """Optional. Used for securities that float or have collateral that floats.

    Attributes
    ----------
    use_forward_index : bool
        Optional. If false, do not use forwardIndexRate or forwardIndexVector.
    forward_index_rate : float
        Optional. Spread over Forward Index. If used, do not use
        forwardIndexVector.
    forward_index_vector : ~analyticsapi.models.Vector
        Optional. Used for fix-to-float bonds.
    calculate_to_maturity : bool
    """

    use_forward_index: Optional[bool] = rest_field(name="useForwardIndex")
    """Optional. If false, do not use forwardIndexRate or forwardIndexVector."""
    forward_index_rate: Optional[float] = rest_field(name="forwardIndexRate")
    """Optional. Spread over Forward Index. If used, do not use forwardIndexVector."""
    forward_index_vector: Optional["_models.Vector"] = rest_field(name="forwardIndexVector")
    """Optional. Used for fix-to-float bonds."""
    calculate_to_maturity: Optional[bool] = rest_field(name="calculateToMaturity")

    @overload
    def __init__(
        self,
        *,
        use_forward_index: Optional[bool] = None,
        forward_index_rate: Optional[float] = None,
        forward_index_vector: Optional["_models.Vector"] = None,
        calculate_to_maturity: Optional[bool] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CashFlowGlobalSettings(_model_base.Model):
    """CashFlowGlobalSettings.

    Attributes
    ----------
    pricing_date : ~datetime.date
        One of pricingDate, usePreviousClose, or useLiveData is required. This
        selects the date of the pricing curve.
    use_previous_close : bool
        One of pricingDate, usePreviousClose, or useLiveData is required. This
        selects the date of the pricing curve.
    use_live_data : bool
        One of pricingDate, usePreviousClose, or useLiveData is required. This
        selects the date of the pricing curve.
    volatility : ~analyticsapi.models.CashflowVolatility
    retrieve_ppm_projection : bool
        Optional. Retrieves monthly prepayment projections.
    use_non_qm_collateral : bool
        Optional, if true, Non-QM collateral is used for non-agency RMBS model
        calls, otherwise Alt-A collateral is used. This flag only applies to
        prepay type v97. If this flag is set to true, you must also set
        'coreLogicCollateral' to 'USE'.
    core_logic_collateral : str
        Optional, for Non-Agency. Enables model to be run using from CoreLogic
        collateral data. Is one of the following types: Literal["DEFAULT"],
        Literal["USE"], Literal["IGNORE"]
    """

    pricing_date: Optional[datetime.date] = rest_field(name="pricingDate")
    """One of pricingDate, usePreviousClose, or useLiveData is required. This selects the date of the
     pricing curve."""
    use_previous_close: Optional[bool] = rest_field(name="usePreviousClose")
    """One of pricingDate, usePreviousClose, or useLiveData is required. This selects the date of the
     pricing curve."""
    use_live_data: Optional[bool] = rest_field(name="useLiveData")
    """One of pricingDate, usePreviousClose, or useLiveData is required. This selects the date of the
     pricing curve."""
    volatility: Optional["_models.CashflowVolatility"] = rest_field()
    retrieve_ppm_projection: Optional[bool] = rest_field(name="retrievePPMProjection")
    """Optional. Retrieves monthly prepayment projections."""
    use_non_qm_collateral: Optional[bool] = rest_field(name="useNonQMCollateral")
    """Optional, if true, Non-QM collateral is used for non-agency RMBS model calls, otherwise Alt-A
     collateral is used. This flag only applies to prepay type v97. If this flag is set to true, you
     must also set 'coreLogicCollateral' to 'USE'."""
    core_logic_collateral: Optional[Literal["DEFAULT", "USE", "IGNORE"]] = rest_field(name="coreLogicCollateral")
    """Optional, for Non-Agency. Enables model to be run using from CoreLogic collateral data. Is one
     of the following types: Literal[\"DEFAULT\"], Literal[\"USE\"], Literal[\"IGNORE\"]"""

    @overload
    def __init__(
        self,
        *,
        pricing_date: Optional[datetime.date] = None,
        use_previous_close: Optional[bool] = None,
        use_live_data: Optional[bool] = None,
        volatility: Optional["_models.CashflowVolatility"] = None,
        retrieve_ppm_projection: Optional[bool] = None,
        use_non_qm_collateral: Optional[bool] = None,
        core_logic_collateral: Optional[Literal["DEFAULT", "USE", "IGNORE"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CashFlowInput(_model_base.Model):  # pylint: disable=too-many-instance-attributes
    """CashFlowInput.

    Attributes
    ----------
    identifier : str
        Security Reference ID.
    id_type : str or ~analyticsapi.models.IdTypeEnum
        Known values are: "SecurityIDEntry", "SecurityID", "CUSIP", "ISIN",
        "REGSISIN", "SEDOL", "Identifier", "ChinaInterbankCode",
        "ShanghaiExchangeCode", "ShenzhenExchangeCode", and "MXTickerID".
    user_instrument : ~analyticsapi.models.JsonRef
        User Instrument reference.
    user_tag : str
        Optional. User supplied value will show up again on the response side.
    curve : ~analyticsapi.models.CurveTypeAndCurrency
    settlement_type : str
        Is one of the following types: Literal["MARKET"], Literal["INDEX"],
        Literal["CUSTOM"]
    settlement_date : ~datetime.date
        Optional. If settlementType is CUSTOM, user can choose between
        settlementDate and customSettlement. Recommend using settlementDate.
    custom_settlement : str
        Optional. If settlementType is CUSTOM, user can choose between
        settlementDate and customSettlement. Example of customSettlement (T +
        2), where T is the pricing date. Recommend using settlementDate.
    par_amount : str
    loss_settings : ~analyticsapi.models.LossSettings
    prepay : ~analyticsapi.models.CashflowPrepaySettings
    floater_settings : ~analyticsapi.models.CashflowFloaterSettings
    muni_settings : ~analyticsapi.models.MuniSettings
    mbs_settings : ~analyticsapi.models.CashflowMbsSettings
    modification : ~analyticsapi.models.JsonRef
    """

    identifier: Optional[str] = rest_field()
    """Security Reference ID."""
    id_type: Optional[Union[str, "_models.IdTypeEnum"]] = rest_field(name="idType")
    """Known values are: \"SecurityIDEntry\", \"SecurityID\", \"CUSIP\", \"ISIN\", \"REGSISIN\",
     \"SEDOL\", \"Identifier\", \"ChinaInterbankCode\", \"ShanghaiExchangeCode\",
     \"ShenzhenExchangeCode\", and \"MXTickerID\"."""
    user_instrument: Optional["_models.JsonRef"] = rest_field(name="userInstrument")
    """User Instrument reference."""
    user_tag: Optional[str] = rest_field(name="userTag")
    """Optional. User supplied value will show up again on the response side."""
    curve: Optional["_models.CurveTypeAndCurrency"] = rest_field()
    settlement_type: Optional[Literal["MARKET", "INDEX", "CUSTOM"]] = rest_field(name="settlementType")
    """Is one of the following types: Literal[\"MARKET\"], Literal[\"INDEX\"], Literal[\"CUSTOM\"]"""
    settlement_date: Optional[datetime.date] = rest_field(name="settlementDate")
    """Optional. If settlementType is CUSTOM, user can choose between settlementDate and
     customSettlement. Recommend using settlementDate."""
    custom_settlement: Optional[str] = rest_field(name="customSettlement")
    """Optional. If settlementType is CUSTOM, user can choose between settlementDate and
     customSettlement. Example of customSettlement (T + 2), where T is the pricing date. Recommend
     using settlementDate."""
    par_amount: Optional[str] = rest_field(name="parAmount")
    loss_settings: Optional["_models.LossSettings"] = rest_field(name="lossSettings")
    prepay: Optional["_models.CashflowPrepaySettings"] = rest_field()
    floater_settings: Optional["_models.CashflowFloaterSettings"] = rest_field(name="floaterSettings")
    muni_settings: Optional["_models.MuniSettings"] = rest_field(name="muniSettings")
    mbs_settings: Optional["_models.CashflowMbsSettings"] = rest_field(name="mbsSettings")
    modification: Optional["_models.JsonRef"] = rest_field()

    @overload
    def __init__(
        self,
        *,
        identifier: Optional[str] = None,
        id_type: Optional[Union[str, "_models.IdTypeEnum"]] = None,
        user_instrument: Optional["_models.JsonRef"] = None,
        user_tag: Optional[str] = None,
        curve: Optional["_models.CurveTypeAndCurrency"] = None,
        settlement_type: Optional[Literal["MARKET", "INDEX", "CUSTOM"]] = None,
        settlement_date: Optional[datetime.date] = None,
        custom_settlement: Optional[str] = None,
        par_amount: Optional[str] = None,
        loss_settings: Optional["_models.LossSettings"] = None,
        prepay: Optional["_models.CashflowPrepaySettings"] = None,
        floater_settings: Optional["_models.CashflowFloaterSettings"] = None,
        muni_settings: Optional["_models.MuniSettings"] = None,
        mbs_settings: Optional["_models.CashflowMbsSettings"] = None,
        modification: Optional["_models.JsonRef"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CashflowMbsSettings(_model_base.Model):
    """Additional settings for mortgage backed securities.

    Attributes
    ----------
    use_roll_info : bool
        Optional, for adjustable rate mortgages (ARMS). If the ARM has roll
        Information, one can choose to assume the ARM has one reset date or use
        the Roll Information. Note, OAS will not calculate if roll information
        is used.
    assume_call : bool
    step_down_fail : bool
    show_collateral_cash_flow : bool
    """

    use_roll_info: Optional[bool] = rest_field(name="useRollInfo")
    """Optional, for adjustable rate mortgages (ARMS). If the ARM has roll Information, one can choose
     to assume the ARM has one reset date or use the Roll Information. Note, OAS will not calculate
     if roll information is used."""
    assume_call: Optional[bool] = rest_field(name="assumeCall")
    step_down_fail: Optional[bool] = rest_field(name="stepDownFail")
    show_collateral_cash_flow: Optional[bool] = rest_field(name="showCollateralCashFlow")

    @overload
    def __init__(
        self,
        *,
        use_roll_info: Optional[bool] = None,
        assume_call: Optional[bool] = None,
        step_down_fail: Optional[bool] = None,
        show_collateral_cash_flow: Optional[bool] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CashflowPrepaySettings(_model_base.Model):
    """Optional. Used for securities that allow principal prepayment.

    Attributes
    ----------
    type : str
        Required. Is one of the following types: Literal["Model"],
        Literal["CurrentModel"], Literal["NewModel"], Literal["OldModel"],
        Literal["PreExpModel"], Literal["OldExpModel"], Literal["ExpModel"],
        Literal["CPR"], Literal["MHP"], Literal["HEP"], Literal["ABS"],
        Literal["CPB"], Literal["HPC"], Literal["CPJ"], Literal["CPY"],
        Literal["VPR"], Literal["PPV"], Literal["PSJ"], Literal["PSA"]
    rate : float
        Prepayment speed. Either rate or values is required.
    values_property : list[~analyticsapi.models.MonthRatePair]
        The default value is None, needs to be assigned before using.
    """

    type: Optional[
        Literal[
            "Model",
            "CurrentModel",
            "NewModel",
            "OldModel",
            "PreExpModel",
            "OldExpModel",
            "ExpModel",
            "CPR",
            "MHP",
            "HEP",
            "ABS",
            "CPB",
            "HPC",
            "CPJ",
            "CPY",
            "VPR",
            "PPV",
            "PSJ",
            "PSA",
        ]
    ] = rest_field(default=None)
    """Required. Is one of the following types: Literal[\"Model\"], Literal[\"CurrentModel\"],
     Literal[\"NewModel\"], Literal[\"OldModel\"], Literal[\"PreExpModel\"],
     Literal[\"OldExpModel\"], Literal[\"ExpModel\"], Literal[\"CPR\"], Literal[\"MHP\"],
     Literal[\"HEP\"], Literal[\"ABS\"], Literal[\"CPB\"], Literal[\"HPC\"], Literal[\"CPJ\"],
     Literal[\"CPY\"], Literal[\"VPR\"], Literal[\"PPV\"], Literal[\"PSJ\"], Literal[\"PSA\"]"""
    rate: Optional[float] = rest_field()
    """Prepayment speed. Either rate or values is required."""
    values_property: Optional[List["_models.MonthRatePair"]] = rest_field(name="values")

    @overload
    def __init__(
        self,
        *,
        type: Optional[
            Literal[
                "Model",
                "CurrentModel",
                "NewModel",
                "OldModel",
                "PreExpModel",
                "OldExpModel",
                "ExpModel",
                "CPR",
                "MHP",
                "HEP",
                "ABS",
                "CPB",
                "HPC",
                "CPJ",
                "CPY",
                "VPR",
                "PPV",
                "PSJ",
                "PSA",
            ]
        ] = None,
        rate: Optional[float] = None,
        values_property: Optional[List["_models.MonthRatePair"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CashFlowRequestData(_model_base.Model):
    """CashFlowRequestData.

    Attributes
    ----------
    global_settings : ~analyticsapi.models.CashFlowGlobalSettings
    input : list[~analyticsapi.models.CashFlowInput]
        The default value is None, needs to be assigned before using.
    keywords : list[str]
        Optional. Used to specify the keywords a user will retrieve in the
        response. All keywords are returned by default.  The default value is
        None, needs to be assigned before using.
    """

    global_settings: Optional["_models.CashFlowGlobalSettings"] = rest_field(name="globalSettings")
    input: Optional[List["_models.CashFlowInput"]] = rest_field()
    keywords: Optional[List[str]] = rest_field()
    """Optional. Used to specify the keywords a user will retrieve in the response. All keywords are
     returned by default."""

    @overload
    def __init__(
        self,
        *,
        global_settings: Optional["_models.CashFlowGlobalSettings"] = None,
        input: Optional[List["_models.CashFlowInput"]] = None,
        keywords: Optional[List[str]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CashflowVolatility(_model_base.Model):
    """Required.

    Attributes
    ----------
    type : str
        Term structure model selection. Is one of the following types:
        Literal["Single"], Literal["Long"], Literal["Market"],
        Literal["Historical"], Literal["MarketWSkew"], Literal["MatrixWSkew"],
        Literal["Matrix"], Literal["1-Factor"], Literal["1FMeanReversion"],
        Literal["1FNormal"], Literal["LMMSkew"], Literal["LMMSkewOIS"],
        Literal["LMMSkewOld"], Literal["LMMDL"], Literal["LMMDLMOD"],
        Literal["LMMDD"], Literal["LMMCMI"], Literal["LMMCMI2"],
        Literal["LMMALTDD"], Literal["LMMSOFR"], Literal["LMMSOFR2"],
        Literal["LMMSOFRFLAT"], Literal["LMMSCMI2"], Literal["LMMTONAR"],
        Literal["Default"], Literal["1FMeanReversionLogNormal"],
        Literal["1FMeanReversionNormal"]
    rate : float
        Volatility rate input, only needed if type selection is SINGLE.
    """

    type: Optional[
        Literal[
            "Single",
            "Long",
            "Market",
            "Historical",
            "MarketWSkew",
            "MatrixWSkew",
            "Matrix",
            "1-Factor",
            "1FMeanReversion",
            "1FNormal",
            "LMMSkew",
            "LMMSkewOIS",
            "LMMSkewOld",
            "LMMDL",
            "LMMDLMOD",
            "LMMDD",
            "LMMCMI",
            "LMMCMI2",
            "LMMALTDD",
            "LMMSOFR",
            "LMMSOFR2",
            "LMMSOFRFLAT",
            "LMMSCMI2",
            "LMMTONAR",
            "Default",
            "1FMeanReversionLogNormal",
            "1FMeanReversionNormal",
        ]
    ] = rest_field(default=None)
    """Term structure model selection. Is one of the following types: Literal[\"Single\"],
     Literal[\"Long\"], Literal[\"Market\"], Literal[\"Historical\"], Literal[\"MarketWSkew\"],
     Literal[\"MatrixWSkew\"], Literal[\"Matrix\"], Literal[\"1-Factor\"],
     Literal[\"1FMeanReversion\"], Literal[\"1FNormal\"], Literal[\"LMMSkew\"],
     Literal[\"LMMSkewOIS\"], Literal[\"LMMSkewOld\"], Literal[\"LMMDL\"], Literal[\"LMMDLMOD\"],
     Literal[\"LMMDD\"], Literal[\"LMMCMI\"], Literal[\"LMMCMI2\"], Literal[\"LMMALTDD\"],
     Literal[\"LMMSOFR\"], Literal[\"LMMSOFR2\"], Literal[\"LMMSOFRFLAT\"], Literal[\"LMMSCMI2\"],
     Literal[\"LMMTONAR\"], Literal[\"Default\"], Literal[\"1FMeanReversionLogNormal\"],
     Literal[\"1FMeanReversionNormal\"]"""
    rate: Optional[float] = rest_field()
    """Volatility rate input, only needed if type selection is SINGLE."""

    @overload
    def __init__(
        self,
        *,
        type: Optional[
            Literal[
                "Single",
                "Long",
                "Market",
                "Historical",
                "MarketWSkew",
                "MatrixWSkew",
                "Matrix",
                "1-Factor",
                "1FMeanReversion",
                "1FNormal",
                "LMMSkew",
                "LMMSkewOIS",
                "LMMSkewOld",
                "LMMDL",
                "LMMDLMOD",
                "LMMDD",
                "LMMCMI",
                "LMMCMI2",
                "LMMALTDD",
                "LMMSOFR",
                "LMMSOFR2",
                "LMMSOFRFLAT",
                "LMMSCMI2",
                "LMMTONAR",
                "Default",
                "1FMeanReversionLogNormal",
                "1FMeanReversionNormal",
            ]
        ] = None,
        rate: Optional[float] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CloSettings(_model_base.Model):
    """CloSettings.

    Attributes
    ----------
    call_date : ~datetime.date
    """

    call_date: Optional[datetime.date] = rest_field(name="callDate")

    @overload
    def __init__(
        self,
        call_date: Optional[datetime.date] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["call_date"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class CmbsPrepayment(_model_base.Model):
    """CmbsPrepayment.

    Attributes
    ----------
    rate_during_yield_to_maturity : float
        Prepayment speed during the yield maintenance period.
    rate_after_yield_to_maturity : float
        Prepayment speed after the yield maintenance period.
    rate_during_premium : float
        Prepayment speed during the premium period.
    """

    rate_during_yield_to_maturity: Optional[float] = rest_field(name="rateDuringYieldToMaturity")
    """Prepayment speed during the yield maintenance period."""
    rate_after_yield_to_maturity: Optional[float] = rest_field(name="rateAfterYieldToMaturity")
    """Prepayment speed after the yield maintenance period."""
    rate_during_premium: Optional[float] = rest_field(name="rateDuringPremium")
    """Prepayment speed during the premium period."""

    @overload
    def __init__(
        self,
        *,
        rate_during_yield_to_maturity: Optional[float] = None,
        rate_after_yield_to_maturity: Optional[float] = None,
        rate_during_premium: Optional[float] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CmbsSettings(_model_base.Model):
    """CmbsSettings.

    Attributes
    ----------
    pricing_scenarios : list[~analyticsapi.models.PricingScenario]
        Choose between type + rate, systemScenarioName, or specifing a full
        scenario using CustomScenario.  The default value is None, needs to be
        assigned before using.
    """

    pricing_scenarios: Optional[List["_models.PricingScenario"]] = rest_field(name="pricingScenarios")
    """Choose between type + rate, systemScenarioName, or specifing a full scenario using
     CustomScenario."""

    @overload
    def __init__(
        self,
        pricing_scenarios: Optional[List["_models.PricingScenario"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["pricing_scenarios"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class CmdtyOptionVolSurfaceChoice(_model_base.Model):
    """The object to provide either a reference to a commodity volatility surface stored in the
    platform or 3rd party volatilities.

    Attributes
    ----------
    reference : str
        The reference to a volatility surface stored in the platform.
    surface : ~analyticsapi.models.CmdtyVolSurfaceInput
        The volatility surface data.
    """

    reference: Optional[str] = rest_field()
    """The reference to a volatility surface stored in the platform."""
    surface: Optional["_models.CmdtyVolSurfaceInput"] = rest_field()
    """The volatility surface data."""

    @overload
    def __init__(
        self,
        *,
        reference: Optional[str] = None,
        surface: Optional["_models.CmdtyVolSurfaceInput"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CmdtyVolSurfaceInput(_model_base.Model):
    """The object defining the 3rd party commodity volatility surface.

    Attributes
    ----------
    strike_type : str or ~analyticsapi.models.StrikeTypeEnum
        The property that defines the type of the strikes provided in the
        surface points. Required. Known values are: "Absolute", "BasisPoint",
        "Delta", "Moneyness", "Percent", and "Relative".
    model_type : str or ~analyticsapi.models.VolModelTypeEnum
        The property that defines the type of the model (Normal or LogNormal)
        of the volatilities provided in the surface points. Required. Known
        values are: "Normal" and "LogNormal".
    points : list[~analyticsapi.models.VolSurfacePoint]
        The list of volatility points. Required.  The default value is None,
        needs to be assigned before using.
    contract_code : str
        The contract code of the commodity. Required.
    """

    strike_type: Union[str, "_models.StrikeTypeEnum"] = rest_field(name="strikeType")
    """The property that defines the type of the strikes provided in the surface points. Required.
     Known values are: \"Absolute\", \"BasisPoint\", \"Delta\", \"Moneyness\", \"Percent\", and
     \"Relative\"."""
    model_type: Union[str, "_models.VolModelTypeEnum"] = rest_field(name="modelType")
    """The property that defines the type of the model (Normal or LogNormal) of the volatilities
     provided in the surface points. Required. Known values are: \"Normal\" and \"LogNormal\"."""
    points: List["_models.VolSurfacePoint"] = rest_field()
    """The list of volatility points. Required."""
    contract_code: str = rest_field(name="contractCode")
    """The contract code of the commodity. Required."""

    @overload
    def __init__(
        self,
        *,
        strike_type: Union[str, "_models.StrikeTypeEnum"],
        model_type: Union[str, "_models.VolModelTypeEnum"],
        points: List["_models.VolSurfacePoint"],
        contract_code: str,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CMOModification(_model_base.Model):
    """CMOModification.

    Attributes
    ----------
    collateral : dict[str, ~analyticsapi.models.ModifyCollateral]
    class_property : ~analyticsapi.models.ModifyClass
    """

    collateral: Optional[Dict[str, "_models.ModifyCollateral"]] = rest_field()
    class_property: Optional["_models.ModifyClass"] = rest_field(name="class")

    @overload
    def __init__(
        self,
        *,
        collateral: Optional[Dict[str, "_models.ModifyCollateral"]] = None,
        class_property: Optional["_models.ModifyClass"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CollectionLinks(_model_base.Model):
    """CollectionLinks.

    Attributes
    ----------
    self_property : ~analyticsapi.models.Link
        Required.
    first : ~analyticsapi.models.Link
    prev : ~analyticsapi.models.Link
    next : ~analyticsapi.models.Link
    last : ~analyticsapi.models.Link
    """

    self_property: "_models.Link" = rest_field(name="self")
    """Required."""
    first: Optional["_models.Link"] = rest_field()
    prev: Optional["_models.Link"] = rest_field()
    next: Optional["_models.Link"] = rest_field()
    last: Optional["_models.Link"] = rest_field()

    @overload
    def __init__(
        self,
        *,
        self_property: "_models.Link",
        first: Optional["_models.Link"] = None,
        prev: Optional["_models.Link"] = None,
        next: Optional["_models.Link"] = None,
        last: Optional["_models.Link"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ColumnDetail(_model_base.Model):  # pylint: disable=too-many-instance-attributes
    """ColumnDetail.

    Attributes
    ----------
    header : str
        Header to be used for the first row. Header should be limited to
        a-zA-Z0-9_ (regular identifiers). If header is omitted, the item is
        used.
    new_field : str
    field : str
    default_value : str
    format : str
    date_format : str
        Date format, e.g. 'yyyy-mm-dd', based on Java date formatting.
    num_scale : int
        Scale factor, multiply value by 10**scale. E.g., to show percent,
        scale=2. Applies to int as well.
    str_width : int
        Max width of output (string).
    bool_true : str
        Boolean format, see above - 'YES', 'Y', 'TRUE', 'T' (and their lower
        case values).
    bool_false : str
        See above.
    charset : str
    type : str
    lookup : ~analyticsapi.models.LookupDetails
    precision : int
    scale : int
    """

    header: Optional[str] = rest_field()
    """Header to be used for the first row. Header should be limited to a-zA-Z0-9_ (regular
     identifiers). If header is omitted, the item is used."""
    new_field: Optional[str] = rest_field(name="newField")
    field: Optional[str] = rest_field()
    default_value: Optional[str] = rest_field(name="defaultValue")
    format: Optional[str] = rest_field()
    date_format: Optional[str] = rest_field(name="dateFormat")
    """Date format, e.g. 'yyyy-mm-dd', based on Java date formatting."""
    num_scale: Optional[int] = rest_field(name="numScale")
    """Scale factor, multiply value by 10**scale. E.g., to show percent, scale=2. Applies to int as
     well."""
    str_width: Optional[int] = rest_field(name="strWidth")
    """Max width of output (string)."""
    bool_true: Optional[str] = rest_field(name="boolTrue")
    """Boolean format, see above - 'YES', 'Y', 'TRUE', 'T' (and their lower case values)."""
    bool_false: Optional[str] = rest_field(name="boolFalse")
    """See above."""
    charset: Optional[str] = rest_field()
    type: Optional[str] = rest_field(default="None")
    lookup: Optional["_models.LookupDetails"] = rest_field()
    precision: Optional[int] = rest_field()
    scale: Optional[int] = rest_field()

    @overload
    def __init__(
        self,
        *,
        header: Optional[str] = None,
        new_field: Optional[str] = None,
        field: Optional[str] = None,
        default_value: Optional[str] = None,
        format: Optional[str] = None,
        date_format: Optional[str] = None,
        num_scale: Optional[int] = None,
        str_width: Optional[int] = None,
        bool_true: Optional[str] = None,
        bool_false: Optional[str] = None,
        charset: Optional[str] = None,
        type: Optional[str] = None,
        lookup: Optional["_models.LookupDetails"] = None,
        precision: Optional[int] = None,
        scale: Optional[int] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ComputeDatesBatched(_model_base.Model):
    """An object to definine the properties of the calculated dates returned, with a dedicated error
    object for each calculation. This serializable object behaves exactly like a list of
    dictionaries when iterated or displayed. It can be converted to a DataFrame without
    transformation.

    Attributes
    ----------
    tenor : str
        The code indicating the tenor added to startDate to calculate the
        resulted date (e.g., 1Y). Required.
    end_date : ~datetime.date
        The date produced by the calculation. The value is expressed in ISO
        8601 format: YYYY-MM-DD (e.g., 2024-01-01).
    processing_information : str
        The error message for the calculation in case of a non-blocking error.
    error : ~analyticsapi.models.ServiceError
    """

    tenor: str = rest_field()
    """The code indicating the tenor added to startDate to calculate the resulted date (e.g., 1Y).
     Required."""
    end_date: Optional[datetime.date] = rest_field(name="endDate")
    """The date produced by the calculation. The value is expressed in ISO 8601 format: YYYY-MM-DD
     (e.g., 2024-01-01)."""
    processing_information: Optional[str] = rest_field(name="processingInformation")
    """The error message for the calculation in case of a non-blocking error."""
    error: Optional["_models.ServiceError"] = rest_field()

    @overload
    def __init__(
        self,
        *,
        tenor: str,
        end_date: Optional[datetime.date] = None,
        processing_information: Optional[str] = None,
        error: Optional["_models.ServiceError"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ComputeDatesResponse(_model_base.Model):
    """An object to define a paginated response to a request to calculate dates.

    Attributes
    ----------
    data : list[~analyticsapi.models.ComputeDatesBatched]
        Required.  The default value is None, needs to be assigned before
        using.
    page : int
        The page number of the current page displayed. Minimum value of this
        property is 1. Required.
    item_per_page : int
        Number of items displayed per page. Required.
    total_pages : int
        Total number of pages available for display. Required.
    total_items : int
        Total number of items available for display. Required.
    links : ~analyticsapi.models.CollectionLinks
        Links for available operations and/or resources linked to current
        response.
    """

    data: List["_models.ComputeDatesBatched"] = rest_field()
    """Required."""
    page: int = rest_field()
    """The page number of the current page displayed. Minimum value of this property is 1. Required."""
    item_per_page: int = rest_field(name="itemPerPage")
    """Number of items displayed per page. Required."""
    total_pages: int = rest_field(name="totalPages")
    """Total number of pages available for display. Required."""
    total_items: int = rest_field(name="totalItems")
    """Total number of items available for display. Required."""
    links: Optional["_models.CollectionLinks"] = rest_field()
    """Links for available operations and/or resources linked to current response."""

    @overload
    def __init__(
        self,
        *,
        data: List["_models.ComputeDatesBatched"],
        page: int,
        item_per_page: int,
        total_pages: int,
        total_items: int,
        links: Optional["_models.CollectionLinks"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ConvertiblePricing(_model_base.Model):
    """ConvertiblePricing.

    Attributes
    ----------
    method : str
        Is one of the following types: Literal["AT_MARKET"],
        Literal["AT_IMPLIED_STOCK_VOLATILITY"],
        Literal["AT_IMPLIED_CREDIT_SPREAD"]
    market_price : float
    credit_spread : float
    stock_price : float
    stock_dividend_yield : float
    stock_volatility : float
    stock_borrow_rate : float
    """

    method: Optional[Literal["AT_MARKET", "AT_IMPLIED_STOCK_VOLATILITY", "AT_IMPLIED_CREDIT_SPREAD"]] = rest_field()
    """Is one of the following types: Literal[\"AT_MARKET\"],
     Literal[\"AT_IMPLIED_STOCK_VOLATILITY\"], Literal[\"AT_IMPLIED_CREDIT_SPREAD\"]"""
    market_price: Optional[float] = rest_field(name="marketPrice")
    credit_spread: Optional[float] = rest_field(name="creditSpread")
    stock_price: Optional[float] = rest_field(name="stockPrice")
    stock_dividend_yield: Optional[float] = rest_field(name="stockDividendYield")
    stock_volatility: Optional[float] = rest_field(name="stockVolatility")
    stock_borrow_rate: Optional[float] = rest_field(name="stockBorrowRate")

    @overload
    def __init__(
        self,
        *,
        method: Optional[Literal["AT_MARKET", "AT_IMPLIED_STOCK_VOLATILITY", "AT_IMPLIED_CREDIT_SPREAD"]] = None,
        market_price: Optional[float] = None,
        credit_spread: Optional[float] = None,
        stock_price: Optional[float] = None,
        stock_dividend_yield: Optional[float] = None,
        stock_volatility: Optional[float] = None,
        stock_borrow_rate: Optional[float] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ConvexityAdjustment(_model_base.Model):
    """An object that contains parameters used to control the convexity adjustment of the reference
    index.

    Attributes
    ----------
    mean_reversion_percent : float
        The mean reversion speed rate used to calculate the convexity
        adjustment.
    volatility_percent : float
        The volatility percent used to calculate the convexity adjustment.
    method : str or ~analyticsapi.models.ConvexityAdjustmentMethodEnum
        The convexity adjustment method. Required. Known values are:
        "BlackScholes", "LinearSwapModel", and "Replication".
    integration_method : str or ~analyticsapi.models.IntegrationMethodEnum
        The integration method used for static replication. Required. Known
        values are: "RiemannSum" and "RungeKutta".
    """

    mean_reversion_percent: Optional[float] = rest_field(name="meanReversionPercent")
    """The mean reversion speed rate used to calculate the convexity adjustment."""
    volatility_percent: Optional[float] = rest_field(name="volatilityPercent")
    """The volatility percent used to calculate the convexity adjustment."""
    method: Union[str, "_models.ConvexityAdjustmentMethodEnum"] = rest_field()
    """The convexity adjustment method. Required. Known values are: \"BlackScholes\",
     \"LinearSwapModel\", and \"Replication\"."""
    integration_method: Union[str, "_models.IntegrationMethodEnum"] = rest_field(name="integrationMethod")
    """The integration method used for static replication. Required. Known values are: \"RiemannSum\"
     and \"RungeKutta\"."""

    @overload
    def __init__(
        self,
        *,
        method: Union[str, "_models.ConvexityAdjustmentMethodEnum"],
        integration_method: Union[str, "_models.IntegrationMethodEnum"],
        mean_reversion_percent: Optional[float] = None,
        volatility_percent: Optional[float] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CountPeriodsOutput(_model_base.Model):
    """The result of the period calculation for the count periods endpoint.

    Attributes
    ----------
    count : float
        The calculated number of dates in the period from startDate to endDate.
        endDate is included, startDate is not. Required.
    period_type : str or ~analyticsapi.models.PeriodTypeOutput
        The type of the calculated period. Required. Known values are: "Day",
        "WorkingDay", "Week", "Month", "Quarter", and "Year".
    processing_information : str
        The error message for the calculation in case of a non-blocking error.
    """

    count: float = rest_field()
    """The calculated number of dates in the period from startDate to endDate. endDate is included,
     startDate is not. Required."""
    period_type: Union[str, "_models.PeriodTypeOutput"] = rest_field(name="periodType")
    """The type of the calculated period. Required. Known values are: \"Day\", \"WorkingDay\",
     \"Week\", \"Month\", \"Quarter\", and \"Year\"."""
    processing_information: Optional[str] = rest_field(name="processingInformation")
    """The error message for the calculation in case of a non-blocking error."""

    @overload
    def __init__(
        self,
        *,
        count: float,
        period_type: Union[str, "_models.PeriodTypeOutput"],
        processing_information: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CountPeriodsResponse(_model_base.Model):
    """An object to define the response to a request to calculate the period of time between two
    dates.

    Attributes
    ----------
    data : ~analyticsapi.models.CountPeriodsOutput
        Required.
    """

    data: "_models.CountPeriodsOutput" = rest_field()
    """Required."""

    @overload
    def __init__(
        self,
        data: "_models.CountPeriodsOutput",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["data"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class CreditCurveChoice(_model_base.Model):
    """The object to provide either a reference to a credit curve stored in the platform or a 3rd
    party curve.

    Attributes
    ----------
    reference : str
        The reference to a credit curve stored in the platform.
    curve : ~analyticsapi.models.CreditCurveInput
        The credit curve data.
    """

    reference: Optional[str] = rest_field()
    """The reference to a credit curve stored in the platform."""
    curve: Optional["_models.CreditCurveInput"] = rest_field()
    """The credit curve data."""

    @overload
    def __init__(
        self,
        *,
        reference: Optional[str] = None,
        curve: Optional["_models.CreditCurveInput"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CreditCurveInput(_model_base.Model):
    """The object defining the 3rd party credit curve.

    Attributes
    ----------
    zc_type : str or ~analyticsapi.models.ZcTypeEnum
        The type of values provided (zero coupon rates or discount factors).
        Required. Known values are: "Rate" and "DiscountFactor".
    zc_unit : str or ~analyticsapi.models.UnitEnum
        The unit of the values provided (absolute, basis point, percentage).
        Required. Known values are: "Absolute", "BasisPoint", and "Percentage".
    points : list[~analyticsapi.models.CurveDataPoint]
        The list of dates and values. Required.  The default value is None,
        needs to be assigned before using.
    entity_code : str
        The code of the reference entity. Required.
    """

    zc_type: Union[str, "_models.ZcTypeEnum"] = rest_field(name="zcType")
    """The type of values provided (zero coupon rates or discount factors). Required. Known values
     are: \"Rate\" and \"DiscountFactor\"."""
    zc_unit: Union[str, "_models.UnitEnum"] = rest_field(name="zcUnit")
    """The unit of the values provided (absolute, basis point, percentage). Required. Known values
     are: \"Absolute\", \"BasisPoint\", and \"Percentage\"."""
    points: List["_models.CurveDataPoint"] = rest_field()
    """The list of dates and values. Required."""
    entity_code: str = rest_field(name="entityCode")
    """The code of the reference entity. Required."""

    @overload
    def __init__(
        self,
        *,
        zc_type: Union[str, "_models.ZcTypeEnum"],
        zc_unit: Union[str, "_models.UnitEnum"],
        points: List["_models.CurveDataPoint"],
        entity_code: str,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CrossCurencySwapOverride(_model_base.Model):
    """An object that contains the cross currency swap properties that can be overridden.

    Attributes
    ----------
    start_date : ~analyticsapi.models.Date
        An object that contains properties to define and adjust the cross
        currency swap start date.
    end_date : ~analyticsapi.models.Date
        An object that contains properties to define and adjust the cross
        currency swap end date.
    amount : float
        The principal amount of the cross currency swap in the base currency.
    contra_amount : float
        The principal amount of the cross currency swap in the contra currency.
    fixed_rate : ~analyticsapi.models.Rate
    spread : ~analyticsapi.models.Rate
    paid_leg : str or ~analyticsapi.models.PaidLegEnum
        A flag that defines whether the first leg or the second leg of the
        cross currency swap is paid. Known values are: "FirstLeg" and
        "SecondLeg".
    """

    start_date: Optional["_models.Date"] = rest_field(name="startDate")
    """An object that contains properties to define and adjust the cross currency swap start date."""
    end_date: Optional["_models.Date"] = rest_field(name="endDate")
    """An object that contains properties to define and adjust the cross currency swap end date."""
    amount: Optional[float] = rest_field()
    """The principal amount of the cross currency swap in the base currency."""
    contra_amount: Optional[float] = rest_field(name="contraAmount")
    """The principal amount of the cross currency swap in the contra currency."""
    fixed_rate: Optional["_models.Rate"] = rest_field(name="fixedRate")
    spread: Optional["_models.Rate"] = rest_field()
    paid_leg: Optional[Union[str, "_models.PaidLegEnum"]] = rest_field(name="paidLeg")
    """A flag that defines whether the first leg or the second leg of the cross currency swap is paid.
     Known values are: \"FirstLeg\" and \"SecondLeg\"."""

    @overload
    def __init__(
        self,
        *,
        start_date: Optional["_models.Date"] = None,
        end_date: Optional["_models.Date"] = None,
        amount: Optional[float] = None,
        contra_amount: Optional[float] = None,
        fixed_rate: Optional["_models.Rate"] = None,
        spread: Optional["_models.Rate"] = None,
        paid_leg: Optional[Union[str, "_models.PaidLegEnum"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CrossCurrencySwapTemplateDefinition(InstrumentTemplateDefinition, discriminator="CrossCurrencySwap"):
    """CrossCurrencySwapTemplateDefinition.

    Attributes
    ----------
    instrument_type : str or ~analyticsapi.models.CROSS_CURRENCY_SWAP
        Required. A cross currency swap contract.
    template : ~analyticsapi.models.IrSwapDefinition
        Required.
    """

    instrument_type: Literal[InstrumentTemplateTypeEnum.CROSS_CURRENCY_SWAP] = rest_discriminator(name="instrumentType")  # type: ignore
    """Required. A cross currency swap contract."""
    template: "_models.IrSwapDefinition" = rest_field()
    """Required."""

    @overload
    def __init__(
        self,
        template: "_models.IrSwapDefinition",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, instrument_type=InstrumentTemplateTypeEnum.CROSS_CURRENCY_SWAP, **kwargs)


class CurencyBasisSwapOverride(_model_base.Model):
    """An object that contains the currency basis swap properties that can be overridden.

    Attributes
    ----------
    start_date : ~analyticsapi.models.Date
        An object that contains properties to define and adjust the currency
        basis swap start date.
    end_date : ~analyticsapi.models.Date
        An object that contains properties to define and adjust the currency
        basis swap end date.
    amount : float
        The principal amount of the currency basis swap in the base currency.
    contra_amount : float
        The principal amount of the currency basis swap in the contra currency.
    first_spread : ~analyticsapi.models.Rate
    second_spread : ~analyticsapi.models.Rate
    paid_leg : str or ~analyticsapi.models.PaidLegEnum
        A flag that defines whether the first leg or the second leg of the
        currency basis swap is paid. Known values are: "FirstLeg" and
        "SecondLeg".
    """

    start_date: Optional["_models.Date"] = rest_field(name="startDate")
    """An object that contains properties to define and adjust the currency basis swap start date."""
    end_date: Optional["_models.Date"] = rest_field(name="endDate")
    """An object that contains properties to define and adjust the currency basis swap end date."""
    amount: Optional[float] = rest_field()
    """The principal amount of the currency basis swap in the base currency."""
    contra_amount: Optional[float] = rest_field(name="contraAmount")
    """The principal amount of the currency basis swap in the contra currency."""
    first_spread: Optional["_models.Rate"] = rest_field(name="firstSpread")
    second_spread: Optional["_models.Rate"] = rest_field(name="secondSpread")
    paid_leg: Optional[Union[str, "_models.PaidLegEnum"]] = rest_field(name="paidLeg")
    """A flag that defines whether the first leg or the second leg of the currency basis swap is paid.
     Known values are: \"FirstLeg\" and \"SecondLeg\"."""

    @overload
    def __init__(
        self,
        *,
        start_date: Optional["_models.Date"] = None,
        end_date: Optional["_models.Date"] = None,
        amount: Optional[float] = None,
        contra_amount: Optional[float] = None,
        first_spread: Optional["_models.Rate"] = None,
        second_spread: Optional["_models.Rate"] = None,
        paid_leg: Optional[Union[str, "_models.PaidLegEnum"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxConstituent(ABC, _model_base.Model):
    """An object to define constituents that are used to construct the curve.

    You probably want to use the sub-classes and not this class directly. Known sub-classes are:
    CurrencyBasisSwapConstituent, DepositFxConstituent, FxForwardConstituent, FxSpotConstituent

    Readonly variables are only populated by the server, and will be ignored when sending a request.

    Attributes
    ----------
    type : str or ~analyticsapi.models.FxConstituentEnum
        The type of the instrument used as a constituent. Required. Known
        values are: "FxSpot", "FxForward", "CurrencyBasisSwap", and "Deposit".
    quote : ~analyticsapi.models.Quote
        An object to define the quote of the instrument used as a constituent.
    status : list[str]
        A message is returned if the constituent cannot be identified, or
        access for a user to the instrument used as a constituent is denied.
    """

    __mapping__: Dict[str, _model_base.Model] = {}
    type: str = rest_discriminator(name="type")
    """The type of the instrument used as a constituent. Required. Known values are: \"FxSpot\",
     \"FxForward\", \"CurrencyBasisSwap\", and \"Deposit\"."""
    quote: Optional["_models.Quote"] = rest_field()
    """An object to define the quote of the instrument used as a constituent."""
    status: Optional[List[str]] = rest_field(visibility=["read"])
    """A message is returned if the constituent cannot be identified, or access for a user to the
     instrument used as a constituent is denied."""

    @overload
    def __init__(
        self,
        *,
        type: str,
        quote: Optional["_models.Quote"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CurrencyBasisSwapConstituent(FxConstituent, discriminator="CurrencyBasisSwap"):
    """An object to define constituents that are used to construct the curve.

    Readonly variables are only populated by the server, and will be ignored when sending a request.

    Attributes
    ----------
    quote : ~analyticsapi.models.Quote
        An object to define the quote of the instrument used as a constituent.
    status : list[str]
        A message is returned if the constituent cannot be identified, or
        access for a user to the instrument used as a constituent is denied.
    type : str or ~analyticsapi.models.CURRENCY_BASIS_SWAP
        The type of the instrument used as a constituent. Required.
    definition : ~analyticsapi.models.CurrencyBasisSwapConstituentDefinition
        An object to define the instrument used as a constituent.
    """

    type: Literal[FxConstituentEnum.CURRENCY_BASIS_SWAP] = rest_discriminator(name="type")  # type: ignore
    """The type of the instrument used as a constituent. Required."""
    definition: Optional["_models.CurrencyBasisSwapConstituentDefinition"] = rest_field()
    """An object to define the instrument used as a constituent."""

    @overload
    def __init__(
        self,
        *,
        quote: Optional["_models.Quote"] = None,
        definition: Optional["_models.CurrencyBasisSwapConstituentDefinition"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, type=FxConstituentEnum.CURRENCY_BASIS_SWAP, **kwargs)


class CurrencyBasisSwapConstituentDefinition(_model_base.Model):
    """An object to define the cross-currency swap instrument used as a constituent.

    Attributes
    ----------
    tenor : str
        The code indicating the tenor of the instrument used as a constituent
        (e.g., '1M', '1Y'). Required.
    template : str
        A pre-defined template can be used as an input by the user. It is the
        currency code of the constituent.
    """

    tenor: str = rest_field()
    """The code indicating the tenor of the instrument used as a constituent (e.g., '1M', '1Y').
     Required."""
    template: Optional[str] = rest_field()
    """A pre-defined template can be used as an input by the user. It is the currency code of the
     constituent."""

    @overload
    def __init__(
        self,
        *,
        tenor: str,
        template: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CurrencyBasisSwapTemplateDefinition(InstrumentTemplateDefinition, discriminator="CurrencyBasisSwap"):
    """CurrencyBasisSwapTemplateDefinition.

    Attributes
    ----------
    instrument_type : str or ~analyticsapi.models.CURRENCY_BASIS_SWAP
        Required. A currency basis swap contract.
    template : ~analyticsapi.models.IrSwapDefinition
        Required.
    """

    instrument_type: Literal[InstrumentTemplateTypeEnum.CURRENCY_BASIS_SWAP] = rest_discriminator(name="instrumentType")  # type: ignore
    """Required. A currency basis swap contract."""
    template: "_models.IrSwapDefinition" = rest_field()
    """Required."""

    @overload
    def __init__(
        self,
        template: "_models.IrSwapDefinition",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, instrument_type=InstrumentTemplateTypeEnum.CURRENCY_BASIS_SWAP, **kwargs)


class Curve(ABC, _model_base.Model):
    """An object to define a Curve depending on its type.

    You probably want to use the sub-classes and not this class directly. Known sub-classes are:
    DividendCurve, FxOutrightCurve, IrZcCurve

    Attributes
    ----------
    curve_type : str or ~analyticsapi.models.CurveTypeEnum
        The type of the curve. Required. Known values are: "IrZcCurve",
        "FxOutrightCurve", and "DividendCurve".
    """

    __mapping__: Dict[str, _model_base.Model] = {}
    curve_type: str = rest_discriminator(name="curveType")
    """The type of the curve. Required. Known values are: \"IrZcCurve\", \"FxOutrightCurve\", and
     \"DividendCurve\"."""

    @overload
    def __init__(
        self,
        curve_type: str,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["curve_type"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class CurveCalculationParameters(_model_base.Model):
    """An object that contains parameters used to define how the curve is constructed from the
    constituents.

    Attributes
    ----------
    valuation_date : ~datetime.date
        The date on which the curve is constructed. The value is expressed in
        ISO 8601 format: YYYY-MM-DD (e.g., '2023-01-01'). The valuation date
        should not be in the future. Default is Today.
    curve_tenors : list[str]
        An array of user-defined tenors for which curve points to be computed.
        The values are expressed in:

        * time period code for tenors (e.g., '1M', '1Y'),
        * ISO 8601 format 'YYYY-MM-DD' for dates (e.g., '2023-01-01').  The default value is None,
        needs to be assigned before using.
    """

    valuation_date: Optional[datetime.date] = rest_field(name="valuationDate")
    """The date on which the curve is constructed. The value is expressed in ISO 8601 format:
     YYYY-MM-DD (e.g., '2023-01-01').
     The valuation date should not be in the future. Default is Today."""
    curve_tenors: Optional[List[str]] = rest_field(name="curveTenors")
    """An array of user-defined tenors for which curve points to be computed. The values are expressed
     in:
     
     
     * time period code for tenors (e.g., '1M', '1Y'),
     * ISO 8601 format 'YYYY-MM-DD' for dates (e.g., '2023-01-01')."""

    @overload
    def __init__(
        self,
        *,
        valuation_date: Optional[datetime.date] = None,
        curve_tenors: Optional[List[str]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CurveDataPoint(_model_base.Model):
    """An object that represents a curve point.

    Attributes
    ----------
    date : ~datetime.date
        The date of the zero coupon value. Required.
    value : float
        The zero coupon value. Required.
    """

    date: datetime.date = rest_field()
    """The date of the zero coupon value. Required."""
    value: float = rest_field()
    """The zero coupon value. Required."""

    @overload
    def __init__(
        self,
        *,
        date: datetime.date,
        value: float,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CurveDetailsRequest(_model_base.Model):
    """CurveDetailsRequest.

    Attributes
    ----------
    curves : list[~analyticsapi.models.CurveSearch]
        The default value is None, needs to be assigned before using.
    """

    curves: Optional[List["_models.CurveSearch"]] = rest_field()

    @overload
    def __init__(
        self,
        curves: Optional[List["_models.CurveSearch"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["curves"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class CurveMultiShift(_model_base.Model):
    """CurveMultiShift.

    Attributes
    ----------
    period : ~decimal.Decimal
        Months from the settlement date. The last month must match the horizon
        date.
    curve_shifts : list[~analyticsapi.models.ApimCurveShift]
        The default value is None, needs to be assigned before using.
    """

    period: Optional[decimal.Decimal] = rest_field()
    """Months from the settlement date. The last month must match the horizon date."""
    curve_shifts: Optional[List["_models.ApimCurveShift"]] = rest_field(name="curveShifts")

    @overload
    def __init__(
        self,
        *,
        period: Optional[decimal.Decimal] = None,
        curve_shifts: Optional[List["_models.ApimCurveShift"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CurvePoint(_model_base.Model):
    """CurvePoint.

    Attributes
    ----------
    rate : ~decimal.Decimal
    term : ~decimal.Decimal
    """

    rate: Optional[decimal.Decimal] = rest_field()
    term: Optional[decimal.Decimal] = rest_field()

    @overload
    def __init__(
        self,
        *,
        rate: Optional[decimal.Decimal] = None,
        term: Optional[decimal.Decimal] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CurvePointRelatedInstruments(_model_base.Model):
    """An object that contains the instrument used to calculate the curve point.

    Attributes
    ----------
    instrument_code : str
        The code to define the instrument used to calculate the curve point.
        Required.
    """

    instrument_code: str = rest_field(name="instrumentCode")
    """The code to define the instrument used to calculate the curve point. Required."""

    @overload
    def __init__(
        self,
        instrument_code: str,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["instrument_code"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class CurveSearch(_model_base.Model):  # pylint: disable=too-many-instance-attributes
    """CurveSearch.

    Attributes
    ----------
    curve_id : str
    curve_type : str
        Is one of the following types: Literal["GVT"], Literal["GVT_TSYM"],
        Literal["GVT_TSYM_MUNI"], Literal["GVT_AGN"], Literal["GVT_MUNI"],
        Literal["GVT_BUND"], Literal["SWAP"], Literal["SWAP_RFR"],
        Literal["SWAP_MUNI"]
    currency : str
    cds_ticker : str
    expand_curve : bool
    pricing_date : ~datetime.date
    show_spot_rate : bool
    show_forward_rate : bool
    show_discount_factor : bool
    forward_period : float
    implied_forward_delay : float
    index : str
    use_live_curve : bool
    """

    curve_id: Optional[str] = rest_field(name="curveId")
    curve_type: Optional[
        Literal["GVT", "GVT_TSYM", "GVT_TSYM_MUNI", "GVT_AGN", "GVT_MUNI", "GVT_BUND", "SWAP", "SWAP_RFR", "SWAP_MUNI"]
    ] = rest_field(name="curveType")
    """Is one of the following types: Literal[\"GVT\"], Literal[\"GVT_TSYM\"],
     Literal[\"GVT_TSYM_MUNI\"], Literal[\"GVT_AGN\"], Literal[\"GVT_MUNI\"], Literal[\"GVT_BUND\"],
     Literal[\"SWAP\"], Literal[\"SWAP_RFR\"], Literal[\"SWAP_MUNI\"]"""
    currency: Optional[str] = rest_field()
    cds_ticker: Optional[str] = rest_field(name="cdsTicker")
    expand_curve: Optional[bool] = rest_field(name="expandCurve")
    pricing_date: Optional[datetime.date] = rest_field(name="pricingDate")
    show_spot_rate: Optional[bool] = rest_field(name="showSpotRate")
    show_forward_rate: Optional[bool] = rest_field(name="showForwardRate")
    show_discount_factor: Optional[bool] = rest_field(name="showDiscountFactor")
    forward_period: Optional[float] = rest_field(name="forwardPeriod")
    implied_forward_delay: Optional[float] = rest_field(name="impliedForwardDelay")
    index: Optional[str] = rest_field()
    use_live_curve: Optional[bool] = rest_field(name="useLiveCurve")

    @overload
    def __init__(
        self,
        *,
        curve_id: Optional[str] = None,
        curve_type: Optional[
            Literal[
                "GVT", "GVT_TSYM", "GVT_TSYM_MUNI", "GVT_AGN", "GVT_MUNI", "GVT_BUND", "SWAP", "SWAP_RFR", "SWAP_MUNI"
            ]
        ] = None,
        currency: Optional[str] = None,
        cds_ticker: Optional[str] = None,
        expand_curve: Optional[bool] = None,
        pricing_date: Optional[datetime.date] = None,
        show_spot_rate: Optional[bool] = None,
        show_forward_rate: Optional[bool] = None,
        show_discount_factor: Optional[bool] = None,
        forward_period: Optional[float] = None,
        implied_forward_delay: Optional[float] = None,
        index: Optional[str] = None,
        use_live_curve: Optional[bool] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CurveTypeAndCurrency(_model_base.Model):
    """CurveTypeAndCurrency.

    Attributes
    ----------
    curve_type : str
        Is one of the following types: Literal["GVT"], Literal["GVT_TSYM"],
        Literal["GVT_TSYM_MUNI"], Literal["GVT_AGN"], Literal["GVT_MUNI"],
        Literal["GVT_BUND"], Literal["SWAP"], Literal["SWAP_RFR"],
        Literal["SWAP_MUNI"]
    currency : str
        Currency of the curveType.
    retrieve_curve : bool
        Return curve rates as part of the response.
    user_defined : ~analyticsapi.models.JsonRef
        Optional. Reference to user defined curve. This can either be request
        id or name associated with the user defined object.
    snapshot : str
        Is either a Literal["FOUR_PM"] type or a Literal["EOD"] type.
    """

    curve_type: Optional[
        Literal["GVT", "GVT_TSYM", "GVT_TSYM_MUNI", "GVT_AGN", "GVT_MUNI", "GVT_BUND", "SWAP", "SWAP_RFR", "SWAP_MUNI"]
    ] = rest_field(name="curveType")
    """Is one of the following types: Literal[\"GVT\"], Literal[\"GVT_TSYM\"],
     Literal[\"GVT_TSYM_MUNI\"], Literal[\"GVT_AGN\"], Literal[\"GVT_MUNI\"], Literal[\"GVT_BUND\"],
     Literal[\"SWAP\"], Literal[\"SWAP_RFR\"], Literal[\"SWAP_MUNI\"]"""
    currency: Optional[str] = rest_field()
    """Currency of the curveType."""
    retrieve_curve: Optional[bool] = rest_field(name="retrieveCurve")
    """Return curve rates as part of the response."""
    user_defined: Optional["_models.JsonRef"] = rest_field(name="userDefined")
    """Optional. Reference to user defined curve. This can either be request id or name associated
     with the user defined object."""
    snapshot: Optional[Literal["FOUR_PM", "EOD"]] = rest_field()
    """Is either a Literal[\"FOUR_PM\"] type or a Literal[\"EOD\"] type."""

    @overload
    def __init__(
        self,
        *,
        curve_type: Optional[
            Literal[
                "GVT", "GVT_TSYM", "GVT_TSYM_MUNI", "GVT_AGN", "GVT_MUNI", "GVT_BUND", "SWAP", "SWAP_RFR", "SWAP_MUNI"
            ]
        ] = None,
        currency: Optional[str] = None,
        retrieve_curve: Optional[bool] = None,
        user_defined: Optional["_models.JsonRef"] = None,
        snapshot: Optional[Literal["FOUR_PM", "EOD"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class CustomScenario(_model_base.Model):
    """CustomScenario.

    Attributes
    ----------
    assume_call : bool
        Applicable for CMBS with a clean up call. If true, remaining balance is
        called once clean up call threshold is reached.
    delay : bool
        If true, prepay and default rates are delayed until the first payment
        the bondholder is entitled to receive. If false, rates apply at the
        first payment, regardless if the bondholder is entitled to receive it.
        Greatly impacts IOs.
    delay_balloon_maturity : bool
        If true, deals where the scheduled balloon payment occurs in the month
        prior to the settlement date, users can delay the maturity by one month
        to prevent pricing errors.
    defeasance : str
        Set collateral defeasance assumption. Is one of the following types:
        Literal["AUTO"], Literal["OPEN"], Literal["MATURITY"]
    prepayment : ~analyticsapi.models.CmbsPrepayment
    defaults : ~analyticsapi.models.Balloon
    balloon_extend : ~analyticsapi.models.Balloon
    balloon_default : ~analyticsapi.models.Balloon
    """

    assume_call: Optional[bool] = rest_field(name="assumeCall")
    """Applicable for CMBS with a clean up call. If true, remaining balance is called once clean up
     call threshold is reached."""
    delay: Optional[bool] = rest_field()
    """If true, prepay and default rates are delayed until the first payment the bondholder is
     entitled to receive. If false, rates apply at the first payment, regardless if the bondholder
     is entitled to receive it. Greatly impacts IOs."""
    delay_balloon_maturity: Optional[bool] = rest_field(name="delayBalloonMaturity")
    """If true, deals where the scheduled balloon payment occurs in the month prior to the settlement
     date, users can delay the maturity by one month to prevent pricing errors."""
    defeasance: Optional[Literal["AUTO", "OPEN", "MATURITY"]] = rest_field()
    """Set collateral defeasance assumption. Is one of the following types: Literal[\"AUTO\"],
     Literal[\"OPEN\"], Literal[\"MATURITY\"]"""
    prepayment: Optional["_models.CmbsPrepayment"] = rest_field()
    defaults: Optional["_models.Balloon"] = rest_field()
    balloon_extend: Optional["_models.Balloon"] = rest_field(name="balloonExtend")
    balloon_default: Optional["_models.Balloon"] = rest_field(name="balloonDefault")

    @overload
    def __init__(
        self,
        *,
        assume_call: Optional[bool] = None,
        delay: Optional[bool] = None,
        delay_balloon_maturity: Optional[bool] = None,
        defeasance: Optional[Literal["AUTO", "OPEN", "MATURITY"]] = None,
        prepayment: Optional["_models.CmbsPrepayment"] = None,
        defaults: Optional["_models.Balloon"] = None,
        balloon_extend: Optional["_models.Balloon"] = None,
        balloon_default: Optional["_models.Balloon"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class DataTable(_model_base.Model):
    """DataTable.

    Attributes
    ----------
    column_details : list[~analyticsapi.models.DataTableColumnDetail]
        The default value is None, needs to be assigned before using.
    data : list[dict[str, any]]
        The default value is None, needs to be assigned before using.
    """

    column_details: Optional[List["_models.DataTableColumnDetail"]] = rest_field(name="columnDetails")
    data: Optional[List[Dict[str, Any]]] = rest_field()

    @overload
    def __init__(
        self,
        *,
        column_details: Optional[List["_models.DataTableColumnDetail"]] = None,
        data: Optional[List[Dict[str, Any]]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class DataTableColumnDetail(_model_base.Model):
    """DataTableColumnDetail.

    Attributes
    ----------
    header : str
    field : str
    format : str
    """

    header: Optional[str] = rest_field()
    field: Optional[str] = rest_field()
    format: Optional[str] = rest_field()

    @overload
    def __init__(
        self,
        *,
        header: Optional[str] = None,
        field: Optional[str] = None,
        format: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class DatedRate(_model_base.Model):
    """An object that defines the effective date for the associated rate.

    Attributes
    ----------
    date : ~datetime.date
        The effective date of the associated rate. The value is expressed in
        ISO 8601 format: YYYY-MM-DD (e.g., '2021-01-01').
    rate : ~analyticsapi.models.Rate
        An object that defines the rate value that becomes effective on the
        associated date. Required.
    """

    date: Optional[datetime.date] = rest_field()
    """The effective date of the associated rate. The value is expressed in ISO 8601 format:
     YYYY-MM-DD (e.g., '2021-01-01')."""
    rate: "_models.Rate" = rest_field()
    """An object that defines the rate value that becomes effective on the associated date. Required."""

    @overload
    def __init__(
        self,
        *,
        rate: "_models.Rate",
        date: Optional[datetime.date] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class DatedValue(_model_base.Model):
    """An object that defines a date-value pair.

    Attributes
    ----------
    date : ~datetime.date
        The effective date of the associated value. The value is expressed in
        ISO 8601 format: YYYY-MM-DD (e.g., 2021-01-01). Required.
    value : float
        The value that becomes effective on the associated date. Required.
    """

    date: datetime.date = rest_field()
    """The effective date of the associated value. The value is expressed in ISO 8601 format:
     YYYY-MM-DD (e.g., 2021-01-01). Required."""
    value: float = rest_field()
    """The value that becomes effective on the associated date. Required."""

    @overload
    def __init__(
        self,
        *,
        date: datetime.date,
        value: float,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class DefaultDials(_model_base.Model):  # pylint: disable=too-many-instance-attributes
    """DefaultDials.

    Attributes
    ----------
    prepayment_decay : ~decimal.Decimal
    credit_score_base : ~decimal.Decimal
    credit_score_slope : ~decimal.Decimal
    loan_to_value_base : ~decimal.Decimal
    loan_to_value_slope : ~decimal.Decimal
    loan_size_base : ~decimal.Decimal
    loan_size_slope : ~decimal.Decimal
    arm_spike_height : ~decimal.Decimal
    arm_spike_length : ~decimal.Decimal
    io_spike_height : ~decimal.Decimal
    io_spike_length : ~decimal.Decimal
    io_spike_elbow : ~decimal.Decimal
    turnover_multiplier : ~analyticsapi.models.ScalarAndVectorWithCollateral
    refi_multiplier : ~analyticsapi.models.ScalarAndVectorWithCollateral
    refi_elbow_shift : ~analyticsapi.models.ScalarAndVectorWithCollateral
    default_multiplier : ~analyticsapi.models.ScalarAndVectorWithCollateral
    curtailment_multiplier : ~analyticsapi.models.ScalarAndVectorWithCollateral
    sato_elbow_shift_multiplier : ~analyticsapi.models.ScalarAndVectorWithCollateral
    turnover_seasoning : ~analyticsapi.models.ScalarAndVector
    turnover_lockin : ~analyticsapi.models.ScalarAndVector
    refi_curve_steepness : ~analyticsapi.models.ScalarAndVector
    refi_burnout : ~analyticsapi.models.ScalarAndVector
    refi_seasoning : ~analyticsapi.models.ScalarAndVector
    refi_media_effect : ~analyticsapi.models.ScalarAndVector
    cashouts : ~analyticsapi.models.ScalarAndVector
    agency_eligibility : ~analyticsapi.models.ScalarAndVector
    ps_spread_shift : ~analyticsapi.models.ScalarAndVector
    ps_spread_steepness : ~analyticsapi.models.ScalarAndVector
    ps_spread_rate : ~analyticsapi.models.ScalarAndVector
    ps_spread_floor : ~analyticsapi.models.ScalarAndVector
    refi_capacity_constraint : ~analyticsapi.models.ScalarAndVector
    refi_fha_to_conventional : ~analyticsapi.models.ScalarAndVector
    upfront_mortgage_insurance_premium : ~analyticsapi.models.ScalarAndVector
    annual_mortgage_insurance_premium : ~analyticsapi.models.ScalarAndVector
    broker_costs : ~analyticsapi.models.ScalarAndVector
    broker_response : ~analyticsapi.models.ScalarAndVector
    broker_intensity : ~analyticsapi.models.ScalarAndVector
    broker_refi_ramp : ~analyticsapi.models.ScalarAndVector
    correspondent_costs : ~analyticsapi.models.ScalarAndVector
    correspondent_response : ~analyticsapi.models.ScalarAndVector
    correspondent_intensity : ~analyticsapi.models.ScalarAndVector
    correspondent_refi_ramp : ~analyticsapi.models.ScalarAndVector
    retail_costs : ~analyticsapi.models.ScalarAndVector
    retail_response : ~analyticsapi.models.ScalarAndVector
    retail_intensity : ~analyticsapi.models.ScalarAndVector
    retail_refi_ramp : ~analyticsapi.models.ScalarAndVector
    online_refi_multiplier : ~analyticsapi.models.ScalarAndVector
    prepay_vector_shift : ~analyticsapi.models.ScalarAndVector
    cash_window_s_curve_multiplier : ~analyticsapi.models.ScalarAndVector
    cash_window_s_curve_slope : ~analyticsapi.models.ScalarAndVector
    cash_window_s_curve_elbow_shift : ~analyticsapi.models.ScalarAndVector
    sato_elbow_shift_age_decay_multiplier : ~analyticsapi.models.ScalarAndVector
    property_inspection_waiver_multiplier : ~analyticsapi.models.ScalarAndVector
    """

    prepayment_decay: Optional[decimal.Decimal] = rest_field(name="prepaymentDecay")
    credit_score_base: Optional[decimal.Decimal] = rest_field(name="creditScoreBase")
    credit_score_slope: Optional[decimal.Decimal] = rest_field(name="creditScoreSlope")
    loan_to_value_base: Optional[decimal.Decimal] = rest_field(name="loanToValueBase")
    loan_to_value_slope: Optional[decimal.Decimal] = rest_field(name="loanToValueSlope")
    loan_size_base: Optional[decimal.Decimal] = rest_field(name="loanSizeBase")
    loan_size_slope: Optional[decimal.Decimal] = rest_field(name="loanSizeSlope")
    arm_spike_height: Optional[decimal.Decimal] = rest_field(name="armSpikeHeight")
    arm_spike_length: Optional[decimal.Decimal] = rest_field(name="armSpikeLength")
    io_spike_height: Optional[decimal.Decimal] = rest_field(name="ioSpikeHeight")
    io_spike_length: Optional[decimal.Decimal] = rest_field(name="ioSpikeLength")
    io_spike_elbow: Optional[decimal.Decimal] = rest_field(name="ioSpikeElbow")
    turnover_multiplier: Optional["_models.ScalarAndVectorWithCollateral"] = rest_field(name="turnoverMultiplier")
    refi_multiplier: Optional["_models.ScalarAndVectorWithCollateral"] = rest_field(name="refiMultiplier")
    refi_elbow_shift: Optional["_models.ScalarAndVectorWithCollateral"] = rest_field(name="refiElbowShift")
    default_multiplier: Optional["_models.ScalarAndVectorWithCollateral"] = rest_field(name="defaultMultiplier")
    curtailment_multiplier: Optional["_models.ScalarAndVectorWithCollateral"] = rest_field(name="curtailmentMultiplier")
    sato_elbow_shift_multiplier: Optional["_models.ScalarAndVectorWithCollateral"] = rest_field(
        name="satoElbowShiftMultiplier"
    )
    turnover_seasoning: Optional["_models.ScalarAndVector"] = rest_field(name="turnoverSeasoning")
    turnover_lockin: Optional["_models.ScalarAndVector"] = rest_field(name="turnoverLockin")
    refi_curve_steepness: Optional["_models.ScalarAndVector"] = rest_field(name="refiCurveSteepness")
    refi_burnout: Optional["_models.ScalarAndVector"] = rest_field(name="refiBurnout")
    refi_seasoning: Optional["_models.ScalarAndVector"] = rest_field(name="refiSeasoning")
    refi_media_effect: Optional["_models.ScalarAndVector"] = rest_field(name="refiMediaEffect")
    cashouts: Optional["_models.ScalarAndVector"] = rest_field()
    agency_eligibility: Optional["_models.ScalarAndVector"] = rest_field(name="agencyEligibility")
    ps_spread_shift: Optional["_models.ScalarAndVector"] = rest_field(name="psSpreadShift")
    ps_spread_steepness: Optional["_models.ScalarAndVector"] = rest_field(name="psSpreadSteepness")
    ps_spread_rate: Optional["_models.ScalarAndVector"] = rest_field(name="psSpreadRate")
    ps_spread_floor: Optional["_models.ScalarAndVector"] = rest_field(name="psSpreadFloor")
    refi_capacity_constraint: Optional["_models.ScalarAndVector"] = rest_field(name="refiCapacityConstraint")
    refi_fha_to_conventional: Optional["_models.ScalarAndVector"] = rest_field(name="refiFHAToConventional")
    upfront_mortgage_insurance_premium: Optional["_models.ScalarAndVector"] = rest_field(
        name="upfrontMortgageInsurancePremium"
    )
    annual_mortgage_insurance_premium: Optional["_models.ScalarAndVector"] = rest_field(
        name="annualMortgageInsurancePremium"
    )
    broker_costs: Optional["_models.ScalarAndVector"] = rest_field(name="brokerCosts")
    broker_response: Optional["_models.ScalarAndVector"] = rest_field(name="brokerResponse")
    broker_intensity: Optional["_models.ScalarAndVector"] = rest_field(name="brokerIntensity")
    broker_refi_ramp: Optional["_models.ScalarAndVector"] = rest_field(name="brokerRefiRamp")
    correspondent_costs: Optional["_models.ScalarAndVector"] = rest_field(name="correspondentCosts")
    correspondent_response: Optional["_models.ScalarAndVector"] = rest_field(name="correspondentResponse")
    correspondent_intensity: Optional["_models.ScalarAndVector"] = rest_field(name="correspondentIntensity")
    correspondent_refi_ramp: Optional["_models.ScalarAndVector"] = rest_field(name="correspondentRefiRamp")
    retail_costs: Optional["_models.ScalarAndVector"] = rest_field(name="retailCosts")
    retail_response: Optional["_models.ScalarAndVector"] = rest_field(name="retailResponse")
    retail_intensity: Optional["_models.ScalarAndVector"] = rest_field(name="retailIntensity")
    retail_refi_ramp: Optional["_models.ScalarAndVector"] = rest_field(name="retailRefiRamp")
    online_refi_multiplier: Optional["_models.ScalarAndVector"] = rest_field(name="onlineRefiMultiplier")
    prepay_vector_shift: Optional["_models.ScalarAndVector"] = rest_field(name="prepayVectorShift")
    cash_window_s_curve_multiplier: Optional["_models.ScalarAndVector"] = rest_field(name="cashWindowSCurveMultiplier")
    cash_window_s_curve_slope: Optional["_models.ScalarAndVector"] = rest_field(name="cashWindowSCurveSlope")
    cash_window_s_curve_elbow_shift: Optional["_models.ScalarAndVector"] = rest_field(name="cashWindowSCurveElbowShift")
    sato_elbow_shift_age_decay_multiplier: Optional["_models.ScalarAndVector"] = rest_field(
        name="satoElbowShiftAgeDecayMultiplier"
    )
    property_inspection_waiver_multiplier: Optional["_models.ScalarAndVector"] = rest_field(
        name="propertyInspectionWaiverMultiplier"
    )

    @overload
    def __init__(
        self,
        *,
        prepayment_decay: Optional[decimal.Decimal] = None,
        credit_score_base: Optional[decimal.Decimal] = None,
        credit_score_slope: Optional[decimal.Decimal] = None,
        loan_to_value_base: Optional[decimal.Decimal] = None,
        loan_to_value_slope: Optional[decimal.Decimal] = None,
        loan_size_base: Optional[decimal.Decimal] = None,
        loan_size_slope: Optional[decimal.Decimal] = None,
        arm_spike_height: Optional[decimal.Decimal] = None,
        arm_spike_length: Optional[decimal.Decimal] = None,
        io_spike_height: Optional[decimal.Decimal] = None,
        io_spike_length: Optional[decimal.Decimal] = None,
        io_spike_elbow: Optional[decimal.Decimal] = None,
        turnover_multiplier: Optional["_models.ScalarAndVectorWithCollateral"] = None,
        refi_multiplier: Optional["_models.ScalarAndVectorWithCollateral"] = None,
        refi_elbow_shift: Optional["_models.ScalarAndVectorWithCollateral"] = None,
        default_multiplier: Optional["_models.ScalarAndVectorWithCollateral"] = None,
        curtailment_multiplier: Optional["_models.ScalarAndVectorWithCollateral"] = None,
        sato_elbow_shift_multiplier: Optional["_models.ScalarAndVectorWithCollateral"] = None,
        turnover_seasoning: Optional["_models.ScalarAndVector"] = None,
        turnover_lockin: Optional["_models.ScalarAndVector"] = None,
        refi_curve_steepness: Optional["_models.ScalarAndVector"] = None,
        refi_burnout: Optional["_models.ScalarAndVector"] = None,
        refi_seasoning: Optional["_models.ScalarAndVector"] = None,
        refi_media_effect: Optional["_models.ScalarAndVector"] = None,
        cashouts: Optional["_models.ScalarAndVector"] = None,
        agency_eligibility: Optional["_models.ScalarAndVector"] = None,
        ps_spread_shift: Optional["_models.ScalarAndVector"] = None,
        ps_spread_steepness: Optional["_models.ScalarAndVector"] = None,
        ps_spread_rate: Optional["_models.ScalarAndVector"] = None,
        ps_spread_floor: Optional["_models.ScalarAndVector"] = None,
        refi_capacity_constraint: Optional["_models.ScalarAndVector"] = None,
        refi_fha_to_conventional: Optional["_models.ScalarAndVector"] = None,
        upfront_mortgage_insurance_premium: Optional["_models.ScalarAndVector"] = None,
        annual_mortgage_insurance_premium: Optional["_models.ScalarAndVector"] = None,
        broker_costs: Optional["_models.ScalarAndVector"] = None,
        broker_response: Optional["_models.ScalarAndVector"] = None,
        broker_intensity: Optional["_models.ScalarAndVector"] = None,
        broker_refi_ramp: Optional["_models.ScalarAndVector"] = None,
        correspondent_costs: Optional["_models.ScalarAndVector"] = None,
        correspondent_response: Optional["_models.ScalarAndVector"] = None,
        correspondent_intensity: Optional["_models.ScalarAndVector"] = None,
        correspondent_refi_ramp: Optional["_models.ScalarAndVector"] = None,
        retail_costs: Optional["_models.ScalarAndVector"] = None,
        retail_response: Optional["_models.ScalarAndVector"] = None,
        retail_intensity: Optional["_models.ScalarAndVector"] = None,
        retail_refi_ramp: Optional["_models.ScalarAndVector"] = None,
        online_refi_multiplier: Optional["_models.ScalarAndVector"] = None,
        prepay_vector_shift: Optional["_models.ScalarAndVector"] = None,
        cash_window_s_curve_multiplier: Optional["_models.ScalarAndVector"] = None,
        cash_window_s_curve_slope: Optional["_models.ScalarAndVector"] = None,
        cash_window_s_curve_elbow_shift: Optional["_models.ScalarAndVector"] = None,
        sato_elbow_shift_age_decay_multiplier: Optional["_models.ScalarAndVector"] = None,
        property_inspection_waiver_multiplier: Optional["_models.ScalarAndVector"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class DepositConstituentDefinition(_model_base.Model):
    """An object to define the deposit instrument used as a constituent.

    Attributes
    ----------
    tenor : str
        The code indicating the tenor of the instrument used as a constituent
        (e.g., '1M', '1Y'). Required.
    template : str
        A pre-defined template can be used as an input by the user. It is the
        currency code of the constituent.
    """

    tenor: str = rest_field()
    """The code indicating the tenor of the instrument used as a constituent (e.g., '1M', '1Y').
     Required."""
    template: Optional[str] = rest_field()
    """A pre-defined template can be used as an input by the user. It is the currency code of the
     constituent."""

    @overload
    def __init__(
        self,
        *,
        tenor: str,
        template: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class SingleInterestRatePaymentDefinition(_model_base.Model):
    """An object that defines the single interest rate payment (e.g., on a term deposit).

    Attributes
    ----------
    notional : ~analyticsapi.models.Amount
        An object that defines the notional amount of the instrument. Required.
    rate : ~analyticsapi.models.InterestRateDefinition
        An object that defines the rate. Required.
    start_date : ~analyticsapi.models.Date
        An object that defines the start date of the interest payment period.
        Required.
    end_date : ~analyticsapi.models.Date
        An object that defines the end date of the interest payment period.
        Required.
    payment_offset : ~analyticsapi.models.OffsetDefinition
        An object that defines how the payment dates are derived from the
        interest period dates.
    settlement_type : str or ~analyticsapi.models.SettlementType
        An indicator that specifies how the payment is settled (e.g.,
        'Physical', 'Cash'). Known values are: "Cash" and "Physical".
    """

    notional: "_models.Amount" = rest_field()
    """An object that defines the notional amount of the instrument. Required."""
    rate: "_models.InterestRateDefinition" = rest_field()
    """An object that defines the rate. Required."""
    start_date: "_models.Date" = rest_field(name="startDate")
    """An object that defines the start date of the interest payment period. Required."""
    end_date: "_models.Date" = rest_field(name="endDate")
    """An object that defines the end date of the interest payment period. Required."""
    payment_offset: Optional["_models.OffsetDefinition"] = rest_field(name="paymentOffset")
    """An object that defines how the payment dates are derived from the interest period dates."""
    settlement_type: Optional[Union[str, "_models.SettlementType"]] = rest_field(name="settlementType")
    """An indicator that specifies how the payment is settled (e.g., 'Physical', 'Cash'). Known values
     are: \"Cash\" and \"Physical\"."""

    @overload
    def __init__(
        self,
        *,
        notional: "_models.Amount",
        rate: "_models.InterestRateDefinition",
        start_date: "_models.Date",
        end_date: "_models.Date",
        payment_offset: Optional["_models.OffsetDefinition"] = None,
        settlement_type: Optional[Union[str, "_models.SettlementType"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class DepositDefinition(SingleInterestRatePaymentDefinition):
    """DepositDefinition.

    Attributes
    ----------
    notional : ~analyticsapi.models.Amount
        An object that defines the notional amount of the instrument. Required.
    rate : ~analyticsapi.models.InterestRateDefinition
        An object that defines the rate. Required.
    start_date : ~analyticsapi.models.Date
        An object that defines the start date of the interest payment period.
        Required.
    end_date : ~analyticsapi.models.Date
        An object that defines the end date of the interest payment period.
        Required.
    payment_offset : ~analyticsapi.models.OffsetDefinition
        An object that defines how the payment dates are derived from the
        interest period dates.
    settlement_type : str or ~analyticsapi.models.SettlementType
        An indicator that specifies how the payment is settled (e.g.,
        'Physical', 'Cash'). Known values are: "Cash" and "Physical".
    """

    @overload
    def __init__(
        self,
        *,
        notional: "_models.Amount",
        rate: "_models.InterestRateDefinition",
        start_date: "_models.Date",
        end_date: "_models.Date",
        payment_offset: Optional["_models.OffsetDefinition"] = None,
        settlement_type: Optional[Union[str, "_models.SettlementType"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class DepositDefinitionTemplate(InstrumentTemplateDefinition, discriminator="Deposit"):
    """DepositDefinitionTemplate.

    Attributes
    ----------
    instrument_type : str or ~analyticsapi.models.DEPOSIT
        Required. An interest rate deposit contract.
    template : ~analyticsapi.models.DepositDefinition
        Required.
    """

    instrument_type: Literal[InstrumentTemplateTypeEnum.DEPOSIT] = rest_discriminator(name="instrumentType")  # type: ignore
    """Required. An interest rate deposit contract."""
    template: "_models.DepositDefinition" = rest_field()
    """Required."""

    @overload
    def __init__(
        self,
        template: "_models.DepositDefinition",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, instrument_type=InstrumentTemplateTypeEnum.DEPOSIT, **kwargs)


class DepositFxConstituent(FxConstituent, discriminator="Deposit"):
    """An object to define constituents that are used to construct the curve.

    Readonly variables are only populated by the server, and will be ignored when sending a request.

    Attributes
    ----------
    quote : ~analyticsapi.models.Quote
        An object to define the quote of the instrument used as a constituent.
    status : list[str]
        A message is returned if the constituent cannot be identified, or
        access for a user to the instrument used as a constituent is denied.
    type : str or ~analyticsapi.models.DEPOSIT
        The type of the instrument used as a constituent. Required.
    definition : ~analyticsapi.models.DepositConstituentDefinition
        An object to define the instrument used as a constituent.
    """

    type: Literal[FxConstituentEnum.DEPOSIT] = rest_discriminator(name="type")  # type: ignore
    """The type of the instrument used as a constituent. Required."""
    definition: Optional["_models.DepositConstituentDefinition"] = rest_field()
    """An object to define the instrument used as a constituent."""

    @overload
    def __init__(
        self,
        *,
        quote: Optional["_models.Quote"] = None,
        definition: Optional["_models.DepositConstituentDefinition"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, type=FxConstituentEnum.DEPOSIT, **kwargs)


class Description(_model_base.Model):
    """Description.

    Attributes
    ----------
    summary : str
        A summary of information about the resource. Limited to 500 characters.
    tags : list[str]
        User-defined tags to identify the resource. Limited to 5 items of up to
        50 characters each. To change the tags, reassign the new tag list, e.g.
        my_curve.description.tags = new_tags. Direct operation on the tag list
        using append, remove, etc., e.g.
        my_curve.description.tags.remove('tag_1'), will not change the actual
        tag list of the Description object.  The default value is None, needs
        to be assigned before using.
    """

    summary: Optional[str] = rest_field()
    """A summary of information about the resource. Limited to 500 characters."""
    tags: Optional[List[str]] = rest_field()
    """User-defined tags to identify the resource. Limited to 5 items of up to 50 characters each.
     To change the tags, reassign the new tag list, e.g. my_curve.description.tags = new_tags.
     Direct operation on the tag list using append, remove, etc., e.g.
     my_curve.description.tags.remove('tag_1'), will not change the actual tag list of the
     Description object."""

    @overload
    def __init__(
        self,
        *,
        summary: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class Distribution(_model_base.Model):
    """Distribution.

    Attributes
    ----------
    state : dict[str, ~decimal.Decimal]
    servicer : dict[str, ~decimal.Decimal]
    """

    state: Optional[Dict[str, decimal.Decimal]] = rest_field()
    servicer: Optional[Dict[str, decimal.Decimal]] = rest_field()

    @overload
    def __init__(
        self,
        *,
        state: Optional[Dict[str, decimal.Decimal]] = None,
        servicer: Optional[Dict[str, decimal.Decimal]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class DividendCurve(Curve, discriminator="DividendCurve"):
    """The model defining the output of dividend curve calculation.

    Attributes
    ----------
    curve_type : str or ~analyticsapi.models.DIVIDEND_CURVE
        Required.
    points : list[~analyticsapi.models.DividendCurvePoint]
        The list of output points. Required.  The default value is None, needs
        to be assigned before using.
    """

    curve_type: Literal[CurveTypeEnum.DIVIDEND_CURVE] = rest_discriminator(name="curveType")  # type: ignore
    """Required."""
    points: List["_models.DividendCurvePoint"] = rest_field()
    """The list of output points. Required."""

    @overload
    def __init__(
        self,
        points: List["_models.DividendCurvePoint"],
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, curve_type=CurveTypeEnum.DIVIDEND_CURVE, **kwargs)


class DividendCurvePoint(_model_base.Model):
    """An object that contains the values applied to the dividend curve point.

    Attributes
    ----------
    ex_dividend_date : ~datetime.date
        The ex-dividend date. Required.
    payment_date : ~datetime.date
        The dividend payment date. Required.
    amount : ~analyticsapi.models.Amount
        The dividend amount. Required.
    yield_property : float
        The dividend expressed as percent. Required.
    """

    ex_dividend_date: datetime.date = rest_field(name="exDividendDate")
    """The ex-dividend date. Required."""
    payment_date: datetime.date = rest_field(name="paymentDate")
    """The dividend payment date. Required."""
    amount: "_models.Amount" = rest_field()
    """The dividend amount. Required."""
    yield_property: float = rest_field(name="yield")
    """The dividend expressed as percent. Required."""

    @overload
    def __init__(
        self,
        *,
        ex_dividend_date: datetime.date,
        payment_date: datetime.date,
        amount: "_models.Amount",
        yield_property: float,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class DoubleBarrierOtcOptionTemplate(InstrumentTemplateDefinition, discriminator="DoubleBarrierOtcOption"):
    """DoubleBarrierOtcOptionTemplate.

    Attributes
    ----------
    instrument_type : str or ~analyticsapi.models.DOUBLE_BARRIER_OTC_OPTION
        Required. Double Barrier OTC Option contract.
    template : ~analyticsapi.models.OptionDefinition
        Required.
    """

    instrument_type: Literal[InstrumentTemplateTypeEnum.DOUBLE_BARRIER_OTC_OPTION] = rest_discriminator(name="instrumentType")  # type: ignore
    """Required. Double Barrier OTC Option contract."""
    template: "_models.OptionDefinition" = rest_field()
    """Required."""

    @overload
    def __init__(
        self,
        template: "_models.OptionDefinition",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, instrument_type=InstrumentTemplateTypeEnum.DOUBLE_BARRIER_OTC_OPTION, **kwargs)


class DoubleBinaryOtcOptionTemplate(InstrumentTemplateDefinition, discriminator="DoubleBinaryOtcOption"):
    """DoubleBinaryOtcOptionTemplate.

    Attributes
    ----------
    instrument_type : str or ~analyticsapi.models.DOUBLE_BINARY_OTC_OPTION
        Required. Double Binary OTC Option contract.
    template : ~analyticsapi.models.OptionDefinition
        Required.
    """

    instrument_type: Literal[InstrumentTemplateTypeEnum.DOUBLE_BINARY_OTC_OPTION] = rest_discriminator(name="instrumentType")  # type: ignore
    """Required. Double Binary OTC Option contract."""
    template: "_models.OptionDefinition" = rest_field()
    """Required."""

    @overload
    def __init__(
        self,
        template: "_models.OptionDefinition",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, instrument_type=InstrumentTemplateTypeEnum.DOUBLE_BINARY_OTC_OPTION, **kwargs)


class Duration(ABC, _model_base.Model):
    """An object to determine the duration of the holiday.

    You probably want to use the sub-classes and not this class directly. Known sub-classes are:
    FullDayDuration, HalfDayDuration

    Attributes
    ----------
    duration_type : str or ~analyticsapi.models.DurationType
        The type of the holiday duration. Possible values are: FullDayDuration
        or HalfDayDuration. Required. Known values are: "FullDayDuration" and
        "HalfDayDuration".
    """

    __mapping__: Dict[str, _model_base.Model] = {}
    duration_type: str = rest_discriminator(name="durationType")
    """The type of the holiday duration. Possible values are: FullDayDuration or HalfDayDuration.
     Required. Known values are: \"FullDayDuration\" and \"HalfDayDuration\"."""

    @overload
    def __init__(
        self,
        duration_type: str,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["duration_type"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class EqOptionVolSurfaceChoice(_model_base.Model):
    """The object to provide either a reference to an equity volatility surface stored in the platform
    or 3rd party volatilities.

    Attributes
    ----------
    reference : str
        The reference to a volatility surface stored in the platform.
    surface : ~analyticsapi.models.EqVolSurfaceInput
        The volatility surface data.
    """

    reference: Optional[str] = rest_field()
    """The reference to a volatility surface stored in the platform."""
    surface: Optional["_models.EqVolSurfaceInput"] = rest_field()
    """The volatility surface data."""

    @overload
    def __init__(
        self,
        *,
        reference: Optional[str] = None,
        surface: Optional["_models.EqVolSurfaceInput"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class EqVolSurfaceInput(_model_base.Model):
    """The object defining the 3rd party equity volatility surface.

    Attributes
    ----------
    strike_type : str or ~analyticsapi.models.StrikeTypeEnum
        The property that defines the type of the strikes provided in the
        surface points. Required. Known values are: "Absolute", "BasisPoint",
        "Delta", "Moneyness", "Percent", and "Relative".
    model_type : str or ~analyticsapi.models.VolModelTypeEnum
        The property that defines the type of the model (Normal or LogNormal)
        of the volatilities provided in the surface points. Required. Known
        values are: "Normal" and "LogNormal".
    points : list[~analyticsapi.models.VolSurfacePoint]
        The list of volatility points. Required.  The default value is None,
        needs to be assigned before using.
    entity_code : str
        The code of the reference entity. Required.
    """

    strike_type: Union[str, "_models.StrikeTypeEnum"] = rest_field(name="strikeType")
    """The property that defines the type of the strikes provided in the surface points. Required.
     Known values are: \"Absolute\", \"BasisPoint\", \"Delta\", \"Moneyness\", \"Percent\", and
     \"Relative\"."""
    model_type: Union[str, "_models.VolModelTypeEnum"] = rest_field(name="modelType")
    """The property that defines the type of the model (Normal or LogNormal) of the volatilities
     provided in the surface points. Required. Known values are: \"Normal\" and \"LogNormal\"."""
    points: List["_models.VolSurfacePoint"] = rest_field()
    """The list of volatility points. Required."""
    entity_code: str = rest_field(name="entityCode")
    """The code of the reference entity. Required."""

    @overload
    def __init__(
        self,
        *,
        strike_type: Union[str, "_models.StrikeTypeEnum"],
        model_type: Union[str, "_models.VolModelTypeEnum"],
        points: List["_models.VolSurfacePoint"],
        entity_code: str,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ExerciseDefinition(_model_base.Model):
    """An object that defines the exercise settings of an option instrument.

    Attributes
    ----------
    strike : float
        The set price at which the option holder can buy or sell the underlying
        asset. The value is expressed according to the market convention linked
        to the underlying asset. Required.
    schedule : ~analyticsapi.models.ScheduleDefinition
        An object that defines the exercise schedule of an option instrument.
    exercise_style : str or ~analyticsapi.models.ExerciseStyleEnum
        The style of an option instrument based on its exercise restrictions.
        Note that all exercise styles may not apply to certain types of option
        instruments. Known values are: "European", "American", and "Bermudan".
    """

    strike: float = rest_field()
    """The set price at which the option holder can buy or sell the underlying asset. The value is
     expressed according to the market convention linked to the underlying asset. Required."""
    schedule: Optional["_models.ScheduleDefinition"] = rest_field()
    """An object that defines the exercise schedule of an option instrument."""
    exercise_style: Optional[Union[str, "_models.ExerciseStyleEnum"]] = rest_field(name="exerciseStyle")
    """The style of an option instrument based on its exercise restrictions. Note that all exercise
     styles may not apply to certain types of option instruments. Known values are: \"European\",
     \"American\", and \"Bermudan\"."""

    @overload
    def __init__(
        self,
        *,
        strike: float,
        schedule: Optional["_models.ScheduleDefinition"] = None,
        exercise_style: Optional[Union[str, "_models.ExerciseStyleEnum"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ExtraSettings(_model_base.Model):  # pylint: disable=too-many-instance-attributes
    """ExtraSettings.

    Attributes
    ----------
    include_partials : bool
        Optional additional pricing settings.
    option_model : str or ~analyticsapi.models.OptionModel
        OASEDUR is recommended, returns OAS and option adjusted measures. OAS
        returns CMO OAS only. Known values are: "OAS", "OASEDUR", and
        "YCMARGIN".
    use_oas_to_call : bool
        Calculate CMO OAS to the call date, not maturity date.
    partial_vega : bool
        Calculate partial vegas.
    other_durations : bool
        Calculate the following specialized durations - GNMA/FNMA spread
        duration, prepay duration, primary secondary spread duration, refi
        elbow duration, refi prepay duration, turnover prepay duration, and
        volatility duration.
    volatility_duration : bool
        Calculate volatility duration.
    prepay_duration : bool
        Calculate prepay duration.
    refi_elbow_duration : bool
        Calculate refi elbow duration.
    current_coupon_spread_sensitivity : bool
        Calculate current coupon spread duration.
    refi_prepay_duration : bool
        Calculate prepay duration.
    turnover_prepay_duration : bool
        Calculate turnover prepay duration.
    primary_secondary_spread_duration : bool
        Calculate primary secondary spread duration.
    index_spread_duration : bool
        Calculate index spread duration.
    partials : ~analyticsapi.models.Partials
        Optional, and only to be used if includePartials = true.
    """

    include_partials: Optional[bool] = rest_field(name="includePartials")
    """Optional additional pricing settings."""
    option_model: Optional[Union[str, "_models.OptionModel"]] = rest_field(name="optionModel")
    """OASEDUR is recommended, returns OAS and option adjusted measures. OAS returns CMO OAS only.
     Known values are: \"OAS\", \"OASEDUR\", and \"YCMARGIN\"."""
    use_oas_to_call: Optional[bool] = rest_field(name="useOASToCall")
    """Calculate CMO OAS to the call date, not maturity date."""
    partial_vega: Optional[bool] = rest_field(name="partialVega")
    """Calculate partial vegas."""
    other_durations: Optional[bool] = rest_field(name="otherDurations")
    """Calculate the following specialized durations - GNMA/FNMA spread duration, prepay duration,
     primary secondary spread duration, refi elbow duration, refi prepay duration, turnover prepay
     duration, and volatility duration."""
    volatility_duration: Optional[bool] = rest_field(name="volatilityDuration")
    """Calculate volatility duration."""
    prepay_duration: Optional[bool] = rest_field(name="prepayDuration")
    """Calculate prepay duration."""
    refi_elbow_duration: Optional[bool] = rest_field(name="refiElbowDuration")
    """Calculate refi elbow duration."""
    current_coupon_spread_sensitivity: Optional[bool] = rest_field(name="currentCouponSpreadSensitivity")
    """Calculate current coupon spread duration."""
    refi_prepay_duration: Optional[bool] = rest_field(name="refiPrepayDuration")
    """Calculate prepay duration."""
    turnover_prepay_duration: Optional[bool] = rest_field(name="turnoverPrepayDuration")
    """Calculate turnover prepay duration."""
    primary_secondary_spread_duration: Optional[bool] = rest_field(name="primarySecondarySpreadDuration")
    """Calculate primary secondary spread duration."""
    index_spread_duration: Optional[bool] = rest_field(name="indexSpreadDuration")
    """Calculate index spread duration."""
    partials: Optional["_models.Partials"] = rest_field()
    """Optional, and only to be used if includePartials = true."""

    @overload
    def __init__(
        self,
        *,
        include_partials: Optional[bool] = None,
        option_model: Optional[Union[str, "_models.OptionModel"]] = None,
        use_oas_to_call: Optional[bool] = None,
        partial_vega: Optional[bool] = None,
        other_durations: Optional[bool] = None,
        volatility_duration: Optional[bool] = None,
        prepay_duration: Optional[bool] = None,
        refi_elbow_duration: Optional[bool] = None,
        current_coupon_spread_sensitivity: Optional[bool] = None,
        refi_prepay_duration: Optional[bool] = None,
        turnover_prepay_duration: Optional[bool] = None,
        primary_secondary_spread_duration: Optional[bool] = None,
        index_spread_duration: Optional[bool] = None,
        partials: Optional["_models.Partials"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FieldDefinition(_model_base.Model):
    """An object that contains the identifiers of the market data fields used for real-time and time
    series requests.

    Attributes
    ----------
    real_time_fid_priority : list[str]
        An array of real-time Fid (field identifier) names used to get the
        market data.  The default value is None, needs to be assigned before
        using.
    historical_fid_priority : list[str]
        An array of historical Fid (field identifier) names used to get the
        market data.  The default value is None, needs to be assigned before
        using.
    """

    real_time_fid_priority: Optional[List[str]] = rest_field(name="realTimeFidPriority")
    """An array of real-time Fid (field identifier) names used to get the market data."""
    historical_fid_priority: Optional[List[str]] = rest_field(name="historicalFidPriority")
    """An array of historical Fid (field identifier) names used to get the market data."""

    @overload
    def __init__(
        self,
        *,
        real_time_fid_priority: Optional[List[str]] = None,
        historical_fid_priority: Optional[List[str]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FieldValue(_model_base.Model):
    """An object that contains the bid and ask quotes and related attributes for the instrument.

    Readonly variables are only populated by the server, and will be ignored when sending a request.

    Attributes
    ----------
    value : float
        The quote value of the instrument. Required.
    is_overridden : bool
        An indicator whether the value is overridden. It returns only 'true' if
        value is overridden in the request.
    market_value : float
        The quote retrieved from the market. It is returned in the response
        only if the value is overridden in the request.
    """

    value: float = rest_field()
    """The quote value of the instrument. Required."""
    is_overridden: Optional[bool] = rest_field(name="isOverridden", visibility=["read"])
    """An indicator whether the value is overridden. It returns only 'true' if value is overridden in
     the request."""
    market_value: Optional[float] = rest_field(name="marketValue", visibility=["read"])
    """The quote retrieved from the market. It is returned in the response only if the value is
     overridden in the request."""

    @overload
    def __init__(
        self,
        value: float,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class InterestRateDefinition(ABC, _model_base.Model):
    """An object that defines the interest rate settings.

    You probably want to use the sub-classes and not this class directly. Known sub-classes are:
    FixedRateDefinition, FloatingRateDefinition, StepRateDefinition

    Attributes
    ----------
    interest_rate_type : str or ~analyticsapi.models.InterestRateTypeEnum
        The interest rate type. Required. Known values are: "FixedRate",
        "StepRate", "FloatingRate", and "FloatingRateFormula".
    """

    __mapping__: Dict[str, _model_base.Model] = {}
    interest_rate_type: str = rest_discriminator(name="interestRateType")
    """The interest rate type. Required. Known values are: \"FixedRate\", \"StepRate\",
     \"FloatingRate\", and \"FloatingRateFormula\"."""

    @overload
    def __init__(
        self,
        interest_rate_type: str,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["interest_rate_type"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class FixedRateDefinition(InterestRateDefinition, discriminator="FixedRate"):
    """An object that defines a fixed rate.

    Attributes
    ----------
    interest_rate_type : str or ~analyticsapi.models.FIXED_RATE
        The type of interest rate that is defined as a fixed rate. Required. A
        fixed interest rate.
    rate : ~analyticsapi.models.Rate
        An object that defines the interest rate value used to derive fixed
        interest payments. Required.
    first_accrual_date : ~datetime.date
        The date from which the interest starts accruing. The value is
        expressed in ISO 8601 format: YYYY-MM-DD (e.g., '2021-01-01').
    """

    interest_rate_type: Literal[InterestRateTypeEnum.FIXED_RATE] = rest_discriminator(name="interestRateType")  # type: ignore
    """The type of interest rate that is defined as a fixed rate. Required. A fixed interest rate."""
    rate: "_models.Rate" = rest_field()
    """An object that defines the interest rate value used to derive fixed interest payments.
     Required."""
    first_accrual_date: Optional[datetime.date] = rest_field(name="firstAccrualDate")
    """The date from which the interest starts accruing. The value is expressed in ISO 8601 format:
     YYYY-MM-DD (e.g., '2021-01-01')."""

    @overload
    def __init__(
        self,
        *,
        rate: "_models.Rate",
        first_accrual_date: Optional[datetime.date] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, interest_rate_type=InterestRateTypeEnum.FIXED_RATE, **kwargs)


class FloaterSettings(_model_base.Model):
    """FloaterSettings.

    Attributes
    ----------
    use_forward_index : bool
        Additional optional settings for floating rate bonds.
    forward_index_rate : float
        Optional. Spread over Forward Index. If used, do not use
        forwardIndexVector.
    index_projections : list[~analyticsapi.models.IndexProjection]
        The default value is None, needs to be assigned before using.
    finance_rate : float
        Optional, the financing rate used when if solving for the forward price
        is requested.
    calculate_to_maturity : bool
        Optional. Used for fix-to-float bonds. If true analytics are calculated
        to the maturity date, otherwise the fixed-to-float date.
    """

    use_forward_index: Optional[bool] = rest_field(name="useForwardIndex")
    """Additional optional settings for floating rate bonds."""
    forward_index_rate: Optional[float] = rest_field(name="forwardIndexRate")
    """Optional. Spread over Forward Index. If used, do not use forwardIndexVector."""
    index_projections: Optional[List["_models.IndexProjection"]] = rest_field(name="indexProjections")
    finance_rate: Optional[float] = rest_field(name="financeRate")
    """Optional, the financing rate used when if solving for the forward price is requested."""
    calculate_to_maturity: Optional[bool] = rest_field(name="calculateToMaturity")
    """Optional. Used for fix-to-float bonds. If true analytics are calculated to the maturity date,
     otherwise the fixed-to-float date."""

    @overload
    def __init__(
        self,
        *,
        use_forward_index: Optional[bool] = None,
        forward_index_rate: Optional[float] = None,
        index_projections: Optional[List["_models.IndexProjection"]] = None,
        finance_rate: Optional[float] = None,
        calculate_to_maturity: Optional[bool] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FloatingRateDefinition(InterestRateDefinition, discriminator="FloatingRate"):
    """An object that defines a floating rate.

    Attributes
    ----------
    interest_rate_type : str or ~analyticsapi.models.FLOATING_RATE
        The type of interest rate that is defined as a floating rate. Required.
        A floating interest rate.
    index : str
        The identifier of the floating rate index definition (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long,
        start with an alphanumeric character, and contain only alphanumeric
        characters, slashes and underscores. Required.
    spread_schedule : list[~analyticsapi.models.DatedRate]
        An array of objects that represents the sequence of spreads (in basis
        points) applied to the index value. If not defined, a flat spread of 0
        basis point is applied. The default value is None, needs to be assigned
        before using.
    compounding : ~analyticsapi.models.IndexCompoundingDefinition
        An object that defines the use of index compounding.
    reset_dates : ~analyticsapi.models.ResetDatesDefinition
        An object that defines the reset of index fixing dates.
    leverage : ~decimal.Decimal
        The leverage applied to the index value.
    cap : ~analyticsapi.models.CapFloorDefinition
        An object that defines a cap option.
    floor : ~analyticsapi.models.CapFloorDefinition
        An object that defines a floor option.
    front_stub_index : ~analyticsapi.models.StubIndexReferences
        An object that defines how the reference rate of the front stub period
        is calculated.
    back_stub_index : ~analyticsapi.models.StubIndexReferences
        An object that defines how the reference rate of the back stub period
        is calculated.
    """

    interest_rate_type: Literal[InterestRateTypeEnum.FLOATING_RATE] = rest_discriminator(name="interestRateType")  # type: ignore
    """The type of interest rate that is defined as a floating rate. Required. A floating interest
     rate."""
    index: str = rest_field()
    """The identifier of the floating rate index definition (GUID or URI).
     Note that a URI must be at least 2 and at most 102 characters long, start with an alphanumeric
     character, and contain only alphanumeric characters, slashes and underscores. Required."""
    spread_schedule: Optional[List["_models.DatedRate"]] = rest_field(name="spreadSchedule")
    """An array of objects that represents the sequence of spreads (in basis points) applied to the
     index value. If not defined, a flat spread of 0 basis point is applied."""
    compounding: Optional["_models.IndexCompoundingDefinition"] = rest_field()
    """An object that defines the use of index compounding."""
    reset_dates: Optional["_models.ResetDatesDefinition"] = rest_field(name="resetDates")
    """An object that defines the reset of index fixing dates."""
    leverage: Optional[decimal.Decimal] = rest_field()
    """The leverage applied to the index value."""
    cap: Optional["_models.CapFloorDefinition"] = rest_field()
    """An object that defines a cap option."""
    floor: Optional["_models.CapFloorDefinition"] = rest_field()
    """An object that defines a floor option."""
    front_stub_index: Optional["_models.StubIndexReferences"] = rest_field(name="frontStubIndex")
    """An object that defines how the reference rate of the front stub period is calculated."""
    back_stub_index: Optional["_models.StubIndexReferences"] = rest_field(name="backStubIndex")
    """An object that defines how the reference rate of the back stub period is calculated."""

    @overload
    def __init__(
        self,
        *,
        index: str,
        spread_schedule: Optional[List["_models.DatedRate"]] = None,
        compounding: Optional["_models.IndexCompoundingDefinition"] = None,
        reset_dates: Optional["_models.ResetDatesDefinition"] = None,
        leverage: Optional[decimal.Decimal] = None,
        cap: Optional["_models.CapFloorDefinition"] = None,
        floor: Optional["_models.CapFloorDefinition"] = None,
        front_stub_index: Optional["_models.StubIndexReferences"] = None,
        back_stub_index: Optional["_models.StubIndexReferences"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, interest_rate_type=InterestRateTypeEnum.FLOATING_RATE, **kwargs)


class FloatingRateIndex(_model_base.Model):
    """A model template defining a resource.

    Readonly variables are only populated by the server, and will be ignored when sending a request.

    Attributes
    ----------
    type : str or ~analyticsapi.models.FLOATING_RATE_INDEX
        Property defining the type of the resource.
    id : str
        Unique identifier of the FloatingRateIndex.
    location : ~analyticsapi.models.Location
        Object defining the location of the FloatingRateIndex in the platform.
        Required.
    description : ~analyticsapi.models.Description
        Object defining metadata for the FloatingRateIndex.
    definition : ~analyticsapi.models.FloatingRateIndexDefinition
        Object defining the FloatingRateIndex. Required.
    """

    type: Optional[Literal[ResourceType.FLOATING_RATE_INDEX]] = rest_field(
        visibility=["read"], default=ResourceType.FLOATING_RATE_INDEX
    )
    """Property defining the type of the resource."""
    id: Optional[str] = rest_field(visibility=["read"])
    """Unique identifier of the FloatingRateIndex."""
    location: "_models.Location" = rest_field(visibility=["read", "create"])
    """Object defining the location of the FloatingRateIndex in the platform. Required."""
    description: Optional["_models.Description"] = rest_field()
    """Object defining metadata for the FloatingRateIndex."""
    definition: "_models.FloatingRateIndexDefinition" = rest_field()
    """Object defining the FloatingRateIndex. Required."""

    @overload
    def __init__(
        self,
        *,
        location: "_models.Location",
        definition: "_models.FloatingRateIndexDefinition",
        description: Optional["_models.Description"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FloatingRateIndexCollectionLinks(_model_base.Model):
    """FloatingRateIndexCollectionLinks.

    Attributes
    ----------
    self_property : ~analyticsapi.models.Link
        Required.
    first : ~analyticsapi.models.Link
    prev : ~analyticsapi.models.Link
    next : ~analyticsapi.models.Link
    last : ~analyticsapi.models.Link
    """

    self_property: "_models.Link" = rest_field(name="self")
    """Required."""
    first: Optional["_models.Link"] = rest_field()
    prev: Optional["_models.Link"] = rest_field()
    next: Optional["_models.Link"] = rest_field()
    last: Optional["_models.Link"] = rest_field()

    @overload
    def __init__(
        self,
        *,
        self_property: "_models.Link",
        first: Optional["_models.Link"] = None,
        prev: Optional["_models.Link"] = None,
        next: Optional["_models.Link"] = None,
        last: Optional["_models.Link"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FloatingRateIndexCollectionResponse(_model_base.Model):
    """A model template describing a paged response.

    Attributes
    ----------
    data : list[~analyticsapi.models.FloatingRateIndexInfo]
        Required.  The default value is None, needs to be assigned before
        using.
    page : int
        The page number of the current page displayed. Minimum value of this
        property is 1. Required.
    item_per_page : int
        Number of items displayed per page. Required.
    total_pages : int
        Total number of pages available for display. Required.
    total_items : int
        Total number of items available for display. Required.
    links : ~analyticsapi.models.FloatingRateIndexCollectionLinks
        Links for available operations and/or resources linked to current
        response.
    """

    data: List["_models.FloatingRateIndexInfo"] = rest_field()
    """Required."""
    page: int = rest_field()
    """The page number of the current page displayed. Minimum value of this property is 1. Required."""
    item_per_page: int = rest_field(name="itemPerPage")
    """Number of items displayed per page. Required."""
    total_pages: int = rest_field(name="totalPages")
    """Total number of pages available for display. Required."""
    total_items: int = rest_field(name="totalItems")
    """Total number of items available for display. Required."""
    links: Optional["_models.FloatingRateIndexCollectionLinks"] = rest_field()
    """Links for available operations and/or resources linked to current response."""

    @overload
    def __init__(
        self,
        *,
        data: List["_models.FloatingRateIndexInfo"],
        page: int,
        item_per_page: int,
        total_pages: int,
        total_items: int,
        links: Optional["_models.FloatingRateIndexCollectionLinks"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FloatingRateIndexDefinition(_model_base.Model):
    """An object that defines the reference index of a floating rate.

    Attributes
    ----------
    currency : str
        The currency of the reference index. The value is expressed in ISO 4217
        alphabetical format (e.g., 'GBP'). Required.
    name : str
        The name of the floating rate index (e.g., 'EURIBOR'). Required.
    tenor : str
        The period code indicating the tenor of the underlying floating rate
        index (e.g., '1M', '1Y'). Required.
    year_basis : str or ~analyticsapi.models.YearBasisEnum
        The period length in days for the year used to calculate the time
        fraction and depends on the year basis convention applied. Required.
        Known values are: "YB_252", "YB_360", "YB_364", "YB_365", "YB_36525",
        "YB_366", and "YB_Actual".
    rounding : ~analyticsapi.models.RoundingDefinition
        An object that defines how rounding is applied to the reference
        floating rate index. Required.
    quote_definition : ~analyticsapi.models.QuoteDefinition
        An object that defines the attributes for getting the floating rate
        index quote. Required.
    """

    currency: str = rest_field()
    """The currency of the reference index. The value is expressed in ISO 4217 alphabetical format
     (e.g., 'GBP'). Required."""
    name: str = rest_field()
    """The name of the floating rate index (e.g., 'EURIBOR'). Required."""
    tenor: str = rest_field()
    """The period code indicating the tenor of the underlying floating rate index (e.g., '1M', '1Y').
     Required."""
    year_basis: Union[str, "_models.YearBasisEnum"] = rest_field(name="yearBasis")
    """The period length in days for the year used to calculate the time fraction and depends on the
     year basis convention applied. Required. Known values are: \"YB_252\", \"YB_360\", \"YB_364\",
     \"YB_365\", \"YB_36525\", \"YB_366\", and \"YB_Actual\"."""
    rounding: "_models.RoundingDefinition" = rest_field()
    """An object that defines how rounding is applied to the reference floating rate index. Required."""
    quote_definition: "_models.QuoteDefinition" = rest_field(name="quoteDefinition")
    """An object that defines the attributes for getting the floating rate index quote. Required."""

    @overload
    def __init__(
        self,
        *,
        currency: str,
        name: str,
        tenor: str,
        year_basis: Union[str, "_models.YearBasisEnum"],
        rounding: "_models.RoundingDefinition",
        quote_definition: "_models.QuoteDefinition",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FloatingRateIndexInfo(_model_base.Model):
    """A model template defining the partial description of the resource returned by the GET list
    service.

    Readonly variables are only populated by the server, and will be ignored when sending a request.

    Attributes
    ----------
    type : str or ~analyticsapi.models.FLOATING_RATE_INDEX
        Property defining the type of the resource.
    id : str
        Unique identifier of the FloatingRateIndex.
    location : ~analyticsapi.models.Location
        Object defining metadata for the FloatingRateIndex. Required.
    description : ~analyticsapi.models.Description
        Object defining the FloatingRateIndex.
    """

    type: Optional[Literal[ResourceType.FLOATING_RATE_INDEX]] = rest_field(
        visibility=["read"], default=ResourceType.FLOATING_RATE_INDEX
    )
    """Property defining the type of the resource."""
    id: Optional[str] = rest_field(visibility=["read"])
    """Unique identifier of the FloatingRateIndex."""
    location: "_models.Location" = rest_field(visibility=["read", "create"])
    """Object defining metadata for the FloatingRateIndex. Required."""
    description: Optional["_models.Description"] = rest_field()
    """Object defining the FloatingRateIndex."""

    @overload
    def __init__(
        self,
        *,
        location: "_models.Location",
        description: Optional["_models.Description"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FloatingRateIndexResponse(_model_base.Model):
    """A model template describing a single response.

    Attributes
    ----------
    data : ~analyticsapi.models.FloatingRateIndex
        Required.
    meta : ~analyticsapi.models.MetaData
    """

    data: "_models.FloatingRateIndex" = rest_field()
    """Required."""
    meta: Optional["_models.MetaData"] = rest_field()

    @overload
    def __init__(
        self,
        *,
        data: "_models.FloatingRateIndex",
        meta: Optional["_models.MetaData"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FraDefinition(SingleInterestRatePaymentDefinition):
    """FraDefinition.

    Attributes
    ----------
    notional : ~analyticsapi.models.Amount
        An object that defines the notional amount of the instrument. Required.
    rate : ~analyticsapi.models.InterestRateDefinition
        An object that defines the rate. Required.
    start_date : ~analyticsapi.models.Date
        An object that defines the start date of the interest payment period.
        Required.
    end_date : ~analyticsapi.models.Date
        An object that defines the end date of the interest payment period.
        Required.
    payment_offset : ~analyticsapi.models.OffsetDefinition
        An object that defines how the payment dates are derived from the
        interest period dates.
    settlement_type : str or ~analyticsapi.models.SettlementType
        An indicator that specifies how the payment is settled (e.g.,
        'Physical', 'Cash'). Known values are: "Cash" and "Physical".
    reference_rate : ~analyticsapi.models.Rate
        Required.
    """

    reference_rate: "_models.Rate" = rest_field(name="referenceRate")
    """Required."""

    @overload
    def __init__(
        self,
        *,
        notional: "_models.Amount",
        rate: "_models.InterestRateDefinition",
        start_date: "_models.Date",
        end_date: "_models.Date",
        reference_rate: "_models.Rate",
        payment_offset: Optional["_models.OffsetDefinition"] = None,
        settlement_type: Optional[Union[str, "_models.SettlementType"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["reference_rate"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class FraDefinitionTemplate(InstrumentTemplateDefinition, discriminator="ForwardRateAgreement"):
    """FraDefinitionTemplate.

    Attributes
    ----------
    instrument_type : str or ~analyticsapi.models.FORWARD_RATE_AGREEMENT
        Required. A foward rate agreement contract.
    template : ~analyticsapi.models.FraDefinition
        Required.
    """

    instrument_type: Literal[InstrumentTemplateTypeEnum.FORWARD_RATE_AGREEMENT] = rest_discriminator(name="instrumentType")  # type: ignore
    """Required. A foward rate agreement contract."""
    template: "_models.FraDefinition" = rest_field()
    """Required."""

    @overload
    def __init__(
        self,
        template: "_models.FraDefinition",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, instrument_type=InstrumentTemplateTypeEnum.FORWARD_RATE_AGREEMENT, **kwargs)


class FullDayDuration(Duration, discriminator="FullDayDuration"):
    """An object to determine the duration of the holiday taking into account a full day.

    Attributes
    ----------
    duration_type : str or ~analyticsapi.models.FULL_DAY_DURATION
        The type of the holiday duration. Only FullDayDuration value applies.
        Required. Full day holidays.
    full_day : int
        The number of full calendar days to determine the duration of the
        holiday. The minimum value is 1. Required.
    """

    duration_type: Literal[DurationType.FULL_DAY_DURATION] = rest_discriminator(name="durationType")  # type: ignore
    """The type of the holiday duration. Only FullDayDuration value applies. Required. Full day
     holidays."""
    full_day: int = rest_field(name="fullDay")
    """The number of full calendar days to determine the duration of the holiday. The minimum value is
     1. Required."""

    @overload
    def __init__(
        self,
        full_day: int,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, duration_type=DurationType.FULL_DAY_DURATION, **kwargs)


class FxAnalyticsDescription(_model_base.Model):
    """The object that contains the analytic fields that describe the instrument.

    Attributes
    ----------
    valuation_date : ~datetime.date
        The date at which the instrument is valued. The date is expressed in
        ISO 8601 format: YYYY-MM-DDT[hh]:[mm]:[ss]Z (e.g.,
        '2021-01-01T00:00:00Z').
    start_date : ~analyticsapi.models.AdjustedDate
        "An object describing a start date of the instrument.".
    end_date : ~analyticsapi.models.AdjustedDate
        "An object describing a maturity date of the instrument.".
    """

    valuation_date: Optional[datetime.date] = rest_field(name="valuationDate")
    """The date at which the instrument is valued. The date is expressed in ISO 8601 format:
     YYYY-MM-DDT[hh]:[mm]:[ss]Z (e.g., '2021-01-01T00:00:00Z')."""
    start_date: Optional["_models.AdjustedDate"] = rest_field(name="startDate")
    """\"An object describing a start date of the instrument.\"."""
    end_date: Optional["_models.AdjustedDate"] = rest_field(name="endDate")
    """\"An object describing a maturity date of the instrument.\"."""

    @overload
    def __init__(
        self,
        *,
        valuation_date: Optional[datetime.date] = None,
        start_date: Optional["_models.AdjustedDate"] = None,
        end_date: Optional["_models.AdjustedDate"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxCurveInput(_model_base.Model):
    """The object defining the 3rd party fx curve.

    Attributes
    ----------
    fx_type : str or ~analyticsapi.models.FxRateTypeEnum
        The type of values provided (outright rates or swap points). Required.
        Known values are: "Outright" and "Swapoint".
    points : list[~analyticsapi.models.CurveDataPoint]
        The list of dates and values. Required.  The default value is None,
        needs to be assigned before using.
    fx_cross_code : str
        The ISO code of the cross currency pair. Required.
    """

    fx_type: Union[str, "_models.FxRateTypeEnum"] = rest_field(name="fxType")
    """The type of values provided (outright rates or swap points). Required. Known values are:
     \"Outright\" and \"Swapoint\"."""
    points: List["_models.CurveDataPoint"] = rest_field()
    """The list of dates and values. Required."""
    fx_cross_code: str = rest_field(name="fxCrossCode")
    """The ISO code of the cross currency pair. Required."""

    @overload
    def __init__(
        self,
        *,
        fx_type: Union[str, "_models.FxRateTypeEnum"],
        points: List["_models.CurveDataPoint"],
        fx_cross_code: str,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForward(_model_base.Model):
    """Object defining a FxForward resource.

    Readonly variables are only populated by the server, and will be ignored when sending a request.

    Attributes
    ----------
    type : str or ~analyticsapi.models.FX_FORWARD
        Property defining the type of the resource.
    id : str
        Unique identifier of the FxForward.
    location : ~analyticsapi.models.Location
        Object defining the location of the FxForward in the platform.
        Required.
    description : ~analyticsapi.models.Description
        Object defining metadata for the FxForward.
    definition : ~analyticsapi.models.FxForwardDefinition
        Object defining the FxForward. Required.
    """

    type: Optional[Literal[ResourceType.FX_FORWARD]] = rest_field(visibility=["read"], default=ResourceType.FX_FORWARD)
    """Property defining the type of the resource."""
    id: Optional[str] = rest_field(visibility=["read"])
    """Unique identifier of the FxForward."""
    location: "_models.Location" = rest_field(visibility=["read", "create"])
    """Object defining the location of the FxForward in the platform. Required."""
    description: Optional["_models.Description"] = rest_field()
    """Object defining metadata for the FxForward."""
    definition: "_models.FxForwardDefinition" = rest_field()
    """Object defining the FxForward. Required."""

    @overload
    def __init__(
        self,
        *,
        location: "_models.Location",
        definition: "_models.FxForwardDefinition",
        description: Optional["_models.Description"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardAnalyticsDescription(FxAnalyticsDescription):
    """The object that contains the analytic fields that describe the instrument.

    Attributes
    ----------
    valuation_date : ~datetime.date
        The date at which the instrument is valued. The date is expressed in
        ISO 8601 format: YYYY-MM-DDT[hh]:[mm]:[ss]Z (e.g.,
        '2021-01-01T00:00:00Z').
    start_date : ~analyticsapi.models.AdjustedDate
        "An object describing a start date of the instrument.".
    end_date : ~analyticsapi.models.AdjustedDate
        "An object describing a maturity date of the instrument.".
    """

    @overload
    def __init__(
        self,
        *,
        valuation_date: Optional[datetime.date] = None,
        start_date: Optional["_models.AdjustedDate"] = None,
        end_date: Optional["_models.AdjustedDate"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardAnalyticsPricingOnResourceResponseData(_model_base.Model):  # pylint: disable=name-too-long
    """FxForwardAnalyticsPricingOnResourceResponseData.

    Attributes
    ----------
    resource : ~analyticsapi.models.FxForward
        Definition of the resource.
    pricing_preferences : ~analyticsapi.models.FxPricingParameters
        The parameters that control the computation of the analytics.
    analytics : ~analyticsapi.models.FxForwardAnalyticsPricingResponseWithError
        The result of the calculation request.
    market_data : ~analyticsapi.models.MarketData
        The market data used to compute the analytics.
    """

    resource: Optional["_models.FxForward"] = rest_field()
    """Definition of the resource."""
    pricing_preferences: Optional["_models.FxPricingParameters"] = rest_field(name="pricingPreferences")
    """The parameters that control the computation of the analytics."""
    analytics: Optional["_models.FxForwardAnalyticsPricingResponseWithError"] = rest_field()
    """The result of the calculation request."""
    market_data: Optional["_models.MarketData"] = rest_field(name="marketData")
    """The market data used to compute the analytics."""

    @overload
    def __init__(
        self,
        *,
        resource: Optional["_models.FxForward"] = None,
        pricing_preferences: Optional["_models.FxPricingParameters"] = None,
        analytics: Optional["_models.FxForwardAnalyticsPricingResponseWithError"] = None,
        market_data: Optional["_models.MarketData"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardAnalyticsPricingResponseData(_model_base.Model):
    """FxForwardAnalyticsPricingResponseData.

    Attributes
    ----------
    definitions : list[~analyticsapi.models.FxForwardDefinitionInstrument]
        The default value is None, needs to be assigned before using.
    pricing_preferences : ~analyticsapi.models.FxPricingParameters
        The parameters that control the computation of the analytics.
    analytics : list[~analyticsapi.models.FxForwardAnalyticsPricingResponseWithError]
        The result of the calculation request.  The default value is None,
        needs to be assigned before using.
    market_data : ~analyticsapi.models.MarketData
        The market data used to compute the analytics.
    """

    definitions: Optional[List["_models.FxForwardDefinitionInstrument"]] = rest_field()
    pricing_preferences: Optional["_models.FxPricingParameters"] = rest_field(name="pricingPreferences")
    """The parameters that control the computation of the analytics."""
    analytics: Optional[List["_models.FxForwardAnalyticsPricingResponseWithError"]] = rest_field()
    """The result of the calculation request."""
    market_data: Optional["_models.MarketData"] = rest_field(name="marketData")
    """The market data used to compute the analytics."""

    @overload
    def __init__(
        self,
        *,
        definitions: Optional[List["_models.FxForwardDefinitionInstrument"]] = None,
        pricing_preferences: Optional["_models.FxPricingParameters"] = None,
        analytics: Optional[List["_models.FxForwardAnalyticsPricingResponseWithError"]] = None,
        market_data: Optional["_models.MarketData"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardAnalyticsPricingResponseWithError(_model_base.Model):  # pylint: disable=name-too-long
    """A model template describing a response with an error for a given object.

    Attributes
    ----------
    description : ~analyticsapi.models.FxForwardAnalyticsDescription
        The analytics fields that describe the instrument.
    pricing_analysis : ~analyticsapi.models.FxForwardPricingAnalysis
        The analytics fields that are linked to a pre-trade analysis of the
        instrument.
    greeks : ~analyticsapi.models.FxForwardRisk
        The analytics fields that are linked to a risk analysis of the
        instrument.
    error : ~analyticsapi.models.ServiceError
        The error message for the calculation in case of a non-blocking error.
    """

    description: Optional["_models.FxForwardAnalyticsDescription"] = rest_field()
    """The analytics fields that describe the instrument."""
    pricing_analysis: Optional["_models.FxForwardPricingAnalysis"] = rest_field(name="pricingAnalysis")
    """The analytics fields that are linked to a pre-trade analysis of the instrument."""
    greeks: Optional["_models.FxForwardRisk"] = rest_field()
    """The analytics fields that are linked to a risk analysis of the instrument."""
    error: Optional["_models.ServiceError"] = rest_field()
    """The error message for the calculation in case of a non-blocking error."""

    @overload
    def __init__(
        self,
        *,
        description: Optional["_models.FxForwardAnalyticsDescription"] = None,
        pricing_analysis: Optional["_models.FxForwardPricingAnalysis"] = None,
        greeks: Optional["_models.FxForwardRisk"] = None,
        error: Optional["_models.ServiceError"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardAnalyticsValuationOnResourceResponseData(_model_base.Model):  # pylint: disable=name-too-long
    """FxForwardAnalyticsValuationOnResourceResponseData.

    Attributes
    ----------
    resource : ~analyticsapi.models.FxForward
        Definition of the resource.
    pricing_preferences : ~analyticsapi.models.FxPricingParameters
        The parameters that control the computation of the analytics.
    analytics : ~analyticsapi.models.FxForwardAnalyticsValuationResponseWithError
        The result of the calculation request.
    market_data : ~analyticsapi.models.MarketData
        The market data used to compute the analytics.
    """

    resource: Optional["_models.FxForward"] = rest_field()
    """Definition of the resource."""
    pricing_preferences: Optional["_models.FxPricingParameters"] = rest_field(name="pricingPreferences")
    """The parameters that control the computation of the analytics."""
    analytics: Optional["_models.FxForwardAnalyticsValuationResponseWithError"] = rest_field()
    """The result of the calculation request."""
    market_data: Optional["_models.MarketData"] = rest_field(name="marketData")
    """The market data used to compute the analytics."""

    @overload
    def __init__(
        self,
        *,
        resource: Optional["_models.FxForward"] = None,
        pricing_preferences: Optional["_models.FxPricingParameters"] = None,
        analytics: Optional["_models.FxForwardAnalyticsValuationResponseWithError"] = None,
        market_data: Optional["_models.MarketData"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardAnalyticsValuationResponseData(_model_base.Model):
    """FxForwardAnalyticsValuationResponseData.

    Attributes
    ----------
    definitions : list[~analyticsapi.models.FxForwardDefinitionInstrument]
        The default value is None, needs to be assigned before using.
    pricing_preferences : ~analyticsapi.models.FxPricingParameters
        The parameters that control the computation of the analytics.
    analytics : list[~analyticsapi.models.FxForwardAnalyticsValuationResponseWithError]
        The result of the calculation request.  The default value is None,
        needs to be assigned before using.
    market_data : ~analyticsapi.models.MarketData
        The market data used to compute the analytics.
    """

    definitions: Optional[List["_models.FxForwardDefinitionInstrument"]] = rest_field()
    pricing_preferences: Optional["_models.FxPricingParameters"] = rest_field(name="pricingPreferences")
    """The parameters that control the computation of the analytics."""
    analytics: Optional[List["_models.FxForwardAnalyticsValuationResponseWithError"]] = rest_field()
    """The result of the calculation request."""
    market_data: Optional["_models.MarketData"] = rest_field(name="marketData")
    """The market data used to compute the analytics."""

    @overload
    def __init__(
        self,
        *,
        definitions: Optional[List["_models.FxForwardDefinitionInstrument"]] = None,
        pricing_preferences: Optional["_models.FxPricingParameters"] = None,
        analytics: Optional[List["_models.FxForwardAnalyticsValuationResponseWithError"]] = None,
        market_data: Optional["_models.MarketData"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardAnalyticsValuationResponseWithError(_model_base.Model):  # pylint: disable=name-too-long
    """A model template describing a response with an error for a given object.

    Attributes
    ----------
    description : ~analyticsapi.models.FxForwardAnalyticsDescription
        The analytics fields that describe the instrument.
    valuation : ~analyticsapi.models.FxForwardValuation
        The analytics fields that are linked to a post-trade analysis of the
        instrument.
    greeks : ~analyticsapi.models.FxForwardRisk
        The analytics fields that are linked to a risk analysis of the
        instrument.
    error : ~analyticsapi.models.ServiceError
        The error message for the calculation in case of a non-blocking error.
    """

    description: Optional["_models.FxForwardAnalyticsDescription"] = rest_field()
    """The analytics fields that describe the instrument."""
    valuation: Optional["_models.FxForwardValuation"] = rest_field()
    """The analytics fields that are linked to a post-trade analysis of the instrument."""
    greeks: Optional["_models.FxForwardRisk"] = rest_field()
    """The analytics fields that are linked to a risk analysis of the instrument."""
    error: Optional["_models.ServiceError"] = rest_field()
    """The error message for the calculation in case of a non-blocking error."""

    @overload
    def __init__(
        self,
        *,
        description: Optional["_models.FxForwardAnalyticsDescription"] = None,
        valuation: Optional["_models.FxForwardValuation"] = None,
        greeks: Optional["_models.FxForwardRisk"] = None,
        error: Optional["_models.ServiceError"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardArrayPriceResponse(_model_base.Model):
    """Object defining the response of a pricing request for a collection of FxForward instruments.

    Attributes
    ----------
    data : ~analyticsapi.models.FxForwardAnalyticsPricingResponseData
        An object that contains calculated analytics, requested, and other data
        used for calculation. Required.
    """

    data: "_models.FxForwardAnalyticsPricingResponseData" = rest_field()
    """An object that contains calculated analytics, requested, and other data used for calculation.
     Required."""

    @overload
    def __init__(
        self,
        data: "_models.FxForwardAnalyticsPricingResponseData",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["data"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class FxForwardArrayValuationResponse(_model_base.Model):
    """Object defining the response of a valuation request for a collection of FxForward instruments.

    Attributes
    ----------
    data : ~analyticsapi.models.FxForwardAnalyticsValuationResponseData
        An object that contains calculated analytics, requested, and other data
        used for calculation. Required.
    """

    data: "_models.FxForwardAnalyticsValuationResponseData" = rest_field()
    """An object that contains calculated analytics, requested, and other data used for calculation.
     Required."""

    @overload
    def __init__(
        self,
        data: "_models.FxForwardAnalyticsValuationResponseData",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["data"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class FxForwardCollectionLinks(_model_base.Model):
    """Object defining the related links available for a collection of FxForward instruments.

    Attributes
    ----------
    self_property : ~analyticsapi.models.Link
        Required.
    first : ~analyticsapi.models.Link
    prev : ~analyticsapi.models.Link
    next : ~analyticsapi.models.Link
    last : ~analyticsapi.models.Link
    """

    self_property: "_models.Link" = rest_field(name="self")
    """Required."""
    first: Optional["_models.Link"] = rest_field()
    prev: Optional["_models.Link"] = rest_field()
    next: Optional["_models.Link"] = rest_field()
    last: Optional["_models.Link"] = rest_field()

    @overload
    def __init__(
        self,
        *,
        self_property: "_models.Link",
        first: Optional["_models.Link"] = None,
        prev: Optional["_models.Link"] = None,
        next: Optional["_models.Link"] = None,
        last: Optional["_models.Link"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardCollectionResponse(_model_base.Model):
    """Object defining the paged response for a collection of FxForward instruments.

    Attributes
    ----------
    data : list[~analyticsapi.models.FxForwardInfo]
        Required.  The default value is None, needs to be assigned before
        using.
    page : int
        The page number of the current page displayed. Minimum value of this
        property is 1. Required.
    item_per_page : int
        Number of items displayed per page. Required.
    total_pages : int
        Total number of pages available for display. Required.
    total_items : int
        Total number of items available for display. Required.
    links : ~analyticsapi.models.FxForwardCollectionLinks
        Links for available operations and/or resources linked to current
        response.
    """

    data: List["_models.FxForwardInfo"] = rest_field()
    """Required."""
    page: int = rest_field()
    """The page number of the current page displayed. Minimum value of this property is 1. Required."""
    item_per_page: int = rest_field(name="itemPerPage")
    """Number of items displayed per page. Required."""
    total_pages: int = rest_field(name="totalPages")
    """Total number of pages available for display. Required."""
    total_items: int = rest_field(name="totalItems")
    """Total number of items available for display. Required."""
    links: Optional["_models.FxForwardCollectionLinks"] = rest_field()
    """Links for available operations and/or resources linked to current response."""

    @overload
    def __init__(
        self,
        *,
        data: List["_models.FxForwardInfo"],
        page: int,
        item_per_page: int,
        total_pages: int,
        total_items: int,
        links: Optional["_models.FxForwardCollectionLinks"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardConstituent(FxConstituent, discriminator="FxForward"):
    """An object to define constituents that are used to construct the curve.

    Readonly variables are only populated by the server, and will be ignored when sending a request.

    Attributes
    ----------
    quote : ~analyticsapi.models.Quote
        An object to define the quote of the instrument used as a constituent.
    status : list[str]
        A message is returned if the constituent cannot be identified, or
        access for a user to the instrument used as a constituent is denied.
    type : str or ~analyticsapi.models.FX_FORWARD
        The type of the instrument used as a constituent. FxForward is the only
        valid value. Required.
    definition : ~analyticsapi.models.FxForwardConstituentDefinition
        An object to define the instrument used as a constituent.
    """

    type: Literal[FxConstituentEnum.FX_FORWARD] = rest_discriminator(name="type")  # type: ignore
    """The type of the instrument used as a constituent. FxForward is the only valid value. Required."""
    definition: Optional["_models.FxForwardConstituentDefinition"] = rest_field()
    """An object to define the instrument used as a constituent."""

    @overload
    def __init__(
        self,
        *,
        quote: Optional["_models.Quote"] = None,
        definition: Optional["_models.FxForwardConstituentDefinition"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, type=FxConstituentEnum.FX_FORWARD, **kwargs)


class FxForwardConstituentDefinition(_model_base.Model):
    """An object to define the FX forward instrument used as a constituent.

    Attributes
    ----------
    tenor : str
        The code indicating the tenor of the instrument used as a constituent
        (e.g., '1M', '1Y'). Required.
    template : str
        A pre-defined template can be used as an input by the user. It is the
        currency code of the constituent. Required.
    """

    tenor: str = rest_field()
    """The code indicating the tenor of the instrument used as a constituent (e.g., '1M', '1Y').
     Required."""
    template: str = rest_field()
    """A pre-defined template can be used as an input by the user. It is the currency code of the
     constituent. Required."""

    @overload
    def __init__(
        self,
        *,
        tenor: str,
        template: str,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardCurve(_model_base.Model):
    """A model defining a FxForward Curve resource.

    Readonly variables are only populated by the server, and will be ignored when sending a request.

    Attributes
    ----------
    type : str or ~analyticsapi.models.FX_FORWARD_CURVE
        Property defining the type of the resource.
    id : str
        Unique identifier of the FxForwardCurve.
    location : ~analyticsapi.models.Location
        Object defining the location of the FxForwardCurve in the platform.
        Required.
    description : ~analyticsapi.models.Description
        Object defining metadata for the FxForwardCurve.
    definition : ~analyticsapi.models.FxForwardCurveDefinition
        Object defining the FxForwardCurve. Required.
    """

    type: Optional[Literal[ResourceType.FX_FORWARD_CURVE]] = rest_field(
        visibility=["read"], default=ResourceType.FX_FORWARD_CURVE
    )
    """Property defining the type of the resource."""
    id: Optional[str] = rest_field(visibility=["read"])
    """Unique identifier of the FxForwardCurve."""
    location: "_models.Location" = rest_field(visibility=["read", "create"])
    """Object defining the location of the FxForwardCurve in the platform. Required."""
    description: Optional["_models.Description"] = rest_field()
    """Object defining metadata for the FxForwardCurve."""
    definition: "_models.FxForwardCurveDefinition" = rest_field()
    """Object defining the FxForwardCurve. Required."""

    @overload
    def __init__(
        self,
        *,
        location: "_models.Location",
        definition: "_models.FxForwardCurveDefinition",
        description: Optional["_models.Description"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardCurveCalculateArrayResponse(_model_base.Model):
    """A model describing the response returned for a FxForward curve calculation request where the
    curve is provided as part of the request.

    Attributes
    ----------
    data : ~analyticsapi.models.FxForwardCurveDataResponseData
        An object that contains calculated analytics, requested, and other data
        used for calculation. Required.
    """

    data: "_models.FxForwardCurveDataResponseData" = rest_field()
    """An object that contains calculated analytics, requested, and other data used for calculation.
     Required."""

    @overload
    def __init__(
        self,
        data: "_models.FxForwardCurveDataResponseData",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["data"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class FxForwardCurveCalculateResponse(_model_base.Model):
    """A model describing the response returned for a FxForward curve calculation request performed on
    an exsting curve.

    Attributes
    ----------
    data : ~analyticsapi.models.FxForwardCurveDataOnResourceResponseData
        Required.
    """

    data: "_models.FxForwardCurveDataOnResourceResponseData" = rest_field()
    """Required."""

    @overload
    def __init__(
        self,
        data: "_models.FxForwardCurveDataOnResourceResponseData",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["data"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class FxForwardCurveCalculationParameters(CurveCalculationParameters):
    """An object that contains parameters used to define how the Fx Forward curve is constructed from
    the constituents.

    Attributes
    ----------
    valuation_date : ~datetime.date
        The date on which the curve is constructed. The value is expressed in
        ISO 8601 format: YYYY-MM-DD (e.g., '2023-01-01'). The valuation date
        should not be in the future. Default is Today.
    curve_tenors : list[str]
        An array of user-defined tenors for which curve points to be computed.
        The values are expressed in:

        * time period code for tenors (e.g., '1M', '1Y'),
        * ISO 8601 format 'YYYY-MM-DD' for dates (e.g., '2023-01-01').  The default value is None,
        needs to be assigned before using.
    fx_forward_curve_calculation_preferences : ~analyticsapi.models.FxForwardCurveCalculationPreferences
        An object to define calculation preferences for the curve.
    """

    fx_forward_curve_calculation_preferences: Optional["_models.FxForwardCurveCalculationPreferences"] = rest_field(
        name="fxForwardCurveCalculationPreferences"
    )
    """An object to define calculation preferences for the curve."""

    @overload
    def __init__(
        self,
        *,
        valuation_date: Optional[datetime.date] = None,
        curve_tenors: Optional[List[str]] = None,
        fx_forward_curve_calculation_preferences: Optional["_models.FxForwardCurveCalculationPreferences"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["fx_forward_curve_calculation_preferences"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class FxForwardCurveCalculationPreferences(_model_base.Model):
    """An object to define calculation preferences for the curve.

    Attributes
    ----------
    extrapolation_mode : str or ~analyticsapi.models.ExtrapolationMode
        The extrapolation method used in the curve bootstrapping. The default
        is Constant. Known values are: "Constant" and "Linear".
    interpolation_mode : str or ~analyticsapi.models.FxForwardCurveInterpolationMode
        The interpolation method used in the curve bootstrapping. The default
        is Linear. Known values are: "CubicSpline", "Constant", and "Linear".
    use_delayed_data_if_denied : bool
        An indicator of whether the delayed data defined in request is used.
        The default is false.
    ignore_invalid_instruments : bool
        An indicator of whether invalid instruments are ignored for the curve
        construction. The default is true.
    ignore_pivot_currency_holidays : bool
        An indicator of whether holidays of the pivot currency are included or
        not in the pricing when dates are calculated. The default is false.
    """

    extrapolation_mode: Optional[Union[str, "_models.ExtrapolationMode"]] = rest_field(name="extrapolationMode")
    """The extrapolation method used in the curve bootstrapping. The default is Constant. Known values
     are: \"Constant\" and \"Linear\"."""
    interpolation_mode: Optional[Union[str, "_models.FxForwardCurveInterpolationMode"]] = rest_field(
        name="interpolationMode"
    )
    """The interpolation method used in the curve bootstrapping. The default is Linear. Known values
     are: \"CubicSpline\", \"Constant\", and \"Linear\"."""
    use_delayed_data_if_denied: Optional[bool] = rest_field(name="useDelayedDataIfDenied")
    """An indicator of whether the delayed data defined in request is used. The default is false."""
    ignore_invalid_instruments: Optional[bool] = rest_field(name="ignoreInvalidInstruments")
    """An indicator of whether invalid instruments are ignored for the curve construction. The default
     is true."""
    ignore_pivot_currency_holidays: Optional[bool] = rest_field(name="ignorePivotCurrencyHolidays")
    """An indicator of whether holidays of the pivot currency are included or not in the pricing when
     dates are calculated. The default is false."""

    @overload
    def __init__(
        self,
        *,
        extrapolation_mode: Optional[Union[str, "_models.ExtrapolationMode"]] = None,
        interpolation_mode: Optional[Union[str, "_models.FxForwardCurveInterpolationMode"]] = None,
        use_delayed_data_if_denied: Optional[bool] = None,
        ignore_invalid_instruments: Optional[bool] = None,
        ignore_pivot_currency_holidays: Optional[bool] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardCurveChoice(_model_base.Model):
    """Object that represents an FxForward curve in one of two ways: Provide either a reference to a
    curve saved on the platform, or a list of data points.

    Attributes
    ----------
    reference : str
        The identifier of the FX curve definition resource (UUID or URI). The
        default space is LSEG if not provided in URI format.
    curve : ~analyticsapi.models.FxCurveInput
        An object to define the curve data points.
    """

    reference: Optional[str] = rest_field()
    """The identifier of the FX curve definition resource (UUID or URI). The default space is LSEG if
     not provided in URI format."""
    curve: Optional["_models.FxCurveInput"] = rest_field()
    """An object to define the curve data points."""

    @overload
    def __init__(
        self,
        *,
        reference: Optional[str] = None,
        curve: Optional["_models.FxCurveInput"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardCurveCollectionLinks(_model_base.Model):
    """FxForwardCurveCollectionLinks.

    Attributes
    ----------
    self_property : ~analyticsapi.models.Link
        Required.
    first : ~analyticsapi.models.Link
    prev : ~analyticsapi.models.Link
    next : ~analyticsapi.models.Link
    last : ~analyticsapi.models.Link
    """

    self_property: "_models.Link" = rest_field(name="self")
    """Required."""
    first: Optional["_models.Link"] = rest_field()
    prev: Optional["_models.Link"] = rest_field()
    next: Optional["_models.Link"] = rest_field()
    last: Optional["_models.Link"] = rest_field()

    @overload
    def __init__(
        self,
        *,
        self_property: "_models.Link",
        first: Optional["_models.Link"] = None,
        prev: Optional["_models.Link"] = None,
        next: Optional["_models.Link"] = None,
        last: Optional["_models.Link"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardCurveCollectionResponse(_model_base.Model):
    """A model describing a paged FXForward Curve response.

    Attributes
    ----------
    data : list[~analyticsapi.models.FxForwardCurveInfo]
        Required.  The default value is None, needs to be assigned before
        using.
    page : int
        The page number of the current page displayed. Minimum value of this
        property is 1. Required.
    item_per_page : int
        Number of items displayed per page. Required.
    total_pages : int
        Total number of pages available for display. Required.
    total_items : int
        Total number of items available for display. Required.
    links : ~analyticsapi.models.FxForwardCurveCollectionLinks
        Links for available operations and/or resources linked to current
        response.
    """

    data: List["_models.FxForwardCurveInfo"] = rest_field()
    """Required."""
    page: int = rest_field()
    """The page number of the current page displayed. Minimum value of this property is 1. Required."""
    item_per_page: int = rest_field(name="itemPerPage")
    """Number of items displayed per page. Required."""
    total_pages: int = rest_field(name="totalPages")
    """Total number of pages available for display. Required."""
    total_items: int = rest_field(name="totalItems")
    """Total number of items available for display. Required."""
    links: Optional["_models.FxForwardCurveCollectionLinks"] = rest_field()
    """Links for available operations and/or resources linked to current response."""

    @overload
    def __init__(
        self,
        *,
        data: List["_models.FxForwardCurveInfo"],
        page: int,
        item_per_page: int,
        total_pages: int,
        total_items: int,
        links: Optional["_models.FxForwardCurveCollectionLinks"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardCurveDataOnResourceResponseData(_model_base.Model):
    """FxForwardCurveDataOnResourceResponseData.

    Attributes
    ----------
    resource : ~analyticsapi.models.FxForwardCurve
        Definition of the resource.
    pricing_preferences : ~analyticsapi.models.FxForwardCurveCalculationParameters
        The parameters that control the computation of the analytics.
    analytics : ~analyticsapi.models.FxForwardCurveDataResponseWithError
        The result of the calculation request.
    """

    resource: Optional["_models.FxForwardCurve"] = rest_field()
    """Definition of the resource."""
    pricing_preferences: Optional["_models.FxForwardCurveCalculationParameters"] = rest_field(name="pricingPreferences")
    """The parameters that control the computation of the analytics."""
    analytics: Optional["_models.FxForwardCurveDataResponseWithError"] = rest_field()
    """The result of the calculation request."""

    @overload
    def __init__(
        self,
        *,
        resource: Optional["_models.FxForwardCurve"] = None,
        pricing_preferences: Optional["_models.FxForwardCurveCalculationParameters"] = None,
        analytics: Optional["_models.FxForwardCurveDataResponseWithError"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardCurveDataResponseData(_model_base.Model):
    """FxForwardCurveDataResponseData.

    Attributes
    ----------
    definitions : list[~analyticsapi.models.FxForwardCurveDefinitionInstrument]
        The default value is None, needs to be assigned before using.
    pricing_preferences : ~analyticsapi.models.FxForwardCurveCalculationParameters
        The parameters that control the computation of the analytics.
    analytics : list[~analyticsapi.models.FxForwardCurveDataResponseWithError]
        The result of the calculation request.  The default value is None,
        needs to be assigned before using.
    """

    definitions: Optional[List["_models.FxForwardCurveDefinitionInstrument"]] = rest_field()
    pricing_preferences: Optional["_models.FxForwardCurveCalculationParameters"] = rest_field(name="pricingPreferences")
    """The parameters that control the computation of the analytics."""
    analytics: Optional[List["_models.FxForwardCurveDataResponseWithError"]] = rest_field()
    """The result of the calculation request."""

    @overload
    def __init__(
        self,
        *,
        definitions: Optional[List["_models.FxForwardCurveDefinitionInstrument"]] = None,
        pricing_preferences: Optional["_models.FxForwardCurveCalculationParameters"] = None,
        analytics: Optional[List["_models.FxForwardCurveDataResponseWithError"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardCurveDataResponseWithError(_model_base.Model):
    """A model template describing a response with an error for a given object.

    Attributes
    ----------
    constituents : list[~analyticsapi.models.FxConstituent]
        An array of objects describing constituents of the curve.  The default
        value is None, needs to be assigned before using.
    outright_curve : ~analyticsapi.models.FxOutrightCurveDescription
        An object that contains curve points and curve type. Required.
    underlying_curves : list[~analyticsapi.models.Curve]
        An object that contains the underlying curves used to construct the
        curve.  The default value is None, needs to be assigned before using.
    invalid_constituents : list[~analyticsapi.models.FxConstituent]
        An array of objects to define constituents that are part of the curve
        definition but cannot be used during the curve construction.  The
        default value is None, needs to be assigned before using.
    error : ~analyticsapi.models.ServiceError
        The error message for the calculation in case of a non-blocking error.
    """

    constituents: Optional[List["_models.FxConstituent"]] = rest_field()
    """An array of objects describing constituents of the curve."""
    outright_curve: "_models.FxOutrightCurveDescription" = rest_field(name="outrightCurve")
    """An object that contains curve points and curve type. Required."""
    underlying_curves: Optional[List["_models.Curve"]] = rest_field(name="underlyingCurves")
    """An object that contains the underlying curves used to construct the curve."""
    invalid_constituents: Optional[List["_models.FxConstituent"]] = rest_field(name="invalidConstituents")
    """An array of objects to define constituents that are part of the curve definition but cannot be
     used during the curve construction."""
    error: Optional["_models.ServiceError"] = rest_field()
    """The error message for the calculation in case of a non-blocking error."""

    @overload
    def __init__(
        self,
        *,
        outright_curve: "_models.FxOutrightCurveDescription",
        constituents: Optional[List["_models.FxConstituent"]] = None,
        underlying_curves: Optional[List["_models.Curve"]] = None,
        invalid_constituents: Optional[List["_models.FxConstituent"]] = None,
        error: Optional["_models.ServiceError"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardCurveDefinition(_model_base.Model):
    """An object that defines the Fx Forward Curve resource. If only the cross currency pair is
    provided, with no optional details, the service will try to build a curve 'on the fly' from the
    list constituents available for this currency pair.
    If there is no direct quotation, the service will attempt to use a reference currency (first
    selecting USD, then EUR). In this case the return will be derived from the underlying curves
    constructed for each currency against the reference currency.
    If the reference currency and/or constituents are provided, the service will use them to create
    a custom curve. For a better result, please use the LSEG curve if it exists for a cross
    currency pair.
    The list type properties will not be initialized as empty list by default. A list of objects
    should be assigned first before adding new elements.

    Attributes
    ----------
    cross_currency : str
        A string to define the cross currency pair of the curve, expressed in
        ISO 4217 alphabetical format (e.g., 'EURCHF'). Value is limited to
        maximum of 6 characters. Required.
    reference_currency : str
        A string to define the reference currency for the cross currency pair
        of the curve, expressed in ISO 4217 alphabetical format (e.g., 'EUR').
        Value is limited to maximum of 3 characters. Optional. The reference
        currency is not used:

        * when a curve definition is created from FX spot and FX Foward instruments (“on the fly“
        request) available for the requested currency pair,
        * when curve points are calculated using an LSEG curve available for the requested currency
        pair.

        If a curve defintion with the same crossCurrency code dosn't exist, USD will be used as the
        reference currency.
        When the reference currency is provided (e.g., USD), constituents are calculated for each
        currency of the currency pair against the reference currency (e.g., EURUSD and GBPUSD).
        Please note that a reference currency must be provided:

        * when constituents are overridden using a pivot currency (e.g., EURUSD and GBPUSD),
        * when a non-standard quotation of the existing curve is used (except when one of the
        currencies is USD or EUR).

        The reference currency should be left empty if the quotation is direct or if the template used
        quotes the cross currency directly.
    constituents : list[~analyticsapi.models.FxConstituent]
        An array of objects to define constituents that are used to construct
        the curve. If not provided, constituents are retrieved from the market
        data.

        * If there is a pivot currency, two sets of constituents are required, each composed of 1
        FxSpot and at least one other constituent.
        * If there is no pivot currency (i.e. a direct cross currency), only one set of constituents
        is needed, with 1 FxSpot and at least one other constituent.

        Optional.  The default value is None, needs to be assigned before using.
    """

    cross_currency: str = rest_field(name="crossCurrency")
    """A string to define the cross currency pair of the curve, expressed in ISO 4217 alphabetical
     format (e.g., 'EURCHF'). Value is limited to maximum of 6 characters. Required."""
    reference_currency: Optional[str] = rest_field(name="referenceCurrency")
    """A string to define the reference currency for the cross currency pair of the curve, expressed
     in ISO 4217 alphabetical format (e.g., 'EUR'). Value is limited to maximum of 3 characters.
     Optional.
     The reference currency is not used:
     
     
     * when a curve definition is created from FX spot and FX Foward instruments (“on the fly“
     request) available for the requested currency pair,
     * when curve points are calculated using an LSEG curve available for the requested currency
     pair.
     
     If a curve defintion with the same crossCurrency code dosn't exist, USD will be used as the
     reference currency.
     When the reference currency is provided (e.g., USD), constituents are calculated for each
     currency of the currency pair against the reference currency (e.g., EURUSD and GBPUSD).
     Please note that a reference currency must be provided:
     
     
     * when constituents are overridden using a pivot currency (e.g., EURUSD and GBPUSD),
     * when a non-standard quotation of the existing curve is used (except when one of the
     currencies is USD or EUR).
     
     The reference currency should be left empty if the quotation is direct or if the template used
     quotes the cross currency directly."""
    constituents: Optional[List["_models.FxConstituent"]] = rest_field()
    """An array of objects to define constituents that are used to construct the curve. If not
     provided, constituents are retrieved from the market data.
     
     
     * If there is a pivot currency, two sets of constituents are required, each composed of 1
     FxSpot and at least one other constituent.
     * If there is no pivot currency (i.e. a direct cross currency), only one set of constituents is
     needed, with 1 FxSpot and at least one other constituent.
     
     Optional."""

    @overload
    def __init__(
        self,
        *,
        cross_currency: str,
        reference_currency: Optional[str] = None,
        constituents: Optional[List["_models.FxConstituent"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardCurveDefinitionInstrument(_model_base.Model):
    """An array of objects describing a curve or an instrument.
    Please provide either a full definition (for a user-defined curve/instrument), or reference to
    a curve/instrument definition saved in the platform, or the code identifying the existing
    curve/instrument.

    Attributes
    ----------
    definition : ~analyticsapi.models.FxForwardCurveDefinition
        The object that describes the definition of the instrument.
    reference : str
        The identifier of a resource (instrument definition, curve definition)
        that is already in the platform.
    code : str
        The unique public code used to identify an instrument that exists on
        the market (ISIN, RIC, etc.).
    """

    definition: Optional["_models.FxForwardCurveDefinition"] = rest_field()
    """The object that describes the definition of the instrument."""
    reference: Optional[str] = rest_field()
    """The identifier of a resource (instrument definition, curve definition) that is already in the
     platform."""
    code: Optional[str] = rest_field()
    """The unique public code used to identify an instrument that exists on the market (ISIN, RIC,
     etc.)."""

    @overload
    def __init__(
        self,
        *,
        definition: Optional["_models.FxForwardCurveDefinition"] = None,
        reference: Optional[str] = None,
        code: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardCurveInfo(_model_base.Model):
    """A model partially describing the FXForward Curve returned by the GET list service.

    Readonly variables are only populated by the server, and will be ignored when sending a request.

    Attributes
    ----------
    type : str or ~analyticsapi.models.FX_FORWARD_CURVE
        Property defining the type of the resource.
    id : str
        Unique identifier of the FxForwardCurve.
    location : ~analyticsapi.models.Location
        Object defining metadata for the FxForwardCurve. Required.
    description : ~analyticsapi.models.Description
        Object defining the FxForwardCurve.
    """

    type: Optional[Literal[ResourceType.FX_FORWARD_CURVE]] = rest_field(
        visibility=["read"], default=ResourceType.FX_FORWARD_CURVE
    )
    """Property defining the type of the resource."""
    id: Optional[str] = rest_field(visibility=["read"])
    """Unique identifier of the FxForwardCurve."""
    location: "_models.Location" = rest_field(visibility=["read", "create"])
    """Object defining metadata for the FxForwardCurve. Required."""
    description: Optional["_models.Description"] = rest_field()
    """Object defining the FxForwardCurve."""

    @overload
    def __init__(
        self,
        *,
        location: "_models.Location",
        description: Optional["_models.Description"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardCurveResponse(_model_base.Model):
    """A model template describing a single response.

    Attributes
    ----------
    data : ~analyticsapi.models.FxForwardCurve
        Required.
    meta : ~analyticsapi.models.MetaData
    """

    data: "_models.FxForwardCurve" = rest_field()
    """Required."""
    meta: Optional["_models.MetaData"] = rest_field()

    @overload
    def __init__(
        self,
        *,
        data: "_models.FxForwardCurve",
        meta: Optional["_models.MetaData"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxSpotDefinition(_model_base.Model):
    """Definition of the Fx Spot.

    Attributes
    ----------
    quoted_currency : str
        Quoted currency code, expressed in ISO 4217 alphabetical format (e.g.,
        'CHF'). Required.
    base_currency : str
        Base  currency code, expressed in ISO 4217 alphabetical format (e.g.,
        'CHF'). Required.
    deal_amount : float
        The amount of the deal (base) currency bought or sold.
    contra_amount : float
        The amount of contraCcy exchanged to buy or sell the amount of the deal
        (base) currency.".
    rate : ~analyticsapi.models.FxRate
        Exchange rate agreed by counterparties.
    start_date : ~analyticsapi.models.Date
        The start date of the instrument. Possible values are: AdjustableDate
        object - requires a date expressed in ISO 8601 format: YYYY-MM-DD
        (e.g., '2021-01-01'). Or a RelativeAdjustableDate - requires a tenor
        expressed as a code indicating the period between
        referenceDate(default=startDate) to endDate of the instrument (e.g.,
        '6M', '1Y'). Only NextBusinessDay is supported for
        DateMovingConvention. For spot date, tenor can only be "SN" (spot next)
        or "SW" (spot week). Default is a spot date.
    end_date : ~analyticsapi.models.Date
        The maturity date of the instrument. Possible values are:
        AdjustableDate object - requires a date expressed in ISO 8601 format:
        YYYY-MM-DD (e.g., '2021-01-01'). Or a RelativeAdjustableDate - requires
        a tenor expressed as a code indicating the period between
        referenceDate(default=startDate) to endDate of the instrument (e.g.,
        '6M', '1Y'). Only NextBusinessDay is supported for
        DateMovingConvention. For spot date, tenor can only be "SN" (spot next)
        or "SW" (spot week).
    payer : str or ~analyticsapi.models.PartyEnum
        The party (Party1 or Party2) who will pay the contraAmount and receive
        the dealAmount. Known values are: "Party1" and "Party2".
    receiver : str or ~analyticsapi.models.PartyEnum
        The party (Party1 or Party2) who will receive the contraAmount and pay
        the dealAmount. Known values are: "Party1" and "Party2".
    """

    quoted_currency: str = rest_field(name="quotedCurrency")
    """Quoted currency code, expressed in ISO 4217 alphabetical format (e.g., 'CHF'). Required."""
    base_currency: str = rest_field(name="baseCurrency")
    """Base  currency code, expressed in ISO 4217 alphabetical format (e.g., 'CHF'). Required."""
    deal_amount: Optional[float] = rest_field(name="dealAmount")
    """The amount of the deal (base) currency bought or sold."""
    contra_amount: Optional[float] = rest_field(name="contraAmount")
    """The amount of contraCcy exchanged to buy or sell the amount of the deal (base) currency.\"."""
    rate: Optional["_models.FxRate"] = rest_field()
    """Exchange rate agreed by counterparties."""
    start_date: Optional["_models.Date"] = rest_field(name="startDate")
    """The start date of the instrument. Possible values are: AdjustableDate object - requires a date
     expressed in ISO 8601 format: YYYY-MM-DD (e.g., '2021-01-01').
     Or a RelativeAdjustableDate - requires a tenor expressed as a code indicating the period
     between referenceDate(default=startDate) to endDate of the instrument (e.g., '6M', '1Y').
     Only NextBusinessDay is supported for DateMovingConvention.
     For spot date, tenor can only be \"SN\" (spot next) or \"SW\" (spot week).
     Default is a spot date."""
    end_date: Optional["_models.Date"] = rest_field(name="endDate")
    """The maturity date of the instrument. Possible values are: AdjustableDate object - requires a
     date expressed in ISO 8601 format: YYYY-MM-DD (e.g., '2021-01-01').
     Or a RelativeAdjustableDate - requires a tenor expressed as a code indicating the period
     between referenceDate(default=startDate) to endDate of the instrument (e.g., '6M', '1Y').
     Only NextBusinessDay is supported for DateMovingConvention.
     For spot date, tenor can only be \"SN\" (spot next) or \"SW\" (spot week)."""
    payer: Optional[Union[str, "_models.PartyEnum"]] = rest_field()
    """The party (Party1 or Party2) who will pay the contraAmount and receive the dealAmount. Known
     values are: \"Party1\" and \"Party2\"."""
    receiver: Optional[Union[str, "_models.PartyEnum"]] = rest_field()
    """The party (Party1 or Party2) who will receive the contraAmount and pay the dealAmount. Known
     values are: \"Party1\" and \"Party2\"."""

    @overload
    def __init__(
        self,
        *,
        quoted_currency: str,
        base_currency: str,
        deal_amount: Optional[float] = None,
        contra_amount: Optional[float] = None,
        rate: Optional["_models.FxRate"] = None,
        start_date: Optional["_models.Date"] = None,
        end_date: Optional["_models.Date"] = None,
        payer: Optional[Union[str, "_models.PartyEnum"]] = None,
        receiver: Optional[Union[str, "_models.PartyEnum"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardDefinition(FxSpotDefinition):
    """Definition of the Fx Forward.

    Attributes
    ----------
    quoted_currency : str
        Quoted currency code, expressed in ISO 4217 alphabetical format (e.g.,
        'CHF'). Required.
    base_currency : str
        Base  currency code, expressed in ISO 4217 alphabetical format (e.g.,
        'CHF'). Required.
    deal_amount : float
        The amount of the deal (base) currency bought or sold.
    contra_amount : float
        The amount of contraCcy exchanged to buy or sell the amount of the deal
        (base) currency.".
    rate : ~analyticsapi.models.FxRate
        Exchange rate agreed by counterparties.
    start_date : ~analyticsapi.models.Date
        The start date of the instrument. Possible values are: AdjustableDate
        object - requires a date expressed in ISO 8601 format: YYYY-MM-DD
        (e.g., '2021-01-01'). Or a RelativeAdjustableDate - requires a tenor
        expressed as a code indicating the period between
        referenceDate(default=startDate) to endDate of the instrument (e.g.,
        '6M', '1Y'). Only NextBusinessDay is supported for
        DateMovingConvention. For spot date, tenor can only be "SN" (spot next)
        or "SW" (spot week). Default is a spot date.
    end_date : ~analyticsapi.models.Date
        The maturity date of the instrument. Possible values are:
        AdjustableDate object - requires a date expressed in ISO 8601 format:
        YYYY-MM-DD (e.g., '2021-01-01'). Or a RelativeAdjustableDate - requires
        a tenor expressed as a code indicating the period between
        referenceDate(default=startDate) to endDate of the instrument (e.g.,
        '6M', '1Y'). Only NextBusinessDay is supported for
        DateMovingConvention. For spot date, tenor can only be "SN" (spot next)
        or "SW" (spot week).
    payer : str or ~analyticsapi.models.PartyEnum
        The party (Party1 or Party2) who will pay the contraAmount and receive
        the dealAmount. Known values are: "Party1" and "Party2".
    receiver : str or ~analyticsapi.models.PartyEnum
        The party (Party1 or Party2) who will receive the contraAmount and pay
        the dealAmount. Known values are: "Party1" and "Party2".
    settlement_type : str or ~analyticsapi.models.SettlementType
        The Flag that specifies how the instrument is settled (e.g. Physical,
        Cash). Known values are: "Cash" and "Physical".
    """

    settlement_type: Optional[Union[str, "_models.SettlementType"]] = rest_field(name="settlementType")
    """The Flag that specifies how the instrument is settled (e.g. Physical, Cash). Known values are:
     \"Cash\" and \"Physical\"."""

    @overload
    def __init__(
        self,
        *,
        quoted_currency: str,
        base_currency: str,
        deal_amount: Optional[float] = None,
        contra_amount: Optional[float] = None,
        rate: Optional["_models.FxRate"] = None,
        start_date: Optional["_models.Date"] = None,
        end_date: Optional["_models.Date"] = None,
        payer: Optional[Union[str, "_models.PartyEnum"]] = None,
        receiver: Optional[Union[str, "_models.PartyEnum"]] = None,
        settlement_type: Optional[Union[str, "_models.SettlementType"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["settlement_type"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class FxForwardDefinitionInstrument(_model_base.Model):
    """An array of objects describing a curve or an instrument.
    Please provide either a full definition (for a user-defined curve/instrument), or reference to
    a curve/instrument definition saved in the platform, or the code identifying the existing
    curve/instrument.

    Attributes
    ----------
    definition : ~analyticsapi.models.FxForwardDefinition
        The object that describes the definition of the instrument.
    reference : str
        The identifier of a resource (instrument definition, curve definition)
        that is already in the platform.
    code : str
        The unique public code used to identify an instrument that exists on
        the market (ISIN, RIC, etc.).
    """

    definition: Optional["_models.FxForwardDefinition"] = rest_field()
    """The object that describes the definition of the instrument."""
    reference: Optional[str] = rest_field()
    """The identifier of a resource (instrument definition, curve definition) that is already in the
     platform."""
    code: Optional[str] = rest_field()
    """The unique public code used to identify an instrument that exists on the market (ISIN, RIC,
     etc.)."""

    @overload
    def __init__(
        self,
        *,
        definition: Optional["_models.FxForwardDefinition"] = None,
        reference: Optional[str] = None,
        code: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardFromTemplateResponse(_model_base.Model):
    """Object defining the response to the creation of a FxForward from a reference to a template and
    a list of overridden values.

    Attributes
    ----------
    data : ~analyticsapi.models.FxForwardDefinition
        An object that describes the instrument generated by the request.
        Required.
    """

    data: "_models.FxForwardDefinition" = rest_field()
    """An object that describes the instrument generated by the request. Required."""

    @overload
    def __init__(
        self,
        data: "_models.FxForwardDefinition",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["data"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class FxForwardInfo(_model_base.Model):
    """Object defining the related links available on a FxForward resource.

    Readonly variables are only populated by the server, and will be ignored when sending a request.

    Attributes
    ----------
    type : str or ~analyticsapi.models.FX_FORWARD
        Property defining the type of the resource.
    id : str
        Unique identifier of the FxForward.
    location : ~analyticsapi.models.Location
        Object defining metadata for the FxForward. Required.
    description : ~analyticsapi.models.Description
        Object defining the FxForward.
    """

    type: Optional[Literal[ResourceType.FX_FORWARD]] = rest_field(visibility=["read"], default=ResourceType.FX_FORWARD)
    """Property defining the type of the resource."""
    id: Optional[str] = rest_field(visibility=["read"])
    """Unique identifier of the FxForward."""
    location: "_models.Location" = rest_field(visibility=["read", "create"])
    """Object defining metadata for the FxForward. Required."""
    description: Optional["_models.Description"] = rest_field()
    """Object defining the FxForward."""

    @overload
    def __init__(
        self,
        *,
        location: "_models.Location",
        description: Optional["_models.Description"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardOverride(_model_base.Model):
    """Object that can be used to override the built-in properties of a FxForward template in a
    request.

    Attributes
    ----------
    deal_amount : float
        The amount of the deal.
    contra_amount : float
        The amount expressed in the foreign currency. It is required if no Fx
        Rate is provided.
    rate : ~analyticsapi.models.FxRate
        The exchange rate of the transaction. It is required if no contraAmount
        is provided.
    start_date : ~analyticsapi.models.Date
        The effective date of the deal.
    end_date : ~analyticsapi.models.Date
        The maturity date of the deal.
    settlement_type : str or ~analyticsapi.models.SettlementType
        The type of settlement (Cash or Physical). This used to identify non
        deliverable forwards. Known values are: "Cash" and "Physical".
    """

    deal_amount: Optional[float] = rest_field(name="dealAmount")
    """The amount of the deal."""
    contra_amount: Optional[float] = rest_field(name="contraAmount")
    """The amount expressed in the foreign currency. It is required if no Fx Rate is provided."""
    rate: Optional["_models.FxRate"] = rest_field()
    """The exchange rate of the transaction. It is required if no contraAmount is provided."""
    start_date: Optional["_models.Date"] = rest_field(name="startDate")
    """The effective date of the deal."""
    end_date: Optional["_models.Date"] = rest_field(name="endDate")
    """The maturity date of the deal."""
    settlement_type: Optional[Union[str, "_models.SettlementType"]] = rest_field(name="settlementType")
    """The type of settlement (Cash or Physical). This used to identify non deliverable forwards.
     Known values are: \"Cash\" and \"Physical\"."""

    @overload
    def __init__(
        self,
        *,
        deal_amount: Optional[float] = None,
        contra_amount: Optional[float] = None,
        rate: Optional["_models.FxRate"] = None,
        start_date: Optional["_models.Date"] = None,
        end_date: Optional["_models.Date"] = None,
        settlement_type: Optional[Union[str, "_models.SettlementType"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardPriceResponse(_model_base.Model):
    """Object defining the response of a pricing request for a FxForward instrument that exists in the
    platform.

    Attributes
    ----------
    data : ~analyticsapi.models.FxForwardAnalyticsPricingOnResourceResponseData
        Required.
    """

    data: "_models.FxForwardAnalyticsPricingOnResourceResponseData" = rest_field()
    """Required."""

    @overload
    def __init__(
        self,
        data: "_models.FxForwardAnalyticsPricingOnResourceResponseData",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["data"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class FxPricingAnalysis(_model_base.Model):
    """The object that contains the analytic fields that are linked to a pre-trade analysis of the
    instrument.

    Attributes
    ----------
    fx_spot : ~analyticsapi.models.BidAskSimpleValues
        The spot price for the currency pair. The field returns the following
        values: Bid (Bid value) and Ask (Ask value).
    deal_amount : float
        The amount of the deal (base) currency bought or sold.
    contra_amount : float
        The amount of contraCcy exchanged to buy or sell the amount of the deal
        (base) currency.
    """

    fx_spot: Optional["_models.BidAskSimpleValues"] = rest_field(name="fxSpot")
    """The spot price for the currency pair. The field returns the following values: Bid (Bid value)
     and Ask (Ask value)."""
    deal_amount: Optional[float] = rest_field(name="dealAmount")
    """The amount of the deal (base) currency bought or sold."""
    contra_amount: Optional[float] = rest_field(name="contraAmount")
    """The amount of contraCcy exchanged to buy or sell the amount of the deal (base) currency."""

    @overload
    def __init__(
        self,
        *,
        fx_spot: Optional["_models.BidAskSimpleValues"] = None,
        deal_amount: Optional[float] = None,
        contra_amount: Optional[float] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardPricingAnalysis(FxPricingAnalysis):
    """The object that contains the analytic fields that are linked to a pre-trade analysis of the
    instrument.

    Attributes
    ----------
    fx_spot : ~analyticsapi.models.BidAskSimpleValues
        The spot price for the currency pair. The field returns the following
        values: Bid (Bid value) and Ask (Ask value).
    deal_amount : float
        The amount of the deal (base) currency bought or sold.
    contra_amount : float
        The amount of contraCcy exchanged to buy or sell the amount of the deal
        (base) currency.
    fx_swaps_ccy1 : ~analyticsapi.models.BidAskSimpleValues
        FX Swap points for the currency 1 against the reference currency. By
        default, the reference currency is USD.
    fx_swaps_ccy2 : ~analyticsapi.models.BidAskSimpleValues
        FX Swap points for the currency 2 against the reference currency. By
        default, the reference currency is USD.
    fx_swaps_ccy1_ccy2 : ~analyticsapi.models.BidAskSimpleValues
        FX Swap points for the FX cross currency pair.
    fx_outright_ccy1_ccy2 : ~analyticsapi.models.BidAskSimpleValues
        FX outright rate for the FX cross currency pair.
    rate : float
        The contractual exchange rate agreed by counterparties. Required.
    settlement_amount : float
        Settlement amount in case of an FxNonDeliverableForward (NDF) contract.
        The value is expressed in the settlement currency.
    """

    fx_swaps_ccy1: Optional["_models.BidAskSimpleValues"] = rest_field(name="fxSwapsCcy1")
    """FX Swap points for the currency 1 against the reference currency. By default, the reference
     currency is USD."""
    fx_swaps_ccy2: Optional["_models.BidAskSimpleValues"] = rest_field(name="fxSwapsCcy2")
    """FX Swap points for the currency 2 against the reference currency. By default, the reference
     currency is USD."""
    fx_swaps_ccy1_ccy2: Optional["_models.BidAskSimpleValues"] = rest_field(name="fxSwapsCcy1Ccy2")
    """FX Swap points for the FX cross currency pair."""
    fx_outright_ccy1_ccy2: Optional["_models.BidAskSimpleValues"] = rest_field(name="fxOutrightCcy1Ccy2")
    """FX outright rate for the FX cross currency pair."""
    rate: float = rest_field()
    """The contractual exchange rate agreed by counterparties. Required."""
    settlement_amount: Optional[float] = rest_field(name="settlementAmount")
    """Settlement amount in case of an FxNonDeliverableForward (NDF) contract. The value is expressed
     in the settlement currency."""

    @overload
    def __init__(
        self,
        *,
        rate: float,
        fx_spot: Optional["_models.BidAskSimpleValues"] = None,
        deal_amount: Optional[float] = None,
        contra_amount: Optional[float] = None,
        fx_swaps_ccy1: Optional["_models.BidAskSimpleValues"] = None,
        fx_swaps_ccy2: Optional["_models.BidAskSimpleValues"] = None,
        fx_swaps_ccy1_ccy2: Optional["_models.BidAskSimpleValues"] = None,
        fx_outright_ccy1_ccy2: Optional["_models.BidAskSimpleValues"] = None,
        settlement_amount: Optional[float] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardResponse(_model_base.Model):
    """Object defining the response for a single FxForward instrument.

    Attributes
    ----------
    data : ~analyticsapi.models.FxForward
        Required.
    meta : ~analyticsapi.models.MetaData
    """

    data: "_models.FxForward" = rest_field()
    """Required."""
    meta: Optional["_models.MetaData"] = rest_field()

    @overload
    def __init__(
        self,
        *,
        data: "_models.FxForward",
        meta: Optional["_models.MetaData"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxRisk(_model_base.Model):
    """The object that contains the analytic fields that are linked to a risk analysis of the
    instrument.

    Attributes
    ----------
    delta_percent : float
        The change in the instrument's price or market value caused by a one-
        unit change in the price of the underlying asset, or by 1bp change in
        the swap rate for a swaption, or by 100bp change in the outright for FX
        instruments. The value is expressed in percentages.
    delta_amount_in_deal_ccy : float
        The change in the instrument's price or market value caused by a one-
        unit change in the price of the underlying asset, or by 1bp change in
        the swap rate for a swaption, or by 100bp change in the outright for FX
        instruments. The value is expressed in the deal currency.
    delta_amount_in_contra_ccy : float
        The change in the instrument's price or market value caused by a one-
        unit change in the price of the underlying asset, or by 1bp change in
        the swap rate for a swaption, or by 100bp change in the outright for FX
        instruments. The value is expressed in the contra (quote) currency.
    """

    delta_percent: Optional[float] = rest_field(name="deltaPercent")
    """The change in the instrument's price or market value caused by a one-unit change in the price
     of the underlying asset, or by 1bp change in the swap rate for a swaption, or by 100bp change
     in the outright for FX instruments. The value is expressed in percentages."""
    delta_amount_in_deal_ccy: Optional[float] = rest_field(name="deltaAmountInDealCcy")
    """The change in the instrument's price or market value caused by a one-unit change in the price
     of the underlying asset, or by 1bp change in the swap rate for a swaption, or by 100bp change
     in the outright for FX instruments. The value is expressed in the deal currency."""
    delta_amount_in_contra_ccy: Optional[float] = rest_field(name="deltaAmountInContraCcy")
    """The change in the instrument's price or market value caused by a one-unit change in the price
     of the underlying asset, or by 1bp change in the swap rate for a swaption, or by 100bp change
     in the outright for FX instruments. The value is expressed in the contra (quote) currency."""

    @overload
    def __init__(
        self,
        *,
        delta_percent: Optional[float] = None,
        delta_amount_in_deal_ccy: Optional[float] = None,
        delta_amount_in_contra_ccy: Optional[float] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardRisk(FxRisk):
    """The object that contains the analytic fields that are linked to a risk analysis of the
    instrument.

    Attributes
    ----------
    delta_percent : float
        The change in the instrument's price or market value caused by a one-
        unit change in the price of the underlying asset, or by 1bp change in
        the swap rate for a swaption, or by 100bp change in the outright for FX
        instruments. The value is expressed in percentages.
    delta_amount_in_deal_ccy : float
        The change in the instrument's price or market value caused by a one-
        unit change in the price of the underlying asset, or by 1bp change in
        the swap rate for a swaption, or by 100bp change in the outright for FX
        instruments. The value is expressed in the deal currency.
    delta_amount_in_contra_ccy : float
        The change in the instrument's price or market value caused by a one-
        unit change in the price of the underlying asset, or by 1bp change in
        the swap rate for a swaption, or by 100bp change in the outright for FX
        instruments. The value is expressed in the contra (quote) currency.
    """

    @overload
    def __init__(
        self,
        *,
        delta_percent: Optional[float] = None,
        delta_amount_in_deal_ccy: Optional[float] = None,
        delta_amount_in_contra_ccy: Optional[float] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardTemplateDefinition(InstrumentTemplateDefinition, discriminator="FxForward"):
    """FxForwardTemplateDefinition.

    Attributes
    ----------
    instrument_type : str or ~analyticsapi.models.FX_FORWARD
        Required. A FX forward contract contract.
    template : ~analyticsapi.models.FxForwardDefinition
        Required.
    """

    instrument_type: Literal[InstrumentTemplateTypeEnum.FX_FORWARD] = rest_discriminator(name="instrumentType")  # type: ignore
    """Required. A FX forward contract contract."""
    template: "_models.FxForwardDefinition" = rest_field()
    """Required."""

    @overload
    def __init__(
        self,
        template: "_models.FxForwardDefinition",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, instrument_type=InstrumentTemplateTypeEnum.FX_FORWARD, **kwargs)


class FxValuation(_model_base.Model):
    """The object that contains the analytic fields that are linked to a post-trade analysis of the
    instrument.

    Attributes
    ----------
    market_value_in_deal_ccy : float
        The market value of the instrument. The value is expressed in the deal
        currency.
    market_value_in_contra_ccy : float
        The market value of the instrument. The value is expressed in the
        contra (quote) currency.
    market_value_in_report_ccy : float
        The present value of the future cash flow in the reporting currency.
    """

    market_value_in_deal_ccy: Optional[float] = rest_field(name="marketValueInDealCcy")
    """The market value of the instrument. The value is expressed in the deal currency."""
    market_value_in_contra_ccy: Optional[float] = rest_field(name="marketValueInContraCcy")
    """The market value of the instrument. The value is expressed in the contra (quote) currency."""
    market_value_in_report_ccy: Optional[float] = rest_field(name="marketValueInReportCcy")
    """The present value of the future cash flow in the reporting currency."""

    @overload
    def __init__(
        self,
        *,
        market_value_in_deal_ccy: Optional[float] = None,
        market_value_in_contra_ccy: Optional[float] = None,
        market_value_in_report_ccy: Optional[float] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxForwardValuation(FxValuation):
    """The object that contains the analytic fields that are linked to a post-trade analysis of the
    instrument.

    Attributes
    ----------
    market_value_in_deal_ccy : float
        The market value of the instrument. The value is expressed in the deal
        currency.
    market_value_in_contra_ccy : float
        The market value of the instrument. The value is expressed in the
        contra (quote) currency.
    market_value_in_report_ccy : float
        The present value of the future cash flow in the reporting currency.
    discount_factor : float
        The ratio derived from EndDate and used to calculate the present value
        of future cash flow for the instrument at MarketDataDate.
    """

    discount_factor: Optional[float] = rest_field(name="discountFactor")
    """The ratio derived from EndDate and used to calculate the present value of future cash flow for
     the instrument at MarketDataDate."""

    @overload
    def __init__(
        self,
        *,
        market_value_in_deal_ccy: Optional[float] = None,
        market_value_in_contra_ccy: Optional[float] = None,
        market_value_in_report_ccy: Optional[float] = None,
        discount_factor: Optional[float] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["discount_factor"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class FxForwardValuationResponse(_model_base.Model):
    """Object defining the response of a valuation request for a FxForward instrument that exists in
    the platform.

    Attributes
    ----------
    data : ~analyticsapi.models.FxForwardAnalyticsValuationOnResourceResponseData
        Required.
    """

    data: "_models.FxForwardAnalyticsValuationOnResourceResponseData" = rest_field()
    """Required."""

    @overload
    def __init__(
        self,
        data: "_models.FxForwardAnalyticsValuationOnResourceResponseData",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["data"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class FxOptionVolSurfaceChoice(_model_base.Model):
    """The object to provide either a reference to an fx volatility surface stored in the platform or
    3rd party volatilities.

    Attributes
    ----------
    reference : str
        The reference to a volatility surface stored in the platform.
    surface : ~analyticsapi.models.FxVolSurfaceInput
        The volatility surface data.
    """

    reference: Optional[str] = rest_field()
    """The reference to a volatility surface stored in the platform."""
    surface: Optional["_models.FxVolSurfaceInput"] = rest_field()
    """The volatility surface data."""

    @overload
    def __init__(
        self,
        *,
        reference: Optional[str] = None,
        surface: Optional["_models.FxVolSurfaceInput"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxOutrightCurve(Curve, discriminator="FxOutrightCurve"):
    """The model defining the output of an fx forward curve calculation.

    Attributes
    ----------
    curve_type : str or ~analyticsapi.models.FX_OUTRIGHT_CURVE
        Required.
    cross_currency : str
        The ISO code of the cross currency pair. Required.
    points : list[~analyticsapi.models.FxOutrightCurvePoint]
        The list of output points. Required.  The default value is None, needs
        to be assigned before using.
    """

    curve_type: Literal[CurveTypeEnum.FX_OUTRIGHT_CURVE] = rest_discriminator(name="curveType")  # type: ignore
    """Required."""
    cross_currency: str = rest_field(name="crossCurrency")
    """The ISO code of the cross currency pair. Required."""
    points: List["_models.FxOutrightCurvePoint"] = rest_field()
    """The list of output points. Required."""

    @overload
    def __init__(
        self,
        *,
        cross_currency: str,
        points: List["_models.FxOutrightCurvePoint"],
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, curve_type=CurveTypeEnum.FX_OUTRIGHT_CURVE, **kwargs)


class FxOutrightCurveDescription(_model_base.Model):
    """An object to define a FX Outright Curve.

    Attributes
    ----------
    curve_type : str or ~analyticsapi.models.FX_OUTRIGHT_CURVE
        Required.
    cross_currency : str
        The ISO code of the cross currency pair. Required.
    points : list[~analyticsapi.models.FxOutrightCurvePoint]
        The list of output points. Required.  The default value is None, needs
        to be assigned before using.
    """

    curve_type: Literal[CurveTypeEnum.FX_OUTRIGHT_CURVE] = rest_field(name="curveType")
    """Required."""
    cross_currency: str = rest_field(name="crossCurrency")
    """The ISO code of the cross currency pair. Required."""
    points: List["_models.FxOutrightCurvePoint"] = rest_field()
    """The list of output points. Required."""

    @overload
    def __init__(
        self,
        *,
        curve_type: Literal[CurveTypeEnum.FX_OUTRIGHT_CURVE],
        cross_currency: str,
        points: List["_models.FxOutrightCurvePoint"],
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxOutrightCurvePoint(_model_base.Model):
    """An object that contains the values applied to the FX Forward curve point.

    Attributes
    ----------
    start_date : ~datetime.date
        The start date of the curve point tenor. The value is expressed in ISO
        8601 format: YYYY-MM-DD (e.g., '2023-01-01'). Required.
    tenor : str
        The code indicating the period between the start date and the end date
        of the curve point (e.g., '1M', 1Y'). Required.
    end_date : ~datetime.date
        The end date of the curve point tenor. The value is expressed in ISO
        8601 format: YYYY-MM-DD (e.g., '2023-01-01'). Required.
    outright : ~analyticsapi.models.BidAskMidSimpleValues
        The outright exchange rate between the two currencies. Required.
    instruments : list[~analyticsapi.models.CurvePointRelatedInstruments]
        An array of objects that contains instruments used to calculate the
        curve point.  The default value is None, needs to be assigned before
        using.
    """

    start_date: datetime.date = rest_field(name="startDate")
    """The start date of the curve point tenor. The value is expressed in ISO 8601 format: YYYY-MM-DD
     (e.g., '2023-01-01'). Required."""
    tenor: str = rest_field()
    """The code indicating the period between the start date and the end date of the curve point
     (e.g., '1M', 1Y'). Required."""
    end_date: datetime.date = rest_field(name="endDate")
    """The end date of the curve point tenor. The value is expressed in ISO 8601 format: YYYY-MM-DD
     (e.g., '2023-01-01'). Required."""
    outright: "_models.BidAskMidSimpleValues" = rest_field()
    """The outright exchange rate between the two currencies. Required."""
    instruments: Optional[List["_models.CurvePointRelatedInstruments"]] = rest_field()
    """An array of objects that contains instruments used to calculate the curve point."""

    @overload
    def __init__(
        self,
        *,
        start_date: datetime.date,
        tenor: str,
        end_date: datetime.date,
        outright: "_models.BidAskMidSimpleValues",
        instruments: Optional[List["_models.CurvePointRelatedInstruments"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxPricingParameters(BasePricingParameters):
    """An object that describes Fx-related calculation parameters.

    Attributes
    ----------
    valuation_date : ~datetime.date
        The date at which the instrument is valued. The value is expressed in
        ISO 8601 format: YYYY-MM-DD (e.g., '2021-01-01').
    report_currency : str
        The reporting currency. The value is expressed in ISO 4217 alphabetical
        format (e.g., 'GBP'). Default is USD.
    ignore_reference_currency_holidays : bool
        Boolean property that determines if reference currency’s holidays are
        taken into account during date calculation.
    reference_currency : str
        An object to specify the reference currency.
    """

    ignore_reference_currency_holidays: Optional[bool] = rest_field(name="ignoreReferenceCurrencyHolidays")
    """Boolean property that determines if reference currency’s holidays are taken into account during
     date calculation."""
    reference_currency: Optional[str] = rest_field(name="referenceCurrency")
    """An object to specify the reference currency."""

    @overload
    def __init__(
        self,
        *,
        valuation_date: Optional[datetime.date] = None,
        report_currency: Optional[str] = None,
        ignore_reference_currency_holidays: Optional[bool] = None,
        reference_currency: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxRate(_model_base.Model):
    """Definition of a FX rate.

    Attributes
    ----------
    value : float
        The contractual exchange rate agreed by the parties.
    scaling_factor : float
        The factor used for quoting cross currency rates.
    rate_precision : int
        Number of decimal digits of precision for the FX rate value.
    """

    value: Optional[float] = rest_field()
    """The contractual exchange rate agreed by the parties."""
    scaling_factor: Optional[float] = rest_field(name="scalingFactor")
    """The factor used for quoting cross currency rates."""
    rate_precision: Optional[int] = rest_field(name="ratePrecision")
    """Number of decimal digits of precision for the FX rate value."""

    @overload
    def __init__(
        self,
        *,
        value: Optional[float] = None,
        scaling_factor: Optional[float] = None,
        rate_precision: Optional[int] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxSpot(_model_base.Model):
    """Object defning an Fx Spot resource.

    Readonly variables are only populated by the server, and will be ignored when sending a request.

    Attributes
    ----------
    type : str or ~analyticsapi.models.FX_SPOT
        Property defining the type of the resource.
    id : str
        Unique identifier of the FxSpot.
    location : ~analyticsapi.models.Location
        Object defining the location of the FxSpot in the platform. Required.
    description : ~analyticsapi.models.Description
        Object defining metadata for the FxSpot.
    definition : ~analyticsapi.models.FxSpotDefinition
        Object defining the FxSpot. Required.
    """

    type: Optional[Literal[ResourceType.FX_SPOT]] = rest_field(visibility=["read"], default=ResourceType.FX_SPOT)
    """Property defining the type of the resource."""
    id: Optional[str] = rest_field(visibility=["read"])
    """Unique identifier of the FxSpot."""
    location: "_models.Location" = rest_field(visibility=["read", "create"])
    """Object defining the location of the FxSpot in the platform. Required."""
    description: Optional["_models.Description"] = rest_field()
    """Object defining metadata for the FxSpot."""
    definition: "_models.FxSpotDefinition" = rest_field()
    """Object defining the FxSpot. Required."""

    @overload
    def __init__(
        self,
        *,
        location: "_models.Location",
        definition: "_models.FxSpotDefinition",
        description: Optional["_models.Description"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxSpotAnalyticsDescription(FxAnalyticsDescription):
    """The object that contains the analytic fields that describe the instrument.

    Attributes
    ----------
    valuation_date : ~datetime.date
        The date at which the instrument is valued. The date is expressed in
        ISO 8601 format: YYYY-MM-DDT[hh]:[mm]:[ss]Z (e.g.,
        '2021-01-01T00:00:00Z').
    start_date : ~analyticsapi.models.AdjustedDate
        "An object describing a start date of the instrument.".
    end_date : ~analyticsapi.models.AdjustedDate
        "An object describing a maturity date of the instrument.".
    """

    @overload
    def __init__(
        self,
        *,
        valuation_date: Optional[datetime.date] = None,
        start_date: Optional["_models.AdjustedDate"] = None,
        end_date: Optional["_models.AdjustedDate"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxSpotAnalyticsPricingOnResourceResponseData(_model_base.Model):  # pylint: disable=name-too-long
    """FxSpotAnalyticsPricingOnResourceResponseData.

    Attributes
    ----------
    resource : ~analyticsapi.models.FxSpot
        Definition of the resource.
    pricing_preferences : ~analyticsapi.models.FxPricingParameters
        The parameters that control the computation of the analytics.
    analytics : ~analyticsapi.models.FxSpotAnalyticsPricingResponseWithError
        The result of the calculation request.
    market_data : ~analyticsapi.models.MarketData
        The market data used to compute the analytics.
    """

    resource: Optional["_models.FxSpot"] = rest_field()
    """Definition of the resource."""
    pricing_preferences: Optional["_models.FxPricingParameters"] = rest_field(name="pricingPreferences")
    """The parameters that control the computation of the analytics."""
    analytics: Optional["_models.FxSpotAnalyticsPricingResponseWithError"] = rest_field()
    """The result of the calculation request."""
    market_data: Optional["_models.MarketData"] = rest_field(name="marketData")
    """The market data used to compute the analytics."""

    @overload
    def __init__(
        self,
        *,
        resource: Optional["_models.FxSpot"] = None,
        pricing_preferences: Optional["_models.FxPricingParameters"] = None,
        analytics: Optional["_models.FxSpotAnalyticsPricingResponseWithError"] = None,
        market_data: Optional["_models.MarketData"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxSpotAnalyticsPricingResponseData(_model_base.Model):
    """FxSpotAnalyticsPricingResponseData.

    Attributes
    ----------
    definitions : list[~analyticsapi.models.FxSpotDefinitionInstrument]
        The default value is None, needs to be assigned before using.
    pricing_preferences : ~analyticsapi.models.FxPricingParameters
        The parameters that control the computation of the analytics.
    analytics : list[~analyticsapi.models.FxSpotAnalyticsPricingResponseWithError]
        The result of the calculation request.  The default value is None,
        needs to be assigned before using.
    market_data : ~analyticsapi.models.MarketData
        The market data used to compute the analytics.
    """

    definitions: Optional[List["_models.FxSpotDefinitionInstrument"]] = rest_field()
    pricing_preferences: Optional["_models.FxPricingParameters"] = rest_field(name="pricingPreferences")
    """The parameters that control the computation of the analytics."""
    analytics: Optional[List["_models.FxSpotAnalyticsPricingResponseWithError"]] = rest_field()
    """The result of the calculation request."""
    market_data: Optional["_models.MarketData"] = rest_field(name="marketData")
    """The market data used to compute the analytics."""

    @overload
    def __init__(
        self,
        *,
        definitions: Optional[List["_models.FxSpotDefinitionInstrument"]] = None,
        pricing_preferences: Optional["_models.FxPricingParameters"] = None,
        analytics: Optional[List["_models.FxSpotAnalyticsPricingResponseWithError"]] = None,
        market_data: Optional["_models.MarketData"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxSpotAnalyticsPricingResponseWithError(_model_base.Model):
    """A model template describing a response with an error for a given object.

    Attributes
    ----------
    description : ~analyticsapi.models.FxSpotAnalyticsDescription
        The analytic fields that describe the instrument.
    pricing_analysis : ~analyticsapi.models.FxSpotPricingAnalysis
        The analytic fields that are linked to a pre-trade analysis of the
        instrument.
    greeks : ~analyticsapi.models.FxSpotRisk
        The analytic fields that are linked to a risk analysis of the
        instrument.
    processing_information : list[str]
        A list of messages providing additional information about the
        processing of the request.  The default value is None, needs to be
        assigned before using.
    error : ~analyticsapi.models.ServiceError
        The error message for the calculation in case of a non-blocking error.
    """

    description: Optional["_models.FxSpotAnalyticsDescription"] = rest_field()
    """The analytic fields that describe the instrument."""
    pricing_analysis: Optional["_models.FxSpotPricingAnalysis"] = rest_field(name="pricingAnalysis")
    """The analytic fields that are linked to a pre-trade analysis of the instrument."""
    greeks: Optional["_models.FxSpotRisk"] = rest_field()
    """The analytic fields that are linked to a risk analysis of the instrument."""
    processing_information: Optional[List[str]] = rest_field(name="processingInformation")
    """A list of messages providing additional information about the processing of the request."""
    error: Optional["_models.ServiceError"] = rest_field()
    """The error message for the calculation in case of a non-blocking error."""

    @overload
    def __init__(
        self,
        *,
        description: Optional["_models.FxSpotAnalyticsDescription"] = None,
        pricing_analysis: Optional["_models.FxSpotPricingAnalysis"] = None,
        greeks: Optional["_models.FxSpotRisk"] = None,
        processing_information: Optional[List[str]] = None,
        error: Optional["_models.ServiceError"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxSpotAnalyticsValuationOnResourceResponseData(_model_base.Model):  # pylint: disable=name-too-long
    """FxSpotAnalyticsValuationOnResourceResponseData.

    Attributes
    ----------
    resource : ~analyticsapi.models.FxSpot
        Definition of the resource.
    pricing_preferences : ~analyticsapi.models.FxPricingParameters
        The parameters that control the computation of the analytics.
    analytics : ~analyticsapi.models.FxSpotAnalyticsValuationResponseWithError
        The result of the calculation request.
    market_data : ~analyticsapi.models.MarketData
        The market data used to compute the analytics.
    """

    resource: Optional["_models.FxSpot"] = rest_field()
    """Definition of the resource."""
    pricing_preferences: Optional["_models.FxPricingParameters"] = rest_field(name="pricingPreferences")
    """The parameters that control the computation of the analytics."""
    analytics: Optional["_models.FxSpotAnalyticsValuationResponseWithError"] = rest_field()
    """The result of the calculation request."""
    market_data: Optional["_models.MarketData"] = rest_field(name="marketData")
    """The market data used to compute the analytics."""

    @overload
    def __init__(
        self,
        *,
        resource: Optional["_models.FxSpot"] = None,
        pricing_preferences: Optional["_models.FxPricingParameters"] = None,
        analytics: Optional["_models.FxSpotAnalyticsValuationResponseWithError"] = None,
        market_data: Optional["_models.MarketData"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxSpotAnalyticsValuationResponseData(_model_base.Model):
    """FxSpotAnalyticsValuationResponseData.

    Attributes
    ----------
    definitions : list[~analyticsapi.models.FxSpotDefinitionInstrument]
        The default value is None, needs to be assigned before using.
    pricing_preferences : ~analyticsapi.models.FxPricingParameters
        The parameters that control the computation of the analytics.
    analytics : list[~analyticsapi.models.FxSpotAnalyticsValuationResponseWithError]
        The result of the calculation request.  The default value is None,
        needs to be assigned before using.
    market_data : ~analyticsapi.models.MarketData
        The market data used to compute the analytics.
    """

    definitions: Optional[List["_models.FxSpotDefinitionInstrument"]] = rest_field()
    pricing_preferences: Optional["_models.FxPricingParameters"] = rest_field(name="pricingPreferences")
    """The parameters that control the computation of the analytics."""
    analytics: Optional[List["_models.FxSpotAnalyticsValuationResponseWithError"]] = rest_field()
    """The result of the calculation request."""
    market_data: Optional["_models.MarketData"] = rest_field(name="marketData")
    """The market data used to compute the analytics."""

    @overload
    def __init__(
        self,
        *,
        definitions: Optional[List["_models.FxSpotDefinitionInstrument"]] = None,
        pricing_preferences: Optional["_models.FxPricingParameters"] = None,
        analytics: Optional[List["_models.FxSpotAnalyticsValuationResponseWithError"]] = None,
        market_data: Optional["_models.MarketData"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxSpotAnalyticsValuationResponseWithError(_model_base.Model):  # pylint: disable=name-too-long
    """A model template describing a response with an error for a given object.

    Attributes
    ----------
    description : ~analyticsapi.models.FxSpotAnalyticsDescription
        The analytic fields that describe the instrument.
    valuation : ~analyticsapi.models.FxSpotValuation
        The analytic fields that are linked to a post-trade analysis of the
        instrument.
    greeks : ~analyticsapi.models.FxSpotRisk
        The analytic fields that are linked to a risk analysis of the
        instrument.
    processing_information : list[str]
        A list of messages providing additional information about the
        processing of the request.  The default value is None, needs to be
        assigned before using.
    error : ~analyticsapi.models.ServiceError
        The error message for the calculation in case of a non-blocking error.
    """

    description: Optional["_models.FxSpotAnalyticsDescription"] = rest_field()
    """The analytic fields that describe the instrument."""
    valuation: Optional["_models.FxSpotValuation"] = rest_field()
    """The analytic fields that are linked to a post-trade analysis of the instrument."""
    greeks: Optional["_models.FxSpotRisk"] = rest_field()
    """The analytic fields that are linked to a risk analysis of the instrument."""
    processing_information: Optional[List[str]] = rest_field(name="processingInformation")
    """A list of messages providing additional information about the processing of the request."""
    error: Optional["_models.ServiceError"] = rest_field()
    """The error message for the calculation in case of a non-blocking error."""

    @overload
    def __init__(
        self,
        *,
        description: Optional["_models.FxSpotAnalyticsDescription"] = None,
        valuation: Optional["_models.FxSpotValuation"] = None,
        greeks: Optional["_models.FxSpotRisk"] = None,
        processing_information: Optional[List[str]] = None,
        error: Optional["_models.ServiceError"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxSpotArrayPriceResponse(_model_base.Model):
    """Object defining the response of a pricing request for a collection of FxSpot instruments.

    Attributes
    ----------
    data : ~analyticsapi.models.FxSpotAnalyticsPricingResponseData
        An object that contains calculated analytics, requested, and other data
        used for calculation. Required.
    """

    data: "_models.FxSpotAnalyticsPricingResponseData" = rest_field()
    """An object that contains calculated analytics, requested, and other data used for calculation.
     Required."""

    @overload
    def __init__(
        self,
        data: "_models.FxSpotAnalyticsPricingResponseData",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["data"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class FxSpotArrayValuationResponse(_model_base.Model):
    """Object defining the response of a valuation request for a collection of FxSpot instruments.

    Attributes
    ----------
    data : ~analyticsapi.models.FxSpotAnalyticsValuationResponseData
        An object that contains calculated analytics, requested, and other data
        used for calculation. Required.
    """

    data: "_models.FxSpotAnalyticsValuationResponseData" = rest_field()
    """An object that contains calculated analytics, requested, and other data used for calculation.
     Required."""

    @overload
    def __init__(
        self,
        data: "_models.FxSpotAnalyticsValuationResponseData",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["data"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class FxSpotCollectionLinks(_model_base.Model):
    """Object defining the related links available for a collection of FxSpot instruments.

    Attributes
    ----------
    self_property : ~analyticsapi.models.Link
        Required.
    first : ~analyticsapi.models.Link
    prev : ~analyticsapi.models.Link
    next : ~analyticsapi.models.Link
    last : ~analyticsapi.models.Link
    """

    self_property: "_models.Link" = rest_field(name="self")
    """Required."""
    first: Optional["_models.Link"] = rest_field()
    prev: Optional["_models.Link"] = rest_field()
    next: Optional["_models.Link"] = rest_field()
    last: Optional["_models.Link"] = rest_field()

    @overload
    def __init__(
        self,
        *,
        self_property: "_models.Link",
        first: Optional["_models.Link"] = None,
        prev: Optional["_models.Link"] = None,
        next: Optional["_models.Link"] = None,
        last: Optional["_models.Link"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxSpotCollectionResponse(_model_base.Model):
    """Object defining the paged response for a collection of FxSpot instruments.

    Attributes
    ----------
    data : list[~analyticsapi.models.FxSpotInfo]
        Required.  The default value is None, needs to be assigned before
        using.
    page : int
        The page number of the current page displayed. Minimum value of this
        property is 1. Required.
    item_per_page : int
        Number of items displayed per page. Required.
    total_pages : int
        Total number of pages available for display. Required.
    total_items : int
        Total number of items available for display. Required.
    links : ~analyticsapi.models.FxSpotCollectionLinks
        Links for available operations and/or resources linked to current
        response.
    """

    data: List["_models.FxSpotInfo"] = rest_field()
    """Required."""
    page: int = rest_field()
    """The page number of the current page displayed. Minimum value of this property is 1. Required."""
    item_per_page: int = rest_field(name="itemPerPage")
    """Number of items displayed per page. Required."""
    total_pages: int = rest_field(name="totalPages")
    """Total number of pages available for display. Required."""
    total_items: int = rest_field(name="totalItems")
    """Total number of items available for display. Required."""
    links: Optional["_models.FxSpotCollectionLinks"] = rest_field()
    """Links for available operations and/or resources linked to current response."""

    @overload
    def __init__(
        self,
        *,
        data: List["_models.FxSpotInfo"],
        page: int,
        item_per_page: int,
        total_pages: int,
        total_items: int,
        links: Optional["_models.FxSpotCollectionLinks"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxSpotConstituent(FxConstituent, discriminator="FxSpot"):
    """An object to define constituents that are used to construct the curve.

    Readonly variables are only populated by the server, and will be ignored when sending a request.

    Attributes
    ----------
    quote : ~analyticsapi.models.Quote
        An object to define the quote of the instrument used as a constituent.
    status : list[str]
        A message is returned if the constituent cannot be identified, or
        access for a user to the instrument used as a constituent is denied.
    type : str or ~analyticsapi.models.FX_SPOT
        The type of the instrument used as a constituent. FxSpot is the only
        valid value. Required.
    definition : ~analyticsapi.models.FxSpotConstituentDefinition
        An object to define the instrument used as a constituent.
    """

    type: Literal[FxConstituentEnum.FX_SPOT] = rest_discriminator(name="type")  # type: ignore
    """The type of the instrument used as a constituent. FxSpot is the only valid value. Required."""
    definition: Optional["_models.FxSpotConstituentDefinition"] = rest_field()
    """An object to define the instrument used as a constituent."""

    @overload
    def __init__(
        self,
        *,
        quote: Optional["_models.Quote"] = None,
        definition: Optional["_models.FxSpotConstituentDefinition"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, type=FxConstituentEnum.FX_SPOT, **kwargs)


class FxSpotConstituentDefinition(_model_base.Model):
    """An object to define the FX spot instrument used as a constituent.

    Attributes
    ----------
    template : str
        A pre-defined template can be used as an input by the user. It is the
        currency code of the constituent.
    """

    template: Optional[str] = rest_field()
    """A pre-defined template can be used as an input by the user. It is the currency code of the
     constituent."""

    @overload
    def __init__(
        self,
        template: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["template"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class FxSpotDefinitionInstrument(_model_base.Model):
    """An array of objects describing a curve or an instrument.
    Please provide either a full definition (for a user-defined curve/instrument), or reference to
    a curve/instrument definition saved in the platform, or the code identifying the existing
    curve/instrument.

    Attributes
    ----------
    definition : ~analyticsapi.models.FxSpotDefinition
        The object that describes the definition of the instrument.
    reference : str
        The identifier of a resource (instrument definition, curve definition)
        that is already in the platform.
    code : str
        The unique public code used to identify an instrument that exists on
        the market (ISIN, RIC, etc.).
    """

    definition: Optional["_models.FxSpotDefinition"] = rest_field()
    """The object that describes the definition of the instrument."""
    reference: Optional[str] = rest_field()
    """The identifier of a resource (instrument definition, curve definition) that is already in the
     platform."""
    code: Optional[str] = rest_field()
    """The unique public code used to identify an instrument that exists on the market (ISIN, RIC,
     etc.)."""

    @overload
    def __init__(
        self,
        *,
        definition: Optional["_models.FxSpotDefinition"] = None,
        reference: Optional[str] = None,
        code: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxSpotFromTemplateResponse(_model_base.Model):
    """Object defining the response of the creation of a FxSpot from a reference to a template and a
    list of overridden values.

    Attributes
    ----------
    data : ~analyticsapi.models.FxSpotDefinition
        An object that describes the instrument generated by the request.
        Required.
    """

    data: "_models.FxSpotDefinition" = rest_field()
    """An object that describes the instrument generated by the request. Required."""

    @overload
    def __init__(
        self,
        data: "_models.FxSpotDefinition",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["data"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class FxSpotInfo(_model_base.Model):
    """Object defining the related links available on a FxSpot resource.

    Readonly variables are only populated by the server, and will be ignored when sending a request.

    Attributes
    ----------
    type : str or ~analyticsapi.models.FX_SPOT
        Property defining the type of the resource.
    id : str
        Unique identifier of the FxSpot.
    location : ~analyticsapi.models.Location
        Object defining metadata for the FxSpot. Required.
    description : ~analyticsapi.models.Description
        Object defining the FxSpot.
    """

    type: Optional[Literal[ResourceType.FX_SPOT]] = rest_field(visibility=["read"], default=ResourceType.FX_SPOT)
    """Property defining the type of the resource."""
    id: Optional[str] = rest_field(visibility=["read"])
    """Unique identifier of the FxSpot."""
    location: "_models.Location" = rest_field(visibility=["read", "create"])
    """Object defining metadata for the FxSpot. Required."""
    description: Optional["_models.Description"] = rest_field()
    """Object defining the FxSpot."""

    @overload
    def __init__(
        self,
        *,
        location: "_models.Location",
        description: Optional["_models.Description"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxSpotOverride(_model_base.Model):
    """Object that can be used to override the built-in properties of a FxSpot template in a request.

    Attributes
    ----------
    deal_amount : float
        The amount of the deal.
    contra_amount : float
        The amount expressed in the foreign currency. It is required if no Fx
        Rate is provided.
    rate : ~analyticsapi.models.FxRate
        The exchange rate of the transaction. It is required if no contraAmount
        is provided.
    start_date : ~analyticsapi.models.Date
        The effective date of the deal.
    end_date : ~analyticsapi.models.Date
        The maturity date of the deal.
    """

    deal_amount: Optional[float] = rest_field(name="dealAmount")
    """The amount of the deal."""
    contra_amount: Optional[float] = rest_field(name="contraAmount")
    """The amount expressed in the foreign currency. It is required if no Fx Rate is provided."""
    rate: Optional["_models.FxRate"] = rest_field()
    """The exchange rate of the transaction. It is required if no contraAmount is provided."""
    start_date: Optional["_models.Date"] = rest_field(name="startDate")
    """The effective date of the deal."""
    end_date: Optional["_models.Date"] = rest_field(name="endDate")
    """The maturity date of the deal."""

    @overload
    def __init__(
        self,
        *,
        deal_amount: Optional[float] = None,
        contra_amount: Optional[float] = None,
        rate: Optional["_models.FxRate"] = None,
        start_date: Optional["_models.Date"] = None,
        end_date: Optional["_models.Date"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxSpotPriceResponse(_model_base.Model):
    """Object defining the response of a pricing request for a FxSpot instrument that exists in the
    platform.

    Attributes
    ----------
    data : ~analyticsapi.models.FxSpotAnalyticsPricingOnResourceResponseData
        Required.
    """

    data: "_models.FxSpotAnalyticsPricingOnResourceResponseData" = rest_field()
    """Required."""

    @overload
    def __init__(
        self,
        data: "_models.FxSpotAnalyticsPricingOnResourceResponseData",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["data"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class FxSpotPricingAnalysis(FxPricingAnalysis):
    """The object that contains the analytic fields that are linked to a pre-trade analysis of the
    instrument.

    Attributes
    ----------
    fx_spot : ~analyticsapi.models.BidAskSimpleValues
        The spot price for the currency pair. The field returns the following
        values: Bid (Bid value) and Ask (Ask value).
    deal_amount : float
        The amount of the deal (base) currency bought or sold.
    contra_amount : float
        The amount of contraCcy exchanged to buy or sell the amount of the deal
        (base) currency.
    """

    @overload
    def __init__(
        self,
        *,
        fx_spot: Optional["_models.BidAskSimpleValues"] = None,
        deal_amount: Optional[float] = None,
        contra_amount: Optional[float] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxSpotResponse(_model_base.Model):
    """Object defining the response for a single FxSpot instrument.

    Attributes
    ----------
    data : ~analyticsapi.models.FxSpot
        Required.
    meta : ~analyticsapi.models.MetaData
    """

    data: "_models.FxSpot" = rest_field()
    """Required."""
    meta: Optional["_models.MetaData"] = rest_field()

    @overload
    def __init__(
        self,
        *,
        data: "_models.FxSpot",
        meta: Optional["_models.MetaData"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxSpotRisk(FxRisk):
    """The object that contains the analytic fields that are linked to a risk analysis of the
    instrument.

    Attributes
    ----------
    delta_percent : float
        The change in the instrument's price or market value caused by a one-
        unit change in the price of the underlying asset, or by 1bp change in
        the swap rate for a swaption, or by 100bp change in the outright for FX
        instruments. The value is expressed in percentages.
    delta_amount_in_deal_ccy : float
        The change in the instrument's price or market value caused by a one-
        unit change in the price of the underlying asset, or by 1bp change in
        the swap rate for a swaption, or by 100bp change in the outright for FX
        instruments. The value is expressed in the deal currency.
    delta_amount_in_contra_ccy : float
        The change in the instrument's price or market value caused by a one-
        unit change in the price of the underlying asset, or by 1bp change in
        the swap rate for a swaption, or by 100bp change in the outright for FX
        instruments. The value is expressed in the contra (quote) currency.
    """

    @overload
    def __init__(
        self,
        *,
        delta_percent: Optional[float] = None,
        delta_amount_in_deal_ccy: Optional[float] = None,
        delta_amount_in_contra_ccy: Optional[float] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxSpotTemplateDefinition(InstrumentTemplateDefinition, discriminator="FxSpot"):
    """FxSpotTemplateDefinition.

    Attributes
    ----------
    instrument_type : str or ~analyticsapi.models.FX_SPOT
        Required. A FX spot contract contract.
    template : ~analyticsapi.models.FxSpotDefinition
        Required.
    """

    instrument_type: Literal[InstrumentTemplateTypeEnum.FX_SPOT] = rest_discriminator(name="instrumentType")  # type: ignore
    """Required. A FX spot contract contract."""
    template: "_models.FxSpotDefinition" = rest_field()
    """Required."""

    @overload
    def __init__(
        self,
        template: "_models.FxSpotDefinition",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, instrument_type=InstrumentTemplateTypeEnum.FX_SPOT, **kwargs)


class FxSpotValuation(FxValuation):
    """The object that contains the analytic fields that are linked to a post-trade analysis of the
    instrument.

    Attributes
    ----------
    market_value_in_deal_ccy : float
        The market value of the instrument. The value is expressed in the deal
        currency.
    market_value_in_contra_ccy : float
        The market value of the instrument. The value is expressed in the
        contra (quote) currency.
    market_value_in_report_ccy : float
        The present value of the future cash flow in the reporting currency.
    """

    @overload
    def __init__(
        self,
        *,
        market_value_in_deal_ccy: Optional[float] = None,
        market_value_in_contra_ccy: Optional[float] = None,
        market_value_in_report_ccy: Optional[float] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class FxSpotValuationResponse(_model_base.Model):
    """Object defining the response of a valuation request for a FxForxard instrument that exists in
    the platform.

    Attributes
    ----------
    data : ~analyticsapi.models.FxSpotAnalyticsValuationOnResourceResponseData
        Required.
    """

    data: "_models.FxSpotAnalyticsValuationOnResourceResponseData" = rest_field()
    """Required."""

    @overload
    def __init__(
        self,
        data: "_models.FxSpotAnalyticsValuationOnResourceResponseData",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["data"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class FxVolSurfaceInput(_model_base.Model):
    """The object defining the 3rd party fx volatility surface.

    Attributes
    ----------
    strike_type : str or ~analyticsapi.models.StrikeTypeEnum
        The property that defines the type of the strikes provided in the
        surface points. Required. Known values are: "Absolute", "BasisPoint",
        "Delta", "Moneyness", "Percent", and "Relative".
    model_type : str or ~analyticsapi.models.VolModelTypeEnum
        The property that defines the type of the model (Normal or LogNormal)
        of the volatilities provided in the surface points. Required. Known
        values are: "Normal" and "LogNormal".
    points : list[~analyticsapi.models.VolSurfacePoint]
        The list of volatility points. Required.  The default value is None,
        needs to be assigned before using.
    fx_cross_code : str
        The ISO code of the cross currency pair. Required.
    """

    strike_type: Union[str, "_models.StrikeTypeEnum"] = rest_field(name="strikeType")
    """The property that defines the type of the strikes provided in the surface points. Required.
     Known values are: \"Absolute\", \"BasisPoint\", \"Delta\", \"Moneyness\", \"Percent\", and
     \"Relative\"."""
    model_type: Union[str, "_models.VolModelTypeEnum"] = rest_field(name="modelType")
    """The property that defines the type of the model (Normal or LogNormal) of the volatilities
     provided in the surface points. Required. Known values are: \"Normal\" and \"LogNormal\"."""
    points: List["_models.VolSurfacePoint"] = rest_field()
    """The list of volatility points. Required."""
    fx_cross_code: str = rest_field(name="fxCrossCode")
    """The ISO code of the cross currency pair. Required."""

    @overload
    def __init__(
        self,
        *,
        strike_type: Union[str, "_models.StrikeTypeEnum"],
        model_type: Union[str, "_models.VolModelTypeEnum"],
        points: List["_models.VolSurfacePoint"],
        fx_cross_code: str,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class GenerateDateScheduleResponse(_model_base.Model):
    """An object to define the response to a request to generate a date schedule.

    Attributes
    ----------
    data : list[~datetime.date]
        Required.  The default value is None, needs to be assigned before
        using.
    page : int
        The page number of the current page displayed. Minimum value of this
        property is 1. Required.
    item_per_page : int
        Number of items displayed per page. Required.
    total_pages : int
        Total number of pages available for display. Required.
    total_items : int
        Total number of items available for display. Required.
    links : ~analyticsapi.models.CollectionLinks
        Links for available operations and/or resources linked to current
        response.
    """

    data: List[datetime.date] = rest_field()
    """Required."""
    page: int = rest_field()
    """The page number of the current page displayed. Minimum value of this property is 1. Required."""
    item_per_page: int = rest_field(name="itemPerPage")
    """Number of items displayed per page. Required."""
    total_pages: int = rest_field(name="totalPages")
    """Total number of pages available for display. Required."""
    total_items: int = rest_field(name="totalItems")
    """Total number of items available for display. Required."""
    links: Optional["_models.CollectionLinks"] = rest_field()
    """Links for available operations and/or resources linked to current response."""

    @overload
    def __init__(
        self,
        *,
        data: List[datetime.date],
        page: int,
        item_per_page: int,
        total_pages: int,
        total_items: int,
        links: Optional["_models.CollectionLinks"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class GenerateHolidaysResponse(_model_base.Model):
    """Object defining the paged response for a collection of generated holidays.

    Attributes
    ----------
    data : list[~analyticsapi.models.Holiday]
        Required.  The default value is None, needs to be assigned before
        using.
    page : int
        The page number of the current page displayed. Minimum value of this
        property is 1. Required.
    item_per_page : int
        Number of items displayed per page. Required.
    total_pages : int
        Total number of pages available for display. Required.
    total_items : int
        Total number of items available for display. Required.
    links : ~analyticsapi.models.CollectionLinks
        Links for available operations and/or resources linked to current
        response.
    """

    data: List["_models.Holiday"] = rest_field()
    """Required."""
    page: int = rest_field()
    """The page number of the current page displayed. Minimum value of this property is 1. Required."""
    item_per_page: int = rest_field(name="itemPerPage")
    """Number of items displayed per page. Required."""
    total_pages: int = rest_field(name="totalPages")
    """Total number of pages available for display. Required."""
    total_items: int = rest_field(name="totalItems")
    """Total number of items available for display. Required."""
    links: Optional["_models.CollectionLinks"] = rest_field()
    """Links for available operations and/or resources linked to current response."""

    @overload
    def __init__(
        self,
        *,
        data: List["_models.Holiday"],
        page: int,
        item_per_page: int,
        total_pages: int,
        total_items: int,
        links: Optional["_models.CollectionLinks"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class HalfDayDuration(Duration, discriminator="HalfDayDuration"):
    """An object to determine the duration of the holiday within one day.

    Attributes
    ----------
    duration_type : str or ~analyticsapi.models.HALF_DAY_DURATION
        The type of the holiday duration. Only HalfDayDuration value applies.
        Required. Half day holidays. Designed to account for the days the
        markets are open, but not for a full trading session.
    start_time : ~analyticsapi.models.Time
        An object to determine the start time of the holiday duration.
    end_time : ~analyticsapi.models.Time
        An object to determine the end time of the holiday duration.
    """

    duration_type: Literal[DurationType.HALF_DAY_DURATION] = rest_discriminator(name="durationType")  # type: ignore
    """The type of the holiday duration. Only HalfDayDuration value applies. Required. Half day
     holidays. Designed to account for the days the markets are open, but not for a full trading
     session."""
    start_time: Optional["_models.Time"] = rest_field(name="startTime")
    """An object to determine the start time of the holiday duration."""
    end_time: Optional["_models.Time"] = rest_field(name="endTime")
    """An object to determine the end time of the holiday duration."""

    @overload
    def __init__(
        self,
        *,
        start_time: Optional["_models.Time"] = None,
        end_time: Optional["_models.Time"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, duration_type=DurationType.HALF_DAY_DURATION, **kwargs)


class HecmSettings(_model_base.Model):
    """HecmSettings.

    Attributes
    ----------
    draw_type : str
        Additional settings for HECM bonds. Is one of the following types:
        Literal["CONSTANT"], Literal["HDC"], Literal["MODEL"]
    draw_rate : float
        Required, method for determining draw amount.
    draw_vector : ~analyticsapi.models.Vector
        Number that specifies draw amount rate. Either drawRate or drawVector
        is required.
    """

    draw_type: Optional[Literal["CONSTANT", "HDC", "MODEL"]] = rest_field(name="drawType")
    """Additional settings for HECM bonds. Is one of the following types: Literal[\"CONSTANT\"],
     Literal[\"HDC\"], Literal[\"MODEL\"]"""
    draw_rate: Optional[float] = rest_field(name="drawRate")
    """Required, method for determining draw amount."""
    draw_vector: Optional["_models.Vector"] = rest_field(name="drawVector")
    """Number that specifies draw amount rate. Either drawRate or drawVector is required."""

    @overload
    def __init__(
        self,
        *,
        draw_type: Optional[Literal["CONSTANT", "HDC", "MODEL"]] = None,
        draw_rate: Optional[float] = None,
        draw_vector: Optional["_models.Vector"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class Holiday(_model_base.Model):
    """Dates and names of holidays for a requested calendar.

    Attributes
    ----------
    date : ~datetime.date
        The date on which the holiday falls. The value is expressed in ISO 8601
        format: YYYY-MM-DD (e.g., 2024-01-01). Required.
    names : list[~analyticsapi.models.HolidayNames]
        An array of objects to define the holiday name, calendar and country in
        which that holiday falls.  The default value is None, needs to be
        assigned before using.
    processing_information : str
        The error message for the calculation in case of a non-blocking error.
    """

    date: datetime.date = rest_field()
    """The date on which the holiday falls. The value is expressed in ISO 8601 format: YYYY-MM-DD
     (e.g., 2024-01-01). Required."""
    names: Optional[List["_models.HolidayNames"]] = rest_field()
    """An array of objects to define the holiday name, calendar and country in which that holiday
     falls."""
    processing_information: Optional[str] = rest_field(name="processingInformation")
    """The error message for the calculation in case of a non-blocking error."""

    @overload
    def __init__(
        self,
        *,
        date: datetime.date,
        names: Optional[List["_models.HolidayNames"]] = None,
        processing_information: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class HolidayNames(_model_base.Model):
    """An object to define the holiday name, calendar and country in which that holiday falls.

    Attributes
    ----------
    name : str
        The name of the holiday.
    calendars : list[str]
        An array of calendar defining objects for which the calculation is
        done.  The default value is None, needs to be assigned before using.
    countries : list[str]
        An array of country codes the holiday belongs to. For example, FRA for
        France, UKG for The United Kingdom.  The default value is None, needs
        to be assigned before using.
    """

    name: Optional[str] = rest_field()
    """The name of the holiday."""
    calendars: Optional[List[str]] = rest_field()
    """An array of calendar defining objects for which the calculation is done."""
    countries: Optional[List[str]] = rest_field()
    """An array of country codes the holiday belongs to. For example, FRA for France, UKG for The
     United Kingdom."""

    @overload
    def __init__(
        self,
        *,
        name: Optional[str] = None,
        calendars: Optional[List[str]] = None,
        countries: Optional[List[str]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class HolidayRule(_model_base.Model):
    """An object to set holiday rules for the calendar.

    Attributes
    ----------
    name : str
        The name of the holiday rule. An alphanumeric character (upper or lower
        case), followed by 1 to 75 characters: alpha numeric (upper and lower
        case) plus spaces, parentheses, dashes, equals and single quotes.
        Required.
    description : str
        The description of the holiday rule.
    duration : ~analyticsapi.models.Duration
        An object to determine the duration of the holiday. Either a number of
        days or the object describing half day holiday should be defined.
        Required.
    validity_period : ~analyticsapi.models.ValidityPeriod
        An object to determine the validity period. Required.
    when : ~analyticsapi.models.When
        An object to determine regular annual holiday rules for the calendar.
        Possible values are: AbsolutePositionWhen (for fixed holidays),
        RelativePositionWhen (for holidays that fall on a particular day of the
        week) or RelativeToRulePositionWhen (for holidays that are set by
        reference to another date). Required.
    """

    name: str = rest_field()
    """The name of the holiday rule. An alphanumeric character (upper or lower case), followed by 1 to
     75 characters: alpha numeric (upper and lower case) plus spaces, parentheses, dashes, equals
     and single quotes. Required."""
    description: Optional[str] = rest_field()
    """The description of the holiday rule."""
    duration: "_models.Duration" = rest_field()
    """An object to determine the duration of the holiday. Either a number of days or the object
     describing half day holiday should be defined. Required."""
    validity_period: "_models.ValidityPeriod" = rest_field(name="validityPeriod")
    """An object to determine the validity period. Required."""
    when: "_models.When" = rest_field()
    """An object to determine regular annual holiday rules for the calendar. Possible values are:
     AbsolutePositionWhen (for fixed holidays), RelativePositionWhen (for holidays that fall on a
     particular day of the week) or RelativeToRulePositionWhen (for holidays that are set by
     reference to another date). Required."""

    @overload
    def __init__(
        self,
        *,
        name: str,
        duration: "_models.Duration",
        validity_period: "_models.ValidityPeriod",
        when: "_models.When",
        description: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class HorizonInfo(_model_base.Model):
    """HorizonInfo.

    Attributes
    ----------
    scenario_id : str
        Identification code of the scenario.
    level : str
        Horizon input price for the security. Input can be a price, yield,
        spread, OAS, etc.. See quick card for list of options.
    prepay : ~analyticsapi.models.RestPrepaySettings
    loss_settings : ~analyticsapi.models.LossSettings
    cmbs_scenario : ~analyticsapi.models.PricingScenario
    scenario_ref : ~analyticsapi.models.JsonScenRef
    """

    scenario_id: Optional[str] = rest_field(name="scenarioID")
    """Identification code of the scenario."""
    level: Optional[str] = rest_field()
    """Horizon input price for the security. Input can be a price, yield, spread, OAS, etc.. See quick
     card for list of options."""
    prepay: Optional["_models.RestPrepaySettings"] = rest_field()
    loss_settings: Optional["_models.LossSettings"] = rest_field(name="lossSettings")
    cmbs_scenario: Optional["_models.PricingScenario"] = rest_field(name="cmbsScenario")
    scenario_ref: Optional["_models.JsonScenRef"] = rest_field(name="scenarioRef")

    @overload
    def __init__(
        self,
        *,
        scenario_id: Optional[str] = None,
        level: Optional[str] = None,
        prepay: Optional["_models.RestPrepaySettings"] = None,
        loss_settings: Optional["_models.LossSettings"] = None,
        cmbs_scenario: Optional["_models.PricingScenario"] = None,
        scenario_ref: Optional["_models.JsonScenRef"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IdentifierInfo(_model_base.Model):
    """The main object containing the information to search for a security in Yield Book reference
    data given the string representing the identifier and the string for the type of identifier.
    For example, given "10YR" as the identifier, and "Identifier" as idType would be sufficient to
    search for reference data on a 10 Year US Treasury Bond.

    Attributes
    ----------
    identifier : str
        The string for the identifier to search for.
    id_type : str or ~analyticsapi.models.IdTypeEnum
        The type of convention for the input identifier. By Default, selecting
        SecurityID would allow the system to automatically select the correct
        type.Possible values are: "SecurityID", "CUSIP", "ISIN", "REGSISIN",
        "SEDOL", "Identifier", "ChinaInterbankCode", "ShanghaiExchangeCode",
        "ShenzhenExchangeCode", and "MXTickerID". Known values are:
        "SecurityIDEntry", "SecurityID", "CUSIP", "ISIN", "REGSISIN", "SEDOL",
        "Identifier", "ChinaInterbankCode", "ShanghaiExchangeCode",
        "ShenzhenExchangeCode", and "MXTickerID".
    user_instrument : ~analyticsapi.models.JsonRef
        Container for possible User defined instrument input via JsonRef
        structure (see further documentation for more information).
    props : dict[str, any]
    """

    identifier: Optional[str] = rest_field()
    """The string for the identifier to search for."""
    id_type: Optional[Union[str, "_models.IdTypeEnum"]] = rest_field(name="idType")
    """The type of convention for the input identifier. By Default, selecting SecurityID would allow
     the system to automatically select the correct type.Possible values are: \"SecurityID\",
     \"CUSIP\", \"ISIN\", \"REGSISIN\", \"SEDOL\", \"Identifier\", \"ChinaInterbankCode\",
     \"ShanghaiExchangeCode\", \"ShenzhenExchangeCode\", and \"MXTickerID\". Known values are:
     \"SecurityIDEntry\", \"SecurityID\", \"CUSIP\", \"ISIN\", \"REGSISIN\", \"SEDOL\",
     \"Identifier\", \"ChinaInterbankCode\", \"ShanghaiExchangeCode\", \"ShenzhenExchangeCode\", and
     \"MXTickerID\"."""
    user_instrument: Optional["_models.JsonRef"] = rest_field(name="userInstrument")
    """Container for possible User defined instrument input via JsonRef structure (see further
     documentation for more information)."""
    props: Optional[Dict[str, Any]] = rest_field()

    @overload
    def __init__(
        self,
        *,
        identifier: Optional[str] = None,
        id_type: Optional[Union[str, "_models.IdTypeEnum"]] = None,
        user_instrument: Optional["_models.JsonRef"] = None,
        props: Optional[Dict[str, Any]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IndexCompoundingDefinition(_model_base.Model):
    """An object that defines the use of index compounding.

    Attributes
    ----------
    observation_method : str or ~analyticsapi.models.IndexObservationMethodEnum
        (RFR) Method for determining the accrual observation period. The number
        of business days between the fixing date and the start or end date of
        the coupon period is determined by the index fixing lag. Required.
        Known values are: "Lookback", "PeriodShift", and "Mixed".
    lockout_period : int
        The period from the start date (inclusive) of the index lockout to the
        end date of the interest calculation period for which the reference
        rate is no longer updated. During this period the index of the day
        preceding the start date of the lockout period is applied to the
        remaining days of the interest period. The value is expressed in
        working days. Please note, that by (ISDA) definition the lockout method
        is applied only to payment periods (with Fixing) and not to future
        periods (with ZcCurve). Required.
    compounding_mode : str or ~analyticsapi.models.CompoundingModeEnum
        The mode used to define how the interest rate is calculated from the
        reset floating rates when the reset frequency is higher than the
        interest payment frequency (e.g., daily index reset with quarterly
        interest payments). Required. Known values are: "Compounding",
        "Average", "Constant", "AdjustedCompounded", and "MexicanCompounded".
    spread_compounding_mode : str or ~analyticsapi.models.SpreadCompoundingModeEnum
        The mode used to define how the spread is applied to a compound
        interest rate. It is only applied when compounding mode is set for the
        reference index. Required. Known values are: "IsdaCompounding",
        "IsdaFlatCompounding", and "NoCompounding".
    """

    observation_method: Union[str, "_models.IndexObservationMethodEnum"] = rest_field(name="observationMethod")
    """(RFR) Method for determining the accrual observation period. The number of business days
     between the fixing date and the start or end date of the coupon period is determined by the
     index fixing lag. Required. Known values are: \"Lookback\", \"PeriodShift\", and \"Mixed\"."""
    lockout_period: int = rest_field(name="lockoutPeriod")
    """The period from the start date (inclusive) of the index lockout to the end date of the interest
     calculation period for which the reference rate is no longer updated.
     During this period the index of the day preceding the start date of the lockout period is
     applied to the remaining days of the interest period.
     The value is expressed in working days.
     Please note, that by (ISDA) definition the lockout method is applied only to payment periods
     (with Fixing) and not to future periods (with ZcCurve). Required."""
    compounding_mode: Union[str, "_models.CompoundingModeEnum"] = rest_field(name="compoundingMode")
    """The mode used to define how the interest rate is calculated from the reset floating rates when
     the reset frequency is higher than the interest payment frequency (e.g., daily index reset with
     quarterly interest payments). Required. Known values are: \"Compounding\", \"Average\",
     \"Constant\", \"AdjustedCompounded\", and \"MexicanCompounded\"."""
    spread_compounding_mode: Union[str, "_models.SpreadCompoundingModeEnum"] = rest_field(name="spreadCompoundingMode")
    """The mode used to define how the spread is applied to a compound interest rate. It is only
     applied when compounding mode is set for the reference index. Required. Known values are:
     \"IsdaCompounding\", \"IsdaFlatCompounding\", and \"NoCompounding\"."""

    @overload
    def __init__(
        self,
        *,
        observation_method: Union[str, "_models.IndexObservationMethodEnum"],
        lockout_period: int,
        compounding_mode: Union[str, "_models.CompoundingModeEnum"],
        spread_compounding_mode: Union[str, "_models.SpreadCompoundingModeEnum"],
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IndexLinkerSettings(_model_base.Model):
    """Optional. Used for Inflation-Linked Securities.

    Attributes
    ----------
    real_yield_beta : float
        Optional, number, allows users to override default realYieldBeta.
    """

    real_yield_beta: Optional[float] = rest_field(name="realYieldBeta")
    """Optional, number, allows users to override default realYieldBeta."""

    @overload
    def __init__(
        self,
        real_yield_beta: Optional[float] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["real_yield_beta"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class IndexProjection(_model_base.Model):
    """IndexProjection.

    Attributes
    ----------
    index : str
    term_unit : str
        Is either a Literal["MONTH"] type or a Literal["YEAR"] type.
    values_property : list[~analyticsapi.models.TermRatePair]
        The default value is None, needs to be assigned before using.
    """

    index: Optional[str] = rest_field()
    term_unit: Optional[Literal["MONTH", "YEAR"]] = rest_field(name="termUnit")
    """Is either a Literal[\"MONTH\"] type or a Literal[\"YEAR\"] type."""
    values_property: Optional[List["_models.TermRatePair"]] = rest_field(name="values")

    @overload
    def __init__(
        self,
        *,
        index: Optional[str] = None,
        term_unit: Optional[Literal["MONTH", "YEAR"]] = None,
        values_property: Optional[List["_models.TermRatePair"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IndirectSourcesDeposits(_model_base.Model):
    """An object that defines the sources containing the market data for the deposit instruments used
    to create the curve definition.
    It applies when there is an indirect quotation for the currency pair of the curve.

    Attributes
    ----------
    base_fx_spot : str
        The source of FX spot for the base currency in the cross-currency pair
        of the curve against the reference currency.
    quoted_fx_spot : str
        The source of FX spot for the quoted currency in the cross-currency
        pair of the curve against the reference currency.
    base_deposit : str
        The source of deposits for the base currency in the cross-currency pair
        of the curve.
    quoted_deposit : str
        The source of deposits for the quoted currency in the cross-currency
        pair of the curve.
    """

    base_fx_spot: Optional[str] = rest_field(name="baseFxSpot")
    """The source of FX spot for the base currency in the cross-currency pair of the curve against the
     reference currency."""
    quoted_fx_spot: Optional[str] = rest_field(name="quotedFxSpot")
    """The source of FX spot for the quoted currency in the cross-currency pair of the curve against
     the reference currency."""
    base_deposit: Optional[str] = rest_field(name="baseDeposit")
    """The source of deposits for the base currency in the cross-currency pair of the curve."""
    quoted_deposit: Optional[str] = rest_field(name="quotedDeposit")
    """The source of deposits for the quoted currency in the cross-currency pair of the curve."""

    @overload
    def __init__(
        self,
        *,
        base_fx_spot: Optional[str] = None,
        quoted_fx_spot: Optional[str] = None,
        base_deposit: Optional[str] = None,
        quoted_deposit: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IndirectSourcesSwaps(_model_base.Model):
    """An object that defines the sources containing the market data for the FX forward instruments
    used to create the curve definition.
    It applies when there is an indirect quotation for the currency pair of the curve. If reference
    currency is not specified, quotedFxSpot and quotedFxForwards properties should be used to
    determine source.

    Attributes
    ----------
    base_fx_spot : str
        The source of FX spot for the base currency in the cross-currency pair.
    quoted_fx_spot : str
        The source of FX spot for the quoted currency in the cross-currency
        pair.
    base_fx_forwards : str
        The source of FX forwards for the base currency in the cross-currency
        pair.
    quoted_fx_forwards : str
        The source of FX forwards for the quoted currency in the cross-currency
        pair.
    """

    base_fx_spot: Optional[str] = rest_field(name="baseFxSpot")
    """The source of FX spot for the base currency in the cross-currency pair."""
    quoted_fx_spot: Optional[str] = rest_field(name="quotedFxSpot")
    """The source of FX spot for the quoted currency in the cross-currency pair."""
    base_fx_forwards: Optional[str] = rest_field(name="baseFxForwards")
    """The source of FX forwards for the base currency in the cross-currency pair."""
    quoted_fx_forwards: Optional[str] = rest_field(name="quotedFxForwards")
    """The source of FX forwards for the quoted currency in the cross-currency pair."""

    @overload
    def __init__(
        self,
        *,
        base_fx_spot: Optional[str] = None,
        quoted_fx_spot: Optional[str] = None,
        base_fx_forwards: Optional[str] = None,
        quoted_fx_forwards: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class InnerError(_model_base.Model):
    """An object that contains the detailed information in case of a blocking error in calculation.

    Attributes
    ----------
    key : str
        The specification of the request in which an error occurs. Required.
    reason : str
        The reason why an error occurs. Required.
    name : str
        The name of the property causing the error.
    invalid_name : str
        The name of the invalid property.
    """

    key: str = rest_field()
    """The specification of the request in which an error occurs. Required."""
    reason: str = rest_field()
    """The reason why an error occurs. Required."""
    name: Optional[str] = rest_field()
    """The name of the property causing the error."""
    invalid_name: Optional[str] = rest_field(name="invalidName")
    """The name of the invalid property."""

    @overload
    def __init__(
        self,
        *,
        key: str,
        reason: str,
        name: Optional[str] = None,
        invalid_name: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class InstrumentTemplate(_model_base.Model):
    """A model template defining a resource.

    Readonly variables are only populated by the server, and will be ignored when sending a request.

    Attributes
    ----------
    type : str or ~analyticsapi.models.INSTRUMENT_TEMPLATE
        Property defining the type of the resource.
    id : str
        Unique identifier of the InstrumentTemplate.
    location : ~analyticsapi.models.Location
        Object defining the location of the InstrumentTemplate in the platform.
        Required.
    description : ~analyticsapi.models.Description
        Object defining metadata for the InstrumentTemplate.
    definition : ~analyticsapi.models.InstrumentTemplateDefinition
        Object defining the InstrumentTemplate. Required.
    """

    type: Optional[Literal[ResourceType.INSTRUMENT_TEMPLATE]] = rest_field(
        visibility=["read"], default=ResourceType.INSTRUMENT_TEMPLATE
    )
    """Property defining the type of the resource."""
    id: Optional[str] = rest_field(visibility=["read"])
    """Unique identifier of the InstrumentTemplate."""
    location: "_models.Location" = rest_field(visibility=["read", "create"])
    """Object defining the location of the InstrumentTemplate in the platform. Required."""
    description: Optional["_models.Description"] = rest_field()
    """Object defining metadata for the InstrumentTemplate."""
    definition: "_models.InstrumentTemplateDefinition" = rest_field()
    """Object defining the InstrumentTemplate. Required."""

    @overload
    def __init__(
        self,
        *,
        location: "_models.Location",
        definition: "_models.InstrumentTemplateDefinition",
        description: Optional["_models.Description"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class InstrumentTemplateCollectionLinks(_model_base.Model):
    """InstrumentTemplateCollectionLinks.

    Attributes
    ----------
    self_property : ~analyticsapi.models.Link
        Required.
    first : ~analyticsapi.models.Link
    prev : ~analyticsapi.models.Link
    next : ~analyticsapi.models.Link
    last : ~analyticsapi.models.Link
    """

    self_property: "_models.Link" = rest_field(name="self")
    """Required."""
    first: Optional["_models.Link"] = rest_field()
    prev: Optional["_models.Link"] = rest_field()
    next: Optional["_models.Link"] = rest_field()
    last: Optional["_models.Link"] = rest_field()

    @overload
    def __init__(
        self,
        *,
        self_property: "_models.Link",
        first: Optional["_models.Link"] = None,
        prev: Optional["_models.Link"] = None,
        next: Optional["_models.Link"] = None,
        last: Optional["_models.Link"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class InstrumentTemplateCollectionResponse(_model_base.Model):
    """A model template describing a paged response.

    Attributes
    ----------
    data : list[~analyticsapi.models.InstrumentTemplateInfo]
        Required.  The default value is None, needs to be assigned before
        using.
    page : int
        The page number of the current page displayed. Minimum value of this
        property is 1. Required.
    item_per_page : int
        Number of items displayed per page. Required.
    total_pages : int
        Total number of pages available for display. Required.
    total_items : int
        Total number of items available for display. Required.
    links : ~analyticsapi.models.InstrumentTemplateCollectionLinks
        Links for available operations and/or resources linked to current
        response.
    """

    data: List["_models.InstrumentTemplateInfo"] = rest_field()
    """Required."""
    page: int = rest_field()
    """The page number of the current page displayed. Minimum value of this property is 1. Required."""
    item_per_page: int = rest_field(name="itemPerPage")
    """Number of items displayed per page. Required."""
    total_pages: int = rest_field(name="totalPages")
    """Total number of pages available for display. Required."""
    total_items: int = rest_field(name="totalItems")
    """Total number of items available for display. Required."""
    links: Optional["_models.InstrumentTemplateCollectionLinks"] = rest_field()
    """Links for available operations and/or resources linked to current response."""

    @overload
    def __init__(
        self,
        *,
        data: List["_models.InstrumentTemplateInfo"],
        page: int,
        item_per_page: int,
        total_pages: int,
        total_items: int,
        links: Optional["_models.InstrumentTemplateCollectionLinks"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class InstrumentTemplateInfo(_model_base.Model):
    """A model template defining the partial description of the resource returned by the GET list
    service.

    Readonly variables are only populated by the server, and will be ignored when sending a request.

    Attributes
    ----------
    type : str or ~analyticsapi.models.INSTRUMENT_TEMPLATE
        Property defining the type of the resource.
    id : str
        Unique identifier of the InstrumentTemplate.
    location : ~analyticsapi.models.Location
        Object defining metadata for the InstrumentTemplate. Required.
    description : ~analyticsapi.models.Description
        Object defining the InstrumentTemplate.
    """

    type: Optional[Literal[ResourceType.INSTRUMENT_TEMPLATE]] = rest_field(
        visibility=["read"], default=ResourceType.INSTRUMENT_TEMPLATE
    )
    """Property defining the type of the resource."""
    id: Optional[str] = rest_field(visibility=["read"])
    """Unique identifier of the InstrumentTemplate."""
    location: "_models.Location" = rest_field(visibility=["read", "create"])
    """Object defining metadata for the InstrumentTemplate. Required."""
    description: Optional["_models.Description"] = rest_field()
    """Object defining the InstrumentTemplate."""

    @overload
    def __init__(
        self,
        *,
        location: "_models.Location",
        description: Optional["_models.Description"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class InstrumentTemplateResponse(_model_base.Model):
    """A model template describing a single response.

    Attributes
    ----------
    data : ~analyticsapi.models.InstrumentTemplate
        Required.
    meta : ~analyticsapi.models.MetaData
    """

    data: "_models.InstrumentTemplate" = rest_field()
    """Required."""
    meta: Optional["_models.MetaData"] = rest_field()

    @overload
    def __init__(
        self,
        *,
        data: "_models.InstrumentTemplate",
        meta: Optional["_models.MetaData"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class InterestRateLegDefinition(_model_base.Model):
    """An object that defines a leg of an interest rate instrument.

    Attributes
    ----------
    rate : ~analyticsapi.models.InterestRateDefinition
        An object that defines the interest rate settings. Required.
    interest_periods : ~analyticsapi.models.ScheduleDefinition
        An object that defines the schedule of interest periods. Required.
    payment_offset : ~analyticsapi.models.OffsetDefinition
        An object that defines how the payment dates are derived from the
        interest period dates.
    coupon_day_count : str or ~analyticsapi.models.DayCountBasis
        The day count basis method that defines how the year fraction of the
        coupon period is computed. If not defined, the market convention
        related to the leg currency applies. Known values are: "Dcb_30_360",
        "Dcb_30_360_US", "Dcb_30_360_German", "Dcb_30_360_ISDA",
        "Dcb_30_365_ISDA", "Dcb_30_365_German", "Dcb_30_365_Brazil",
        "Dcb_30_Actual_German", "Dcb_30_Actual", "Dcb_30_Actual_ISDA",
        "Dcb_30E_360_ISMA", "Dcb_Actual_360", "Dcb_Actual_364",
        "Dcb_Actual_365", "Dcb_Actual_Actual", "Dcb_Actual_Actual_ISDA",
        "Dcb_Actual_Actual_AFB", "Dcb_WorkingDays_252", "Dcb_Actual_365L",
        "Dcb_Actual_365P", "Dcb_ActualLeapDay_365", "Dcb_ActualLeapDay_360",
        "Dcb_Actual_36525", and "Dcb_Actual_365_CanadianConvention".
    accrual_day_count : str or ~analyticsapi.models.DayCountBasis
        The day count basis method that defines how the year fraction of the
        accrual period is computed. If not defined, the market convention
        related to the leg currency applies. Known values are: "Dcb_30_360",
        "Dcb_30_360_US", "Dcb_30_360_German", "Dcb_30_360_ISDA",
        "Dcb_30_365_ISDA", "Dcb_30_365_German", "Dcb_30_365_Brazil",
        "Dcb_30_Actual_German", "Dcb_30_Actual", "Dcb_30_Actual_ISDA",
        "Dcb_30E_360_ISMA", "Dcb_Actual_360", "Dcb_Actual_364",
        "Dcb_Actual_365", "Dcb_Actual_Actual", "Dcb_Actual_Actual_ISDA",
        "Dcb_Actual_Actual_AFB", "Dcb_WorkingDays_252", "Dcb_Actual_365L",
        "Dcb_Actual_365P", "Dcb_ActualLeapDay_365", "Dcb_ActualLeapDay_360",
        "Dcb_Actual_36525", and "Dcb_Actual_365_CanadianConvention".
    principal : ~analyticsapi.models.PrincipalDefinition
        An object that defines the principal used to calculate interest
        payments. It can also be exchanged between parties. Required.
    payer : str or ~analyticsapi.models.PartyEnum
        The party (Party1 or Party2) that makes the payment. Required. Known
        values are: "Party1" and "Party2".
    receiver : str or ~analyticsapi.models.PartyEnum
        The party (Party1 or Party2) that receives the payment. Required. Known
        values are: "Party1" and "Party2".
    """

    rate: "_models.InterestRateDefinition" = rest_field()
    """An object that defines the interest rate settings. Required."""
    interest_periods: "_models.ScheduleDefinition" = rest_field(name="interestPeriods")
    """An object that defines the schedule of interest periods. Required."""
    payment_offset: Optional["_models.OffsetDefinition"] = rest_field(name="paymentOffset")
    """An object that defines how the payment dates are derived from the interest period dates."""
    coupon_day_count: Optional[Union[str, "_models.DayCountBasis"]] = rest_field(name="couponDayCount")
    """The day count basis method that defines how the year fraction of the coupon period is computed.
     If not defined, the market convention related to the leg currency applies. Known values are:
     \"Dcb_30_360\", \"Dcb_30_360_US\", \"Dcb_30_360_German\", \"Dcb_30_360_ISDA\",
     \"Dcb_30_365_ISDA\", \"Dcb_30_365_German\", \"Dcb_30_365_Brazil\", \"Dcb_30_Actual_German\",
     \"Dcb_30_Actual\", \"Dcb_30_Actual_ISDA\", \"Dcb_30E_360_ISMA\", \"Dcb_Actual_360\",
     \"Dcb_Actual_364\", \"Dcb_Actual_365\", \"Dcb_Actual_Actual\", \"Dcb_Actual_Actual_ISDA\",
     \"Dcb_Actual_Actual_AFB\", \"Dcb_WorkingDays_252\", \"Dcb_Actual_365L\", \"Dcb_Actual_365P\",
     \"Dcb_ActualLeapDay_365\", \"Dcb_ActualLeapDay_360\", \"Dcb_Actual_36525\", and
     \"Dcb_Actual_365_CanadianConvention\"."""
    accrual_day_count: Optional[Union[str, "_models.DayCountBasis"]] = rest_field(name="accrualDayCount")
    """The day count basis method that defines how the year fraction of the accrual period is
     computed. If not defined, the market convention related to the leg currency applies. Known
     values are: \"Dcb_30_360\", \"Dcb_30_360_US\", \"Dcb_30_360_German\", \"Dcb_30_360_ISDA\",
     \"Dcb_30_365_ISDA\", \"Dcb_30_365_German\", \"Dcb_30_365_Brazil\", \"Dcb_30_Actual_German\",
     \"Dcb_30_Actual\", \"Dcb_30_Actual_ISDA\", \"Dcb_30E_360_ISMA\", \"Dcb_Actual_360\",
     \"Dcb_Actual_364\", \"Dcb_Actual_365\", \"Dcb_Actual_Actual\", \"Dcb_Actual_Actual_ISDA\",
     \"Dcb_Actual_Actual_AFB\", \"Dcb_WorkingDays_252\", \"Dcb_Actual_365L\", \"Dcb_Actual_365P\",
     \"Dcb_ActualLeapDay_365\", \"Dcb_ActualLeapDay_360\", \"Dcb_Actual_36525\", and
     \"Dcb_Actual_365_CanadianConvention\"."""
    principal: "_models.PrincipalDefinition" = rest_field()
    """An object that defines the principal used to calculate interest payments. It can also be
     exchanged between parties. Required."""
    payer: Union[str, "_models.PartyEnum"] = rest_field()
    """The party (Party1 or Party2) that makes the payment. Required. Known values are: \"Party1\" and
     \"Party2\"."""
    receiver: Union[str, "_models.PartyEnum"] = rest_field()
    """The party (Party1 or Party2) that receives the payment. Required. Known values are: \"Party1\"
     and \"Party2\"."""

    @overload
    def __init__(
        self,
        *,
        rate: "_models.InterestRateDefinition",
        interest_periods: "_models.ScheduleDefinition",
        principal: "_models.PrincipalDefinition",
        payer: Union[str, "_models.PartyEnum"],
        receiver: Union[str, "_models.PartyEnum"],
        payment_offset: Optional["_models.OffsetDefinition"] = None,
        coupon_day_count: Optional[Union[str, "_models.DayCountBasis"]] = None,
        accrual_day_count: Optional[Union[str, "_models.DayCountBasis"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class InterestRateLegTemplateDefinition(InstrumentTemplateDefinition, discriminator="InterestRateLeg"):
    """InterestRateLegTemplateDefinition.

    Attributes
    ----------
    instrument_type : str or ~analyticsapi.models.INTEREST_RATE_LEG
        Required. An interest rate leg.
    template : ~analyticsapi.models.InterestRateLegDefinition
        Required.
    """

    instrument_type: Literal[InstrumentTemplateTypeEnum.INTEREST_RATE_LEG] = rest_discriminator(name="instrumentType")  # type: ignore
    """Required. An interest rate leg."""
    template: "_models.InterestRateLegDefinition" = rest_field()
    """Required."""

    @overload
    def __init__(
        self,
        template: "_models.InterestRateLegDefinition",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, instrument_type=InstrumentTemplateTypeEnum.INTEREST_RATE_LEG, **kwargs)


class InterestRateSwapTemplateDefinition(InstrumentTemplateDefinition, discriminator="VanillaSwap"):
    """InterestRateSwapTemplateDefinition.

    Attributes
    ----------
    instrument_type : str or ~analyticsapi.models.VANILLA_SWAP
        Required. A vanilla interest rate swap contract.
    template : ~analyticsapi.models.IrSwapDefinition
        Required.
    """

    instrument_type: Literal[InstrumentTemplateTypeEnum.VANILLA_SWAP] = rest_discriminator(name="instrumentType")  # type: ignore
    """Required. A vanilla interest rate swap contract."""
    template: "_models.IrSwapDefinition" = rest_field()
    """Required."""

    @overload
    def __init__(
        self,
        template: "_models.IrSwapDefinition",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, instrument_type=InstrumentTemplateTypeEnum.VANILLA_SWAP, **kwargs)


class InterpolationTypeAndVector(_model_base.Model):
    """InterpolationTypeAndVector.

    Attributes
    ----------
    interpolation_type : str
        Default value is "LINEAR".
    vector : list[~analyticsapi.models.TermAndValue]
        The default value is None, needs to be assigned before using.
    """

    interpolation_type: Optional[Literal["LINEAR"]] = rest_field(name="interpolationType")
    """Default value is \"LINEAR\"."""
    vector: Optional[List["_models.TermAndValue"]] = rest_field()

    @overload
    def __init__(
        self,
        *,
        interpolation_type: Optional[Literal["LINEAR"]] = None,
        vector: Optional[List["_models.TermAndValue"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrCapVolSurfaceChoice(_model_base.Model):
    """The object to provide either a reference to a interest rate cap volatility surface stored in
    the platform or 3rd party volatilities.

    Attributes
    ----------
    reference : str
        The reference to a volatility surface stored in the platform.
    surface : ~analyticsapi.models.IrVolSurfaceInput
        The volatility surface data.
    """

    reference: Optional[str] = rest_field()
    """The reference to a volatility surface stored in the platform."""
    surface: Optional["_models.IrVolSurfaceInput"] = rest_field()
    """The volatility surface data."""

    @overload
    def __init__(
        self,
        *,
        reference: Optional[str] = None,
        surface: Optional["_models.IrVolSurfaceInput"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrCurveChoice(_model_base.Model):
    """The object to provide either a reference to a interest rate zero curve stored in the platform
    or a 3rd party curve.

    Attributes
    ----------
    reference : str
        The reference to an interest rate curve stored in the platform.
    curve : ~analyticsapi.models.IrZcCurveInput
        The interest rate curve data.
    """

    reference: Optional[str] = rest_field()
    """The reference to an interest rate curve stored in the platform."""
    curve: Optional["_models.IrZcCurveInput"] = rest_field()
    """The interest rate curve data."""

    @overload
    def __init__(
        self,
        *,
        reference: Optional[str] = None,
        curve: Optional["_models.IrZcCurveInput"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrLegDescriptionFields(_model_base.Model):
    """An object that contains fields related to the instrument's description.

    Attributes
    ----------
    leg_tag : str
        A user-defined string to identify a leg. Required.
    leg_description : str
        The label that describes a leg. Required.
    interest_type : str or ~analyticsapi.models.InterestType
        An indicator whether a leg pays a fixed or floating interest. Required.
        Known values are: "Fixed" and "Float".
    currency : str
        The currency of a leg's notional amount. The value is expressed in ISO
        4217 alphabetical format (e.g., 'USD'). Required.
    start_date : ~datetime.date
        The start date of a leg. The value is expressed in ISO 8601 format:
        YYYY-MM-DD (e.g., 2021-01-01). Required.
    end_date : ~datetime.date
        The end date of a leg. The value is expressed in ISO 8601 format: YYYY-
        MM-DD (e.g., 2021-01-01). Required.
    index : str
        The floating rate index identifier.
    """

    leg_tag: str = rest_field(name="legTag")
    """A user-defined string to identify a leg. Required."""
    leg_description: str = rest_field(name="legDescription")
    """The label that describes a leg. Required."""
    interest_type: Union[str, "_models.InterestType"] = rest_field(name="interestType")
    """An indicator whether a leg pays a fixed or floating interest. Required. Known values are:
     \"Fixed\" and \"Float\"."""
    currency: str = rest_field()
    """The currency of a leg's notional amount. The value is expressed in ISO 4217 alphabetical format
     (e.g., 'USD'). Required."""
    start_date: datetime.date = rest_field(name="startDate")
    """The start date of a leg. The value is expressed in ISO 8601 format: YYYY-MM-DD (e.g.,
     2021-01-01). Required."""
    end_date: datetime.date = rest_field(name="endDate")
    """The end date of a leg. The value is expressed in ISO 8601 format: YYYY-MM-DD (e.g.,
     2021-01-01). Required."""
    index: Optional[str] = rest_field()
    """The floating rate index identifier."""

    @overload
    def __init__(
        self,
        *,
        leg_tag: str,
        leg_description: str,
        interest_type: Union[str, "_models.InterestType"],
        currency: str,
        start_date: datetime.date,
        end_date: datetime.date,
        index: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrLegResponseFields(_model_base.Model):
    """An object that contains the fields returned in the analytic response for a leg.

    Attributes
    ----------
    description : ~analyticsapi.models.IrLegDescriptionFields
        An object that contains fields related to the instrument's description.
        Required.
    valuation : ~analyticsapi.models.IrValuationFields
        An object that contains fields related to the instrument's valuation.
    risk : ~analyticsapi.models.IrRiskFields
        An object that contains fields related to the instrument's risk
        assessment.
    """

    description: "_models.IrLegDescriptionFields" = rest_field()
    """An object that contains fields related to the instrument's description. Required."""
    valuation: Optional["_models.IrValuationFields"] = rest_field()
    """An object that contains fields related to the instrument's valuation."""
    risk: Optional["_models.IrRiskFields"] = rest_field()
    """An object that contains fields related to the instrument's risk assessment."""

    @overload
    def __init__(
        self,
        *,
        description: "_models.IrLegDescriptionFields",
        valuation: Optional["_models.IrValuationFields"] = None,
        risk: Optional["_models.IrRiskFields"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrLegValuationResponseFields(IrLegResponseFields):
    """An object that contains the fields returned in the valuation response for a leg.

    Attributes
    ----------
    description : ~analyticsapi.models.IrLegDescriptionFields
        An object that contains fields related to the instrument's description.
        Required.
    valuation : ~analyticsapi.models.IrValuationFields
        An object that contains fields related to the instrument's valuation.
    risk : ~analyticsapi.models.IrRiskFields
        An object that contains fields related to the instrument's risk
        assessment.
    """

    @overload
    def __init__(
        self,
        *,
        description: "_models.IrLegDescriptionFields",
        valuation: Optional["_models.IrValuationFields"] = None,
        risk: Optional["_models.IrRiskFields"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrMeasure(_model_base.Model):
    """An object that contains measures used to express the results of the instrument leg valuation.

    Attributes
    ----------
    value : float
        The amount expressed as an absolute value. Required.
    bp : float
        The amount expressed in basis points.
    percent : float
        The amount expressed as a percentage.
    deal_currency : ~analyticsapi.models.Amount
        An object that specifies the amount expressed in the deal currency.
    report_currency : ~analyticsapi.models.Amount
        An object that specifies the amount expressed in the reporting
        currency.
    domestic_currency : ~analyticsapi.models.Amount
        An object that specifies the amount expressed in the domestic currency.
    foreign_currency : ~analyticsapi.models.Amount
        An object that specifies the amount expressed in the foreign currency
        (FX specific).
    leg_currency : ~analyticsapi.models.Amount
        An object that specifies the amount in the leg currency.
    """

    value: float = rest_field()
    """The amount expressed as an absolute value. Required."""
    bp: Optional[float] = rest_field()
    """The amount expressed in basis points."""
    percent: Optional[float] = rest_field()
    """The amount expressed as a percentage."""
    deal_currency: Optional["_models.Amount"] = rest_field(name="dealCurrency")
    """An object that specifies the amount expressed in the deal currency."""
    report_currency: Optional["_models.Amount"] = rest_field(name="reportCurrency")
    """An object that specifies the amount expressed in the reporting currency."""
    domestic_currency: Optional["_models.Amount"] = rest_field(name="domesticCurrency")
    """An object that specifies the amount expressed in the domestic currency."""
    foreign_currency: Optional["_models.Amount"] = rest_field(name="foreignCurrency")
    """An object that specifies the amount expressed in the foreign currency (FX specific)."""
    leg_currency: Optional["_models.Amount"] = rest_field(name="legCurrency")
    """An object that specifies the amount in the leg currency."""

    @overload
    def __init__(
        self,
        *,
        value: float,
        bp: Optional[float] = None,
        percent: Optional[float] = None,
        deal_currency: Optional["_models.Amount"] = None,
        report_currency: Optional["_models.Amount"] = None,
        domestic_currency: Optional["_models.Amount"] = None,
        foreign_currency: Optional["_models.Amount"] = None,
        leg_currency: Optional["_models.Amount"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrPricingParameters(BasePricingParameters):
    """An object that contains parameters used to control interest rate analytics.

    Attributes
    ----------
    valuation_date : ~datetime.date
        The date at which the instrument is valued. The value is expressed in
        ISO 8601 format: YYYY-MM-DD (e.g., '2021-01-01').
    report_currency : str
        The reporting currency. The value is expressed in ISO 4217 alphabetical
        format (e.g., 'GBP'). Default is USD.
    index_convexity : ~analyticsapi.models.ConvexityAdjustment
        An object that contains parameters used to control the convexity
        adjustment of the reference index.
    solving_parameters : ~analyticsapi.models.IrSwapSolvingParameters
        An object that contains parameters used to control solving.
    """

    index_convexity: Optional["_models.ConvexityAdjustment"] = rest_field(name="indexConvexity")
    """An object that contains parameters used to control the convexity adjustment of the reference
     index."""
    solving_parameters: Optional["_models.IrSwapSolvingParameters"] = rest_field(name="solvingParameters")
    """An object that contains parameters used to control solving."""

    @overload
    def __init__(
        self,
        *,
        valuation_date: Optional[datetime.date] = None,
        report_currency: Optional[str] = None,
        index_convexity: Optional["_models.ConvexityAdjustment"] = None,
        solving_parameters: Optional["_models.IrSwapSolvingParameters"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrRiskFields(_model_base.Model):
    """An object that contains fields related to the instrument's risk assessment.

    Attributes
    ----------
    duration : ~analyticsapi.models.IrMeasure
        An object that describes the weighted average maturity in years of all
        cash flows. The final cash flow includes the principal, which has a
        much greater weight than the intermediate cash flows. Required.
    modified_duration : ~analyticsapi.models.IrMeasure
        An object that describes the measure of price sensitivity in percent to
        a 100 basis points change in the instrument's yield, or a 1% parallel
        shift in the underlying zero-coupon curve. For a floating rate
        instrument, it is computed as time to next payment. Required.
    benchmark_hedge_notional : ~analyticsapi.models.Amount
        An object that specifies the notional amount of the benchmark
        instrument that allows to hedge the instrument (available for IRS
        only). The value is expressed in the deal currency. It is computed for
        instrument legs only. Required.
    annuity : ~analyticsapi.models.IrMeasure
        An object that describes the sensitivity of the net present value of
        the fixed rate leg to a 1bp shift in the fixed rate. Required.
    dv01 : ~analyticsapi.models.IrMeasure
        An object that describes the sensitivity of the net present value to a
        1bp parallel shift in the zero-coupon curve. Required.
    pv01 : ~analyticsapi.models.IrMeasure
        An object that describes the sensitivity of the net present value to a
        1bp parallel shift in the yield curve. Required.
    br01 : ~analyticsapi.models.IrMeasure
        An object that describes the sensitivity of the net present value to a
        1bp shift of Currency Basis Swap (CBS) spreads. Required.
    """

    duration: "_models.IrMeasure" = rest_field()
    """An object that describes the weighted average maturity in years of all cash flows. The final
     cash flow includes the principal, which has a much greater weight than the intermediate cash
     flows. Required."""
    modified_duration: "_models.IrMeasure" = rest_field(name="modifiedDuration")
    """An object that describes the measure of price sensitivity in percent to a 100 basis points
     change in the instrument's yield, or a 1% parallel shift in the underlying zero-coupon curve.
     For a floating rate instrument, it is computed as time to next payment. Required."""
    benchmark_hedge_notional: "_models.Amount" = rest_field(name="benchmarkHedgeNotional")
    """An object that specifies the notional amount of the benchmark instrument that allows to hedge
     the instrument (available for IRS only). The value is expressed in the deal currency. It is
     computed for instrument legs only. Required."""
    annuity: "_models.IrMeasure" = rest_field()
    """An object that describes the sensitivity of the net present value of the fixed rate leg to a
     1bp shift in the fixed rate. Required."""
    dv01: "_models.IrMeasure" = rest_field()
    """An object that describes the sensitivity of the net present value to a 1bp parallel shift in
     the zero-coupon curve. Required."""
    pv01: "_models.IrMeasure" = rest_field()
    """An object that describes the sensitivity of the net present value to a 1bp parallel shift in
     the yield curve. Required."""
    br01: "_models.IrMeasure" = rest_field()
    """An object that describes the sensitivity of the net present value to a 1bp shift of Currency
     Basis Swap (CBS) spreads. Required."""

    @overload
    def __init__(
        self,
        *,
        duration: "_models.IrMeasure",
        modified_duration: "_models.IrMeasure",
        benchmark_hedge_notional: "_models.Amount",
        annuity: "_models.IrMeasure",
        dv01: "_models.IrMeasure",
        pv01: "_models.IrMeasure",
        br01: "_models.IrMeasure",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrsInstrumentResponse(_model_base.Model):
    """An object that contains fields related to the interest rate swap definition.

    Attributes
    ----------
    data : ~analyticsapi.models.IrSwapDefinition
        An object that describes the instrument generated by the request.
        Required.
    """

    data: "_models.IrSwapDefinition" = rest_field()
    """An object that describes the instrument generated by the request. Required."""

    @overload
    def __init__(
        self,
        data: "_models.IrSwapDefinition",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["data"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class IrSwap(_model_base.Model):
    """The resource used to create, save and price an interest rate swap.

    Readonly variables are only populated by the server, and will be ignored when sending a request.

    Attributes
    ----------
    type : str or ~analyticsapi.models.IR_SWAP
        Property defining the type of the resource.
    id : str
        Unique identifier of the IrSwap.
    location : ~analyticsapi.models.Location
        Object defining the location of the IrSwap in the platform. Required.
    description : ~analyticsapi.models.Description
        Object defining metadata for the IrSwap.
    definition : ~analyticsapi.models.IrSwapDefinition
        Object defining the IrSwap. Required.
    """

    type: Optional[Literal[ResourceType.IR_SWAP]] = rest_field(visibility=["read"], default=ResourceType.IR_SWAP)
    """Property defining the type of the resource."""
    id: Optional[str] = rest_field(visibility=["read"])
    """Unique identifier of the IrSwap."""
    location: "_models.Location" = rest_field(visibility=["read", "create"])
    """Object defining the location of the IrSwap in the platform. Required."""
    description: Optional["_models.Description"] = rest_field()
    """Object defining metadata for the IrSwap."""
    definition: "_models.IrSwapDefinition" = rest_field()
    """Object defining the IrSwap. Required."""

    @overload
    def __init__(
        self,
        *,
        location: "_models.Location",
        definition: "_models.IrSwapDefinition",
        description: Optional["_models.Description"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrSwapAsCollectionItem(_model_base.Model):
    """A model template defining the partial description of the resource returned by the GET list
    service.

    Readonly variables are only populated by the server, and will be ignored when sending a request.

    Attributes
    ----------
    type : str or ~analyticsapi.models.IR_SWAP
        Property defining the type of the resource.
    id : str
        Unique identifier of the IrSwap.
    location : ~analyticsapi.models.Location
        Object defining metadata for the IrSwap. Required.
    description : ~analyticsapi.models.Description
        Object defining the IrSwap.
    """

    type: Optional[Literal[ResourceType.IR_SWAP]] = rest_field(visibility=["read"], default=ResourceType.IR_SWAP)
    """Property defining the type of the resource."""
    id: Optional[str] = rest_field(visibility=["read"])
    """Unique identifier of the IrSwap."""
    location: "_models.Location" = rest_field(visibility=["read", "create"])
    """Object defining metadata for the IrSwap. Required."""
    description: Optional["_models.Description"] = rest_field()
    """Object defining the IrSwap."""

    @overload
    def __init__(
        self,
        *,
        location: "_models.Location",
        description: Optional["_models.Description"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrSwapCollectionLinks(_model_base.Model):
    """IrSwapCollectionLinks.

    Attributes
    ----------
    self_property : ~analyticsapi.models.Link
        Required.
    first : ~analyticsapi.models.Link
    prev : ~analyticsapi.models.Link
    next : ~analyticsapi.models.Link
    last : ~analyticsapi.models.Link
    """

    self_property: "_models.Link" = rest_field(name="self")
    """Required."""
    first: Optional["_models.Link"] = rest_field()
    prev: Optional["_models.Link"] = rest_field()
    next: Optional["_models.Link"] = rest_field()
    last: Optional["_models.Link"] = rest_field()

    @overload
    def __init__(
        self,
        *,
        self_property: "_models.Link",
        first: Optional["_models.Link"] = None,
        prev: Optional["_models.Link"] = None,
        next: Optional["_models.Link"] = None,
        last: Optional["_models.Link"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrSwapCollectionResponse(_model_base.Model):
    """A model template describing a paged response.

    Attributes
    ----------
    data : list[~analyticsapi.models.IrSwapAsCollectionItem]
        Required.  The default value is None, needs to be assigned before
        using.
    page : int
        The page number of the current page displayed. Minimum value of this
        property is 1. Required.
    item_per_page : int
        Number of items displayed per page. Required.
    total_pages : int
        Total number of pages available for display. Required.
    total_items : int
        Total number of items available for display. Required.
    links : ~analyticsapi.models.IrSwapCollectionLinks
        Links for available operations and/or resources linked to current
        response.
    """

    data: List["_models.IrSwapAsCollectionItem"] = rest_field()
    """Required."""
    page: int = rest_field()
    """The page number of the current page displayed. Minimum value of this property is 1. Required."""
    item_per_page: int = rest_field(name="itemPerPage")
    """Number of items displayed per page. Required."""
    total_pages: int = rest_field(name="totalPages")
    """Total number of pages available for display. Required."""
    total_items: int = rest_field(name="totalItems")
    """Total number of items available for display. Required."""
    links: Optional["_models.IrSwapCollectionLinks"] = rest_field()
    """Links for available operations and/or resources linked to current response."""

    @overload
    def __init__(
        self,
        *,
        data: List["_models.IrSwapAsCollectionItem"],
        page: int,
        item_per_page: int,
        total_pages: int,
        total_items: int,
        links: Optional["_models.IrSwapCollectionLinks"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrSwapDefinition(_model_base.Model):
    """An object that defines an interest rate swap.

    Attributes
    ----------
    first_leg : ~analyticsapi.models.InterestRateLegDefinition
        An object that defines the paid leg of the swap. Required.
    second_leg : ~analyticsapi.models.InterestRateLegDefinition
        An object that defines the received leg of the swap. Required.
    upfront_payment : ~analyticsapi.models.Payment
        An object that defines the upfront payment of the swap.
    """

    first_leg: "_models.InterestRateLegDefinition" = rest_field(name="firstLeg")
    """An object that defines the paid leg of the swap. Required."""
    second_leg: "_models.InterestRateLegDefinition" = rest_field(name="secondLeg")
    """An object that defines the received leg of the swap. Required."""
    upfront_payment: Optional["_models.Payment"] = rest_field(name="upfrontPayment")
    """An object that defines the upfront payment of the swap."""

    @overload
    def __init__(
        self,
        *,
        first_leg: "_models.InterestRateLegDefinition",
        second_leg: "_models.InterestRateLegDefinition",
        upfront_payment: Optional["_models.Payment"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrSwapDefinitionInstrument(_model_base.Model):
    """An array of objects describing a curve or an instrument.
    Please provide either a full definition (for a user-defined curve/instrument), or reference to
    a curve/instrument definition saved in the platform, or the code identifying the existing
    curve/instrument.

    Attributes
    ----------
    definition : ~analyticsapi.models.IrSwapDefinition
        The object that describes the definition of the instrument.
    reference : str
        The identifier of a resource (instrument definition, curve definition)
        that is already in the platform.
    code : str
        The unique public code used to identify an instrument that exists on
        the market (ISIN, RIC, etc.).
    """

    definition: Optional["_models.IrSwapDefinition"] = rest_field()
    """The object that describes the definition of the instrument."""
    reference: Optional[str] = rest_field()
    """The identifier of a resource (instrument definition, curve definition) that is already in the
     platform."""
    code: Optional[str] = rest_field()
    """The unique public code used to identify an instrument that exists on the market (ISIN, RIC,
     etc.)."""

    @overload
    def __init__(
        self,
        *,
        definition: Optional["_models.IrSwapDefinition"] = None,
        reference: Optional[str] = None,
        code: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrSwapInstrumentArraySolveResponse(_model_base.Model):
    """The solve response of the swaps that are defined as part of a request.

    Attributes
    ----------
    data : ~analyticsapi.models.IrSwapInstrumentSolveResponseFieldsResponseData
        An object that contains calculated analytics, requested, and other data
        used for calculation. Required.
    """

    data: "_models.IrSwapInstrumentSolveResponseFieldsResponseData" = rest_field()
    """An object that contains calculated analytics, requested, and other data used for calculation.
     Required."""

    @overload
    def __init__(
        self,
        data: "_models.IrSwapInstrumentSolveResponseFieldsResponseData",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["data"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class IrSwapInstrumentArrayValuationResponse(_model_base.Model):
    """The valuation response of the swaps that are defined as part of a request.

    Attributes
    ----------
    data : ~analyticsapi.models.IrSwapInstrumentValuationResponseFieldsResponseData
        An object that contains calculated analytics, requested, and other data
        used for calculation. Required.
    """

    data: "_models.IrSwapInstrumentValuationResponseFieldsResponseData" = rest_field()
    """An object that contains calculated analytics, requested, and other data used for calculation.
     Required."""

    @overload
    def __init__(
        self,
        data: "_models.IrSwapInstrumentValuationResponseFieldsResponseData",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["data"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class IrSwapInstrumentDescriptionFields(_model_base.Model):
    """An object that contains fields related to the swap description.

    Attributes
    ----------
    instrument_tag : str
        A user defined string to identify the instrument. It can be used to
        link output results to the instrument definition. Limited to 40
        characters. Only alphabetic, numeric and the characters  '- _.#=@' are
        supported.
    instrument_description : str
        The label that describes the instrument. Required.
    start_date : ~datetime.date
        The start date of the instrument. This value is expressed in ISO 8601
        format: YYYY-MM-DD (e.g., 2021-01-01). Required.
    end_date : ~datetime.date
        The maturity or expiry date of the instrument. The value is expressed
        in ISO 8601 format: YYYY-MM-DD (e.g., 2021-01-01). Required.
    tenor : str
        The code indicating the period between startDate and endDate of the
        instrument (e.g., '6M', '1Y'). A tenor expresses a period of time using
        a specific syntax. There are two kinds of tenor:

        * Ad-hoc tenors explicitly state the length of time in Days (D), Weeks (W), Months (M) and
        Years (Y).
          For example "1D" for one day, "2W" for two weeks or "3M1D" for three months and a day.
          When mixing units, units must be written in descending order of size (Y > M > W > D).  So,
        5M3D is valid, but 3D5M is not.
        * Common tenors are expressed as letter codes:
        * ON (Overnight) - A one business day period that starts today.
        * TN (Tomorrow-Next) - A one business day period that starts next business day.
        * SPOT (Spot Date) - A period that ends on the spot date.  Date is calculated as trade date
        (today) + days to spot.
        * SN (Spot-Next) - A one business day period that starts at the spot date.
        * SW (Spot-Week) - A one business week period that starts at the spot date. Required.
    """

    instrument_tag: Optional[str] = rest_field(name="instrumentTag")
    """A user defined string to identify the instrument. It can be used to link output results to the
     instrument definition. Limited to 40 characters. Only alphabetic, numeric and the characters
     '- _.#=@' are supported."""
    instrument_description: str = rest_field(name="instrumentDescription")
    """The label that describes the instrument. Required."""
    start_date: datetime.date = rest_field(name="startDate")
    """The start date of the instrument. This value is expressed in ISO 8601 format: YYYY-MM-DD (e.g.,
     2021-01-01). Required."""
    end_date: datetime.date = rest_field(name="endDate")
    """The maturity or expiry date of the instrument. The value is expressed in ISO 8601 format:
     YYYY-MM-DD (e.g., 2021-01-01). Required."""
    tenor: str = rest_field()
    """The code indicating the period between startDate and endDate of the instrument (e.g., '6M',
     '1Y').
     A tenor expresses a period of time using a specific syntax. There are two kinds of tenor:
     
     
     * Ad-hoc tenors explicitly state the length of time in Days (D), Weeks (W), Months (M) and
     Years (Y).
       For example \"1D\" for one day, \"2W\" for two weeks or \"3M1D\" for three months and a day.
       When mixing units, units must be written in descending order of size (Y > M > W > D).  So,
     5M3D is valid, but 3D5M is not.
     * Common tenors are expressed as letter codes:
     * ON (Overnight) - A one business day period that starts today.
     * TN (Tomorrow-Next) - A one business day period that starts next business day.
     * SPOT (Spot Date) - A period that ends on the spot date.  Date is calculated as trade date
     (today) + days to spot.
     * SN (Spot-Next) - A one business day period that starts at the spot date.
     * SW (Spot-Week) - A one business week period that starts at the spot date. Required."""

    @overload
    def __init__(
        self,
        *,
        instrument_description: str,
        start_date: datetime.date,
        end_date: datetime.date,
        tenor: str,
        instrument_tag: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrSwapInstrumentRiskFields(IrRiskFields):
    """An object that contains fields related to swap risk assessment.

    Attributes
    ----------
    duration : ~analyticsapi.models.IrMeasure
        An object that describes the weighted average maturity in years of all
        cash flows. The final cash flow includes the principal, which has a
        much greater weight than the intermediate cash flows. Required.
    modified_duration : ~analyticsapi.models.IrMeasure
        An object that describes the measure of price sensitivity in percent to
        a 100 basis points change in the instrument's yield, or a 1% parallel
        shift in the underlying zero-coupon curve. For a floating rate
        instrument, it is computed as time to next payment. Required.
    benchmark_hedge_notional : ~analyticsapi.models.Amount
        An object that specifies the notional amount of the benchmark
        instrument that allows to hedge the instrument (available for IRS
        only). The value is expressed in the deal currency. It is computed for
        instrument legs only. Required.
    annuity : ~analyticsapi.models.IrMeasure
        An object that describes the sensitivity of the net present value of
        the fixed rate leg to a 1bp shift in the fixed rate. Required.
    dv01 : ~analyticsapi.models.IrMeasure
        An object that describes the sensitivity of the net present value to a
        1bp parallel shift in the zero-coupon curve. Required.
    pv01 : ~analyticsapi.models.IrMeasure
        An object that describes the sensitivity of the net present value to a
        1bp parallel shift in the yield curve. Required.
    br01 : ~analyticsapi.models.IrMeasure
        An object that describes the sensitivity of the net present value to a
        1bp shift of Currency Basis Swap (CBS) spreads. Required.
    """

    @overload
    def __init__(
        self,
        *,
        duration: "_models.IrMeasure",
        modified_duration: "_models.IrMeasure",
        benchmark_hedge_notional: "_models.Amount",
        annuity: "_models.IrMeasure",
        dv01: "_models.IrMeasure",
        pv01: "_models.IrMeasure",
        br01: "_models.IrMeasure",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrSwapInstrumentSolveResponse(_model_base.Model):
    """The solve response of a swap that is already on the platform.

    Attributes
    ----------
    data : ~analyticsapi.models.IrSwapInstrumentSolveResponseFieldsOnResourceResponseData
        Required.
    """

    data: "_models.IrSwapInstrumentSolveResponseFieldsOnResourceResponseData" = rest_field()
    """Required."""

    @overload
    def __init__(
        self,
        data: "_models.IrSwapInstrumentSolveResponseFieldsOnResourceResponseData",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["data"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class IrSwapInstrumentSolveResponseFieldsOnResourceResponseData(_model_base.Model):  # pylint: disable=name-too-long
    """IrSwapInstrumentSolveResponseFieldsOnResourceResponseData.

    Attributes
    ----------
    resource : ~analyticsapi.models.IrSwap
        Definition of the resource.
    pricing_preferences : ~analyticsapi.models.IrPricingParameters
        The parameters that control the computation of the analytics.
    analytics : ~analyticsapi.models.IrSwapInstrumentSolveResponseFieldsResponseWithError
        The result of the calculation request.
    market_data : ~analyticsapi.models.MarketData
        The market data used to compute the analytics.
    """

    resource: Optional["_models.IrSwap"] = rest_field()
    """Definition of the resource."""
    pricing_preferences: Optional["_models.IrPricingParameters"] = rest_field(name="pricingPreferences")
    """The parameters that control the computation of the analytics."""
    analytics: Optional["_models.IrSwapInstrumentSolveResponseFieldsResponseWithError"] = rest_field()
    """The result of the calculation request."""
    market_data: Optional["_models.MarketData"] = rest_field(name="marketData")
    """The market data used to compute the analytics."""

    @overload
    def __init__(
        self,
        *,
        resource: Optional["_models.IrSwap"] = None,
        pricing_preferences: Optional["_models.IrPricingParameters"] = None,
        analytics: Optional["_models.IrSwapInstrumentSolveResponseFieldsResponseWithError"] = None,
        market_data: Optional["_models.MarketData"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrSwapInstrumentSolveResponseFieldsResponseData(_model_base.Model):  # pylint: disable=name-too-long
    """IrSwapInstrumentSolveResponseFieldsResponseData.

    Attributes
    ----------
    definitions : list[~analyticsapi.models.IrSwapDefinitionInstrument]
        The default value is None, needs to be assigned before using.
    pricing_preferences : ~analyticsapi.models.IrPricingParameters
        The parameters that control the computation of the analytics.
    analytics : list[~analyticsapi.models.IrSwapInstrumentSolveResponseFieldsResponseWithError]
        The result of the calculation request.  The default value is None,
        needs to be assigned before using.
    market_data : ~analyticsapi.models.MarketData
        The market data used to compute the analytics.
    """

    definitions: Optional[List["_models.IrSwapDefinitionInstrument"]] = rest_field()
    pricing_preferences: Optional["_models.IrPricingParameters"] = rest_field(name="pricingPreferences")
    """The parameters that control the computation of the analytics."""
    analytics: Optional[List["_models.IrSwapInstrumentSolveResponseFieldsResponseWithError"]] = rest_field()
    """The result of the calculation request."""
    market_data: Optional["_models.MarketData"] = rest_field(name="marketData")
    """The market data used to compute the analytics."""

    @overload
    def __init__(
        self,
        *,
        definitions: Optional[List["_models.IrSwapDefinitionInstrument"]] = None,
        pricing_preferences: Optional["_models.IrPricingParameters"] = None,
        analytics: Optional[List["_models.IrSwapInstrumentSolveResponseFieldsResponseWithError"]] = None,
        market_data: Optional["_models.MarketData"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrSwapInstrumentSolveResponseFieldsResponseWithError(_model_base.Model):  # pylint: disable=name-too-long
    """A model template describing a response with an error for a given object.

    Attributes
    ----------
    solving : ~analyticsapi.models.SolvingResult
        An object that contains the swap solving result. Required.
    description : ~analyticsapi.models.IrSwapInstrumentDescriptionFields
        An object that contains fields related to the swap description.
        Required.
    valuation : ~analyticsapi.models.IrSwapInstrumentValuationFields
        An object that contains fields related to the swap valuation.
    risk : ~analyticsapi.models.IrSwapInstrumentRiskFields
        An object that contains fields related to the swap risk assessment.
    first_leg : ~analyticsapi.models.IrLegValuationResponseFields
        An object that contains fields related to the first leg of the swap.
    second_leg : ~analyticsapi.models.IrLegValuationResponseFields
        An object that contains fields related to the second leg of the swap.
    error : ~analyticsapi.models.ServiceError
        The error message for the calculation in case of a non-blocking error.
    """

    solving: "_models.SolvingResult" = rest_field()
    """An object that contains the swap solving result. Required."""
    description: "_models.IrSwapInstrumentDescriptionFields" = rest_field()
    """An object that contains fields related to the swap description. Required."""
    valuation: Optional["_models.IrSwapInstrumentValuationFields"] = rest_field()
    """An object that contains fields related to the swap valuation."""
    risk: Optional["_models.IrSwapInstrumentRiskFields"] = rest_field()
    """An object that contains fields related to the swap risk assessment."""
    first_leg: Optional["_models.IrLegValuationResponseFields"] = rest_field(name="firstLeg")
    """An object that contains fields related to the first leg of the swap."""
    second_leg: Optional["_models.IrLegValuationResponseFields"] = rest_field(name="secondLeg")
    """An object that contains fields related to the second leg of the swap."""
    error: Optional["_models.ServiceError"] = rest_field()
    """The error message for the calculation in case of a non-blocking error."""

    @overload
    def __init__(
        self,
        *,
        solving: "_models.SolvingResult",
        description: "_models.IrSwapInstrumentDescriptionFields",
        valuation: Optional["_models.IrSwapInstrumentValuationFields"] = None,
        risk: Optional["_models.IrSwapInstrumentRiskFields"] = None,
        first_leg: Optional["_models.IrLegValuationResponseFields"] = None,
        second_leg: Optional["_models.IrLegValuationResponseFields"] = None,
        error: Optional["_models.ServiceError"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrValuationFields(_model_base.Model):
    """An object that contains fields related to the instrument's valuation.

    Attributes
    ----------
    accrued : ~analyticsapi.models.IrMeasure
        An object that describes accrued interest that is accumulated but not
        paid out. Required.
    market_value : ~analyticsapi.models.IrMeasure
        An object that describes the market value of the instrument. Required.
    clean_market_value : ~analyticsapi.models.IrMeasure
        An object that describes the market value of the instrument less any
        accrued interest. Required.
    """

    accrued: "_models.IrMeasure" = rest_field()
    """An object that describes accrued interest that is accumulated but not paid out. Required."""
    market_value: "_models.IrMeasure" = rest_field(name="marketValue")
    """An object that describes the market value of the instrument. Required."""
    clean_market_value: "_models.IrMeasure" = rest_field(name="cleanMarketValue")
    """An object that describes the market value of the instrument less any accrued interest.
     Required."""

    @overload
    def __init__(
        self,
        *,
        accrued: "_models.IrMeasure",
        market_value: "_models.IrMeasure",
        clean_market_value: "_models.IrMeasure",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrSwapInstrumentValuationFields(IrValuationFields):
    """An object that contains fields related to the swap valuation.

    Attributes
    ----------
    accrued : ~analyticsapi.models.IrMeasure
        An object that describes accrued interest that is accumulated but not
        paid out. Required.
    market_value : ~analyticsapi.models.IrMeasure
        An object that describes the market value of the instrument. Required.
    clean_market_value : ~analyticsapi.models.IrMeasure
        An object that describes the market value of the instrument less any
        accrued interest. Required.
    """

    @overload
    def __init__(
        self,
        *,
        accrued: "_models.IrMeasure",
        market_value: "_models.IrMeasure",
        clean_market_value: "_models.IrMeasure",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrSwapInstrumentValuationResponse(_model_base.Model):
    """The valuation response of a swap that is already on the platform.

    Attributes
    ----------
    data : ~analyticsapi.models.IrSwapInstrumentValuationResponseFieldsOnResourceResponseData
        Required.
    """

    data: "_models.IrSwapInstrumentValuationResponseFieldsOnResourceResponseData" = rest_field()
    """Required."""

    @overload
    def __init__(
        self,
        data: "_models.IrSwapInstrumentValuationResponseFieldsOnResourceResponseData",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["data"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class IrSwapInstrumentValuationResponseFieldsOnResourceResponseData(_model_base.Model):  # pylint: disable=name-too-long
    """IrSwapInstrumentValuationResponseFieldsOnResourceResponseData.

    Attributes
    ----------
    resource : ~analyticsapi.models.IrSwap
        Definition of the resource.
    pricing_preferences : ~analyticsapi.models.IrPricingParameters
        The parameters that control the computation of the analytics.
    analytics : ~analyticsapi.models.IrSwapInstrumentValuationResponseFieldsResponseWithError
        The result of the calculation request.
    market_data : ~analyticsapi.models.MarketData
        The market data used to compute the analytics.
    """

    resource: Optional["_models.IrSwap"] = rest_field()
    """Definition of the resource."""
    pricing_preferences: Optional["_models.IrPricingParameters"] = rest_field(name="pricingPreferences")
    """The parameters that control the computation of the analytics."""
    analytics: Optional["_models.IrSwapInstrumentValuationResponseFieldsResponseWithError"] = rest_field()
    """The result of the calculation request."""
    market_data: Optional["_models.MarketData"] = rest_field(name="marketData")
    """The market data used to compute the analytics."""

    @overload
    def __init__(
        self,
        *,
        resource: Optional["_models.IrSwap"] = None,
        pricing_preferences: Optional["_models.IrPricingParameters"] = None,
        analytics: Optional["_models.IrSwapInstrumentValuationResponseFieldsResponseWithError"] = None,
        market_data: Optional["_models.MarketData"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrSwapInstrumentValuationResponseFieldsResponseData(_model_base.Model):  # pylint: disable=name-too-long
    """IrSwapInstrumentValuationResponseFieldsResponseData.

    Attributes
    ----------
    definitions : list[~analyticsapi.models.IrSwapDefinitionInstrument]
        The default value is None, needs to be assigned before using.
    pricing_preferences : ~analyticsapi.models.IrPricingParameters
        The parameters that control the computation of the analytics.
    analytics : list[~analyticsapi.models.IrSwapInstrumentValuationResponseFieldsResponseWithError]
        The result of the calculation request.  The default value is None,
        needs to be assigned before using.
    market_data : ~analyticsapi.models.MarketData
        The market data used to compute the analytics.
    """

    definitions: Optional[List["_models.IrSwapDefinitionInstrument"]] = rest_field()
    pricing_preferences: Optional["_models.IrPricingParameters"] = rest_field(name="pricingPreferences")
    """The parameters that control the computation of the analytics."""
    analytics: Optional[List["_models.IrSwapInstrumentValuationResponseFieldsResponseWithError"]] = rest_field()
    """The result of the calculation request."""
    market_data: Optional["_models.MarketData"] = rest_field(name="marketData")
    """The market data used to compute the analytics."""

    @overload
    def __init__(
        self,
        *,
        definitions: Optional[List["_models.IrSwapDefinitionInstrument"]] = None,
        pricing_preferences: Optional["_models.IrPricingParameters"] = None,
        analytics: Optional[List["_models.IrSwapInstrumentValuationResponseFieldsResponseWithError"]] = None,
        market_data: Optional["_models.MarketData"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrSwapInstrumentValuationResponseFieldsResponseWithError(_model_base.Model):  # pylint: disable=name-too-long
    """A model template describing a response with an error for a given object.

    Attributes
    ----------
    description : ~analyticsapi.models.IrSwapInstrumentDescriptionFields
        An object that contains fields related to the swap description.
        Required.
    valuation : ~analyticsapi.models.IrSwapInstrumentValuationFields
        An object that contains fields related to the swap valuation.
    risk : ~analyticsapi.models.IrSwapInstrumentRiskFields
        An object that contains fields related to the swap risk assessment.
    first_leg : ~analyticsapi.models.IrLegValuationResponseFields
        An object that contains fields related to the first leg of the swap.
    second_leg : ~analyticsapi.models.IrLegValuationResponseFields
        An object that contains fields related to the second leg of the swap.
    error : ~analyticsapi.models.ServiceError
        The error message for the calculation in case of a non-blocking error.
    """

    description: "_models.IrSwapInstrumentDescriptionFields" = rest_field()
    """An object that contains fields related to the swap description. Required."""
    valuation: Optional["_models.IrSwapInstrumentValuationFields"] = rest_field()
    """An object that contains fields related to the swap valuation."""
    risk: Optional["_models.IrSwapInstrumentRiskFields"] = rest_field()
    """An object that contains fields related to the swap risk assessment."""
    first_leg: Optional["_models.IrLegValuationResponseFields"] = rest_field(name="firstLeg")
    """An object that contains fields related to the first leg of the swap."""
    second_leg: Optional["_models.IrLegValuationResponseFields"] = rest_field(name="secondLeg")
    """An object that contains fields related to the second leg of the swap."""
    error: Optional["_models.ServiceError"] = rest_field()
    """The error message for the calculation in case of a non-blocking error."""

    @overload
    def __init__(
        self,
        *,
        description: "_models.IrSwapInstrumentDescriptionFields",
        valuation: Optional["_models.IrSwapInstrumentValuationFields"] = None,
        risk: Optional["_models.IrSwapInstrumentRiskFields"] = None,
        first_leg: Optional["_models.IrLegValuationResponseFields"] = None,
        second_leg: Optional["_models.IrLegValuationResponseFields"] = None,
        error: Optional["_models.ServiceError"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrSwapResponse(_model_base.Model):
    """A model template describing a single response.

    Attributes
    ----------
    data : ~analyticsapi.models.IrSwap
        Required.
    meta : ~analyticsapi.models.MetaData
    """

    data: "_models.IrSwap" = rest_field()
    """Required."""
    meta: Optional["_models.MetaData"] = rest_field()

    @overload
    def __init__(
        self,
        *,
        data: "_models.IrSwap",
        meta: Optional["_models.MetaData"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrSwapSolvingParameters(_model_base.Model):
    """An object that contains the solving target and variable parameters applied to an interest rate
    swap.
    These parameters provide an approach to obtaining the target value by selecting a variable
    value.
    This allows to consider different scenarios of the behavior of a specific parameter (variable)
    given the set value of another parameter (target).

    Attributes
    ----------
    variable : ~analyticsapi.models.IrSwapSolvingVariable
        An object that contains the properties used to identify the swap
        variable parameter. Required.
    target : ~analyticsapi.models.IrSwapSolvingTarget
        An object that contains the properties applied to the swap target
        parameter. Required.
    """

    variable: "_models.IrSwapSolvingVariable" = rest_field()
    """An object that contains the properties used to identify the swap variable parameter. Required."""
    target: "_models.IrSwapSolvingTarget" = rest_field()
    """An object that contains the properties applied to the swap target parameter. Required."""

    @overload
    def __init__(
        self,
        *,
        variable: "_models.IrSwapSolvingVariable",
        target: "_models.IrSwapSolvingTarget",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrSwapSolvingTarget(_model_base.Model):  # pylint: disable=too-many-instance-attributes
    """ "An object that contains the properties that apply to the swap target parameter.
        To obtain the solution for the selected variable parameter please specify the value of the
        target parameter.
        Note: Only one of possible target parameters should be requested for solver computations.

        :ivar leg: A swap leg to which the target property applies. It can be used where several
    options are possible (e.g., the market value of the first leg). Known values are: "FirstLeg"
    and "SecondLeg".
        :vartype leg: str or ~analyticsapi.models.SolvingLegEnum
        :ivar accrued: An object that describes the target as the accrued interest of one of the swap
    legs or the swap instrument globally.
        :vartype accrued: ~analyticsapi.models.IrMeasure
        :ivar market_value: An object that describes the target as the market value of one of the swap
    legs or the swap instrument globally.
        :vartype market_value: ~analyticsapi.models.IrMeasure
        :ivar clean_market_value: An object that describes the target as the clean market value of one
    of the swap legs or the swap instrument globally.
        :vartype clean_market_value: ~analyticsapi.models.IrMeasure
        :ivar duration: An object that describes the target as the duration of one of the swap legs or
    the swap instrument globally.
        :vartype duration: ~analyticsapi.models.IrMeasure
        :ivar modified_duration: An object that describes the target as the modified duration of one of
    the swap legs or the swap instrument globally.
        :vartype modified_duration: ~analyticsapi.models.IrMeasure
        :ivar dv01: An object that describes the target as the dv01 of one of the swap legs or the swap
    instrument globally.
        :vartype dv01: ~analyticsapi.models.IrMeasure
        :ivar pv01: An object that describes the target as the pv01 of one of the swap legs or the swap
    instrument globally.
        :vartype pv01: ~analyticsapi.models.IrMeasure
        :ivar br01: An object that describes the target as the br01 of one of the swap legs or the swap
    instrument globally.
        :vartype br01: ~analyticsapi.models.IrMeasure
        :ivar annuity: An object that describes the target as the annuity of one of the swap legs or
    the swap instrument globally.
        :vartype annuity: ~analyticsapi.models.IrMeasure
        :ivar fixed_rate: An object that describes the target as the fixed rate of the swap.
        :vartype fixed_rate: ~analyticsapi.models.Rate
        :ivar spread: An object that describes the target as the spread over the floating rate of the
    swap.
        :vartype spread: ~analyticsapi.models.Rate
    """

    leg: Optional[Union[str, "_models.SolvingLegEnum"]] = rest_field()
    """A swap leg to which the target property applies. It can be used where several options are
     possible (e.g., the market value of the first leg). Known values are: \"FirstLeg\" and
     \"SecondLeg\"."""
    accrued: Optional["_models.IrMeasure"] = rest_field()
    """An object that describes the target as the accrued interest of one of the swap legs or the swap
     instrument globally."""
    market_value: Optional["_models.IrMeasure"] = rest_field(name="marketValue")
    """An object that describes the target as the market value of one of the swap legs or the swap
     instrument globally."""
    clean_market_value: Optional["_models.IrMeasure"] = rest_field(name="cleanMarketValue")
    """An object that describes the target as the clean market value of one of the swap legs or the
     swap instrument globally."""
    duration: Optional["_models.IrMeasure"] = rest_field()
    """An object that describes the target as the duration of one of the swap legs or the swap
     instrument globally."""
    modified_duration: Optional["_models.IrMeasure"] = rest_field(name="modifiedDuration")
    """An object that describes the target as the modified duration of one of the swap legs or the
     swap instrument globally."""
    dv01: Optional["_models.IrMeasure"] = rest_field()
    """An object that describes the target as the dv01 of one of the swap legs or the swap instrument
     globally."""
    pv01: Optional["_models.IrMeasure"] = rest_field()
    """An object that describes the target as the pv01 of one of the swap legs or the swap instrument
     globally."""
    br01: Optional["_models.IrMeasure"] = rest_field()
    """An object that describes the target as the br01 of one of the swap legs or the swap instrument
     globally."""
    annuity: Optional["_models.IrMeasure"] = rest_field()
    """An object that describes the target as the annuity of one of the swap legs or the swap
     instrument globally."""
    fixed_rate: Optional["_models.Rate"] = rest_field(name="fixedRate")
    """An object that describes the target as the fixed rate of the swap."""
    spread: Optional["_models.Rate"] = rest_field()
    """An object that describes the target as the spread over the floating rate of the swap."""

    @overload
    def __init__(
        self,
        *,
        leg: Optional[Union[str, "_models.SolvingLegEnum"]] = None,
        accrued: Optional["_models.IrMeasure"] = None,
        market_value: Optional["_models.IrMeasure"] = None,
        clean_market_value: Optional["_models.IrMeasure"] = None,
        duration: Optional["_models.IrMeasure"] = None,
        modified_duration: Optional["_models.IrMeasure"] = None,
        dv01: Optional["_models.IrMeasure"] = None,
        pv01: Optional["_models.IrMeasure"] = None,
        br01: Optional["_models.IrMeasure"] = None,
        annuity: Optional["_models.IrMeasure"] = None,
        fixed_rate: Optional["_models.Rate"] = None,
        spread: Optional["_models.Rate"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrSwapSolvingVariable(_model_base.Model):
    """An object that contains the properties used to identify the swap variable parameter.

    Attributes
    ----------
    leg : str or ~analyticsapi.models.SolvingLegEnum
        A swap leg to which the variable property applies. It can be used where
        several options are possible (e.g., the spread of a tenor basis swap).
        Known values are: "FirstLeg" and "SecondLeg".
    name : str or ~analyticsapi.models.SwapSolvingVariableEnum
        The list of swap variable parameters for which the solution is
        calculated. Known values are: "FixedRate" and "Spread".
    """

    leg: Optional[Union[str, "_models.SolvingLegEnum"]] = rest_field()
    """A swap leg to which the variable property applies. It can be used where several options are
     possible (e.g., the spread of a tenor basis swap). Known values are: \"FirstLeg\" and
     \"SecondLeg\"."""
    name: Optional[Union[str, "_models.SwapSolvingVariableEnum"]] = rest_field()
    """The list of swap variable parameters for which the solution is calculated. Known values are:
     \"FixedRate\" and \"Spread\"."""

    @overload
    def __init__(
        self,
        *,
        leg: Optional[Union[str, "_models.SolvingLegEnum"]] = None,
        name: Optional[Union[str, "_models.SwapSolvingVariableEnum"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrSwaptionVolCubeChoice(_model_base.Model):
    """The object to provide either a reference to a interest rate swaption volatility surface stored
    in the platform or 3rd party volatilities.

    Attributes
    ----------
    reference : str
        The reference to a volatility surface stored in the platform.
    cube : ~analyticsapi.models.IrVolCubeInput
        The volatility cube data.
    """

    reference: Optional[str] = rest_field()
    """The reference to a volatility surface stored in the platform."""
    cube: Optional["_models.IrVolCubeInput"] = rest_field()
    """The volatility cube data."""

    @overload
    def __init__(
        self,
        *,
        reference: Optional[str] = None,
        cube: Optional["_models.IrVolCubeInput"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrVolCubeInput(_model_base.Model):
    """The object defining the 3rd party interest rate swaption volatility cube.

    Attributes
    ----------
    strike_type : str or ~analyticsapi.models.StrikeTypeEnum
        The property that defines the type of the strikes provided in the
        surface points. Required. Known values are: "Absolute", "BasisPoint",
        "Delta", "Moneyness", "Percent", and "Relative".
    model_type : str or ~analyticsapi.models.VolModelTypeEnum
        The property that defines the type of the model (Normal or LogNormal)
        of the volatilities provided in the surface points. Required. Known
        values are: "Normal" and "LogNormal".
    points : list[~analyticsapi.models.VolCubePoint]
        The list of volatility points. Required.  The default value is None,
        needs to be assigned before using.
    index_reference : str
        The reference to the floating rate index. Required.
    """

    strike_type: Union[str, "_models.StrikeTypeEnum"] = rest_field(name="strikeType")
    """The property that defines the type of the strikes provided in the surface points. Required.
     Known values are: \"Absolute\", \"BasisPoint\", \"Delta\", \"Moneyness\", \"Percent\", and
     \"Relative\"."""
    model_type: Union[str, "_models.VolModelTypeEnum"] = rest_field(name="modelType")
    """The property that defines the type of the model (Normal or LogNormal) of the volatilities
     provided in the surface points. Required. Known values are: \"Normal\" and \"LogNormal\"."""
    points: List["_models.VolCubePoint"] = rest_field()
    """The list of volatility points. Required."""
    index_reference: str = rest_field(name="indexReference")
    """The reference to the floating rate index. Required."""

    @overload
    def __init__(
        self,
        *,
        strike_type: Union[str, "_models.StrikeTypeEnum"],
        model_type: Union[str, "_models.VolModelTypeEnum"],
        points: List["_models.VolCubePoint"],
        index_reference: str,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrVolSurfaceInput(_model_base.Model):
    """The object defining the 3rd party interest rate cap volatility surface.

    Attributes
    ----------
    strike_type : str or ~analyticsapi.models.StrikeTypeEnum
        The property that defines the type of the strikes provided in the
        surface points. Required. Known values are: "Absolute", "BasisPoint",
        "Delta", "Moneyness", "Percent", and "Relative".
    model_type : str or ~analyticsapi.models.VolModelTypeEnum
        The property that defines the type of the model (Normal or LogNormal)
        of the volatilities provided in the surface points. Required. Known
        values are: "Normal" and "LogNormal".
    points : list[~analyticsapi.models.VolSurfacePoint]
        The list of volatility points. Required.  The default value is None,
        needs to be assigned before using.
    index_reference : str
        The reference to the floating rate index. Required.
    """

    strike_type: Union[str, "_models.StrikeTypeEnum"] = rest_field(name="strikeType")
    """The property that defines the type of the strikes provided in the surface points. Required.
     Known values are: \"Absolute\", \"BasisPoint\", \"Delta\", \"Moneyness\", \"Percent\", and
     \"Relative\"."""
    model_type: Union[str, "_models.VolModelTypeEnum"] = rest_field(name="modelType")
    """The property that defines the type of the model (Normal or LogNormal) of the volatilities
     provided in the surface points. Required. Known values are: \"Normal\" and \"LogNormal\"."""
    points: List["_models.VolSurfacePoint"] = rest_field()
    """The list of volatility points. Required."""
    index_reference: str = rest_field(name="indexReference")
    """The reference to the floating rate index. Required."""

    @overload
    def __init__(
        self,
        *,
        strike_type: Union[str, "_models.StrikeTypeEnum"],
        model_type: Union[str, "_models.VolModelTypeEnum"],
        points: List["_models.VolSurfacePoint"],
        index_reference: str,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrZcCurve(Curve, discriminator="IrZcCurve"):
    """The model defining the output of a interest rate zc curve calculation.

    Attributes
    ----------
    curve_type : str or ~analyticsapi.models.IR_ZC_CURVE
        The type of the curve. Required.
    index : str
        The reference to the floating rate index.
    points : list[~analyticsapi.models.IrZcCurvePoint]
        The list of output points.  The default value is None, needs to be
        assigned before using.
    """

    curve_type: Literal[CurveTypeEnum.IR_ZC_CURVE] = rest_discriminator(name="curveType")  # type: ignore
    """The type of the curve. Required."""
    index: Optional[str] = rest_field()
    """The reference to the floating rate index."""
    points: Optional[List["_models.IrZcCurvePoint"]] = rest_field()
    """The list of output points."""

    @overload
    def __init__(
        self,
        *,
        index: Optional[str] = None,
        points: Optional[List["_models.IrZcCurvePoint"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, curve_type=CurveTypeEnum.IR_ZC_CURVE, **kwargs)


class IrZcCurveInput(_model_base.Model):
    """The object defining the 3rd party interest rate zero curve.

    Attributes
    ----------
    zc_type : str or ~analyticsapi.models.ZcTypeEnum
        The type of values provided (zero coupon rates or discount factors).
        Required. Known values are: "Rate" and "DiscountFactor".
    zc_unit : str or ~analyticsapi.models.UnitEnum
        The unit of the values provided (absolute, basis point, percentage).
        Required. Known values are: "Absolute", "BasisPoint", and "Percentage".
    points : list[~analyticsapi.models.CurveDataPoint]
        The list of dates and values. Required.  The default value is None,
        needs to be assigned before using.
    index_reference : str
        The reference to the floating rate index. Required.
    """

    zc_type: Union[str, "_models.ZcTypeEnum"] = rest_field(name="zcType")
    """The type of values provided (zero coupon rates or discount factors). Required. Known values
     are: \"Rate\" and \"DiscountFactor\"."""
    zc_unit: Union[str, "_models.UnitEnum"] = rest_field(name="zcUnit")
    """The unit of the values provided (absolute, basis point, percentage). Required. Known values
     are: \"Absolute\", \"BasisPoint\", and \"Percentage\"."""
    points: List["_models.CurveDataPoint"] = rest_field()
    """The list of dates and values. Required."""
    index_reference: str = rest_field(name="indexReference")
    """The reference to the floating rate index. Required."""

    @overload
    def __init__(
        self,
        *,
        zc_type: Union[str, "_models.ZcTypeEnum"],
        zc_unit: Union[str, "_models.UnitEnum"],
        points: List["_models.CurveDataPoint"],
        index_reference: str,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class IrZcCurvePoint(_model_base.Model):
    """An object that contains the values applied to the interest rate curve point.

    Attributes
    ----------
    start_date : ~datetime.date
        The start date of the curve point tenor. The value is expressed in ISO
        8601 format: YYYY-MM-DD (e.g., '2023-01-01'). Required.
    tenor : str
        The code indicating the period between the start date and the end date
        of the curve point (e.g., '1M', 1Y'). Required.
    end_date : ~datetime.date
        The end date of the curve point tenor. The value is expressed in ISO
        8601 format: YYYY-MM-DD (e.g., '2023-01-01'). Required.
    rate : ~analyticsapi.models.Rate
        The zero coupon rate. Required.
    discount_factor : ~analyticsapi.models.Rate
        The discount factor calculated for a given curve point. Required.
    instruments : list[~analyticsapi.models.CurvePointRelatedInstruments]
        An array of objects that contains instruments used to calculate the
        curve point.  The default value is None, needs to be assigned before
        using.
    """

    start_date: datetime.date = rest_field(name="startDate")
    """The start date of the curve point tenor. The value is expressed in ISO 8601 format: YYYY-MM-DD
     (e.g., '2023-01-01'). Required."""
    tenor: str = rest_field()
    """The code indicating the period between the start date and the end date of the curve point
     (e.g., '1M', 1Y'). Required."""
    end_date: datetime.date = rest_field(name="endDate")
    """The end date of the curve point tenor. The value is expressed in ISO 8601 format: YYYY-MM-DD
     (e.g., '2023-01-01'). Required."""
    rate: "_models.Rate" = rest_field()
    """The zero coupon rate. Required."""
    discount_factor: "_models.Rate" = rest_field(name="discountFactor")
    """The discount factor calculated for a given curve point. Required."""
    instruments: Optional[List["_models.CurvePointRelatedInstruments"]] = rest_field()
    """An array of objects that contains instruments used to calculate the curve point."""

    @overload
    def __init__(
        self,
        *,
        start_date: datetime.date,
        tenor: str,
        end_date: datetime.date,
        rate: "_models.Rate",
        discount_factor: "_models.Rate",
        instruments: Optional[List["_models.CurvePointRelatedInstruments"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class JobCreationRequest(_model_base.Model):
    """JobCreationRequest.

    Attributes
    ----------
    priority : int
        Control priority of job. Requests within jobs of higher priority are
        processed prior to jobs with lower priority.
    hold : bool
        When set to true, suspends the excution of all requests in the job,
        processing resumes only after the job is updated and the value is set
        to false.
    start_after : ~datetime.datetime
    stop_after : ~datetime.datetime
    name : str
        Optional. Unique name associated with a job. There can only be one
        active job with this name. Job name can be used for all future job
        references. If a previously open job exists with the same name, the
        older job is closed before a new job is created.
    asof : ~datetime.date
    order : str
        Is one of the following types: Literal["FAST"], Literal["FIFO"],
        Literal["NONE"]
    chain : str
    desc : str
        User defined description of the job.
    """

    priority: Optional[int] = rest_field()
    """Control priority of job. Requests within jobs of higher priority are processed prior to jobs
     with lower priority."""
    hold: Optional[bool] = rest_field()
    """When set to true, suspends the excution of all requests in the job, processing resumes only
     after the job is updated and the value is set to false."""
    start_after: Optional[datetime.datetime] = rest_field(name="startAfter", format="rfc3339")
    stop_after: Optional[datetime.datetime] = rest_field(name="stopAfter", format="rfc3339")
    name: Optional[str] = rest_field()
    """Optional. Unique name associated with a job. There can only be one active job with this name.
     Job name can be used for all future job references. If a previously open job exists with the
     same name, the older job is closed before a new job is created."""
    asof: Optional[datetime.date] = rest_field()
    order: Optional[Literal["FAST", "FIFO", "NONE"]] = rest_field()
    """Is one of the following types: Literal[\"FAST\"], Literal[\"FIFO\"], Literal[\"NONE\"]"""
    chain: Optional[str] = rest_field()
    desc: Optional[str] = rest_field()
    """User defined description of the job."""

    @overload
    def __init__(
        self,
        *,
        priority: Optional[int] = None,
        hold: Optional[bool] = None,
        start_after: Optional[datetime.datetime] = None,
        stop_after: Optional[datetime.datetime] = None,
        name: Optional[str] = None,
        asof: Optional[datetime.date] = None,
        order: Optional[Literal["FAST", "FIFO", "NONE"]] = None,
        chain: Optional[str] = None,
        desc: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class JobResponse(_model_base.Model):  # pylint: disable=too-many-instance-attributes
    """JobResponse.

    Attributes
    ----------
    id : str
        Required.
    sequence : int
    as_of : ~datetime.date
    closed : bool
    on_hold : bool
    aborted : bool
    exit_status : str
        Is one of the following types: Literal["DONE"], Literal["ERROR"],
        Literal["NEVER_STARTED"], Literal["ABORTED"], Literal["TIMEOUT"],
        Literal["ABANDONED"]
    actual_hold : bool
    name : str
    chain : str
    description : str
    priority : int
    order : str
        Is one of the following types: Literal["FAST"], Literal["FIFO"],
        Literal["NONE"]
    request_count : int
    pending_count : int
    running_count : int
    ok_count : int
    error_count : int
    aborted_count : int
    skip_count : int
    start_after : ~datetime.datetime
    stop_after : ~datetime.datetime
    created_at : ~datetime.datetime
    updated_at : ~datetime.datetime
    timeline : list[~analyticsapi.models.JobTimelineEntry]
        The default value is None, needs to be assigned before using.
    """

    id: str = rest_field()
    """Required."""
    sequence: Optional[int] = rest_field()
    as_of: Optional[datetime.date] = rest_field(name="asOf")
    closed: Optional[bool] = rest_field()
    on_hold: Optional[bool] = rest_field(name="onHold")
    aborted: Optional[bool] = rest_field()
    exit_status: Optional[Literal["DONE", "ERROR", "NEVER_STARTED", "ABORTED", "TIMEOUT", "ABANDONED"]] = rest_field(
        name="exitStatus"
    )
    """Is one of the following types: Literal[\"DONE\"], Literal[\"ERROR\"],
     Literal[\"NEVER_STARTED\"], Literal[\"ABORTED\"], Literal[\"TIMEOUT\"], Literal[\"ABANDONED\"]"""
    actual_hold: Optional[bool] = rest_field(name="actualHold")
    name: Optional[str] = rest_field()
    chain: Optional[str] = rest_field()
    description: Optional[str] = rest_field()
    priority: Optional[int] = rest_field()
    order: Optional[Literal["FAST", "FIFO", "NONE"]] = rest_field()
    """Is one of the following types: Literal[\"FAST\"], Literal[\"FIFO\"], Literal[\"NONE\"]"""
    request_count: Optional[int] = rest_field(name="requestCount")
    pending_count: Optional[int] = rest_field(name="pendingCount")
    running_count: Optional[int] = rest_field(name="runningCount")
    ok_count: Optional[int] = rest_field(name="okCount")
    error_count: Optional[int] = rest_field(name="errorCount")
    aborted_count: Optional[int] = rest_field(name="abortedCount")
    skip_count: Optional[int] = rest_field(name="skipCount")
    start_after: Optional[datetime.datetime] = rest_field(name="startAfter", format="rfc3339")
    stop_after: Optional[datetime.datetime] = rest_field(name="stopAfter", format="rfc3339")
    created_at: Optional[datetime.datetime] = rest_field(name="createdAt", format="rfc3339")
    updated_at: Optional[datetime.datetime] = rest_field(name="updatedAt", format="rfc3339")
    timeline: Optional[List["_models.JobTimelineEntry"]] = rest_field()

    @overload
    def __init__(
        self,
        *,
        id: str,  # pylint: disable=redefined-builtin
        sequence: Optional[int] = None,
        as_of: Optional[datetime.date] = None,
        closed: Optional[bool] = None,
        on_hold: Optional[bool] = None,
        aborted: Optional[bool] = None,
        exit_status: Optional[Literal["DONE", "ERROR", "NEVER_STARTED", "ABORTED", "TIMEOUT", "ABANDONED"]] = None,
        actual_hold: Optional[bool] = None,
        name: Optional[str] = None,
        chain: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[int] = None,
        order: Optional[Literal["FAST", "FIFO", "NONE"]] = None,
        request_count: Optional[int] = None,
        pending_count: Optional[int] = None,
        running_count: Optional[int] = None,
        ok_count: Optional[int] = None,
        error_count: Optional[int] = None,
        aborted_count: Optional[int] = None,
        skip_count: Optional[int] = None,
        start_after: Optional[datetime.datetime] = None,
        stop_after: Optional[datetime.datetime] = None,
        created_at: Optional[datetime.datetime] = None,
        updated_at: Optional[datetime.datetime] = None,
        timeline: Optional[List["_models.JobTimelineEntry"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class JobResubmissionRequest(_model_base.Model):
    """JobResubmissionRequest.

    Attributes
    ----------
    scope : str
        Is one of the following types: Literal["OK"], Literal["ERROR"],
        Literal["ABORTED"], Literal["FAILED"], Literal["ALL"]
    ids : list[str]
        The default value is None, needs to be assigned before using.
    """

    scope: Optional[Literal["OK", "ERROR", "ABORTED", "FAILED", "ALL"]] = rest_field()
    """Is one of the following types: Literal[\"OK\"], Literal[\"ERROR\"], Literal[\"ABORTED\"],
     Literal[\"FAILED\"], Literal[\"ALL\"]"""
    ids: Optional[List[str]] = rest_field()

    @overload
    def __init__(
        self,
        *,
        scope: Optional[Literal["OK", "ERROR", "ABORTED", "FAILED", "ALL"]] = None,
        ids: Optional[List[str]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class JobStatusResponse(_model_base.Model):  # pylint: disable=too-many-instance-attributes
    """JobStatusResponse.

    Attributes
    ----------
    id : str
    name : str
    job_status : str
        Is one of the following types: Literal["OPEN"], Literal["EMPTY"],
        Literal["HOLD"], Literal["CLOSED"], Literal["DONE"], Literal["ABORTED"]
    as_of : ~datetime.date
    start_time : ~datetime.datetime
    run_time : str
    pool_id : str
    priority : int
    can_manage : bool
    request_count : int
    pending_count : int
    running_count : int
    ok_count : int
    error_count : int
    aborted_count : int
    skipped_count : int
    """

    id: Optional[str] = rest_field()
    name: Optional[str] = rest_field()
    job_status: Optional[Literal["OPEN", "EMPTY", "HOLD", "CLOSED", "DONE", "ABORTED"]] = rest_field(name="jobStatus")
    """Is one of the following types: Literal[\"OPEN\"], Literal[\"EMPTY\"], Literal[\"HOLD\"],
     Literal[\"CLOSED\"], Literal[\"DONE\"], Literal[\"ABORTED\"]"""
    as_of: Optional[datetime.date] = rest_field(name="asOf")
    start_time: Optional[datetime.datetime] = rest_field(name="startTime", format="rfc3339")
    run_time: Optional[str] = rest_field(name="runTime")
    pool_id: Optional[str] = rest_field(name="poolId")
    priority: Optional[int] = rest_field()
    can_manage: Optional[bool] = rest_field(name="canManage")
    request_count: Optional[int] = rest_field(name="requestCount")
    pending_count: Optional[int] = rest_field(name="pendingCount")
    running_count: Optional[int] = rest_field(name="runningCount")
    ok_count: Optional[int] = rest_field(name="okCount")
    error_count: Optional[int] = rest_field(name="errorCount")
    aborted_count: Optional[int] = rest_field(name="abortedCount")
    skipped_count: Optional[int] = rest_field(name="skippedCount")

    @overload
    def __init__(
        self,
        *,
        id: Optional[str] = None,  # pylint: disable=redefined-builtin
        name: Optional[str] = None,
        job_status: Optional[Literal["OPEN", "EMPTY", "HOLD", "CLOSED", "DONE", "ABORTED"]] = None,
        as_of: Optional[datetime.date] = None,
        start_time: Optional[datetime.datetime] = None,
        run_time: Optional[str] = None,
        pool_id: Optional[str] = None,
        priority: Optional[int] = None,
        can_manage: Optional[bool] = None,
        request_count: Optional[int] = None,
        pending_count: Optional[int] = None,
        running_count: Optional[int] = None,
        ok_count: Optional[int] = None,
        error_count: Optional[int] = None,
        aborted_count: Optional[int] = None,
        skipped_count: Optional[int] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class JobTimelineEntry(_model_base.Model):
    """JobTimelineEntry.

    Attributes
    ----------
    ts : ~datetime.datetime
        Required.
    ok_count : int
        Required.
    error_count : int
        Required.
    interval : int
        Required.
    """

    ts: datetime.datetime = rest_field(format="rfc3339")
    """Required."""
    ok_count: int = rest_field(name="okCount")
    """Required."""
    error_count: int = rest_field(name="errorCount")
    """Required."""
    interval: int = rest_field()
    """Required."""

    @overload
    def __init__(
        self,
        *,
        ts: datetime.datetime,
        ok_count: int,
        error_count: int,
        interval: int,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class JsonRef(_model_base.Model):
    """Container for JSON formated references.

    Attributes
    ----------
    d_ref : str
    """

    d_ref: Optional[str] = rest_field(name="$ref")

    @overload
    def __init__(
        self,
        d_ref: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["d_ref"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class JsonScenRef(_model_base.Model):
    """JsonScenRef.

    Attributes
    ----------
    d_ref : str
        This can be a job store reference or system user scenario.

          System scenarios - Shorthand notation for scenarios that have simple shift. Scenarios can be
        defined using the below format

        *
          /sys/scenario/{ShiftType}/{Shift in bps}

          Example 1 - Parallel shift of 50 bps

        *
          /sys/scenario/Par/50

          Example 2 - Forward shift of -150 bps

        *
          /sys/scenario/Fwd/-150

          Valid values for Shift type are Par, Spot, Fwd, ImplFwd (short notation)

          If you would like to make changes to other scenario setup fields like timing etc, use the
        below

        *
          /sys/scenario/Fwd/50?timing=Immediate&reinvestmentRate=Default&swapSpreadConst=true.
    """

    d_ref: Optional[str] = rest_field(name="$ref")
    """This can be a job store reference or system user scenario.
     
       System scenarios - Shorthand notation for scenarios that have simple shift. Scenarios can be
     defined using the below format
     
     
     *
       /sys/scenario/{ShiftType}/{Shift in bps}
     
       Example 1 - Parallel shift of 50 bps
     
     *
       /sys/scenario/Par/50
     
       Example 2 - Forward shift of -150 bps
     
     *
       /sys/scenario/Fwd/-150
     
       Valid values for Shift type are Par, Spot, Fwd, ImplFwd (short notation)
     
       If you would like to make changes to other scenario setup fields like timing etc, use the
     below
     
     *
       /sys/scenario/Fwd/50?timing=Immediate&reinvestmentRate=Default&swapSpreadConst=true."""

    @overload
    def __init__(
        self,
        d_ref: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["d_ref"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class RescheduleDescription(ABC, _model_base.Model):
    """An object to determine a holiday rescheduling.

    You probably want to use the sub-classes and not this class directly. Known sub-classes are:
    LagDaysRescheduleDescription, RelativeRescheduleDescription

    Attributes
    ----------
    reschedule_type : str or ~analyticsapi.models.RescheduleType
        The type of rescheduling for the observation period. Required. Known
        values are: "LagDaysRescheduleDescription" and
        "RelativeRescheduleDescription".
    """

    __mapping__: Dict[str, _model_base.Model] = {}
    reschedule_type: str = rest_discriminator(name="rescheduleType")
    """The type of rescheduling for the observation period. Required. Known values are:
     \"LagDaysRescheduleDescription\" and \"RelativeRescheduleDescription\"."""

    @overload
    def __init__(
        self,
        reschedule_type: str,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["reschedule_type"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class LagDaysRescheduleDescription(RescheduleDescription, discriminator="LagDaysRescheduleDescription"):
    """An object to determine the rule for rescheduling a holiday using day lags.

    Attributes
    ----------
    reschedule_type : str or ~analyticsapi.models.LAG_DAYS_RESCHEDULE_DESCRIPTION
        The type of rescheduling for the observation period. Only
        LagDaysRescheduleDescription value applies. Required. The rule for
        rescheduling a holiday using day lags. For example, if a holiday falls
        on Sunday, it is rescheduled by the number of days defined by the lag.
    lag_days : int
        The length of the lag in days. The holiday will be rescheduled to a
        date this many days in the future. Value can be negative. Required.
    """

    reschedule_type: Literal[RescheduleType.LAG_DAYS_RESCHEDULE_DESCRIPTION] = rest_discriminator(name="rescheduleType")  # type: ignore
    """The type of rescheduling for the observation period. Only LagDaysRescheduleDescription value
     applies. Required. The rule for rescheduling a holiday using day lags. For example, if a
     holiday falls on Sunday, it is rescheduled by the number of days defined by the lag."""
    lag_days: int = rest_field(name="lagDays")
    """The length of the lag in days. The holiday will be rescheduled to a date this many days in the
     future. Value can be negative. Required."""

    @overload
    def __init__(
        self,
        lag_days: int,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, reschedule_type=RescheduleType.LAG_DAYS_RESCHEDULE_DESCRIPTION, **kwargs)


class Link(_model_base.Model):
    """An object representing a hyperlink to a related resource, including its URL, optional schema,
    and HTTP method.

    Attributes
    ----------
    href : str
        The URL reference to the related resource. Required.
    href_schema : str
        The URL to the schema definition for the referenced resource.
    http_method : str
        The HTTP method (e.g., GET, POST) to be used when accessing the
        referenced resource.
    """

    href: str = rest_field()
    """The URL reference to the related resource. Required."""
    href_schema: Optional[str] = rest_field(name="hrefSchema")
    """The URL to the schema definition for the referenced resource."""
    http_method: Optional[str] = rest_field(name="httpMethod")
    """The HTTP method (e.g., GET, POST) to be used when accessing the referenced resource."""

    @overload
    def __init__(
        self,
        *,
        href: str,
        href_schema: Optional[str] = None,
        http_method: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class Location(_model_base.Model):
    """An object identifying a resource by a combination of its name and the space where it's saved on
    the platform.

    Attributes
    ----------
    space : str
        The space in which the resource is saved.
    name : str
        The name of the resource. Required.
    """

    space: Optional[str] = rest_field()
    """The space in which the resource is saved."""
    name: str = rest_field()
    """The name of the resource. Required."""

    @overload
    def __init__(
        self,
        *,
        name: str,
        space: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class LookbackSettings(_model_base.Model):
    """LookbackSettings.

    Attributes
    ----------
    basis_lookback_days : int
    curve_lookback_days : int
    volatility_lookback_days : int
    ccoas_lookback_days : int
    mortgage_date_lookback_days : int
    curve_date_shift_lookback_days : int
    curve_date_roll_lookback : bool
    """

    basis_lookback_days: Optional[int] = rest_field(name="basisLookbackDays")
    curve_lookback_days: Optional[int] = rest_field(name="curveLookbackDays")
    volatility_lookback_days: Optional[int] = rest_field(name="volatilityLookbackDays")
    ccoas_lookback_days: Optional[int] = rest_field(name="ccoasLookbackDays")
    mortgage_date_lookback_days: Optional[int] = rest_field(name="mortgageDateLookbackDays")
    curve_date_shift_lookback_days: Optional[int] = rest_field(name="curveDateShiftLookbackDays")
    curve_date_roll_lookback: Optional[bool] = rest_field(name="curveDateRollLookback")

    @overload
    def __init__(
        self,
        *,
        basis_lookback_days: Optional[int] = None,
        curve_lookback_days: Optional[int] = None,
        volatility_lookback_days: Optional[int] = None,
        ccoas_lookback_days: Optional[int] = None,
        mortgage_date_lookback_days: Optional[int] = None,
        curve_date_shift_lookback_days: Optional[int] = None,
        curve_date_roll_lookback: Optional[bool] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class LookupDetails(_model_base.Model):
    """LookupDetails.

    All required parameters must be populated in order to send to server.

    Attributes
    ----------
    table : str
        Required.
    show : str
    default : any
    default_value : any
    """

    table: str = rest_field()
    """Required."""
    show: Optional[str] = rest_field()
    default: Optional[Any] = rest_field()
    default_value: Optional[Any] = rest_field(name="defaultValue")

    @overload
    def __init__(
        self,
        *,
        table: str,
        show: Optional[str] = None,
        default: Optional[Any] = None,
        default_value: Optional[Any] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class LossSettings(_model_base.Model):  # pylint: disable=too-many-instance-attributes
    """Only used for securities that are modeled with losses.

    Attributes
    ----------
    default_type : str
        Required. Loss determination type. Is one of the following types:
        Literal["SDA"], Literal["CDR"], Literal["MODEL"]
    default_rate : float
        Number that specifies the default rate. Either defaultRate or default
        Vector is required.
    default_vector : ~analyticsapi.models.Vector
    severity_type : str
        Default loss severity type selection. Is either a Literal["PERCENT"]
        type or a Literal["MODEL"] type.
    severity_rate : float
        If severity type is set to percent, this is the severity percentage. If
        set to model, this is loss model speed. Baseline speed is 100. Either
        severityRate or severityVector is required.
    severity_vector : ~analyticsapi.models.Vector
    recovery_lag : int
        Required if severityType = PERCENT. The expected number of months from
        the time of date of an assumed default until the receipt of the assumed
        recovery on defaulted assets.
    delinquency_type : str
        Is one of the following types: Literal["PERCENT"], Literal["PASS"],
        Literal["FAIL"], Literal["MODEL"]
    delinquency_rate : float
        If delinquency type is PERCENT, this is the delinquency percentage. If
        type is MODEL, this is the model speed. Baseline model speed is 100.
        Either delinquencyRate or delinquencyVector is required.
    delinquency_vector : ~analyticsapi.models.Vector
        A month/rate vector that specifies delinquency amount. Either
        delinquencyRate or delinquencyVector is required.
    use_model_loan_modifications : bool
        Optional. Choose whether or not to use loan modifications that are
        assumed/projected by the our proprietary, internal models.
    ignore_insurance : bool
        Optional. Choose whether or not to incorporate mortgage insurance into
        loss projections.
    """

    default_type: Optional[Literal["SDA", "CDR", "MODEL"]] = rest_field(name="defaultType")
    """Required. Loss determination type. Is one of the following types: Literal[\"SDA\"],
     Literal[\"CDR\"], Literal[\"MODEL\"]"""
    default_rate: Optional[float] = rest_field(name="defaultRate")
    """Number that specifies the default rate. Either defaultRate or default Vector is required."""
    default_vector: Optional["_models.Vector"] = rest_field(name="defaultVector")
    severity_type: Optional[Literal["PERCENT", "MODEL"]] = rest_field(name="severityType")
    """Default loss severity type selection. Is either a Literal[\"PERCENT\"] type or a
     Literal[\"MODEL\"] type."""
    severity_rate: Optional[float] = rest_field(name="severityRate")
    """If severity type is set to percent, this is the severity percentage. If set to model, this is
     loss model speed. Baseline speed is 100. Either severityRate or severityVector is required."""
    severity_vector: Optional["_models.Vector"] = rest_field(name="severityVector")
    recovery_lag: Optional[int] = rest_field(name="recoveryLag")
    """Required if severityType = PERCENT. The expected number of months from the time of date of an
     assumed default until the receipt of the assumed recovery on defaulted assets."""
    delinquency_type: Optional[Literal["PERCENT", "PASS", "FAIL", "MODEL"]] = rest_field(name="delinquencyType")
    """Is one of the following types: Literal[\"PERCENT\"], Literal[\"PASS\"], Literal[\"FAIL\"],
     Literal[\"MODEL\"]"""
    delinquency_rate: Optional[float] = rest_field(name="delinquencyRate")
    """If delinquency type is PERCENT, this is the delinquency percentage. If type is MODEL, this is
     the model speed. Baseline model speed is 100. Either delinquencyRate or delinquencyVector is
     required."""
    delinquency_vector: Optional["_models.Vector"] = rest_field(name="delinquencyVector")
    """A month/rate vector that specifies delinquency amount. Either delinquencyRate or
     delinquencyVector is required."""
    use_model_loan_modifications: Optional[bool] = rest_field(name="useModelLoanModifications")
    """Optional. Choose whether or not to use loan modifications that are assumed/projected by the our
     proprietary, internal models."""
    ignore_insurance: Optional[bool] = rest_field(name="ignoreInsurance")
    """Optional. Choose whether or not to incorporate mortgage insurance into loss projections."""

    @overload
    def __init__(
        self,
        *,
        default_type: Optional[Literal["SDA", "CDR", "MODEL"]] = None,
        default_rate: Optional[float] = None,
        default_vector: Optional["_models.Vector"] = None,
        severity_type: Optional[Literal["PERCENT", "MODEL"]] = None,
        severity_rate: Optional[float] = None,
        severity_vector: Optional["_models.Vector"] = None,
        recovery_lag: Optional[int] = None,
        delinquency_type: Optional[Literal["PERCENT", "PASS", "FAIL", "MODEL"]] = None,
        delinquency_rate: Optional[float] = None,
        delinquency_vector: Optional["_models.Vector"] = None,
        use_model_loan_modifications: Optional[bool] = None,
        ignore_insurance: Optional[bool] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class MappedResponseRefData(_model_base.Model):
    """Bond indicative response data from the server. It returns a generic container of data contaning
    a combined dataset of all available instrument types, with only dedicated data filled out. For
    more information check 'Results' model documentation.

    Attributes
    ----------
    meta : ~analyticsapi.models.RefDataMeta
        Required.
    results : list[~analyticsapi.models.Results]
        Required.  The default value is None, needs to be assigned before
        using.
    """

    meta: "_models.RefDataMeta" = rest_field()
    """Required."""
    results: List["_models.Results"] = rest_field()
    """Required."""

    @overload
    def __init__(
        self,
        *,
        meta: "_models.RefDataMeta",
        results: List["_models.Results"],
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class MarketData(_model_base.Model):
    """model describing the data that may be provided to control the market data, curves, surfaces to
    be used in analytic computations.

    Attributes
    ----------
    fx_forward_curves : list[~analyticsapi.models.FxForwardCurveChoice]
        The list of fx forward curves per currency. This is used to generate fx
        forward rates.  The default value is None, needs to be assigned before
        using.
    ir_curves : list[~analyticsapi.models.IrCurveChoice]
        The list of interest rate curves per interest reference index. This is
        used to generate forward interest rates.  The default value is None,
        needs to be assigned before using.
    discount_curves : list[~analyticsapi.models.IrCurveChoice]
        The list of discount curves per currency. This is used to generate
        discount factors.  The default value is None, needs to be assigned
        before using.
    credit_curves : list[~analyticsapi.models.CreditCurveChoice]
        The list of risky curves per reference entity. This is used to generate
        risky interest rate or discount factors.  The default value is None,
        needs to be assigned before using.
    eq_option_vol_surface : list[~analyticsapi.models.EqOptionVolSurfaceChoice]
        The list of volatility surfaces per reference entity. This is used to
        generate equity option volatilities.  The default value is None, needs
        to be assigned before using.
    fx_option_vol_surface : list[~analyticsapi.models.FxOptionVolSurfaceChoice]
        The list of volatility surfaces per currency pair. This is used to
        generate fx option volatilities.  The default value is None, needs to
        be assigned before using.
    cmdty_option_vol_surface : list[~analyticsapi.models.CmdtyOptionVolSurfaceChoice]
        The list of volatility surfaces per commodity contract. This is used to
        generate commodity option volatilities.  The default value is None,
        needs to be assigned before using.
    ir_cap_vol_surface : list[~analyticsapi.models.IrCapVolSurfaceChoice]
        The list of volatility surfaces per interest reference index. This is
        used to generate cap or floor volatilities.  The default value is None,
        needs to be assigned before using.
    ir_swaption_vol_cube : list[~analyticsapi.models.IrSwaptionVolCubeChoice]
        The list of volatility cubes per interest reference index. This is used
        to generate swaption volatilities.  The default value is None, needs to
        be assigned before using.
    """

    fx_forward_curves: Optional[List["_models.FxForwardCurveChoice"]] = rest_field(name="fxForwardCurves")
    """The list of fx forward curves per currency. This is used to generate fx forward rates."""
    ir_curves: Optional[List["_models.IrCurveChoice"]] = rest_field(name="irCurves")
    """The list of interest rate curves per interest reference index. This is used to generate forward
     interest rates."""
    discount_curves: Optional[List["_models.IrCurveChoice"]] = rest_field(name="discountCurves")
    """The list of discount curves per currency. This is used to generate discount factors."""
    credit_curves: Optional[List["_models.CreditCurveChoice"]] = rest_field(name="creditCurves")
    """The list of risky curves per reference entity. This is used to generate risky interest rate or
     discount factors."""
    eq_option_vol_surface: Optional[List["_models.EqOptionVolSurfaceChoice"]] = rest_field(name="eqOptionVolSurface")
    """The list of volatility surfaces per reference entity. This is used to generate equity option
     volatilities."""
    fx_option_vol_surface: Optional[List["_models.FxOptionVolSurfaceChoice"]] = rest_field(name="fxOptionVolSurface")
    """The list of volatility surfaces per currency pair. This is used to generate fx option
     volatilities."""
    cmdty_option_vol_surface: Optional[List["_models.CmdtyOptionVolSurfaceChoice"]] = rest_field(
        name="cmdtyOptionVolSurface"
    )
    """The list of volatility surfaces per commodity contract. This is used to generate commodity
     option volatilities."""
    ir_cap_vol_surface: Optional[List["_models.IrCapVolSurfaceChoice"]] = rest_field(name="irCapVolSurface")
    """The list of volatility surfaces per interest reference index. This is used to generate cap or
     floor volatilities."""
    ir_swaption_vol_cube: Optional[List["_models.IrSwaptionVolCubeChoice"]] = rest_field(name="irSwaptionVolCube")
    """The list of volatility cubes per interest reference index. This is used to generate swaption
     volatilities."""

    @overload
    def __init__(
        self,
        *,
        fx_forward_curves: Optional[List["_models.FxForwardCurveChoice"]] = None,
        ir_curves: Optional[List["_models.IrCurveChoice"]] = None,
        discount_curves: Optional[List["_models.IrCurveChoice"]] = None,
        credit_curves: Optional[List["_models.CreditCurveChoice"]] = None,
        eq_option_vol_surface: Optional[List["_models.EqOptionVolSurfaceChoice"]] = None,
        fx_option_vol_surface: Optional[List["_models.FxOptionVolSurfaceChoice"]] = None,
        cmdty_option_vol_surface: Optional[List["_models.CmdtyOptionVolSurfaceChoice"]] = None,
        ir_cap_vol_surface: Optional[List["_models.IrCapVolSurfaceChoice"]] = None,
        ir_swaption_vol_cube: Optional[List["_models.IrSwaptionVolCubeChoice"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class MbsSettings(_model_base.Model):
    """Additional settings for mortgage backed securities.

    Attributes
    ----------
    use_roll_info : bool
        Optional, for adjustable rate mortgages (ARMS). If the ARM has roll
        Information, one can choose to assume the ARM has one reset date or use
        the Roll Information. Note, OAS will not calculate if roll information
        is used.
    call_underlying_remics : bool
        Optional, used for re-remic securities. Treats the underlying
        collateral remics as callable.
    """

    use_roll_info: Optional[bool] = rest_field(name="useRollInfo")
    """Optional, for adjustable rate mortgages (ARMS). If the ARM has roll Information, one can choose
     to assume the ARM has one reset date or use the Roll Information. Note, OAS will not calculate
     if roll information is used."""
    call_underlying_remics: Optional[bool] = rest_field(name="callUnderlyingRemics")
    """Optional, used for re-remic securities. Treats the underlying collateral remics as callable."""

    @overload
    def __init__(
        self,
        *,
        use_roll_info: Optional[bool] = None,
        call_underlying_remics: Optional[bool] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class MetaData(_model_base.Model):
    """The metadata of the resource.

    Attributes
    ----------
    created_at : ~datetime.datetime
        The date and time when the resource was created.

        The value is expressed in ISO 8601 format: YYYY-MM-DDT[hh]:[mm]:[ss]Z (e.g.,
        2023-01-01T00:00:00Z).
    status : str or ~analyticsapi.models.Status
        The status of the resource. Known values are: "Active" and "Deleted".
    revision : str
        The version of the resource.
    creator : str
        The uuid of the user who created the resource.
    updated_at : ~datetime.datetime
        The date and time when the resource was updated.

        The value is expressed in ISO 8601 format: YYYY-MM-DDT[hh]:[mm]:[ss]Z (e.g.,
        2023-01-01T00:00:00Z).
    deleted_at : ~datetime.datetime
        The date and time when the resource was deleted.

        The value is expressed in ISO 8601 format: YYYY-MM-DDT[hh]:[mm]:[ss]Z (e.g.,
        2023-01-01T00:00:00Z).
    updated_by : str
        The name of the user who updated the resource.
    """

    created_at: Optional[datetime.datetime] = rest_field(name="createdAt", format="rfc3339")
    """The date and time when the resource was created.
     
     The value is expressed in ISO 8601 format: YYYY-MM-DDT[hh]:[mm]:[ss]Z (e.g.,
     2023-01-01T00:00:00Z)."""
    status: Optional[Union[str, "_models.Status"]] = rest_field()
    """The status of the resource. Known values are: \"Active\" and \"Deleted\"."""
    revision: Optional[str] = rest_field()
    """The version of the resource."""
    creator: Optional[str] = rest_field()
    """The uuid of the user who created the resource."""
    updated_at: Optional[datetime.datetime] = rest_field(name="updatedAt", format="rfc3339")
    """The date and time when the resource was updated.
     
     The value is expressed in ISO 8601 format: YYYY-MM-DDT[hh]:[mm]:[ss]Z (e.g.,
     2023-01-01T00:00:00Z)."""
    deleted_at: Optional[datetime.datetime] = rest_field(name="deletedAt", format="rfc3339")
    """The date and time when the resource was deleted.
     
     The value is expressed in ISO 8601 format: YYYY-MM-DDT[hh]:[mm]:[ss]Z (e.g.,
     2023-01-01T00:00:00Z)."""
    updated_by: Optional[str] = rest_field(name="updatedBy")
    """The name of the user who updated the resource."""

    @overload
    def __init__(
        self,
        *,
        created_at: Optional[datetime.datetime] = None,
        status: Optional[Union[str, "_models.Status"]] = None,
        revision: Optional[str] = None,
        creator: Optional[str] = None,
        updated_at: Optional[datetime.datetime] = None,
        deleted_at: Optional[datetime.datetime] = None,
        updated_by: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ModifyClass(_model_base.Model):  # pylint: disable=too-many-instance-attributes
    """ModifyClass.

    Attributes
    ----------
    current_coupon : ~decimal.Decimal
    notional_flag : bool
    modify_interest_flag : bool
    index : str
    leverage : ~decimal.Decimal
    reset_margin : ~decimal.Decimal
    life_cap : ~decimal.Decimal
    life_floor : ~decimal.Decimal
    payment_delay : int
    class_amount : ~decimal.Decimal
    ignore_amount : ~decimal.Decimal
    modify_class_calc_type : str
    payment_day_of_month : int
    """

    current_coupon: Optional[decimal.Decimal] = rest_field(name="currentCoupon")
    notional_flag: Optional[bool] = rest_field(name="notionalFlag")
    modify_interest_flag: Optional[bool] = rest_field(name="modifyInterestFlag")
    index: Optional[str] = rest_field()
    leverage: Optional[decimal.Decimal] = rest_field()
    reset_margin: Optional[decimal.Decimal] = rest_field(name="resetMargin")
    life_cap: Optional[decimal.Decimal] = rest_field(name="lifeCap")
    life_floor: Optional[decimal.Decimal] = rest_field(name="lifeFloor")
    payment_delay: Optional[int] = rest_field(name="paymentDelay")
    class_amount: Optional[decimal.Decimal] = rest_field(name="classAmount")
    ignore_amount: Optional[decimal.Decimal] = rest_field(name="ignoreAmount")
    modify_class_calc_type: Optional[str] = rest_field(name="modifyClassCalcType")
    payment_day_of_month: Optional[int] = rest_field(name="paymentDayOfMonth")

    @overload
    def __init__(
        self,
        *,
        current_coupon: Optional[decimal.Decimal] = None,
        notional_flag: Optional[bool] = None,
        modify_interest_flag: Optional[bool] = None,
        index: Optional[str] = None,
        leverage: Optional[decimal.Decimal] = None,
        reset_margin: Optional[decimal.Decimal] = None,
        life_cap: Optional[decimal.Decimal] = None,
        life_floor: Optional[decimal.Decimal] = None,
        payment_delay: Optional[int] = None,
        class_amount: Optional[decimal.Decimal] = None,
        ignore_amount: Optional[decimal.Decimal] = None,
        modify_class_calc_type: Optional[str] = None,
        payment_day_of_month: Optional[int] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ModifyCollateral(_model_base.Model):  # pylint: disable=too-many-instance-attributes
    """ModifyCollateral.

    Attributes
    ----------
    collateral_net_coupon : ~decimal.Decimal
    gross_wac : ~decimal.Decimal
    loan_age : int
    current3_rd_party_origination : ~decimal.Decimal
    spread_at_origination : ~decimal.Decimal
    current_ltv : ~decimal.Decimal
    ltv : ~decimal.Decimal
    post_modification_ltv : ~decimal.Decimal
    credit_score : int
    post_modification_credit_score : ~decimal.Decimal
    percent_refi : ~decimal.Decimal
    percent_prev_loss_mitigation : ~decimal.Decimal
    percent2_to4_unit : ~decimal.Decimal
    percent_inv : ~decimal.Decimal
    percent_harp : ~decimal.Decimal
    percent_harp2 : ~decimal.Decimal
    percent_dti : ~decimal.Decimal
    combined_ltv : ~decimal.Decimal
    percent_reperformer : ~decimal.Decimal
    reperformer_months : int
    clean_pay_months : int
    percent_payment_reduction : ~decimal.Decimal
    forbearance_amount : ~decimal.Decimal
    forbearance_modification : ~decimal.Decimal
    percent_first_time_home_buyer : ~decimal.Decimal
    new_original_loan_size : ~decimal.Decimal
    new_current_loan_size : ~decimal.Decimal
    origination_channel : ~analyticsapi.models.OriginChannel
    percent_fha : ~decimal.Decimal
    percent_va : ~decimal.Decimal
    percent_rh : ~decimal.Decimal
    percent_pih : ~decimal.Decimal
    percent_retail : ~decimal.Decimal
    percent_unspecified : ~decimal.Decimal
    adjusted_spread_at_origination : ~decimal.Decimal
    adjusted_ltv : ~decimal.Decimal
    adjusted_original_loan_size : ~decimal.Decimal
    adjusted_current_loan_size : ~decimal.Decimal
    weighted_avg_loan_size : ~decimal.Decimal
    original_weighted_avg_loan_size : ~decimal.Decimal
    second_lien_frac : ~decimal.Decimal
    occupancy_second_home : ~decimal.Decimal
    permanent_jumbo_frac : ~decimal.Decimal
    units_multi : ~decimal.Decimal
    loan_purpose_cashout : ~decimal.Decimal
    percent_piw_appraisal : ~decimal.Decimal
    percent_piw_onsite_avm : ~decimal.Decimal
    percent_piwgse_refinance : ~decimal.Decimal
    percent_piw_waiver : ~decimal.Decimal
    percent_home_ready_home_possible : ~decimal.Decimal
    percent_state_hfa : ~decimal.Decimal
    percent_hamp_mods : ~decimal.Decimal
    percent_regular_mods : ~decimal.Decimal
    modify_collateral_type : str
    prepay_model_servicer : list[~analyticsapi.models.PrepayModelServicer]
        The default value is None, needs to be assigned before using.
    prepay_model_seller : list[~analyticsapi.models.PrepayModelSeller]
        The default value is None, needs to be assigned before using.
    """

    collateral_net_coupon: Optional[decimal.Decimal] = rest_field(name="collateralNetCoupon")
    gross_wac: Optional[decimal.Decimal] = rest_field(name="grossWAC")
    loan_age: Optional[int] = rest_field(name="loanAge")
    current3_rd_party_origination: Optional[decimal.Decimal] = rest_field(name="current3RdPartyOrigination")
    spread_at_origination: Optional[decimal.Decimal] = rest_field(name="spreadAtOrigination")
    current_ltv: Optional[decimal.Decimal] = rest_field(name="currentLTV")
    ltv: Optional[decimal.Decimal] = rest_field()
    post_modification_ltv: Optional[decimal.Decimal] = rest_field(name="postModificationLTV")
    credit_score: Optional[int] = rest_field(name="creditScore")
    post_modification_credit_score: Optional[decimal.Decimal] = rest_field(name="postModificationCreditScore")
    percent_refi: Optional[decimal.Decimal] = rest_field(name="percentRefi")
    percent_prev_loss_mitigation: Optional[decimal.Decimal] = rest_field(name="percentPrevLossMitigation")
    percent2_to4_unit: Optional[decimal.Decimal] = rest_field(name="percent2To4Unit")
    percent_inv: Optional[decimal.Decimal] = rest_field(name="percentInv")
    percent_harp: Optional[decimal.Decimal] = rest_field(name="percentHARP")
    percent_harp2: Optional[decimal.Decimal] = rest_field(name="percentHARP2")
    percent_dti: Optional[decimal.Decimal] = rest_field(name="percentDTI")
    combined_ltv: Optional[decimal.Decimal] = rest_field(name="combinedLTV")
    percent_reperformer: Optional[decimal.Decimal] = rest_field(name="percentReperformer")
    reperformer_months: Optional[int] = rest_field(name="reperformerMonths")
    clean_pay_months: Optional[int] = rest_field(name="cleanPayMonths")
    percent_payment_reduction: Optional[decimal.Decimal] = rest_field(name="percentPaymentReduction")
    forbearance_amount: Optional[decimal.Decimal] = rest_field(name="forbearanceAmount")
    forbearance_modification: Optional[decimal.Decimal] = rest_field(name="forbearanceModification")
    percent_first_time_home_buyer: Optional[decimal.Decimal] = rest_field(name="percentFirstTimeHomeBuyer")
    new_original_loan_size: Optional[decimal.Decimal] = rest_field(name="newOriginalLoanSize")
    new_current_loan_size: Optional[decimal.Decimal] = rest_field(name="newCurrentLoanSize")
    origination_channel: Optional["_models.OriginChannel"] = rest_field(name="originationChannel")
    percent_fha: Optional[decimal.Decimal] = rest_field(name="percentFHA")
    percent_va: Optional[decimal.Decimal] = rest_field(name="percentVA")
    percent_rh: Optional[decimal.Decimal] = rest_field(name="percentRH")
    percent_pih: Optional[decimal.Decimal] = rest_field(name="percentPIH")
    percent_retail: Optional[decimal.Decimal] = rest_field(name="percentRetail")
    percent_unspecified: Optional[decimal.Decimal] = rest_field(name="percentUnspecified")
    adjusted_spread_at_origination: Optional[decimal.Decimal] = rest_field(name="adjustedSpreadAtOrigination")
    adjusted_ltv: Optional[decimal.Decimal] = rest_field(name="adjustedLTV")
    adjusted_original_loan_size: Optional[decimal.Decimal] = rest_field(name="adjustedOriginalLoanSize")
    adjusted_current_loan_size: Optional[decimal.Decimal] = rest_field(name="adjustedCurrentLoanSize")
    weighted_avg_loan_size: Optional[decimal.Decimal] = rest_field(name="weightedAvgLoanSize")
    original_weighted_avg_loan_size: Optional[decimal.Decimal] = rest_field(name="originalWeightedAvgLoanSize")
    second_lien_frac: Optional[decimal.Decimal] = rest_field(name="secondLienFrac")
    occupancy_second_home: Optional[decimal.Decimal] = rest_field(name="occupancySecondHome")
    permanent_jumbo_frac: Optional[decimal.Decimal] = rest_field(name="permanentJumboFrac")
    units_multi: Optional[decimal.Decimal] = rest_field(name="unitsMulti")
    loan_purpose_cashout: Optional[decimal.Decimal] = rest_field(name="loanPurposeCashout")
    percent_piw_appraisal: Optional[decimal.Decimal] = rest_field(name="percentPIWAppraisal")
    percent_piw_onsite_avm: Optional[decimal.Decimal] = rest_field(name="percentPIWOnsiteAVM")
    percent_piwgse_refinance: Optional[decimal.Decimal] = rest_field(name="percentPIWGSERefinance")
    percent_piw_waiver: Optional[decimal.Decimal] = rest_field(name="percentPIWWaiver")
    percent_home_ready_home_possible: Optional[decimal.Decimal] = rest_field(name="percentHomeReadyHomePossible")
    percent_state_hfa: Optional[decimal.Decimal] = rest_field(name="percentStateHFA")
    percent_hamp_mods: Optional[decimal.Decimal] = rest_field(name="percentHAMPMods")
    percent_regular_mods: Optional[decimal.Decimal] = rest_field(name="percentRegularMods")
    modify_collateral_type: Optional[str] = rest_field(name="modifyCollateralType")
    prepay_model_servicer: Optional[List["_models.PrepayModelServicer"]] = rest_field(name="prepayModelServicer")
    prepay_model_seller: Optional[List["_models.PrepayModelSeller"]] = rest_field(name="prepayModelSeller")

    @overload
    def __init__(
        self,
        *,
        collateral_net_coupon: Optional[decimal.Decimal] = None,
        gross_wac: Optional[decimal.Decimal] = None,
        loan_age: Optional[int] = None,
        current3_rd_party_origination: Optional[decimal.Decimal] = None,
        spread_at_origination: Optional[decimal.Decimal] = None,
        current_ltv: Optional[decimal.Decimal] = None,
        ltv: Optional[decimal.Decimal] = None,
        post_modification_ltv: Optional[decimal.Decimal] = None,
        credit_score: Optional[int] = None,
        post_modification_credit_score: Optional[decimal.Decimal] = None,
        percent_refi: Optional[decimal.Decimal] = None,
        percent_prev_loss_mitigation: Optional[decimal.Decimal] = None,
        percent2_to4_unit: Optional[decimal.Decimal] = None,
        percent_inv: Optional[decimal.Decimal] = None,
        percent_harp: Optional[decimal.Decimal] = None,
        percent_harp2: Optional[decimal.Decimal] = None,
        percent_dti: Optional[decimal.Decimal] = None,
        combined_ltv: Optional[decimal.Decimal] = None,
        percent_reperformer: Optional[decimal.Decimal] = None,
        reperformer_months: Optional[int] = None,
        clean_pay_months: Optional[int] = None,
        percent_payment_reduction: Optional[decimal.Decimal] = None,
        forbearance_amount: Optional[decimal.Decimal] = None,
        forbearance_modification: Optional[decimal.Decimal] = None,
        percent_first_time_home_buyer: Optional[decimal.Decimal] = None,
        new_original_loan_size: Optional[decimal.Decimal] = None,
        new_current_loan_size: Optional[decimal.Decimal] = None,
        origination_channel: Optional["_models.OriginChannel"] = None,
        percent_fha: Optional[decimal.Decimal] = None,
        percent_va: Optional[decimal.Decimal] = None,
        percent_rh: Optional[decimal.Decimal] = None,
        percent_pih: Optional[decimal.Decimal] = None,
        percent_retail: Optional[decimal.Decimal] = None,
        percent_unspecified: Optional[decimal.Decimal] = None,
        adjusted_spread_at_origination: Optional[decimal.Decimal] = None,
        adjusted_ltv: Optional[decimal.Decimal] = None,
        adjusted_original_loan_size: Optional[decimal.Decimal] = None,
        adjusted_current_loan_size: Optional[decimal.Decimal] = None,
        weighted_avg_loan_size: Optional[decimal.Decimal] = None,
        original_weighted_avg_loan_size: Optional[decimal.Decimal] = None,
        second_lien_frac: Optional[decimal.Decimal] = None,
        occupancy_second_home: Optional[decimal.Decimal] = None,
        permanent_jumbo_frac: Optional[decimal.Decimal] = None,
        units_multi: Optional[decimal.Decimal] = None,
        loan_purpose_cashout: Optional[decimal.Decimal] = None,
        percent_piw_appraisal: Optional[decimal.Decimal] = None,
        percent_piw_onsite_avm: Optional[decimal.Decimal] = None,
        percent_piwgse_refinance: Optional[decimal.Decimal] = None,
        percent_piw_waiver: Optional[decimal.Decimal] = None,
        percent_home_ready_home_possible: Optional[decimal.Decimal] = None,
        percent_state_hfa: Optional[decimal.Decimal] = None,
        percent_hamp_mods: Optional[decimal.Decimal] = None,
        percent_regular_mods: Optional[decimal.Decimal] = None,
        modify_collateral_type: Optional[str] = None,
        prepay_model_servicer: Optional[List["_models.PrepayModelServicer"]] = None,
        prepay_model_seller: Optional[List["_models.PrepayModelSeller"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class MonthRatePair(_model_base.Model):
    """MonthRatePair.

    Attributes
    ----------
    month : int
    rate : float
    """

    month: Optional[int] = rest_field()
    rate: Optional[float] = rest_field()

    @overload
    def __init__(
        self,
        *,
        month: Optional[int] = None,
        rate: Optional[float] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class MuniSettings(_model_base.Model):
    """Optional settings for municipal bonds.

    Attributes
    ----------
    paydown_optional : bool
        Optional, if true the bond's sink or paydown schedule is treated as
        optional.
    ignore_call_info : bool
        Optional, if true the bond's call schedule is ignored.
    use_stub_rate : bool
        Optional, if true stub rate is used for municipal bond discounting.
    """

    paydown_optional: Optional[bool] = rest_field(name="paydownOptional")
    """Optional, if true the bond's sink or paydown schedule is treated as optional."""
    ignore_call_info: Optional[bool] = rest_field(name="ignoreCallInfo")
    """Optional, if true the bond's call schedule is ignored."""
    use_stub_rate: Optional[bool] = rest_field(name="useStubRate")
    """Optional, if true stub rate is used for municipal bond discounting."""

    @overload
    def __init__(
        self,
        *,
        paydown_optional: Optional[bool] = None,
        ignore_call_info: Optional[bool] = None,
        use_stub_rate: Optional[bool] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class Observance(_model_base.Model):
    """An object to determine a holiday rescheduling if it falls on a rest day.

    Attributes
    ----------
    falls_on : str or ~analyticsapi.models.WeekDay
        The day of the week the holiday falls on. It is used as a reference
        point. Required. Known values are: "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", and "Sunday".
    reschedule_description : ~analyticsapi.models.RescheduleDescription
        An object to determine a holiday rescheduling. Required.
    """

    falls_on: Union[str, "_models.WeekDay"] = rest_field(name="fallsOn")
    """The day of the week the holiday falls on. It is used as a reference point. Required. Known
     values are: \"Monday\", \"Tuesday\", \"Wednesday\", \"Thursday\", \"Friday\", \"Saturday\", and
     \"Sunday\"."""
    reschedule_description: "_models.RescheduleDescription" = rest_field(name="rescheduleDescription")
    """An object to determine a holiday rescheduling. Required."""

    @overload
    def __init__(
        self,
        *,
        falls_on: Union[str, "_models.WeekDay"],
        reschedule_description: "_models.RescheduleDescription",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class OffsetDefinition(_model_base.Model):
    """An object that defines how the payment dates are derived from the interest period dates.

    Attributes
    ----------
    tenor : str
        The tenor that represents the difference between the actual payment
        date and the interest period reference date. A tenor expresses a period
        of time using a specific syntax. There are two kinds of tenor:

        * Ad-hoc tenors explicitly state the length of time in Days (D), Weeks (W), Months (M) and
        Years (Y).
          For example "1D" for one day, "2W" for two weeks or "3M1D" for three months and a day.
          When mixing units, units must be written in descending order of size (Y > M > W > D).  So,
        5M3D is valid, but 3D5M is not.
        * Common tenors are expressed as letter codes:
        * ON (Overnight) - A one business day period that starts today.
        * TN (Tomorrow-Next) - A one business day period that starts next business day.
        * SPOT (Spot Date) - A period that ends on the spot date.  Date is calculated as trade date
        (today) + days to spot.
        * SN (Spot-Next) - A one business day period that starts at the spot date.
        * SW (Spot-Week) - A one business week period that starts at the spot date. Required.
    business_day_adjustment : ~analyticsapi.models.BusinessDayAdjustmentDefinition
        An object that defines the business day adjustment convention.
        Required.
    reference_date : str or ~analyticsapi.models.CouponReferenceDateEnum
        The reference date for the actual payment date calculation. Required.
        Known values are: "PeriodStartDate" and "PeriodEndDate".
    direction : str or ~analyticsapi.models.DirectionEnum
        The direction of the actual payment date calculation (backward or
        forward). Required. Known values are: "Backward" and "Forward".
    """

    tenor: str = rest_field()
    """The tenor that represents the difference between the actual payment date and the interest
     period reference date.
     A tenor expresses a period of time using a specific syntax. There are two kinds of tenor:
     
     
     * Ad-hoc tenors explicitly state the length of time in Days (D), Weeks (W), Months (M) and
     Years (Y).
       For example \"1D\" for one day, \"2W\" for two weeks or \"3M1D\" for three months and a day.
       When mixing units, units must be written in descending order of size (Y > M > W > D).  So,
     5M3D is valid, but 3D5M is not.
     * Common tenors are expressed as letter codes:
     * ON (Overnight) - A one business day period that starts today.
     * TN (Tomorrow-Next) - A one business day period that starts next business day.
     * SPOT (Spot Date) - A period that ends on the spot date.  Date is calculated as trade date
     (today) + days to spot.
     * SN (Spot-Next) - A one business day period that starts at the spot date.
     * SW (Spot-Week) - A one business week period that starts at the spot date. Required."""
    business_day_adjustment: "_models.BusinessDayAdjustmentDefinition" = rest_field(name="businessDayAdjustment")
    """An object that defines the business day adjustment convention. Required."""
    reference_date: Union[str, "_models.CouponReferenceDateEnum"] = rest_field(name="referenceDate")
    """The reference date for the actual payment date calculation. Required. Known values are:
     \"PeriodStartDate\" and \"PeriodEndDate\"."""
    direction: Union[str, "_models.DirectionEnum"] = rest_field()
    """The direction of the actual payment date calculation (backward or forward). Required. Known
     values are: \"Backward\" and \"Forward\"."""

    @overload
    def __init__(
        self,
        *,
        tenor: str,
        business_day_adjustment: "_models.BusinessDayAdjustmentDefinition",
        reference_date: Union[str, "_models.CouponReferenceDateEnum"],
        direction: Union[str, "_models.DirectionEnum"],
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class OptionDefinition(_model_base.Model):
    """An object that defines an option instrument.
    It can can be either a vanilla option (that gives the holder the right to buy or sell the
    underlying asset at a predetermined price within a given time frame),
    or an exotic option (such as an Asian, a barrier, a binary and other options).

    Attributes
    ----------
    underlying : ~analyticsapi.models.UnderlyingDefinition
        An object that defines the underlying asset of an option instrument.
        Required.
    exercise : ~analyticsapi.models.ExerciseDefinition
        An object that defines the exercise settings of an option instrument.
        Required.
    settlement : ~analyticsapi.models.SettlementDefinition
        An object that defines the settlement settings of an option instrument.
    option_type : str or ~analyticsapi.models.CallPutEnum
        An indicator of whether an option instrument is a call or a put. Known
        values are: "Call" and "Put".
    notional_amount : ~analyticsapi.models.Amount
        An object that defines the notional amount of an option instrument.
    barrier_up : ~analyticsapi.models.BarrierDefinition
        An object that defines an up barrier option.
    barrier_down : ~analyticsapi.models.BarrierDefinition
        An object that defines a down barrier option.
    binary_up : ~analyticsapi.models.BinaryDefinition
        An object that defines an up binary option.
    binary_down : ~analyticsapi.models.BinaryDefinition
        An object that defines a down binary option.
    asian : ~analyticsapi.models.AsianDefinition
        An object that defines an Asian option.
    """

    underlying: "_models.UnderlyingDefinition" = rest_field()
    """An object that defines the underlying asset of an option instrument. Required."""
    exercise: "_models.ExerciseDefinition" = rest_field()
    """An object that defines the exercise settings of an option instrument. Required."""
    settlement: Optional["_models.SettlementDefinition"] = rest_field()
    """An object that defines the settlement settings of an option instrument."""
    option_type: Optional[Union[str, "_models.CallPutEnum"]] = rest_field(name="optionType")
    """An indicator of whether an option instrument is a call or a put. Known values are: \"Call\" and
     \"Put\"."""
    notional_amount: Optional["_models.Amount"] = rest_field(name="notionalAmount")
    """An object that defines the notional amount of an option instrument."""
    barrier_up: Optional["_models.BarrierDefinition"] = rest_field(name="barrierUp")
    """An object that defines an up barrier option."""
    barrier_down: Optional["_models.BarrierDefinition"] = rest_field(name="barrierDown")
    """An object that defines a down barrier option."""
    binary_up: Optional["_models.BinaryDefinition"] = rest_field(name="binaryUp")
    """An object that defines an up binary option."""
    binary_down: Optional["_models.BinaryDefinition"] = rest_field(name="binaryDown")
    """An object that defines a down binary option."""
    asian: Optional["_models.AsianDefinition"] = rest_field()
    """An object that defines an Asian option."""

    @overload
    def __init__(
        self,
        *,
        underlying: "_models.UnderlyingDefinition",
        exercise: "_models.ExerciseDefinition",
        settlement: Optional["_models.SettlementDefinition"] = None,
        option_type: Optional[Union[str, "_models.CallPutEnum"]] = None,
        notional_amount: Optional["_models.Amount"] = None,
        barrier_up: Optional["_models.BarrierDefinition"] = None,
        barrier_down: Optional["_models.BarrierDefinition"] = None,
        binary_up: Optional["_models.BinaryDefinition"] = None,
        binary_down: Optional["_models.BinaryDefinition"] = None,
        asian: Optional["_models.AsianDefinition"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class OriginChannel(_model_base.Model):
    """OriginChannel.

    Attributes
    ----------
    unspecified : ~decimal.Decimal
    broker : ~decimal.Decimal
    correspondence : ~decimal.Decimal
    retail : ~decimal.Decimal
    """

    unspecified: Optional[decimal.Decimal] = rest_field()
    broker: Optional[decimal.Decimal] = rest_field()
    correspondence: Optional[decimal.Decimal] = rest_field()
    retail: Optional[decimal.Decimal] = rest_field()

    @overload
    def __init__(
        self,
        *,
        unspecified: Optional[decimal.Decimal] = None,
        broker: Optional[decimal.Decimal] = None,
        correspondence: Optional[decimal.Decimal] = None,
        retail: Optional[decimal.Decimal] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class Partials(_model_base.Model):
    """Partials.

    Attributes
    ----------
    curve_type : str
        Is one of the following types: Literal["PAR"], Literal["SPOT"],
        Literal["FORWARD"]
    curve_shift : float
        Shock amount, in basis points.
    shock_type : str
        Is either a Literal["SQUARE"] type or a Literal["TRIANGLE"] type.
    use_cumulative_wave_method : bool
        A cumulative shock which starts at the short end and attributes
        sensitivity to the tenors as it moves through the curve, so the entire
        curve is shocked by 25bps.
    partial_duration_years : list[float]
        Specific custom partial points.  The default value is None, needs to be
        assigned before using.
    """

    curve_type: Optional[Literal["PAR", "SPOT", "FORWARD"]] = rest_field(name="curveType")
    """Is one of the following types: Literal[\"PAR\"], Literal[\"SPOT\"], Literal[\"FORWARD\"]"""
    curve_shift: Optional[float] = rest_field(name="curveShift")
    """Shock amount, in basis points."""
    shock_type: Optional[Literal["SQUARE", "TRIANGLE"]] = rest_field(name="shockType")
    """Is either a Literal[\"SQUARE\"] type or a Literal[\"TRIANGLE\"] type."""
    use_cumulative_wave_method: Optional[bool] = rest_field(name="useCumulativeWaveMethod")
    """A cumulative shock which starts at the short end and attributes sensitivity to the tenors as it
     moves through the curve, so the entire curve is shocked by 25bps."""
    partial_duration_years: Optional[List[float]] = rest_field(name="partialDurationYears")
    """Specific custom partial points."""

    @overload
    def __init__(
        self,
        *,
        curve_type: Optional[Literal["PAR", "SPOT", "FORWARD"]] = None,
        curve_shift: Optional[float] = None,
        shock_type: Optional[Literal["SQUARE", "TRIANGLE"]] = None,
        use_cumulative_wave_method: Optional[bool] = None,
        partial_duration_years: Optional[List[float]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class Payment(_model_base.Model):
    """An object that defines a payment.

    Attributes
    ----------
    date : ~analyticsapi.models.Date
        An object that contains properties to define and adjust the payment
        date.
    amount : ~analyticsapi.models.Amount
        An object that defines the amount and currency of a payment. Required.
    payer : str or ~analyticsapi.models.PartyEnum
        The party (Party1 or Party2) that makes the payment. Required. Known
        values are: "Party1" and "Party2".
    receiver : str or ~analyticsapi.models.PartyEnum
        The party (Party1 or Party2) that receives the payment. Required. Known
        values are: "Party1" and "Party2".
    """

    date: Optional["_models.Date"] = rest_field()
    """An object that contains properties to define and adjust the payment date."""
    amount: "_models.Amount" = rest_field()
    """An object that defines the amount and currency of a payment. Required."""
    payer: Union[str, "_models.PartyEnum"] = rest_field()
    """The party (Party1 or Party2) that makes the payment. Required. Known values are: \"Party1\" and
     \"Party2\"."""
    receiver: Union[str, "_models.PartyEnum"] = rest_field()
    """The party (Party1 or Party2) that receives the payment. Required. Known values are: \"Party1\"
     and \"Party2\"."""

    @overload
    def __init__(
        self,
        *,
        amount: "_models.Amount",
        payer: Union[str, "_models.PartyEnum"],
        receiver: Union[str, "_models.PartyEnum"],
        date: Optional["_models.Date"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class PrepayDialsInput(_model_base.Model):
    """PrepayDialsInput.

    Attributes
    ----------
    settings : ~analyticsapi.models.PrepayDialsSettings
    dials : ~analyticsapi.models.DefaultDials
    """

    settings: Optional["_models.PrepayDialsSettings"] = rest_field()
    dials: Optional["_models.DefaultDials"] = rest_field()

    @overload
    def __init__(
        self,
        *,
        settings: Optional["_models.PrepayDialsSettings"] = None,
        dials: Optional["_models.DefaultDials"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class PrepayDialsSettings(_model_base.Model):  # pylint: disable=too-many-instance-attributes
    """PrepayDialsSettings.

    Attributes
    ----------
    ignore_housing_inflation_flag : bool
    cmo_geographic_info_flag : bool
    current_coupon_spread_adjustment : ~decimal.Decimal
    ignore_disclosure_info : bool
    short_term_prepay_adjustment_flag : bool
    fnma_model_for_whole_loans_flag : bool
    fnma_model_for_gnma_loans_flag : bool
    fnma_model_for_alta_loans_flag : bool
    ignore_servicer_flag : bool
    ignore_current_delinquency_flag : bool
    commingled_super_as_fn_flag : bool
    use_lphpa_flag : bool
    ignore_sshpa_flag : bool
    ignore_ss_user_hpa_flag : bool
    ignore_dti_dispersion_flag : bool
    ignore_fico_dispersion_flag : bool
    ignore_wala_dispersion_flag : bool
    ignore_ltv_dispersion_flag : bool
    ignore_wac_dispersion_flag : bool
    ignore_model_hpa_scenario_flag : bool
    ps_spread_model_flag : bool
    harp_cutoff_date : str
    ps_spread_lookback : int
    delinquency_resolution_period : int
    home_price_appreciation : ~analyticsapi.models.InterpolationTypeAndVector
    state_home_price_appreciation : list[~analyticsapi.models.StateHomePriceAppreciation]
        The default value is None, needs to be assigned before using.
    unemployment_projection : ~analyticsapi.models.InterpolationTypeAndVector
    cpr_adjustment : ~analyticsapi.models.InterpolationTypeAndVector
    term_unit : str
        Is either a Literal["MONTH"] type or a Literal["YEAR"] type.
    """

    ignore_housing_inflation_flag: Optional[bool] = rest_field(name="ignoreHousingInflationFlag")
    cmo_geographic_info_flag: Optional[bool] = rest_field(name="cmoGeographicInfoFlag")
    current_coupon_spread_adjustment: Optional[decimal.Decimal] = rest_field(name="currentCouponSpreadAdjustment")
    ignore_disclosure_info: Optional[bool] = rest_field(name="ignoreDisclosureInfo")
    short_term_prepay_adjustment_flag: Optional[bool] = rest_field(name="shortTermPrepayAdjustmentFlag")
    fnma_model_for_whole_loans_flag: Optional[bool] = rest_field(name="fnmaModelForWholeLoansFlag")
    fnma_model_for_gnma_loans_flag: Optional[bool] = rest_field(name="fnmaModelForGNMALoansFlag")
    fnma_model_for_alta_loans_flag: Optional[bool] = rest_field(name="fnmaModelForALTALoansFlag")
    ignore_servicer_flag: Optional[bool] = rest_field(name="ignoreServicerFlag")
    ignore_current_delinquency_flag: Optional[bool] = rest_field(name="ignoreCurrentDelinquencyFlag")
    commingled_super_as_fn_flag: Optional[bool] = rest_field(name="commingledSuperAsFNFlag")
    use_lphpa_flag: Optional[bool] = rest_field(name="useLPHPAFlag")
    ignore_sshpa_flag: Optional[bool] = rest_field(name="ignoreSSHPAFlag")
    ignore_ss_user_hpa_flag: Optional[bool] = rest_field(name="ignoreSSUserHPAFlag")
    ignore_dti_dispersion_flag: Optional[bool] = rest_field(name="ignoreDTIDispersionFlag")
    ignore_fico_dispersion_flag: Optional[bool] = rest_field(name="ignoreFICODispersionFlag")
    ignore_wala_dispersion_flag: Optional[bool] = rest_field(name="ignoreWALADispersionFlag")
    ignore_ltv_dispersion_flag: Optional[bool] = rest_field(name="ignoreLTVDispersionFlag")
    ignore_wac_dispersion_flag: Optional[bool] = rest_field(name="ignoreWACDispersionFlag")
    ignore_model_hpa_scenario_flag: Optional[bool] = rest_field(name="ignoreModelHPAScenarioFlag")
    ps_spread_model_flag: Optional[bool] = rest_field(name="psSpreadModelFlag")
    harp_cutoff_date: Optional[str] = rest_field(name="harpCutoffDate")
    ps_spread_lookback: Optional[int] = rest_field(name="psSpreadLookback")
    delinquency_resolution_period: Optional[int] = rest_field(name="delinquencyResolutionPeriod")
    home_price_appreciation: Optional["_models.InterpolationTypeAndVector"] = rest_field(name="homePriceAppreciation")
    state_home_price_appreciation: Optional[List["_models.StateHomePriceAppreciation"]] = rest_field(
        name="stateHomePriceAppreciation"
    )
    unemployment_projection: Optional["_models.InterpolationTypeAndVector"] = rest_field(name="unemploymentProjection")
    cpr_adjustment: Optional["_models.InterpolationTypeAndVector"] = rest_field(name="cprAdjustment")
    term_unit: Optional[Literal["MONTH", "YEAR"]] = rest_field(name="termUnit")
    """Is either a Literal[\"MONTH\"] type or a Literal[\"YEAR\"] type."""

    @overload
    def __init__(
        self,
        *,
        ignore_housing_inflation_flag: Optional[bool] = None,
        cmo_geographic_info_flag: Optional[bool] = None,
        current_coupon_spread_adjustment: Optional[decimal.Decimal] = None,
        ignore_disclosure_info: Optional[bool] = None,
        short_term_prepay_adjustment_flag: Optional[bool] = None,
        fnma_model_for_whole_loans_flag: Optional[bool] = None,
        fnma_model_for_gnma_loans_flag: Optional[bool] = None,
        fnma_model_for_alta_loans_flag: Optional[bool] = None,
        ignore_servicer_flag: Optional[bool] = None,
        ignore_current_delinquency_flag: Optional[bool] = None,
        commingled_super_as_fn_flag: Optional[bool] = None,
        use_lphpa_flag: Optional[bool] = None,
        ignore_sshpa_flag: Optional[bool] = None,
        ignore_ss_user_hpa_flag: Optional[bool] = None,
        ignore_dti_dispersion_flag: Optional[bool] = None,
        ignore_fico_dispersion_flag: Optional[bool] = None,
        ignore_wala_dispersion_flag: Optional[bool] = None,
        ignore_ltv_dispersion_flag: Optional[bool] = None,
        ignore_wac_dispersion_flag: Optional[bool] = None,
        ignore_model_hpa_scenario_flag: Optional[bool] = None,
        ps_spread_model_flag: Optional[bool] = None,
        harp_cutoff_date: Optional[str] = None,
        ps_spread_lookback: Optional[int] = None,
        delinquency_resolution_period: Optional[int] = None,
        home_price_appreciation: Optional["_models.InterpolationTypeAndVector"] = None,
        state_home_price_appreciation: Optional[List["_models.StateHomePriceAppreciation"]] = None,
        unemployment_projection: Optional["_models.InterpolationTypeAndVector"] = None,
        cpr_adjustment: Optional["_models.InterpolationTypeAndVector"] = None,
        term_unit: Optional[Literal["MONTH", "YEAR"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class PrepayModelSeller(_model_base.Model):
    """PrepayModelSeller.

    Attributes
    ----------
    seller : str
    percent : ~decimal.Decimal
    """

    seller: Optional[str] = rest_field()
    percent: Optional[decimal.Decimal] = rest_field()

    @overload
    def __init__(
        self,
        *,
        seller: Optional[str] = None,
        percent: Optional[decimal.Decimal] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class PrepayModelServicer(_model_base.Model):
    """PrepayModelServicer.

    Attributes
    ----------
    servicer : str
    percent : ~decimal.Decimal
    """

    servicer: Optional[str] = rest_field()
    percent: Optional[decimal.Decimal] = rest_field()

    @overload
    def __init__(
        self,
        *,
        servicer: Optional[str] = None,
        percent: Optional[decimal.Decimal] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class PricingScenario(_model_base.Model):
    """PricingScenario.

    Attributes
    ----------
    primary : bool
        Primary pricing speed assumption.
    type : str
        Is either a Literal["CPY"] type or a Literal["CPJ"] type.
    rate : float
        Prepayment speed.
    system_scenario_name : str
        Pre-set pricing scenario.
    custom_scenario : ~analyticsapi.models.CustomScenario
    """

    primary: Optional[bool] = rest_field()
    """Primary pricing speed assumption."""
    type: Optional[Literal["CPY", "CPJ"]] = rest_field(default=None)
    """Is either a Literal[\"CPY\"] type or a Literal[\"CPJ\"] type."""
    rate: Optional[float] = rest_field()
    """Prepayment speed."""
    system_scenario_name: Optional[str] = rest_field(name="systemScenarioName")
    """Pre-set pricing scenario."""
    custom_scenario: Optional["_models.CustomScenario"] = rest_field(name="customScenario")

    @overload
    def __init__(
        self,
        *,
        primary: Optional[bool] = None,
        type: Optional[Literal["CPY", "CPJ"]] = None,
        rate: Optional[float] = None,
        system_scenario_name: Optional[str] = None,
        custom_scenario: Optional["_models.CustomScenario"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class PrincipalDefinition(_model_base.Model):
    """An object that defines the principal used to calculate interest payments, which can also be
    exchanged between parties.

    Attributes
    ----------
    currency : str
        The currency of the payments derived from the principal (e.g., interest
        rate payments). Required.
    amount : float
        The principal value of the instrument. It can be zero if it gradually
        increases with the payments defined in the payments parameter.
    payments : list[~analyticsapi.models.DatedValue]
        An array of date-value pairs representing the actual principal amounts
        added (positive value) or substracted from the principal.  The default
        value is None, needs to be assigned before using.
    amortization : ~analyticsapi.models.AmortizationDefinition
        An object that defines the amortization schedule.
    initial_principal_exchange : bool
        An indicator of whether the principal is exchanged between parties on
        the start date.
    final_principal_exchange : bool
        An indicator of whether the principal is exchanged between parties on
        the end date.
    interim_principal_exchange : bool
        An indicator of whether the principal is exchanged between parties
        during the life of the instrtument (e.g., resettable principal).
    repayment_currency : str
        The currency in which the principal is repaid if different from the
        denomination currency. This can be used for dual currency bonds.
    """

    currency: str = rest_field()
    """The currency of the payments derived from the principal (e.g., interest rate payments).
     Required."""
    amount: Optional[float] = rest_field()
    """The principal value of the instrument. It can be zero if it gradually increases with the
     payments defined in the payments parameter."""
    payments: Optional[List["_models.DatedValue"]] = rest_field()
    """An array of date-value pairs representing the actual principal amounts added (positive value)
     or substracted from the principal."""
    amortization: Optional["_models.AmortizationDefinition"] = rest_field()
    """An object that defines the amortization schedule."""
    initial_principal_exchange: Optional[bool] = rest_field(name="initialPrincipalExchange")
    """An indicator of whether the principal is exchanged between parties on the start date."""
    final_principal_exchange: Optional[bool] = rest_field(name="finalPrincipalExchange")
    """An indicator of whether the principal is exchanged between parties on the end date."""
    interim_principal_exchange: Optional[bool] = rest_field(name="interimPrincipalExchange")
    """An indicator of whether the principal is exchanged between parties during the life of the
     instrtument (e.g., resettable principal)."""
    repayment_currency: Optional[str] = rest_field(name="repaymentCurrency")
    """The currency in which the principal is repaid if different from the denomination currency. This
     can be used for dual currency bonds."""

    @overload
    def __init__(
        self,
        *,
        currency: str,
        amount: Optional[float] = None,
        payments: Optional[List["_models.DatedValue"]] = None,
        amortization: Optional["_models.AmortizationDefinition"] = None,
        initial_principal_exchange: Optional[bool] = None,
        final_principal_exchange: Optional[bool] = None,
        interim_principal_exchange: Optional[bool] = None,
        repayment_currency: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class PyCalcGlobalSettings(_model_base.Model):  # pylint: disable=too-many-instance-attributes
    """PyCalcGlobalSettings.

    Attributes
    ----------
    pricing_date : ~datetime.date
        A historical curve and term structure date. Only one date option can be
        used (pricingDate, usePreviousClose, useLiveData).
    use_previous_close : bool
        A date selection that uses the prior closing business day’s curve and
        volatility surface. Only one date option can be used (pricingDate,
        usePreviousClose, useLiveData).
    use_live_data : bool
        A date selection that will always use live curve data. Only one date
        option can be used (pricingDate, usePreviousClose, useLiveData).
    use_ibor6_m : bool
        Use Euribor 6M Swap curve (EUR securities only).
    retrieve_ppm_projection : bool
        Optional. If true, retrieves monthly prepayment model projections.
    retrieve_oas_path : bool
        Optional. If true, OAS model path data.
    use_stochastic_hpa : bool
        Optional, for CRT and Non-Agency. If true, for OAS computations, for
        each rates path there will be an associated stochastic HPA path. If
        false, HPA will align with the agency approach.
    use_five_point_convexity : bool
        Optional, if true convexity is calculated using 5-points, default is
        3-points.
    retrieve_roll_rate_matrix : bool
        Optional, if true Roll Rate Matrix projections are retrieved (for
        CRT/non-agency Deals).
    use_model_col_haircut : bool
        Optional. Default is off (our recommendation) and delinquency model
        used. If true haircut model-projected principal and interest cash flows
        are used. Cash flows are reduced when servicers stop advancing
        principal and interest on delinquent loans.
    use1000_path : bool
        Optional. Default is 200 paths. If true, CMO OAS is calculated using
        1,000 paths.
    use_core_logic_group_model : bool
        Optional, for Non-Agency. Prepayment and default assumptions are based
        at the group level, rather than the deal level.
    sba_ignore_prepay_penalty : bool
        Optional, for SBA bonds. If true, prepayment penalties are ignored.
    use_ois : bool
    use_non_qm_collateral : bool
        Optional, if true, Non-QM collateral is used for non-agency RMBS model
        calls, otherwise Alt-A collateral is used. This flag only applies to
        prepay type v97. If this flag is set to true, you must also set
        'coreLogicCollateral' to 'USE'.
    core_logic_collateral : str
        Optional, for Non-Agency. Enables model to be run using from CoreLogic
        collateral data. Is one of the following types: Literal["DEFAULT"],
        Literal["USE"], Literal["IGNORE"]
    shock_repo_rates_futures : bool
        Optional, for Futures. Repo rates for shocked when calculating partials
        for futures.
    use_muni_non_call_curve : bool
        Optional, for Muni bonds. Curve is constructed using non-callable
        securities only.
    use_muni_tax_settings : bool
        Optional, for Munis. Take into consideration, de minimus, capital gains
        rate, and ordinary income rate.
    muni_de_minimis_annual_discount : float
        Optional, for Muni bonds. User specified de minimus discount.
    muni_capital_gains_rate : float
        Optional, for Muni bonds. User specified capital gains tax rate.
    muni_ordinary_income_rate : float
        Optional, for Muni bonds. User specified ordinary income tax rate.
    prepay_dials : ~analyticsapi.models.JsonRef
        Optional. Used to refer to a prepay dial that a user has uploaded as
        part of a job.
    current_coupon_rates : str
        Is one of the following types: Literal["MOATS"],
        Literal["SpreadToSwap"], Literal["SpreadToTreasury"],
        Literal["SpreadToSwapMeanReversion"], Literal["TreasuryMoats"]
    sensitivity_shocks : ~analyticsapi.models.SensitivityShocks
    lookback_settings : ~analyticsapi.models.LookbackSettings
    custom : dict[str, str]
    """

    pricing_date: Optional[datetime.date] = rest_field(name="pricingDate")
    """A historical curve and term structure date. Only one date option can be used (pricingDate,
     usePreviousClose, useLiveData)."""
    use_previous_close: Optional[bool] = rest_field(name="usePreviousClose")
    """A date selection that uses the prior closing business day’s curve and volatility surface. Only
     one date option can be used (pricingDate, usePreviousClose, useLiveData)."""
    use_live_data: Optional[bool] = rest_field(name="useLiveData")
    """A date selection that will always use live curve data. Only one date option can be used
     (pricingDate, usePreviousClose, useLiveData)."""
    use_ibor6_m: Optional[bool] = rest_field(name="useIBOR6M")
    """Use Euribor 6M Swap curve (EUR securities only)."""
    retrieve_ppm_projection: Optional[bool] = rest_field(name="retrievePPMProjection")
    """Optional. If true, retrieves monthly prepayment model projections."""
    retrieve_oas_path: Optional[bool] = rest_field(name="retrieveOASPath")
    """Optional. If true, OAS model path data."""
    use_stochastic_hpa: Optional[bool] = rest_field(name="useStochasticHPA")
    """Optional, for CRT and Non-Agency. If true, for OAS computations, for each rates path there will
     be an associated stochastic HPA path. If false, HPA will align with the agency approach."""
    use_five_point_convexity: Optional[bool] = rest_field(name="useFivePointConvexity")
    """Optional, if true convexity is calculated using 5-points, default is 3-points."""
    retrieve_roll_rate_matrix: Optional[bool] = rest_field(name="retrieveRollRateMatrix")
    """Optional, if true Roll Rate Matrix projections are retrieved (for CRT/non-agency Deals)."""
    use_model_col_haircut: Optional[bool] = rest_field(name="useModelColHaircut")
    """Optional. Default is off (our recommendation) and delinquency model used. If true haircut
     model-projected principal and interest cash flows are used. Cash flows are reduced when
     servicers stop advancing principal and interest on delinquent loans."""
    use1000_path: Optional[bool] = rest_field(name="use1000Path")
    """Optional. Default is 200 paths. If true, CMO OAS is calculated using 1,000 paths."""
    use_core_logic_group_model: Optional[bool] = rest_field(name="useCoreLogicGroupModel")
    """Optional, for Non-Agency. Prepayment and default assumptions are based at the group level,
     rather than the deal level."""
    sba_ignore_prepay_penalty: Optional[bool] = rest_field(name="sbaIgnorePrepayPenalty")
    """Optional, for SBA bonds. If true, prepayment penalties are ignored."""
    use_ois: Optional[bool] = rest_field(name="useOIS")
    use_non_qm_collateral: Optional[bool] = rest_field(name="useNonQMCollateral")
    """Optional, if true, Non-QM collateral is used for non-agency RMBS model calls, otherwise Alt-A
     collateral is used. This flag only applies to prepay type v97. If this flag is set to true, you
     must also set 'coreLogicCollateral' to 'USE'."""
    core_logic_collateral: Optional[Literal["DEFAULT", "USE", "IGNORE"]] = rest_field(name="coreLogicCollateral")
    """Optional, for Non-Agency. Enables model to be run using from CoreLogic collateral data. Is one
     of the following types: Literal[\"DEFAULT\"], Literal[\"USE\"], Literal[\"IGNORE\"]"""
    shock_repo_rates_futures: Optional[bool] = rest_field(name="shockRepoRatesFutures")
    """Optional, for Futures. Repo rates for shocked when calculating partials for futures."""
    use_muni_non_call_curve: Optional[bool] = rest_field(name="useMuniNonCallCurve")
    """Optional, for Muni bonds. Curve is constructed using non-callable securities only."""
    use_muni_tax_settings: Optional[bool] = rest_field(name="useMuniTaxSettings")
    """Optional, for Munis. Take into consideration, de minimus, capital gains rate, and ordinary
     income rate."""
    muni_de_minimis_annual_discount: Optional[float] = rest_field(name="muniDeMinimisAnnualDiscount")
    """Optional, for Muni bonds. User specified de minimus discount."""
    muni_capital_gains_rate: Optional[float] = rest_field(name="muniCapitalGainsRate")
    """Optional, for Muni bonds. User specified capital gains tax rate."""
    muni_ordinary_income_rate: Optional[float] = rest_field(name="muniOrdinaryIncomeRate")
    """Optional, for Muni bonds. User specified ordinary income tax rate."""
    prepay_dials: Optional["_models.JsonRef"] = rest_field(name="prepayDials")
    """Optional. Used to refer to a prepay dial that a user has uploaded as part of a job."""
    current_coupon_rates: Optional[
        Literal["MOATS", "SpreadToSwap", "SpreadToTreasury", "SpreadToSwapMeanReversion", "TreasuryMoats"]
    ] = rest_field(name="currentCouponRates")
    """Is one of the following types: Literal[\"MOATS\"], Literal[\"SpreadToSwap\"],
     Literal[\"SpreadToTreasury\"], Literal[\"SpreadToSwapMeanReversion\"],
     Literal[\"TreasuryMoats\"]"""
    sensitivity_shocks: Optional["_models.SensitivityShocks"] = rest_field(name="sensitivityShocks")
    lookback_settings: Optional["_models.LookbackSettings"] = rest_field(name="lookbackSettings")
    custom: Optional[Dict[str, str]] = rest_field()

    @overload
    def __init__(
        self,
        *,
        pricing_date: Optional[datetime.date] = None,
        use_previous_close: Optional[bool] = None,
        use_live_data: Optional[bool] = None,
        use_ibor6_m: Optional[bool] = None,
        retrieve_ppm_projection: Optional[bool] = None,
        retrieve_oas_path: Optional[bool] = None,
        use_stochastic_hpa: Optional[bool] = None,
        use_five_point_convexity: Optional[bool] = None,
        retrieve_roll_rate_matrix: Optional[bool] = None,
        use_model_col_haircut: Optional[bool] = None,
        use1000_path: Optional[bool] = None,
        use_core_logic_group_model: Optional[bool] = None,
        sba_ignore_prepay_penalty: Optional[bool] = None,
        use_ois: Optional[bool] = None,
        use_non_qm_collateral: Optional[bool] = None,
        core_logic_collateral: Optional[Literal["DEFAULT", "USE", "IGNORE"]] = None,
        shock_repo_rates_futures: Optional[bool] = None,
        use_muni_non_call_curve: Optional[bool] = None,
        use_muni_tax_settings: Optional[bool] = None,
        muni_de_minimis_annual_discount: Optional[float] = None,
        muni_capital_gains_rate: Optional[float] = None,
        muni_ordinary_income_rate: Optional[float] = None,
        prepay_dials: Optional["_models.JsonRef"] = None,
        current_coupon_rates: Optional[
            Literal["MOATS", "SpreadToSwap", "SpreadToTreasury", "SpreadToSwapMeanReversion", "TreasuryMoats"]
        ] = None,
        sensitivity_shocks: Optional["_models.SensitivityShocks"] = None,
        lookback_settings: Optional["_models.LookbackSettings"] = None,
        custom: Optional[Dict[str, str]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class PyCalcInput(_model_base.Model):  # pylint: disable=too-many-instance-attributes
    """PyCalcInput.

    Attributes
    ----------
    identifier : str
        Security reference ID.
    id_type : str or ~analyticsapi.models.IdTypeEnum
        Known values are: "SecurityIDEntry", "SecurityID", "CUSIP", "ISIN",
        "REGSISIN", "SEDOL", "Identifier", "ChinaInterbankCode",
        "ShanghaiExchangeCode", "ShenzhenExchangeCode", and "MXTickerID".
    user_tag : str
        User provided tag - this will be returned in the response.
    level : str
        Input price for the security. Input can be a price, yield, spread, OAS,
        etc.. See quick card for for list of options.
    level_value : float
        If level is not provided, provide levelValue - only numbers.
    level_type : str
        levelType can be provided along with levelValue. Example - "y" (for
        yield), "o" (for OAS).
    settlement_type : str
        Is one of the following types: Literal["MARKET"], Literal["INDEX"],
        Literal["CUSTOM"]
    settlement_date : ~datetime.date
        User specified settlement date. If settlementType is CUSTOM, user can
        choose between settlementDate and customSettlement. Recommend using
        settlementDate.
    custom_settlement : str
        Optional. If settlementType is CUSTOM, user can choose between
        settlementDate and customSettlement.
          Example of customSettlement (T + 2), where T is the pricing date. Recommend using
        settlementDate.
    underlying_price : float
    curve : ~analyticsapi.models.CurveTypeAndCurrency
    volatility : ~analyticsapi.models.Volatility
    extra_settings : ~analyticsapi.models.ExtraSettings
    hecm_settings : ~analyticsapi.models.HecmSettings
    loss_settings : ~analyticsapi.models.LossSettings
    prepay_settings : ~analyticsapi.models.RestPrepaySettings
    cmbs_settings : ~analyticsapi.models.CmbsSettings
    floater_settings : ~analyticsapi.models.FloaterSettings
    index_linker_settings : ~analyticsapi.models.IndexLinkerSettings
    muni_settings : ~analyticsapi.models.MuniSettings
    mbs_settings : ~analyticsapi.models.MbsSettings
    clo_settings : ~analyticsapi.models.CloSettings
    convertible_pricing : ~analyticsapi.models.ConvertiblePricing
    user_instrument : ~analyticsapi.models.JsonRef
        User Instrument reference.
    modification : ~analyticsapi.models.JsonRef
        Modify Collateral reference.
    current_coupon_spread : ~analyticsapi.models.JsonRef
    props : dict[str, any]
    """

    identifier: Optional[str] = rest_field()
    """Security reference ID."""
    id_type: Optional[Union[str, "_models.IdTypeEnum"]] = rest_field(name="idType")
    """Known values are: \"SecurityIDEntry\", \"SecurityID\", \"CUSIP\", \"ISIN\", \"REGSISIN\",
     \"SEDOL\", \"Identifier\", \"ChinaInterbankCode\", \"ShanghaiExchangeCode\",
     \"ShenzhenExchangeCode\", and \"MXTickerID\"."""
    user_tag: Optional[str] = rest_field(name="userTag")
    """User provided tag - this will be returned in the response."""
    level: Optional[str] = rest_field()
    """Input price for the security. Input can be a price, yield, spread, OAS, etc.. See quick card
     for for list of options."""
    level_value: Optional[float] = rest_field(name="levelValue")
    """If level is not provided, provide levelValue - only numbers."""
    level_type: Optional[str] = rest_field(name="levelType")
    """levelType can be provided along with levelValue. Example - \"y\" (for yield), \"o\" (for OAS)."""
    settlement_type: Optional[Literal["MARKET", "INDEX", "CUSTOM"]] = rest_field(name="settlementType")
    """Is one of the following types: Literal[\"MARKET\"], Literal[\"INDEX\"], Literal[\"CUSTOM\"]"""
    settlement_date: Optional[datetime.date] = rest_field(name="settlementDate")
    """User specified settlement date. If settlementType is CUSTOM, user can choose between
     settlementDate and customSettlement. Recommend using settlementDate."""
    custom_settlement: Optional[str] = rest_field(name="customSettlement")
    """Optional. If settlementType is CUSTOM, user can choose between settlementDate and
     customSettlement.
       Example of customSettlement (T + 2), where T is the pricing date. Recommend using
     settlementDate."""
    underlying_price: Optional[float] = rest_field(name="underlyingPrice")
    curve: Optional["_models.CurveTypeAndCurrency"] = rest_field()
    volatility: Optional["_models.Volatility"] = rest_field()
    extra_settings: Optional["_models.ExtraSettings"] = rest_field(name="extraSettings")
    hecm_settings: Optional["_models.HecmSettings"] = rest_field(name="hecmSettings")
    loss_settings: Optional["_models.LossSettings"] = rest_field(name="lossSettings")
    prepay_settings: Optional["_models.RestPrepaySettings"] = rest_field(name="prepaySettings")
    cmbs_settings: Optional["_models.CmbsSettings"] = rest_field(name="cmbsSettings")
    floater_settings: Optional["_models.FloaterSettings"] = rest_field(name="floaterSettings")
    index_linker_settings: Optional["_models.IndexLinkerSettings"] = rest_field(name="indexLinkerSettings")
    muni_settings: Optional["_models.MuniSettings"] = rest_field(name="muniSettings")
    mbs_settings: Optional["_models.MbsSettings"] = rest_field(name="mbsSettings")
    clo_settings: Optional["_models.CloSettings"] = rest_field(name="cloSettings")
    convertible_pricing: Optional["_models.ConvertiblePricing"] = rest_field(name="convertiblePricing")
    user_instrument: Optional["_models.JsonRef"] = rest_field(name="userInstrument")
    """User Instrument reference."""
    modification: Optional["_models.JsonRef"] = rest_field()
    """Modify Collateral reference."""
    current_coupon_spread: Optional["_models.JsonRef"] = rest_field(name="currentCouponSpread")
    props: Optional[Dict[str, Any]] = rest_field()

    @overload
    def __init__(
        self,
        *,
        identifier: Optional[str] = None,
        id_type: Optional[Union[str, "_models.IdTypeEnum"]] = None,
        user_tag: Optional[str] = None,
        level: Optional[str] = None,
        level_value: Optional[float] = None,
        level_type: Optional[str] = None,
        settlement_type: Optional[Literal["MARKET", "INDEX", "CUSTOM"]] = None,
        settlement_date: Optional[datetime.date] = None,
        custom_settlement: Optional[str] = None,
        underlying_price: Optional[float] = None,
        curve: Optional["_models.CurveTypeAndCurrency"] = None,
        volatility: Optional["_models.Volatility"] = None,
        extra_settings: Optional["_models.ExtraSettings"] = None,
        hecm_settings: Optional["_models.HecmSettings"] = None,
        loss_settings: Optional["_models.LossSettings"] = None,
        prepay_settings: Optional["_models.RestPrepaySettings"] = None,
        cmbs_settings: Optional["_models.CmbsSettings"] = None,
        floater_settings: Optional["_models.FloaterSettings"] = None,
        index_linker_settings: Optional["_models.IndexLinkerSettings"] = None,
        muni_settings: Optional["_models.MuniSettings"] = None,
        mbs_settings: Optional["_models.MbsSettings"] = None,
        clo_settings: Optional["_models.CloSettings"] = None,
        convertible_pricing: Optional["_models.ConvertiblePricing"] = None,
        user_instrument: Optional["_models.JsonRef"] = None,
        modification: Optional["_models.JsonRef"] = None,
        current_coupon_spread: Optional["_models.JsonRef"] = None,
        props: Optional[Dict[str, Any]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class PyCalcRequest(_model_base.Model):
    """PyCalcRequest.

    Attributes
    ----------
    global_settings : ~analyticsapi.models.PyCalcGlobalSettings
    input : list[~analyticsapi.models.PyCalcInput]
        The default value is None, needs to be assigned before using.
    keywords : list[str]
        The default value is None, needs to be assigned before using.
    """

    global_settings: Optional["_models.PyCalcGlobalSettings"] = rest_field(name="globalSettings")
    input: Optional[List["_models.PyCalcInput"]] = rest_field()
    keywords: Optional[List[str]] = rest_field()

    @overload
    def __init__(
        self,
        *,
        global_settings: Optional["_models.PyCalcGlobalSettings"] = None,
        input: Optional[List["_models.PyCalcInput"]] = None,
        keywords: Optional[List[str]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class Quote(_model_base.Model):
    """The object that contains the instrument quote and related attributes.

    Readonly variables are only populated by the server, and will be ignored when sending a request.

    Attributes
    ----------
    start_date : ~datetime.date
        The start date of the instrument. Depending on the tenor the start date
        is defined as follows:

        * for ON and SPOT it is typically equal to the valuation date,
        * for TN it is the valuation date + 1D,
        * for post-spot tenors (1D, 1M, 1Y, etc.) it is the valuation date + spot lag.

        The value is expressed in ISO 8601 format: YYYY-MM-DD (e.g., '2023-01-01').
    end_date : ~datetime.date
        The maturity or expiry date of the instrument. The value is expressed
        in ISO 8601 format: YYYY-MM-DD (e.g., '2024-01-01').
    definition : ~analyticsapi.models.QuoteDefinition
        An object that defines the attributes for getting the instrument quote.
        Required.
    values_property : ~analyticsapi.models.Values
        An object that contains the bid and ask quotes for the instrument.
    """

    start_date: Optional[datetime.date] = rest_field(name="startDate", visibility=["read"])
    """The start date of the instrument. Depending on the tenor the start date is defined as follows:
     
     
     * for ON and SPOT it is typically equal to the valuation date,
     * for TN it is the valuation date + 1D,
     * for post-spot tenors (1D, 1M, 1Y, etc.) it is the valuation date + spot lag.
     
     The value is expressed in ISO 8601 format: YYYY-MM-DD (e.g., '2023-01-01')."""
    end_date: Optional[datetime.date] = rest_field(name="endDate", visibility=["read"])
    """The maturity or expiry date of the instrument. The value is expressed in ISO 8601 format:
     YYYY-MM-DD (e.g., '2024-01-01')."""
    definition: "_models.QuoteDefinition" = rest_field()
    """An object that defines the attributes for getting the instrument quote. Required."""
    values_property: Optional["_models.Values"] = rest_field(name="values")
    """An object that contains the bid and ask quotes for the instrument."""

    @overload
    def __init__(
        self,
        *,
        definition: "_models.QuoteDefinition",
        values_property: Optional["_models.Values"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class QuoteDefinition(_model_base.Model):
    """An object that defines the attributes for getting the instrument quote.

    Attributes
    ----------
    instrument_code : str
        The code (RIC) of the instrument. Required.
    bid : ~analyticsapi.models.FieldDefinition
        An object that contains the bid quote for the instrument.
    ask : ~analyticsapi.models.FieldDefinition
        An object that contains the ask quote for the instrument.
    source : str
        The code of the contributor of the quote for the instrument used as a
        constituent (e.g., 'ICAP').
    """

    instrument_code: str = rest_field(name="instrumentCode")
    """The code (RIC) of the instrument. Required."""
    bid: Optional["_models.FieldDefinition"] = rest_field()
    """An object that contains the bid quote for the instrument."""
    ask: Optional["_models.FieldDefinition"] = rest_field()
    """An object that contains the ask quote for the instrument."""
    source: Optional[str] = rest_field()
    """The code of the contributor of the quote for the instrument used as a constituent (e.g.,
     'ICAP')."""

    @overload
    def __init__(
        self,
        *,
        instrument_code: str,
        bid: Optional["_models.FieldDefinition"] = None,
        ask: Optional["_models.FieldDefinition"] = None,
        source: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class Rate(_model_base.Model):
    """An object that defines the interest rate.

    Attributes
    ----------
    value : float
        The rate value. Required.
    unit : str or ~analyticsapi.models.UnitEnum
        The unit of the rate value. Required. Known values are: "Absolute",
        "BasisPoint", and "Percentage".
    """

    value: float = rest_field()
    """The rate value. Required."""
    unit: Union[str, "_models.UnitEnum"] = rest_field()
    """The unit of the rate value. Required. Known values are: \"Absolute\", \"BasisPoint\", and
     \"Percentage\"."""

    @overload
    def __init__(
        self,
        *,
        value: float,
        unit: Union[str, "_models.UnitEnum"],
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class RefDataMeta(_model_base.Model):
    """RefDataMeta.

    Attributes
    ----------
    request_id : str
        Required.
    status : str
        Required. Is one of the following types: Literal["NEW"],
        Literal["WAITING"], Literal["PENDING"], Literal["RUNNING"],
        Literal["ABORTING"], Literal["DONE"], Literal["ERROR"],
        Literal["SKIPPED"], Literal["ABORTED"]
    time_stamp : ~datetime.datetime
        Required.
    response_type : str
        Required. Is one of the following types: Literal["BOND_INDIC"],
        Literal["BOND_SEARCH"], Literal["CURVE_POINTS"],
        Literal["MARKET_SETTINGS"], Literal["MBS_HISTORY"], Literal["PY_CALC"],
        Literal["COLLATERAL_DETAILS"], Literal["CALC_SETTINGS"],
        Literal["MORTGAGE_MODEL"], Literal["ACTUAL_VS_PROJECTED"],
        Literal["WAL_SENSITIVITY"], Literal["SCENARIO_CALC"],
        Literal["MATRIX_PY"], Literal["HISTORICAL_DATA"], Literal["CASHFLOW"],
        Literal["VOLATILITY"], Literal["TEST"], Literal["SCENARIO_SETUPS"],
        Literal["XMLAPI"], Literal["BULK_ZIP"], Literal["BULK_COMPOSITE"],
        Literal["FORWARD_PRICING"], Literal["CALC_STATUS"],
        Literal["DELIMITED"], Literal["COMPACT"], Literal["BULK"],
        Literal["FX_FWDS"], Literal["USER_CURVE"], Literal["WAIT"],
        Literal["RETURNS_CALC"], Literal["TABLE"], Literal["PREPAY_DIALS"]
    results_status : str
        Required. Is one of the following types: Literal["ALL"],
        Literal["NONE"], Literal["PARTIAL"]
    """

    request_id: str = rest_field(name="requestId")
    """Required."""
    status: Literal["NEW", "WAITING", "PENDING", "RUNNING", "ABORTING", "DONE", "ERROR", "SKIPPED", "ABORTED"] = (
        rest_field()
    )
    """Required. Is one of the following types: Literal[\"NEW\"], Literal[\"WAITING\"],
     Literal[\"PENDING\"], Literal[\"RUNNING\"], Literal[\"ABORTING\"], Literal[\"DONE\"],
     Literal[\"ERROR\"], Literal[\"SKIPPED\"], Literal[\"ABORTED\"]"""
    time_stamp: datetime.datetime = rest_field(name="timeStamp", format="rfc3339")
    """Required."""
    response_type: Literal[
        "BOND_INDIC",
        "BOND_SEARCH",
        "CURVE_POINTS",
        "MARKET_SETTINGS",
        "MBS_HISTORY",
        "PY_CALC",
        "COLLATERAL_DETAILS",
        "CALC_SETTINGS",
        "MORTGAGE_MODEL",
        "ACTUAL_VS_PROJECTED",
        "WAL_SENSITIVITY",
        "SCENARIO_CALC",
        "MATRIX_PY",
        "HISTORICAL_DATA",
        "CASHFLOW",
        "VOLATILITY",
        "TEST",
        "SCENARIO_SETUPS",
        "XMLAPI",
        "BULK_ZIP",
        "BULK_COMPOSITE",
        "FORWARD_PRICING",
        "CALC_STATUS",
        "DELIMITED",
        "COMPACT",
        "BULK",
        "FX_FWDS",
        "USER_CURVE",
        "WAIT",
        "RETURNS_CALC",
        "TABLE",
        "PREPAY_DIALS",
    ] = rest_field(name="responseType")
    """Required. Is one of the following types: Literal[\"BOND_INDIC\"], Literal[\"BOND_SEARCH\"],
     Literal[\"CURVE_POINTS\"], Literal[\"MARKET_SETTINGS\"], Literal[\"MBS_HISTORY\"],
     Literal[\"PY_CALC\"], Literal[\"COLLATERAL_DETAILS\"], Literal[\"CALC_SETTINGS\"],
     Literal[\"MORTGAGE_MODEL\"], Literal[\"ACTUAL_VS_PROJECTED\"], Literal[\"WAL_SENSITIVITY\"],
     Literal[\"SCENARIO_CALC\"], Literal[\"MATRIX_PY\"], Literal[\"HISTORICAL_DATA\"],
     Literal[\"CASHFLOW\"], Literal[\"VOLATILITY\"], Literal[\"TEST\"],
     Literal[\"SCENARIO_SETUPS\"], Literal[\"XMLAPI\"], Literal[\"BULK_ZIP\"],
     Literal[\"BULK_COMPOSITE\"], Literal[\"FORWARD_PRICING\"], Literal[\"CALC_STATUS\"],
     Literal[\"DELIMITED\"], Literal[\"COMPACT\"], Literal[\"BULK\"], Literal[\"FX_FWDS\"],
     Literal[\"USER_CURVE\"], Literal[\"WAIT\"], Literal[\"RETURNS_CALC\"], Literal[\"TABLE\"],
     Literal[\"PREPAY_DIALS\"]"""
    results_status: Literal["ALL", "NONE", "PARTIAL"] = rest_field(name="resultsStatus")
    """Required. Is one of the following types: Literal[\"ALL\"], Literal[\"NONE\"],
     Literal[\"PARTIAL\"]"""

    @overload
    def __init__(
        self,
        *,
        request_id: str,
        status: Literal["NEW", "WAITING", "PENDING", "RUNNING", "ABORTING", "DONE", "ERROR", "SKIPPED", "ABORTED"],
        time_stamp: datetime.datetime,
        response_type: Literal[
            "BOND_INDIC",
            "BOND_SEARCH",
            "CURVE_POINTS",
            "MARKET_SETTINGS",
            "MBS_HISTORY",
            "PY_CALC",
            "COLLATERAL_DETAILS",
            "CALC_SETTINGS",
            "MORTGAGE_MODEL",
            "ACTUAL_VS_PROJECTED",
            "WAL_SENSITIVITY",
            "SCENARIO_CALC",
            "MATRIX_PY",
            "HISTORICAL_DATA",
            "CASHFLOW",
            "VOLATILITY",
            "TEST",
            "SCENARIO_SETUPS",
            "XMLAPI",
            "BULK_ZIP",
            "BULK_COMPOSITE",
            "FORWARD_PRICING",
            "CALC_STATUS",
            "DELIMITED",
            "COMPACT",
            "BULK",
            "FX_FWDS",
            "USER_CURVE",
            "WAIT",
            "RETURNS_CALC",
            "TABLE",
            "PREPAY_DIALS",
        ],
        results_status: Literal["ALL", "NONE", "PARTIAL"],
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class RelativeAdjustableDate(Date, discriminator="RelativeAdjustableDate"):
    """RelativeAdjustableDate.

    Attributes
    ----------
    date_moving_convention : str or ~analyticsapi.models.DateMovingConvention
        The method to adjust dates to working days. The possible values are:
        ModifiedFollowing: dates are adjusted to the next business day
        convention unless it goes into the next month. In such case, the
        previous business day convention is used, NextBusinessDay: dates are
        moved to the following working day, PreviousBusinessDay: dates are
        moved to the preceding working day, NoMoving: dates are not adjusted,
        EveryThirdWednesday: dates are moved to the third Wednesday of the
        month, or to the next working day if the third Wednesday is not a
        working day, BbswModifiedFollowing: dates are adjusted to the next
        business day convention unless it goes into the next month, or crosses
        mid-month (15th). In such case, the previous business day convention is
        used. Default is ModifiedFollowing. Known values are:
        "ModifiedFollowing", "NextBusinessDay", "PreviousBusinessDay",
        "NoMoving", "EveryThirdWednesday", and "BbswModifiedFollowing".
    calendars : list[str]
        An array of calendars that should be used for the date adjustment.
        Typically the calendars are derived based on the instruments currency
        or crossCurrency code.  The default value is None, needs to be assigned
        before using.
    date_type : str or ~analyticsapi.models.RELATIVE_ADJUSTABLE_DATE
        The type of the Date input. Possible values are: AdjustableDate,
        RelativeAdjustableDate. Required. The date is defined as adjusteable
        according the BusinessDayAdjustmentDefinition and relative to a
        reference date and a tenor.
    tenor : str
        A tenor (relative date) expressed as a code indicating the period
        between referenceDate(default=startDate) to endDate of the instrument
        (e.g., '6M', '1Y'). Predefined values are: ON (Overnight - A one
        business day period that starts today), TN (Tomorrow-Next - A one
        business day period that starts next business day, SPOT (Spot Date), SN
        (Spot-Next - A one business day period that starts at the spot date of
        a currency pair) or SW (Spot-Week - A one business week period that
        starts at the spot date of a currency pair). Tenors can also be
        specified as a whole number of time units. Possible units are: D
        (Days), W (Weeks), M (Months) or Y (Years). For example, one month is
        written '1M', 3 years is written: '3Y'. Time units can be mixed.  For
        example, 5M3D means '5 months and 3 days'. Note: units must be written
        in descending order of size (Y > M > W > D). Required.
    reference_date : str or ~analyticsapi.models.ReferenceDate
        The date which has been used as a reference date for the provided
        tenor. Possible values are: StartDate, ValuationDate, SpotDate. Default
        is StartDate. Known values are: "SpotDate", "StartDate", and
        "ValuationDate".
    """

    date_type: Literal[DateType.RELATIVE_ADJUSTABLE_DATE] = rest_discriminator(name="dateType")  # type: ignore
    """The type of the Date input. Possible values are: AdjustableDate, RelativeAdjustableDate.
     Required. The date is defined as adjusteable according the BusinessDayAdjustmentDefinition and
     relative to a reference date and a tenor."""
    tenor: str = rest_field()
    """A tenor (relative date) expressed as a code indicating the period between
     referenceDate(default=startDate) to endDate of the instrument (e.g., '6M', '1Y').
     Predefined values are: ON (Overnight - A one business day period that starts today), TN
     (Tomorrow-Next - A one business day period that starts next business day, SPOT (Spot Date), SN
     (Spot-Next - A one business day period that starts at the spot date of a currency pair) or SW
     (Spot-Week - A one business week period that starts at the spot date of a currency pair).
     Tenors can also be specified as a whole number of time units. Possible units are: D (Days), W
     (Weeks), M (Months) or Y (Years). For example, one month is written '1M', 3 years is written:
     '3Y'.
     Time units can be mixed.  For example, 5M3D means '5 months and 3 days'. Note: units must be
     written in descending order of size (Y > M > W > D). Required."""
    reference_date: Optional[Union[str, "_models.ReferenceDate"]] = rest_field(name="referenceDate")
    """The date which has been used as a reference date for the provided tenor. Possible values are:
     StartDate, ValuationDate, SpotDate. Default is StartDate. Known values are: \"SpotDate\",
     \"StartDate\", and \"ValuationDate\"."""

    @overload
    def __init__(
        self,
        *,
        tenor: str,
        date_moving_convention: Optional[Union[str, "_models.DateMovingConvention"]] = None,
        calendars: Optional[List[str]] = None,
        reference_date: Optional[Union[str, "_models.ReferenceDate"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, date_type=DateType.RELATIVE_ADJUSTABLE_DATE, **kwargs)


class RelativePositionWhen(When, discriminator="RelativePositionWhen"):
    """An object to determine the rule for a holiday that falls on a certain day of the week in a
    certain month. For example, Summer holiday on last Monday of August.

    Attributes
    ----------
    position_type : str or ~analyticsapi.models.RELATIVE_POSITION_WHEN
        The type of regular annual holiday rule. Only RelativePositionWhen
        value applies. Required. A rule to determine a holiday depending on the
        day of the week in a certain month. For example, Summer holiday on the
        last Monday of August.
    index : str or ~analyticsapi.models.IndexOrder
        The ordinal number of the day of the week in the month. Required. Known
        values are: "First", "Second", "Third", "Fourth", and "Last".
    day_of_week : str or ~analyticsapi.models.WeekDay
        The day of the week. Required. Known values are: "Monday", "Tuesday",
        "Wednesday", "Thursday", "Friday", "Saturday", and "Sunday".
    month : str or ~analyticsapi.models.Month
        The month of the year. Required. Known values are: "January",
        "February", "March", "April", "May", "June", "July", "August",
        "September", "October", "November", and "December".
    """

    position_type: Literal[PositionType.RELATIVE_POSITION_WHEN] = rest_discriminator(name="positionType")  # type: ignore
    """The type of regular annual holiday rule. Only RelativePositionWhen value applies. Required. A
     rule to determine a holiday depending on the day of the week in a certain month. For example,
     Summer holiday on the last Monday of August."""
    index: Union[str, "_models.IndexOrder"] = rest_field()
    """The ordinal number of the day of the week in the month. Required. Known values are: \"First\",
     \"Second\", \"Third\", \"Fourth\", and \"Last\"."""
    day_of_week: Union[str, "_models.WeekDay"] = rest_field(name="dayOfWeek")
    """The day of the week. Required. Known values are: \"Monday\", \"Tuesday\", \"Wednesday\",
     \"Thursday\", \"Friday\", \"Saturday\", and \"Sunday\"."""
    month: Union[str, "_models.Month"] = rest_field()
    """The month of the year. Required. Known values are: \"January\", \"February\", \"March\",
     \"April\", \"May\", \"June\", \"July\", \"August\", \"September\", \"October\", \"November\",
     and \"December\"."""

    @overload
    def __init__(
        self,
        *,
        index: Union[str, "_models.IndexOrder"],
        day_of_week: Union[str, "_models.WeekDay"],
        month: Union[str, "_models.Month"],
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, position_type=PositionType.RELATIVE_POSITION_WHEN, **kwargs)


class RelativeRescheduleDescription(RescheduleDescription, discriminator="RelativeRescheduleDescription"):
    """An object to determine the rule for rescheduling a holiday to a specific day.

    Attributes
    ----------
    reschedule_type : str or ~analyticsapi.models.RELATIVE_RESCHEDULE_DESCRIPTION
        The type of rescheduling for the observation period. Only
        RelativeRescheduleRescheduleDescription value applies. Required. The
        rule for rescheduling a holiday to a specific day. For example, if a
        holiday falls on Sunday, it is rescheduled to the first Monday after
        the holiday.
    index : str or ~analyticsapi.models.IndexOrder
        The ordinal number of the day of the week in the month. The value
        'Last' should only be used if the direction is set to 'Before'.
        Required. Known values are: "First", "Second", "Third", "Fourth", and
        "Last".
    day_of_week : str or ~analyticsapi.models.WeekDay
        The day of the week. Required. Known values are: "Monday", "Tuesday",
        "Wednesday", "Thursday", "Friday", "Saturday", and "Sunday".
    direction : str or ~analyticsapi.models.Direction
        An indicator of whether the observation period falls before or after
        the reference point. Required. Known values are: "Before" and "After".
    """

    reschedule_type: Literal[RescheduleType.RELATIVE_RESCHEDULE_DESCRIPTION] = rest_discriminator(name="rescheduleType")  # type: ignore
    """The type of rescheduling for the observation period. Only
     RelativeRescheduleRescheduleDescription value applies. Required. The rule for rescheduling a
     holiday to a specific day. For example, if a holiday falls on Sunday, it is rescheduled to the
     first Monday after the holiday."""
    index: Union[str, "_models.IndexOrder"] = rest_field()
    """The ordinal number of the day of the week in the month. The value 'Last' should only be used if
     the direction is set to 'Before'. Required. Known values are: \"First\", \"Second\", \"Third\",
     \"Fourth\", and \"Last\"."""
    day_of_week: Union[str, "_models.WeekDay"] = rest_field(name="dayOfWeek")
    """The day of the week. Required. Known values are: \"Monday\", \"Tuesday\", \"Wednesday\",
     \"Thursday\", \"Friday\", \"Saturday\", and \"Sunday\"."""
    direction: Union[str, "_models.Direction"] = rest_field()
    """An indicator of whether the observation period falls before or after the reference point.
     Required. Known values are: \"Before\" and \"After\"."""

    @overload
    def __init__(
        self,
        *,
        index: Union[str, "_models.IndexOrder"],
        day_of_week: Union[str, "_models.WeekDay"],
        direction: Union[str, "_models.Direction"],
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, reschedule_type=RescheduleType.RELATIVE_RESCHEDULE_DESCRIPTION, **kwargs)


class RelativeToRulePositionWhen(When, discriminator="RelativeToRulePositionWhen"):
    """An object to define a rule by reference to another rule. This defines the holiday period by
    reference to another holiday rule. Easter is most commonly used as a reference point.

    Attributes
    ----------
    position_type : str or ~analyticsapi.models.RELATIVE_TO_RULE_POSITION_WHEN
        The type of regular annual holiday rule. Only
        RelativeToRulePositionWhen value applies. Required. A rule that
        references another rule. For example, Easter is most commonly used as a
        reference point.
    key : str
        A user-defined key to create a reference to another rule (e.g. Easter)
        by name. Required.
    reschedule_description : ~analyticsapi.models.RescheduleDescription
        An object to determine holiday rescheduling. Required.
    """

    position_type: Literal[PositionType.RELATIVE_TO_RULE_POSITION_WHEN] = rest_discriminator(name="positionType")  # type: ignore
    """The type of regular annual holiday rule. Only RelativeToRulePositionWhen value applies.
     Required. A rule that references another rule. For example, Easter is most commonly used as a
     reference point."""
    key: str = rest_field()
    """A user-defined key to create a reference to another rule (e.g. Easter) by name. Required."""
    reschedule_description: "_models.RescheduleDescription" = rest_field(name="rescheduleDescription")
    """An object to determine holiday rescheduling. Required."""

    @overload
    def __init__(
        self,
        *,
        key: str,
        reschedule_description: "_models.RescheduleDescription",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, position_type=PositionType.RELATIVE_TO_RULE_POSITION_WHEN, **kwargs)


class RequestId(_model_base.Model):
    """RequestId.

    Attributes
    ----------
    request_id : str
        Required.
    """

    request_id: str = rest_field(name="requestId")
    """Required."""

    @overload
    def __init__(
        self,
        request_id: str,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["request_id"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class ResetDatesDefinition(_model_base.Model):
    """An object that defines the reset of index fixing dates.

    Attributes
    ----------
    offset : ~analyticsapi.models.OffsetDefinition
        An object that defines how the fixing dates of each period are derived
        from the interest period dates. Required.
    frequency : str or ~analyticsapi.models.FrequencyEnum
        The frequency of index reset. Known values are: "Annual", "SemiAnnual",
        "Quarterly", "Monthly", "BiMonthly", "Everyday", "EveryWorkingDay",
        "Every7Days", "Every14Days", "Every28Days", "Every30Days",
        "Every90Days", "Every91Days", "Every92Days", "Every93Days",
        "Every4Months", "Every180Days", "Every182Days", "Every183Days",
        "Every184Days", "Every364Days", "Every365Days", "R2", "R4", "Zero", and
        "Scheduled".
    """

    offset: "_models.OffsetDefinition" = rest_field()
    """An object that defines how the fixing dates of each period are derived from the interest period
     dates. Required."""
    frequency: Optional[Union[str, "_models.FrequencyEnum"]] = rest_field()
    """The frequency of index reset. Known values are: \"Annual\", \"SemiAnnual\", \"Quarterly\",
     \"Monthly\", \"BiMonthly\", \"Everyday\", \"EveryWorkingDay\", \"Every7Days\", \"Every14Days\",
     \"Every28Days\", \"Every30Days\", \"Every90Days\", \"Every91Days\", \"Every92Days\",
     \"Every93Days\", \"Every4Months\", \"Every180Days\", \"Every182Days\", \"Every183Days\",
     \"Every184Days\", \"Every364Days\", \"Every365Days\", \"R2\", \"R4\", \"Zero\", and
     \"Scheduled\"."""

    @overload
    def __init__(
        self,
        *,
        offset: "_models.OffsetDefinition",
        frequency: Optional[Union[str, "_models.FrequencyEnum"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class RestDays(_model_base.Model):
    """An object to determine rest days for the calendar.

    Attributes
    ----------
    rest_days : list[str or ~analyticsapi.models.WeekDay]
        Days of the week that are set as rest days. An array of WeekDay
        objects. Default is [WeekDay.Saturday, WeekDay.Sunday]. Required.  The
        default value is None, needs to be assigned before using.
    validity_period : ~analyticsapi.models.ValidityPeriod
        An object to determine the validity period. If not specified, the
        validity period is assumed to be perpetual.
    """

    rest_days: List[Union[str, "_models.WeekDay"]] = rest_field(name="restDays")
    """Days of the week that are set as rest days. An array of WeekDay objects. Default is
     [WeekDay.Saturday, WeekDay.Sunday]. Required."""
    validity_period: Optional["_models.ValidityPeriod"] = rest_field(name="validityPeriod")
    """An object to determine the validity period. If not specified, the validity period is assumed to
     be perpetual."""

    @overload
    def __init__(
        self,
        *,
        rest_days: List[Union[str, "_models.WeekDay"]],
        validity_period: Optional["_models.ValidityPeriod"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class RestPrepaySettings(_model_base.Model):
    """Optional. Used for securities that allow principal prepayment.

    Attributes
    ----------
    type : str
        Required. Is one of the following types: Literal["Model"],
        Literal["CurrentModel"], Literal["NewModel"], Literal["OldModel"],
        Literal["PreExpModel"], Literal["OldExpModel"], Literal["ExpModel"],
        Literal["CPR"], Literal["MHP"], Literal["HEP"], Literal["ABS"],
        Literal["CPB"], Literal["HPC"], Literal["CPJ"], Literal["CPY"],
        Literal["VPR"], Literal["PPV"], Literal["PSJ"], Literal["PSA"]
    rate : float
        Prepayment speed. Either rate or vector is required.
    vector : ~analyticsapi.models.Vector
    model_to_balloon : bool
        Selected model dictates prepayments until the balloon date, then
        security prepays in full.
    """

    type: Optional[
        Literal[
            "Model",
            "CurrentModel",
            "NewModel",
            "OldModel",
            "PreExpModel",
            "OldExpModel",
            "ExpModel",
            "CPR",
            "MHP",
            "HEP",
            "ABS",
            "CPB",
            "HPC",
            "CPJ",
            "CPY",
            "VPR",
            "PPV",
            "PSJ",
            "PSA",
        ]
    ] = rest_field(default=None)
    """Required. Is one of the following types: Literal[\"Model\"], Literal[\"CurrentModel\"],
     Literal[\"NewModel\"], Literal[\"OldModel\"], Literal[\"PreExpModel\"],
     Literal[\"OldExpModel\"], Literal[\"ExpModel\"], Literal[\"CPR\"], Literal[\"MHP\"],
     Literal[\"HEP\"], Literal[\"ABS\"], Literal[\"CPB\"], Literal[\"HPC\"], Literal[\"CPJ\"],
     Literal[\"CPY\"], Literal[\"VPR\"], Literal[\"PPV\"], Literal[\"PSJ\"], Literal[\"PSA\"]"""
    rate: Optional[float] = rest_field()
    """Prepayment speed. Either rate or vector is required."""
    vector: Optional["_models.Vector"] = rest_field()
    model_to_balloon: Optional[bool] = rest_field(name="modelToBalloon")
    """Selected model dictates prepayments until the balloon date, then security prepays in full."""

    @overload
    def __init__(
        self,
        *,
        type: Optional[
            Literal[
                "Model",
                "CurrentModel",
                "NewModel",
                "OldModel",
                "PreExpModel",
                "OldExpModel",
                "ExpModel",
                "CPR",
                "MHP",
                "HEP",
                "ABS",
                "CPB",
                "HPC",
                "CPJ",
                "CPY",
                "VPR",
                "PPV",
                "PSJ",
                "PSA",
            ]
        ] = None,
        rate: Optional[float] = None,
        vector: Optional["_models.Vector"] = None,
        model_to_balloon: Optional[bool] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ResultResponseBulkResultItem(_model_base.Model):
    """ResultResponseBulkResultItem.

    Attributes
    ----------
    meta : ~analyticsapi.models.BulkMeta
    data : ~analyticsapi.models.BulkResultItem
    results : list[~analyticsapi.models.BulkResultItem]
        The default value is None, needs to be assigned before using.
    errors : list[~analyticsapi.models.ApimError]
        The default value is None, needs to be assigned before using.
    summary : ~analyticsapi.models.Summary
    """

    meta: Optional["_models.BulkMeta"] = rest_field()
    data: Optional["_models.BulkResultItem"] = rest_field()
    results: Optional[List["_models.BulkResultItem"]] = rest_field()
    errors: Optional[List["_models.ApimError"]] = rest_field()
    summary: Optional["_models.Summary"] = rest_field()

    @overload
    def __init__(
        self,
        *,
        meta: Optional["_models.BulkMeta"] = None,
        data: Optional["_models.BulkResultItem"] = None,
        results: Optional[List["_models.BulkResultItem"]] = None,
        errors: Optional[List["_models.ApimError"]] = None,
        summary: Optional["_models.Summary"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class Results(_model_base.Model):
    """Internal instrument data structure. It's created in dictionary format, replicating the API's
    JSON structure response. In-depth documentation will be provided in future versions of SDK.

    """


class ReturnAttributionCurveTypeAndCurrency(_model_base.Model):
    """ReturnAttributionCurveTypeAndCurrency.

    Attributes
    ----------
    curve_type : str
    currency : str
    """

    curve_type: Optional[str] = rest_field(name="curveType")
    currency: Optional[str] = rest_field()

    @overload
    def __init__(
        self,
        *,
        curve_type: Optional[str] = None,
        currency: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ReturnAttributionGlobalSettings(_model_base.Model):
    """ReturnAttributionGlobalSettings.

    Attributes
    ----------
    begin : ~analyticsapi.models.ScenarioSettlement
    end : ~analyticsapi.models.ScenarioSettlement
    curve : ~analyticsapi.models.ReturnAttributionCurveTypeAndCurrency
    volatility : ~analyticsapi.models.Volatility
    """

    begin: Optional["_models.ScenarioSettlement"] = rest_field()
    end: Optional["_models.ScenarioSettlement"] = rest_field()
    curve: Optional["_models.ReturnAttributionCurveTypeAndCurrency"] = rest_field()
    volatility: Optional["_models.Volatility"] = rest_field()

    @overload
    def __init__(
        self,
        *,
        begin: Optional["_models.ScenarioSettlement"] = None,
        end: Optional["_models.ScenarioSettlement"] = None,
        curve: Optional["_models.ReturnAttributionCurveTypeAndCurrency"] = None,
        volatility: Optional["_models.Volatility"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ReturnAttributionInput(_model_base.Model):
    """ReturnAttributionInput.

    Attributes
    ----------
    identifier : str
    id_type : str or ~analyticsapi.models.IdTypeEnum
        Known values are: "SecurityIDEntry", "SecurityID", "CUSIP", "ISIN",
        "REGSISIN", "SEDOL", "Identifier", "ChinaInterbankCode",
        "ShanghaiExchangeCode", "ShenzhenExchangeCode", and "MXTickerID".
    tag : str
    begin_level : str
    end_level : str
    prepay_settings : ~analyticsapi.models.RestPrepaySettings
    """

    identifier: Optional[str] = rest_field()
    id_type: Optional[Union[str, "_models.IdTypeEnum"]] = rest_field(name="idType")
    """Known values are: \"SecurityIDEntry\", \"SecurityID\", \"CUSIP\", \"ISIN\", \"REGSISIN\",
     \"SEDOL\", \"Identifier\", \"ChinaInterbankCode\", \"ShanghaiExchangeCode\",
     \"ShenzhenExchangeCode\", and \"MXTickerID\"."""
    tag: Optional[str] = rest_field()
    begin_level: Optional[str] = rest_field(name="beginLevel")
    end_level: Optional[str] = rest_field(name="endLevel")
    prepay_settings: Optional["_models.RestPrepaySettings"] = rest_field(name="prepaySettings")

    @overload
    def __init__(
        self,
        *,
        identifier: Optional[str] = None,
        id_type: Optional[Union[str, "_models.IdTypeEnum"]] = None,
        tag: Optional[str] = None,
        begin_level: Optional[str] = None,
        end_level: Optional[str] = None,
        prepay_settings: Optional["_models.RestPrepaySettings"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ReturnAttributionRequest(_model_base.Model):
    """ReturnAttributionRequest.

    Attributes
    ----------
    global_settings : ~analyticsapi.models.ReturnAttributionGlobalSettings
    input : list[~analyticsapi.models.ReturnAttributionInput]
        The default value is None, needs to be assigned before using.
    """

    global_settings: Optional["_models.ReturnAttributionGlobalSettings"] = rest_field(name="globalSettings")
    input: Optional[List["_models.ReturnAttributionInput"]] = rest_field()

    @overload
    def __init__(
        self,
        *,
        global_settings: Optional["_models.ReturnAttributionGlobalSettings"] = None,
        input: Optional[List["_models.ReturnAttributionInput"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class RoundingDefinition(_model_base.Model):
    """An object that defines how rounding is applied.

    Attributes
    ----------
    decimal_places : int
        The decimal place the rounding applies to. Required.
    direction : str or ~analyticsapi.models.RoundingModeEnum
        The direction of the rounding. Known values are: "Ceiling", "Down",
        "Floor", "Near", and "Up".
    scale : int
        The scaling factor applied before the rounding operation.
    """

    decimal_places: int = rest_field(name="decimalPlaces")
    """The decimal place the rounding applies to. Required."""
    direction: Optional[Union[str, "_models.RoundingModeEnum"]] = rest_field()
    """The direction of the rounding. Known values are: \"Ceiling\", \"Down\", \"Floor\", \"Near\",
     and \"Up\"."""
    scale: Optional[int] = rest_field()
    """The scaling factor applied before the rounding operation."""

    @overload
    def __init__(
        self,
        *,
        decimal_places: int,
        direction: Optional[Union[str, "_models.RoundingModeEnum"]] = None,
        scale: Optional[int] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ScalarAndVector(_model_base.Model):
    """ScalarAndVector.

    Attributes
    ----------
    value : ~decimal.Decimal
    vector : list[~analyticsapi.models.TermAndValue]
        The default value is None, needs to be assigned before using.
    """

    value: Optional[decimal.Decimal] = rest_field()
    vector: Optional[List["_models.TermAndValue"]] = rest_field()

    @overload
    def __init__(
        self,
        *,
        value: Optional[decimal.Decimal] = None,
        vector: Optional[List["_models.TermAndValue"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ScalarAndVectorWithCollateral(_model_base.Model):
    """ScalarAndVectorWithCollateral.

    Attributes
    ----------
    value : ~decimal.Decimal
    vector : list[~analyticsapi.models.TermAndValue]
        The default value is None, needs to be assigned before using.
    """

    value: Optional[decimal.Decimal] = rest_field()
    vector: Optional[List["_models.TermAndValue"]] = rest_field()

    @overload
    def __init__(
        self,
        *,
        value: Optional[decimal.Decimal] = None,
        vector: Optional[List["_models.TermAndValue"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ScenAbsoluteCurvePoint(_model_base.Model):
    """ScenAbsoluteCurvePoint.

    Attributes
    ----------
    term : ~decimal.Decimal
    rate : ~decimal.Decimal
    spot_rate : ~decimal.Decimal
    forward_rate : ~decimal.Decimal
    discount_factor : ~decimal.Decimal
    """

    term: Optional[decimal.Decimal] = rest_field()
    rate: Optional[decimal.Decimal] = rest_field()
    spot_rate: Optional[decimal.Decimal] = rest_field(name="spotRate")
    forward_rate: Optional[decimal.Decimal] = rest_field(name="forwardRate")
    discount_factor: Optional[decimal.Decimal] = rest_field(name="discountFactor")

    @overload
    def __init__(
        self,
        *,
        term: Optional[decimal.Decimal] = None,
        rate: Optional[decimal.Decimal] = None,
        spot_rate: Optional[decimal.Decimal] = None,
        forward_rate: Optional[decimal.Decimal] = None,
        discount_factor: Optional[decimal.Decimal] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class Scenario(_model_base.Model):
    """Scenario.

    Attributes
    ----------
    scenario_id : str
        Identification code of the scenario.
    scenario_title : str
        Name of the scenario.
    timing : str
        Is one of the following types: Literal["Immediate"],
        Literal["Gradual"], Literal["AtHorizon"]
    reinvestment_rate : str
        Annualized rate at which scenario cash flows are reinvested. Default
        reinvestment rate is the 3-month rate on the OTR Treasury curve.
    definition : ~analyticsapi.models.ScenarioDefinition
    volatility : ~analyticsapi.models.ScenarioVolatility
    current_coupon_spread_change : float
    """

    scenario_id: Optional[str] = rest_field(name="scenarioID")
    """Identification code of the scenario."""
    scenario_title: Optional[str] = rest_field(name="scenarioTitle")
    """Name of the scenario."""
    timing: Optional[Literal["Immediate", "Gradual", "AtHorizon"]] = rest_field()
    """Is one of the following types: Literal[\"Immediate\"], Literal[\"Gradual\"],
     Literal[\"AtHorizon\"]"""
    reinvestment_rate: Optional[str] = rest_field(name="reinvestmentRate")
    """Annualized rate at which scenario cash flows are reinvested. Default reinvestment rate is the
     3-month rate on the OTR Treasury curve."""
    definition: Optional["_models.ScenarioDefinition"] = rest_field()
    volatility: Optional["_models.ScenarioVolatility"] = rest_field()
    current_coupon_spread_change: Optional[float] = rest_field(name="currentCouponSpreadChange")

    @overload
    def __init__(
        self,
        *,
        scenario_id: Optional[str] = None,
        scenario_title: Optional[str] = None,
        timing: Optional[Literal["Immediate", "Gradual", "AtHorizon"]] = None,
        reinvestment_rate: Optional[str] = None,
        definition: Optional["_models.ScenarioDefinition"] = None,
        volatility: Optional["_models.ScenarioVolatility"] = None,
        current_coupon_spread_change: Optional[float] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ScenarioCalcFloaterSettings(_model_base.Model):
    """ScenarioCalcFloaterSettings.

    Attributes
    ----------
    use_forward_index : bool
        Optional, if true floating coupon follows the index's forward path.
        Otherwise floating coupon is static.
    use_immediate_forward_shift : bool
        Optional. Spread over Forward Index. If used, do not use
        forwardIndexVector.
    """

    use_forward_index: Optional[bool] = rest_field(name="useForwardIndex")
    """Optional, if true floating coupon follows the index's forward path. Otherwise floating coupon
     is static."""
    use_immediate_forward_shift: Optional[bool] = rest_field(name="useImmediateForwardShift")
    """Optional. Spread over Forward Index. If used, do not use forwardIndexVector."""

    @overload
    def __init__(
        self,
        *,
        use_forward_index: Optional[bool] = None,
        use_immediate_forward_shift: Optional[bool] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ScenarioCalcGlobalSettings(_model_base.Model):  # pylint: disable=too-many-instance-attributes
    """ScenarioCalcGlobalSettings.

    Attributes
    ----------
    pricing_date : ~datetime.date
        A historical curve and term structure date. Only one date option can be
        used (pricingDate, usePreviousClose, useLiveData).
    use_previous_close : bool
        A date selection that uses the prior closing business day’s curve and
        volatility surface. Only one date option can be used (pricingDate,
        usePreviousClose, useLiveData).
    use_live_data : bool
        A date selection that will always use live curve data. Only one date
        option can be used (pricingDate, usePreviousClose, useLiveData).
    calc_horizon_effective_measures : bool
        Optional, if true, effective measures at the horizon date are
        calculated (e.g. effective duration, effective convexity, effective
        dv01, etc.).
    calc_horizon_option_measures : bool
        Optional, if true, option greeks at the horizon date are calculated.
    calc_scenario_cash_flow : bool
        Optional, if true, returns the scenario cash flows.
    calc_prepay_sensitivity : bool
        Optional, if true, triggers the calculation of current coupon OAS
        spread duration, turnover duration, prepay duration, primary-secondary
        spread duration, refi duration, and refi-elbow duration.
    current_coupon_rates : str
        Is one of the following types: Literal["MOATS"],
        Literal["SpreadToSwap"], Literal["SpreadToTreasury"],
        Literal["SpreadToSwapMeanReversion"], Literal["TreasuryMoats"]
    horizon_months : int
        The number of months in the scenario. Horizon months and/or horizon
        days are required.
    horizon_days : int
        The number of days in the scenario. Horizon months and/or horizon days
        are required.
    use_stochastic_hpa : bool
        Optional, for CRT and Non-Agency. If true, for OAS computations, for
        each rates path there will be an associated stochastic HPA path. If
        false, HPA will align with the agency approach.
    use_five_point_convexity : bool
        Optional, if true, convexity is calculated using 5-points, default is
        3-points.
    use_core_logic_group_model : bool
        Optional, for Non-Agency MBS. If true, prepayment and default
        assumptions are based at the group level, rather than the deal level.
    use_muni_non_call_curve : bool
        Optional, for Muni bonds. If true, pricing curve is constructed using
        non-callable securities only.
    use_muni_tax_settings : bool
        Optional, for Muni bonds. If true, analytics include certain tax
        considerations - de minimus rule, capital gains rate, and ordinary
        income rate.
    use_ois : bool
    use_non_qm_collateral : bool
        Optional, if true, Non-QM collateral is used for non-agency RMBS model
        calls, otherwise Alt-A collateral is used. This flag only applies to
        prepay type v97. If this flag is set to true, you must also set
        'coreLogicCollateral' to 'USE'.
    core_logic_collateral : str
        Optional, for Non-Agency. Enables model to be run using from CoreLogic
        collateral data. Is one of the following types: Literal["DEFAULT"],
        Literal["USE"], Literal["IGNORE"]
    """

    pricing_date: Optional[datetime.date] = rest_field(name="pricingDate")
    """A historical curve and term structure date. Only one date option can be used (pricingDate,
     usePreviousClose, useLiveData)."""
    use_previous_close: Optional[bool] = rest_field(name="usePreviousClose")
    """A date selection that uses the prior closing business day’s curve and volatility surface. Only
     one date option can be used (pricingDate, usePreviousClose, useLiveData)."""
    use_live_data: Optional[bool] = rest_field(name="useLiveData")
    """A date selection that will always use live curve data. Only one date option can be used
     (pricingDate, usePreviousClose, useLiveData)."""
    calc_horizon_effective_measures: Optional[bool] = rest_field(name="calcHorizonEffectiveMeasures")
    """Optional, if true, effective measures at the horizon date are calculated (e.g. effective
     duration, effective convexity, effective dv01, etc.)."""
    calc_horizon_option_measures: Optional[bool] = rest_field(name="calcHorizonOptionMeasures")
    """Optional, if true, option greeks at the horizon date are calculated."""
    calc_scenario_cash_flow: Optional[bool] = rest_field(name="calcScenarioCashFlow")
    """Optional, if true, returns the scenario cash flows."""
    calc_prepay_sensitivity: Optional[bool] = rest_field(name="calcPrepaySensitivity")
    """Optional, if true, triggers the calculation of current coupon OAS spread duration, turnover
     duration, prepay duration, primary-secondary spread duration, refi duration, and refi-elbow
     duration."""
    current_coupon_rates: Optional[
        Literal["MOATS", "SpreadToSwap", "SpreadToTreasury", "SpreadToSwapMeanReversion", "TreasuryMoats"]
    ] = rest_field(name="currentCouponRates")
    """Is one of the following types: Literal[\"MOATS\"], Literal[\"SpreadToSwap\"],
     Literal[\"SpreadToTreasury\"], Literal[\"SpreadToSwapMeanReversion\"],
     Literal[\"TreasuryMoats\"]"""
    horizon_months: Optional[int] = rest_field(name="horizonMonths")
    """The number of months in the scenario. Horizon months and/or horizon days are required."""
    horizon_days: Optional[int] = rest_field(name="horizonDays")
    """The number of days in the scenario. Horizon months and/or horizon days are required."""
    use_stochastic_hpa: Optional[bool] = rest_field(name="useStochasticHPA")
    """Optional, for CRT and Non-Agency. If true, for OAS computations, for each rates path there will
     be an associated stochastic HPA path. If false, HPA will align with the agency approach."""
    use_five_point_convexity: Optional[bool] = rest_field(name="useFivePointConvexity")
    """Optional, if true, convexity is calculated using 5-points, default is 3-points."""
    use_core_logic_group_model: Optional[bool] = rest_field(name="useCoreLogicGroupModel")
    """Optional, for Non-Agency MBS. If true, prepayment and default assumptions are based at the
     group level, rather than the deal level."""
    use_muni_non_call_curve: Optional[bool] = rest_field(name="useMuniNonCallCurve")
    """Optional, for Muni bonds. If true, pricing curve is constructed using non-callable securities
     only."""
    use_muni_tax_settings: Optional[bool] = rest_field(name="useMuniTaxSettings")
    """Optional, for Muni bonds. If true, analytics include certain tax considerations - de minimus
     rule, capital gains rate, and ordinary income rate."""
    use_ois: Optional[bool] = rest_field(name="useOIS")
    use_non_qm_collateral: Optional[bool] = rest_field(name="useNonQMCollateral")
    """Optional, if true, Non-QM collateral is used for non-agency RMBS model calls, otherwise Alt-A
     collateral is used. This flag only applies to prepay type v97. If this flag is set to true, you
     must also set 'coreLogicCollateral' to 'USE'."""
    core_logic_collateral: Optional[Literal["DEFAULT", "USE", "IGNORE"]] = rest_field(name="coreLogicCollateral")
    """Optional, for Non-Agency. Enables model to be run using from CoreLogic collateral data. Is one
     of the following types: Literal[\"DEFAULT\"], Literal[\"USE\"], Literal[\"IGNORE\"]"""

    @overload
    def __init__(
        self,
        *,
        pricing_date: Optional[datetime.date] = None,
        use_previous_close: Optional[bool] = None,
        use_live_data: Optional[bool] = None,
        calc_horizon_effective_measures: Optional[bool] = None,
        calc_horizon_option_measures: Optional[bool] = None,
        calc_scenario_cash_flow: Optional[bool] = None,
        calc_prepay_sensitivity: Optional[bool] = None,
        current_coupon_rates: Optional[
            Literal["MOATS", "SpreadToSwap", "SpreadToTreasury", "SpreadToSwapMeanReversion", "TreasuryMoats"]
        ] = None,
        horizon_months: Optional[int] = None,
        horizon_days: Optional[int] = None,
        use_stochastic_hpa: Optional[bool] = None,
        use_five_point_convexity: Optional[bool] = None,
        use_core_logic_group_model: Optional[bool] = None,
        use_muni_non_call_curve: Optional[bool] = None,
        use_muni_tax_settings: Optional[bool] = None,
        use_ois: Optional[bool] = None,
        use_non_qm_collateral: Optional[bool] = None,
        core_logic_collateral: Optional[Literal["DEFAULT", "USE", "IGNORE"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ScenarioCalcInput(_model_base.Model):  # pylint: disable=too-many-instance-attributes
    """ScenarioCalcInput.

    Attributes
    ----------
    identifier : str
        Security reference ID.
    id_type : str or ~analyticsapi.models.IdTypeEnum
        Known values are: "SecurityIDEntry", "SecurityID", "CUSIP", "ISIN",
        "REGSISIN", "SEDOL", "Identifier", "ChinaInterbankCode",
        "ShanghaiExchangeCode", "ShenzhenExchangeCode", and "MXTickerID".
    user_tag : str
        User provided tag - this will be returned in the response.
    curve : ~analyticsapi.models.CurveTypeAndCurrency
    volatility : ~analyticsapi.models.Volatility
    settlement_info : ~analyticsapi.models.SettlementInfo
    horizon_info : list[~analyticsapi.models.HorizonInfo]
        The default value is None, needs to be assigned before using.
    assume_call : bool
        Applicable for CMBS with a clean up call. If true, remaining balance is
        called once clean up call threshold is reached.
    horizon_py_method : str
        Is one of the following types: Literal["OAS Change"], Literal["Spread
        Change"], Literal["Price Change"], Literal["DM Change"], Literal["Libor
        Sprd Change"], Literal["TED Spread Change"], Literal["Stripped Spread
        Change"], Literal["Static Spread Change"], Literal["OAS"],
        Literal["Spread"], Literal["Yield"], Literal["Stripped Yield"],
        Literal["Price"], Literal["Discount Margin"], Literal["Sprd To Libor"],
        Literal["Stripped Spread"], Literal["Static Spread"],
        Literal["Annualized ROR"], Literal["Volatility"], Literal["Volatility
        Change"], Literal["Real Yield Beta"], Literal["Real Yield Change"],
        Literal["Real Spread"], Literal["Real Spread Change"],
        Literal["Inflation"], Literal["TED Spread"], Literal["Yield Curve
        Margin"], Literal["Yield Curve Margin Change"], Literal["Forward
        Yield"], Literal["Forward Yield Change"], Literal["MX Spread"],
        Literal["MX Spread Change"], Literal["Daily BPVol Change"],
        Literal["Rich Cheap"], Literal["OAS Pct Change"], Literal["Tax Adjusted
        OAS Change"]
    floater_settings : ~analyticsapi.models.ScenarioCalcFloaterSettings
    hecm_settings : ~analyticsapi.models.HecmSettings
    extra_settings : ~analyticsapi.models.ScenCalcExtraSettings
    user_instrument : ~analyticsapi.models.JsonRef
    modification : ~analyticsapi.models.JsonRef
    current_coupon_spread : ~analyticsapi.models.JsonRef
    props : dict[str, any]
    """

    identifier: Optional[str] = rest_field()
    """Security reference ID."""
    id_type: Optional[Union[str, "_models.IdTypeEnum"]] = rest_field(name="idType")
    """Known values are: \"SecurityIDEntry\", \"SecurityID\", \"CUSIP\", \"ISIN\", \"REGSISIN\",
     \"SEDOL\", \"Identifier\", \"ChinaInterbankCode\", \"ShanghaiExchangeCode\",
     \"ShenzhenExchangeCode\", and \"MXTickerID\"."""
    user_tag: Optional[str] = rest_field(name="userTag")
    """User provided tag - this will be returned in the response."""
    curve: Optional["_models.CurveTypeAndCurrency"] = rest_field()
    volatility: Optional["_models.Volatility"] = rest_field()
    settlement_info: Optional["_models.SettlementInfo"] = rest_field(name="settlementInfo")
    horizon_info: Optional[List["_models.HorizonInfo"]] = rest_field(name="horizonInfo")
    assume_call: Optional[bool] = rest_field(name="assumeCall")
    """Applicable for CMBS with a clean up call. If true, remaining balance is called once clean up
     call threshold is reached."""
    horizon_py_method: Optional[
        Literal[
            "OAS Change",
            "Spread Change",
            "Price Change",
            "DM Change",
            "Libor Sprd Change",
            "TED Spread Change",
            "Stripped Spread Change",
            "Static Spread Change",
            "OAS",
            "Spread",
            "Yield",
            "Stripped Yield",
            "Price",
            "Discount Margin",
            "Sprd To Libor",
            "Stripped Spread",
            "Static Spread",
            "Annualized ROR",
            "Volatility",
            "Volatility Change",
            "Real Yield Beta",
            "Real Yield Change",
            "Real Spread",
            "Real Spread Change",
            "Inflation",
            "TED Spread",
            "Yield Curve Margin",
            "Yield Curve Margin Change",
            "Forward Yield",
            "Forward Yield Change",
            "MX Spread",
            "MX Spread Change",
            "Daily BPVol Change",
            "Rich Cheap",
            "OAS Pct Change",
            "Tax Adjusted OAS Change",
        ]
    ] = rest_field(name="horizonPYMethod")
    """Is one of the following types: Literal[\"OAS Change\"], Literal[\"Spread Change\"],
     Literal[\"Price Change\"], Literal[\"DM Change\"], Literal[\"Libor Sprd Change\"],
     Literal[\"TED Spread Change\"], Literal[\"Stripped Spread Change\"], Literal[\"Static Spread
     Change\"], Literal[\"OAS\"], Literal[\"Spread\"], Literal[\"Yield\"], Literal[\"Stripped
     Yield\"], Literal[\"Price\"], Literal[\"Discount Margin\"], Literal[\"Sprd To Libor\"],
     Literal[\"Stripped Spread\"], Literal[\"Static Spread\"], Literal[\"Annualized ROR\"],
     Literal[\"Volatility\"], Literal[\"Volatility Change\"], Literal[\"Real Yield Beta\"],
     Literal[\"Real Yield Change\"], Literal[\"Real Spread\"], Literal[\"Real Spread Change\"],
     Literal[\"Inflation\"], Literal[\"TED Spread\"], Literal[\"Yield Curve Margin\"],
     Literal[\"Yield Curve Margin Change\"], Literal[\"Forward Yield\"], Literal[\"Forward Yield
     Change\"], Literal[\"MX Spread\"], Literal[\"MX Spread Change\"], Literal[\"Daily BPVol
     Change\"], Literal[\"Rich Cheap\"], Literal[\"OAS Pct Change\"], Literal[\"Tax Adjusted OAS
     Change\"]"""
    floater_settings: Optional["_models.ScenarioCalcFloaterSettings"] = rest_field(name="floaterSettings")
    hecm_settings: Optional["_models.HecmSettings"] = rest_field(name="hecmSettings")
    extra_settings: Optional["_models.ScenCalcExtraSettings"] = rest_field(name="extraSettings")
    user_instrument: Optional["_models.JsonRef"] = rest_field(name="userInstrument")
    modification: Optional["_models.JsonRef"] = rest_field()
    current_coupon_spread: Optional["_models.JsonRef"] = rest_field(name="currentCouponSpread")
    props: Optional[Dict[str, Any]] = rest_field()

    @overload
    def __init__(
        self,
        *,
        identifier: Optional[str] = None,
        id_type: Optional[Union[str, "_models.IdTypeEnum"]] = None,
        user_tag: Optional[str] = None,
        curve: Optional["_models.CurveTypeAndCurrency"] = None,
        volatility: Optional["_models.Volatility"] = None,
        settlement_info: Optional["_models.SettlementInfo"] = None,
        horizon_info: Optional[List["_models.HorizonInfo"]] = None,
        assume_call: Optional[bool] = None,
        horizon_py_method: Optional[
            Literal[
                "OAS Change",
                "Spread Change",
                "Price Change",
                "DM Change",
                "Libor Sprd Change",
                "TED Spread Change",
                "Stripped Spread Change",
                "Static Spread Change",
                "OAS",
                "Spread",
                "Yield",
                "Stripped Yield",
                "Price",
                "Discount Margin",
                "Sprd To Libor",
                "Stripped Spread",
                "Static Spread",
                "Annualized ROR",
                "Volatility",
                "Volatility Change",
                "Real Yield Beta",
                "Real Yield Change",
                "Real Spread",
                "Real Spread Change",
                "Inflation",
                "TED Spread",
                "Yield Curve Margin",
                "Yield Curve Margin Change",
                "Forward Yield",
                "Forward Yield Change",
                "MX Spread",
                "MX Spread Change",
                "Daily BPVol Change",
                "Rich Cheap",
                "OAS Pct Change",
                "Tax Adjusted OAS Change",
            ]
        ] = None,
        floater_settings: Optional["_models.ScenarioCalcFloaterSettings"] = None,
        hecm_settings: Optional["_models.HecmSettings"] = None,
        extra_settings: Optional["_models.ScenCalcExtraSettings"] = None,
        user_instrument: Optional["_models.JsonRef"] = None,
        modification: Optional["_models.JsonRef"] = None,
        current_coupon_spread: Optional["_models.JsonRef"] = None,
        props: Optional[Dict[str, Any]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ScenarioCalcRequest(_model_base.Model):
    """ScenarioCalcRequest.

    Attributes
    ----------
    global_settings : ~analyticsapi.models.ScenarioCalcGlobalSettings
    keywords : list[str]
        The default value is None, needs to be assigned before using.
    scenarios : list[~analyticsapi.models.Scenario]
        The default value is None, needs to be assigned before using.
    input : list[~analyticsapi.models.ScenarioCalcInput]
        The default value is None, needs to be assigned before using.
    """

    global_settings: Optional["_models.ScenarioCalcGlobalSettings"] = rest_field(name="globalSettings")
    keywords: Optional[List[str]] = rest_field()
    scenarios: Optional[List["_models.Scenario"]] = rest_field()
    input: Optional[List["_models.ScenarioCalcInput"]] = rest_field()

    @overload
    def __init__(
        self,
        *,
        global_settings: Optional["_models.ScenarioCalcGlobalSettings"] = None,
        keywords: Optional[List[str]] = None,
        scenarios: Optional[List["_models.Scenario"]] = None,
        input: Optional[List["_models.ScenarioCalcInput"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ScenarioDefinition(_model_base.Model):
    """ScenarioDefinition.

    Attributes
    ----------
    system_scenario : ~analyticsapi.models.SystemScenario
        User can either use a systemScenario or create a userScenario.
    user_scenario : ~analyticsapi.models.UserScenario
    """

    system_scenario: Optional["_models.SystemScenario"] = rest_field(name="systemScenario")
    """User can either use a systemScenario or create a userScenario."""
    user_scenario: Optional["_models.UserScenario"] = rest_field(name="userScenario")

    @overload
    def __init__(
        self,
        *,
        system_scenario: Optional["_models.SystemScenario"] = None,
        user_scenario: Optional["_models.UserScenario"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ScenarioSettlement(_model_base.Model):
    """ScenarioSettlement.

    Attributes
    ----------
    holding_date : ~datetime.date
    settlement_type : str
    settlement_date : ~datetime.date
        Optional. If settlementType is CUSTOM, user needs to input
        settlementDate.
    """

    holding_date: Optional[datetime.date] = rest_field(name="holdingDate")
    settlement_type: Optional[str] = rest_field(name="settlementType")
    settlement_date: Optional[datetime.date] = rest_field(name="settlementDate")
    """Optional. If settlementType is CUSTOM, user needs to input settlementDate."""

    @overload
    def __init__(
        self,
        *,
        holding_date: Optional[datetime.date] = None,
        settlement_type: Optional[str] = None,
        settlement_date: Optional[datetime.date] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ScenarioVolatility(_model_base.Model):
    """ScenarioVolatility.

    Attributes
    ----------
    term_unit : str
        Is either a Literal["MONTH"] type or a Literal["YEAR"] type.
    value_type : str
        Is either a Literal["ABS"] type or a Literal["REL"] type.
    parallel_shift : ~decimal.Decimal
        Shock amount to be applied to the entire volatility surface.
    swaption_volatility : ~analyticsapi.models.SwaptionVolatility
    cap_volatility : ~analyticsapi.models.CapVolatility
    """

    term_unit: Optional[Literal["MONTH", "YEAR"]] = rest_field(name="termUnit")
    """Is either a Literal[\"MONTH\"] type or a Literal[\"YEAR\"] type."""
    value_type: Optional[Literal["ABS", "REL"]] = rest_field(name="valueType")
    """Is either a Literal[\"ABS\"] type or a Literal[\"REL\"] type."""
    parallel_shift: Optional[decimal.Decimal] = rest_field(name="parallelShift")
    """Shock amount to be applied to the entire volatility surface."""
    swaption_volatility: Optional["_models.SwaptionVolatility"] = rest_field(name="swaptionVolatility")
    cap_volatility: Optional["_models.CapVolatility"] = rest_field(name="capVolatility")

    @overload
    def __init__(
        self,
        *,
        term_unit: Optional[Literal["MONTH", "YEAR"]] = None,
        value_type: Optional[Literal["ABS", "REL"]] = None,
        parallel_shift: Optional[decimal.Decimal] = None,
        swaption_volatility: Optional["_models.SwaptionVolatility"] = None,
        cap_volatility: Optional["_models.CapVolatility"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ScenCalcExtraSettings(_model_base.Model):
    """Optional additional pricing settings.

    Attributes
    ----------
    include_partials : bool
        Partial durations are calculated.
    partials : ~analyticsapi.models.Partials
        Optional, and only to be used if includePartials = true.
    """

    include_partials: Optional[bool] = rest_field(name="includePartials")
    """Partial durations are calculated."""
    partials: Optional["_models.Partials"] = rest_field()
    """Optional, and only to be used if includePartials = true."""

    @overload
    def __init__(
        self,
        *,
        include_partials: Optional[bool] = None,
        partials: Optional["_models.Partials"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ScheduleDefinition(_model_base.Model):
    """An object that defines a date schedule.
    This common model is used in financial instruments where a structured sequence of dates is
    required for financial calculations or contract terms,
    for example, to specify interest periods, amortization dates, or the sequence of dates in the
    fixing period of an Asian option.

    Attributes
    ----------
    start_date : ~analyticsapi.models.Date
        An object that contains properties to define and adjust the start date
        of the schedule. If not defined, the schedule is spot-starting, and the
        default start date is determined based on market conventions.
    end_date : ~analyticsapi.models.Date
        An object that contains properties to define and adjust the end date of
        the schedule. Required.
    first_regular_date : ~analyticsapi.models.Date
        An object that contains properties to define and adjust the first
        regular date of the schedule.
    last_regular_date : ~analyticsapi.models.Date
        An object that contains properties to define and adjust the last
        regular date of the schedule.
    stub_rule : str or ~analyticsapi.models.StubRuleEnum
        The rule that specifies whether the first or last period on the
        schedule is unregular. Known values are: "LongFirst", "LongLast",
        "ShortFirst", and "ShortLast".
    frequency : str or ~analyticsapi.models.FrequencyEnum
        The frequency of the dates generated in the regular period. Known
        values are: "Annual", "SemiAnnual", "Quarterly", "Monthly",
        "BiMonthly", "Everyday", "EveryWorkingDay", "Every7Days",
        "Every14Days", "Every28Days", "Every30Days", "Every90Days",
        "Every91Days", "Every92Days", "Every93Days", "Every4Months",
        "Every180Days", "Every182Days", "Every183Days", "Every184Days",
        "Every364Days", "Every365Days", "R2", "R4", "Zero", and "Scheduled".
    business_day_adjustment : ~analyticsapi.models.BusinessDayAdjustmentDefinition
        An object that defines the business day adjustment convention.
    roll_convention : str or ~analyticsapi.models.EndOfMonthConvention
        The method to adjust a date when it falls at the end of the month.
        Known values are: "Last", "Same", "Last28", "Same28", and "Same1".
    """

    start_date: Optional["_models.Date"] = rest_field(name="startDate")
    """An object that contains properties to define and adjust the start date of the schedule. If not
     defined, the schedule is spot-starting, and the default start date is determined based on
     market conventions."""
    end_date: "_models.Date" = rest_field(name="endDate")
    """An object that contains properties to define and adjust the end date of the schedule. Required."""
    first_regular_date: Optional["_models.Date"] = rest_field(name="firstRegularDate")
    """An object that contains properties to define and adjust the first regular date of the schedule."""
    last_regular_date: Optional["_models.Date"] = rest_field(name="lastRegularDate")
    """An object that contains properties to define and adjust the last regular date of the schedule."""
    stub_rule: Optional[Union[str, "_models.StubRuleEnum"]] = rest_field(name="stubRule")
    """The rule that specifies whether the first or last period on the schedule is unregular. Known
     values are: \"LongFirst\", \"LongLast\", \"ShortFirst\", and \"ShortLast\"."""
    frequency: Optional[Union[str, "_models.FrequencyEnum"]] = rest_field()
    """The frequency of the dates generated in the regular period. Known values are: \"Annual\",
     \"SemiAnnual\", \"Quarterly\", \"Monthly\", \"BiMonthly\", \"Everyday\", \"EveryWorkingDay\",
     \"Every7Days\", \"Every14Days\", \"Every28Days\", \"Every30Days\", \"Every90Days\",
     \"Every91Days\", \"Every92Days\", \"Every93Days\", \"Every4Months\", \"Every180Days\",
     \"Every182Days\", \"Every183Days\", \"Every184Days\", \"Every364Days\", \"Every365Days\",
     \"R2\", \"R4\", \"Zero\", and \"Scheduled\"."""
    business_day_adjustment: Optional["_models.BusinessDayAdjustmentDefinition"] = rest_field(
        name="businessDayAdjustment"
    )
    """An object that defines the business day adjustment convention."""
    roll_convention: Optional[Union[str, "_models.EndOfMonthConvention"]] = rest_field(name="rollConvention")
    """The method to adjust a date when it falls at the end of the month. Known values are: \"Last\",
     \"Same\", \"Last28\", \"Same28\", and \"Same1\"."""

    @overload
    def __init__(
        self,
        *,
        end_date: "_models.Date",
        start_date: Optional["_models.Date"] = None,
        first_regular_date: Optional["_models.Date"] = None,
        last_regular_date: Optional["_models.Date"] = None,
        stub_rule: Optional[Union[str, "_models.StubRuleEnum"]] = None,
        frequency: Optional[Union[str, "_models.FrequencyEnum"]] = None,
        business_day_adjustment: Optional["_models.BusinessDayAdjustmentDefinition"] = None,
        roll_convention: Optional[Union[str, "_models.EndOfMonthConvention"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ScheduleItem(_model_base.Model):
    """ScheduleItem.

    Attributes
    ----------
    date : ~datetime.date
    value : ~decimal.Decimal
    """

    date: Optional[datetime.date] = rest_field()
    value: Optional[decimal.Decimal] = rest_field()

    @overload
    def __init__(
        self,
        *,
        date: Optional[datetime.date] = None,
        value: Optional[decimal.Decimal] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class SensitivityShocks(_model_base.Model):
    """SensitivityShocks.

    Attributes
    ----------
    effective_duration : float
    spread : float
    prepay : float
    current_coupon_spreads : float
    prepay_model_elbow : float
    prepay_model_refi : float
    hpa : float
    """

    effective_duration: Optional[float] = rest_field(name="effectiveDuration")
    spread: Optional[float] = rest_field()
    prepay: Optional[float] = rest_field()
    current_coupon_spreads: Optional[float] = rest_field(name="currentCouponSpreads")
    prepay_model_elbow: Optional[float] = rest_field(name="prepayModelElbow")
    prepay_model_refi: Optional[float] = rest_field(name="prepayModelRefi")
    hpa: Optional[float] = rest_field()

    @overload
    def __init__(
        self,
        *,
        effective_duration: Optional[float] = None,
        spread: Optional[float] = None,
        prepay: Optional[float] = None,
        current_coupon_spreads: Optional[float] = None,
        prepay_model_elbow: Optional[float] = None,
        prepay_model_refi: Optional[float] = None,
        hpa: Optional[float] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ServiceError(_model_base.Model):
    """An object that contains the information in case of a blocking error in calculation.

    Attributes
    ----------
    id : str
        The identifier of the error. Required.
    code : str
        The code of the error. Required.
    message : str
        The message in case of a blocking error in calculation. Required.
    status : str
        The status of the error.
    errors : list[~analyticsapi.models.InnerError]
        An array of objects that contains the detailed information in case of a
        blocking error in calculation.  The default value is None, needs to be
        assigned before using.
    """

    id: str = rest_field()
    """The identifier of the error. Required."""
    code: str = rest_field()
    """The code of the error. Required."""
    message: str = rest_field()
    """The message in case of a blocking error in calculation. Required."""
    status: Optional[str] = rest_field()
    """The status of the error."""
    errors: Optional[List["_models.InnerError"]] = rest_field()
    """An array of objects that contains the detailed information in case of a blocking error in
     calculation."""

    @overload
    def __init__(
        self,
        *,
        id: str,  # pylint: disable=redefined-builtin
        code: str,
        message: str,
        status: Optional[str] = None,
        errors: Optional[List["_models.InnerError"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ServiceErrorResponse(_model_base.Model):
    """The error information returned in response.

    Attributes
    ----------
    error : ~analyticsapi.models.ServiceError
        An object that contains the information in case of a blocking error in
        calculation. Required.
    """

    error: "_models.ServiceError" = rest_field()
    """An object that contains the information in case of a blocking error in calculation. Required."""

    @overload
    def __init__(
        self,
        error: "_models.ServiceError",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["error"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class SettlementDefinition(_model_base.Model):
    """An object that defines the settlement settings.

    Attributes
    ----------
    type : str or ~analyticsapi.models.SettlementType
        The settlement type that indicates whether the payment is made by
        exchanging a cash amount or a physical asset. Known values are: "Cash"
        and "Physical".
    currency : str
        The currency in which the payment is settled. The value is expressed in
        ISO 4217 alphabetical format (e.g., 'USD').
    delivery_date : ~analyticsapi.models.Date
        An object that defines the delivery date.
    """

    type: Optional[Union[str, "_models.SettlementType"]] = rest_field(default="None")
    """The settlement type that indicates whether the payment is made by exchanging a cash amount or a
     physical asset. Known values are: \"Cash\" and \"Physical\"."""
    currency: Optional[str] = rest_field()
    """The currency in which the payment is settled. The value is expressed in ISO 4217 alphabetical
     format (e.g., 'USD')."""
    delivery_date: Optional["_models.Date"] = rest_field(name="deliveryDate")
    """An object that defines the delivery date."""

    @overload
    def __init__(
        self,
        *,
        type: Optional[Union[str, "_models.SettlementType"]] = None,
        currency: Optional[str] = None,
        delivery_date: Optional["_models.Date"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class SettlementInfo(_model_base.Model):
    """SettlementInfo.

    Attributes
    ----------
    level : str
        Settlement input price for the security. Input can be a price, yield,
        spread, OAS, etc. See quick card for a list of options.
    settlement_type : str
        Is one of the following types: Literal["MARKET"], Literal["INDEX"],
        Literal["CUSTOM"]
    settlement_date : ~datetime.date
        Optional. If settlementType is CUSTOM, user can choose between
        settlementDate and customSettlement. Recommend using settlementDate.
    custom_settlement : str
        Optional. If settlementType is CUSTOM, user can choose between
        settlementDate and customSettlement. Example of customSettlement (T +
        2), where T is the pricing date. Recommend using settlementDate.
    prepay : ~analyticsapi.models.RestPrepaySettings
    loss_settings : ~analyticsapi.models.LossSettings
    cmbs_scenario : ~analyticsapi.models.PricingScenario
    """

    level: Optional[str] = rest_field()
    """Settlement input price for the security. Input can be a price, yield, spread, OAS, etc. See
     quick card for a list of options."""
    settlement_type: Optional[Literal["MARKET", "INDEX", "CUSTOM"]] = rest_field(name="settlementType")
    """Is one of the following types: Literal[\"MARKET\"], Literal[\"INDEX\"], Literal[\"CUSTOM\"]"""
    settlement_date: Optional[datetime.date] = rest_field(name="settlementDate")
    """Optional. If settlementType is CUSTOM, user can choose between settlementDate and
     customSettlement. Recommend using settlementDate."""
    custom_settlement: Optional[str] = rest_field(name="customSettlement")
    """Optional. If settlementType is CUSTOM, user can choose between settlementDate and
     customSettlement. Example of customSettlement (T + 2), where T is the pricing date. Recommend
     using settlementDate."""
    prepay: Optional["_models.RestPrepaySettings"] = rest_field()
    loss_settings: Optional["_models.LossSettings"] = rest_field(name="lossSettings")
    cmbs_scenario: Optional["_models.PricingScenario"] = rest_field(name="cmbsScenario")

    @overload
    def __init__(
        self,
        *,
        level: Optional[str] = None,
        settlement_type: Optional[Literal["MARKET", "INDEX", "CUSTOM"]] = None,
        settlement_date: Optional[datetime.date] = None,
        custom_settlement: Optional[str] = None,
        prepay: Optional["_models.RestPrepaySettings"] = None,
        loss_settings: Optional["_models.LossSettings"] = None,
        cmbs_scenario: Optional["_models.PricingScenario"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class SingleBarrierOtcOptionTemplate(InstrumentTemplateDefinition, discriminator="SingleBarrierOtcOption"):
    """SingleBarrierOtcOptionTemplate.

    Attributes
    ----------
    instrument_type : str or ~analyticsapi.models.SINGLE_BARRIER_OTC_OPTION
        Required. Single Barrier OTC Option contract.
    template : ~analyticsapi.models.OptionDefinition
        Required.
    """

    instrument_type: Literal[InstrumentTemplateTypeEnum.SINGLE_BARRIER_OTC_OPTION] = rest_discriminator(name="instrumentType")  # type: ignore
    """Required. Single Barrier OTC Option contract."""
    template: "_models.OptionDefinition" = rest_field()
    """Required."""

    @overload
    def __init__(
        self,
        template: "_models.OptionDefinition",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, instrument_type=InstrumentTemplateTypeEnum.SINGLE_BARRIER_OTC_OPTION, **kwargs)


class SingleBinaryOtcOptionTemplate(InstrumentTemplateDefinition, discriminator="SingleBinaryOtcOption"):
    """SingleBinaryOtcOptionTemplate.

    Attributes
    ----------
    instrument_type : str or ~analyticsapi.models.SINGLE_BINARY_OTC_OPTION
        Required. Single Binary OTC Option contract.
    template : ~analyticsapi.models.OptionDefinition
        Required.
    """

    instrument_type: Literal[InstrumentTemplateTypeEnum.SINGLE_BINARY_OTC_OPTION] = rest_discriminator(name="instrumentType")  # type: ignore
    """Required. Single Binary OTC Option contract."""
    template: "_models.OptionDefinition" = rest_field()
    """Required."""

    @overload
    def __init__(
        self,
        template: "_models.OptionDefinition",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, instrument_type=InstrumentTemplateTypeEnum.SINGLE_BINARY_OTC_OPTION, **kwargs)


class SolvingMethod(_model_base.Model):
    """An object that contains properties used to apply the solving method.

    Attributes
    ----------
    name : str or ~analyticsapi.models.SolvingMethodEnum
        The method used to select the variable parameter value. Required. Known
        values are: "BiSection", "Brent", and "Secant".
    lower_bound : float
        The lower bound of the range of possible values of the variable
        parameter. Not applicable to the 'Secant' method. Required.
    upper_bound : float
        The upper bound of the range of possible values of the variable
        parameter. Not applicable to the 'Secant' method. Required.
    guess : float
        An initial value for the variable parameter used in computation. It is
        applicable to 'Secant' method only.
    """

    name: Union[str, "_models.SolvingMethodEnum"] = rest_field()
    """The method used to select the variable parameter value. Required. Known values are:
     \"BiSection\", \"Brent\", and \"Secant\"."""
    lower_bound: float = rest_field(name="lowerBound")
    """The lower bound of the range of possible values of the variable parameter. Not applicable to
     the 'Secant' method. Required."""
    upper_bound: float = rest_field(name="upperBound")
    """The upper bound of the range of possible values of the variable parameter. Not applicable to
     the 'Secant' method. Required."""
    guess: Optional[float] = rest_field()
    """An initial value for the variable parameter used in computation. It is applicable to 'Secant'
     method only."""

    @overload
    def __init__(
        self,
        *,
        name: Union[str, "_models.SolvingMethodEnum"],
        lower_bound: float,
        upper_bound: float,
        guess: Optional[float] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class SolvingResult(_model_base.Model):
    """An object that contains the swap solving result.

    Attributes
    ----------
    result : float
        The solution result for the variable value that gives the set target
        value. Required.
    method : ~analyticsapi.models.SolvingMethod
        An object that contains properties used to apply the solving method.
        Required.
    """

    result: float = rest_field()
    """The solution result for the variable value that gives the set target value. Required."""
    method: "_models.SolvingMethod" = rest_field()
    """An object that contains properties used to apply the solving method. Required."""

    @overload
    def __init__(
        self,
        *,
        result: float,
        method: "_models.SolvingMethod",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class SqlSettings(_model_base.Model):
    """SqlSettings.

    Attributes
    ----------
    table_name : str
    insert_tran_limit : int
    insert_row_limit : int
    primary_key : list[str]
        The default value is None, needs to be assigned before using.
    create_table : bool
    drop_table : bool
    multi_value_insert_enabled : bool
    default_id : bool
    pk_list_as_string : str
    """

    table_name: Optional[str] = rest_field(name="tableName")
    insert_tran_limit: Optional[int] = rest_field(name="insertTranLimit")
    insert_row_limit: Optional[int] = rest_field(name="insertRowLimit")
    primary_key: Optional[List[str]] = rest_field(name="primaryKey")
    create_table: Optional[bool] = rest_field(name="createTable")
    drop_table: Optional[bool] = rest_field(name="dropTable")
    multi_value_insert_enabled: Optional[bool] = rest_field(name="multiValueInsertEnabled")
    default_id: Optional[bool] = rest_field(name="defaultId")
    pk_list_as_string: Optional[str] = rest_field(name="pkListAsString")

    @overload
    def __init__(
        self,
        *,
        table_name: Optional[str] = None,
        insert_tran_limit: Optional[int] = None,
        insert_row_limit: Optional[int] = None,
        primary_key: Optional[List[str]] = None,
        create_table: Optional[bool] = None,
        drop_table: Optional[bool] = None,
        multi_value_insert_enabled: Optional[bool] = None,
        default_id: Optional[bool] = None,
        pk_list_as_string: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class StateHomePriceAppreciation(_model_base.Model):
    """StateHomePriceAppreciation.

    Attributes
    ----------
    hpa_state : str
        Is one of the following types: Literal["AL"], Literal["AK"],
        Literal["AZ"], Literal["AR"], Literal["CA"], Literal["CO"],
        Literal["CT"], Literal["DE"], Literal["FL"], Literal["GA"],
        Literal["HI"], Literal["ID"], Literal["IL"], Literal["IN"],
        Literal["IA"], Literal["KS"], Literal["KY"], Literal["LA"],
        Literal["ME"], Literal["MD"], Literal["MA"], Literal["MI"],
        Literal["MN"], Literal["MS"], Literal["MO"], Literal["MT"],
        Literal["NE"], Literal["NV"], Literal["NH"], Literal["NJ"],
        Literal["NM"], Literal["NY"], Literal["NC"], Literal["ND"],
        Literal["OH"], Literal["OK"], Literal["OR"], Literal["PA"],
        Literal["RI"], Literal["SC"], Literal["SD"], Literal["TN"],
        Literal["TX"], Literal["UT"], Literal["VT"], Literal["VA"],
        Literal["WA"], Literal["WV"], Literal["WI"], Literal["WY"]
    home_price_appreciation : ~analyticsapi.models.InterpolationTypeAndVector
    """

    hpa_state: Optional[
        Literal[
            "AL",
            "AK",
            "AZ",
            "AR",
            "CA",
            "CO",
            "CT",
            "DE",
            "FL",
            "GA",
            "HI",
            "ID",
            "IL",
            "IN",
            "IA",
            "KS",
            "KY",
            "LA",
            "ME",
            "MD",
            "MA",
            "MI",
            "MN",
            "MS",
            "MO",
            "MT",
            "NE",
            "NV",
            "NH",
            "NJ",
            "NM",
            "NY",
            "NC",
            "ND",
            "OH",
            "OK",
            "OR",
            "PA",
            "RI",
            "SC",
            "SD",
            "TN",
            "TX",
            "UT",
            "VT",
            "VA",
            "WA",
            "WV",
            "WI",
            "WY",
        ]
    ] = rest_field(name="hpaState")
    """Is one of the following types: Literal[\"AL\"], Literal[\"AK\"], Literal[\"AZ\"],
     Literal[\"AR\"], Literal[\"CA\"], Literal[\"CO\"], Literal[\"CT\"], Literal[\"DE\"],
     Literal[\"FL\"], Literal[\"GA\"], Literal[\"HI\"], Literal[\"ID\"], Literal[\"IL\"],
     Literal[\"IN\"], Literal[\"IA\"], Literal[\"KS\"], Literal[\"KY\"], Literal[\"LA\"],
     Literal[\"ME\"], Literal[\"MD\"], Literal[\"MA\"], Literal[\"MI\"], Literal[\"MN\"],
     Literal[\"MS\"], Literal[\"MO\"], Literal[\"MT\"], Literal[\"NE\"], Literal[\"NV\"],
     Literal[\"NH\"], Literal[\"NJ\"], Literal[\"NM\"], Literal[\"NY\"], Literal[\"NC\"],
     Literal[\"ND\"], Literal[\"OH\"], Literal[\"OK\"], Literal[\"OR\"], Literal[\"PA\"],
     Literal[\"RI\"], Literal[\"SC\"], Literal[\"SD\"], Literal[\"TN\"], Literal[\"TX\"],
     Literal[\"UT\"], Literal[\"VT\"], Literal[\"VA\"], Literal[\"WA\"], Literal[\"WV\"],
     Literal[\"WI\"], Literal[\"WY\"]"""
    home_price_appreciation: Optional["_models.InterpolationTypeAndVector"] = rest_field(name="homePriceAppreciation")

    @overload
    def __init__(
        self,
        *,
        hpa_state: Optional[
            Literal[
                "AL",
                "AK",
                "AZ",
                "AR",
                "CA",
                "CO",
                "CT",
                "DE",
                "FL",
                "GA",
                "HI",
                "ID",
                "IL",
                "IN",
                "IA",
                "KS",
                "KY",
                "LA",
                "ME",
                "MD",
                "MA",
                "MI",
                "MN",
                "MS",
                "MO",
                "MT",
                "NE",
                "NV",
                "NH",
                "NJ",
                "NM",
                "NY",
                "NC",
                "ND",
                "OH",
                "OK",
                "OR",
                "PA",
                "RI",
                "SC",
                "SD",
                "TN",
                "TX",
                "UT",
                "VT",
                "VA",
                "WA",
                "WV",
                "WI",
                "WY",
            ]
        ] = None,
        home_price_appreciation: Optional["_models.InterpolationTypeAndVector"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class StepRateDefinition(InterestRateDefinition, discriminator="StepRate"):
    """An object that defines a stepped rate.

    Attributes
    ----------
    interest_rate_type : str or ~analyticsapi.models.STEP_RATE
        The type of interest rate that is defined as a stepped rate. Required.
        A variable (step) interest rate schedule.
    schedule : list[~analyticsapi.models.DatedRate]
        An array of objects that represens the sequence of fixed rates.
        Required.  The default value is None, needs to be assigned before
        using.
    """

    interest_rate_type: Literal[InterestRateTypeEnum.STEP_RATE] = rest_discriminator(name="interestRateType")  # type: ignore
    """The type of interest rate that is defined as a stepped rate. Required. A variable (step)
     interest rate schedule."""
    schedule: List["_models.DatedRate"] = rest_field()
    """An array of objects that represens the sequence of fixed rates. Required."""

    @overload
    def __init__(
        self,
        schedule: List["_models.DatedRate"],
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, interest_rate_type=InterestRateTypeEnum.STEP_RATE, **kwargs)


class StructureNote(_model_base.Model):
    """StructureNote.

    Attributes
    ----------
    pricing : str
        Additional settings for Structured Notes. Is either a
        Literal["DISCOUNTING"] type or a Literal["ASSETSWAP"] type.
    callable_zero_pricing : str
        Is one of the following types: Literal["NETPROCEED"],
        Literal["ACCRETING"], Literal["DYNAMIC"]
    """

    pricing: Optional[Literal["DISCOUNTING", "ASSETSWAP"]] = rest_field()
    """Additional settings for Structured Notes. Is either a Literal[\"DISCOUNTING\"] type or a
     Literal[\"ASSETSWAP\"] type."""
    callable_zero_pricing: Optional[Literal["NETPROCEED", "ACCRETING", "DYNAMIC"]] = rest_field(
        name="callableZeroPricing"
    )
    """Is one of the following types: Literal[\"NETPROCEED\"], Literal[\"ACCRETING\"],
     Literal[\"DYNAMIC\"]"""

    @overload
    def __init__(
        self,
        *,
        pricing: Optional[Literal["DISCOUNTING", "ASSETSWAP"]] = None,
        callable_zero_pricing: Optional[Literal["NETPROCEED", "ACCRETING", "DYNAMIC"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class StubIndexReferences(_model_base.Model):
    """An object that defines how the reference rate of a stub period is calculated.

    Attributes
    ----------
    first : str
        The identifier of the first floating rate index definition used to
        determine the reference rate of the stub period (GUID or URI). Note
        that a URI must be at least 2 and at most 102 characters long, start
        with an alphanumeric character, and contain only alphanumeric
        characters, slashes and underscores.
    second : str
        The identifier of the second floating rate index definition used to
        determine the reference rate of the stub period (GUID or URI). Note
        that a URI must be at least 2 and at most 102 characters long, start
        with an alphanumeric character, and contain only alphanumeric
        characters, slashes and underscores.
    reference_rate : ~analyticsapi.models.Rate
        An object that defines the reference rate value.
    """

    first: Optional[str] = rest_field()
    """The identifier of the first floating rate index definition used to determine the reference rate
     of the stub period (GUID or URI).
     Note that a URI must be at least 2 and at most 102 characters long, start with an alphanumeric
     character, and contain only alphanumeric characters, slashes and underscores."""
    second: Optional[str] = rest_field()
    """The identifier of the second floating rate index definition used to determine the reference
     rate of the stub period (GUID or URI).
     Note that a URI must be at least 2 and at most 102 characters long, start with an alphanumeric
     character, and contain only alphanumeric characters, slashes and underscores."""
    reference_rate: Optional["_models.Rate"] = rest_field(name="referenceRate")
    """An object that defines the reference rate value."""

    @overload
    def __init__(
        self,
        *,
        first: Optional[str] = None,
        second: Optional[str] = None,
        reference_rate: Optional["_models.Rate"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class Summary(_model_base.Model):
    """Summary.

    Attributes
    ----------
    total : int
    excluded : int
    accepted : int
    rejected : int
    """

    total: Optional[int] = rest_field()
    excluded: Optional[int] = rest_field()
    accepted: Optional[int] = rest_field()
    rejected: Optional[int] = rest_field()

    @overload
    def __init__(
        self,
        *,
        total: Optional[int] = None,
        excluded: Optional[int] = None,
        accepted: Optional[int] = None,
        rejected: Optional[int] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class SwaptionVolatility(_model_base.Model):
    """SwaptionVolatility.

    Attributes
    ----------
    value_type : str
        Is either a Literal["ABS"] type or a Literal["REL"] type.
    values_property : list[~analyticsapi.models.SwaptionVolItem]
        The default value is None, needs to be assigned before using.
    """

    value_type: Optional[Literal["ABS", "REL"]] = rest_field(name="valueType")
    """Is either a Literal[\"ABS\"] type or a Literal[\"REL\"] type."""
    values_property: Optional[List["_models.SwaptionVolItem"]] = rest_field(name="values")

    @overload
    def __init__(
        self,
        *,
        value_type: Optional[Literal["ABS", "REL"]] = None,
        values_property: Optional[List["_models.SwaptionVolItem"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class SwaptionVolItem(_model_base.Model):
    """SwaptionVolItem.

    Attributes
    ----------
    expiration : ~decimal.Decimal
    value : ~decimal.Decimal
    term : ~decimal.Decimal
    """

    expiration: Optional[decimal.Decimal] = rest_field()
    value: Optional[decimal.Decimal] = rest_field()
    term: Optional[decimal.Decimal] = rest_field()

    @overload
    def __init__(
        self,
        *,
        expiration: Optional[decimal.Decimal] = None,
        value: Optional[decimal.Decimal] = None,
        term: Optional[decimal.Decimal] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class SystemScenario(_model_base.Model):
    """SystemScenario.

    Attributes
    ----------
    name : str
        Is one of the following types: Literal["BEARSTEEP50"],
        Literal["BEARFLAT50"], Literal["BULLFLAT50"], Literal["BULLSTEEP50"],
        Literal["BEARSTEEP100"], Literal["BEARFLAT100"],
        Literal["BULLFLAT100"], Literal["BULLSTEEP100"],
        Literal["SHORTEND1PLUS25"], Literal["SHORTEND1MINUS25"],
        Literal["SHORTEND2PLUS25"], Literal["SHORTEND2MINUS25"],
        Literal["SHORTEND3PLUS25"], Literal["SHORTEND3MINUS25"],
        Literal["LONGEND5PLUS25"], Literal["LONGEND5MINUS25"],
        Literal["LONGEND10PLUS25"], Literal["LONGEND10MINUS25"],
        Literal["LONGEND30PLUS25"], Literal["LONGEND30MINUS25"],
        Literal["YR20PLUS25"], Literal["YR20MINUS25"], Literal["PC1MOCOMP1UP"],
        Literal["PC1MOCOMP2UP"], Literal["PC1MOCOMP3UP"],
        Literal["PC1MOCOMP1DOWN"], Literal["PC1MOCOMP2DOWN"],
        Literal["PC1MOCOMP3DOWN"], Literal["PC3MOCOMP1UP"],
        Literal["PC3MOCOMP2UP"], Literal["PC3MOCOMP3UP"],
        Literal["PC3MOCOMP1DOWN"], Literal["PC3MOCOMP2DOWN"],
        Literal["PC3MOCOMP3DOWN"], Literal["PC6MOCOMP1UP"],
        Literal["PC6MOCOMP2UP"], Literal["PC6MOCOMP3UP"],
        Literal["PC6MOCOMP1DOWN"], Literal["PC6MOCOMP2DOWN"],
        Literal["PC6MOCOMP3DOWN"], Literal["PC1YRCOMP1UP"],
        Literal["PC1YRCOMP2UP"], Literal["PC1YRCOMP3UP"],
        Literal["PC1YRCOMP1DOWN"], Literal["PC1YRCOMP2DOWN"],
        Literal["PC1YRCOMP3DOWN"]
    """

    name: Optional[
        Literal[
            "BEARSTEEP50",
            "BEARFLAT50",
            "BULLFLAT50",
            "BULLSTEEP50",
            "BEARSTEEP100",
            "BEARFLAT100",
            "BULLFLAT100",
            "BULLSTEEP100",
            "SHORTEND1PLUS25",
            "SHORTEND1MINUS25",
            "SHORTEND2PLUS25",
            "SHORTEND2MINUS25",
            "SHORTEND3PLUS25",
            "SHORTEND3MINUS25",
            "LONGEND5PLUS25",
            "LONGEND5MINUS25",
            "LONGEND10PLUS25",
            "LONGEND10MINUS25",
            "LONGEND30PLUS25",
            "LONGEND30MINUS25",
            "YR20PLUS25",
            "YR20MINUS25",
            "PC1MOCOMP1UP",
            "PC1MOCOMP2UP",
            "PC1MOCOMP3UP",
            "PC1MOCOMP1DOWN",
            "PC1MOCOMP2DOWN",
            "PC1MOCOMP3DOWN",
            "PC3MOCOMP1UP",
            "PC3MOCOMP2UP",
            "PC3MOCOMP3UP",
            "PC3MOCOMP1DOWN",
            "PC3MOCOMP2DOWN",
            "PC3MOCOMP3DOWN",
            "PC6MOCOMP1UP",
            "PC6MOCOMP2UP",
            "PC6MOCOMP3UP",
            "PC6MOCOMP1DOWN",
            "PC6MOCOMP2DOWN",
            "PC6MOCOMP3DOWN",
            "PC1YRCOMP1UP",
            "PC1YRCOMP2UP",
            "PC1YRCOMP3UP",
            "PC1YRCOMP1DOWN",
            "PC1YRCOMP2DOWN",
            "PC1YRCOMP3DOWN",
        ]
    ] = rest_field()
    """Is one of the following types: Literal[\"BEARSTEEP50\"], Literal[\"BEARFLAT50\"],
     Literal[\"BULLFLAT50\"], Literal[\"BULLSTEEP50\"], Literal[\"BEARSTEEP100\"],
     Literal[\"BEARFLAT100\"], Literal[\"BULLFLAT100\"], Literal[\"BULLSTEEP100\"],
     Literal[\"SHORTEND1PLUS25\"], Literal[\"SHORTEND1MINUS25\"], Literal[\"SHORTEND2PLUS25\"],
     Literal[\"SHORTEND2MINUS25\"], Literal[\"SHORTEND3PLUS25\"], Literal[\"SHORTEND3MINUS25\"],
     Literal[\"LONGEND5PLUS25\"], Literal[\"LONGEND5MINUS25\"], Literal[\"LONGEND10PLUS25\"],
     Literal[\"LONGEND10MINUS25\"], Literal[\"LONGEND30PLUS25\"], Literal[\"LONGEND30MINUS25\"],
     Literal[\"YR20PLUS25\"], Literal[\"YR20MINUS25\"], Literal[\"PC1MOCOMP1UP\"],
     Literal[\"PC1MOCOMP2UP\"], Literal[\"PC1MOCOMP3UP\"], Literal[\"PC1MOCOMP1DOWN\"],
     Literal[\"PC1MOCOMP2DOWN\"], Literal[\"PC1MOCOMP3DOWN\"], Literal[\"PC3MOCOMP1UP\"],
     Literal[\"PC3MOCOMP2UP\"], Literal[\"PC3MOCOMP3UP\"], Literal[\"PC3MOCOMP1DOWN\"],
     Literal[\"PC3MOCOMP2DOWN\"], Literal[\"PC3MOCOMP3DOWN\"], Literal[\"PC6MOCOMP1UP\"],
     Literal[\"PC6MOCOMP2UP\"], Literal[\"PC6MOCOMP3UP\"], Literal[\"PC6MOCOMP1DOWN\"],
     Literal[\"PC6MOCOMP2DOWN\"], Literal[\"PC6MOCOMP3DOWN\"], Literal[\"PC1YRCOMP1UP\"],
     Literal[\"PC1YRCOMP2UP\"], Literal[\"PC1YRCOMP3UP\"], Literal[\"PC1YRCOMP1DOWN\"],
     Literal[\"PC1YRCOMP2DOWN\"], Literal[\"PC1YRCOMP3DOWN\"]"""

    @overload
    def __init__(
        self,
        name: Optional[
            Literal[
                "BEARSTEEP50",
                "BEARFLAT50",
                "BULLFLAT50",
                "BULLSTEEP50",
                "BEARSTEEP100",
                "BEARFLAT100",
                "BULLFLAT100",
                "BULLSTEEP100",
                "SHORTEND1PLUS25",
                "SHORTEND1MINUS25",
                "SHORTEND2PLUS25",
                "SHORTEND2MINUS25",
                "SHORTEND3PLUS25",
                "SHORTEND3MINUS25",
                "LONGEND5PLUS25",
                "LONGEND5MINUS25",
                "LONGEND10PLUS25",
                "LONGEND10MINUS25",
                "LONGEND30PLUS25",
                "LONGEND30MINUS25",
                "YR20PLUS25",
                "YR20MINUS25",
                "PC1MOCOMP1UP",
                "PC1MOCOMP2UP",
                "PC1MOCOMP3UP",
                "PC1MOCOMP1DOWN",
                "PC1MOCOMP2DOWN",
                "PC1MOCOMP3DOWN",
                "PC3MOCOMP1UP",
                "PC3MOCOMP2UP",
                "PC3MOCOMP3UP",
                "PC3MOCOMP1DOWN",
                "PC3MOCOMP2DOWN",
                "PC3MOCOMP3DOWN",
                "PC6MOCOMP1UP",
                "PC6MOCOMP2UP",
                "PC6MOCOMP3UP",
                "PC6MOCOMP1DOWN",
                "PC6MOCOMP2DOWN",
                "PC6MOCOMP3DOWN",
                "PC1YRCOMP1UP",
                "PC1YRCOMP2UP",
                "PC1YRCOMP3UP",
                "PC1YRCOMP1DOWN",
                "PC1YRCOMP2DOWN",
                "PC1YRCOMP3DOWN",
            ]
        ] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["name"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class TenorBasisSwapOverride(_model_base.Model):
    """An object that contains the tenor basis swap properties that can be overridden.

    Attributes
    ----------
    start_date : ~analyticsapi.models.Date
        An object that contains properties to define and adjust the tenor basis
        swap start date.
    end_date : ~analyticsapi.models.Date
        An object that contains properties to define and adjust the tenor basis
        swap end date.
    amount : float
        The principal amount of the tenor basis swap.
    first_spread : ~analyticsapi.models.Rate
    second_spread : ~analyticsapi.models.Rate
    paid_leg : str or ~analyticsapi.models.PaidLegEnum
        A flag that defines whether the first leg or the second leg of the
        tenor basis swap is paid. Known values are: "FirstLeg" and "SecondLeg".
    """

    start_date: Optional["_models.Date"] = rest_field(name="startDate")
    """An object that contains properties to define and adjust the tenor basis swap start date."""
    end_date: Optional["_models.Date"] = rest_field(name="endDate")
    """An object that contains properties to define and adjust the tenor basis swap end date."""
    amount: Optional[float] = rest_field()
    """The principal amount of the tenor basis swap."""
    first_spread: Optional["_models.Rate"] = rest_field(name="firstSpread")
    second_spread: Optional["_models.Rate"] = rest_field(name="secondSpread")
    paid_leg: Optional[Union[str, "_models.PaidLegEnum"]] = rest_field(name="paidLeg")
    """A flag that defines whether the first leg or the second leg of the tenor basis swap is paid.
     Known values are: \"FirstLeg\" and \"SecondLeg\"."""

    @overload
    def __init__(
        self,
        *,
        start_date: Optional["_models.Date"] = None,
        end_date: Optional["_models.Date"] = None,
        amount: Optional[float] = None,
        first_spread: Optional["_models.Rate"] = None,
        second_spread: Optional["_models.Rate"] = None,
        paid_leg: Optional[Union[str, "_models.PaidLegEnum"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class TenorBasisSwapTemplateDefinition(InstrumentTemplateDefinition, discriminator="TenorBasisSwap"):
    """TenorBasisSwapTemplateDefinition.

    Attributes
    ----------
    instrument_type : str or ~analyticsapi.models.TENOR_BASIS_SWAP
        Required. A tenor basis swap contract.
    template : ~analyticsapi.models.IrSwapDefinition
        Required.
    """

    instrument_type: Literal[InstrumentTemplateTypeEnum.TENOR_BASIS_SWAP] = rest_discriminator(name="instrumentType")  # type: ignore
    """Required. A tenor basis swap contract."""
    template: "_models.IrSwapDefinition" = rest_field()
    """Required."""

    @overload
    def __init__(
        self,
        template: "_models.IrSwapDefinition",
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, instrument_type=InstrumentTemplateTypeEnum.TENOR_BASIS_SWAP, **kwargs)


class TermAndValue(_model_base.Model):
    """TermAndValue.

    Attributes
    ----------
    term : int
    value : ~decimal.Decimal
    """

    term: Optional[int] = rest_field()
    value: Optional[decimal.Decimal] = rest_field()

    @overload
    def __init__(
        self,
        *,
        term: Optional[int] = None,
        value: Optional[decimal.Decimal] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class TermRatePair(_model_base.Model):
    """TermRatePair.

    Attributes
    ----------
    term : int
    rate : float
    """

    term: Optional[int] = rest_field()
    rate: Optional[float] = rest_field()

    @overload
    def __init__(
        self,
        *,
        term: Optional[int] = None,
        rate: Optional[float] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class Time(_model_base.Model):
    """An object to determine a certain time.

    Attributes
    ----------
    local_time : ~datetime.time
        The local time of the time zone used to determine a certain time. It is
        expressed in hh:mm:ss format (e.g., '17:00:00'). Required.
    time_zone_id : str or ~analyticsapi.models.TimezoneEnum
        The time zone used to determine a certain time. Known values are:
        "Africa/Abidjan", "Africa/Accra", "Africa/Addis_Ababa",
        "Africa/Algiers", "Africa/Asmara", "Africa/Asmera", "Africa/Bamako",
        "Africa/Bangui", "Africa/Banjul", "Africa/Bissau", "Africa/Blantyre",
        "Africa/Brazzaville", "Africa/Bujumbura", "Africa/Cairo",
        "Africa/Casablanca", "Africa/Ceuta", "Africa/Conakry", "Africa/Dakar",
        "Africa/Dar_es_Salaam", "Africa/Djibouti", "Africa/Douala",
        "Africa/El_Aaiun", "Africa/Freetown", "Africa/Gaborone",
        "Africa/Harare", "Africa/Johannesburg", "Africa/Juba",
        "Africa/Kampala", "Africa/Khartoum", "Africa/Kigali",
        "Africa/Kinshasa", "Africa/Lagos", "Africa/Libreville", "Africa/Lome",
        "Africa/Luanda", "Africa/Lubumbashi", "Africa/Lusaka", "Africa/Malabo",
        "Africa/Maputo", "Africa/Maseru", "Africa/Mbabane", "Africa/Mogadishu",
        "Africa/Monrovia", "Africa/Nairobi", "Africa/Ndjamena",
        "Africa/Niamey", "Africa/Nouakchott", "Africa/Ouagadougou",
        "Africa/Porto-Novo", "Africa/Sao_Tome", "Africa/Timbuktu",
        "Africa/Tripoli", "Africa/Tunis", "Africa/Windhoek", "America/Adak",
        "America/Anchorage", "America/Anguilla", "America/Antigua",
        "America/Araguaina", "America/Argentina/Buenos_Aires",
        "America/Argentina/Catamarca", "America/Argentina/ComodRivadavia",
        "America/Argentina/Cordoba", "America/Argentina/Jujuy",
        "America/Argentina/La_Rioja", "America/Argentina/Mendoza",
        "America/Argentina/Rio_Gallegos", "America/Argentina/Salta",
        "America/Argentina/San_Juan", "America/Argentina/San_Luis",
        "America/Argentina/Tucuman", "America/Argentina/Ushuaia",
        "America/Aruba", "America/Asuncion", "America/Atikokan",
        "America/Atka", "America/Bahia", "America/Bahia_Banderas",
        "America/Barbados", "America/Belem", "America/Belize", "America/Blanc-
        Sablon", "America/Boa_Vista", "America/Bogota", "America/Boise",
        "America/Buenos_Aires", "America/Cambridge_Bay",
        "America/Campo_Grande", "America/Cancun", "America/Caracas",
        "America/Catamarca", "America/Cayenne", "America/Cayman",
        "America/Chicago", "America/Chihuahua", "America/Ciudad_Juarez",
        "America/Coral_Harbour", "America/Cordoba", "America/Costa_Rica",
        "America/Creston", "America/Cuiaba", "America/Curacao",
        "America/Danmarkshavn", "America/Dawson", "America/Dawson_Creek",
        "America/Denver", "America/Detroit", "America/Dominica",
        "America/Edmonton", "America/Eirunepe", "America/El_Salvador",
        "America/Ensenada", "America/Fort_Nelson", "America/Fort_Wayne",
        "America/Fortaleza", "America/Glace_Bay", "America/Godthab",
        "America/Goose_Bay", "America/Grand_Turk", "America/Grenada",
        "America/Guadeloupe", "America/Guatemala", "America/Guayaquil",
        "America/Guyana", "America/Halifax", "America/Havana",
        "America/Hermosillo", "America/Indiana/Indianapolis",
        "America/Indiana/Knox", "America/Indiana/Marengo",
        "America/Indiana/Petersburg", "America/Indiana/Tell_City",
        "America/Indiana/Vevay", "America/Indiana/Vincennes",
        "America/Indiana/Winamac", "America/Indianapolis", "America/Inuvik",
        "America/Iqaluit", "America/Jamaica", "America/Jujuy",
        "America/Juneau", "America/Kentucky/Louisville",
        "America/Kentucky/Monticello", "America/Knox_IN", "America/Kralendijk",
        "America/La_Paz", "America/Lima", "America/Los_Angeles",
        "America/Louisville", "America/Lower_Princes", "America/Maceio",
        "America/Managua", "America/Manaus", "America/Marigot",
        "America/Martinique", "America/Matamoros", "America/Mazatlan",
        "America/Mendoza", "America/Menominee", "America/Merida",
        "America/Metlakatla", "America/Mexico_City", "America/Miquelon",
        "America/Moncton", "America/Monterrey", "America/Montevideo",
        "America/Montreal", "America/Montserrat", "America/Nassau",
        "America/New_York", "America/Nipigon", "America/Nome",
        "America/Noronha", "America/North_Dakota/Beulah",
        "America/North_Dakota/Center", "America/North_Dakota/New_Salem",
        "America/Nuuk", "America/Ojinaga", "America/Panama",
        "America/Pangnirtung", "America/Paramaribo", "America/Phoenix",
        "America/Port-au-Prince", "America/Port_of_Spain",
        "America/Porto_Acre", "America/Porto_Velho", "America/Puerto_Rico",
        "America/Punta_Arenas", "America/Rainy_River", "America/Rankin_Inlet",
        "America/Recife", "America/Regina", "America/Resolute",
        "America/Rio_Branco", "America/Rosario", "America/Santa_Isabel",
        "America/Santarem", "America/Santiago", "America/Santo_Domingo",
        "America/Sao_Paulo", "America/Scoresbysund", "America/Shiprock",
        "America/Sitka", "America/St_Barthelemy", "America/St_Johns",
        "America/St_Kitts", "America/St_Lucia", "America/St_Thomas",
        "America/St_Vincent", "America/Swift_Current", "America/Tegucigalpa",
        "America/Thule", "America/Thunder_Bay", "America/Tijuana",
        "America/Toronto", "America/Tortola", "America/Vancouver",
        "America/Virgin", "America/Whitehorse", "America/Winnipeg",
        "America/Yakutat", "America/Yellowknife", "Antarctica/Casey",
        "Antarctica/Davis", "Antarctica/DumontDUrville",
        "Antarctica/Macquarie", "Antarctica/Mawson", "Antarctica/McMurdo",
        "Antarctica/Palmer", "Antarctica/Rothera", "Antarctica/South_Pole",
        "Antarctica/Syowa", "Antarctica/Troll", "Antarctica/Vostok",
        "Arctic/Longyearbyen", "Asia/Aden", "Asia/Almaty", "Asia/Amman",
        "Asia/Anadyr", "Asia/Aqtau", "Asia/Aqtobe", "Asia/Ashgabat",
        "Asia/Ashkhabad", "Asia/Atyrau", "Asia/Baghdad", "Asia/Bahrain",
        "Asia/Baku", "Asia/Bangkok", "Asia/Barnaul", "Asia/Beirut",
        "Asia/Bishkek", "Asia/Brunei", "Asia/Calcutta", "Asia/Chita",
        "Asia/Choibalsan", "Asia/Chongqing", "Asia/Chungking", "Asia/Colombo",
        "Asia/Dacca", "Asia/Damascus", "Asia/Dhaka", "Asia/Dili", "Asia/Dubai",
        "Asia/Dushanbe", "Asia/Famagusta", "Asia/Gaza", "Asia/Harbin",
        "Asia/Hebron", "Asia/Ho_Chi_Minh", "Asia/Hong_Kong", "Asia/Hovd",
        "Asia/Irkutsk", "Asia/Istanbul", "Asia/Jakarta", "Asia/Jayapura",
        "Asia/Jerusalem", "Asia/Kabul", "Asia/Kamchatka", "Asia/Karachi",
        "Asia/Kashgar", "Asia/Kathmandu", "Asia/Katmandu", "Asia/Khandyga",
        "Asia/Kolkata", "Asia/Krasnoyarsk", "Asia/Kuala_Lumpur",
        "Asia/Kuching", "Asia/Kuwait", "Asia/Macao", "Asia/Macau",
        "Asia/Magadan", "Asia/Makassar", "Asia/Manila", "Asia/Muscat",
        "Asia/Nicosia", "Asia/Novokuznetsk", "Asia/Novosibirsk", "Asia/Omsk",
        "Asia/Oral", "Asia/Phnom_Penh", "Asia/Pontianak", "Asia/Pyongyang",
        "Asia/Qatar", "Asia/Qostanay", "Asia/Qyzylorda", "Asia/Rangoon",
        "Asia/Riyadh", "Asia/Saigon", "Asia/Sakhalin", "Asia/Samarkand",
        "Asia/Seoul", "Asia/Shanghai", "Asia/Singapore", "Asia/Srednekolymsk",
        "Asia/Taipei", "Asia/Tashkent", "Asia/Tbilisi", "Asia/Tehran",
        "Asia/Tel_Aviv", "Asia/Thimbu", "Asia/Thimphu", "Asia/Tokyo",
        "Asia/Tomsk", "Asia/Ujung_Pandang", "Asia/Ulaanbaatar",
        "Asia/Ulan_Bator", "Asia/Urumqi", "Asia/Ust-Nera", "Asia/Vientiane",
        "Asia/Vladivostok", "Asia/Yakutsk", "Asia/Yangon",
        "Asia/Yekaterinburg", "Asia/Yerevan", "Atlantic/Azores",
        "Atlantic/Bermuda", "Atlantic/Canary", "Atlantic/Cape_Verde",
        "Atlantic/Faeroe", "Atlantic/Faroe", "Atlantic/Jan_Mayen",
        "Atlantic/Madeira", "Atlantic/Reykjavik", "Atlantic/South_Georgia",
        "Atlantic/St_Helena", "Atlantic/Stanley", "Australia/ACT",
        "Australia/Adelaide", "Australia/Brisbane", "Australia/Broken_Hill",
        "Australia/Canberra", "Australia/Currie", "Australia/Darwin",
        "Australia/Eucla", "Australia/Hobart", "Australia/LHI",
        "Australia/Lindeman", "Australia/Lord_Howe", "Australia/Melbourne",
        "Australia/NSW", "Australia/North", "Australia/Perth",
        "Australia/Queensland", "Australia/South", "Australia/Sydney",
        "Australia/Tasmania", "Australia/Victoria", "Australia/West",
        "Australia/Yancowinna", "Brazil/Acre", "Brazil/DeNoronha",
        "Brazil/East", "Brazil/West", "CET", "CST6CDT", "Canada/Atlantic",
        "Canada/Central", "Canada/Eastern", "Canada/Mountain",
        "Canada/Newfoundland", "Canada/Pacific", "Canada/Saskatchewan",
        "Canada/Yukon", "Chile/Continental", "Chile/EasterIsland", "Cuba",
        "EET", "EST", "EST5EDT", "Egypt", "Eire", "Etc/GMT", "Etc/GMT+0",
        "Etc/GMT+1", "Etc/GMT+10", "Etc/GMT+11", "Etc/GMT+12", "Etc/GMT+2",
        "Etc/GMT+3", "Etc/GMT+4", "Etc/GMT+5", "Etc/GMT+6", "Etc/GMT+7",
        "Etc/GMT+8", "Etc/GMT+9", "Etc/GMT-0", "Etc/GMT-1", "Etc/GMT-10",
        "Etc/GMT-11", "Etc/GMT-12", "Etc/GMT-13", "Etc/GMT-14", "Etc/GMT-2",
        "Etc/GMT-3", "Etc/GMT-4", "Etc/GMT-5", "Etc/GMT-6", "Etc/GMT-7",
        "Etc/GMT-8", "Etc/GMT-9", "Etc/GMT0", "Etc/Greenwich", "Etc/UCT",
        "Etc/UTC", "Etc/Universal", "Etc/Zulu", "Europe/Amsterdam",
        "Europe/Andorra", "Europe/Astrakhan", "Europe/Athens",
        "Europe/Belfast", "Europe/Belgrade", "Europe/Berlin",
        "Europe/Bratislava", "Europe/Brussels", "Europe/Bucharest",
        "Europe/Budapest", "Europe/Busingen", "Europe/Chisinau",
        "Europe/Copenhagen", "Europe/Dublin", "Europe/Gibraltar",
        "Europe/Guernsey", "Europe/Helsinki", "Europe/Isle_of_Man",
        "Europe/Istanbul", "Europe/Jersey", "Europe/Kaliningrad",
        "Europe/Kiev", "Europe/Kirov", "Europe/Kyiv", "Europe/Lisbon",
        "Europe/Ljubljana", "Europe/London", "Europe/Luxembourg",
        "Europe/Madrid", "Europe/Malta", "Europe/Mariehamn", "Europe/Minsk",
        "Europe/Monaco", "Europe/Moscow", "Europe/Nicosia", "Europe/Oslo",
        "Europe/Paris", "Europe/Podgorica", "Europe/Prague", "Europe/Riga",
        "Europe/Rome", "Europe/Samara", "Europe/San_Marino", "Europe/Sarajevo",
        "Europe/Saratov", "Europe/Simferopol", "Europe/Skopje", "Europe/Sofia",
        "Europe/Stockholm", "Europe/Tallinn", "Europe/Tirane",
        "Europe/Tiraspol", "Europe/Ulyanovsk", "Europe/Uzhgorod",
        "Europe/Vaduz", "Europe/Vatican", "Europe/Vienna", "Europe/Vilnius",
        "Europe/Volgograd", "Europe/Warsaw", "Europe/Zagreb",
        "Europe/Zaporozhye", "Europe/Zurich", "GB", "GB-Eire", "GMT", "GMT+0",
        "GMT-0", "GMT0", "Greenwich", "HST", "Hongkong", "Iceland",
        "Indian/Antananarivo", "Indian/Chagos", "Indian/Christmas",
        "Indian/Cocos", "Indian/Comoro", "Indian/Kerguelen", "Indian/Mahe",
        "Indian/Maldives", "Indian/Mauritius", "Indian/Mayotte",
        "Indian/Reunion", "Iran", "Israel", "Jamaica", "Japan", "Kwajalein",
        "Libya", "MET", "MST", "MST7MDT", "Mexico/BajaNorte", "Mexico/BajaSur",
        "Mexico/General", "NZ", "NZ-CHAT", "Navajo", "PRC", "PST8PDT",
        "Pacific/Apia", "Pacific/Auckland", "Pacific/Bougainville",
        "Pacific/Chatham", "Pacific/Chuuk", "Pacific/Easter", "Pacific/Efate",
        "Pacific/Enderbury", "Pacific/Fakaofo", "Pacific/Fiji",
        "Pacific/Funafuti", "Pacific/Galapagos", "Pacific/Gambier",
        "Pacific/Guadalcanal", "Pacific/Guam", "Pacific/Honolulu",
        "Pacific/Johnston", "Pacific/Kanton", "Pacific/Kiritimati",
        "Pacific/Kosrae", "Pacific/Kwajalein", "Pacific/Majuro",
        "Pacific/Marquesas", "Pacific/Midway", "Pacific/Nauru", "Pacific/Niue",
        "Pacific/Norfolk", "Pacific/Noumea", "Pacific/Pago_Pago",
        "Pacific/Palau", "Pacific/Pitcairn", "Pacific/Pohnpei",
        "Pacific/Ponape", "Pacific/Port_Moresby", "Pacific/Rarotonga",
        "Pacific/Saipan", "Pacific/Samoa", "Pacific/Tahiti", "Pacific/Tarawa",
        "Pacific/Tongatapu", "Pacific/Truk", "Pacific/Wake", "Pacific/Wallis",
        "Pacific/Yap", "Poland", "Portugal", "ROC", "ROK", "Singapore",
        "Turkey", "UCT", "US/Alaska", "US/Aleutian", "US/Arizona",
        "US/Central", "US/East-Indiana", "US/Eastern", "US/Hawaii",
        "US/Indiana-Starke", "US/Michigan", "US/Mountain", "US/Pacific",
        "US/Samoa", "UTC", "Universal", "W-SU", "WET", and "Zulu".
    """

    local_time: datetime.time = rest_field(name="localTime")
    """The local time of the time zone used to determine a certain time. It is expressed in hh:mm:ss
     format (e.g., '17:00:00'). Required."""
    time_zone_id: Optional[Union[str, "_models.TimezoneEnum"]] = rest_field(name="timeZoneId")
    """The time zone used to determine a certain time. Known values are: \"Africa/Abidjan\",
     \"Africa/Accra\", \"Africa/Addis_Ababa\", \"Africa/Algiers\", \"Africa/Asmara\",
     \"Africa/Asmera\", \"Africa/Bamako\", \"Africa/Bangui\", \"Africa/Banjul\", \"Africa/Bissau\",
     \"Africa/Blantyre\", \"Africa/Brazzaville\", \"Africa/Bujumbura\", \"Africa/Cairo\",
     \"Africa/Casablanca\", \"Africa/Ceuta\", \"Africa/Conakry\", \"Africa/Dakar\",
     \"Africa/Dar_es_Salaam\", \"Africa/Djibouti\", \"Africa/Douala\", \"Africa/El_Aaiun\",
     \"Africa/Freetown\", \"Africa/Gaborone\", \"Africa/Harare\", \"Africa/Johannesburg\",
     \"Africa/Juba\", \"Africa/Kampala\", \"Africa/Khartoum\", \"Africa/Kigali\",
     \"Africa/Kinshasa\", \"Africa/Lagos\", \"Africa/Libreville\", \"Africa/Lome\",
     \"Africa/Luanda\", \"Africa/Lubumbashi\", \"Africa/Lusaka\", \"Africa/Malabo\",
     \"Africa/Maputo\", \"Africa/Maseru\", \"Africa/Mbabane\", \"Africa/Mogadishu\",
     \"Africa/Monrovia\", \"Africa/Nairobi\", \"Africa/Ndjamena\", \"Africa/Niamey\",
     \"Africa/Nouakchott\", \"Africa/Ouagadougou\", \"Africa/Porto-Novo\", \"Africa/Sao_Tome\",
     \"Africa/Timbuktu\", \"Africa/Tripoli\", \"Africa/Tunis\", \"Africa/Windhoek\",
     \"America/Adak\", \"America/Anchorage\", \"America/Anguilla\", \"America/Antigua\",
     \"America/Araguaina\", \"America/Argentina/Buenos_Aires\", \"America/Argentina/Catamarca\",
     \"America/Argentina/ComodRivadavia\", \"America/Argentina/Cordoba\",
     \"America/Argentina/Jujuy\", \"America/Argentina/La_Rioja\", \"America/Argentina/Mendoza\",
     \"America/Argentina/Rio_Gallegos\", \"America/Argentina/Salta\",
     \"America/Argentina/San_Juan\", \"America/Argentina/San_Luis\", \"America/Argentina/Tucuman\",
     \"America/Argentina/Ushuaia\", \"America/Aruba\", \"America/Asuncion\", \"America/Atikokan\",
     \"America/Atka\", \"America/Bahia\", \"America/Bahia_Banderas\", \"America/Barbados\",
     \"America/Belem\", \"America/Belize\", \"America/Blanc-Sablon\", \"America/Boa_Vista\",
     \"America/Bogota\", \"America/Boise\", \"America/Buenos_Aires\", \"America/Cambridge_Bay\",
     \"America/Campo_Grande\", \"America/Cancun\", \"America/Caracas\", \"America/Catamarca\",
     \"America/Cayenne\", \"America/Cayman\", \"America/Chicago\", \"America/Chihuahua\",
     \"America/Ciudad_Juarez\", \"America/Coral_Harbour\", \"America/Cordoba\",
     \"America/Costa_Rica\", \"America/Creston\", \"America/Cuiaba\", \"America/Curacao\",
     \"America/Danmarkshavn\", \"America/Dawson\", \"America/Dawson_Creek\", \"America/Denver\",
     \"America/Detroit\", \"America/Dominica\", \"America/Edmonton\", \"America/Eirunepe\",
     \"America/El_Salvador\", \"America/Ensenada\", \"America/Fort_Nelson\", \"America/Fort_Wayne\",
     \"America/Fortaleza\", \"America/Glace_Bay\", \"America/Godthab\", \"America/Goose_Bay\",
     \"America/Grand_Turk\", \"America/Grenada\", \"America/Guadeloupe\", \"America/Guatemala\",
     \"America/Guayaquil\", \"America/Guyana\", \"America/Halifax\", \"America/Havana\",
     \"America/Hermosillo\", \"America/Indiana/Indianapolis\", \"America/Indiana/Knox\",
     \"America/Indiana/Marengo\", \"America/Indiana/Petersburg\", \"America/Indiana/Tell_City\",
     \"America/Indiana/Vevay\", \"America/Indiana/Vincennes\", \"America/Indiana/Winamac\",
     \"America/Indianapolis\", \"America/Inuvik\", \"America/Iqaluit\", \"America/Jamaica\",
     \"America/Jujuy\", \"America/Juneau\", \"America/Kentucky/Louisville\",
     \"America/Kentucky/Monticello\", \"America/Knox_IN\", \"America/Kralendijk\",
     \"America/La_Paz\", \"America/Lima\", \"America/Los_Angeles\", \"America/Louisville\",
     \"America/Lower_Princes\", \"America/Maceio\", \"America/Managua\", \"America/Manaus\",
     \"America/Marigot\", \"America/Martinique\", \"America/Matamoros\", \"America/Mazatlan\",
     \"America/Mendoza\", \"America/Menominee\", \"America/Merida\", \"America/Metlakatla\",
     \"America/Mexico_City\", \"America/Miquelon\", \"America/Moncton\", \"America/Monterrey\",
     \"America/Montevideo\", \"America/Montreal\", \"America/Montserrat\", \"America/Nassau\",
     \"America/New_York\", \"America/Nipigon\", \"America/Nome\", \"America/Noronha\",
     \"America/North_Dakota/Beulah\", \"America/North_Dakota/Center\",
     \"America/North_Dakota/New_Salem\", \"America/Nuuk\", \"America/Ojinaga\", \"America/Panama\",
     \"America/Pangnirtung\", \"America/Paramaribo\", \"America/Phoenix\",
     \"America/Port-au-Prince\", \"America/Port_of_Spain\", \"America/Porto_Acre\",
     \"America/Porto_Velho\", \"America/Puerto_Rico\", \"America/Punta_Arenas\",
     \"America/Rainy_River\", \"America/Rankin_Inlet\", \"America/Recife\", \"America/Regina\",
     \"America/Resolute\", \"America/Rio_Branco\", \"America/Rosario\", \"America/Santa_Isabel\",
     \"America/Santarem\", \"America/Santiago\", \"America/Santo_Domingo\", \"America/Sao_Paulo\",
     \"America/Scoresbysund\", \"America/Shiprock\", \"America/Sitka\", \"America/St_Barthelemy\",
     \"America/St_Johns\", \"America/St_Kitts\", \"America/St_Lucia\", \"America/St_Thomas\",
     \"America/St_Vincent\", \"America/Swift_Current\", \"America/Tegucigalpa\", \"America/Thule\",
     \"America/Thunder_Bay\", \"America/Tijuana\", \"America/Toronto\", \"America/Tortola\",
     \"America/Vancouver\", \"America/Virgin\", \"America/Whitehorse\", \"America/Winnipeg\",
     \"America/Yakutat\", \"America/Yellowknife\", \"Antarctica/Casey\", \"Antarctica/Davis\",
     \"Antarctica/DumontDUrville\", \"Antarctica/Macquarie\", \"Antarctica/Mawson\",
     \"Antarctica/McMurdo\", \"Antarctica/Palmer\", \"Antarctica/Rothera\",
     \"Antarctica/South_Pole\", \"Antarctica/Syowa\", \"Antarctica/Troll\", \"Antarctica/Vostok\",
     \"Arctic/Longyearbyen\", \"Asia/Aden\", \"Asia/Almaty\", \"Asia/Amman\", \"Asia/Anadyr\",
     \"Asia/Aqtau\", \"Asia/Aqtobe\", \"Asia/Ashgabat\", \"Asia/Ashkhabad\", \"Asia/Atyrau\",
     \"Asia/Baghdad\", \"Asia/Bahrain\", \"Asia/Baku\", \"Asia/Bangkok\", \"Asia/Barnaul\",
     \"Asia/Beirut\", \"Asia/Bishkek\", \"Asia/Brunei\", \"Asia/Calcutta\", \"Asia/Chita\",
     \"Asia/Choibalsan\", \"Asia/Chongqing\", \"Asia/Chungking\", \"Asia/Colombo\", \"Asia/Dacca\",
     \"Asia/Damascus\", \"Asia/Dhaka\", \"Asia/Dili\", \"Asia/Dubai\", \"Asia/Dushanbe\",
     \"Asia/Famagusta\", \"Asia/Gaza\", \"Asia/Harbin\", \"Asia/Hebron\", \"Asia/Ho_Chi_Minh\",
     \"Asia/Hong_Kong\", \"Asia/Hovd\", \"Asia/Irkutsk\", \"Asia/Istanbul\", \"Asia/Jakarta\",
     \"Asia/Jayapura\", \"Asia/Jerusalem\", \"Asia/Kabul\", \"Asia/Kamchatka\", \"Asia/Karachi\",
     \"Asia/Kashgar\", \"Asia/Kathmandu\", \"Asia/Katmandu\", \"Asia/Khandyga\", \"Asia/Kolkata\",
     \"Asia/Krasnoyarsk\", \"Asia/Kuala_Lumpur\", \"Asia/Kuching\", \"Asia/Kuwait\", \"Asia/Macao\",
     \"Asia/Macau\", \"Asia/Magadan\", \"Asia/Makassar\", \"Asia/Manila\", \"Asia/Muscat\",
     \"Asia/Nicosia\", \"Asia/Novokuznetsk\", \"Asia/Novosibirsk\", \"Asia/Omsk\", \"Asia/Oral\",
     \"Asia/Phnom_Penh\", \"Asia/Pontianak\", \"Asia/Pyongyang\", \"Asia/Qatar\", \"Asia/Qostanay\",
     \"Asia/Qyzylorda\", \"Asia/Rangoon\", \"Asia/Riyadh\", \"Asia/Saigon\", \"Asia/Sakhalin\",
     \"Asia/Samarkand\", \"Asia/Seoul\", \"Asia/Shanghai\", \"Asia/Singapore\",
     \"Asia/Srednekolymsk\", \"Asia/Taipei\", \"Asia/Tashkent\", \"Asia/Tbilisi\", \"Asia/Tehran\",
     \"Asia/Tel_Aviv\", \"Asia/Thimbu\", \"Asia/Thimphu\", \"Asia/Tokyo\", \"Asia/Tomsk\",
     \"Asia/Ujung_Pandang\", \"Asia/Ulaanbaatar\", \"Asia/Ulan_Bator\", \"Asia/Urumqi\",
     \"Asia/Ust-Nera\", \"Asia/Vientiane\", \"Asia/Vladivostok\", \"Asia/Yakutsk\", \"Asia/Yangon\",
     \"Asia/Yekaterinburg\", \"Asia/Yerevan\", \"Atlantic/Azores\", \"Atlantic/Bermuda\",
     \"Atlantic/Canary\", \"Atlantic/Cape_Verde\", \"Atlantic/Faeroe\", \"Atlantic/Faroe\",
     \"Atlantic/Jan_Mayen\", \"Atlantic/Madeira\", \"Atlantic/Reykjavik\",
     \"Atlantic/South_Georgia\", \"Atlantic/St_Helena\", \"Atlantic/Stanley\", \"Australia/ACT\",
     \"Australia/Adelaide\", \"Australia/Brisbane\", \"Australia/Broken_Hill\",
     \"Australia/Canberra\", \"Australia/Currie\", \"Australia/Darwin\", \"Australia/Eucla\",
     \"Australia/Hobart\", \"Australia/LHI\", \"Australia/Lindeman\", \"Australia/Lord_Howe\",
     \"Australia/Melbourne\", \"Australia/NSW\", \"Australia/North\", \"Australia/Perth\",
     \"Australia/Queensland\", \"Australia/South\", \"Australia/Sydney\", \"Australia/Tasmania\",
     \"Australia/Victoria\", \"Australia/West\", \"Australia/Yancowinna\", \"Brazil/Acre\",
     \"Brazil/DeNoronha\", \"Brazil/East\", \"Brazil/West\", \"CET\", \"CST6CDT\",
     \"Canada/Atlantic\", \"Canada/Central\", \"Canada/Eastern\", \"Canada/Mountain\",
     \"Canada/Newfoundland\", \"Canada/Pacific\", \"Canada/Saskatchewan\", \"Canada/Yukon\",
     \"Chile/Continental\", \"Chile/EasterIsland\", \"Cuba\", \"EET\", \"EST\", \"EST5EDT\",
     \"Egypt\", \"Eire\", \"Etc/GMT\", \"Etc/GMT+0\", \"Etc/GMT+1\", \"Etc/GMT+10\", \"Etc/GMT+11\",
     \"Etc/GMT+12\", \"Etc/GMT+2\", \"Etc/GMT+3\", \"Etc/GMT+4\", \"Etc/GMT+5\", \"Etc/GMT+6\",
     \"Etc/GMT+7\", \"Etc/GMT+8\", \"Etc/GMT+9\", \"Etc/GMT-0\", \"Etc/GMT-1\", \"Etc/GMT-10\",
     \"Etc/GMT-11\", \"Etc/GMT-12\", \"Etc/GMT-13\", \"Etc/GMT-14\", \"Etc/GMT-2\", \"Etc/GMT-3\",
     \"Etc/GMT-4\", \"Etc/GMT-5\", \"Etc/GMT-6\", \"Etc/GMT-7\", \"Etc/GMT-8\", \"Etc/GMT-9\",
     \"Etc/GMT0\", \"Etc/Greenwich\", \"Etc/UCT\", \"Etc/UTC\", \"Etc/Universal\", \"Etc/Zulu\",
     \"Europe/Amsterdam\", \"Europe/Andorra\", \"Europe/Astrakhan\", \"Europe/Athens\",
     \"Europe/Belfast\", \"Europe/Belgrade\", \"Europe/Berlin\", \"Europe/Bratislava\",
     \"Europe/Brussels\", \"Europe/Bucharest\", \"Europe/Budapest\", \"Europe/Busingen\",
     \"Europe/Chisinau\", \"Europe/Copenhagen\", \"Europe/Dublin\", \"Europe/Gibraltar\",
     \"Europe/Guernsey\", \"Europe/Helsinki\", \"Europe/Isle_of_Man\", \"Europe/Istanbul\",
     \"Europe/Jersey\", \"Europe/Kaliningrad\", \"Europe/Kiev\", \"Europe/Kirov\", \"Europe/Kyiv\",
     \"Europe/Lisbon\", \"Europe/Ljubljana\", \"Europe/London\", \"Europe/Luxembourg\",
     \"Europe/Madrid\", \"Europe/Malta\", \"Europe/Mariehamn\", \"Europe/Minsk\", \"Europe/Monaco\",
     \"Europe/Moscow\", \"Europe/Nicosia\", \"Europe/Oslo\", \"Europe/Paris\", \"Europe/Podgorica\",
     \"Europe/Prague\", \"Europe/Riga\", \"Europe/Rome\", \"Europe/Samara\", \"Europe/San_Marino\",
     \"Europe/Sarajevo\", \"Europe/Saratov\", \"Europe/Simferopol\", \"Europe/Skopje\",
     \"Europe/Sofia\", \"Europe/Stockholm\", \"Europe/Tallinn\", \"Europe/Tirane\",
     \"Europe/Tiraspol\", \"Europe/Ulyanovsk\", \"Europe/Uzhgorod\", \"Europe/Vaduz\",
     \"Europe/Vatican\", \"Europe/Vienna\", \"Europe/Vilnius\", \"Europe/Volgograd\",
     \"Europe/Warsaw\", \"Europe/Zagreb\", \"Europe/Zaporozhye\", \"Europe/Zurich\", \"GB\",
     \"GB-Eire\", \"GMT\", \"GMT+0\", \"GMT-0\", \"GMT0\", \"Greenwich\", \"HST\", \"Hongkong\",
     \"Iceland\", \"Indian/Antananarivo\", \"Indian/Chagos\", \"Indian/Christmas\",
     \"Indian/Cocos\", \"Indian/Comoro\", \"Indian/Kerguelen\", \"Indian/Mahe\",
     \"Indian/Maldives\", \"Indian/Mauritius\", \"Indian/Mayotte\", \"Indian/Reunion\", \"Iran\",
     \"Israel\", \"Jamaica\", \"Japan\", \"Kwajalein\", \"Libya\", \"MET\", \"MST\", \"MST7MDT\",
     \"Mexico/BajaNorte\", \"Mexico/BajaSur\", \"Mexico/General\", \"NZ\", \"NZ-CHAT\", \"Navajo\",
     \"PRC\", \"PST8PDT\", \"Pacific/Apia\", \"Pacific/Auckland\", \"Pacific/Bougainville\",
     \"Pacific/Chatham\", \"Pacific/Chuuk\", \"Pacific/Easter\", \"Pacific/Efate\",
     \"Pacific/Enderbury\", \"Pacific/Fakaofo\", \"Pacific/Fiji\", \"Pacific/Funafuti\",
     \"Pacific/Galapagos\", \"Pacific/Gambier\", \"Pacific/Guadalcanal\", \"Pacific/Guam\",
     \"Pacific/Honolulu\", \"Pacific/Johnston\", \"Pacific/Kanton\", \"Pacific/Kiritimati\",
     \"Pacific/Kosrae\", \"Pacific/Kwajalein\", \"Pacific/Majuro\", \"Pacific/Marquesas\",
     \"Pacific/Midway\", \"Pacific/Nauru\", \"Pacific/Niue\", \"Pacific/Norfolk\",
     \"Pacific/Noumea\", \"Pacific/Pago_Pago\", \"Pacific/Palau\", \"Pacific/Pitcairn\",
     \"Pacific/Pohnpei\", \"Pacific/Ponape\", \"Pacific/Port_Moresby\", \"Pacific/Rarotonga\",
     \"Pacific/Saipan\", \"Pacific/Samoa\", \"Pacific/Tahiti\", \"Pacific/Tarawa\",
     \"Pacific/Tongatapu\", \"Pacific/Truk\", \"Pacific/Wake\", \"Pacific/Wallis\", \"Pacific/Yap\",
     \"Poland\", \"Portugal\", \"ROC\", \"ROK\", \"Singapore\", \"Turkey\", \"UCT\", \"US/Alaska\",
     \"US/Aleutian\", \"US/Arizona\", \"US/Central\", \"US/East-Indiana\", \"US/Eastern\",
     \"US/Hawaii\", \"US/Indiana-Starke\", \"US/Michigan\", \"US/Mountain\", \"US/Pacific\",
     \"US/Samoa\", \"UTC\", \"Universal\", \"W-SU\", \"WET\", and \"Zulu\"."""

    @overload
    def __init__(
        self,
        *,
        local_time: datetime.time,
        time_zone_id: Optional[Union[str, "_models.TimezoneEnum"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class UDIExtension(_model_base.Model):
    """UDIExtension.

    Attributes
    ----------
    identifier : str
    """

    identifier: Optional[str] = rest_field()

    @overload
    def __init__(
        self,
        identifier: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["identifier"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class UnderlyingDefinition(ABC, _model_base.Model):
    """An object that defines the underlying asset.

    You probably want to use the sub-classes and not this class directly. Known sub-classes are:
    UnderlyingBond, UnderlyingBondFuture, UnderlyingCommodity, UnderlyingEquity, UnderlyingFx,
    UnderlyingIrs

    Attributes
    ----------
    underlying_type : str or ~analyticsapi.models.UnderlyingTypeEnum
        The type of the underlying asset. Required. Known values are: "Fx",
        "Bond", "Irs", "Commodity", "Equity", and "BondFuture".
    code : str
        The code (a RIC) used to define the underlying asset.
    definition : str
        The identifier of the underlying definition resource (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long,
        start with an alphanumeric character, and contain only alphanumeric
        characters, slashes and underscores.
    """

    __mapping__: Dict[str, _model_base.Model] = {}
    underlying_type: str = rest_discriminator(name="underlyingType")
    """The type of the underlying asset. Required. Known values are: \"Fx\", \"Bond\", \"Irs\",
     \"Commodity\", \"Equity\", and \"BondFuture\"."""
    code: Optional[str] = rest_field()
    """The code (a RIC) used to define the underlying asset."""
    definition: Optional[str] = rest_field()
    """The identifier of the underlying definition resource (GUID or URI).
     Note that a URI must be at least 2 and at most 102 characters long, start with an alphanumeric
     character, and contain only alphanumeric characters, slashes and underscores."""

    @overload
    def __init__(
        self,
        *,
        underlying_type: str,
        code: Optional[str] = None,
        definition: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class UnderlyingBond(UnderlyingDefinition, discriminator="Bond"):
    """An object that defines the underlying bond instrument.

    Attributes
    ----------
    code : str
        The code (a RIC) used to define the underlying asset.
    definition : str
        The identifier of the underlying definition resource (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long,
        start with an alphanumeric character, and contain only alphanumeric
        characters, slashes and underscores.
    underlying_type : str or ~analyticsapi.models.BOND
        The type of the underlying asset. Restricted to 'Bond'. Required.
    """

    underlying_type: Literal[UnderlyingTypeEnum.BOND] = rest_discriminator(name="underlyingType")  # type: ignore
    """The type of the underlying asset. Restricted to 'Bond'. Required."""

    @overload
    def __init__(
        self,
        *,
        code: Optional[str] = None,
        definition: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["underlying_type"] = args[0]
            args = tuple()
        super().__init__(*args, underlying_type=UnderlyingTypeEnum.BOND, **kwargs)


class UnderlyingBondFuture(UnderlyingDefinition, discriminator="BondFuture"):
    """An object that defines the underlying bond future instrument.

    Attributes
    ----------
    code : str
        The code (a RIC) used to define the underlying asset.
    definition : str
        The identifier of the underlying definition resource (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long,
        start with an alphanumeric character, and contain only alphanumeric
        characters, slashes and underscores.
    underlying_type : str or ~analyticsapi.models.BOND_FUTURE
        The type of the underlying asset. Restricted to 'BondFuture'. Required.
    """

    underlying_type: Literal[UnderlyingTypeEnum.BOND_FUTURE] = rest_discriminator(name="underlyingType")  # type: ignore
    """The type of the underlying asset. Restricted to 'BondFuture'. Required."""

    @overload
    def __init__(
        self,
        *,
        code: Optional[str] = None,
        definition: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["underlying_type"] = args[0]
            args = tuple()
        super().__init__(*args, underlying_type=UnderlyingTypeEnum.BOND_FUTURE, **kwargs)


class UnderlyingCommodity(UnderlyingDefinition, discriminator="Commodity"):
    """An object that defines the underlying commodity instrument.

    Attributes
    ----------
    code : str
        The code (a RIC) used to define the underlying asset.
    definition : str
        The identifier of the underlying definition resource (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long,
        start with an alphanumeric character, and contain only alphanumeric
        characters, slashes and underscores.
    underlying_type : str or ~analyticsapi.models.COMMODITY
        The type of the underlying asset. Restricted to 'Commodity'. Required.
    """

    underlying_type: Literal[UnderlyingTypeEnum.COMMODITY] = rest_discriminator(name="underlyingType")  # type: ignore
    """The type of the underlying asset. Restricted to 'Commodity'. Required."""

    @overload
    def __init__(
        self,
        *,
        code: Optional[str] = None,
        definition: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["underlying_type"] = args[0]
            args = tuple()
        super().__init__(*args, underlying_type=UnderlyingTypeEnum.COMMODITY, **kwargs)


class UnderlyingEquity(UnderlyingDefinition, discriminator="Equity"):
    """An object that defines the underlying equity instrument.

    Attributes
    ----------
    code : str
        The code (a RIC) used to define the underlying asset.
    definition : str
        The identifier of the underlying definition resource (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long,
        start with an alphanumeric character, and contain only alphanumeric
        characters, slashes and underscores.
    underlying_type : str or ~analyticsapi.models.EQUITY
        The type of the underlying asset. Restricted to 'Equity'. Required.
    """

    underlying_type: Literal[UnderlyingTypeEnum.EQUITY] = rest_discriminator(name="underlyingType")  # type: ignore
    """The type of the underlying asset. Restricted to 'Equity'. Required."""

    @overload
    def __init__(
        self,
        *,
        code: Optional[str] = None,
        definition: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["underlying_type"] = args[0]
            args = tuple()
        super().__init__(*args, underlying_type=UnderlyingTypeEnum.EQUITY, **kwargs)


class UnderlyingFx(UnderlyingDefinition, discriminator="Fx"):
    """An object that defines the underlying FX instrument.

    Attributes
    ----------
    code : str
        The code (a RIC) used to define the underlying asset.
    definition : str
        The identifier of the underlying definition resource (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long,
        start with an alphanumeric character, and contain only alphanumeric
        characters, slashes and underscores.
    underlying_type : str or ~analyticsapi.models.FX
        The type of the underlying asset. Restricted to 'Fx'. Required.
    """

    underlying_type: Literal[UnderlyingTypeEnum.FX] = rest_discriminator(name="underlyingType")  # type: ignore
    """The type of the underlying asset. Restricted to 'Fx'. Required."""

    @overload
    def __init__(
        self,
        *,
        code: Optional[str] = None,
        definition: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["underlying_type"] = args[0]
            args = tuple()
        super().__init__(*args, underlying_type=UnderlyingTypeEnum.FX, **kwargs)


class UnderlyingIrs(UnderlyingDefinition, discriminator="Irs"):
    """An object that defines the underlying interest rate swap instrument.

    Attributes
    ----------
    code : str
        The code (a RIC) used to define the underlying asset.
    definition : str
        The identifier of the underlying definition resource (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long,
        start with an alphanumeric character, and contain only alphanumeric
        characters, slashes and underscores.
    underlying_type : str or ~analyticsapi.models.IRS
        The type of the underlying asset. Restricted to 'Irs'. Required.
    """

    underlying_type: Literal[UnderlyingTypeEnum.IRS] = rest_discriminator(name="underlyingType")  # type: ignore
    """The type of the underlying asset. Restricted to 'Irs'. Required."""

    @overload
    def __init__(
        self,
        *,
        code: Optional[str] = None,
        definition: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["underlying_type"] = args[0]
            args = tuple()
        super().__init__(*args, underlying_type=UnderlyingTypeEnum.IRS, **kwargs)


class UserCurve(_model_base.Model):  # pylint: disable=too-many-instance-attributes
    """UserCurve.

    Attributes
    ----------
    curve_type : str
        Is one of the following types: Literal["GVT"], Literal["GVT_TSYM"],
        Literal["GVT_TSYM_MUNI"], Literal["GVT_AGN"], Literal["GVT_MUNI"],
        Literal["GVT_BUND"], Literal["SWAP"], Literal["SWAP_RFR"],
        Literal["SWAP_MUNI"]
    currency : str
    points : list[~analyticsapi.models.CurvePoint]
        The default value is None, needs to be assigned before using.
    rate_type : str
        Is one of the following types: Literal["Spot"], Literal["Par"],
        Literal["Forward"], Literal["DiscountFactor"]
    source : str
    asof : str
    compounding_freq : int
    relative : bool
    validate : bool
    swap_index : str
    swap_fixed_day_type : str
    swap_float_day_type : str
    swap_reset_convention : str
    """

    curve_type: Optional[
        Literal["GVT", "GVT_TSYM", "GVT_TSYM_MUNI", "GVT_AGN", "GVT_MUNI", "GVT_BUND", "SWAP", "SWAP_RFR", "SWAP_MUNI"]
    ] = rest_field(name="curveType")
    """Is one of the following types: Literal[\"GVT\"], Literal[\"GVT_TSYM\"],
     Literal[\"GVT_TSYM_MUNI\"], Literal[\"GVT_AGN\"], Literal[\"GVT_MUNI\"], Literal[\"GVT_BUND\"],
     Literal[\"SWAP\"], Literal[\"SWAP_RFR\"], Literal[\"SWAP_MUNI\"]"""
    currency: Optional[str] = rest_field()
    points: Optional[List["_models.CurvePoint"]] = rest_field()
    rate_type: Optional[Literal["Spot", "Par", "Forward", "DiscountFactor"]] = rest_field(name="rateType")
    """Is one of the following types: Literal[\"Spot\"], Literal[\"Par\"], Literal[\"Forward\"],
     Literal[\"DiscountFactor\"]"""
    source: Optional[str] = rest_field()
    asof: Optional[str] = rest_field()
    compounding_freq: Optional[int] = rest_field(name="compoundingFreq")
    relative: Optional[bool] = rest_field()
    validate: Optional[bool] = rest_field()
    swap_index: Optional[str] = rest_field(name="swapIndex")
    swap_fixed_day_type: Optional[str] = rest_field(name="swapFixedDayType")
    swap_float_day_type: Optional[str] = rest_field(name="swapFloatDayType")
    swap_reset_convention: Optional[str] = rest_field(name="swapResetConvention")

    @overload
    def __init__(
        self,
        *,
        curve_type: Optional[
            Literal[
                "GVT", "GVT_TSYM", "GVT_TSYM_MUNI", "GVT_AGN", "GVT_MUNI", "GVT_BUND", "SWAP", "SWAP_RFR", "SWAP_MUNI"
            ]
        ] = None,
        currency: Optional[str] = None,
        points: Optional[List["_models.CurvePoint"]] = None,
        rate_type: Optional[Literal["Spot", "Par", "Forward", "DiscountFactor"]] = None,
        source: Optional[str] = None,
        asof: Optional[str] = None,
        compounding_freq: Optional[int] = None,
        relative: Optional[bool] = None,
        validate: Optional[bool] = None,
        swap_index: Optional[str] = None,
        swap_fixed_day_type: Optional[str] = None,
        swap_float_day_type: Optional[str] = None,
        swap_reset_convention: Optional[str] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class UserScenario(_model_base.Model):
    """UserScenario.

    Attributes
    ----------
    shift_type : str
        Is one of the following types: Literal["Forward"],
        Literal["ImpliedForward"], Literal["Par"], Literal["Spot"]
    interpolation_type : str
        Is one of the following types: Literal["Years"], Literal["Yields"],
        Literal["PrincipalComponents"]
    swap_spread_const : bool
        Optional, if true, the spread between the treasury curve and swap curve
        is held constant.
    curve_shifts : list[~analyticsapi.models.ApimCurveShift]
        The default value is None, needs to be assigned before using.
    curve_multi_shifts : list[~analyticsapi.models.CurveMultiShift]
        The default value is None, needs to be assigned before using.
    curve_points : list[~analyticsapi.models.ScenAbsoluteCurvePoint]
        The default value is None, needs to be assigned before using.
    """

    shift_type: Optional[Literal["Forward", "ImpliedForward", "Par", "Spot"]] = rest_field(name="shiftType")
    """Is one of the following types: Literal[\"Forward\"], Literal[\"ImpliedForward\"],
     Literal[\"Par\"], Literal[\"Spot\"]"""
    interpolation_type: Optional[Literal["Years", "Yields", "PrincipalComponents"]] = rest_field(
        name="interpolationType"
    )
    """Is one of the following types: Literal[\"Years\"], Literal[\"Yields\"],
     Literal[\"PrincipalComponents\"]"""
    swap_spread_const: Optional[bool] = rest_field(name="swapSpreadConst")
    """Optional, if true, the spread between the treasury curve and swap curve is held constant."""
    curve_shifts: Optional[List["_models.ApimCurveShift"]] = rest_field(name="curveShifts")
    curve_multi_shifts: Optional[List["_models.CurveMultiShift"]] = rest_field(name="curveMultiShifts")
    curve_points: Optional[List["_models.ScenAbsoluteCurvePoint"]] = rest_field(name="curvePoints")

    @overload
    def __init__(
        self,
        *,
        shift_type: Optional[Literal["Forward", "ImpliedForward", "Par", "Spot"]] = None,
        interpolation_type: Optional[Literal["Years", "Yields", "PrincipalComponents"]] = None,
        swap_spread_const: Optional[bool] = None,
        curve_shifts: Optional[List["_models.ApimCurveShift"]] = None,
        curve_multi_shifts: Optional[List["_models.CurveMultiShift"]] = None,
        curve_points: Optional[List["_models.ScenAbsoluteCurvePoint"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class UserScenarioCurve(_model_base.Model):
    """UserScenarioCurve.

    Attributes
    ----------
    timing : str
        Is one of the following types: Literal["Immediate"],
        Literal["Gradual"], Literal["AtHorizon"]
    reinvestment_rate : str
    definition : ~analyticsapi.models.UserScenCurveDefinition
    current_coupon_spread_change : ~decimal.Decimal
    """

    timing: Optional[Literal["Immediate", "Gradual", "AtHorizon"]] = rest_field()
    """Is one of the following types: Literal[\"Immediate\"], Literal[\"Gradual\"],
     Literal[\"AtHorizon\"]"""
    reinvestment_rate: Optional[str] = rest_field(name="reinvestmentRate")
    definition: Optional["_models.UserScenCurveDefinition"] = rest_field()
    current_coupon_spread_change: Optional[decimal.Decimal] = rest_field(name="currentCouponSpreadChange")

    @overload
    def __init__(
        self,
        *,
        timing: Optional[Literal["Immediate", "Gradual", "AtHorizon"]] = None,
        reinvestment_rate: Optional[str] = None,
        definition: Optional["_models.UserScenCurveDefinition"] = None,
        current_coupon_spread_change: Optional[decimal.Decimal] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class UserScenarioInput(_model_base.Model):
    """UserScenarioInput.

    Attributes
    ----------
    volatility : ~analyticsapi.models.ScenarioVolatility
    curve : ~analyticsapi.models.UserScenarioCurve
    """

    volatility: Optional["_models.ScenarioVolatility"] = rest_field()
    curve: Optional["_models.UserScenarioCurve"] = rest_field()

    @overload
    def __init__(
        self,
        *,
        volatility: Optional["_models.ScenarioVolatility"] = None,
        curve: Optional["_models.UserScenarioCurve"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class UserScenCurveDefinition(_model_base.Model):
    """UserScenCurveDefinition.

    Attributes
    ----------
    user_scenario : ~analyticsapi.models.UserScenario
    """

    user_scenario: Optional["_models.UserScenario"] = rest_field(name="userScenario")

    @overload
    def __init__(
        self,
        user_scenario: Optional["_models.UserScenario"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        if len(args) == 1 and not isinstance(args[0], dict):
            kwargs["user_scenario"] = args[0]
            args = tuple()
        super().__init__(*args, **kwargs)


class UserVol(_model_base.Model):
    """UserVol.

    Attributes
    ----------
    shift_type : str
    volatility_type : str
    currency : str
    asof : str
    term_unit : str
        Is either a Literal["MONTH"] type or a Literal["YEAR"] type.
    swaption_volatility : list[~analyticsapi.models.VolItem]
        The default value is None, needs to be assigned before using.
    cap_volatility : list[~analyticsapi.models.VolItem]
        The default value is None, needs to be assigned before using.
    """

    shift_type: Optional[str] = rest_field(name="shiftType")
    volatility_type: Optional[str] = rest_field(name="volatilityType")
    currency: Optional[str] = rest_field()
    asof: Optional[str] = rest_field()
    term_unit: Optional[Literal["MONTH", "YEAR"]] = rest_field(name="termUnit")
    """Is either a Literal[\"MONTH\"] type or a Literal[\"YEAR\"] type."""
    swaption_volatility: Optional[List["_models.VolItem"]] = rest_field(name="swaptionVolatility")
    cap_volatility: Optional[List["_models.VolItem"]] = rest_field(name="capVolatility")

    @overload
    def __init__(
        self,
        *,
        shift_type: Optional[str] = None,
        volatility_type: Optional[str] = None,
        currency: Optional[str] = None,
        asof: Optional[str] = None,
        term_unit: Optional[Literal["MONTH", "YEAR"]] = None,
        swaption_volatility: Optional[List["_models.VolItem"]] = None,
        cap_volatility: Optional[List["_models.VolItem"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class ValidityPeriod(_model_base.Model):
    """An object to determine the validity period.

    Attributes
    ----------
    start_date : ~datetime.date
        The start date of the validity period. The value is expressed in ISO
        8601 format: YYYY-MM-DD (e.g., 2023-01-01). The default is
        "1950-01-01".
    end_date : ~datetime.date
        The end date of the validity period. The value is expressed in ISO 8601
        format: YYYY-MM-DD (e.g., 2024-01-01). The default is "2050-01-01".
    """

    start_date: Optional[datetime.date] = rest_field(name="startDate")
    """The start date of the validity period. The value is expressed in ISO 8601 format: YYYY-MM-DD
     (e.g., 2023-01-01). The default is \"1950-01-01\"."""
    end_date: Optional[datetime.date] = rest_field(name="endDate")
    """The end date of the validity period. The value is expressed in ISO 8601 format: YYYY-MM-DD
     (e.g., 2024-01-01). The default is \"2050-01-01\"."""

    @overload
    def __init__(
        self,
        *,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class Values(_model_base.Model):
    """An object that contains the bid and ask quotes for the instrument.

    Attributes
    ----------
    bid : ~analyticsapi.models.FieldValue
        An object that contains the bid quote for the instrument.
    ask : ~analyticsapi.models.FieldValue
        An object that contains the ask quote for the instrument.
    """

    bid: Optional["_models.FieldValue"] = rest_field()
    """An object that contains the bid quote for the instrument."""
    ask: Optional["_models.FieldValue"] = rest_field()
    """An object that contains the ask quote for the instrument."""

    @overload
    def __init__(
        self,
        *,
        bid: Optional["_models.FieldValue"] = None,
        ask: Optional["_models.FieldValue"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class VanillaIrsOverride(_model_base.Model):
    """An object that contains interest rate swap properties that can be overridden.

    Attributes
    ----------
    start_date : ~analyticsapi.models.Date
        An object that contains properties to define and adjust the interest
        rate swap start date.
    end_date : ~analyticsapi.models.Date
        An object that contains properties to define and adjust the interest
        rate swap end date.
    amount : float
        The principal amount of the interest rate swap.
    fixed_rate : ~analyticsapi.models.Rate
        An object that contains properties to override the fixed rate of the
        interest rate swap.
    spread : ~analyticsapi.models.Rate
        An object that contains properties to override the interet rate swap
        spread over the floating rate index.
    payer_receiver : str or ~analyticsapi.models.PayerReceiverEnum
        A flag that defines whether the interest rate swap is a fixed rate
        payer or receiver. Known values are: "Payer" and "Receiver".
    """

    start_date: Optional["_models.Date"] = rest_field(name="startDate")
    """An object that contains properties to define and adjust the interest rate swap start date."""
    end_date: Optional["_models.Date"] = rest_field(name="endDate")
    """An object that contains properties to define and adjust the interest rate swap end date."""
    amount: Optional[float] = rest_field()
    """The principal amount of the interest rate swap."""
    fixed_rate: Optional["_models.Rate"] = rest_field(name="fixedRate")
    """An object that contains properties to override the fixed rate of the interest rate swap."""
    spread: Optional["_models.Rate"] = rest_field()
    """An object that contains properties to override the interet rate swap spread over the floating
     rate index."""
    payer_receiver: Optional[Union[str, "_models.PayerReceiverEnum"]] = rest_field(name="payerReceiver")
    """A flag that defines whether the interest rate swap is a fixed rate payer or receiver. Known
     values are: \"Payer\" and \"Receiver\"."""

    @overload
    def __init__(
        self,
        *,
        start_date: Optional["_models.Date"] = None,
        end_date: Optional["_models.Date"] = None,
        amount: Optional[float] = None,
        fixed_rate: Optional["_models.Rate"] = None,
        spread: Optional["_models.Rate"] = None,
        payer_receiver: Optional[Union[str, "_models.PayerReceiverEnum"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class Vector(_model_base.Model):
    """Vector.

    Attributes
    ----------
    interpolation_type : str
        How the draw amount should be determined in between specified vector
        months. Is either a Literal["INTERPOLATED"] type or a Literal["LEVEL"]
        type.
    index : str
    values_property : list[~analyticsapi.models.MonthRatePair]
        The default value is None, needs to be assigned before using.
    """

    interpolation_type: Optional[Literal["INTERPOLATED", "LEVEL"]] = rest_field(name="interpolationType")
    """How the draw amount should be determined in between specified vector months. Is either a
     Literal[\"INTERPOLATED\"] type or a Literal[\"LEVEL\"] type."""
    index: Optional[str] = rest_field()
    values_property: Optional[List["_models.MonthRatePair"]] = rest_field(name="values")

    @overload
    def __init__(
        self,
        *,
        interpolation_type: Optional[Literal["INTERPOLATED", "LEVEL"]] = None,
        index: Optional[str] = None,
        values_property: Optional[List["_models.MonthRatePair"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class Volatility(_model_base.Model):
    """Volatility.

    Attributes
    ----------
    type : str
        Term structure model selection. Is one of the following types:
        Literal["Single"], Literal["Long"], Literal["Market"],
        Literal["Historical"], Literal["MarketWSkew"], Literal["MatrixWSkew"],
        Literal["Matrix"], Literal["1-Factor"], Literal["1FMeanReversion"],
        Literal["1FNormal"], Literal["LMMSkew"], Literal["LMMSkewOIS"],
        Literal["LMMSkewOld"], Literal["LMMDL"], Literal["LMMDLMOD"],
        Literal["LMMDD"], Literal["LMMCMI"], Literal["LMMCMI2"],
        Literal["LMMALTDD"], Literal["LMMSOFR"], Literal["LMMSOFR2"],
        Literal["LMMSOFRFLAT"], Literal["LMMSCMI2"], Literal["LMMTONAR"],
        Literal["Default"], Literal["1FMeanReversionLogNormal"],
        Literal["1FMeanReversionNormal"]
    rate : float
        Volatility rate input, only needed if type selection is SINGLE.
    structure_note : ~analyticsapi.models.StructureNote
    user_defined : ~analyticsapi.models.JsonRef
    """

    type: Optional[
        Literal[
            "Single",
            "Long",
            "Market",
            "Historical",
            "MarketWSkew",
            "MatrixWSkew",
            "Matrix",
            "1-Factor",
            "1FMeanReversion",
            "1FNormal",
            "LMMSkew",
            "LMMSkewOIS",
            "LMMSkewOld",
            "LMMDL",
            "LMMDLMOD",
            "LMMDD",
            "LMMCMI",
            "LMMCMI2",
            "LMMALTDD",
            "LMMSOFR",
            "LMMSOFR2",
            "LMMSOFRFLAT",
            "LMMSCMI2",
            "LMMTONAR",
            "Default",
            "1FMeanReversionLogNormal",
            "1FMeanReversionNormal",
        ]
    ] = rest_field(default=None)
    """Term structure model selection. Is one of the following types: Literal[\"Single\"],
     Literal[\"Long\"], Literal[\"Market\"], Literal[\"Historical\"], Literal[\"MarketWSkew\"],
     Literal[\"MatrixWSkew\"], Literal[\"Matrix\"], Literal[\"1-Factor\"],
     Literal[\"1FMeanReversion\"], Literal[\"1FNormal\"], Literal[\"LMMSkew\"],
     Literal[\"LMMSkewOIS\"], Literal[\"LMMSkewOld\"], Literal[\"LMMDL\"], Literal[\"LMMDLMOD\"],
     Literal[\"LMMDD\"], Literal[\"LMMCMI\"], Literal[\"LMMCMI2\"], Literal[\"LMMALTDD\"],
     Literal[\"LMMSOFR\"], Literal[\"LMMSOFR2\"], Literal[\"LMMSOFRFLAT\"], Literal[\"LMMSCMI2\"],
     Literal[\"LMMTONAR\"], Literal[\"Default\"], Literal[\"1FMeanReversionLogNormal\"],
     Literal[\"1FMeanReversionNormal\"]"""
    rate: Optional[float] = rest_field()
    """Volatility rate input, only needed if type selection is SINGLE."""
    structure_note: Optional["_models.StructureNote"] = rest_field(name="structureNote")
    user_defined: Optional["_models.JsonRef"] = rest_field(name="userDefined")

    @overload
    def __init__(
        self,
        *,
        type: Optional[
            Literal[
                "Single",
                "Long",
                "Market",
                "Historical",
                "MarketWSkew",
                "MatrixWSkew",
                "Matrix",
                "1-Factor",
                "1FMeanReversion",
                "1FNormal",
                "LMMSkew",
                "LMMSkewOIS",
                "LMMSkewOld",
                "LMMDL",
                "LMMDLMOD",
                "LMMDD",
                "LMMCMI",
                "LMMCMI2",
                "LMMALTDD",
                "LMMSOFR",
                "LMMSOFR2",
                "LMMSOFRFLAT",
                "LMMSCMI2",
                "LMMTONAR",
                "Default",
                "1FMeanReversionLogNormal",
                "1FMeanReversionNormal",
            ]
        ] = None,
        rate: Optional[float] = None,
        structure_note: Optional["_models.StructureNote"] = None,
        user_defined: Optional["_models.JsonRef"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class VolCubePoint(_model_base.Model):
    """An object describing a point in the cube.

    Attributes
    ----------
    expiry_tenor : str
        The expiry tenor of the option related to the volatility. Required.
    underlying_expiry_tenor : str
        The expiry tenor of the underlying instrument of the option. Required.
    strike : float
        The strike value related to the volatility. Required.
    volatility : float
        The volatility expressed as a float. Required.
    """

    expiry_tenor: str = rest_field(name="expiryTenor")
    """The expiry tenor of the option related to the volatility. Required."""
    underlying_expiry_tenor: str = rest_field(name="underlyingExpiryTenor")
    """The expiry tenor of the underlying instrument of the option. Required."""
    strike: float = rest_field()
    """The strike value related to the volatility. Required."""
    volatility: float = rest_field()
    """The volatility expressed as a float. Required."""

    @overload
    def __init__(
        self,
        *,
        expiry_tenor: str,
        underlying_expiry_tenor: str,
        strike: float,
        volatility: float,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class VolItem(_model_base.Model):
    """VolItem.

    Attributes
    ----------
    expiration : ~decimal.Decimal
    value : ~decimal.Decimal
    term : ~decimal.Decimal
    """

    expiration: Optional[decimal.Decimal] = rest_field()
    value: Optional[decimal.Decimal] = rest_field()
    term: Optional[decimal.Decimal] = rest_field()

    @overload
    def __init__(
        self,
        *,
        expiration: Optional[decimal.Decimal] = None,
        value: Optional[decimal.Decimal] = None,
        term: Optional[decimal.Decimal] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class VolSurfacePoint(_model_base.Model):
    """An object describing a point in the surface.

    Attributes
    ----------
    expiry_date : ~datetime.date
        The expiry date of the option related to the volatility. Required.
    strike : float
        The strike of the option related to the volatility. Required.
    volatility : float
        The volatility of the related option expressed as a float. Required.
    """

    expiry_date: datetime.date = rest_field(name="expiryDate")
    """The expiry date of the option related to the volatility. Required."""
    strike: float = rest_field()
    """The strike of the option related to the volatility. Required."""
    volatility: float = rest_field()
    """The volatility of the related option expressed as a float. Required."""

    @overload
    def __init__(
        self,
        *,
        expiry_date: datetime.date,
        strike: float,
        volatility: float,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)


class YBPortUserBond(_model_base.Model):
    """YBPortUserBond.

    Attributes
    ----------
    id : str
    extends : ~analyticsapi.models.UDIExtension
    indic : dict[str, any]
    schedule : dict[str, list[~analyticsapi.models.ScheduleItem]]
    distribution : ~analyticsapi.models.Distribution
    """

    id: Optional[str] = rest_field()
    extends: Optional["_models.UDIExtension"] = rest_field()
    indic: Optional[Dict[str, Any]] = rest_field()
    schedule: Optional[Dict[str, List["_models.ScheduleItem"]]] = rest_field()
    distribution: Optional["_models.Distribution"] = rest_field()

    @overload
    def __init__(
        self,
        *,
        id: Optional[str] = None,  # pylint: disable=redefined-builtin
        extends: Optional["_models.UDIExtension"] = None,
        indic: Optional[Dict[str, Any]] = None,
        schedule: Optional[Dict[str, List["_models.ScheduleItem"]]] = None,
        distribution: Optional["_models.Distribution"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        Parameters
        ----------
        mapping : Mapping[str, Any]
            raw JSON to initialize the model.
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pylint: disable=useless-super-delegation
        super().__init__(*args, **kwargs)
