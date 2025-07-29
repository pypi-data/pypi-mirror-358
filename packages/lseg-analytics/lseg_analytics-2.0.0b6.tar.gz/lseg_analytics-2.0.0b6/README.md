# LSEG Analytics SDK for Python

The LSEG Analytics SDK for Python provides access to LSEG Financials Analytics Services.

## Getting Started

```shell
$ pip install lseg-analytics
```


## Usage Examples

An example to create a FX Forward Curve.

```python
from lseg_analytics.common import (
    CrossCurrencyInput,
    CurrencyInput,
    TenorType
)

from lseg_analytics.market_data.fx_forward_curves import (
    create_from_fx_forwards,
    IndirectSourcesSwaps
)

create_from_fx_forwards(
    cross_currency=CrossCurrencyInput(code="EURGBP"),
    reference_currency=CurrencyInput(code="USD"),
    sources=IndirectSourcesSwaps(
        base_fx_spot="ICAP",
        base_fx_forwards="ICAP",
        quoted_fx_spot="TTKL",
        quoted_fx_forwards="TTKL",
    ),
    additional_tenor_types=[TenorType.LONG, TenorType.END_OF_MONTH],
)
```

## Modules Structure

- `common` - contains models that can be used in different API modules
- `logging` - logging configuration
- `exceptions`
- API modules
  - `reference_data`
    - `calendars`
  - `market_data`
    - `fx_forward_curves`
  - `instruments`
    - `fx_spots`
    - `fx_forwards`

## API module structure

- Each API Module has a main object, which has the same name as a module, but in singular form
  - Examples
    - `reference_data.calendars`: `Calendar`
    - `market_data.fx_forward_curves`: `FxForwardCurve`
    - `instruments.fx_spots`: `FxSpot`
    - `instruments.fx_forwards`: `FxForward`
  - Instance of this object represents corresponding resource on the server
- Each API Module has functions `load`, `search`, `delete`
