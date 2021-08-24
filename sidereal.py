#!/usr/bin/env python

import math


def ymd2jd(year, month, day):
    """
    Converts a year, month, and day to a Julian Date.
    This function uses an algorithm from the book "Practical Astronomy with your
    Calculator" by Peter Duffet-Smith (Page 7)

    Parameters
    ----------
    year : int
        A Gregorian year
    month : int
        A Gregorian month
    day : int
        A Gregorian day

    Returns
    -------
    jd : float
        A Julian Date computed from the input year, month, and day.

    """
    if month == 1 or month == 2:
        yprime = year - 1
        mprime = month + 12
    else:
        yprime = year
        mprime = month

    if year > 1582 or (year == 1582 and (month >= 10 and day >= 15)):
        A = int(yprime / 100)
        B = 2 - A + int(A/4.0)
    else:
        B = 0

    if yprime < 0:
        C = int((365.25 * yprime) - 0.75)
    else:
        C = int(365.25 * yprime)

    D = int(30.6001 * (mprime + 1))

    return B + C + D + day + 1720994.5


def utcDatetime2gmst(datetimeObj):
    """
    Converts a Python datetime object with UTC time to Greenwich Mean Sidereal Time.
    This function uses an algorithm from the book "Practical Astronomy with your
    Calculator" by Peter Duffet-Smith (Page 17)

    Parameters
    ----------
    datetimeObj : datetime.datetime
        A Python datetime.datetime object

    Returns
    -------
    < > : datetime.datetime
        A Python datetime.datetime object corresponding to the Greenwich Mean
        Sidereal Time of the input datetime.datetime object.

    """
    jd = ymd2jd(datetimeObj.year, datetimeObj.month, datetimeObj.day)

    S = jd - 2451545.0
    T = S / 36525.0
    T0 = 6.697374558 + (2400.051336 * T) + (0.000025862 * T**2)
    T0 = T0 % 24

    UT = datetime2decHours(datetimeObj.time()) * 1.002737909
    T0 += UT

    GST = T0 % 24

    return GST


def datetime2decHours(time):
    """
    Converts a datetime.time or datetime.datetime object into decimal time.

    Parameters
    ----------
    time : datetime.time or datetime.datetime

    Returns
    -------
    decTime : float
        A decimal number representing the input time
    """
    return time.hour + time.minute/60.0 + time.second/3600.0 + time.microsecond/3600000000.0


def dec2sex(deci):
    """
    Converts a Decimal number (in hours or degrees) to Sexagesimal.

    Parameters
    ----------
    deci : float
        A decimal number to be converted to Sexagismal.

    Returns
    -------
    hd : int
        hours or degrees
    m : int
        minutes or arcminutes
    s : float
        seconds or arcseconds
    """
    (hfrac, hd) = math.modf(deci)
    (min_frac, m) = math.modf(hfrac * 60)
    s = min_frac * 60.
    return (int(hd), int(m), s)
