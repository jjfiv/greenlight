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

Executing ``python iso_ne_api.py`` will give you:

```
# Pricing Info
  Timestamp: 3 minutes ago
  Energy, Congestion, Loss: 22.29 0 0.09
  Total Price: 22.38

# Current Fuel Mix
  Timestamp: 4 minutes ago
  Mw Distribution {'Coal': 51, 'Hydro': 319, 'Natural Gas': 8404, 'Nuclear': 3297, 'Other': 12, 'Renewables': 1234}
  Renewables: 0.09%
```

