from todoist_api_python.api import TodoistAPI
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

api = TodoistAPI("")

class TodoTask:
    def __init__(self, text, subtext,description):
        self.text = text
        self.subtext = subtext
        self.description = description

class TodoistModule:
    def __init__(self):
        self.tasks = self.get_todo_tasks(datetime.now())

    def get_subtext(self, task, day: datetime):
        if task.due is None:
            return "No Due Date"
        
        if task.due.datetime:
            try:
                dt = datetime.fromisoformat(task.due.datetime.replace("Z", "+00:00"))
            except ValueError:
                raise ValueError("Invalid datetime format")
        else:
            dt = datetime.strptime(task.due.date, "%Y-%m-%d")
        
        dt = dt.astimezone()
        day = day.astimezone()
        
        month_day = dt.strftime("%b %d %I:%M %p")
        day_of_week = dt.strftime("%A")
        
        if day > dt:
            return f"{month_day} · Overdue"
        elif (dt - day).days == 1:
            return f"{month_day} · {day_of_week} · Today"
        elif (dt - day).days == 2:
            return f"{month_day} · {day_of_week} · Tomorrow"
        else:
            return f"{month_day} · {day_of_week}"
        
    def get_todo_tasks(self, day: datetime):
        tasks = api.get_tasks()
        items = []
        
        for task in tasks[:7]:
            items.append(TodoTask(task.content, self.get_subtext(task, day),task.description))
        return items

    def draw_todo_tasks(tasks):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        img = Image.new('RGB', (400, 240), color='white')
        d = ImageDraw.Draw(img)
        font_task = ImageFont.truetype(os.path.join(script_dir, "AtkinsonHyperlegible-Regular.ttf"), 12)
        font_title = ImageFont.truetype(os.path.join(script_dir, "AtkinsonHyperlegible-Regular.ttf"), 14)
        font_header = ImageFont.truetype(os.path.join(script_dir, "AtkinsonHyperlegible-Regular.ttf"), 20)
        
        d.text((10, 10), "Todoist Tasks", font=font_header, fill='black')
        d.rectangle([(0,0), (400, 240)], outline='black',width=2)

        for i, task in enumerate(tasks):
            d.ellipse([(5, 50 + i * 45), (15, 60 + i * 45)], fill='black')
            d.text((20, 45 + i * 45), task.text, font=font_title, fill='black')
            d.text((20, 60 + i * 45), task.subtext, font=font_task, fill='black')
            d.text((20, 75 + i * 45), task.description, font=font_task, fill='black')
        
        image_path = os.path.join(script_dir, 'todoist_image.png')
        img.save(image_path)

if __name__ == "__main__":
    day = datetime.now()
    todo = TodoistModule()
    TodoistModule.draw_todo_tasks(todo.tasks)
