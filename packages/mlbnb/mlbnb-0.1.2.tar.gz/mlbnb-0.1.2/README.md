# mlbnb

Machine learning bread and butter - tools used in machine learning experiments

## Fix fdm library:

```
sed -i 's/np\.math/np/g' .venv/lib/python3.12/site-packages/fdm/fdm.py
sed -i 's/np\.factorial/math.factorial/g' .venv/lib/python3.12/site-packages/fdm/fdm.py
sed -i '1s/^/import math\n/' .venv/lib/python3.12/site-packages/fdm/fdm.py
```
