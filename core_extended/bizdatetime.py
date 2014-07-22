"""
Copyright (c) 2011 Sergiy Kuzmenko

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

https://bitbucket.org/shelldweller/python-bizdatetime

A class for calculating business date deltas based on a policy.

Definitions:

    Weekend - a day off reoccurring on a weekly basis (no shifting weekends
    supported)

    Holiday - a special day off. The app is agnostic as to how holidays reoccur.
    It expects a list of date instances that represent a sequence of holidays
    within the desired range.

    Policy - a definition of weekends and holidays.

"""

MON = 0
TUE = 1
WED = 2
THU = 3
FRI = 4
SAT = 5
SUN = 6

from datetime import date, timedelta


class Policy(object):
    """
    Policy class defined holidays and weekends. All calculations related to
    business day arithmetics are done in teh context of Policy.
    """

    def __init__(self, weekends=[], holidays=[]):
        if len(weekends) > 6:
            raise AssertionError("Too many weekends per week")
        self.weekends = weekends
        self._holidays = []
        #holidays
        self._set_holidays(holidays)

    def _get_holidays(self):
        return self._holidays

    def _set_holidays(self, holidays):
        if holidays:
            self._holidays = list(holidays)
            self._holidays.sort()
        else:
            self._holidays = []

    holidays = property(_get_holidays, _set_holidays)

    def is_empty(self):
        """ Returns True is policy has no weekends or holidays.

        >>> policy = Policy()
        >>> policy.is_empty()
        True
        >>> policy = Policy(weekends=[SUN,])
        >>> policy.is_empty()
        False
        """
        return not (self.weekends or self._holidays)

    def is_weekend(self, day):
        """ Returns True only if the day falls on a weekend.

        >>> policy = Policy(weekends=(SAT, SUN))
        >>> policy.is_weekend(date(2011, 7, 1)) # Friday
        False
        >>> policy.is_weekend(date(2011, 7, 2)) # Saturday
        True
        >>> policy.is_weekend(date(2011, 7, 3)) # Sunday
        True
        >>> policy.is_weekend(date(2011, 7, 4)) # Monday
        False
        """
        return day.weekday() in self.weekends

    def is_holiday(self, day):
        """ Returns true only if the day falls on a holiday.
        >>> policy = Policy(weekends=(SAT, SUN), holidays=(date(2011,  7,  1),))
        >>> policy.is_holiday(date(2011, 7, 1)) # Friday
        True
        >>> policy.is_holiday(date(2011, 7, 2)) # Saturday
        False
        """
        return day in self._holidays

    def is_day_off(self, day):
        """ Returns True if the day is either weekend or holiday.

        >>> policy = Policy(weekends=(SAT, SUN), holidays=(date(2011,  7,  1), ))
        >>> policy.is_day_off(date(2011, 7, 1)) # Friday
        True
        >>> policy.is_day_off(date(2011, 7, 2)) # Saturday
        True
        >>> policy.is_day_off(date(2011, 7, 3)) # Sunday
        True
        >>> policy.is_day_off(date(2011, 7, 4)) # Monday
        False
        """
        return self.is_weekend(day) or self.is_holiday(day)

    def closest_biz_day(self, day, forward=True):
        """If the given date falls on a weekend or holiday, returns the closest
        business day. Otherwise the original date is returned. If forward is
        True (default) the returned date will be next closest business date.
        Otherwise closest previous business date will be retured.

        >>> policy = Policy(weekends=(SAT, SUN), holidays=(date(2011,  7,  1), ))
        >>> policy.closest_biz_day(date(2011, 6, 30)) # regular business day
        datetime.date(2011, 6, 30)
        >>> policy.closest_biz_day(date(2011, 7, 1)) # Friday of long weekend
        datetime.date(2011, 7, 4)
        >>> policy.closest_biz_day(date(2011, 7, 1), False) # Previous closest buisuness day
        datetime.date(2011, 6, 30)

        """

        if forward:
            delta = timedelta(days=1)
        else:
            delta = timedelta(days=-1)
        while day.weekday() in self.weekends or day in self.holidays:
            day = day + delta
        return day

    def holidays_between(self, day1, day2, skip_weekends=True):
        """
        Returns the number of holidays between two given dates, excluding
        boundaries. If skip_weekends is True (default) holidays occuring on
        weekends will not be counted.

        >>> policy = Policy(weekends=(SAT, SUN), holidays=(date(2011,  7,  1), date(2011, 8, 1)))
        >>> policy.holidays_between(date(2011, 6, 12), date(2011, 9, 12))
        2
        >>> policy.holidays_between(date(2011,  7,  1), date(2011, 8, 1))
        0
        """

        if day1 > day2:
            return self.holidays_between(day2, day1)
        if day1 == day2:
            return 0
        n = 0
        #FIXME: should probably use bisect here
        for h in self._holidays:
            if h > day1:
                if h >= day2:
                    break
                if skip_weekends:
                    if h.weekday() not in self.weekends:
                        n += 1
                else:
                    n += 1
        return n

    def subtract(self, day, delta):
        '''
        Inverse of add, just passes negative delta to add.
        '''
        return self.add(day, -delta)

    def add(self, day, delta):
        """
        Adds the number of business days specified by delta to the given day.
        Delta can be a timedelta object or an integer. Delta can also be negative.

        >>> policy = Policy(weekends=(SAT, SUN), holidays=(date(2011,7,1), date(2011,8,1)))
        >>> day = date(2011, 6, 29) # Wednesday
        >>> policy.add(day, 2) # Monday after the long weekend
        datetime.date(2011, 7, 4)
        >>> policy.add(day, 22) # Spanning two holidays and several weekends
        datetime.date(2011, 8, 2)
        >>> policy.add(day, -10) # 10 business days (2 weeks) ago
        datetime.date(2011, 6, 15)
        """

        if isinstance(delta, timedelta):
            days = delta.days
        else:
            days = int(delta)
        if days == 0:
            return day

        if days < 0:
            sign = -1
            look_forward = False
        else:
            sign = 1
            look_forward = True

        if self.weekends:
            weeklen = 7 - len(self.weekends)
            weeks_add = abs(days) / weeklen * sign
            days_add = abs(days) % weeklen * sign
        else:
            weeks_add = 0
            days_add = days

        new_date = day + timedelta(days=weeks_add * 7)
        while days_add:
            # remaining days may or may not include weekends;
            new_date = new_date + timedelta(sign)
            if not self.is_weekend(new_date):
                days_add -= sign

        days_add = self.holidays_between(day, new_date)  # any holidays?
        if days_add:
            return self.add(new_date, days_add * sign)
        else:
            return self.closest_biz_day(new_date, look_forward)

    def weekends_between(self, day1, day2):
        """
        Returns the number of weekends between two dates, including upper boundary.

        >>> policy = Policy(weekends=(SAT, SUN))
        >>> policy.weekends_between(date(2011, 6, 3), date(2011, 6, 15))
        4
        >>> policy.weekends_between(date(2011, 6, 4), date(2011, 6, 11)) # SAT to SAT
        2
        """

        # FIXME: check about boundaries
        if day2 < day1:
            return self.weekends_between(day2, day1)
        delta = day2 - day1
        weeks = delta.days / 7
        extra = delta.days % 7
        n = weeks * len(self.weekends)
        while extra:
            day = day2 - timedelta(days=extra)
            if self.is_weekend(day):
                n += 1
            extra -= 1
        return n

    def biz_day_delta(self, day1, day2):
        """
        Returns the number of business days between day1 and day2, excluding
        boundaries.

        >>> policy = Policy(weekends=(SAT, SUN), holidays=(date(2011,  7,  1),))
        >>> policy.biz_day_delta(date(2011, 7, 4), date(2011, 6, 30)) # one holiday, one weekend between
        1
        >>> policy.biz_day_delta(date(2011, 6, 10), date(2011, 6, 24), ) # two weekends between
        10
        """
        if day2 < day1:
            return self.biz_day_delta(day2, day1)

        delta = day2 - day1

        return delta.days - self.weekends_between(day1, day2) - self.holidays_between(day1, day2)

    def biz_days_between(self, day1, day2):
        """
        Returns a list of all business days between day1 and day2, inclusive.

        >>> policy = Policy(weekends=(SAT, SUN), holidays=(date(2013, 9, 2),))
        >>> dlist = policy.biz_days_between(date(2013, 9, 1), date(2013, 9, 30))
        >>> len(dlist) # there are 20 biz days between
        20
        >>> dlist[0] == date(2013, 9, 1) # should not include the starting point if it's not a biz day
        False
        >>> dlist[19] == date(2013, 9, 30) # should include end point
        True
        """
        day1 = self.closest_biz_day(day1, forward=True)
        day2 = self.closest_biz_day(day2, forward=False)
        delta_incl = self.biz_day_delta(day1, day2) + 1
        return [self.add(day1, x) for x in xrange(delta_incl)]

if __name__ == "__main__":
    # run tests when called directly
    import doctest
    doctest.testmod()
