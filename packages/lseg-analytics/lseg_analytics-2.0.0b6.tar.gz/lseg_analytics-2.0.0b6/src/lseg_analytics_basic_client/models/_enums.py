# coding=utf-8


from enum import Enum

from corehttp.utils import CaseInsensitiveEnumMeta


class AmortizationTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of amortization."""

    LINEAR = "Linear"
    """The amount repaid is the same each period, so the remaining amount decreases linearly."""
    ANNUITY = "Annuity"
    """The amount repaid is low at the beginning of the term and increases towards the end."""


class AsianTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of AsianTypeEnum."""

    PRICE = "Price"
    STRIKE = "Strike"


class AverageTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of AverageTypeEnum."""

    ARITHMETIC = "Arithmetic"
    GEOMETRIC = "Geometric"


class BarrierModeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of BarrierModeEnum."""

    AMERICAN = "American"
    EUROPEAN = "European"
    BERMUDAN = "Bermudan"


class BinaryTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of BinaryTypeEnum."""

    ONE_TOUCH = "OneTouch"
    NO_TOUCH = "NoTouch"
    DIGITAL = "Digital"


class CallPutEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of CallPutEnum."""

    CALL = "Call"
    PUT = "Put"


class CapFloorTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of an interest rate cap or an interest rate floor."""

    STANDARD = "Standard"
    """The cap or floor value applies to each interest period of the instrument."""
    PERIODIC = "Periodic"
    """The cap or floor value is incremented for each new interest period of the instrument."""
    LIFE_TIME = "LifeTime"
    """The cap or floor applies to the cumulative value of the interest paid over the life of the
    instrument.
    """
    FIRST_PERIOD = "FirstPeriod"
    """The cap or floor applies only to the first interest period of the instrument."""


class CompoundingModeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The mode used to define how the interest rate is calculated from the reset floating rates when
    the reset frequency is higher than the interest payment frequency (e.g., daily index reset with
    quarterly interest payments).
    """

    COMPOUNDING = "Compounding"
    """The mode uses the compounded average rate from multiple fixings."""
    AVERAGE = "Average"
    """The mode uses the arithmetic average rate from multiple fixings."""
    CONSTANT = "Constant"
    """The mode uses the last published rate among multiple fixings."""
    ADJUSTED_COMPOUNDED = "AdjustedCompounded"
    """The mode uses Chinese 7-day repo fixing."""
    MEXICAN_COMPOUNDED = "MexicanCompounded"
    """The mode uses Mexican Bremse fixing."""


class ConvexityAdjustmentMethodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The convexity adjustment method."""

    BLACK_SCHOLES = "BlackScholes"
    """The Black-Scholes method is based on the assumption that the forward swap rate follows a
    lognormal process.
    """
    LINEAR_SWAP_MODEL = "LinearSwapModel"
    """A linear swap model addresses the non-linear relationship between interest rates and the price
    of a swap.
    """
    REPLICATION = "Replication"
    """The method attempts to replicate the payoff of a CMS structure by means of European swaptions
    of various strikes, regardless of the nature of the underlying process.
    """


class CouponReferenceDateEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The reference date for the interest payment date calculation."""

    PERIOD_START_DATE = "PeriodStartDate"
    """The reference date is the start date of the interest period."""
    PERIOD_END_DATE = "PeriodEndDate"
    """The reference date is the end date of the interest period."""


class CurveTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The enum that lists the type of curves supported."""

    IR_ZC_CURVE = "IrZcCurve"
    FX_OUTRIGHT_CURVE = "FxOutrightCurve"
    DIVIDEND_CURVE = "DividendCurve"


class DateMovingConvention(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The method to adjust dates to working days."""

    MODIFIED_FOLLOWING = "ModifiedFollowing"
    """Dates are moved to the next working day unless it falls in the next month, in which case the
    PreviousBusinessDay convention is used.
    """
    NEXT_BUSINESS_DAY = "NextBusinessDay"
    """Dates are moved to the next working day."""
    PREVIOUS_BUSINESS_DAY = "PreviousBusinessDay"
    """Dates are moved to the previous working day."""
    NO_MOVING = "NoMoving"
    """Dates are not adjusted."""
    EVERY_THIRD_WEDNESDAY = "EveryThirdWednesday"
    """Dates are moved to the third Wednesday of the month, or to the next working day if the third
    Wednesday is not a working day.
    """
    BBSW_MODIFIED_FOLLOWING = "BbswModifiedFollowing"
    """Dates are moved to the next working day unless it falls in the next month, or crosses mid-month
    (15th). In such case, the PreviousBusinessDay convention is used.
    """


class DateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies how a date is defined."""

    ADJUSTABLE_DATE = "AdjustableDate"
    """The date is defined as adjustable according the BusinessDayAdjustmentDefinition."""
    RELATIVE_ADJUSTABLE_DATE = "RelativeAdjustableDate"
    """The date is defined as adjusteable according the BusinessDayAdjustmentDefinition and relative
    to a reference date and a tenor.
    """


class DayCountBasis(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The day count basis convention used to calculate the period between two dates."""

    DCB_30_360 = "Dcb_30_360"
    """For two dates (Y1,M1,D1) and (Y2,M2,D2) the number of days in the period is defined as:
    (D2−D1)+(M2−M1)×30+(Y2−Y1)×360. The year basis is 360 days.

    Date adjustment rules (to be applied in order):

    #. If D1 is the last day of the month, change D1 to 30.
    #. If D1=30, then D2=min(D2,30).
    """
    DCB_30_360_US = "Dcb_30_360_US"
    """For two dates (Y1,M1,D1) and (Y2,M2,D2) the number of days in the period is defined as:
    (D2−D1)+(M2−M1)×30+(Y2−Y1)×360. The year basis is 360 days.

    Date adjustment rules (to be applied in order):

    #. If D1 is the last day of the month, change D1 to 30.
    #. If D1=30 then, D2=min(D2,30).
    #. If D1 and D2 are the last day of February, then D2=30.
    """
    DCB_30_360_GERMAN = "Dcb_30_360_German"
    """For two dates (Y1,M1,D1) and (Y2,M2,D2) the number of days in the period is defined as:
    (D2−D1)+(M2−M1)×30+(Y2−Y1)×360. The year basis is 360 days.

    Date adjustment rules (to be applied in order):

    #. If D1 or D2 is 31, change it to 30.
    #. If D1 or D2 is February 29th, change it to 30.
    """
    DCB_30_360_ISDA = "Dcb_30_360_ISDA"
    """For two dates (Y1,M1,D1) and (Y2,M2,D2) the number of days in the period is defined as:
    (D2−D1)+(M2−M1)×30+(Y2−Y1)×360. The year basis is 360 days.

    Date adjustment rules (to be applied in order):

    #. D1=min(D1,30).
    #. If D1=30, then D2=min(D2,30).
    """
    DCB_30_365_ISDA = "Dcb_30_365_ISDA"
    """Similar to Dcb_30_360_ISDA convention, except that the year basis is 365 days."""
    DCB_30_365_GERMAN = "Dcb_30_365_German"
    """Similar to Dcb_30_360_German convention, except that the year basis is 365 days."""
    DCB_30_365_BRAZIL = "Dcb_30_365_Brazil"
    """Similar to Dcb_30_360_US convention, except that the year basis is 365 days."""
    DCB_30_ACTUAL_GERMAN = "Dcb_30_Actual_German"
    """Similar to Dcb_30_360_German convention, except that the year basis is the actual number of
    days in the year.
    """
    DCB_30_ACTUAL = "Dcb_30_Actual"
    """Similar to Dcb_30_360_US convention, except that the year basis is the actual number of days in
    the year.
    """
    DCB_30_ACTUAL_ISDA = "Dcb_30_Actual_ISDA"
    """Similar to Dcb_30_360_ISDA convention, except that the year basis is the actual number of days
    in the year.
    """
    DCB_30_E_360_ISMA = "Dcb_30E_360_ISMA"
    """The actual number of days in the coupon period is used.
    But it is calculated on the year basis of 360 days with twelve 30-day months (regardless of the
    date of the first day or last day of the period).
    """
    DCB_ACTUAL_360 = "Dcb_Actual_360"
    """The actual number of days in the period is used. The year basis is 360 days."""
    DCB_ACTUAL_364 = "Dcb_Actual_364"
    """The actual number of days in the period is used. The year basis is 364 days."""
    DCB_ACTUAL_365 = "Dcb_Actual_365"
    """The actual number of days in the period is used. The year basis is 365 days."""
    DCB_ACTUAL_ACTUAL = "Dcb_Actual_Actual"
    """The actual number of days in the period is used. The year basis is the actual number of days in
    the year.
    """
    DCB_ACTUAL_ACTUAL_ISDA = "Dcb_Actual_Actual_ISDA"
    """Similar to Dcb_Actual_365 convention, except that on a leap year the year basis is 366 days.
    The period is calculated as: the number of days in a leap year/366 + the number of days in a
    non-leap year/365.
    """
    DCB_ACTUAL_ACTUAL_AFB = "Dcb_Actual_Actual_AFB"
    """The actual number of days in the period is used. The year basis is 366 days if the calculation
    period contains February 29th, otherwise it is 365 days.
    """
    DCB_WORKING_DAYS_252 = "Dcb_WorkingDays_252"
    """The actual number of business days in the period according to a given calendar is used. The
    year basis is 252 days.
    """
    DCB_ACTUAL_365_L = "Dcb_Actual_365L"
    """The actual number of days in the period is used. The year basis is calculated as follows:
    If the coupon frequency is annual and February 29th is included in the period, the year basis
    is 366 days, otherwise it is 365 days.
    If the coupon frequency is not annual, the year basis is 366 days for each coupon period whose
    end date falls in a leap year, otherwise it is 365.
    """
    DCB_ACTUAL_365_P = "Dcb_Actual_365P"
    DCB_ACTUAL_LEAP_DAY_365 = "Dcb_ActualLeapDay_365"
    """The actual number of days in the period is used, but February 29th is ignored for a leap year
    when counting days. The year basis is 365 days."""
    DCB_ACTUAL_LEAP_DAY_360 = "Dcb_ActualLeapDay_360"
    """The actual number of days in the period is used, but February 29th is ignored for a leap year
    when counting days. The year basis is 360 days.
    """
    DCB_ACTUAL_36525 = "Dcb_Actual_36525"
    """The actual number of days in the period is used. The year basis is 365.25 days."""
    DCB_ACTUAL_365_CANADIAN_CONVENTION = "Dcb_Actual_365_CanadianConvention"
    """The actual number of days in the period is used. If it is less than one regular coupon period,
    the year basis is 365 days.
    Otherwise, the day count is defined as: 1 – days remaining in the period x Frequency / 365.
    In most cases, Canadian domestic bonds have semiannual coupons.
    """


class Direction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """An indicator of whether the observation period falls before or after the reference point."""

    BEFORE = "Before"
    AFTER = "After"


class DirectionEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The direction of date calculation."""

    BACKWARD = "Backward"
    """The date is calculated backward."""
    FORWARD = "Forward"
    """The date is calculated forward."""


class DurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of holiday duration. Possible values are FullDayDuration (full days) or
    HalfDayDuration (half days).
    """

    FULL_DAY_DURATION = "FullDayDuration"
    """Full day holidays."""
    HALF_DAY_DURATION = "HalfDayDuration"
    """Half day holidays. Designed to account for the days the markets are open, but not for a full
    trading session.
    """


class EndOfMonthConvention(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies how ends of months are managed when generating date schedules."""

    LAST = "Last"
    """Dates are set to the last working day."""
    SAME = "Same"
    """Dates are set to the same day, if possible, otherwise, they are moved to the last day. The
    adjusted date is also moved if it is a non-working day, according to the convention set by
    DateMovingConvention.
    """
    LAST28 = "Last28"
    """Dates are set to the last day of the month as with Last, but never February 29. For example, a
    semi-annual bond with this convention maturing on August 31 pays coupons on August 31 and
    February 28, even in a leap year.
    """
    SAME28 = "Same28"
    """Dates are set to the same day of the month as with Same, but never February 29."""
    SAME1 = "Same1"
    """Dates are set to the same day of the month as with Same, but payments scheduled for February 29
    are moved to March 1 in a non-leap year.
    For example, a semi-annual bond with this convention maturing on August 29 pays coupons:

    * on February 29 and August 29 in a leap year,
    * on March 1 and August 29 in a non-leap year.
    """


class ExerciseStyleEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of ExerciseStyleEnum."""

    EUROPEAN = "European"
    AMERICAN = "American"
    BERMUDAN = "Bermudan"


class ExtrapolationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The extrapolation method used in the curve bootstrapping."""

    CONSTANT = "Constant"
    """The method of constant extrapolation."""
    LINEAR = "Linear"
    """The method of linear extrapolation."""


class Frequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies the the frequency of an event."""

    DAILY = "Daily"
    """The event happens every day."""
    WEEKLY = "Weekly"
    """The event happens every week."""
    BI_WEEKLY = "BiWeekly"
    """The event happens every other week."""
    MONTHLY = "Monthly"
    """The event happens every month."""
    QUARTERLY = "Quarterly"
    """The event happens every quarter."""
    ANUALLY = "Anually"
    """The event happens every year."""


class FrequencyEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies the frequency used in period based calcualtions."""

    ANNUAL = "Annual"
    """Once per year."""
    SEMI_ANNUAL = "SemiAnnual"
    """Twice per year."""
    QUARTERLY = "Quarterly"
    """Four times per year."""
    MONTHLY = "Monthly"
    """Every month."""
    BI_MONTHLY = "BiMonthly"
    """Twice per month."""
    EVERYDAY = "Everyday"
    """Every day."""
    EVERY_WORKING_DAY = "EveryWorkingDay"
    """Every working day."""
    EVERY7_DAYS = "Every7Days"
    """Every seven days."""
    EVERY14_DAYS = "Every14Days"
    """Every 14 days."""
    EVERY28_DAYS = "Every28Days"
    """Every 28 days."""
    EVERY30_DAYS = "Every30Days"
    """Every 30 days."""
    EVERY90_DAYS = "Every90Days"
    """Every 90 days."""
    EVERY91_DAYS = "Every91Days"
    """Every 91 days."""
    EVERY92_DAYS = "Every92Days"
    """Every 92 days."""
    EVERY93_DAYS = "Every93Days"
    """Every 93 days."""
    EVERY4_MONTHS = "Every4Months"
    """Every four months."""
    EVERY180_DAYS = "Every180Days"
    """Every 180 days."""
    EVERY182_DAYS = "Every182Days"
    """Every 182 days."""
    EVERY183_DAYS = "Every183Days"
    """Every 183 days."""
    EVERY184_DAYS = "Every184Days"
    """Every 184 days."""
    EVERY364_DAYS = "Every364Days"
    """Every 364 days."""
    EVERY365_DAYS = "Every365Days"
    """Every 365 days."""
    R2 = "R2"
    """Semiannual: H1 - 182 days, H2 - 183 days."""
    R4 = "R4"
    """Quarterly: Q1 - 91 days, Q2 - 91 days, Q3 - 91 days, Q4 - 92 days."""
    ZERO = "Zero"
    """No frequency set."""
    SCHEDULED = "Scheduled"
    """No fixed interval; frequency is defined by a Schedule field."""


class FxConstituentEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of the instrument used as a constituent."""

    FX_SPOT = "FxSpot"
    FX_FORWARD = "FxForward"
    CURRENCY_BASIS_SWAP = "CurrencyBasisSwap"
    DEPOSIT = "Deposit"


class FxForwardCurveInterpolationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The interpolation method used in the curve bootstrapping."""

    CUBIC_SPLINE = "CubicSpline"
    """The local cubic interpolation of discount factors."""
    CONSTANT = "Constant"
    """The method of constant interpolation."""
    LINEAR = "Linear"
    """The method of linear interpolation."""


class FxRateTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """An enum that describes the type of the values provided in the fx curve."""

    OUTRIGHT = "Outright"
    """The fx curve values are provided as outright rates."""
    SWAPOINT = "Swapoint"
    """The fx curve values are provided as swap points."""


class IdTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of IdTypeEnum."""

    SECURITY_ID_ENTRY = "SecurityIDEntry"
    SECURITY_ID = "SecurityID"
    CUSIP = "CUSIP"
    ISIN = "ISIN"
    REGSISIN = "REGSISIN"
    SEDOL = "SEDOL"
    IDENTIFIER = "Identifier"
    CHINA_INTERBANK_CODE = "ChinaInterbankCode"
    SHANGHAI_EXCHANGE_CODE = "ShanghaiExchangeCode"
    SHENZHEN_EXCHANGE_CODE = "ShenzhenExchangeCode"
    MXTICKER_ID = "MXTickerID"


class IndexObservationMethodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """(RFR) Method for determining the accrual observation period. The number of business days
    between the fixing date and the start or end date of the coupon period is determined by the
    index fixing lag.
    """

    LOOKBACK = "Lookback"
    """The method uses the interest period for both rate accrual and interest payment."""
    PERIOD_SHIFT = "PeriodShift"
    """The method uses the observation period for both rate accrual and interest payment."""
    MIXED = "Mixed"
    """The method uses the observation period for rate accrual and the interest period for interest
    payment.
    """


class IndexOrder(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The ordinal number of the day of the week in the month. For example, to specify the second
    Tuesday of the month, you would use "Second" here, and specify Tuesday elsewhere.
    """

    FIRST = "First"
    SECOND = "Second"
    THIRD = "Third"
    FOURTH = "Fourth"
    LAST = "Last"


class InOrOutEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of InOrOutEnum."""

    IN = "In"
    OUT = "Out"


class InstrumentTemplateTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of instrument represented by the template."""

    INTEREST_RATE_LEG = "InterestRateLeg"
    """An interest rate leg."""
    VANILLA_SWAP = "VanillaSwap"
    """A vanilla interest rate swap contract."""
    TENOR_BASIS_SWAP = "TenorBasisSwap"
    """A tenor basis swap contract."""
    CROSS_CURRENCY_SWAP = "CrossCurrencySwap"
    """A cross currency swap contract."""
    CURRENCY_BASIS_SWAP = "CurrencyBasisSwap"
    """A currency basis swap contract."""
    FX_SPOT = "FxSpot"
    """A FX spot contract contract."""
    FX_FORWARD = "FxForward"
    """A FX forward contract contract."""
    FX_SWAP = "FxSwap"
    """A FX swap contract contract."""
    NON_DELIVERABLE_FORWARD = "NonDeliverableForward"
    """A non-deliverable fx forward contract."""
    DEPOSIT = "Deposit"
    """An interest rate deposit contract."""
    FORWARD_RATE_AGREEMENT = "ForwardRateAgreement"
    """A foward rate agreement contract."""
    MONEY_MARKET_FUTURE = "MoneyMarketFuture"
    """A future contract on short term interest rate."""
    VANILLA_OTC_OPTION = "VanillaOtcOption"
    """Vanilla OTC Option contract."""
    ASIAN_OTC_OPTION = "AsianOtcOption"
    """Asian OTC Option contract."""
    SINGLE_BARRIER_OTC_OPTION = "SingleBarrierOtcOption"
    """Single Barrier OTC Option contract."""
    DOUBLE_BARRIER_OTC_OPTION = "DoubleBarrierOtcOption"
    """Double Barrier OTC Option contract."""
    SINGLE_BINARY_OTC_OPTION = "SingleBinaryOtcOption"
    """Single Binary OTC Option contract."""
    DOUBLE_BINARY_OTC_OPTION = "DoubleBinaryOtcOption"
    """Double Binary OTC Option contract."""


class IntegrationMethodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The integration method used for static replication."""

    RIEMANN_SUM = "RiemannSum"
    """A Riemann sum is the process of summing over the areas of many small rectangles."""
    RUNGE_KUTTA = "RungeKutta"
    """A method of numerically integrating ordinary differential equations by using a trial step at
    the midpoint of an interval to cancel out lower-order error terms.
    """


class InterestRateTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The interest rate type."""

    FIXED_RATE = "FixedRate"
    """A fixed interest rate."""
    STEP_RATE = "StepRate"
    """A variable (step) interest rate schedule."""
    FLOATING_RATE = "FloatingRate"
    """A floating interest rate."""
    FLOATING_RATE_FORMULA = "FloatingRateFormula"
    """A formula of several floating rates."""


class InterestType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies whether an  interest rate is fixed or linked to a floating reference."""

    FIXED = "Fixed"
    """The interest rate is fixed."""
    FLOAT = "Float"
    """The interest rate is linked to a floating reference."""


class Month(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The month of the year. Month names written in full."""

    JANUARY = "January"
    FEBRUARY = "February"
    MARCH = "March"
    APRIL = "April"
    MAY = "May"
    JUNE = "June"
    JULY = "July"
    AUGUST = "August"
    SEPTEMBER = "September"
    OCTOBER = "October"
    NOVEMBER = "November"
    DECEMBER = "December"


class OptionModel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of OptionModel."""

    OAS = "OAS"
    OASEDUR = "OASEDUR"
    YCMARGIN = "YCMARGIN"


class PaidLegEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies which one of the two swap legs being defined is the paid leg."""

    FIRST_LEG = "FirstLeg"
    """The first leg is paid."""
    SECOND_LEG = "SecondLeg"
    """The second leg is paid."""


class PartyEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The parties that participate in a transaction."""

    PARTY1 = "Party1"
    PARTY2 = "Party2"


class PayerReceiverEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies whether a given counterparty pays or receives the a payment."""

    PAYER = "Payer"
    """The counterparty is paying."""
    RECEIVER = "Receiver"
    """The counterparty is receiving."""


class PaymentTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of PaymentTypeEnum."""

    IMMEDIATE = "Immediate"
    DEFERRED = "Deferred"


class PeriodType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The method of the period calculation."""

    WORKING_DAY = "WorkingDay"
    """Only working days are taken into account."""
    NON_WORKING_DAY = "NonWorkingDay"
    """Only non-working days are taken into account."""
    DAY = "Day"
    """All calendar days are taken into account."""
    WEEK = "Week"
    """The period is calculated in weeks."""
    MONTH = "Month"
    """The period is calculated in months."""
    QUARTER = "Quarter"
    """The period is calculated in quarters."""
    YEAR = "Year"
    """The period is calculated in years."""


class PeriodTypeOutput(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of the calculated period. Possible values are: Day, WorkingDay, Week, Month, Quarter
    or Year.
    """

    DAY = "Day"
    """The period is expressed in calendar days."""
    WORKING_DAY = "WorkingDay"
    """The period is expressed in working days."""
    WEEK = "Week"
    """The period is expressed in weeks."""
    MONTH = "Month"
    """The period is expressed in months."""
    QUARTER = "Quarter"
    """The period is expressed in quarters."""
    YEAR = "Year"
    """The period is expressed in years."""


class PositionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of regular annual holiday rule. Possible values are: AbsolutePositionWhen (for fixed
    dates), RelativePositionWhen (for a holiday that falls on a particular weekday in a month), or
    RelativeToRulePositionWhen (for a holiday that depends on the timing of another holiday).
    """

    ABSOLUTE_POSITION_WHEN = "AbsolutePositionWhen"
    """A rule to determine a fixed holiday. For example, New Year holiday on January 1."""
    RELATIVE_POSITION_WHEN = "RelativePositionWhen"
    """A rule to determine a holiday depending on the day of the week in a certain month. For example,
    Summer holiday on the last Monday of August.
    """
    RELATIVE_TO_RULE_POSITION_WHEN = "RelativeToRulePositionWhen"
    """A rule that references another rule. For example, Easter is most commonly used as a reference
    point.
    """


class ReferenceDate(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies the reference date when computing a date from a tenor."""

    SPOT_DATE = "SpotDate"
    """The market spot date is the reference date."""
    START_DATE = "StartDate"
    """The start date of the schedule is the reference date."""
    VALUATION_DATE = "ValuationDate"
    """The valuation date is the reference date."""


class RescheduleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The type of rescheduling for the observation period."""

    LAG_DAYS_RESCHEDULE_DESCRIPTION = "LagDaysRescheduleDescription"
    """The rule for rescheduling a holiday using day lags. For example, if a holiday falls on Sunday,
    it is rescheduled by the number of days defined by the lag.
    """
    RELATIVE_RESCHEDULE_DESCRIPTION = "RelativeRescheduleDescription"
    """The rule for rescheduling a holiday to a specific day. For example, if a holiday falls on
    Sunday, it is rescheduled to the first Monday after the holiday.
    """


class ResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Resource type."""

    CALENDAR = "Calendar"
    FLOATING_RATE_INDEX_DEFINITION = "FloatingRateIndexDefinition"
    INTEREST_RATE_CURVE = "InterestRateCurve"
    FX_FORWARD_CURVE = "FxForwardCurve"
    ANALYTICS = "Analytics"
    LOAN = "Loan"
    FX_SPOT = "FxSpot"
    FX_FORWARD = "FxForward"
    NON_DELIVERABLE_FORWARD = "NonDeliverableForward"
    DEPOSIT = "Deposit"
    SPACE = "Space"
    IR_SWAP = "IrSwap"
    IR_LEG = "IrLeg"
    FLOATING_RATE_INDEX = "FloatingRateIndex"
    INSTRUMENT = "Instrument"
    INSTRUMENT_TEMPLATE = "InstrumentTemplate"
    FORWARD_RATE_AGREEMENT = "ForwardRateAgreement"
    OPTION = "Option"
    FINANCIAL_MODEL = "FinancialModel"
    EQ_VOL_SURFACE = "EqVolSurface"
    FX_VOL_SURFACE = "FxVolSurface"
    CMDTY_VOL_SURFACE = "CmdtyVolSurface"
    IR_CAP_VOL_SURFACE = "IrCapVolSurface"
    IR_SWAPTION_VOL_CUBE = "IrSwaptionVolCube"


class RoundingModeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The direction of the rounding."""

    CEILING = "Ceiling"
    """The number is rounded to the minimum of the closest value and the ceiling."""
    DOWN = "Down"
    """The number is truncated."""
    FLOOR = "Floor"
    """The number is rounded to the maximum of the closest value and the floor."""
    NEAR = "Near"
    """The number is rounded to the closest value."""
    UP = "Up"
    """The number is truncated and 1 is added to the previous decimal value."""


class SettlementType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies whether a payment is made by exchanging a cash amount or a physical asset."""

    CASH = "Cash"
    """A cash amount is exchanged."""
    PHYSICAL = "Physical"
    """A physical asset is exchanged."""


class SolvingLegEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """A swap leg to which the the target or variable property applies."""

    FIRST_LEG = "FirstLeg"
    """The solution is calculated for the first leg."""
    SECOND_LEG = "SecondLeg"
    """The solution is calculated for the second leg."""


class SolvingMethodEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The method used to select the variable parameter value."""

    BI_SECTION = "BiSection"
    """An approximation method to find the roots of the given equation by repeatedly dividing an
    interval in half until it narrows down to a root.
    """
    BRENT = "Brent"
    """A hybrid root-finding algorithm combining the bisection method, the secant method and inverse
    quadratic interpolation.
    """
    SECANT = "Secant"
    """A root-finding procedure in numerical analysis that uses a series of roots of secant lines to
    better approximate a root of a continoius function.
    """


class SortingOrderEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of SortingOrderEnum."""

    ASC = "Asc"
    DESC = "Desc"


class SpreadCompoundingModeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The mode used to define how the spread is applied to a compound interest rate."""

    ISDA_COMPOUNDING = "IsdaCompounding"
    """The index and the spread are compounded together."""
    ISDA_FLAT_COMPOUNDING = "IsdaFlatCompounding"
    """The spread is compounded with the index only for the first reset. After that only the index is
    compounded.
    """
    NO_COMPOUNDING = "NoCompounding"
    """The spread is not compounded. It is added to the compounded index."""


class Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The status of the resource."""

    ACTIVE = "Active"
    DELETED = "Deleted"


class StoreType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of StoreType."""

    TABLE = "table"
    CURVE = "curve"
    PREPAY_DIALS = "prepay-dials"
    OUTPUT_FORMAT = "output-format"
    VOL_SURFACE = "vol-surface"
    YBPORT_UDI = "ybport-udi"
    CMO_MODIFICATION = "cmo-modification"
    SCENARIO_V1 = "scenario-v1"
    CURRENT_COUPON_SPREAD = "currentCouponSpread"


class StrikeTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """An object defining the way the strike price is expressed when constructing the volatility
    surface.
    """

    ABSOLUTE = "Absolute"
    BASIS_POINT = "BasisPoint"
    DELTA = "Delta"
    MONEYNESS = "Moneyness"
    PERCENT = "Percent"
    RELATIVE = "Relative"


class StubRuleEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Specifies whether the first or last coupon period is unregular."""

    LONG_FIRST = "LongFirst"
    """All payment dates are calculated backwards from the end date of the schedule. The generation
    stops so that the first period is a long period.
    """
    LONG_LAST = "LongLast"
    """All payment dates are calculated backwards from the start date of the schedule. The generation
    stops so that the last period is a long period.
    """
    SHORT_FIRST = "ShortFirst"
    """All payment dates are calculated backwards from the end date of the schedule. The generation
    stops so that the first period is a short period.
    """
    SHORT_LAST = "ShortLast"
    """All payment dates are calculated backwards from the start date of the schedule. The generation
    stops so that the last period is a short period.
    """


class SwapSolvingVariableEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The list of swap variable parameters for which the solution is calculated."""

    FIXED_RATE = "FixedRate"
    """The solution is calculated for the fixed rate."""
    SPREAD = "Spread"
    """The solution is calculated for the spread."""


class TenorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The tenor type."""

    ODD = "Odd"
    """A period selected from a list that includes both standard and non-standard periods.
    The standard periods are: ON, TN, SN, SW, 1M, 2M, 3M, 6M, 9M, 1Y, 2Y.
    The non-standard periods are: 2W, 3W, 2M, 4M, 5M, 7M, 8M, 10M, 11M, 15M, 18M, 21M.
    """
    LONG = "Long"
    """Long-term tenor. The length of long-term tenors depends on the asset class."""
    IMM = "IMM"
    """The end date of the tenor is the third Wednesday of either: March, June, September or December.

    * IMM1 means the next of the 4 possible days.
    * IMM2 means the one after next of the 4 possible days.
    * IMM3 means the second after next of the 4 possible days.
    * IMM4 means the third after next of the 4 possible days.
      For example, if the current date is 23rd of April, IMM1 is the third Wdnesday in June, IMM2
    is the third wednesday in September, etc..
    """
    BEGINNING_OF_MONTH = "BeginningOfMonth"
    """The end date of the tenor is the first business day of a month.
    Possible values are: JANB, FEBB, MARB, APRB, MAYB, JUNB, JULB, AUGB, SEPB, OCTB, NOVB, DECB.
    The first three letters of each value represents the month. So, JANB is the first business day
    of January, FEBB is the first business day of February, etc..
    """
    END_OF_MONTH = "EndOfMonth"
    """The end date of the tenor is the last business day of a month.
    Possible values are: JANM, FEBM, MARM, APRM, MAYM, JUNM, JULM, AUGM, SEPM, OCTM, NOVM, DECM.
    The first three letters of each value represents the month. So, JANM is the last business day
    of January, FEBM is the last business day of February, etc..
    """


class TimezoneEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of TimezoneEnum."""

    AFRICA_ABIDJAN = "Africa/Abidjan"
    AFRICA_ACCRA = "Africa/Accra"
    AFRICA_ADDIS_ABABA = "Africa/Addis_Ababa"
    AFRICA_ALGIERS = "Africa/Algiers"
    AFRICA_ASMARA = "Africa/Asmara"
    AFRICA_ASMERA = "Africa/Asmera"
    AFRICA_BAMAKO = "Africa/Bamako"
    AFRICA_BANGUI = "Africa/Bangui"
    AFRICA_BANJUL = "Africa/Banjul"
    AFRICA_BISSAU = "Africa/Bissau"
    AFRICA_BLANTYRE = "Africa/Blantyre"
    AFRICA_BRAZZAVILLE = "Africa/Brazzaville"
    AFRICA_BUJUMBURA = "Africa/Bujumbura"
    AFRICA_CAIRO = "Africa/Cairo"
    AFRICA_CASABLANCA = "Africa/Casablanca"
    AFRICA_CEUTA = "Africa/Ceuta"
    AFRICA_CONAKRY = "Africa/Conakry"
    AFRICA_DAKAR = "Africa/Dakar"
    AFRICA_DAR_ES_SALAAM = "Africa/Dar_es_Salaam"
    AFRICA_DJIBOUTI = "Africa/Djibouti"
    AFRICA_DOUALA = "Africa/Douala"
    AFRICA_EL_AAIUN = "Africa/El_Aaiun"
    AFRICA_FREETOWN = "Africa/Freetown"
    AFRICA_GABORONE = "Africa/Gaborone"
    AFRICA_HARARE = "Africa/Harare"
    AFRICA_JOHANNESBURG = "Africa/Johannesburg"
    AFRICA_JUBA = "Africa/Juba"
    AFRICA_KAMPALA = "Africa/Kampala"
    AFRICA_KHARTOUM = "Africa/Khartoum"
    AFRICA_KIGALI = "Africa/Kigali"
    AFRICA_KINSHASA = "Africa/Kinshasa"
    AFRICA_LAGOS = "Africa/Lagos"
    AFRICA_LIBREVILLE = "Africa/Libreville"
    AFRICA_LOME = "Africa/Lome"
    AFRICA_LUANDA = "Africa/Luanda"
    AFRICA_LUBUMBASHI = "Africa/Lubumbashi"
    AFRICA_LUSAKA = "Africa/Lusaka"
    AFRICA_MALABO = "Africa/Malabo"
    AFRICA_MAPUTO = "Africa/Maputo"
    AFRICA_MASERU = "Africa/Maseru"
    AFRICA_MBABANE = "Africa/Mbabane"
    AFRICA_MOGADISHU = "Africa/Mogadishu"
    AFRICA_MONROVIA = "Africa/Monrovia"
    AFRICA_NAIROBI = "Africa/Nairobi"
    AFRICA_NDJAMENA = "Africa/Ndjamena"
    AFRICA_NIAMEY = "Africa/Niamey"
    AFRICA_NOUAKCHOTT = "Africa/Nouakchott"
    AFRICA_OUAGADOUGOU = "Africa/Ouagadougou"
    AFRICA_PORTO_NOVO = "Africa/Porto-Novo"
    AFRICA_SAO_TOME = "Africa/Sao_Tome"
    AFRICA_TIMBUKTU = "Africa/Timbuktu"
    AFRICA_TRIPOLI = "Africa/Tripoli"
    AFRICA_TUNIS = "Africa/Tunis"
    AFRICA_WINDHOEK = "Africa/Windhoek"
    AMERICA_ADAK = "America/Adak"
    AMERICA_ANCHORAGE = "America/Anchorage"
    AMERICA_ANGUILLA = "America/Anguilla"
    AMERICA_ANTIGUA = "America/Antigua"
    AMERICA_ARAGUAINA = "America/Araguaina"
    AMERICA_ARGENTINA_BUENOS_AIRES = "America/Argentina/Buenos_Aires"
    AMERICA_ARGENTINA_CATAMARCA = "America/Argentina/Catamarca"
    AMERICA_ARGENTINA_COMOD_RIVADAVIA = "America/Argentina/ComodRivadavia"
    AMERICA_ARGENTINA_CORDOBA = "America/Argentina/Cordoba"
    AMERICA_ARGENTINA_JUJUY = "America/Argentina/Jujuy"
    AMERICA_ARGENTINA_LA_RIOJA = "America/Argentina/La_Rioja"
    AMERICA_ARGENTINA_MENDOZA = "America/Argentina/Mendoza"
    AMERICA_ARGENTINA_RIO_GALLEGOS = "America/Argentina/Rio_Gallegos"
    AMERICA_ARGENTINA_SALTA = "America/Argentina/Salta"
    AMERICA_ARGENTINA_SAN_JUAN = "America/Argentina/San_Juan"
    AMERICA_ARGENTINA_SAN_LUIS = "America/Argentina/San_Luis"
    AMERICA_ARGENTINA_TUCUMAN = "America/Argentina/Tucuman"
    AMERICA_ARGENTINA_USHUAIA = "America/Argentina/Ushuaia"
    AMERICA_ARUBA = "America/Aruba"
    AMERICA_ASUNCION = "America/Asuncion"
    AMERICA_ATIKOKAN = "America/Atikokan"
    AMERICA_ATKA = "America/Atka"
    AMERICA_BAHIA = "America/Bahia"
    AMERICA_BAHIA_BANDERAS = "America/Bahia_Banderas"
    AMERICA_BARBADOS = "America/Barbados"
    AMERICA_BELEM = "America/Belem"
    AMERICA_BELIZE = "America/Belize"
    AMERICA_BLANC_SABLON = "America/Blanc-Sablon"
    AMERICA_BOA_VISTA = "America/Boa_Vista"
    AMERICA_BOGOTA = "America/Bogota"
    AMERICA_BOISE = "America/Boise"
    AMERICA_BUENOS_AIRES = "America/Buenos_Aires"
    AMERICA_CAMBRIDGE_BAY = "America/Cambridge_Bay"
    AMERICA_CAMPO_GRANDE = "America/Campo_Grande"
    AMERICA_CANCUN = "America/Cancun"
    AMERICA_CARACAS = "America/Caracas"
    AMERICA_CATAMARCA = "America/Catamarca"
    AMERICA_CAYENNE = "America/Cayenne"
    AMERICA_CAYMAN = "America/Cayman"
    AMERICA_CHICAGO = "America/Chicago"
    AMERICA_CHIHUAHUA = "America/Chihuahua"
    AMERICA_CIUDAD_JUAREZ = "America/Ciudad_Juarez"
    AMERICA_CORAL_HARBOUR = "America/Coral_Harbour"
    AMERICA_CORDOBA = "America/Cordoba"
    AMERICA_COSTA_RICA = "America/Costa_Rica"
    AMERICA_CRESTON = "America/Creston"
    AMERICA_CUIABA = "America/Cuiaba"
    AMERICA_CURACAO = "America/Curacao"
    AMERICA_DANMARKSHAVN = "America/Danmarkshavn"
    AMERICA_DAWSON = "America/Dawson"
    AMERICA_DAWSON_CREEK = "America/Dawson_Creek"
    AMERICA_DENVER = "America/Denver"
    AMERICA_DETROIT = "America/Detroit"
    AMERICA_DOMINICA = "America/Dominica"
    AMERICA_EDMONTON = "America/Edmonton"
    AMERICA_EIRUNEPE = "America/Eirunepe"
    AMERICA_EL_SALVADOR = "America/El_Salvador"
    AMERICA_ENSENADA = "America/Ensenada"
    AMERICA_FORT_NELSON = "America/Fort_Nelson"
    AMERICA_FORT_WAYNE = "America/Fort_Wayne"
    AMERICA_FORTALEZA = "America/Fortaleza"
    AMERICA_GLACE_BAY = "America/Glace_Bay"
    AMERICA_GODTHAB = "America/Godthab"
    AMERICA_GOOSE_BAY = "America/Goose_Bay"
    AMERICA_GRAND_TURK = "America/Grand_Turk"
    AMERICA_GRENADA = "America/Grenada"
    AMERICA_GUADELOUPE = "America/Guadeloupe"
    AMERICA_GUATEMALA = "America/Guatemala"
    AMERICA_GUAYAQUIL = "America/Guayaquil"
    AMERICA_GUYANA = "America/Guyana"
    AMERICA_HALIFAX = "America/Halifax"
    AMERICA_HAVANA = "America/Havana"
    AMERICA_HERMOSILLO = "America/Hermosillo"
    AMERICA_INDIANA_INDIANAPOLIS = "America/Indiana/Indianapolis"
    AMERICA_INDIANA_KNOX = "America/Indiana/Knox"
    AMERICA_INDIANA_MARENGO = "America/Indiana/Marengo"
    AMERICA_INDIANA_PETERSBURG = "America/Indiana/Petersburg"
    AMERICA_INDIANA_TELL_CITY = "America/Indiana/Tell_City"
    AMERICA_INDIANA_VEVAY = "America/Indiana/Vevay"
    AMERICA_INDIANA_VINCENNES = "America/Indiana/Vincennes"
    AMERICA_INDIANA_WINAMAC = "America/Indiana/Winamac"
    AMERICA_INDIANAPOLIS = "America/Indianapolis"
    AMERICA_INUVIK = "America/Inuvik"
    AMERICA_IQALUIT = "America/Iqaluit"
    AMERICA_JAMAICA = "America/Jamaica"
    AMERICA_JUJUY = "America/Jujuy"
    AMERICA_JUNEAU = "America/Juneau"
    AMERICA_KENTUCKY_LOUISVILLE = "America/Kentucky/Louisville"
    AMERICA_KENTUCKY_MONTICELLO = "America/Kentucky/Monticello"
    AMERICA_KNOX_IN = "America/Knox_IN"
    AMERICA_KRALENDIJK = "America/Kralendijk"
    AMERICA_LA_PAZ = "America/La_Paz"
    AMERICA_LIMA = "America/Lima"
    AMERICA_LOS_ANGELES = "America/Los_Angeles"
    AMERICA_LOUISVILLE = "America/Louisville"
    AMERICA_LOWER_PRINCES = "America/Lower_Princes"
    AMERICA_MACEIO = "America/Maceio"
    AMERICA_MANAGUA = "America/Managua"
    AMERICA_MANAUS = "America/Manaus"
    AMERICA_MARIGOT = "America/Marigot"
    AMERICA_MARTINIQUE = "America/Martinique"
    AMERICA_MATAMOROS = "America/Matamoros"
    AMERICA_MAZATLAN = "America/Mazatlan"
    AMERICA_MENDOZA = "America/Mendoza"
    AMERICA_MENOMINEE = "America/Menominee"
    AMERICA_MERIDA = "America/Merida"
    AMERICA_METLAKATLA = "America/Metlakatla"
    AMERICA_MEXICO_CITY = "America/Mexico_City"
    AMERICA_MIQUELON = "America/Miquelon"
    AMERICA_MONCTON = "America/Moncton"
    AMERICA_MONTERREY = "America/Monterrey"
    AMERICA_MONTEVIDEO = "America/Montevideo"
    AMERICA_MONTREAL = "America/Montreal"
    AMERICA_MONTSERRAT = "America/Montserrat"
    AMERICA_NASSAU = "America/Nassau"
    AMERICA_NEW_YORK = "America/New_York"
    AMERICA_NIPIGON = "America/Nipigon"
    AMERICA_NOME = "America/Nome"
    AMERICA_NORONHA = "America/Noronha"
    AMERICA_NORTH_DAKOTA_BEULAH = "America/North_Dakota/Beulah"
    AMERICA_NORTH_DAKOTA_CENTER = "America/North_Dakota/Center"
    AMERICA_NORTH_DAKOTA_NEW_SALEM = "America/North_Dakota/New_Salem"
    AMERICA_NUUK = "America/Nuuk"
    AMERICA_OJINAGA = "America/Ojinaga"
    AMERICA_PANAMA = "America/Panama"
    AMERICA_PANGNIRTUNG = "America/Pangnirtung"
    AMERICA_PARAMARIBO = "America/Paramaribo"
    AMERICA_PHOENIX = "America/Phoenix"
    AMERICA_PORT_AU_PRINCE = "America/Port-au-Prince"
    AMERICA_PORT_OF_SPAIN = "America/Port_of_Spain"
    AMERICA_PORTO_ACRE = "America/Porto_Acre"
    AMERICA_PORTO_VELHO = "America/Porto_Velho"
    AMERICA_PUERTO_RICO = "America/Puerto_Rico"
    AMERICA_PUNTA_ARENAS = "America/Punta_Arenas"
    AMERICA_RAINY_RIVER = "America/Rainy_River"
    AMERICA_RANKIN_INLET = "America/Rankin_Inlet"
    AMERICA_RECIFE = "America/Recife"
    AMERICA_REGINA = "America/Regina"
    AMERICA_RESOLUTE = "America/Resolute"
    AMERICA_RIO_BRANCO = "America/Rio_Branco"
    AMERICA_ROSARIO = "America/Rosario"
    AMERICA_SANTA_ISABEL = "America/Santa_Isabel"
    AMERICA_SANTAREM = "America/Santarem"
    AMERICA_SANTIAGO = "America/Santiago"
    AMERICA_SANTO_DOMINGO = "America/Santo_Domingo"
    AMERICA_SAO_PAULO = "America/Sao_Paulo"
    AMERICA_SCORESBYSUND = "America/Scoresbysund"
    AMERICA_SHIPROCK = "America/Shiprock"
    AMERICA_SITKA = "America/Sitka"
    AMERICA_ST_BARTHELEMY = "America/St_Barthelemy"
    AMERICA_ST_JOHNS = "America/St_Johns"
    AMERICA_ST_KITTS = "America/St_Kitts"
    AMERICA_ST_LUCIA = "America/St_Lucia"
    AMERICA_ST_THOMAS = "America/St_Thomas"
    AMERICA_ST_VINCENT = "America/St_Vincent"
    AMERICA_SWIFT_CURRENT = "America/Swift_Current"
    AMERICA_TEGUCIGALPA = "America/Tegucigalpa"
    AMERICA_THULE = "America/Thule"
    AMERICA_THUNDER_BAY = "America/Thunder_Bay"
    AMERICA_TIJUANA = "America/Tijuana"
    AMERICA_TORONTO = "America/Toronto"
    AMERICA_TORTOLA = "America/Tortola"
    AMERICA_VANCOUVER = "America/Vancouver"
    AMERICA_VIRGIN = "America/Virgin"
    AMERICA_WHITEHORSE = "America/Whitehorse"
    AMERICA_WINNIPEG = "America/Winnipeg"
    AMERICA_YAKUTAT = "America/Yakutat"
    AMERICA_YELLOWKNIFE = "America/Yellowknife"
    ANTARCTICA_CASEY = "Antarctica/Casey"
    ANTARCTICA_DAVIS = "Antarctica/Davis"
    ANTARCTICA_DUMONT_D_URVILLE = "Antarctica/DumontDUrville"
    ANTARCTICA_MACQUARIE = "Antarctica/Macquarie"
    ANTARCTICA_MAWSON = "Antarctica/Mawson"
    ANTARCTICA_MC_MURDO = "Antarctica/McMurdo"
    ANTARCTICA_PALMER = "Antarctica/Palmer"
    ANTARCTICA_ROTHERA = "Antarctica/Rothera"
    ANTARCTICA_SOUTH_POLE = "Antarctica/South_Pole"
    ANTARCTICA_SYOWA = "Antarctica/Syowa"
    ANTARCTICA_TROLL = "Antarctica/Troll"
    ANTARCTICA_VOSTOK = "Antarctica/Vostok"
    ARCTIC_LONGYEARBYEN = "Arctic/Longyearbyen"
    ASIA_ADEN = "Asia/Aden"
    ASIA_ALMATY = "Asia/Almaty"
    ASIA_AMMAN = "Asia/Amman"
    ASIA_ANADYR = "Asia/Anadyr"
    ASIA_AQTAU = "Asia/Aqtau"
    ASIA_AQTOBE = "Asia/Aqtobe"
    ASIA_ASHGABAT = "Asia/Ashgabat"
    ASIA_ASHKHABAD = "Asia/Ashkhabad"
    ASIA_ATYRAU = "Asia/Atyrau"
    ASIA_BAGHDAD = "Asia/Baghdad"
    ASIA_BAHRAIN = "Asia/Bahrain"
    ASIA_BAKU = "Asia/Baku"
    ASIA_BANGKOK = "Asia/Bangkok"
    ASIA_BARNAUL = "Asia/Barnaul"
    ASIA_BEIRUT = "Asia/Beirut"
    ASIA_BISHKEK = "Asia/Bishkek"
    ASIA_BRUNEI = "Asia/Brunei"
    ASIA_CALCUTTA = "Asia/Calcutta"
    ASIA_CHITA = "Asia/Chita"
    ASIA_CHOIBALSAN = "Asia/Choibalsan"
    ASIA_CHONGQING = "Asia/Chongqing"
    ASIA_CHUNGKING = "Asia/Chungking"
    ASIA_COLOMBO = "Asia/Colombo"
    ASIA_DACCA = "Asia/Dacca"
    ASIA_DAMASCUS = "Asia/Damascus"
    ASIA_DHAKA = "Asia/Dhaka"
    ASIA_DILI = "Asia/Dili"
    ASIA_DUBAI = "Asia/Dubai"
    ASIA_DUSHANBE = "Asia/Dushanbe"
    ASIA_FAMAGUSTA = "Asia/Famagusta"
    ASIA_GAZA = "Asia/Gaza"
    ASIA_HARBIN = "Asia/Harbin"
    ASIA_HEBRON = "Asia/Hebron"
    ASIA_HO_CHI_MINH = "Asia/Ho_Chi_Minh"
    ASIA_HONG_KONG = "Asia/Hong_Kong"
    ASIA_HOVD = "Asia/Hovd"
    ASIA_IRKUTSK = "Asia/Irkutsk"
    ASIA_ISTANBUL = "Asia/Istanbul"
    ASIA_JAKARTA = "Asia/Jakarta"
    ASIA_JAYAPURA = "Asia/Jayapura"
    ASIA_JERUSALEM = "Asia/Jerusalem"
    ASIA_KABUL = "Asia/Kabul"
    ASIA_KAMCHATKA = "Asia/Kamchatka"
    ASIA_KARACHI = "Asia/Karachi"
    ASIA_KASHGAR = "Asia/Kashgar"
    ASIA_KATHMANDU = "Asia/Kathmandu"
    ASIA_KATMANDU = "Asia/Katmandu"
    ASIA_KHANDYGA = "Asia/Khandyga"
    ASIA_KOLKATA = "Asia/Kolkata"
    ASIA_KRASNOYARSK = "Asia/Krasnoyarsk"
    ASIA_KUALA_LUMPUR = "Asia/Kuala_Lumpur"
    ASIA_KUCHING = "Asia/Kuching"
    ASIA_KUWAIT = "Asia/Kuwait"
    ASIA_MACAO = "Asia/Macao"
    ASIA_MACAU = "Asia/Macau"
    ASIA_MAGADAN = "Asia/Magadan"
    ASIA_MAKASSAR = "Asia/Makassar"
    ASIA_MANILA = "Asia/Manila"
    ASIA_MUSCAT = "Asia/Muscat"
    ASIA_NICOSIA = "Asia/Nicosia"
    ASIA_NOVOKUZNETSK = "Asia/Novokuznetsk"
    ASIA_NOVOSIBIRSK = "Asia/Novosibirsk"
    ASIA_OMSK = "Asia/Omsk"
    ASIA_ORAL = "Asia/Oral"
    ASIA_PHNOM_PENH = "Asia/Phnom_Penh"
    ASIA_PONTIANAK = "Asia/Pontianak"
    ASIA_PYONGYANG = "Asia/Pyongyang"
    ASIA_QATAR = "Asia/Qatar"
    ASIA_QOSTANAY = "Asia/Qostanay"
    ASIA_QYZYLORDA = "Asia/Qyzylorda"
    ASIA_RANGOON = "Asia/Rangoon"
    ASIA_RIYADH = "Asia/Riyadh"
    ASIA_SAIGON = "Asia/Saigon"
    ASIA_SAKHALIN = "Asia/Sakhalin"
    ASIA_SAMARKAND = "Asia/Samarkand"
    ASIA_SEOUL = "Asia/Seoul"
    ASIA_SHANGHAI = "Asia/Shanghai"
    ASIA_SINGAPORE = "Asia/Singapore"
    ASIA_SREDNEKOLYMSK = "Asia/Srednekolymsk"
    ASIA_TAIPEI = "Asia/Taipei"
    ASIA_TASHKENT = "Asia/Tashkent"
    ASIA_TBILISI = "Asia/Tbilisi"
    ASIA_TEHRAN = "Asia/Tehran"
    ASIA_TEL_AVIV = "Asia/Tel_Aviv"
    ASIA_THIMBU = "Asia/Thimbu"
    ASIA_THIMPHU = "Asia/Thimphu"
    ASIA_TOKYO = "Asia/Tokyo"
    ASIA_TOMSK = "Asia/Tomsk"
    ASIA_UJUNG_PANDANG = "Asia/Ujung_Pandang"
    ASIA_ULAANBAATAR = "Asia/Ulaanbaatar"
    ASIA_ULAN_BATOR = "Asia/Ulan_Bator"
    ASIA_URUMQI = "Asia/Urumqi"
    ASIA_UST_NERA = "Asia/Ust-Nera"
    ASIA_VIENTIANE = "Asia/Vientiane"
    ASIA_VLADIVOSTOK = "Asia/Vladivostok"
    ASIA_YAKUTSK = "Asia/Yakutsk"
    ASIA_YANGON = "Asia/Yangon"
    ASIA_YEKATERINBURG = "Asia/Yekaterinburg"
    ASIA_YEREVAN = "Asia/Yerevan"
    ATLANTIC_AZORES = "Atlantic/Azores"
    ATLANTIC_BERMUDA = "Atlantic/Bermuda"
    ATLANTIC_CANARY = "Atlantic/Canary"
    ATLANTIC_CAPE_VERDE = "Atlantic/Cape_Verde"
    ATLANTIC_FAEROE = "Atlantic/Faeroe"
    ATLANTIC_FAROE = "Atlantic/Faroe"
    ATLANTIC_JAN_MAYEN = "Atlantic/Jan_Mayen"
    ATLANTIC_MADEIRA = "Atlantic/Madeira"
    ATLANTIC_REYKJAVIK = "Atlantic/Reykjavik"
    ATLANTIC_SOUTH_GEORGIA = "Atlantic/South_Georgia"
    ATLANTIC_ST_HELENA = "Atlantic/St_Helena"
    ATLANTIC_STANLEY = "Atlantic/Stanley"
    AUSTRALIA_ACT = "Australia/ACT"
    AUSTRALIA_ADELAIDE = "Australia/Adelaide"
    AUSTRALIA_BRISBANE = "Australia/Brisbane"
    AUSTRALIA_BROKEN_HILL = "Australia/Broken_Hill"
    AUSTRALIA_CANBERRA = "Australia/Canberra"
    AUSTRALIA_CURRIE = "Australia/Currie"
    AUSTRALIA_DARWIN = "Australia/Darwin"
    AUSTRALIA_EUCLA = "Australia/Eucla"
    AUSTRALIA_HOBART = "Australia/Hobart"
    AUSTRALIA_LHI = "Australia/LHI"
    AUSTRALIA_LINDEMAN = "Australia/Lindeman"
    AUSTRALIA_LORD_HOWE = "Australia/Lord_Howe"
    AUSTRALIA_MELBOURNE = "Australia/Melbourne"
    AUSTRALIA_NSW = "Australia/NSW"
    AUSTRALIA_NORTH = "Australia/North"
    AUSTRALIA_PERTH = "Australia/Perth"
    AUSTRALIA_QUEENSLAND = "Australia/Queensland"
    AUSTRALIA_SOUTH = "Australia/South"
    AUSTRALIA_SYDNEY = "Australia/Sydney"
    AUSTRALIA_TASMANIA = "Australia/Tasmania"
    AUSTRALIA_VICTORIA = "Australia/Victoria"
    AUSTRALIA_WEST = "Australia/West"
    AUSTRALIA_YANCOWINNA = "Australia/Yancowinna"
    BRAZIL_ACRE = "Brazil/Acre"
    BRAZIL_DE_NORONHA = "Brazil/DeNoronha"
    BRAZIL_EAST = "Brazil/East"
    BRAZIL_WEST = "Brazil/West"
    CET = "CET"
    CST6CDT = "CST6CDT"
    CANADA_ATLANTIC = "Canada/Atlantic"
    CANADA_CENTRAL = "Canada/Central"
    CANADA_EASTERN = "Canada/Eastern"
    CANADA_MOUNTAIN = "Canada/Mountain"
    CANADA_NEWFOUNDLAND = "Canada/Newfoundland"
    CANADA_PACIFIC = "Canada/Pacific"
    CANADA_SASKATCHEWAN = "Canada/Saskatchewan"
    CANADA_YUKON = "Canada/Yukon"
    CHILE_CONTINENTAL = "Chile/Continental"
    CHILE_EASTER_ISLAND = "Chile/EasterIsland"
    CUBA = "Cuba"
    EET = "EET"
    EST = "EST"
    EST5EDT = "EST5EDT"
    EGYPT = "Egypt"
    EIRE = "Eire"
    ETC_GMT = "Etc/GMT"
    ETC_GMT_PLUS_0 = "Etc/GMT+0"
    ETC_GMT_PLUS_1 = "Etc/GMT+1"
    ETC_GMT_PLUS_10 = "Etc/GMT+10"
    ETC_GMT_PLUS_11 = "Etc/GMT+11"
    ETC_GMT_PLUS_12 = "Etc/GMT+12"
    ETC_GMT_PLUS_2 = "Etc/GMT+2"
    ETC_GMT_PLUS_3 = "Etc/GMT+3"
    ETC_GMT_PLUS_4 = "Etc/GMT+4"
    ETC_GMT_PLUS_5 = "Etc/GMT+5"
    ETC_GMT_PLUS_6 = "Etc/GMT+6"
    ETC_GMT_PLUS_7 = "Etc/GMT+7"
    ETC_GMT_PLUS_8 = "Etc/GMT+8"
    ETC_GMT_PLUS_9 = "Etc/GMT+9"
    ETC_GMT_MINUS_0 = "Etc/GMT-0"
    ETC_GMT_MINUS_1 = "Etc/GMT-1"
    ETC_GMT_MINUS_10 = "Etc/GMT-10"
    ETC_GMT_MINUS_11 = "Etc/GMT-11"
    ETC_GMT_MINUS_12 = "Etc/GMT-12"
    ETC_GMT_MINUS_13 = "Etc/GMT-13"
    ETC_GMT_MINUS_14 = "Etc/GMT-14"
    ETC_GMT_MINUS_2 = "Etc/GMT-2"
    ETC_GMT_MINUS_3 = "Etc/GMT-3"
    ETC_GMT_MINUS_4 = "Etc/GMT-4"
    ETC_GMT_MINUS_5 = "Etc/GMT-5"
    ETC_GMT_MINUS_6 = "Etc/GMT-6"
    ETC_GMT_MINUS_7 = "Etc/GMT-7"
    ETC_GMT_MINUS_8 = "Etc/GMT-8"
    ETC_GMT_MINUS_9 = "Etc/GMT-9"
    ETC_GMT0 = "Etc/GMT0"
    ETC_GREENWICH = "Etc/Greenwich"
    ETC_UCT = "Etc/UCT"
    ETC_UTC = "Etc/UTC"
    ETC_UNIVERSAL = "Etc/Universal"
    ETC_ZULU = "Etc/Zulu"
    EUROPE_AMSTERDAM = "Europe/Amsterdam"
    EUROPE_ANDORRA = "Europe/Andorra"
    EUROPE_ASTRAKHAN = "Europe/Astrakhan"
    EUROPE_ATHENS = "Europe/Athens"
    EUROPE_BELFAST = "Europe/Belfast"
    EUROPE_BELGRADE = "Europe/Belgrade"
    EUROPE_BERLIN = "Europe/Berlin"
    EUROPE_BRATISLAVA = "Europe/Bratislava"
    EUROPE_BRUSSELS = "Europe/Brussels"
    EUROPE_BUCHAREST = "Europe/Bucharest"
    EUROPE_BUDAPEST = "Europe/Budapest"
    EUROPE_BUSINGEN = "Europe/Busingen"
    EUROPE_CHISINAU = "Europe/Chisinau"
    EUROPE_COPENHAGEN = "Europe/Copenhagen"
    EUROPE_DUBLIN = "Europe/Dublin"
    EUROPE_GIBRALTAR = "Europe/Gibraltar"
    EUROPE_GUERNSEY = "Europe/Guernsey"
    EUROPE_HELSINKI = "Europe/Helsinki"
    EUROPE_ISLE_OF_MAN = "Europe/Isle_of_Man"
    EUROPE_ISTANBUL = "Europe/Istanbul"
    EUROPE_JERSEY = "Europe/Jersey"
    EUROPE_KALININGRAD = "Europe/Kaliningrad"
    EUROPE_KIEV = "Europe/Kiev"
    EUROPE_KIROV = "Europe/Kirov"
    EUROPE_KYIV = "Europe/Kyiv"
    EUROPE_LISBON = "Europe/Lisbon"
    EUROPE_LJUBLJANA = "Europe/Ljubljana"
    EUROPE_LONDON = "Europe/London"
    EUROPE_LUXEMBOURG = "Europe/Luxembourg"
    EUROPE_MADRID = "Europe/Madrid"
    EUROPE_MALTA = "Europe/Malta"
    EUROPE_MARIEHAMN = "Europe/Mariehamn"
    EUROPE_MINSK = "Europe/Minsk"
    EUROPE_MONACO = "Europe/Monaco"
    EUROPE_MOSCOW = "Europe/Moscow"
    EUROPE_NICOSIA = "Europe/Nicosia"
    EUROPE_OSLO = "Europe/Oslo"
    EUROPE_PARIS = "Europe/Paris"
    EUROPE_PODGORICA = "Europe/Podgorica"
    EUROPE_PRAGUE = "Europe/Prague"
    EUROPE_RIGA = "Europe/Riga"
    EUROPE_ROME = "Europe/Rome"
    EUROPE_SAMARA = "Europe/Samara"
    EUROPE_SAN_MARINO = "Europe/San_Marino"
    EUROPE_SARAJEVO = "Europe/Sarajevo"
    EUROPE_SARATOV = "Europe/Saratov"
    EUROPE_SIMFEROPOL = "Europe/Simferopol"
    EUROPE_SKOPJE = "Europe/Skopje"
    EUROPE_SOFIA = "Europe/Sofia"
    EUROPE_STOCKHOLM = "Europe/Stockholm"
    EUROPE_TALLINN = "Europe/Tallinn"
    EUROPE_TIRANE = "Europe/Tirane"
    EUROPE_TIRASPOL = "Europe/Tiraspol"
    EUROPE_ULYANOVSK = "Europe/Ulyanovsk"
    EUROPE_UZHGOROD = "Europe/Uzhgorod"
    EUROPE_VADUZ = "Europe/Vaduz"
    EUROPE_VATICAN = "Europe/Vatican"
    EUROPE_VIENNA = "Europe/Vienna"
    EUROPE_VILNIUS = "Europe/Vilnius"
    EUROPE_VOLGOGRAD = "Europe/Volgograd"
    EUROPE_WARSAW = "Europe/Warsaw"
    EUROPE_ZAGREB = "Europe/Zagreb"
    EUROPE_ZAPOROZHYE = "Europe/Zaporozhye"
    EUROPE_ZURICH = "Europe/Zurich"
    GB = "GB"
    GB_EIRE = "GB-Eire"
    GMT = "GMT"
    GMT_PLUS_0 = "GMT+0"
    GMT_MINUS_0 = "GMT-0"
    GMT0 = "GMT0"
    GREENWICH = "Greenwich"
    HST = "HST"
    HONGKONG = "Hongkong"
    ICELAND = "Iceland"
    INDIAN_ANTANANARIVO = "Indian/Antananarivo"
    INDIAN_CHAGOS = "Indian/Chagos"
    INDIAN_CHRISTMAS = "Indian/Christmas"
    INDIAN_COCOS = "Indian/Cocos"
    INDIAN_COMORO = "Indian/Comoro"
    INDIAN_KERGUELEN = "Indian/Kerguelen"
    INDIAN_MAHE = "Indian/Mahe"
    INDIAN_MALDIVES = "Indian/Maldives"
    INDIAN_MAURITIUS = "Indian/Mauritius"
    INDIAN_MAYOTTE = "Indian/Mayotte"
    INDIAN_REUNION = "Indian/Reunion"
    IRAN = "Iran"
    ISRAEL = "Israel"
    JAMAICA = "Jamaica"
    JAPAN = "Japan"
    KWAJALEIN = "Kwajalein"
    LIBYA = "Libya"
    MET = "MET"
    MST = "MST"
    MST7MDT = "MST7MDT"
    MEXICO_BAJA_NORTE = "Mexico/BajaNorte"
    MEXICO_BAJA_SUR = "Mexico/BajaSur"
    MEXICO_GENERAL = "Mexico/General"
    NZ = "NZ"
    NZ_CHAT = "NZ-CHAT"
    NAVAJO = "Navajo"
    PRC = "PRC"
    PST8PDT = "PST8PDT"
    PACIFIC_APIA = "Pacific/Apia"
    PACIFIC_AUCKLAND = "Pacific/Auckland"
    PACIFIC_BOUGAINVILLE = "Pacific/Bougainville"
    PACIFIC_CHATHAM = "Pacific/Chatham"
    PACIFIC_CHUUK = "Pacific/Chuuk"
    PACIFIC_EASTER = "Pacific/Easter"
    PACIFIC_EFATE = "Pacific/Efate"
    PACIFIC_ENDERBURY = "Pacific/Enderbury"
    PACIFIC_FAKAOFO = "Pacific/Fakaofo"
    PACIFIC_FIJI = "Pacific/Fiji"
    PACIFIC_FUNAFUTI = "Pacific/Funafuti"
    PACIFIC_GALAPAGOS = "Pacific/Galapagos"
    PACIFIC_GAMBIER = "Pacific/Gambier"
    PACIFIC_GUADALCANAL = "Pacific/Guadalcanal"
    PACIFIC_GUAM = "Pacific/Guam"
    PACIFIC_HONOLULU = "Pacific/Honolulu"
    PACIFIC_JOHNSTON = "Pacific/Johnston"
    PACIFIC_KANTON = "Pacific/Kanton"
    PACIFIC_KIRITIMATI = "Pacific/Kiritimati"
    PACIFIC_KOSRAE = "Pacific/Kosrae"
    PACIFIC_KWAJALEIN = "Pacific/Kwajalein"
    PACIFIC_MAJURO = "Pacific/Majuro"
    PACIFIC_MARQUESAS = "Pacific/Marquesas"
    PACIFIC_MIDWAY = "Pacific/Midway"
    PACIFIC_NAURU = "Pacific/Nauru"
    PACIFIC_NIUE = "Pacific/Niue"
    PACIFIC_NORFOLK = "Pacific/Norfolk"
    PACIFIC_NOUMEA = "Pacific/Noumea"
    PACIFIC_PAGO_PAGO = "Pacific/Pago_Pago"
    PACIFIC_PALAU = "Pacific/Palau"
    PACIFIC_PITCAIRN = "Pacific/Pitcairn"
    PACIFIC_POHNPEI = "Pacific/Pohnpei"
    PACIFIC_PONAPE = "Pacific/Ponape"
    PACIFIC_PORT_MORESBY = "Pacific/Port_Moresby"
    PACIFIC_RAROTONGA = "Pacific/Rarotonga"
    PACIFIC_SAIPAN = "Pacific/Saipan"
    PACIFIC_SAMOA = "Pacific/Samoa"
    PACIFIC_TAHITI = "Pacific/Tahiti"
    PACIFIC_TARAWA = "Pacific/Tarawa"
    PACIFIC_TONGATAPU = "Pacific/Tongatapu"
    PACIFIC_TRUK = "Pacific/Truk"
    PACIFIC_WAKE = "Pacific/Wake"
    PACIFIC_WALLIS = "Pacific/Wallis"
    PACIFIC_YAP = "Pacific/Yap"
    POLAND = "Poland"
    PORTUGAL = "Portugal"
    ROC = "ROC"
    ROK = "ROK"
    SINGAPORE = "Singapore"
    TURKEY = "Turkey"
    UCT = "UCT"
    US_ALASKA = "US/Alaska"
    US_ALEUTIAN = "US/Aleutian"
    US_ARIZONA = "US/Arizona"
    US_CENTRAL = "US/Central"
    US_EAST_INDIANA = "US/East-Indiana"
    US_EASTERN = "US/Eastern"
    US_HAWAII = "US/Hawaii"
    US_INDIANA_STARKE = "US/Indiana-Starke"
    US_MICHIGAN = "US/Michigan"
    US_MOUNTAIN = "US/Mountain"
    US_PACIFIC = "US/Pacific"
    US_SAMOA = "US/Samoa"
    UTC = "UTC"
    UNIVERSAL = "Universal"
    W_SU = "W-SU"
    WET = "WET"
    ZULU = "Zulu"


class UnderlyingTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of UnderlyingTypeEnum."""

    FX = "Fx"
    BOND = "Bond"
    IRS = "Irs"
    COMMODITY = "Commodity"
    EQUITY = "Equity"
    BOND_FUTURE = "BondFuture"


class UnitEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The unit that describes the value."""

    ABSOLUTE = "Absolute"
    """The value is expressed in absolute units."""
    BASIS_POINT = "BasisPoint"
    """The value is expressed in basis points (scaled by 10,000)."""
    PERCENTAGE = "Percentage"
    """The value is expressed in percentages (scaled by 100)."""


class Visible(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of Visible."""

    Y = "Y"
    U = "U"
    N = "N"


class VolModelTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """An object defining the different type of model used to represent the volatilities."""

    NORMAL = "Normal"
    LOG_NORMAL = "LogNormal"


class WeekDay(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The day of the week. Day names written in full."""

    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


class YbRestCurveType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Type of YbRestCurveType."""

    GVT = "GVT"
    GVT_TSYM = "GVT_TSYM"
    GVT_TSYM_MUNI = "GVT_TSYM_MUNI"
    GVT_AGN = "GVT_AGN"
    GVT_MUNI = "GVT_MUNI"
    GVT_BUND = "GVT_BUND"
    SWAP = "SWAP"
    SWAP_RFR = "SWAP_RFR"
    SWAP_MUNI = "SWAP_MUNI"
    SWAP_LIB6M = "SWAP_LIB6M"


class YearBasisEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The number of days used to represent a year."""

    YB_252 = "YB_252"
    """252 days in a year, the conventional number of days in a year when taking only working days
    into account.
    """
    YB_360 = "YB_360"
    """360 days in a year."""
    YB_364 = "YB_364"
    """364 days in a year."""
    YB_365 = "YB_365"
    """365 days in a year."""
    YB_36525 = "YB_36525"
    """365.25 days in a year."""
    YB_366 = "YB_366"
    """366 days in a year."""
    YB_ACTUAL = "YB_Actual"
    """365 days or 366 days in a year, taking leap years into account."""


class ZcTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """An enum that describes the type of the value provided in the zero coupon curve."""

    RATE = "Rate"
    """The zero coupon curve values are provided as rates."""
    DISCOUNT_FACTOR = "DiscountFactor"
    """The zero coupon curve values are provided as discount factor."""
