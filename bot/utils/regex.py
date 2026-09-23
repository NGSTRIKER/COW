import re

# Regular expression pattern matching "cow" or "moo+" variations in text (case-insensitive)
COW = re.compile(r"\bcow\b|\bmo+\b", re.IGNORECASE)

# Regular expression pattern matching "milk" word boundaries in text (case-insensitive)
MILK = re.compile(r"\bmilk\b", re.IGNORECASE)