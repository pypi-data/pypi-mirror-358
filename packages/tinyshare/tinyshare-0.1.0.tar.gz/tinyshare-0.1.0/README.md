# TinyShare

A lightweight wrapper for tushare financial data API that provides the exact same interface as tushare but with additional features and optimizations.

## Installation

```bash
pip install tinyshare
```

## Usage

TinyShare provides the exact same API as tushare, so you can simply replace your import statement:

```python
# Instead of: import tushare as ts
import tinyshare as ts

# Set your token
ts.set_token('your_tushare_token_here')
pro = ts.pro_api()

# Get index daily data
df = pro.index_daily(
    ts_code='000001.SH',
    start_date='20250621',
    end_date='20250628'
)

print(df)
```

## Features

- **100% API Compatible**: Drop-in replacement for tushare
- **Enhanced Error Handling**: Better error messages and debugging
- **Performance Optimizations**: Caching and request optimization
- **Easy Migration**: Simply change your import statement

## Requirements

- Python 3.7+
- tushare>=1.2.0
- pandas>=1.0.0

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 