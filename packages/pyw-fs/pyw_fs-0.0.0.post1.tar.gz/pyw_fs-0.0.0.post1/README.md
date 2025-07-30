# pyw-fs 📁
[![PyPI](https://img.shields.io/pypi/v/pyw-fs.svg)](https://pypi.org/project/pyw-fs/)
[![CI](https://github.com/pythonWoods/pyw-fs/actions/workflows/ci.yml/badge.svg)](https://github.com/pythonWoods/pyw-fs/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
Unified filesystem API basata su **fsspec**  
`open("s3://bucket/file.txt")` funziona come un semplice `open("file.txt")`.

```bash
pip install pyw-fs          # locale + S3
pip install pyw-fs[gcs]     # + Google Cloud
```

```python
from pyw.fs import open
with open("s3://my-bucket/data.csv") as f:
    print(f.read())
```

* Plugin S3 (`s3fs`) e GCS (`gcsfs`) caricati via extras.


## Links utili
Documentazione dev (work-in-progress) → https://pythonwoods.dev/docs/pyw-fs/latest/

Issue tracker → https://github.com/pythonWoods/pyw-fs/issues

Changelog → https://github.com/pythonWoods/pyw-fs/releases

© pythonWoods — MIT License