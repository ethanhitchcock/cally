"""Module that controls saving data files"""

from pathlib import Path

from calcure.data import *
from calcure.calendars import convert_to_gregorian_date


class TaskSaverCSV:
    """Save tasks into CSV files"""

    def __init__(self, user_tasks, cf):
        self.user_tasks = user_tasks
        self.tasks_file = cf.TASKS_FILE
        self.use_persian_calendar = cf.USE_PERSIAN_CALENDAR

    def save(self):
        """Rewrite CSV file with changed tasks (only local tasks, exclude Notion tasks)"""
        original_file = self.tasks_file
        dummy_file = Path(f"{self.tasks_file}.bak")
        local_tasks_saved = 0
        try:
            from calcure.debug_logger import debug_logger
            debug_logger.log_event("TASK_SAVE_START", f"Saving tasks to {self.tasks_file}")
        except:
            pass
        
        with open(dummy_file, "w", encoding="utf-8") as f:
            for task in self.user_tasks.items:
                # Skip Notion tasks and header tasks - only save local tasks
                if hasattr(task, 'notion_id') and task.notion_id:
                    continue
                if hasattr(task, 'is_header') and task.is_header:
                    continue

                # If persian calendar was used, we convert event back to Gregorian for storage:
                if self.use_persian_calendar and task.year != 0:
                    year, month, day = convert_to_gregorian_date(task.year, task.month, task.day)
                else:
                    year, month, day = task.year, task.month, task.day

                dot = "."
                f.write(f'{year},{month},{day},"{dot*task.privacy}{task.name}",{task.status.name.lower()}')
                for stamp in task.timer.stamps:
                    f.write(f',{str(stamp)}')
                f.write("\n")
                local_tasks_saved += 1
                
                try:
                    from calcure.debug_logger import debug_logger
                    debug_logger.logger.debug(f"Saved task (ID: {task.item_id}): '{task.name}'")
                except:
                    pass
        
        dummy_file.replace(original_file)
        self.user_tasks.changed = False
        
        try:
            from calcure.debug_logger import debug_logger
            debug_logger.log_event("TASK_SAVE_COMPLETE", f"Saved {local_tasks_saved} local tasks to {self.tasks_file}")
        except:
            pass


class EventSaverCSV:
    """Save events into CSV files"""

    def __init__(self, user_events, cf):
        self.user_events = user_events
        self.events_file = cf.EVENTS_FILE
        self.use_persian_calendar = cf.USE_PERSIAN_CALENDAR

    def save(self):
        """Rewrite the data file with changed events"""
        original_file = self.events_file
        dummy_file = Path(f"{self.events_file}.bak")
        with open(dummy_file, "w", encoding="utf-8") as file:
            for ev in self.user_events.items:

                # If persian calendar was used, we convert event back to Gregorian for storage:
                if self.use_persian_calendar:
                    year, month, day = convert_to_gregorian_date(ev.year, ev.month, ev.day)
                else:
                    year, month, day = ev.year, ev. month, ev.day

                name = f'{"."*ev.privacy}{ev.name}'
                file.write(f'{ev.item_id},{year},{month},{day},"{name}",{ev.repetition},{ev.frequency.name.lower()},{ev.status.name.lower()}\n')
        dummy_file.replace(original_file)
        self.user_events.changed = False
