from lseg_analytics.yield_book_rest import (
    request_bond_indic_sync,
    IdentifierInfo
)
import json as js

# List of instruments defined by either CUSIP or ISIN identifiers 
instrument_input=[IdentifierInfo(identifier="91282CLF6"),
                    IdentifierInfo(identifier="US1352752"),
                    IdentifierInfo(identifier="999818YT")]

# Request single/multiple bond indices with sync post
response = request_bond_indic_sync(input=instrument_input)

# Print results in json format
print(js.dumps(obj=response.as_dict(), indent=4))