import json
import random
import datetime
from datetime import timedelta
import textwrap
from PIL import Image, ImageDraw, ImageFont
import rounded_rectangle
import logging
logging.basicConfig(level=logging.DEBUG)

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
    earliest = datetime.datetime.strptime(json[0]['inizio'], date_scheme).time()
    latest = datetime.datetime.strptime(json[0]['fine'], date_scheme).time()
    for i in json:
        i_date = datetime.datetime.strptime(i['inizio'], date_scheme).time()
        if i_date < earliest:
            earliest = i_date
        i_date = datetime.datetime.strptime(i['fine'], date_scheme).time()
        if i_date > latest:
            latest = i_date
    return earliest, latest

def getEventsDays(json):
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
    font = ImageFont.truetype("fonts/Lato-Bold.ttf", 20)
    #get multiple day events
    for i in json:
        event_start = datetime.datetime.strptime(i['inizio'], date_scheme)
        event_end = datetime.datetime.strptime(i['fine'], date_scheme)
        if event_start.date() != event_end.date():
            #w, h = d.textsize(i['materia'], font=font)
            multiple_day_events.append(i)
    #remove multiple day events from other events
    for i in multiple_day_events:
        for x in json:
            if i == x:
                json.remove(x)
    return multiple_day_events

def drawCalendar(events, multiple_day_events, start, end, verbose):
    if verbose: logger.info('Drawing calendar starting from ' + str(start) + ' ending at ' + str(end))

    #Draw backgroud
    img = Image.new('RGB', (X, Y), color = (20, 20, 20))
    d = ImageDraw.Draw(img)

    COLORS = {}

    #Assign color to every event(events with same name will get same color)
    for i in events:
        color = (random.randint(0, 127), random.randint(0, 127), random.randint(0, 127))
        COLORS[i['materia']] = color
    for i in multiple_day_events:
        color = (random.randint(0, 127), random.randint(0, 127), random.randint(0, 127))
        COLORS[i['materia']] = color

    #Draw hours
    h_earliest_in, h_latest_in = getHoursRange(events)
    h_earliest = timedelta(hours = h_earliest_in.hour, minutes = h_earliest_in.minute, seconds = h_earliest_in.second)
    h_latest = timedelta(hours = h_latest_in.hour, minutes = h_latest_in.minute, seconds = h_latest_in.second)
    h_duration = h_latest- h_earliest
    h_spacing = (Y - H_SPACING['top'] - H_SPACING['bottom']) / (h_duration.seconds / 3600)
    font = ImageFont.truetype("fonts/Baloo2-Bold.ttf", 20)
    for i in range(0, h_duration.seconds // 3600 + 1):
        w, h = d.textsize(str((h_earliest + timedelta(hours = i)).seconds // 3600) + ':00', font=font)
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
        d.text((HOURS_TEXT_MARGIN['left'], i * h_spacing + H_SPACING['top'] + HOURS_TEXT_MARGIN['top']), str((h_earliest + timedelta(hours = i)).seconds // 3600) + ':00', fill=(230, 230, 230), font=font)
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
        event_posY = (event_start - h_earliest).hour + (event_start - h_earliest).minute / 60 + (event_start - h_earliest).second / 3600
        event_end_posY = (event_end - h_earliest).hour + (event_end - h_earliest).minute / 60 + (event_end - h_earliest).second / 3600
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
    events = data_calendar.copy()

    #Reset H_SPACING['top'] to default value
    H_SPACING['top'] = H_SPACING['top-original']

    temp_multiple_day_events = filterMultipleDayEvents(events)
    events_days = getEventsDays(events)

    multiple_day_events=[]

    #if data range is not specified
    if not start and not end:
        for i in temp_multiple_day_events:
            event_start = datetime.datetime.strptime(i['inizio'], date_scheme)
            event_end = datetime.datetime.strptime(i['fine'], date_scheme)
            if event_end <= events_days[len(events_days) - 1] or (event_start >= events_days[0] and event_start <= events_days[len(events_days) - 1]):
                multiple_day_events.append(i)
                H_SPACING['top'] += MULTIPLE_DAY_EVENTS_HEIGHT
        img = drawCalendar(events, multiple_day_events, events_days[0].date(), events_days[len(events_days) - 1].date(), verbose)

    #if data range is specified
    else:
        for i in temp_multiple_day_events:
            event_start = datetime.datetime.strptime(i['inizio'], date_scheme)
            event_end = datetime.datetime.strptime(i['fine'], date_scheme)
            if event_end <= end or (event_start >= start and event_start <= end):
                multiple_day_events.append(i)
                H_SPACING['top'] += MULTIPLE_DAY_EVENTS_HEIGHT
        img = drawCalendar(events, multiple_day_events, start.date(), end.date(), verbose);

    if verbose: logger.info('Saving calendar to ' + filename)
    img.save(filename)
