import datetime
from PIL import Image, ImageDraw, ImageFont
import calendar
import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from pprint import pprint

class Calendar:
    def __init__(self):
        self.left = 0
        self.right = 400
        self.height = 480
        self.days = 4
        self.box_height = 240
        self.box_width = 200
        self.events_dict = {}
        self.font = ImageFont.truetype("./AtkinsonHyperlegible-Regular.ttf", 24)  # Regular font
        self.small_font = ImageFont.truetype("./AtkinsonHyperlegible-Regular.ttf", 16)  #small font
        self.time_font = ImageFont.truetype("./AtkinsonHyperlegible-Regular.ttf", 12)  #time font
        self.img = Image.new('RGB', (400, 480), color='white')
        self.d = ImageDraw.Draw(self.img)
        self.colors = {
            'outline': "black",
            'days': "black",
            'today': "red",
            'background': "white",
            'internal_event': "blue",
            'external_event': "orange",
            'number': "black"  # Added 'number' color
        }
        self.load_credentials()
    
    def load_credentials(self):
        with open("./KEY.json") as f:
            data = json.load(f)
        self.cal_ids = data.get("calendar_ids", [])
        self.credentials = Credentials.from_service_account_file("./KEY.json")
        self.service = build("calendar", "v3", credentials=self.credentials)

        


    def get_events(self, start_time, end_time):
        all_events = []
        for cal_id in self.cal_ids:
            events_result = self.service.events().list(
                calendarId=cal_id, timeMin=start_time, timeMax=end_time, singleEvents=True, orderBy="startTime"
            ).execute()
            events = events_result.get("items", [])
            # Add calendar ID to each event for later identification
            for event in events:
                event['calendarId'] = cal_id
            all_events.extend(events)
        # Sort all events by start time
        all_events.sort(key=lambda x: x.get('start', {}).get('dateTime', x.get('start', {}).get('date', '')))
        return all_events


    def populate_events_dict(self, events):
        for event in events:
            start_date, end_date, time, end, location = self.extract_event_details(event)
            cal_id = event.get('calendarId', '')
            self.add_event_to_dict(start_date, [event["summary"], cal_id, time, end, location])


    def extract_event_details(self, event):
        try:
            start = event["start"]["dateTime"]
            end = event["end"]["dateTime"]
            start_date, time = start[:10], start
            end_date, end_time = end[:10], end
            location = event.get("location", "None")
        except KeyError:
            try:
                start_date = event["start"]["date"]
                end_date = event["end"]["date"]
            except KeyError:
                # Fallback if neither dateTime nor date exists
                start_date = end_date = "1900-01-01"
            time = "06:00"
            end_time = "06:30"
            location = event.get("location", "None")
        return start_date, end_date, time, end_time, location


    def add_event_to_dict(self, date, event_details):
        if date in self.events_dict:
            self.events_dict[date].append(event_details)
        else:
            self.events_dict[date] = [event_details]

    def draw_cal_grid(self):
        self.d.rectangle([(0, 0), (self.right, self.height)], fill=self.colors['background'],outline=self.colors['outline'],width=2)

        self.d.rectangle([(0, 25), (self.right/2, self.box_height)], fill=self.colors['background'],outline=self.colors['outline'],width=2)
        self.d.rectangle([(self.right/2, 25), (self.right, self.box_height)], fill=self.colors['background'],outline=self.colors['outline'],width=2)
        self.d.rectangle([(0, self.box_height), (self.right/2, self.height)], fill=self.colors['background'],outline=self.colors['outline'],width=2)
        self.d.rectangle([(self.right/2, self.box_height), (self.right, self.height)], fill=self.colors['background'],outline=self.colors['outline'],width=2)
        now = datetime.datetime.now()
        year = now.year
        month = now.month

        text = calendar.month_name[month] + " " + str(now.day) + " " + str(year)
        topdate = self.d.textbbox((0, 0), text, font=self.font)
        text_width = topdate[2] - topdate[0]
        x = (self.right - text_width) / 2
        self.d.text((x, 0), text, font=self.font, fill=self.colors['number'])

        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        today = datetime.datetime.now().date()
        i = 0
        total = 0
        while total < 4:
            current_date = today + datetime.timedelta(days=i)
            date_str = current_date.strftime("%Y-%m-%d")
            print(i,total)
            if date_str in self.events_dict:
                current_weekday = current_date.weekday()
                x = 20 if total % 2 == 0 else 220
                y = 25 if total < 2 else 245
                if(current_date == today):
                    self.d.text((x, y), weekdays[current_weekday], font=self.small_font, fill=self.colors['today'])
                    self.d.text((x + 125, y - 3), str(current_date.day), font=self.font, fill=self.colors['today'])
                else:
                    self.d.text((x, y), weekdays[current_weekday], font=self.small_font, fill=self.colors['days'])
                    self.d.text((x + 125, y - 3), str(current_date.day), font=self.font, fill=self.colors['number'])
                total += 1
            i += 1

    def draw_month_events(self):
        today = datetime.datetime.now().date()
        total = 0
        i = 0
        while total < 4:
            current_date = today + datetime.timedelta(days=i)
            date_str = current_date.strftime("%Y-%m-%d")
            
            if date_str in self.events_dict:
                events = self.events_dict[date_str]
                
                for j, event in enumerate(events):
                    if len(event[0]) > 20:
                        event[0] = event[0][:20]
                    if len(event[4]) > 30:
                        event[4] = event[4][:29] + ".."

                    if self.cal_ids and self.cal_ids[0] in event[1]:
                        text_colour = self.colors['internal_event']
                    else:
                        text_colour = self.colors['external_event']
                    
                    x = 20 if total % 2 == 0 else 220
                    y = 45 + (total // 2) * 220 + j * 40
                    
                    self.d.text((x, y), event[0], font=self.small_font, fill=text_colour)
                    start_time = datetime.datetime.strptime(event[2][11:16], "%H:%M").strftime("%I:%M %p")  # Convert to 12-hour format and remove leading zero
                    end_time = datetime.datetime.strptime(event[3][11:16], "%H:%M").strftime("%I:%M %p")  # Convert to 12-hour format and remove leading zero
                    if(start_time[0] == "0"):
                        start_time = start_time[1:]
                    if(end_time[0] == "0"):
                        end_time = end_time[1:]
                    event_time = start_time + " - " + end_time
                    self.d.text((x, y+15), event_time, font=self.time_font, fill='black')
                    self.d.text((x,y+25),event[4],font=self.time_font,fill='black')
                    
                total += 1
            i += 1

    def save_image(self):
        self.img.save("./calendar_image.png")

    def draw_calendar(self):
        self.draw_cal_grid()
        self.draw_month_events()
        self.save_image()

if __name__ == "__main__":
    calimg = Calendar()
    start_time = datetime.datetime.now().isoformat() + 'Z'
    end_time = (datetime.datetime.now() + datetime.timedelta(days=7)).isoformat() + 'Z'
    events = calimg.get_events(start_time, end_time)
    calimg.populate_events_dict(events)
    calimg.draw_calendar()