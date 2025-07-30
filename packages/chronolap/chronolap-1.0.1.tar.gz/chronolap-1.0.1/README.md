# Chronolap

Advanced stopwatch with lap tracking for Python developers.

## Installation

```bash
pip install chronolap
```


```python

from chronolap import ChronolapTimer

timer = ChronolapTimer()
timer.start()
# your code
timer.lap("First section")
timer.stop()

for lap in timer.laps:
    print(lap)

```


## Support

If you find this project useful, consider supporting me:

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-%23FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/ertugrulkara)

## License

MIT © Ertugrul Kara