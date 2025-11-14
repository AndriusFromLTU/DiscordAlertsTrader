#!/usr/bin/env python3
"""Test Unicode apostrophe matching"""

# Regular ASCII apostrophe
ascii_apos = "I'm trimming"
# Unicode right single quotation mark (what Discord uses)
unicode_apos = "I'm trimming"

alert = "**Contract:** QQQ 11/12 622P\r\n\r\n**I'm trimming here for 52%**"

print(f"ASCII apostrophe: {repr(ascii_apos)}")
print(f"Unicode apostrophe: {repr(unicode_apos)}")
print(f"Alert snippet: {repr(alert[30:50])}")

search_list = [
    ascii_apos,
    unicode_apos,
    "I'm closing",
    "I'm closing",
    "full profit",
    "fully close",
]

print(f"\nSearch list: {[repr(s) for s in search_list]}")
print(f"Match result: {any(a in alert for a in search_list)}")

# Check each individually
for s in search_list:
    if s in alert:
        print(f"  MATCHED: {repr(s)}")
