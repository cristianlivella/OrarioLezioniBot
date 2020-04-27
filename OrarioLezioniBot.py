import requests, re, icalendar, recurring_ical_events, json, textwrap, PIL, threading, time, os, sys
from whatsapp import WhatsApp
from datetime import datetime, timedelta, date
from dateutil.parser import parse
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
from json_to_calendar import json_to_calendar

# url del calendario: lo trovi nele impostazioni del calendario in Google Calendar, sotto la voce "Indirizzo segreto in formato iCal"
CALENDAR_URL = ""
# nome della gruppo WhatsApp
CHAT_NAME = ""

def lezioniRange(start, end):
    lezioni = []
    ical_string = requests.get(CALENDAR_URL).text
    calendar = icalendar.Calendar.from_ical(ical_string)
    events = recurring_ical_events.of(calendar).between(start, end)
    for event in events:
        name = event["SUMMARY"]
        description = event["DESCRIPTION"]
        url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', description)
        try:
            url = url[0]
        except:
            url = ""
        start = fixDateTime(str(event["DTSTART"].dt))
        end = fixDateTime(str(event["DTEND"].dt))
        evento = {"materia": name, "url": url, "inizio": start, "fine": end}
        lezioni.append(evento)
    return sorted(lezioni, key = lambda i: i['inizio'])

def utcToLocal(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset

def fixDateTime(date):
    if '+00' in date:
        date = utcToLocal(parse(date))
    else:
        date = parse(date)
    return date.strftime("%Y-%m-%d %H:%M:%S")

def getDates():
    today = date.today()
    if today.weekday() == 6:
            today = today + timedelta(days=1)
    start_date = today - timedelta(days=today.weekday())
    end_date = start_date + timedelta(days=6)
    return [(start_date.year, start_date.month, start_date.day), (end_date.year, end_date.month, end_date.day)]

def lezioniOggi():
    messaggio = "*LEZIONI DI OGGI*\n"
    today = date.today()
    tomorrow = today + timedelta(days=1)
    lezioni = lezioniRange(today, tomorrow)
    if len(lezioni) == 0:
        return "Oggi non ci sono lezioni"
    for lezione in lezioni:
        messaggio = messaggio + "*" + datetime.strptime(lezione['inizio'], '%Y-%m-%d %H:%M:%S').strftime("%H:%M") + " - " + datetime.strptime(lezione['fine'], '%Y-%m-%d %H:%M:%S').strftime("%H:%M") + "* " + lezione['materia'] + "\n"
    return messaggio

def lezioniDomani():
    messaggio = "*LEZIONI DI DOMANI*\n"
    today = date.today() + timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    lezioni = lezioniRange(today, tomorrow)
    if len(lezioni) == 0:
        return "Domani non ci saranno lezioni"
    for lezione in lezioni:
        messaggio = messaggio + "*" + datetime.strptime(lezione['inizio'], '%Y-%m-%d %H:%M:%S').strftime("%H:%M") + " - " + datetime.strptime(lezione['fine'], '%Y-%m-%d %H:%M:%S').strftime("%H:%M") + "* " + lezione['materia'] + "\n"
    return messaggio

def lezioniDopoDomani():
    messaggio = "*LEZIONI DI DOPODOMANI*\n"
    today = date.today() + timedelta(days=2)
    tomorrow = today + timedelta(days=1)
    lezioni = lezioniRange(today, tomorrow)
    if len(lezioni) == 0:
        return "Dopodomani non ci saranno lezioni"
    for lezione in lezioni:
        messaggio = messaggio + "*" + datetime.strptime(lezione['inizio'], '%Y-%m-%d %H:%M:%S').strftime("%H:%M") + " - " + datetime.strptime(lezione['fine'], '%Y-%m-%d %H:%M:%S').strftime("%H:%M") + "* " + lezione['materia'] + "\n"
    return messaggio

def handleMessage():
    global whatsapp
    oldMessage = ""
    oldMessages = whatsapp.get_last_message_for(CHAT_NAME)
    while True:
        event.clear()
        lock.acquire()
        messages = whatsapp.get_last_message_for(CHAT_NAME)
        messages.reverse()
        try:
            if messages[0] != oldMessage:
                message = messages[0]
                if message.lower() == "lezioni oggi" or message.lower() == "orario oggi":
                    sendMessage(lezioniOggi(), False)
                elif message.lower() == "lezioni domani" or message.lower() == "orario domani":
                    sendMessage(lezioniDomani(), False)
                elif message.lower() == "lezioni dopodomani" or message.lower() == "orario dopodomani":
                    sendMessage(lezioniDopoDomani(), False)
                elif message.lower() == "cambia immagine" or message.lower() == "aggiorna immagine":
                    json_to_calendar(lezioniCache)
                    changePicture(False)
                oldMessage = messages[0]
        except:
            pass
        lock.release()
        event.set()

def sendMessage(message, lockk=True):
    try:
        if lockk:
            event.wait()
            lock.acquire()
        time.sleep(1)
        whatsapp.send_message(CHAT_NAME, message)
        if lockk:
            lock.release()
    except:
        if lockk:
            lock.release()

def changePicture(lockk=True):
    try:
        if lockk:
            event.wait()
            lock.acquire()
        time.sleep(1)
        whatsapp.set_group_picture(CHAT_NAME, os.path.join(os.getcwd(), "image.png"))
        time.sleep(1)
        if lockk:
            lock.release()
    except:
        if lockk:
            lock.release()

def run():
    threading.Timer(120.0, run).start()
    global lastMateria
    global lezioniCache
    dates = getDates()
    lezioni = lezioniRange(dates[0], dates[1])
    lezioniCache = lezioni
    try:
        f = open("orario.old", "r")
    except:
        f = open("orario.old", "w")
        f.close()
        f = open("orario.old", "r")
    if (f.read() != json.dumps(lezioni)):
        f.close()
        f = open("orario.old", "w")
        f.write(json.dumps(lezioni))
        f.close()
        json_to_calendar(lezioni)
        changePicture()
    today = date.today()
    todayy = (today.year, today.month, today.day)
    tomorrow = today + timedelta(days=1)
    lezioni = lezioniRange(todayy, tomorrow)
    for lezione in lezioni:
        lezioneStart = datetime.strptime(lezione['inizio'], '%Y-%m-%d %H:%M:%S')
        now = datetime.now()
        if (lezioneStart > now and (lezioneStart-now).total_seconds() < (60*5) and lastMateria != lezione['materia']):
            lastMateria = lezione['materia']
            sendMessage("*PROSSIMA LEZIONE:*\n" + lezione['materia'] + "\n(" + datetime.strptime(lezione['inizio'], '%Y-%m-%d %H:%M:%S').strftime("%H:%M") + " - " + datetime.strptime(lezione['fine'], '%Y-%m-%d %H:%M:%S').strftime("%H:%M") + ")\n\n" + lezione['url'])

if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

lastMateria = ''
lezioniCache = []
lock = threading.Lock()
event = threading.Event()
whatsapp = WhatsApp(100, session="mysession")

thread1 = threading.Thread(target = handleMessage)
thread1.start()

run()
