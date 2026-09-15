# python -m ruff format --check src tests
unformatted: File would be reformatted
 --> src/easop/__init__.py:1:29
  |
  - """EASOP backend package."""
1 + """EASOP backend package."""
  |

unformatted: File would be reformatted
for below code:
"""EASOP backend package."""

# Try below command:
# Run Ruff without --check
Let Ruff automatically reformat:
python -m ruff format src tests
