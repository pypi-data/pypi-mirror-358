# jing
This is a python libary, used for download stock data and perform data analisys.

## Installation
```bash
pip install jing

## Only 2 class exported

### downloader `D`
- **Function**: download the data from internet to local file system
- **Parameter**:
  - `_market` (str): us, cn, hk, default is us
- **Return Value**: No return value

### sample code

```python
import jing

d = jing.D(_market='hk')
d.download('00005')

