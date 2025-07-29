from lseg_analytics.yield_book_rest import (
    request_bond_indic_sync,
    request_bond_indic_sync_get,
    request_bond_indic_async,
    request_bond_indic_async_get,
    IdentifierInfo,
    get_result
)

import json as js

import time

# Select an ISIN or CUSIP ID of the instrument
identifier="NL0000102317"

# Prepare the input data container
instrument_input=[IdentifierInfo(identifier=identifier)]

# Request bond indic with sync post
sync_post_response = request_bond_indic_sync(input=instrument_input)

# Request bond indic with sync get
sync_get_response = request_bond_indic_sync_get(id=identifier)

# Request bond indic with async post
async_post_response = request_bond_indic_async(input=instrument_input)

# Get results by request_id
async_post_results_response = get_result(request_id_parameter=async_post_response.request_id)

# Request bond indic with async get
async_get_response = request_bond_indic_async_get(id=identifier)

# Get results by request_id
async_get_results_response = get_result(request_id_parameter=async_get_response.request_id)

# Due to async nature, code Will perform the fetch 10 times, as result is not always ready instantly, with 3 second lapse between attempts
attempt = 1

if not async_get_results_response:
    while attempt < 10:        
        print(f"Attempt " + str(attempt) + " resulted in error retrieving results from:" + async_get_results_response.request_id)
        
        time.sleep(3)
        
        async_get_results_response = get_result(request_id_parameter=async_get_results_response.request_id)
        
        if not async_get_results_response:
            attempt += 1
        else:
            break

# Print results in json format
print(js.dumps(sync_post_response.as_dict(), indent=4))

# Print results in json format
print(js.dumps(sync_get_response, indent=4))

# Print results in json format
print(js.dumps(async_post_results_response, indent=4))

# Print results in json format
print(js.dumps(async_get_results_response, indent=4))