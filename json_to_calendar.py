import json
import random
import datetime
from datetime import timedelta
import textwrap
from PIL import Image, ImageDraw, ImageFont
import rounded_rectangle

X, Y = 1000, 1000

HOURS_RECT_PADDING = {
    'top': 0,
    'bottom': 6,
    'right': 6,
    'left': 6
}

HOURS_TEXT_MARGIN = {
    'top': -15,
    'left': 30
}

DAYS_TEXT_MARGIN= {
    'top': 10,
    'left': 10
}

DAYS_TEXT_SPACING = {
    'number': 0,
    'text': -15
}

D_SPACING = {
    'top': 30,
    'bottom': 30,
    'right': 30,
    'left': 110
}
H_SPACING = {
    'top-original': 80, #same as top
    'top': 80,
    'bottom': 30,
    'right': 30,
    'left': 90
}

EVENT_PADDING = 5
TEXT_PADDING = 10
MULTIPLE_DAY_EVENTS_HEIGHT = 30

LINE_WIDTH = 3
CIRCLE_DIAMETER = 60

WEEK_DAY = ['Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab', 'Dom']

date_scheme = '%Y-%m-%d %H:%M:%S'

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
    duration = delta.seconds / 3600
    return [earliest.hour, earliest.minute], [latest.hour, latest.minute], int(duration)

def getDaysRange(json):
    r = []
    earliest = datetime.datetime.strptime(json[0]['inizio'], date_scheme)
    latest = datetime.datetime.strptime(json[len(json) - 1]['inizio'], date_scheme)
    for i in json:
        c = datetime.datetime.strptime(i['inizio'], date_scheme)
        if c < earliest:
            earliest = c
        if c > latest:
            latest = c
    duration = latest - earliest
    for i in range(0, duration.days + 1):
        r.append(earliest + timedelta(days = i))
    return r

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

def filterEvents(json, start, end):
    events = []
    for i in json:
        event_start = datetime.datetime.strptime(i['inizio'], date_scheme).date()
        event_end = datetime.datetime.strptime(i['fine'], date_scheme).date()
        if event_start >= start and event_end <= end:
            events.append(i)
    return events

def filterMultipleDayEvents(json):
    multiple_day_events = []
    temp = []
    font = ImageFont.truetype("fonts/Lato-Bold.ttf", 20)
    #get multiple day events
    for i in json:
        event_start = datetime.datetime.strptime(i['inizio'], date_scheme)
        event_end = datetime.datetime.strptime(i['fine'], date_scheme)
        r = getDaysRange(json)
        if event_start.date() != event_end.date():
            #w, h = d.textsize(i['materia'], font=font)
            temp.append(i)
    #remove multiple day events from other events
    for i in temp:
        for x in json:
            if i == x:
                json.remove(x)
    #save multiple day events present in the current calendar
    for i in temp:
        if event_end <= r[len(r) - 1] or (event_start >= r[0] and event_start <= r[len(r) - 1]):
            multiple_day_events.append(i)
            H_SPACING['top'] += MULTIPLE_DAY_EVENTS_HEIGHT
    return multiple_day_events

def drawCalendar(data, start, end, verbose):
    #Debug crap
    if verbose: print('Drawing calendar starting from ' + str(start) + ' ending at ' + str(end))

    #Draw backgroud
    img = Image.new('RGB', (X, Y), color = (20, 20, 20))
    d = ImageDraw.Draw(img)

    COLORS = {}

    #Assign color to every event(events with same name will get same color)
    for i in data:
        color = (random.randint(0, 127), random.randint(0, 127), random.randint(0, 127))
        COLORS[i['materia']] = color

    multiple_day_events = filterMultipleDayEvents(data)
    events = filterEvents(data, start, end)

    #Draw hours
    h_earliest, h_latest, h_duration = getHoursRange(events)
    h_spacing = (Y - H_SPACING['top'] - H_SPACING['bottom']) / h_duration
    font = ImageFont.truetype("fonts/Baloo2-Bold.ttf", 20)
    for i in range(0, h_duration + 1):
        w, h = d.textsize(str(h_earliest[0] + i) + ':00', font=font)
        shape = [
            (
                HOURS_TEXT_MARGIN['left'] - HOURS_RECT_PADDING['left'],
                i * h_spacing + H_SPACING['top'] - HOURS_RECT_PADDING['top'] + HOURS_TEXT_MARGIN['top']
            ),
            (
                HOURS_RECT_PADDING['right'] + HOURS_TEXT_MARGIN['left'] + w,
                i * h_spacing + H_SPACING['top'] +  HOURS_RECT_PADDING['bottom'] + HOURS_TEXT_MARGIN['top'] + h
            )
        ]
        d.rounded_rectangle(shape, 5, fill = (40, 40, 40))
        d.text((HOURS_TEXT_MARGIN['left'], i * h_spacing + H_SPACING['top'] + HOURS_TEXT_MARGIN['top']), str(h_earliest[0] + i) + ':00', fill=(230, 230, 230), font=font)
        shape = [(H_SPACING['left'], i * h_spacing + H_SPACING['top']), (X - H_SPACING['right'], i * h_spacing + H_SPACING['top'])]
        d.line(shape, fill =(30, 30, 30), width = LINE_WIDTH)

    #Draw days
    earliest, latest, d_duration = start, end, (end - start).days + 1
    d_spacing = (X - D_SPACING['right'] - D_SPACING['left']) / d_duration
    font = ImageFont.truetype("fonts/Baloo2-Bold.ttf", 30)
    for i in range(0, d_duration):
        #Draw circle
        circle_posX = d_spacing * i + (d_spacing - CIRCLE_DIAMETER) / 2
        text_center_offset = (DAYS_TEXT_SPACING['text'] - DAYS_TEXT_SPACING['number']) - 2
        d.ellipse((circle_posX + D_SPACING['left'], D_SPACING['top'] + text_center_offset, circle_posX + D_SPACING['left'] + CIRCLE_DIAMETER, D_SPACING['top'] + CIRCLE_DIAMETER + text_center_offset), fill = (40, 40, 40))
        #Draw day number
        font = ImageFont.truetype("fonts/Baloo2-Bold.ttf", 30)
        text = str((start + timedelta(days = i)).day)
        w, h = d.textsize(text, font=font)
        text_posX = d_spacing * i + (d_spacing - w) / 2
        d.text((text_posX + D_SPACING['left'], D_SPACING['top'] + DAYS_TEXT_SPACING['number']), text, fill=(230, 230, 230), font=font)
        #Draw day text
        font = ImageFont.truetype("fonts/BalooThambi2-Regular.ttf", 20)
        text = WEEK_DAY[(start + timedelta(days = i)).weekday()]
        w, h = d.textsize(text, font=font)
        text_posX = d_spacing * i + (d_spacing - w) / 2
        d.text((text_posX + D_SPACING['left'], D_SPACING['top'] + DAYS_TEXT_SPACING['text']), text, fill=(230, 230, 230), font=font)
    for i in range(0, d_duration + 1):
        shape = [(i * d_spacing + D_SPACING['left'], D_SPACING['top']), (i * d_spacing + D_SPACING['left'], Y - D_SPACING['bottom'])]
        d.line(shape, fill =(30, 30, 30), width = LINE_WIDTH)

    #Draw multiple day events
    if multiple_day_events:
        count = 0
        for i in multiple_day_events:
            event_start = datetime.datetime.strptime(i['inizio'], date_scheme).date()
            event_end = datetime.datetime.strptime(i['fine'], date_scheme).date()
            if event_end <= latest or (event_start >= earliest and event_start <= latest):
                text = i['materia']
                font = ImageFont.truetype("fonts/Lato-Bold.ttf", 20)
                w, h = d.textsize(text, font=font)
                if (event_start - earliest).days < 0:
                    event_start_posX = 0
                else:
                    event_start_posX = (event_start - earliest).days

                if (event_end - earliest).days > d_duration:
                    event_end_posX = d_duration
                else:
                    event_end_posX = (event_end - earliest).days
                shape = [
                    (
                        event_start_posX * d_spacing + D_SPACING['left'] + EVENT_PADDING,
                        H_SPACING['top-original'] + MULTIPLE_DAY_EVENTS_HEIGHT * count
                    ),
                    (
                        event_end_posX * d_spacing + D_SPACING['left'] - EVENT_PADDING,
                        H_SPACING['top-original'] + MULTIPLE_DAY_EVENTS_HEIGHT * (count + 1) - EVENT_PADDING
                    )
                ]
                d.rounded_rectangle(shape, 10, fill = COLORS[i['materia']])
                position = (
                    event_start_posX * d_spacing + D_SPACING['left'] + TEXT_PADDING + EVENT_PADDING,
                    H_SPACING['top-original'] + MULTIPLE_DAY_EVENTS_HEIGHT * count
                )
                d.text(position, text, fill=(250, 250, 250), font=font)
                count += 1

    #Draw events
    font = ImageFont.truetype("fonts/Lato-Bold.ttf", 20)
    for i in events:
        color = (random.randint(0, 127), random.randint(0, 255), random.randint(0, 255))
        event_start = datetime.datetime.strptime(i['inizio'], date_scheme)
        event_end = datetime.datetime.strptime(i['fine'], date_scheme)
        event_posX = (event_start.date() - earliest).days
        event_posY = event_start.hour - h_earliest[0]
        event_end_posY = event_end.hour - h_earliest[0]
        shape = [
            (
                event_posX * d_spacing + D_SPACING['left'] + EVENT_PADDING,
                event_posY * h_spacing + H_SPACING['top'] + EVENT_PADDING
            ),
            (
                (event_posX + 1) * d_spacing + D_SPACING['left'] - EVENT_PADDING,
                event_end_posY * h_spacing + H_SPACING['top'] - EVENT_PADDING
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
                event_posX * d_spacing + D_SPACING['left'] + EVENT_PADDING + TEXT_PADDING,
                event_posY * h_spacing + H_SPACING['top'] + EVENT_PADDING + TEXT_PADDING + y_text
            )
            d.text(position, lines[0], fill=(250, 250, 250), font=font)
            text = text[len(lines[0]) + 1:]
            y_text += height

    return img

def json_to_calendar(data_calendar, start=None, end=None, filename='image.png', verbose=False):
    #Create a copy of the original object
    data = data_calendar.copy()

    #Reset H_SPACING['top'] to default value
    H_SPACING['top'] = H_SPACING['top-original']

    #Debug crap
    if verbose: print('Saving calendar to ' + filename)

    if not start and not end:
        days_range = getDaysRange(data)
        img = drawCalendar(data, days_range[0].date(), days_range[len(days_range) - 1].date(), verbose)
    else:
        img = drawCalendar(data, start.date(), end.date(), verbose);

    if verbose: print('Saving calendar to ' + filename)
    img.save(filename)
