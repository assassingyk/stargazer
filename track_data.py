#!/usr/bin/env python
from math import atan2, cos, pi, sin, sqrt
from datetime import datetime, timedelta

from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv

from .sidereal import utcDatetime2gmst, ymd2jd
from shapely.geometry import Point, Polygon, LineString

# twoline2rv() function returns a Satellite object whose attributes
# carry the data loaded from the TLE entry

# Satellite attributes of interest
# satnum     -  Unique satellite number given in the TLE file
# epochyr    - Full four-digit year of this element set's epoch moment
# epochdays  - Fractional days into the year of the epoch moment
# jdsatepoch - Julian date of the epoch (computed from epochyr and epochdays)
# ndot       - First time derivative of the mean motion (ignored by SGP4)
# nddot      - Second time derivative of the mean motion (ignored by SGP4)
# bstar      - Ballistic drag coefficient B* in inverse earth radii
# inclo      - Inclination in radians
# nodeo      - Right ascension of ascending node in radians
# ecco       - Eccentricity
# argpo      - Argument of perigee in radians
# mo         - Mean anomaly in radians
# no         - Mean motion in radians per minute

# Calculate groundtrack


def groundtrack(vector):
    x = vector[0]
    y = vector[1]
    z = vector[2]

    # Constants for WGS-87 ellipsoid
    a = 6378.137
    e = 8.1819190842622e-2

    # Groundtrack
    b = sqrt(pow(a, 2) * (1-pow(e, 2)))
    ep = sqrt((pow(a, 2)-pow(b, 2))/pow(b, 2))
    p = sqrt(pow(x, 2)+pow(y, 2))
    th = atan2(a*z, b*p)
    lon = atan2(y, x)
    lat = atan2((z+ep*ep*b*pow(sin(th), 3)), (p-e*e*a*pow(cos(th), 3)))
    n = a/sqrt(1-e*e*pow(sin(lat), 2))

    alt = p/cos(lat)-n
    lat = (lat*180)/pi
    lon = (lon*180)/pi

    return (lat, lon, alt)


issline1 = (
    '1 25544U 98067A   21227.32718450  .00001179  00000-0  29623-4 0  9998')
issline2 = (
    '2 25544  51.6442  50.2621 0001283 311.2543 108.3261 15.48903018297764')


def geojson(name='ISS', line1=issline1, line2=issline2, nowtime=datetime.now(), time=360, step=30):

    satellite = twoline2rv(line1, line2, wgs72)

    #date = datetime(2000, 6, 29, 12, 46, 19)
    date = nowtime
    delta = timedelta(minutes=0.2)

    # empty array for GeoJSON LineString for groundtrack plotting
    points = []
    lines = []
    last = None
    now = None
    anow = None
    vnow = None
    timeseries = {}

    # Loop in one-minute steps to calculate track
    for n in range(0, time*5+1):
        # print date
        position, velocity = satellite.propagate(date.year, date.month, date.day,
                                                 date.hour, date.minute, date.second)
        # print(position)
        # print(velocity)
        lat, gmra, alt = groundtrack(position)
        gmst = utcDatetime2gmst(date)
        # print gmst
        lon = (gmst * 15.0) - gmra
        lon = ((lon + 180.0) % 360.0) - 180.0
        if n == 0:
            last = lon
            now = [lon, lat]
            anow = alt
            vnow = sqrt(pow(velocity[0], 2) +
                        pow(velocity[1], 2)+pow(velocity[2], 2))
        elif not n % (step*5):
            timeseries[date.strftime("%H:%M")] = [lon, lat]
        # print lon
        # add current point coordinates to GeoJSON LineString array
        if abs(last-lon) > 180:
            lines.append(LineString(points))
            points = []
        last = lon
        points.append([lon, lat])
        date = date+delta
    if points:
        lines.append(LineString(points))

    print(anow)
    print(vnow)

    # Generate GeoJSON LineString for groundtrack
    line = {'geometry': lines}
    now = {'geometry': {0: Point(now)}, 'name': {0: name}}
    timeline = {'geometry': {}, 'name': {}}
    i = 0
    for t in timeseries:
        timeline['name'][i] = t
        timeline['geometry'][i] = Point(timeseries[t])
        i += 1

    # Bottle function returns dict as JSON
    return (line, now, timeline, anow, vnow)
