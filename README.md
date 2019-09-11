# GreenLight

## .config.json

```json
{
  "user": "registered_email@whatever",
  "password": "your_iso_ne_password",
}
```

## Python Setup

I'm using Python 3.7 on my Mac in a virtualenv "virtual environment". It will be fine in an earlier version of Python, but I've been using the type annotations so it'll probably be stuck earlier than Python 3.5

```bash
pip install -r requirements.txt
```

## Current behavior:

Executing ``python ise_ne_api.py`` will give you:

```
Current Fuel Mix
Timestamp:  a minute ago
Mw Distribution {'Coal': 51, 'Hydro': 439, 'Natural Gas': 8493, 'Nuclear': 3297, 'Other': 12, 'Renewables': 1222}
Renewables: 0.09%
```

