from PIL import Image
#from inky.auto import auto
from calendar_draw import Calendar
from todoist_draw import TodoistModule
import weather_draw
import datetime
import os

Inky_palette =[
    (0,0,0), # black
    (255,255,255), # white
    (255,0,0), # red
    (0,255,0), # green
    (0,0,255), # blue
    (255,255,0), # yellow
    (255,140,0) # orange
]

palette_image = Image.new('P', (1, 1))
flat_palette =[c for color in Inky_palette for c in color] + [0] * (256 * 3 - len(Inky_palette) * 3)
palette_image.putpalette(flat_palette)


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
    cal_image = Image.open("./calendar_image.png")
    todo_image = Image.open("./todoist_image.png")
    weather_image = Image.open("./weather_image.png")

    # Paste the images into the final image
    final_image.paste(cal_image, (0, 0))
    final_image.paste(todo_image, (400, 0))
    final_image.paste(weather_image, (400, 240))

    final_inkcolor = final_image.quantize(palette=palette_image, dither=Image.Dither.FLOYDSTEINBERG)

    # Save the final image
    final_inkcolor.save("final_image.png")
    
    inky_display = auto(ask_user=True, verbose=True)
    image = Image.open("final_image.png")
    inky_display.set_image(image)
    inky_display.show()
    
if __name__ == "__main__":
    main()