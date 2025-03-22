from PIL import Image
#from inky.auto import auto
from calendar_draw import Calendar
from todoist_draw import TodoistModule
import weather_draw
import datetime

def main():
    cal = Calendar()
    start_time = datetime.datetime.now().isoformat() + 'Z'
    end_time = (datetime.datetime.now() + datetime.timedelta(days=7)).isoformat() + 'Z'
    events = cal.get_events(start_time, end_time)
    cal.populate_events_dict(events)
    cal.draw_calendar()
    todo = TodoistModule()
    TodoistModule.draw_todo_tasks(todo.tasks)
    weather_draw.draw_weather()

    # Create a new blank image with the size 800x480
    final_image = Image.new('RGB', (800, 480))

    # Open the images created by cal, todo, and weather
    cal_image = Image.open("C:/Users/frizz/Documents/GitHub/Inky_calendar_pi5/calendar_image.png")
    todo_image = Image.open("C:/Users/frizz/Documents/GitHub/Inky_calendar_pi5/todoist_image.png")
    weather_image = Image.open("C:/Users/frizz/Documents/GitHub/Inky_calendar_pi5/weather_image.png")

    # Paste the images into the final image
    final_image.paste(cal_image, (0, 0))
    final_image.paste(todo_image, (400, 0))
    final_image.paste(weather_image, (400, 240))

    # Save the final image
    final_image.save("final_image.png")
    inky_display = auto(ask_user=True, verbose=True)
    image = Image.open("final_image.png")
    inky_display.set_image(image)
    inky_display.show()
    
if __name__ == "__main__":
    main()