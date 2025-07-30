from enum import Enum
class Search:
    class filter_date(Enum):
        ANYDATE = ""
        DAY = "day"
        WEEK = "week"
        MONTH = "month"
        YEAR = "year"
class SearchImage:
    class filter_color(Enum):
        ANYCOLOR = ""
        ORANGE = "orange"
        RED = "red"
        GREEN = "green"
        YELLOW = "yellow"
        BLUE = "blue"
        TEAL = "teal"
        PINK = "pink"
        PURPLE = "purple"
        GRAY = "gray"
        WHITE = "white"
        BROWN = "brown"
        BLACK = "black"
    class filter_size(Enum):
        ANYSIZE = ""
        LARGE = "large"
        MEDIUM = "medium"
        ICON = "icon"
    class filter_type(Enum):
        ANYTYPE = ""
        CLIPART = "clipart"
        LINEART = "lineart"
        ANIMATED = "animated"
    class filter_date(Enum):
        ANYDATE = ""
        DAY = "day"
        WEEK = "week"
        MONTH = "month"
        YEAR = "year"
class SearchVideo:
    class filter_length(Enum):
        ANYLENGTH = ""
        SHORT = "short"
        MEDIUM = "medium"
        LONG = "long"
    class filter_date(Enum):
        ANYDATE = ""
        DAY = "day"
        WEEK = "week"
        MONTH = "month"
        YEAR = "year"
    class filter_resolution(Enum):
        ANYRESOLUTION = ""
        HIGH = "high"
class SearchNews:
    class filter_date(Enum):
        ANYDATE = ""
        DAY = "day"
        WEEK = "week"
        MONTH = "month"
        YEAR = "year"
    class filter_sort(Enum):
        ANYSORT = ""
        DATE = "date"