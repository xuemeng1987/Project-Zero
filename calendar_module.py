import datetime
from discord.ext import tasks

class CalendarEvent:
    def __init__(self, event_name, event_date_time, user_id, description="", reminder_time=None, repeat=None):
        self.event_name = event_name
        self.event_date_time = event_date_time
        self.user_id = user_id
        self.description = description
        self.reminder_time = reminder_time
        self.repeat = repeat

# 儲存所有事件的列表
event_list = []

@tasks.loop(seconds=60)
async def check_events(bot):
    current_time = datetime.datetime.now()
    for event in event_list:
        # 檢查是否需要發送提醒
        if event.event_date_time - datetime.timedelta(minutes=event.reminder_time) <= current_time:
            user = bot.get_user(event.user_id)
            if user:
                await user.send(f"提醒：您的事件 `{event.event_name}` 即將開始！")
            if event.repeat:
                # 如果事件設置了重複，則將事件時間延後
                event.event_date_time += event.repeat

def add_event(event):
    event_list.append(event)

def remove_event(event_name, user_id):
    global event_list
    event_list = [event for event in event_list if not (event.event_name == event_name and event.user_id == user_id)]

def get_user_events(user_id):
    return [event for event in event_list if event.user_id == user_id]
