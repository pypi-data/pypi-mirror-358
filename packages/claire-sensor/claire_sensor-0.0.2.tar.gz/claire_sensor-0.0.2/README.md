# claire-sensor

# User installation
```
pip install .
# or
pip install claire-sensor==0.0.1
```

Execute agent as
```
~/.local/bin/claire-sensor
```
# Help
Documentation of supported paths and attributes can be found on http://127.0.0.1:8123/help which is redirected to /docs

# Development
```commandline
source .venv/bin/activate
fastapi dev claire_sensor/main.py --port 8123
```

# Creating & publishing PiPY package

```commandline
pip install build twine
python -m build
twine upload dist/*
```