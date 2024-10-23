from ics_parser import ICS
from datetime import datetime, timedelta
from mrequests import mrequests
import re, time

def contains_non_unicode_bytes(s):
    try:
        s.encode('utf-8')
    except UnicodeEncodeError:
        return True
    return False

import sys

def log_error(tag, message):
    print("[ERROR] [{}] {}".format(tag, message), file=sys.stderr)

def log_info(tag, message):
    print("[INFO] [{}] {}".format(tag, message))

def is_continuation_byte(byte):
    return (byte & 0xC0) == 0x80

def is_valid_utf8(byte_string):
    bytes = bytearray(byte_string)
    i = 0
    while i < len(bytes):
        byte = bytes[i]
        if byte <= 0x7F:
            i += 1
        elif (byte & 0xE0) == 0xC0:
            if i + 1 >= len(bytes) or not is_continuation_byte(bytes[i + 1]):
                log_error("UTF8_CHECK", "Invalid 2-byte sequence at index {}".format(i))
                return False
            i += 2
        elif (byte & 0xF0) == 0xE0:
            if i + 2 >= len(bytes) or not is_continuation_byte(bytes[i + 1]) or not is_continuation_byte(bytes[i + 2]):
                log_error("UTF8_CHECK", "Invalid 3-byte sequence at index {}".format(i))
                return False
            i += 3
        elif (byte & 0xF8) == 0xF0:
            if i + 3 >= len(bytes) or not is_continuation_byte(bytes[i + 1]) or not is_continuation_byte(bytes[i + 2]) or not is_continuation_byte(bytes[i + 3]):
                log_error("UTF8_CHECK", "Invalid 4-byte sequence at index {}".format(i))
                return False
            i += 4
        else:
            log_error("UTF8_CHECK", "Invalid UTF-8 start byte at index {}".format(i))
            return False
    log_info("UTF8_CHECK", "Valid UTF-8 string")
    return True


def dtStrToIso(dtstart):
    # Assuming the format of dtstart is '20230412T165722Z'
    # We remove the 'Z' as it indicates UTC and 'fromisoformat' does not support 'Z'
    dtstart = dtstart.rstrip('Z')
    time_iso = None
    date_part = dtstart[:8]
    
    # Insert hyphens and colons to match ISO 8601 format
    date_iso = "{}-{}-{}".format(date_part[:4], date_part[4:6], date_part[6:])
    if len(dtstart) > 10:
        time_part = dtstart[9:]
        time_iso = "{}:{}:{}".format(time_part[:2], time_part[2:4], time_part[4:])
        return "{}T{}".format(date_iso, time_iso)
    else:
        return date_iso

def toDtStr(date_input):
    if date_input is None:
        return None
    
    if isinstance(date_input, str):
        # Assume the string is already in the correct format.
        pattern = re.compile("^([0-9]+T*[0-9]*)Z*$")        
        if pattern.match(date_input):
            return date_input
    
    if isinstance(date_input, tuple) and len(date_input) >= 6:
        # Format the time tuple to the datetime string.
        return "{:04d}{:02d}{:02d}T{:02d}{:02d}{:02d}Z".format(
            date_input[0], date_input[1], date_input[2],
            date_input[3], date_input[4], date_input[5]) 
   
    raise ValueError("Invalid date input type. Must be datetime string or time tuple.")

def toDict(event_tuple):
    # print(event_tuple)
    if not event_tuple:
        return None
    
    dt = dtStrToIso(event_tuple[1])
    if len(dt) > 10:
        return {
            "start": {"dateTime": dt},
            "summary": event_tuple[0]
        }
    else:
        return {
            "start": {"date": dt},
            "summary": event_tuple[0]
        }


class ResponseWithProgress(mrequests.Response):
    _total_read = 0
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._total_read = 0

    def readinto(self, buf, size=0):
        bytes_read = super().readinto(buf, size)
        self._total_read += bytes_read
        print("Progress: {:.2f}%".format(self._total_read / (self._content_size * 0.01)))
        return bytes_read

class Calendar(ICS):
    
    startTime = None
    endTime = None
    daysAhead = None
    sources = []
    def __init__(self, filename=None, start=None, end=None, daysAhead=None, url=None):
        super().__init__()
        self.reset()
        self.sources = []
        if start is not None:
            self.start(start)
            
        if end is not None:
            self.end(end)
        
        if daysAhead is not None:
            self.startTime = datetime.now().timetuple()
            self.start(self.startTime)
            self.endTime = (datetime.now() + timedelta(days=daysAhead)).timetuple()
            self.end(self.endTime)
            self.daysAhead = daysAhead

        if filename is not None:
            self.parseFile(filename)
    
    def parseFile(self, filename):
        print(f"Parsing file: {filename}")
        with open(filename) as f:
            count = self.parseIcs(f.read())
        print(f"Parsed {count} items from file")
        return count

    def parseURL(self, url):
        print(f"Parsing URL: {url}")
        url = url.replace('webcal://', 'http://')
        if url not in self.sources:
            self.sources.append(url)
        return self._parseChunks(url)

    def _parseChunks(self, url, chunkSize=1024):
        print(f"Fetching URL in chunks: {url}")
        start = time.ticks_ms()
        timeout = 20000
        response = None
        try:
            response = mrequests.get(url, headers={b"accept": b"text/html"}, response_class=ResponseWithProgress)
        except Exception as e:
            print(f"Exception occurred during request: {e}")
            return 0
        finally:
            if response and response.status_code == 200:
                count = 0
                try:
                    while time.ticks_diff(time.ticks_ms(), start) < timeout:
                        chunk = response.read(chunkSize)
                        if not chunk or len(chunk) == 0:
                            break
                        try:
                            # decoded_chunk = chunk.decode(encoding)
                            # if contains_non_unicode_bytes(decoded_chunk):
                            #     print("Non-Unicode bytes detected, skipping chunk")
                            count = self.parseIcs(chunk)
                            start = time.ticks_ms()
                        except UnicodeError as e:
                            print(f"UnicodeDecodeError occurred: {e}")
                            is_valid_utf8(chunk)
                    if time.ticks_diff(time.ticks_ms(), start) > timeout:
                        print(f"Timeout reading  {url}")
                        
                finally:
                    response.close()
                    
                print(f"Parsed {count} items from URL in chunks")
                return count
            
            else:
                print(response)
                if response is not None:
                    response.close()
                    print(f"Failed to fetch calendar data in chunks, status code: {response.status_code}")

    def refresh(self, start_date=None, end_date=None):
        print("Refreshing calendar")
        self.reset()
        print("reset")
        items = 0
        if start_date is not None:
            self.start(start_date)
        elif self.startTime is not None:
            self.start(self.startTime)  
            
        if end_date is not None:
            self.end(end_date)
        elif self.endTime is not None:
            self.end(self.endTime)

        if self.daysAhead is not None:
            self.startTime = datetime.now().timetuple()
            self.start(self.startTime)
            self.endTime = (datetime.now() + timedelta(days=self.daysAhead)).timetuple()
            self.end(self.endTime)

        for url in self.sources:
            try:
                items = self._parseChunks(url)
            except Exception as e:
                print(f"Error parsing url: {url}, {e}")
        print(f"Refreshed {items} items")
        return items
    
    def first(self):
        ev = None
        try:
            ev = self.getFirst()
            return toDict(ev)
        except UnicodeError:
            print("GetFirst Unicode error", ev)
        
    def next(self):
        ev = None
        try:
            ev = self.getNext()
            return toDict(ev)
        except UnicodeError:
            print("GetNext Unicode error", ev)
    
    def start(self, startDate):
        self.setStartDate(toDtStr(startDate))
        
    def end(self, endDate):
        self.setEndDate(toDtStr(endDate))
