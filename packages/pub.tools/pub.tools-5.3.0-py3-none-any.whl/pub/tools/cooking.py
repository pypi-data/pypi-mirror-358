import deprecation

from . import config
from . import formatting

preferred_date_format = formatting.preferred_date_format
preferred_date_format_long = formatting.preferred_date_format_long

daterange_to_month_start = formatting.daterange_to_month_start
daterange_to_month_end = formatting.daterange_to_month_end
standardize_range = formatting.standardize_range

# convert date into a format recognized by RIS
ris_month = formatting.ris_month

monthlist = formatting.monthlist
punclist = formatting.punclist


@deprecation.deprecated(
    deprecated_in="5.0", removed_in="6.0", current_version=config.VERSION, details="Import from `formatting` instead."
)
def cook_date(year="", month="", day="", medlinedate="", end=False):
    return formatting.format_date(year, month, day, medlinedate, end)


@deprecation.deprecated(
    deprecated_in="5.0", removed_in="6.0", current_version=config.VERSION, details="Import from `formatting` instead."
)
def cook_date_str(value):
    return formatting.format_date_str(value)


@deprecation.deprecated(
    deprecated_in="5.0", removed_in="6.0", current_version=config.VERSION, details="Import from `formatting` instead."
)
def cook_date_ris(value):
    return formatting.format_date_ris(value)


@deprecation.deprecated(
    deprecated_in="5.0", removed_in="6.0", current_version=config.VERSION, details="Import from `formatting` instead."
)
def cook_date_months(start, end):
    return formatting.format_date_months(start, end)


@deprecation.deprecated(
    deprecated_in="5.0", removed_in="6.0", current_version=config.VERSION, details="Import from `formatting` instead."
)
def blankify(datastring=""):
    return formatting.blankify(datastring)


@deprecation.deprecated(
    deprecated_in="5.0", removed_in="6.0", current_version=config.VERSION, details="Import from `formatting` instead."
)
def depunctuate(datastring):
    return formatting.depunctuate(datastring)


@deprecation.deprecated(
    deprecated_in="5.0", removed_in="6.0", current_version=config.VERSION, details="Import from `formatting` instead."
)
def alphanum(value):
    return formatting.alphanum(value)
