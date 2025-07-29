from lseg_analytics.yield_book_rest import (
        post_cash_flow_sync,
        CashFlowGlobalSettings, 
        CashFlowInput,
        Volatility,
        CurveTypeAndCurrency,
        LossSettings,
        RestPrepaySettings,
        CashflowFloaterSettings,
        CashflowMbsSettings,
        MuniSettings
)
import json as js

# Formulate Request body parameters - Global Settings
global_settings = CashFlowGlobalSettings(
            pricing_date="2025-01-13",
            use_previous_close=True,
            use_live_data=False,
            volatility=Volatility(
                type="Market",
                rate=1.11,
            ),
            retrieve_ppm_projection=True,
            core_logic_collateral="DEFAULT",
        )

# Formulate Request body parameters - Input 
input = CashFlowInput(
            identifier="01F002628",
            id_type="CUSIP",
            curve=CurveTypeAndCurrency(
                curve_type="GVT",
                currency="USD",
                retrieve_curve=True,
                snapshot="EOD",
            ),
            settlement_type="MARKET",
            settlement_date="2025-01-15",
            custom_settlement="custom_settlement",
            par_amount="10000",
            loss_settings=LossSettings(
                default_type="SDA",
                default_rate=0.01,
                severity_type="MODEL",
                severity_rate=0.01,
                recovery_lag=1,
                delinquency_type="PASS",
                delinquency_rate=0.01,
                use_model_loan_modifications=True,
                ignore_insurance=True,
            ),
            prepay=RestPrepaySettings(
                type="Model",
                rate=0.01,
            ),
            floater_settings=CashflowFloaterSettings(
                use_forward_index=True,
                forward_index_rate=0.01,
                calculate_to_maturity=True,
            ),
            muni_settings=MuniSettings(paydown_optional=True, ignore_call_info=True, use_stub_rate=True),
            mbs_settings=CashflowMbsSettings(
                use_roll_info=True, assume_call=True, step_down_fail=True, show_collateral_cash_flow=True
            )
)

# Execute Post sync request with prepared inputs
cf_async_get_response = post_cash_flow_sync(
                            global_settings=global_settings,
                            input=[input]
                        )

# Print output to a file, as CF output is too long for terminal printout
print(js.dumps(cf_async_get_response, indent=4), file=open('CF_output.json', 'w+'))