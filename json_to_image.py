import json
import random
import datetime
import textwrap
from PIL import Image, ImageDraw, ImageFont
import rounded_rectangle

X, Y = 1000, 1000
D_SPACING = {
    'top': 30,
    'bottom': 30,
    'right': 30,
    'left': 120
}
H_SPACING = {
    'top': 80,
    'bottom': -30,
    'right': 20,
    'left': 20
}

D_LINE_OFFSET = - 10
H_LINE_OFFSET = 30

EVENT_PADDING = 5
TEXT_PADDING = 10

LINE_WIDTH = 2

date_scheme = '%Y-%m-%d %H:%M:%S%z'

input = '[{"materia": "Matematica", "url": "https://join.skype.com/jrRYOumb900g", "inizio": "2020-03-23 10:00:00+01:00", "fine": "2020-03-23 11:00:00+01:00"}, {"materia": "Italiano", "url": "", "inizio": "2020-03-23 11:00:00+01:00", "fine": "2020-03-23 12:00:00+01:00"}, {"materia": "Storia", "url": "", "inizio": "2020-03-23 12:00:00+01:00", "fine": "2020-03-23 13:00:00+01:00"}, {"materia": "Italiano", "url": "", "inizio": "2020-03-24 09:00:00+01:00", "fine": "2020-03-24 10:00:00+01:00"}, {"materia": "Sistemi e reti / GeP", "url": "http://bit.ly/5id2020sergep", "inizio": "2020-03-24 10:00:00+01:00", "fine": "2020-03-24 11:00:00+01:00"}, {"materia": "Matematica", "url": "https://join.skype.com/jrRYOumb900g", "inizio": "2020-03-24 14:00:00+01:00", "fine": "2020-03-24 15:00:00+01:00"}, {"materia": "Inglese", "url": "https://join.skype.com/mxlS2v4rhGc5", "inizio": "2020-03-25 09:00:00+01:00", "fine": "2020-03-25 10:00:00+01:00"}, {"materia": "Informatica", "url": "https://meet.google.com/ubo-mtwc-aiz", "inizio": "2020-03-25 10:00:00+01:00", "fine": "2020-03-25 11:00:00+01:00"}, {"materia": "Informatica laboratorio", "url": "https://meet.google.com/mno-cjfp-zif", "inizio": "2020-03-25 11:00:00+01:00", "fine": "2020-03-25 12:00:00+01:00"}, {"materia": "Sistemi e reti / GeP", "url": "http://bit.ly/5id2020sergep", "inizio": "2020-03-25 12:00:00+01:00", "fine": "2020-03-25 13:00:00+01:00"}, {"materia": "Informatica", "url": "https://meet.google.com/ubo-mtwc-aiz", "inizio": "2020-03-26 09:00:00+01:00", "fine": "2020-03-26 10:00:00+01:00"}, {"materia": "Matematica", "url": "https://join.skype.com/jrRYOumb900g", "inizio": "2020-03-26 10:00:00+01:00", "fine": "2020-03-26 11:00:00+01:00"}, {"materia": "Sistemi e reti / GeP", "url": "http://bit.ly/5id2020sergep", "inizio": "2020-03-27 09:00:00+01:00", "fine": "2020-03-27 10:00:00+01:00"}, {"materia": "Italiano", "url": "", "inizio": "2020-03-27 10:00:00+01:00", "fine": "2020-03-27 11:00:00+01:00"}, {"materia": "Storia", "url": "", "inizio": "2020-03-27 11:00:00+01:00", "fine": "2020-03-27 12:00:00+01:00"}, {"materia": "TPS", "url": "https://meet.google.com/gum-uizr-idn", "inizio": "2020-03-27 12:00:00+01:00", "fine": "2020-03-27 13:00:00+01:00"}, {"materia": "Informatica", "url": "https://meet.google.com/ubo-mtwc-aiz", "inizio": "2020-03-28 09:00:00+01:00", "fine": "2020-03-28 10:00:00+01:00"}, {"materia": "TPS laboratorio", "url": "https://meet.google.com/bio-kbsc-anr", "inizio": "2020-03-28 10:00:00+01:00", "fine": "2020-03-28 15:00:00+01:00"}]'

data = json.loads(input)

COLORS = {}

for i in data:
    color = (random.randint(0, 127), random.randint(0, 127), random.randint(0, 127))
    COLORS[i['materia']] = color

def getHoursRange(json):
    earliest = datetime.datetime.strptime(json[0]['inizio'], date_scheme)
    latest = datetime.datetime.strptime(json[0]['fine'], date_scheme)
    for i in json:
        i_date = datetime.datetime.strptime(i['inizio'], date_scheme)
        if i_date.hour < earliest.hour:
            earliest = i_date
        elif i_date.hour == earliest.hour and i_date.minute < earliest.minute:
            earliest = i_date
        i_date = datetime.datetime.strptime(i['fine'], date_scheme)
        if i_date.hour > latest.hour:
            latest = i_date
        elif i_date.hour == latest.hour and i_date.minute > latest.minute:
            latest = i_date
    delta = latest - earliest
    duration = delta.seconds / 3600 + 1
    return [earliest.hour, earliest.minute], [latest.hour, latest.minute], int(duration)

def getDaysRange(json):
    earliest = datetime.datetime.strptime(json[0]['inizio'], date_scheme).day
    latest = datetime.datetime.strptime(json[len(json) - 1]['inizio'], date_scheme).day
    for i in json:
        day = datetime.datetime.strptime(i['inizio'], date_scheme).day
        if day < earliest:
            earliest = day
        if day > latest:
            latest = day
    duration = latest - earliest + 1
    return earliest, latest, duration

def getOptimalTextWidth(text, font, Y):
    i = 1
    last_width = 0
    width = 1
    while(width < Y and last_width != width):
        lines = textwrap.wrap(text, width=i)
        last_width = width
        width, height = font.getsize(lines[0])
        i += 1
    return i

#Draw backgroud
img = Image.new('RGB', (X, Y), color = (20, 20, 20))
d = ImageDraw.Draw(img)

#Draw hours
h_earliest, h_latest, h_duration = getHoursRange(data)
h_spacing = (Y - H_SPACING['top'] - H_SPACING['bottom']) / h_duration
font = ImageFont.truetype("arial.ttf", 20)
for i in range(0, h_duration):
    d.text((H_SPACING['left'], i * h_spacing + H_SPACING['top']), str(h_earliest[0] + i) + ':00', fill=(250, 250, 250), font=font)
    shape = [(H_SPACING['left'], i * h_spacing + H_SPACING['top'] + H_LINE_OFFSET), (X - H_SPACING['right'], i * h_spacing + H_SPACING['top'] + H_LINE_OFFSET)]
    d.line(shape, fill =(30, 30, 30), width = LINE_WIDTH)

#Draw days
d_earliest, d_latest, d_duration = getDaysRange(data)
d_spacing = (X - D_SPACING['right'] - D_SPACING['left']) / d_duration
font = ImageFont.truetype("arial.ttf", 30)
for i in range(0, d_duration):
    d.text((i * d_spacing + D_SPACING['left'], D_SPACING['top']), str(d_earliest + i), fill=(250, 250, 250), font=font)
for i in range(0, d_duration + 1):
    shape = [(i * d_spacing + D_SPACING['left'] + D_LINE_OFFSET, D_SPACING['top']), (i * d_spacing + D_SPACING['left'] + D_LINE_OFFSET, Y - D_SPACING['bottom'])]
    d.line(shape, fill =(30, 30, 30), width = LINE_WIDTH)

#Draw events
font = ImageFont.truetype("arialbd.ttf", 20)
for i in data:
    color = (random.randint(0, 127), random.randint(0, 255), random.randint(0, 255))
    start = datetime.datetime.strptime(i['inizio'], date_scheme)
    finish = datetime.datetime.strptime(i['fine'], date_scheme)
    event_posX = start.day - d_earliest
    event_posY = start.hour - h_earliest[0]
    event_end_posY = finish.hour - h_earliest[0]
    shape = [
        (
            event_posX * d_spacing + D_SPACING['left'] + EVENT_PADDING + D_LINE_OFFSET,
            event_posY * h_spacing + H_SPACING['top'] + EVENT_PADDING + H_LINE_OFFSET
        ),
        (
            (event_posX + 1) * d_spacing + D_SPACING['left'] - EVENT_PADDING + D_LINE_OFFSET,
            event_end_posY * h_spacing + H_SPACING['top'] - EVENT_PADDING + H_LINE_OFFSET
        )
    ]
    d.rounded_rectangle(shape, 10, fill = COLORS[i['materia']])

    text = i['materia']
    y_text = 0
    while(len(text) > 0):
        wd = getOptimalTextWidth(text, font, d_spacing - EVENT_PADDING * 2 - TEXT_PADDING)
        lines = textwrap.wrap(text, width=wd)
        width, height = font.getsize(lines[0])
        position = (
            event_posX * d_spacing + D_SPACING['left'] + EVENT_PADDING + D_LINE_OFFSET + TEXT_PADDING,
            event_posY * h_spacing + H_SPACING['top'] + EVENT_PADDING + H_LINE_OFFSET + TEXT_PADDING + y_text
        )
        d.text(position, lines[0], fill=(250, 250, 250), font=font)
        text = text[len(lines[0]) + 1:]
        y_text += height

img.save('image.png')
