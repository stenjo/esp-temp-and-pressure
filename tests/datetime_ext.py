from datetime import datetime as _datetime, timedelta as _timedelta, date as _date, timezone
import time as _tmod

class timedelta(_timedelta):
    pass
    
class date(_date):
    def strftime(self, format):
        """
        Format using strftime().

        Example: "%d/%m/%Y, %H:%M:%S"
        """
        return _wrap_strftime(self, format, self.timetuple())


class datetime(_datetime):
    
    def strftime(self, format):
        """
        Format using strftime().

        Example: "%d/%m/%Y, %H:%M:%S"
        """
        return _wrap_strftime(self, format, self.timetuple())
    
    # def now(self, tz=timezone.utc):
    #     return super().now(tz)

    # def fromtimestamp(this, ts, tz=None):
    #     if isinstance(ts, float):
    #         ts, us = divmod(round(ts * 1_000_000), 1_000_000)
    #     else:
    #         us = 0
    #     if tz is None:
    #         raise NotImplementedError
    #     else:
    #         dt = this(*_tmod.gmtime(ts)[:6], microsecond=us, tzinfo=tz)
    #         dt = tz.fromutc(dt)
    #     return dt

def _strftime(format, timetuple):
    
    year, month, day, hour, minute, second, microsecond, _ = timetuple
    mapping = {
        '%d':f"{day:02d}",
        '%m': f"{month:02d}",
        '%H': f"{hour:02d}",
        '%M': f"{minute:02d}",
        '%S': f"{second:02d}",
        '%Y': f"{year}",
        '%y': f"{year}"[2:],
        '%f': f"{microsecond:06d}"
        }
    
    params = [format[i:i+2] for i, c in enumerate(format) if c == '%']
    
    while params:
        p = params.pop()
        format = format.replace(p, mapping[p])

    return format
                    
def _wrap_strftime(object, format, timetuple):
    # Don't call utcoffset() or tzname() unless actually needed.
    fReplace = None  # the string to use for %f
    zReplace = None  # the string to use for %z
    colonZReplace = None  # the string to use for %:z
    zReplace = None  # the string to use for %Z

    # Scan format for %z, %:z and %Z escapes, replacing as needed.
    newFormat = []
    push = newFormat.append
    i, n = 0, len(format)
    while i < n:
        ch = format[i]
        i += 1
        if ch == '%':
            if i < n:
                ch = format[i]
                i += 1
                if ch == 'f':
                    if fReplace is None:
                        fReplace = '%06d' % getattr(object,
                                                    'microsecond', 0)
                    newFormat.append(fReplace)
                elif ch == 'z':
                    if zReplace is None:
                        if hasattr(object, "utcoffset"):
                            zReplace = object._format_offset(object.utcoffset(), sep="")
                        else:
                            zReplace = ""
                    assert '%' not in zReplace
                    newFormat.append(zReplace)
                elif ch == ':':
                    if i < n:
                        ch2 = format[i]
                        i += 1
                        if ch2 == 'z':
                            if colonZReplace is None:
                                if hasattr(object, "utcoffset"):
                                    colonZReplace = object._format_offset(object.utcoffset(), sep=":")
                                else:
                                    colonZReplace = ""
                            assert '%' not in colonZReplace
                            newFormat.append(colonZReplace)
                        else:
                            push('%')
                            push(ch)
                            push(ch2)
                elif ch == 'Z':
                    if zReplace is None:
                        zReplace = ""
                        if hasattr(object, "tzname"):
                            s = object.tzname()
                            if s is not None:
                                # strftime is going to have at this: escape %
                                zReplace = s.replace('%', '%%')
                    newFormat.append(zReplace)
                else:
                    push('%')
                    push(ch)
            else:
                push('%')
        else:
            push(ch)
    newFormat = "".join(newFormat)
    return _strftime(newFormat, timetuple)
