# PyLogical

PyLogical é um pacote Python com 18 atributos lógicos avançados para facilitar verificações complexas em código.

## Instalação
```bash
pip install pylogical
```

## Uso
```python
from pylogical import IsEven, IsEmpty
print(IsEven(10).result())  # True
print(IsEmpty([]).result())  # True
```

## Testes
```bash
pytest tests/
```
