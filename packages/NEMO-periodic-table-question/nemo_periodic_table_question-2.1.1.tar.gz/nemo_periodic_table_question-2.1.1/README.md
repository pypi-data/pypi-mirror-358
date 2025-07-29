# NEMO Periodic Table Question

This plugin for NEMO allows to use a `periodic_table` type of question in post usage questions or reservation questions.

# Compatibility:

NEMO/NEMO-CE >= 7.0.0 ----> NEMO-Reports >= 2.0.0

# Installation

`pip install NEMO-periodic-table-question`

# Add NEMO Periodic Table Question

in `settings.py` add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    '...',
    'NEMO_periodic_table_question',
    '...'
]
```

# Usage
Use `type: "periodic-table"` in Tool post usage questions or Reservation questions.

Options:
 - required: true or false (default: false)
 - collapsible: true or false (default: false)
 - collapsed: true or false (default: false)
 - help: "Some help text to display under the periodic table"

**Important note**:<br>
The `collapsible`/`collapsed` options aren't supported in the admin preview but should work in the calendar.