from lseg_analytics.yield_book_rest import (
    request_bond_indic_sync,
    request_bond_indic_async,
    IdentifierInfo,
    get_result
)
import json as js

# List of instruments defined by either CUSIP or ISIN identifiers 
instrument_input=[IdentifierInfo(identifier="91282CLF6"),
                    IdentifierInfo(identifier="US1352752"),
                    IdentifierInfo(identifier="999818YT")]

# Request single/multiple bond indices with sync post
sync_response = request_bond_indic_sync(input=instrument_input)

# Request multiple bond indices with async post
async_response = request_bond_indic_async(input=instrument_input)

# Get results by request_id
results_response = get_result(request_id_parameter=async_response.request_id)

# Print results in json format
print(js.dumps(obj=sync_response.as_dict(), indent=4))

# Print results in json format
print(js.dumps(results_response, indent=4))