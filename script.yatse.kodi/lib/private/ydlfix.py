# -*- coding: utf-8 -*-
import sys

from ..youtube_dl import utils


# noinspection PyUnresolvedReferences
def fixed_unified_strdate(date_str, day_first=True):
    """Return a string with the date in the format YYYYMMDD"""
    if date_str is None:
        return None
    upload_date = None
    # Replace commas
    date_str = date_str.replace(',', ' ')
    # Remove AM/PM + timezone
    date_str = re.sub(r'(?i)\s*(?:AM|PM)(?:\s+[A-Z]+)?', '', date_str)
    _, date_str = extract_timezone(date_str)

    for expression in date_formats(day_first):
        # noinspection PyBroadException
        try:
            upload_date = datetime.datetime.strptime(date_str, expression).strftime('%Y%m%d')
        except ValueError:
            pass
        except:  # Added to bypass Python bug on Kodi 17 - Windows
            pass
    if upload_date is None:
        timetuple = email.utils.parsedate_tz(date_str)
        if timetuple:
            # noinspection PyBroadException
            try:
                upload_date = datetime.datetime(*timetuple[:6]).strftime('%Y%m%d')
            except ValueError:
                pass
            except:  # Added to bypass Python bug on Kodi 17 - Windows
                pass
    if upload_date is not None:
        return compat_str(upload_date)


# noinspection PyUnresolvedReferences
def fixed_unified_timestamp(date_str, day_first=True):
    if date_str is None:
        return None

    date_str = re.sub(r'[,|]', '', date_str)

    pm_delta = 12 if re.search(r'(?i)PM', date_str) else 0
    timezone, date_str = extract_timezone(date_str)

    # Remove AM/PM + timezone
    date_str = re.sub(r'(?i)\s*(?:AM|PM)(?:\s+[A-Z]+)?', '', date_str)

    # Remove unrecognized timezones from ISO 8601 alike timestamps
    m = re.search(r'\d{1,2}:\d{1,2}(?:\.\d+)?(?P<tz>\s*[A-Z]+)$', date_str)
    if m:
        date_str = date_str[:-len(m.group('tz'))]

    for expression in date_formats(day_first):
        # noinspection PyBroadException
        try:
            dt = datetime.datetime.strptime(date_str, expression) - timezone + datetime.timedelta(hours=pm_delta)
            return calendar.timegm(dt.timetuple())
        except ValueError:
            pass
        except:  # Added to bypass Python bug on Kodi 17 - Windows
            pass
    timetuple = email.utils.parsedate_tz(date_str)
    if timetuple:
        return calendar.timegm(timetuple) + pm_delta * 3600


# noinspection PyMethodMayBeStatic
class ReplacementStdErr(sys.stderr.__class__):
    def isatty(self):
        return False


def patch_youtube_dl():
    utils.unified_strdate.__code__ = fixed_unified_strdate.__code__
    utils.unified_timestamp.__code__ = fixed_unified_timestamp.__code__
    sys.stderr.__class__ = ReplacementStdErr
    try:
        import _subprocess
    except ImportError:
        # noinspection PyProtectedMember
        from lib.private.subprocess import _subprocess
