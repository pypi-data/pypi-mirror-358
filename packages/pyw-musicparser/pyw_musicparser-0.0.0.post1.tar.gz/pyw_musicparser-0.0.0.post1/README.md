# pyw-musicparser 🎼
[![PyPI](https://img.shields.io/pypi/v/pyw-musicparser.svg)](https://pypi.org/project/pyw-musicparser/)
[![CI](https://github.com/pythonWoods/pyw-musicparser/actions/workflows/ci.yml/badge.svg)](https://github.com/pythonWoods/pyw-musicparser/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Converti **MIDI** o **Lilypond** in oggetti Music21 + estrazione feature.

```bash
pip install pyw-musicparser
```

```python
from pyw.musicparser import parse
score = parse("demo.mid")
print(score.keySignature, score.tempo)
```


## Links utili
Documentazione dev (work-in-progress) → https://pythonwoods.dev/docs/pyw-musicparser/latest/

Issue tracker → https://github.com/pythonWoods/pyw-musicparser/issues

Changelog → https://github.com/pythonWoods/pyw-musicparser/releases

© pythonWoods — MIT License