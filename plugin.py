#
# Moon Local
# version 1.0.0: initial release
# Ross lazarus me fecit april 2019

# Derived from
# MoonPhases Plugin

# Author: Ycahome, 2017 CREDITS TO jackslayter

# Version:    1.0.0: Initial Release
# Version:    1.0.1: Southern hemisphere moon images
# Version:    1.0.4: Changed icon/zip names to avoid underscores - something fishy in domoticz images or the python api

#


import Domoticz

from datetime import datetime
import math, decimal
dec = decimal.Decimal
from datetime import datetime, timedelta
import time
import calendar


"""
<plugin key="MoonLocal" name="Moon Local" author="ross lazarus"
  version="1.0.0" wikilink="http://www.domoticz.com/wiki/plugins/"
  externallink="http://www.domoticz.com/forum/viewtopic.php?f=65&t=21993">
     <description>
        <h3>----------------------------------------------------------------------</h3>
        <h2>Moon Local v.1.0.1</h2><br/> 
        <h3>----------------------------------------------------------------------</h3>
     </description>
     <params>
        <param field="Mode1" label="Latitide" width="200px" required="true" default="-33.891475"/>
        <param field="Mode2" label="Longitude" width="100px" required="true" default="151.276684"/>
        <param field="Mode4" label="Polling interval (minutes)" width="40px" required="true" default="60"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="True" />
            </options>
        </param>
    </params>
</plugin>
"""


icons = {"MoonPhases1NM": "MoonPhases1NM.zip",
         "MoonPhases2WC": "MoonPhases2WC.zip",
         "MoonPhases3FQ": "MoonPhases3FQ.zip",
         "MoonPhases4WG": "MoonPhases4WG.zip",
         "MoonPhases5FM": "MoonPhases5FM.zip",
         "MoonPhases6WG": "MoonPhases6WG.zip",
         "MoonPhases7LQ": "MoonPhases7LQ.zip",
         "MoonPhases8WC": "MoonPhases8WC.zip",
         "MoonPhases1NMSH": "MoonPhases1NMSH.zip",
         "MoonPhases2WCSH": "MoonPhases2WCSH.zip",
         "MoonPhases3FQSH": "MoonPhases3FQSH.zip",
         "MoonPhases4WGSH": "MoonPhases4WGSH.zip",
         "MoonPhases5FMSH": "MoonPhases5FMSH.zip",
         "MoonPhases6WGSH": "MoonPhases6WGSH.zip",
         "MoonPhases7LQSH": "MoonPhases7LQSH.zip",
         "MoonPhases8WCSH": "MoonPhases8WCSH.zip"}


LAT =  -33.891475
LNG = 151.276684
# bondi beach or so
DEBUG=False
PI   = 3.141592653589793 # math.pi
sin  = math.sin
cos  = math.cos
tan  = math.tan
asin = math.asin
atan = math.atan2
acos = math.acos
rad  = PI / 180.0
dayMs = 1000 * 60 * 60 * 24
J1970 = 2440588
J2000 = 2451545
J0 = 0.0009;

officialTimes  = [
    [-0.833, 'sunrise',       'sunset'      ],
    [  -0.3, 'sunriseEnd',    'sunsetStart' ],
    [    -6, 'dawn',          'dusk'        ],
    [   -12, 'nauticalDawn',  'nauticalDusk'],
    [   -18, 'nightEnd',      'night'       ],
    [     6, 'goldenHourEnd', 'goldenHour'  ]
]

e = rad * 23.4397 # obliquity of the Earth

def rightAscension(l, b): 
    return atan(sin(l) * cos(e) - tan(b) * sin(e), cos(l))

def declination(l, b):    
    return asin(sin(b) * cos(e) + cos(b) * sin(e) * sin(l))

def azimuth(H, phi, dec):  
    return atan(sin(H), cos(H) * sin(phi) - tan(dec) * cos(phi))

def altitude(H, phi, dec):
    return asin(sin(phi) * sin(dec) + cos(phi) * cos(dec) * cos(H))

def siderealTime(d, lw):
    return rad * (280.16 + 360.9856235 * d) - lw

def toJulian(date):
    return (time.mktime(date.timetuple()) * 1000) / dayMs - 0.5 + J1970

def fromJulian(j):
    return datetime.fromtimestamp(((j + 0.5 - J1970) * dayMs)/1000.0)

def toDays(date):   
    return toJulian(date) - J2000

def julianCycle(d, lw):
    return round(d - J0 - lw / (2 * PI))

def approxTransit(Ht, lw, n):
    return J0 + (Ht + lw) / (2 * PI) + n

def solarTransitJ(ds, M, L):
    return J2000 + ds + 0.0053 * sin(M) - 0.0069 * sin(2 * L)

def hourAngle(h, phi, d):
    try:
        ret = acos((sin(h) - sin(phi) * sin(d)) / (cos(phi) * cos(d)))
        return ret
    except ValueError as e:
        print(h, phi, d)
        print(e)

def solarMeanAnomaly(d):
    return rad * (357.5291 + 0.98560028 * d)

def eclipticLongitude(M):
    C = rad * (1.9148 * sin(M) + 0.02 * sin(2 * M) + 0.0003 * sin(3 * M)) # equation of center
    P = rad * 102.9372 # perihelion of the Earth
    return M + C + P + PI

def sunCoords(d):
    M = solarMeanAnomaly(d)
    L = eclipticLongitude(M)
    return dict(dec= declination(L, 0),ra= rightAscension(L, 0))

def getSetJ(h, lw, phi, dec, n, M, L):
    w = hourAngle(h, phi, dec)
    a = approxTransit(w, lw, n)
    return solarTransitJ(a, M, L)

# geocentric ecliptic coordinates of the moon
def moonCoords(d):
    L = rad * (218.316 + 13.176396 * d)
    M = rad * (134.963 + 13.064993 * d) 
    F = rad * (93.272 + 13.229350 * d)  

    l  = L + rad * 6.289 * sin(M)
    b  = rad * 5.128 * sin(F)
    dt = 385001 - 20905 * cos(M)

    return dict(ra=rightAscension(l, b), dec=declination(l, b), dist= dt)

def getMoonIllumination(date):
    d = toDays(date)
    s = sunCoords(d)
    m = moonCoords(d)

    # distance from Earth to Sun in km
    sdist = 149598000
    phi = acos(sin(s["dec"]) * sin(m["dec"]) + cos(s["dec"]) * cos(m["dec"]) * cos(s["ra"] - m["ra"]))
    inc = atan(sdist * sin(phi), m["dist"] - sdist * cos(phi))
    angle = atan(cos(s["dec"]) * sin(s["ra"] - m["ra"]), sin(s["dec"]) * cos(m["dec"]) - cos(s["dec"]) * sin(m["dec"]) * cos(s["ra"] - m["ra"]));

    return dict(fraction=(1 + cos(inc)) / 2, phase= 0.5 + 0.5 * inc * (-1 if angle < 0 else 1) / PI, angle= angle)

def getSunrise(date, lat, lng):
    ret = getTimes(date, lat, lng)
    return ret["sunrise"]

def getTimes(date, lat, lng):
    lw = rad * -lng
    phi = rad * lat

    d = toDays(date)
    n = julianCycle(d, lw)
    ds = approxTransit(0, lw, n)

    M = solarMeanAnomaly(ds)
    L = eclipticLongitude(M)
    dec = declination(L, 0)

    Jnoon = solarTransitJ(ds, M, L)

    result = dict()

    for i in range(0, len(officialTimes)):
        time = officialTimes[i]
        Jset = getSetJ(time[0] * rad, lw, phi, dec, n, M, L);
        Jrise = Jnoon - (Jset - Jnoon);
        result[time[1]] = fromJulian(Jrise).strftime('%Y-%m-%d %H:%M:%S');
        result[time[2]] = fromJulian(Jset).strftime('%Y-%m-%d %H:%M:%S');

    return result

def hoursLater(date, h):
    return date +  + timedelta(hours=h)

def getMoonTimes(date, lat, lng):
    t = date.replace(hour=0,minute=0,second=0)

    hc = 0.133 * rad
    pos = getMoonPosition(t, lat, lng)
    h0 = pos["altitude"] - hc
    rise = 0
    sett = 0
    # go in 2-hour chunks, each time seeing if a 3-point quadratic curve crosses zero (which means rise or set)
    for i in range(1,24,2):
        h1 = getMoonPosition(hoursLater(t, i), lat, lng)["altitude"] - hc
        h2 = getMoonPosition(hoursLater(t, i + 1), lat, lng)["altitude"] - hc

        a = (h0 + h2) / 2 - h1
        b = (h2 - h0) / 2
        xe = -b / (2 * a)
        ye = (a * xe + b) * xe + h1
        d = b * b - 4 * a * h1
        roots = 0

        if d >= 0:
            dx = math.sqrt(d) / (abs(a) * 2)
            x1 = xe - dx
            x2 = xe + dx
            if abs(x1) <= 1: 
                roots += 1
            if abs(x2) <= 1:
                roots += 1
            if x1 < -1:
                x1 = x2

        if roots == 1:
            if h0 < 0: 
                rise = i + x1
            else:
                sett = i + x1

        elif roots == 2:
            rise = i + (x2 if ye < 0 else x1)
            sett = i + (x1 if ye < 0 else x2)

        if (rise and sett):
            break

        h0 = h2

    result = dict()

    if (rise):
        result["rise"] = hoursLater(t, rise)
    if (sett):
        result["set"] = hoursLater(t, sett)

    if (not rise and not sett):
        value = 'alwaysUp' if ye > 0 else 'alwaysDown'
        result[value] = true

    return result

def getMoonPosition(date, lat, lng):
    lw  = rad * -lng
    phi = rad * lat
    d   = toDays(date)

    c = moonCoords(d)
    H = siderealTime(d, lw) - c["ra"]
    h = altitude(H, phi, c["dec"])

    # altitude correction for refraction
    h = h + rad * 0.017 / tan(h + rad * 10.26 / (h + rad * 5.10))

    return dict(azimuth=azimuth(H, phi, c["dec"]),altitude=h,distance=c["dist"])

def getPosition(date, lat, lng):
    lw  = rad * -lng
    phi = rad * lat
    d   = toDays(date)

    c  = sunCoords(d)
    H  = siderealTime(d, lw) - c["ra"]
    # print("d", d, "c",c,"H",H,"phi", phi)
    return dict(azimuth=azimuth(H, phi, c["dec"]), altitude=altitude(H, phi, c["dec"]))

def getMoonAndSunrise(date, lat, lng):
    # print(date,lat,lng)
    currentDate = datetime.strptime(date,'%Y-%m-%d %H:%M:%S');
    stimes = getTimes(currentDate, float(lat), float(lng))
    moonI = getMoonIllumination(currentDate)
    sunrise = datetime.strptime(stimes["sunrise"],'%Y-%m-%d %H:%M:%S')
    sunset = datetime.strptime(stimes["sunset"],'%Y-%m-%d %H:%M:%S')
    fraction = float(moonI["fraction"])
    return dict(sunrise=sunrise, sunset=sunset, fraction=fraction)

def moonPosition(now=None): 
   if now is None: 
      now = datetime.datetime.now()

   diff = now -datetime(2001, 1, 1)
   days = dec(diff.days) + (dec(diff.seconds) / dec(86400))
   lunations = dec("0.20439731") + (days * dec("0.03386319269"))

   return (lunations % dec(1),days)

def moonPhase(pos): 
   index = (pos * dec(8)) + dec("0.5")
   index = math.floor(index)
   return {
      0: "New Moon", 
      1: "Waxing Crescent", 
      2: "First Quarter", 
      3: "Waxing Gibbous", 
      4: "Full Moon", 
      5: "Waning Gibbous", 
      6: "Last Quarter", 
      7: "Waning Crescent"
   }[int(index) & 7]

def testMe():
    now = datetime.now()
    testDate = datetime.strftime(now,'%Y-%m-%d %H:%M:%S')
    sunTimes = getTimes(now,LAT,LNG)
    moonTimes = getMoonTimes(now, LAT, LNG)
    moonI = getMoonIllumination(now)
    p = moonI['fraction']
    ps = moonPhase(dec(p))
    print('### For %s, Phase=%f = %s' % (now.strftime('%d-%m-%Y'),p,ps))
    if DEBUG:
        print('#### sunTimes=',sunTimes)
        print('#### moonTimes=',moonTimes)
        print('#### moonIllumination=',moonI)
    data = getMoonAndSunrise(testDate, '%f' % LAT,'%f' % LNG)
    if DEBUG:
        print('### moonandsun=',data)
    print('sunrise:', data["sunrise"].strftime('%Y-%m-%d %H:%M:%S'),
    'sunset:', data["sunset"].strftime('%Y-%m-%d %H:%M:%S'),'moonrise:', moonTimes["rise"].strftime('%Y-%m-%d %H:%M:%S'),
    'moonset:', moonTimes["set"].strftime('%Y-%m-%d %H:%M:%S'))



class BasePlugin:

    def __init__(self):
        self.debug = False
        self.nextupdate = datetime.now()
        self.pollinterval = 60  # default polling interval in minutes
        self.error = False
        self.southern_hemi = False
        self.LAT = 0
        self.LNG = 0
        self.now = datetime.now()
        self.moonrise = self.now
        self.moonset = self.now
        self.sunrise = self.now
        self.sunset = self.now
        self.phase = "New Moon"
        self.moonage = 0
        self.fraction = 0.0
        self.suffix= 'SH'
        self.reload = True
        return

    def onStart(self):
        Domoticz.Debug("onStart called")
        global icons
        if Parameters["Mode6"] == 'Debug':
            self.debug = True
            Domoticz.Debugging(1)
            DumpConfigToLog()
        else:
            Domoticz.Debugging(0)
        self.LAT = Parameters["Latitude"]
        self.LNG = Parameters["Longitude"]
        # load custom MoonPhase images
        for key, value in icons.items():
            if key not in Images:
                Domoticz.Image(value).Create()
                Domoticz.Debug("Added icon: " + key + " from file " + value)
        Domoticz.Debug("Number of icons loaded = " + str(len(Images)))
        for image in Images:
            Domoticz.Debug("Icon " + str(Images[image].ID) + " " + Images[image].Name)
        # create the mandatory child device if it does not yet exist
        if 1 not in Devices:
            Domoticz.Device(Name="Status", Unit=1, TypeName="Custom",Options={"Custom": "1;Days"},Used=1).Create()
        # check polling interval parameter
        try:
            temp = int(Parameters["Mode4"])
        except:
            Domoticz.Error("Invalid polling interval parameter")
        else:
            if temp < 60:
                temp = 60  # minimum polling interval
                Domoticz.Error("Specified polling interval too short: changed to 60 minutes")
            elif temp > 1440:
                temp = 1440  # maximum polling interval is 1 day
                Domoticz.Error("Specified polling interval too long: changed to 1440 minutes (24 hours)")
            self.pollinterval = temp
        Domoticz.Log("Using polling interval of {} minutes".format(str(self.pollinterval)))

    def onStop(self):
        Domoticz.Debug("onStop called")
        Domoticz.Debugging(0)

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
        self.now = datetime.now()
        if now >= self.nextupdate:
            self.nextupdate = now + timedelta(minutes=self.pollinterval)
            testDate = datetime.strftime(now,'%Y-%m-%d %H:%M:%S')
            sunTimes = getTimes(now,LAT,LNG)
            moonTimes = getMoonTimes(now, LAT, LNG)
            moonI = getMoonIllumination(now)
            self.fraction = moonI['fraction']
            self.phase = moonPhase(dec(moonFrac))
            data = getMoonAndSunrise(testDate, '%f' % self.LAT,'%f' % self.LNG)
            self.moonrise = data["rise"]
            self.moonset = data["set"]
            self.sunrise = data["rise"]
            self.sunset = data["set"]
            self.moonage = round(self.fraction*0.03386319269)) # 28 days or so
            Domoticz.Debug(s)
            s = '### Moon Local @ %s: sunrise:%s sunset:%s moonrise:%s moonset:%s' % (testDate,data["sunrise"].strftime('%Y-%m-%d %H:%M:%S'),
            data["sunset"].strftime('%Y-%m-%d %H:%M:%S'), moonTimes["rise"].strftime('%Y-%m-%d %H:%M:%S'),
            moonTimes["set"].strftime('%Y-%m-%d %H:%M:%S'))
            self.southern_hemi = (self.LAT < 0.0)
            Domoticz.Log("Moon Phase:"+str(self.phase))
            Domoticz.Log("Moon Age:"+str(self.moonage))
            self.UpdateDevice()



    def UpdateDevice(self):
        Domoticz.Debug("UpdateDevice called")
        # Make sure that the Domoticz device still exists (they can be deleted) before updating it
        datafr = ""
        lune = self.phase
        luneage = self.moonage
        phase = 1
        if 1 in Devices:
            if lune == "New Moon":
                datafr = "MoonPhases1NM"
                phase = 1
            elif lune == "Waxing Crescent":
                datafr = "MoonPhases2WC"
                phase = 2
            elif lune == "First Quarter":
                datafr = "MoonPhases3FQ"
                phase = 3
            elif lune == "Waxing Gibbous":
                datafr = "MoonPhases4WG"
                phase = 4
            elif lune == "Full":
                datafr = "MoonPhases5FM"
                phase = 5
            elif lune == "Waning Gibbous":
                datafr = "MoonPhases6WG"
                phase = 6
            elif lune == "Last Quarter":
                datafr = "MoonPhases7LQ"
                phase = 7
            elif lune == "Waning Crescent":
                datafr = "MoonPhases8WC"
                phase = 8

            if self.southern_hemi:
                datafr = '%s%s' % (datafr,self.suffix)
            titl = "1;%s" % lune
            Domoticz.Debug("Setting Custom to" + titl +  ", Icon to " + str(datafr))
            try:
               Devices[1].Update(nValue=0,  sValue=str(luneage), Options={"Custom": titl}, Image=Images[datafr].ID)
            except:
               Domoticz.Error("Failed to update device unit 1 with values %s:%s:" % (lune,luneage))

        return



global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

# Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
    return
