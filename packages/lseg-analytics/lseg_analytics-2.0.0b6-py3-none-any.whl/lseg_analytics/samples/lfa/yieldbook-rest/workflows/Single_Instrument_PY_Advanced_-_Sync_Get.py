import json as js

from lseg_analytics.yield_book_rest import (
    request_py_calculation_sync_by_id,
    OptionModel
)

# Request single instrument PY Calculation
py_sync_get_response = request_py_calculation_sync_by_id(
            id="01F002628", 
            level="100",
            curve_type="GVT",
            pricing_date="2025-01-17",
            currency="USD",
            prepay_type="CPR",
            prepay_rate=1.1,
            option_model=OptionModel.OAS,
        )

# Print results in json format
print(js.dumps(obj=py_sync_get_response, indent=4))