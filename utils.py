import re


ALLOWED_CHARS_PATTERN = re.compile(r"[^0-9A-Za-z+=\-*/^(). ,:∫∂]")


def normalize_text(s: str) -> str:
"""Basic normalization and OCR corrections."""
if s is None:
return ''
s = s.replace('\u2013', '-')
s = s.replace('−', '-')
s = s.replace('×', '*')
s = s.replace('\u00d7', '*')
s = s.replace('—', '-')
s = s.replace('\n', ' ')
s = s.replace('\t', ' ')
# common OCR mistakes
s = s.replace('O', '0')
s = s.replace('l', '1')
# Keep only allowed characters
s = ALLOWED_CHARS_PATTERN.sub('', s)
# collapse multiple spaces
s = ' '.join(s.split())
return s