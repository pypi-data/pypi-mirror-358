# NEMO Stockroom

Stockroom plugin for NEMO.  This plugin expands upon NEMO's built-in Consumables feature.  It allows lab users to place orders (ConsumableRequests) for stockroom items, and staff can fulfill them.

# Installation

`pip install NEMO-stockroom`

# Add core stockroom plugin

in `settings.py` add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    '...',
    'NEMO_stockroom', # Add before NEMO to have new navbar menu items show up
    'NEMO',
    '...'
]
```

### NEMO Compatibility

NEMO >= 4.5.5 ----> NEMO-Stockroom >= 1.1.1

### Usage

This plugin adds additional features to NEMO's built-in Consumables feature.  Users can do the following:
1. Place requests for Consumables on their own (without staff).
2. View their order status history.  They can view pending requests (requests that haven't been fulfilled yet), fulfilled requets, and deleted requests.

Staff are able to do what users can, but with the following additional features:
1. Fulfill pending orders
2. Edit quantities of Consumables
3. View all fulfilled requests

The plugin will also send a confirmation e-mail when an order is fulfilled.


# (recommended) add Billing plugin

The NEMO billing plugin can be found here:  https://gitlab.com/nemo-community/atlantis-labs/nemo-billing
It is recommended to install the billing plugin, and also setup the rates plugin.


# Post Installation

run:

`python manage.py migrate`
