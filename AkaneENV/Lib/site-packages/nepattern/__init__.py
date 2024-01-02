from tarina import Empty as Empty  # noqa

from .base import DirectPattern as DirectPattern
from .base import MappingPattern as MappingPattern
from .base import RegexPattern as RegexPattern
from .base import SequencePattern as SequencePattern
from .base import SwitchPattern as SwitchPattern
from .base import UnionPattern as UnionPattern
from .context import Patterns as Patterns
from .context import all_patterns as all_patterns
from .context import create_local_patterns as create_local_patterns
from .context import local_patterns as local_patterns
from .context import switch_local_patterns as switch_local_patterns
from .context import reset_local_patterns as reset_local_patterns
from .core import BasePattern as BasePattern
from .core import MatchMode as MatchMode
from .core import ValidateResult as ValidateResult
from .core import set_unit as set_unit
from .exception import MatchFailed as MatchFailed
from .main import DATETIME as DATETIME
from .main import EMAIL as EMAIL
from .main import FLOAT as FLOAT
from .main import HEX as HEX
from .main import HEX_COLOR as HEX_COLOR
from .main import INTEGER as INTEGER
from .main import IP as IP
from .main import NUMBER as NUMBER
from .main import URL as URL
from .main import STRING as STRING
from .main import AnyOne as AnyOne
from .main import AnyString as AnyString
from .main import Bind as Bind
from .main import type_parser as type_parser
from .util import AllParam as AllParam
from .util import TPattern as TPattern
from .util import RawStr as RawStr

PatternModel = MatchMode
parser = type_parser
