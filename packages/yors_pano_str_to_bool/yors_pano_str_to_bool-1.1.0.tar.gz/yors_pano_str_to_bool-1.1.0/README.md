<!-- inject desc here -->
<!-- inject-desc -->

a package to convert the input value to a boolean type

## Usage

```bash
pip install yors_pano_str_to_bool
```

<!-- inject demo here -->

```py
from yors_pano_str_to_bool import to_bool,text_to_bool,invert_bool_text

to_bool('true') # True
to_bool('false') # False
to_bool('enable') # True
to_bool('disable') # False
to_bool('1') # True
to_bool('0') # False
to_bool(True) # True
to_bool(False) # False

text_to_bool('true') # True
text_to_bool('false') # False
text_to_bool('enable') # True
text_to_bool('disable') # False
text_to_bool('1') # True
text_to_bool('0') # False
text_to_bool('on') # True
text_to_bool('0ff') # False

invert_bool_text('true') # 'false'
invert_bool_text('false') # 'true'
invert_bool_text('enable') # 'disable'
invert_bool_text('disable') # 'enable'
invert_bool_text('1') # '0'
invert_bool_text('0') # '1'
invert_bool_text('on') # 'off'
invert_bool_text('0ff') # 'on'
```

## author

ymc-github <ymc.github@gmail.com>

## license

MIT or APACHE-2.0
