# OrarioLezioniBot
## LessonsTimetableBot
This Whatsapp bot automatically gets the lessons timetable from a *Google Calendar iCal*, generates an image and sets it as a Whatsapp group picture.

When there are 5 minutes left to the beginning of a lesson, it sends a reminder message with the link of the call (from Google Meet, or any other link found in the description of the event).

It replies at the commands ***lezioni oggi*** (today's lessons), ***lezioni domani*** (tomorrow's lessons) and ***lezioni dopodomani*** (lessons of the day after tomorrow), by sending the list of the lessons of the chosen day.

The bot is still under development and testing, so it may not work properly.

In addition to the dependencies contained in *requirements.txt*, [**Simple-Yet-Hackable-WhatsApp-api**](https://github.com/VISWESWARAN1998/Simple-Yet-Hackable-WhatsApp-api) and its dependencies are also required.
