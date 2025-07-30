__all__ = ['from_dict', 'from_file', 'to_dict', 'as_dict', 'fields', 'Field', 'dictparser', 'type_info']

import sys

if sys.version_info >= (3, 11):
    from ._init_p311 import from_dict
    from ._init_p311 import from_file
    from ._init_p311 import to_dict
    from ._init_p311 import as_dict
    from ._init_p311 import fields
    from ._init_p311 import Field
    from ._init_p311 import dictparser
    from ._init_p311 import type_info
else:
    from ._init_p36 import from_dict
    from ._init_p36 import from_file
    from ._init_p36 import to_dict
    from ._init_p36 import as_dict
    from ._init_p36 import fields
    from ._init_p36 import Field
    from ._init_p36 import dictparser
    from ._init_p36 import type_info
