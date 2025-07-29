from lseg_analytics.yield_book_rest import (
        request_scenario_calculation_sync,
        Volatility,
        StructureNote,
        CurveTypeAndCurrency,
        LossSettings,
        Vector,
        MonthRatePair,
        RestPrepaySettings,
        ScenarioCalcGlobalSettings,
        Scenario,
        ScenarioDefinition,
        SystemScenario,
        UserScenario,
        ApimCurveShift,
        CurveMultiShift,
        ScenAbsoluteCurvePoint,
        ScenarioVolatility,
        SwaptionVolatility,
        SwaptionVolItem,
        CapVolatility,
        CapVolItem,
        ScenarioCalcInput,
        SettlementInfo,
        PricingScenario,
        CustomScenario,
        CmbsPrepayment,
        Balloon,
        HorizonInfo,
        ScenarioCalcFloaterSettings,
        HecmSettings,
        ScenCalcExtraSettings,
        Partials,
)
import json as js

# request_scenario_calculation_async
global_settings = ScenarioCalcGlobalSettings(
            pricing_date="2025-01-01",
            use_previous_close=False,
            use_live_data=False,
            calc_horizon_effective_measures=False,
            calc_horizon_option_measures=True,
            calc_scenario_cash_flow=True,
            calc_prepay_sensitivity=True,
            current_coupon_rates="MOATS",
            horizon_months=1,
            horizon_days=5,
            use_stochastic_hpa=True,
            use_five_point_convexity=True,
            use_core_logic_group_model=True,
            use_muni_non_call_curve=True,
            use_muni_tax_settings=True,
            use_ois=False,
            core_logic_collateral="DEFAULT",
        )
scenario = Scenario(
            scenario_id="ScenID1",
            scenario_title="ScenTest1",
            timing="AtHorizon",
            reinvestment_rate="1.3",
            definition=ScenarioDefinition(
                system_scenario=SystemScenario(name="BEARFLAT100"),
                user_scenario=UserScenario(
                    shift_type="Forward",
                    interpolation_type="PrincipalComponents",
                    swap_spread_const=True,
                    curve_shifts=[ApimCurveShift(year=1, value=1.1)],
                    curve_multi_shifts=[CurveMultiShift(curve_shifts=[ApimCurveShift(year=1, value=1.1)])],
                    curve_points=[
                        ScenAbsoluteCurvePoint(
                            term=1, rate=1.1, spot_rate=1.231, forward_rate=1.105, discount_factor=0.8
                        )
                    ],
                ),
            ),
            volatility=ScenarioVolatility(
                term_unit="MONTH",
                value_type="ABS",
                parallel_shift=1.1,
                swaption_volatility=SwaptionVolatility(
                    value_type="ABS", values_property=[SwaptionVolItem(expiration=1.121, value=1.011, term=3.3)]
                ),
                cap_volatility=CapVolatility(
                    value_type="ABS", values_property=[CapVolItem(expiration=1.121, value=1.011)]
                ),
            ),
            current_coupon_spread_change=1.1,
        )
input = ScenarioCalcInput(
            identifier="US742718AV11",
            id_type="ISIN",
            curve=CurveTypeAndCurrency(
                curve_type="GVT",
                currency="USD",
                retrieve_curve=True,
                snapshot="4PM",
            ),
            volatility=Volatility(
                type="Single",
                rate="1.1",
                structure_note=StructureNote(pricing="ASSETSWAP", callable_zero_pricing="NETPROCEED"),
            ),
            settlement_info=SettlementInfo(
                level="100",
                settlement_type="CUSTOM",
                settlement_date="2025-01-01",
                prepay=RestPrepaySettings(
                    type="ABS",
                    rate=1.1,
                    vector=Vector(
                        interpolation_type="INTERPOLATED",
                        index="PRIM",
                        values_property=[MonthRatePair(month=1, rate=1.1)],
                    ),
                    model_to_balloon=True,
                ),
                loss_settings=LossSettings(
                    default_type="CDR",
                    default_rate=1.1,
                    default_vector=Vector(
                        interpolation_type="INTERPOLATED",
                        index="PRIM",
                        values_property=[MonthRatePair(month=1, rate=1.1)],
                    ),
                    severity_type="MODEL",
                    severity_rate=1.1,
                    severity_vector=Vector(
                        interpolation_type="INTERPOLATED",
                        index="PRIM",
                        values_property=[MonthRatePair(month=1, rate=1.1)],
                    ),
                    recovery_lag=1,
                    delinquency_type="MODEL",
                    delinquency_rate=1.1,
                    delinquency_vector=Vector(
                        interpolation_type="INTERPOLATED",
                        index="PRIM",
                        values_property=[MonthRatePair(month=1, rate=1.1)],
                    ),
                    use_model_loan_modifications=True,
                    ignore_insurance=True,
                ),
                cmbs_scenario=PricingScenario(
                    primary=True,
                    type="CPJ",
                    rate=1.1,
                    system_scenario_name="name",
                    custom_scenario=CustomScenario(
                        assume_call=True,
                        delay=True,
                        delay_balloon_maturity=True,
                        defeasance="AUTO",
                        prepayment=CmbsPrepayment(
                            rate_during_yield_to_maturity=1.017,
                            rate_after_yield_to_maturity=0.987,
                            rate_during_premium=2.331,
                        ),
                        defaults=Balloon(
                            percent=0.8,
                            loss_severity=0.8,
                            recovery_period=1,
                            loss_type="CDR",
                            loss_rate=0.8,
                            month_to_extend=2,
                            loss_vector=Vector(
                                interpolation_type="INTERPOLATED",
                                index="PRIM",
                                values_property=[MonthRatePair(month=1, rate=1.1)],
                            ),
                        ),
                        balloon_extend=Balloon(
                            percent=0.8,
                            loss_severity=0.8,
                            recovery_period=1,
                            loss_type="CDR",
                            loss_rate=0.8,
                            month_to_extend=2,
                            loss_vector=Vector(
                                interpolation_type="INTERPOLATED",
                                index="PRIM",
                                values_property=[MonthRatePair(month=1, rate=1.1)],
                            ),
                        ),
                        balloon_default=Balloon(
                            percent=0.8,
                            loss_severity=0.8,
                            recovery_period=1,
                            loss_type="CDR",
                            loss_rate=0.8,
                            month_to_extend=2,
                            loss_vector=Vector(
                                interpolation_type="INTERPOLATED",
                                index="PRIM",
                                values_property=[MonthRatePair(month=1, rate=1.1)],
                            ),
                        ),
                    ),
                ),
            ),
            horizon_info=[
                HorizonInfo(
                    scenario_id="ScenID1",
                    level="100",
                    prepay=RestPrepaySettings(
                        type="ABS",
                        rate=1.1,
                        vector=Vector(
                            interpolation_type="INTERPOLATED",
                            index="PRIM",
                            values_property=[MonthRatePair(month=1, rate=1.1)],
                        ),
                        model_to_balloon=True,
                    ),
                    loss_settings=LossSettings(
                        default_type="CDR",
                        default_rate=1.1,
                        default_vector=Vector(
                            interpolation_type="INTERPOLATED",
                            index="PRIM",
                            values_property=[MonthRatePair(month=1, rate=1.1)],
                        ),
                        severity_type="MODEL",
                        severity_rate=1.1,
                        severity_vector=Vector(
                            interpolation_type="INTERPOLATED",
                            index="PRIM",
                            values_property=[MonthRatePair(month=1, rate=1.1)],
                        ),
                        recovery_lag=1,
                        delinquency_type="MODEL",
                        delinquency_rate=1.1,
                        delinquency_vector=Vector(
                            interpolation_type="INTERPOLATED",
                            index="PRIM",
                            values_property=[MonthRatePair(month=1, rate=1.1)],
                        ),
                        use_model_loan_modifications=True,
                        ignore_insurance=True,
                    ),
                    cmbs_scenario=PricingScenario(
                        primary=True,
                        type="CPJ",
                        rate=1.1,
                        system_scenario_name="name",
                        custom_scenario=CustomScenario(
                            assume_call=True,
                            delay=True,
                            delay_balloon_maturity=True,
                            defeasance="AUTO",
                            prepayment=CmbsPrepayment(
                                rate_during_yield_to_maturity=1.017,
                                rate_after_yield_to_maturity=0.987,
                                rate_during_premium=2.331,
                            ),
                            defaults=Balloon(
                                percent=0.8,
                                loss_severity=0.8,
                                recovery_period=1,
                                loss_type="CDR",
                                loss_rate=0.8,
                                month_to_extend=2,
                                loss_vector=Vector(
                                    interpolation_type="INTERPOLATED",
                                    index="PRIM",
                                    values_property=[MonthRatePair(month=1, rate=1.1)],
                                ),
                            ),
                            balloon_extend=Balloon(
                                percent=0.8,
                                loss_severity=0.8,
                                recovery_period=1,
                                loss_type="CDR",
                                loss_rate=0.8,
                                month_to_extend=2,
                                loss_vector=Vector(
                                    interpolation_type="INTERPOLATED",
                                    index="PRIM",
                                    values_property=[MonthRatePair(month=1, rate=1.1)],
                                ),
                            ),
                            balloon_default=Balloon(
                                percent=0.8,
                                loss_severity=0.8,
                                recovery_period=1,
                                loss_type="CDR",
                                loss_rate=0.8,
                                month_to_extend=2,
                                loss_vector=Vector(
                                    interpolation_type="INTERPOLATED",
                                    index="PRIM",
                                    values_property=[MonthRatePair(month=1, rate=1.1)],
                                ),
                            ),
                        ),
                    ),
                )
            ],
            assume_call=True,
            horizon_py_method="Annualized ROR",
            floater_settings=ScenarioCalcFloaterSettings(use_forward_index=True, use_immediate_forward_shift=True),
            hecm_settings=HecmSettings(
                draw_type="CONSTANT",
                draw_rate=1.1,
                draw_vector=Vector(
                    interpolation_type="INTERPOLATED",
                    index="PRIM",
                    values_property=[MonthRatePair(month=1, rate=1.1)],
                ),
            ),
            extra_settings=ScenCalcExtraSettings(
                include_partials=True,
                partials=Partials(
                    curve_type="FORWARD",
                    curve_shift=1.1,
                    shock_type="SQUARE",
                    partial_duration_years=[1.1, 1.2],
                ),
            ),
        )

# Execute Post sync request with prepared inputs
response = request_scenario_calculation_sync(
            global_settings=global_settings,
            scenarios=[scenario],
            input=[input],
        )

# Print output in JSON format
print(js.dumps(obj=response, indent=4))