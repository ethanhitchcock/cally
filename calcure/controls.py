"""This module contains functions that react to user input on each screen"""

import curses
import importlib
import logging

# Modules:
from calcure.data import *
from calcure.dialogues import *
from calcure.configuration import Config

cf = Config()

# Language:
if cf.LANG == "fr":
    from calcure.translations.fr import *
elif cf.LANG == "ru":
    from calcure.translations.ru import *
elif cf.LANG == "it":
    from calcure.translations.it import *
elif cf.LANG == "br":
    from calcure.translations.br import *
elif cf.LANG == "tr":
    from calcure.translations.tr import *
elif cf.LANG == "zh":
    from calcure.translations.zh import *
elif cf.LANG == "tw":
    from calcure.translations.tw import *
elif cf.LANG == "sk":
    from calcure.translations.sk import *
elif cf.LANG == "es":
    from calcure.translations.es import *
else:
    from calcure.translations.en import *


def safe_run(func):
    """Decorator preventing crashes on keyboard interruption and no input"""

    def inner(stdscr, screen, *args, **kwargs):
        try:
            func(stdscr, screen, *args, **kwargs)

        # Handle keyboard interruption with ctrl+c:
        except KeyboardInterrupt:
            confirmed = ask_confirmation(stdscr, MSG_EXIT, cf.ASK_CONFIRMATION_TO_QUIT)
            screen.state = AppState.EXIT if confirmed else screen.state

        # Prevent crash if no input:
        except curses.error:
            pass
    return inner


@safe_run
def control_monthly_screen(stdscr, screen, user_events, importer):
    """Handle user input on the monthly screen"""

    # If we previously entered the selection mode, now we perform the action:
    if screen.selection_mode:
        screen.selection_mode = False

        # Change event status:
        if screen.key in ['i', 'h']:
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_HIGH)
            if user_events.filter_events_that_month(screen).is_valid_number(number):
                event_id = user_events.filter_events_that_month(screen).items[number].item_id
                user_events.toggle_item_status(event_id, Status.IMPORTANT)
        if screen.key == 'l':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_LOW)
            if user_events.filter_events_that_month(screen).is_valid_number(number):
                event_id = user_events.filter_events_that_month(screen).items[number].item_id
                user_events.toggle_item_status(event_id, Status.UNIMPORTANT)
        if screen.key == 'u':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_RESET)
            if user_events.filter_events_that_month(screen).is_valid_number(number):
                event_id = user_events.filter_events_that_month(screen).items[number].item_id
                user_events.toggle_item_status(event_id, Status.NORMAL)
        if screen.key == 'd':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_DONE)
            if user_events.filter_events_that_month(screen).is_valid_number(number):
                event_id = user_events.filter_events_that_month(screen).items[number].item_id
                user_events.toggle_item_status(event_id, Status.DONE)

        # Toggle event privacy:
        if screen.key == '.':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_PRIVACY)
            if user_events.filter_events_that_month(screen).is_valid_number(number):
                event_id = user_events.filter_events_that_month(screen).items[number].item_id
                user_events.toggle_item_privacy(event_id)

        # Delete event:
        if screen.key == 'x':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_DEL)
            if user_events.filter_events_that_month(screen).is_valid_number(number):
                event_id = user_events.filter_events_that_month(screen).items[number].item_id
                user_events.delete_item(event_id)

        # Rename event:
        if screen.key in ['e', 'r']:
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_REN)
            if user_events.filter_events_that_month(screen).is_valid_number(number):
                event_id = user_events.filter_events_that_month(screen).items[number].item_id
                clear_line(stdscr, screen.y_max-2)
                new_name = input_string(stdscr, screen.y_max-2, 0, MSG_NEW_TITLE, screen.x_max-len(MSG_NEW_TITLE)-2)
                user_events.rename_item(event_id, new_name)

        # Move event:
        if screen.key in ['m', 'M']:
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_MV)
            if user_events.filter_events_that_month(screen).is_valid_number(number):
                event_id = user_events.filter_events_that_month(screen).items[number].item_id
                clear_line(stdscr, screen.y_max-2)
                if screen.key == 'm':
                    year, month, day = input_date(stdscr, screen.y_max-2, 0, MSG_EVENT_MV_TO)
                    if screen.is_valid_date(year, month, day):
                        user_events.change_date(event_id, year, month, day)

                if screen.key == 'M':
                    question = f'{MSG_EVENT_MV_TO_D} {screen.year}/{screen.month}/'
                    day = input_day(stdscr, screen.y_max-2, 0, question)
                    if screen.is_valid_day(day):
                        user_events.change_day(event_id, day)

    # Otherwise, we check for user input:
    else:
        # Key should already be set by main loop for unified workflow
        # Don't read key again - use the one already set
        if screen.key is None:
            return  # No key available, skip processing

        # If we need to select an event, change to selection mode:
        selection_keys = ['h', 'l', 'u', 'i', 'd', 'x', 'e', 'r', 'c', 'm', 'M', '.']
        if screen.key in selection_keys and user_events.filter_events_that_month(screen).items:
            screen.selection_mode = True

        # Navigation:
        if screen.key in ["n", "j", "KEY_DOWN", "KEY_RIGHT"]:
            screen.next_month()
        if screen.key in ["p", "k", "KEY_UP", "KEY_LEFT"]:
            screen.previous_month()
        if screen.key in ["KEY_HOME", "R"]:
            screen.reset_to_today()

        # Handle "g" and "G" as go to selected day:
        if screen.key == "g":
            clear_line(stdscr, screen.y_max-2, 0)
            year, month, day = input_date(stdscr, screen.y_max-2, 0, MSG_GOTO)
            if screen.is_valid_date(year, month, day):
                screen.day = day
                screen.month = month
                screen.year = year
                screen.calendar_state = CalState.DAILY

        if screen.key == "G":
            clear_line(stdscr, screen.y_max-2, 0)
            question = f"{MSG_GOTO_D} {screen.year}/{screen.month}/"
            day = input_day(stdscr, screen.y_max-2, 0, question)
            if screen.is_valid_date(screen.year, screen.month, day):
                screen.day = day
                screen.calendar_state = CalState.DAILY

        # Change the view to daily:
        if screen.key == "v":
            screen.day = 1
            screen.calendar_state = CalState.DAILY

        # Add single event (unified workflow: a = add event):
        if screen.key == "a":
            # Step 1: Ask for date
            clear_line(stdscr, screen.y_max-2, 0)
            year, month, day = input_date(stdscr, screen.y_max-2, 0, MSG_EVENT_DATE)
            if not screen.is_valid_date(year, month, day):
                # If invalid, use current screen date
                year, month, day = screen.year, screen.month, screen.day
            
            # Step 2: Ask for title
            clear_line(stdscr, screen.y_max-2, 0)
            name = input_string(stdscr, screen.y_max-2, 0, MSG_EVENT_TITLE, screen.x_max-len(MSG_EVENT_TITLE)-2)
            if name:
                # Step 3: Ask for start time (Enter = all-day event)
                clear_line(stdscr, screen.y_max-2, 0)
                start_time_str = input_string(stdscr, screen.y_max-2, 0, "Start time (HH:MM or Enter for all-day): ", 6)
                hour, minute = None, None
                end_hour, end_minute = None, None
                
                if start_time_str and ":" in start_time_str:
                    try:
                        parts = start_time_str.split(":")
                        hour = int(parts[0])
                        minute = int(parts[1]) if len(parts) > 1 else 0
                        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                            hour, minute = None, None
                        else:
                            # Step 4: Ask for end time (Enter = default to 1 hour duration)
                            clear_line(stdscr, screen.y_max-2, 0)
                            end_time_str = input_string(stdscr, screen.y_max-2, 0, "End time (HH:MM or Enter for 1 hour): ", 6)
                            if end_time_str and ":" in end_time_str:
                                try:
                                    end_parts = end_time_str.split(":")
                                    end_hour = int(end_parts[0])
                                    end_minute = int(end_parts[1]) if len(end_parts) > 1 else 0
                                    if end_hour < 0 or end_hour > 23 or end_minute < 0 or end_minute > 59:
                                        end_hour, end_minute = None, None
                                except ValueError:
                                    end_hour, end_minute = None, None
                            else:
                                # Default to 1 hour duration
                                end_hour = (hour + 1) % 24
                                end_minute = minute
                    except ValueError:
                        hour, minute = None, None
                
                event_id = user_events.items[-1].item_id + 1 if not user_events.is_empty() else 1
                # Status is imported from calcure.data import * at top of file
                user_events.add_item(UserEvent(event_id, year, month, day, name, 1, Frequency.ONCE, Status.NORMAL, False, hour=hour, minute=minute, end_hour=end_hour, end_minute=end_minute))
                screen.refresh_now = True

        # Add a recurring event:
        if screen.key == "A":
            question = f'{MSG_EVENT_DATE}{screen.year}/{screen.month}/'
            day = input_day(stdscr, screen.y_max-2, 0, question)
            if screen.is_valid_day(day):
                clear_line(stdscr, screen.y_max-2)
                name = input_string(stdscr, screen.y_max-2, 0, MSG_EVENT_TITLE, screen.x_max-len(MSG_EVENT_TITLE)-2)
                item_id = user_events.items[-1].item_id + 1 if not user_events.is_empty() else 1
                reps = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_REP)
                freq = input_frequency(stdscr, screen.y_max-2, 0, MSG_EVENT_FR)
                if reps is not None and freq is not None:
                    reps = 1 if reps == 0 else reps
                    user_events.add_item(UserEvent(item_id, screen.year, screen.month, day, name, reps+1, freq, Status.NORMAL, False))

        # Reload:
        if screen.key in ["Q"]:
            screen.reload_data = True
            screen.refresh_now = True

        # Imports:
        if screen.key == "C":
            confirmed = ask_confirmation(stdscr, MSG_EVENT_IMP, cf.ASK_CONFIRMATIONS)
            if confirmed:
                importer.import_events_from_calcurse()
                screen.refresh_now = True

        # Other actions:
        if vim_style_exit(stdscr, screen):
            confirmed = ask_confirmation(stdscr, MSG_EXIT, cf.ASK_CONFIRMATION_TO_QUIT)
            screen.state = AppState.EXIT if confirmed else screen.state
        if screen.key == "*":
            screen.privacy = not screen.privacy
        # Removed Space keybinding - no state switching in unified workflow
        if screen.key == "?":
            screen.state = AppState.HELP
        if screen.key == "q":
            confirmed = ask_confirmation(stdscr, MSG_EXIT, cf.ASK_CONFIRMATION_TO_QUIT)
            screen.state = AppState.EXIT if confirmed else screen.state
        # Removed / keybinding - split screen always on in unified workflow
        
        # Unified keybinding: t = create task (handled in control_journal_screen)
        # Don't handle here to avoid conflicts
        
        if screen.key == "w":
            # Toggle between monthly and weekly
            if screen.calendar_state == CalState.MONTHLY:
                screen.calendar_state = CalState.WEEKLY
            else:
                screen.calendar_state = CalState.MONTHLY
            screen.refresh_now = True
        if screen.key == "W":
            screen.show_week_numbers = not screen.show_week_numbers
            screen.refresh_now = True


@safe_run
def control_daily_screen(stdscr, screen, user_events, importer):
    """Handle user input on the daily screen"""
    # Key should already be set by main loop for unified workflow
    # Don't read key again - use the one already set
    if screen.key is None:
        return  # No key available, skip processing
    
    # If we previously entered the selection mode, now we perform the action:
    if screen.selection_mode:
        screen.selection_mode = False

        # Change event status:
        if screen.key in ['i', 'h']:
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_HIGH)
            if user_events.filter_events_that_day(screen).is_valid_number(number):
                item_id = user_events.filter_events_that_day(screen).items[number].item_id
                user_events.toggle_item_status(item_id, Status.IMPORTANT)
        if screen.key == 'l':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_LOW)
            if user_events.filter_events_that_day(screen).is_valid_number(number):
                item_id = user_events.filter_events_that_day(screen).items[number].item_id
                user_events.toggle_item_status(item_id, Status.UNIMPORTANT)
        if screen.key == 'u':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_RESET)
            if user_events.filter_events_that_day(screen).is_valid_number(number):
                item_id = user_events.filter_events_that_day(screen).items[number].item_id
                user_events.toggle_item_status(item_id, Status.NORMAL)
        if screen.key == 'd':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_DONE)
            if user_events.filter_events_that_day(screen).is_valid_number(number):
                item_id = user_events.filter_events_that_day(screen).items[number].item_id
                user_events.toggle_item_status(item_id, Status.DONE)

        # Toggle event privacy:
        if screen.key == '.':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_PRIVACY)
            if user_events.filter_events_that_day(screen).is_valid_number(number):
                event_id = user_events.filter_events_that_day(screen).items[number].item_id
                user_events.toggle_item_privacy(event_id)

        # Delete event:
        if screen.key in ['x']:
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_DEL)
            if user_events.filter_events_that_day(screen).is_valid_number(number):
                item_id = user_events.filter_events_that_day(screen).items[number].item_id
                user_events.delete_item(item_id)

        # Rename event:
        if screen.key in ['e', 'r']:
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_REN)
            if user_events.filter_events_that_day(screen).is_valid_number(number):
                item_id = user_events.filter_events_that_day(screen).items[number].item_id
                clear_line(stdscr, screen.y_max-2)
                new_name = input_string(stdscr, screen.y_max-2, 0, MSG_NEW_TITLE, screen.x_max-len(MSG_NEW_TITLE)-2)
                user_events.rename_item(item_id, new_name)

        # Move event:
        if screen.key in ['m', 'M']:
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_MV)
            if user_events.filter_events_that_day(screen).is_valid_number(number):
                item_id = user_events.filter_events_that_day(screen).items[number].item_id
                clear_line(stdscr, screen.y_max-2)
                if screen.key == 'm':
                    year, month, day = input_date(stdscr, screen.y_max-2, 0, MSG_EVENT_MV_TO)
                    if screen.is_valid_date(year, month, day):
                        user_events.change_date(event_id, year, month, day)

                if screen.key == 'M':
                    question = f'{MSG_EVENT_MV_TO_D}{screen.year}/{screen.month}/'
                    day = input_day(stdscr, screen.y_max-2, 0, question)
                    if screen.is_valid_day(day):
                        user_events.change_day(event_id, day)

    # Otherwise, we check for user input:
    else:
        # Wait for user to press a key:
        screen.key = stdscr.getkey()

        # If we need to select an event, change to selection mode:
        selection_keys = ['h', 'l', 'u', 'i', 'd', 'x', 'e', 'r', 'c', 'm', 'M', '.']
        if screen.key in selection_keys and user_events.filter_events_that_day(screen).items:
            screen.selection_mode = True

        # Navigation:
        if screen.key in ["n", "j", "KEY_UP", "KEY_RIGHT"]:
            screen.next_day()
        if screen.key in ["p", "k", "KEY_DOWN", "KEY_LEFT"]:
            screen.previous_day()
        if screen.key in ["KEY_HOME", "R"]:
            screen.reset_to_today()

        # Add single event (unified workflow: a = add event):
        if screen.key == "a":
            # Step 1: Ask for date
            clear_line(stdscr, screen.y_max-2, 0)
            year, month, day = input_date(stdscr, screen.y_max-2, 0, MSG_EVENT_DATE)
            if not screen.is_valid_date(year, month, day):
                # If invalid, use current screen date
                year, month, day = screen.year, screen.month, screen.day
            
            # Step 2: Ask for title
            clear_line(stdscr, screen.y_max-2, 0)
            name = input_string(stdscr, screen.y_max-2, 0, MSG_EVENT_TITLE, screen.x_max-len(MSG_EVENT_TITLE)-2)
            if name:
                # Step 3: Ask for start time (Enter = all-day event)
                clear_line(stdscr, screen.y_max-2, 0)
                start_time_str = input_string(stdscr, screen.y_max-2, 0, "Start time (HH:MM or Enter for all-day): ", 6)
                hour, minute = None, None
                end_hour, end_minute = None, None
                
                if start_time_str and ":" in start_time_str:
                    try:
                        parts = start_time_str.split(":")
                        hour = int(parts[0])
                        minute = int(parts[1]) if len(parts) > 1 else 0
                        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                            hour, minute = None, None
                        else:
                            # Step 4: Ask for end time (Enter = default to 1 hour duration)
                            clear_line(stdscr, screen.y_max-2, 0)
                            end_time_str = input_string(stdscr, screen.y_max-2, 0, "End time (HH:MM or Enter for 1 hour): ", 6)
                            if end_time_str and ":" in end_time_str:
                                try:
                                    end_parts = end_time_str.split(":")
                                    end_hour = int(end_parts[0])
                                    end_minute = int(end_parts[1]) if len(end_parts) > 1 else 0
                                    if end_hour < 0 or end_hour > 23 or end_minute < 0 or end_minute > 59:
                                        end_hour, end_minute = None, None
                                except ValueError:
                                    end_hour, end_minute = None, None
                            else:
                                # Default to 1 hour duration
                                end_hour = (hour + 1) % 24
                                end_minute = minute
                    except ValueError:
                        hour, minute = None, None
                
                item_id = user_events.items[-1].item_id + 1 if not user_events.is_empty() else 1
                user_events.add_item(UserEvent(item_id, year, month, day, name, 1, Frequency.ONCE, Status.NORMAL, False, hour=hour, minute=minute, end_hour=end_hour, end_minute=end_minute))
                screen.refresh_now = True

        # Add a recurring event:
        if screen.key == "A":
            name = input_string(stdscr, screen.y_max-2, 0, MSG_EVENT_TITLE, screen.x_max-len(MSG_EVENT_TITLE)-2)
            if name:
                clear_line(stdscr, screen.y_max-2, 0)
                time_str = input_string(stdscr, screen.y_max-2, 0, "Time (HH:MM or Enter for all-day): ", 6)
                hour, minute = None, None
                if time_str and ":" in time_str:
                    try:
                        parts = time_str.split(":")
                        hour = int(parts[0])
                        minute = int(parts[1]) if len(parts) > 1 else 0
                        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                            hour, minute = None, None
                    except ValueError:
                        hour, minute = None, None
                
                item_id = user_events.items[-1].item_id + 1 if not user_events.is_empty() else 1
                reps = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_REP)
                freq = input_frequency(stdscr, screen.y_max-2, 0, MSG_EVENT_FR)
                if reps is not None and freq is not None:
                    reps = 1 if reps == 0 else reps
                    user_events.add_item(UserEvent(item_id, screen.year, screen.month, screen.day, name, reps+1, freq, Status.NORMAL, False, hour=hour, minute=minute))

        # Import from calcurse:
        if screen.key == "C":
            confirmed = ask_confirmation(stdscr, MSG_EVENT_IMP, cf.ASK_CONFIRMATIONS)
            if confirmed:
                importer.import_events_from_calcurse()

        # Handle "g" and "G" as go to selected (prefilled) day:
        if screen.key == "g":
            clear_line(stdscr, screen.y_max-2, 0)
            year, month, day = input_date(stdscr, screen.y_max-2, 0, MSG_GOTO)
            if screen.is_valid_date(year, month, day):
                screen.day = day
                screen.month = month
                screen.year = year
                screen.calendar_state = CalState.DAILY

        if screen.key == "G":
            clear_line(stdscr, screen.y_max-2, 0)
            question = f"{MSG_GOTO_D} {screen.year}/{screen.month}/"
            day = input_day(stdscr, screen.y_max-2, 0, question)
            if screen.is_valid_date(screen.year, screen.month, day):
                screen.day = day
                screen.calendar_state = CalState.DAILY

        # Reload/Refresh data:
        if screen.key == "Q":
            screen.reload_data = True
            screen.refresh_now = True
        # F5 also refreshes data
        try:
            if screen.key == "\x1b[15~":  # F5 key
                screen.reload_data = True
                screen.refresh_now = True
        except:
            pass

        # Change the view to monthly:
        if screen.key == "v":
            screen.calendar_state = CalState.MONTHLY

        if screen.key == "w":
            screen.calendar_state = CalState.MONTHLY

        # Other actions:
        if vim_style_exit(stdscr, screen):
            confirmed = ask_confirmation(stdscr, MSG_EXIT, cf.ASK_CONFIRMATION_TO_QUIT)
            screen.state = AppState.EXIT if confirmed else screen.state
        if screen.key == "*":
            screen.privacy = not screen.privacy
        # Removed Space keybinding - no state switching in unified workflow
        if screen.key == "?":
            screen.state = AppState.HELP
        if screen.key == "q":
            confirmed = ask_confirmation(stdscr, MSG_EXIT, cf.ASK_CONFIRMATION_TO_QUIT)
            screen.state = AppState.EXIT if confirmed else screen.state
        # Removed / keybinding - split screen always on in unified workflow
        
        # Unified keybinding: t = create task (handled in control_journal_screen)
        # Don't handle here to avoid conflicts
        if screen.key == "W":
            screen.show_week_numbers = not screen.show_week_numbers
            screen.refresh_now = True


@safe_run
def control_weekly_screen(stdscr, screen, user_events, importer):
    """Handle user input on the weekly screen"""
    # Key should already be set by main loop for unified workflow
    # Don't read key again - use the one already set
    if screen.key is None:
        return  # No key available, skip processing
    
    if screen.key in ["n", "j", "KEY_DOWN", "KEY_RIGHT"]:
        # Next week
        for _ in range(7):
            screen.next_day()
        screen.refresh_now = True
    if screen.key in ["p", "k", "KEY_UP", "KEY_LEFT"]:
        # Previous week
        for _ in range(7):
            screen.previous_day()
        screen.refresh_now = True
    if screen.key in ["KEY_HOME", "R"]:
        screen.reset_to_today()
        screen.refresh_now = True
    if screen.key == "R" and screen.key != "KEY_HOME":
        # Manual refresh of data (Shift+R, not just R which is reset to today)
        screen.reload_data = True
        screen.refresh_now = True
    
    # Add single event (unified workflow: a = add event):
    if screen.key == "a":
        # Step 1: Ask for date
        clear_line(stdscr, screen.y_max-2, 0)
        year, month, day = input_date(stdscr, screen.y_max-2, 0, MSG_EVENT_DATE)
        if not screen.is_valid_date(year, month, day):
            # If invalid, use current screen date
            year, month, day = screen.year, screen.month, screen.day
        
        # Step 2: Ask for title
        clear_line(stdscr, screen.y_max-2, 0)
        name = input_string(stdscr, screen.y_max-2, 0, MSG_EVENT_TITLE, screen.x_max-len(MSG_EVENT_TITLE)-2)
        if name:
            # Step 3: Ask for start time (Enter = all-day event)
            clear_line(stdscr, screen.y_max-2, 0)
            start_time_str = input_string(stdscr, screen.y_max-2, 0, "Start time (HH:MM or Enter for all-day): ", 6)
            hour, minute = None, None
            end_hour, end_minute = None, None
            
            if start_time_str and ":" in start_time_str:
                try:
                    parts = start_time_str.split(":")
                    hour = int(parts[0])
                    minute = int(parts[1]) if len(parts) > 1 else 0
                    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                        hour, minute = None, None
                    else:
                        # Step 4: Ask for end time (Enter = default to 1 hour duration)
                        clear_line(stdscr, screen.y_max-2, 0)
                        end_time_str = input_string(stdscr, screen.y_max-2, 0, "End time (HH:MM or Enter for 1 hour): ", 6)
                        if end_time_str and ":" in end_time_str:
                            try:
                                end_parts = end_time_str.split(":")
                                end_hour = int(end_parts[0])
                                end_minute = int(end_parts[1]) if len(end_parts) > 1 else 0
                                if end_hour < 0 or end_hour > 23 or end_minute < 0 or end_minute > 59:
                                    end_hour, end_minute = None, None
                            except ValueError:
                                end_hour, end_minute = None, None
                        else:
                            # Default to 1 hour duration
                            end_hour = (hour + 1) % 24
                            end_minute = minute
                except ValueError:
                    hour, minute = None, None
            
            item_id = user_events.items[-1].item_id + 1 if not user_events.is_empty() else 1
            user_events.add_item(UserEvent(item_id, year, month, day, name, 1, Frequency.ONCE, Status.NORMAL, False, hour=hour, minute=minute, end_hour=end_hour, end_minute=end_minute))
            screen.refresh_now = True
    
    # Add a recurring event:
    if screen.key == "A":
        name = input_string(stdscr, screen.y_max-2, 0, MSG_EVENT_TITLE, screen.x_max-len(MSG_EVENT_TITLE)-2)
        if name:
            clear_line(stdscr, screen.y_max-2, 0)
            time_str = input_string(stdscr, screen.y_max-2, 0, "Time (HH:MM or Enter for all-day): ", 6)
            hour, minute = None, None
            if time_str and ":" in time_str:
                try:
                    parts = time_str.split(":")
                    hour = int(parts[0])
                    minute = int(parts[1]) if len(parts) > 1 else 0
                    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                        hour, minute = None, None
                except ValueError:
                    hour, minute = None, None
            
            item_id = user_events.items[-1].item_id + 1 if not user_events.is_empty() else 1
            reps = input_integer(stdscr, screen.y_max-2, 0, MSG_EVENT_REP)
            freq = input_frequency(stdscr, screen.y_max-2, 0, MSG_EVENT_FR)
            if reps is not None and freq is not None:
                reps = 1 if reps == 0 else reps
                user_events.add_item(UserEvent(item_id, screen.year, screen.month, screen.day, name, reps+1, freq, Status.NORMAL, False, hour=hour, minute=minute))
            screen.refresh_now = True
    
    if screen.key == "v":
        screen.calendar_state = CalState.MONTHLY
        screen.refresh_now = True
    if screen.key == "w":
        screen.calendar_state = CalState.MONTHLY
        screen.refresh_now = True
    # Removed Space keybinding - no state switching in unified workflow
    if screen.key == "?":
        screen.state = AppState.HELP
        screen.refresh_now = True
    if screen.key == "q":
        confirmed = ask_confirmation(stdscr, MSG_EXIT, cf.ASK_CONFIRMATION_TO_QUIT)
        screen.state = AppState.EXIT if confirmed else screen.state
    if vim_style_exit(stdscr, screen):
        confirmed = ask_confirmation(stdscr, MSG_EXIT, cf.ASK_CONFIRMATION_TO_QUIT)
        screen.state = AppState.EXIT if confirmed else screen.state


@safe_run
def control_journal_screen(stdscr, screen, user_tasks, importer, notion_saver=None):
    """Process user input on the journal screen"""
    # If we previously selected a task, now we perform the action:
    if screen.selection_mode:

        # Timer operations:
        if screen.key == 't':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TM_ADD)
            # Map number to actual task index (skipping headers)
            selectable_tasks = [i for i, t in enumerate(user_tasks.items) if not (hasattr(t, 'is_header') and t.is_header)]
            if number is not None and 0 <= number < len(selectable_tasks):
                actual_index = selectable_tasks[number]
                task_id = user_tasks.items[actual_index].item_id
                if cf.ONE_TIMER_AT_A_TIME:
                    user_tasks.pause_all_other_timers(task_id)
                user_tasks.add_timestamp_for_task(task_id)

        if screen.key == 'T':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TM_RESET)
            selectable_tasks = [i for i, t in enumerate(user_tasks.items) if not (hasattr(t, 'is_header') and t.is_header)]
            if number is not None and 0 <= number < len(selectable_tasks):
                actual_index = selectable_tasks[number]
                task_id = user_tasks.items[actual_index].item_id
                user_tasks.reset_timer_for_task(task_id)

        # Add deadline:
        if screen.key == "f":
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_DEAD_ADD)
            selectable_tasks = [i for i, t in enumerate(user_tasks.items) if not (hasattr(t, 'is_header') and t.is_header)]
            if number is not None and 0 <= number < len(selectable_tasks):
                actual_index = selectable_tasks[number]
                task_id = user_tasks.items[actual_index].item_id
                clear_line(stdscr, screen.y_max-2, 0)
                year, month, day = input_date(stdscr, screen.y_max-2, 0, MSG_TS_DEAD_DATE)
                if screen.is_valid_date(year, month, day):
                    user_tasks.change_deadline(task_id, year, month, day)

        # Remove deadline:
        if screen.key == "F":
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_DEAD_DEL)
            selectable_tasks = [i for i, t in enumerate(user_tasks.items) if not (hasattr(t, 'is_header') and t.is_header)]
            if number is not None and 0 <= number < len(selectable_tasks):
                actual_index = selectable_tasks[number]
                task_id = user_tasks.items[actual_index].item_id
                user_tasks.change_deadline(task_id, 0, 0, 0)

        # Change the status:
        if screen.key in ['i', 'h']:
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_HIGH)
            # Map number to actual task index (skipping headers)
            selectable_tasks = [i for i, t in enumerate(user_tasks.items) if not (hasattr(t, 'is_header') and t.is_header)]
            if number is not None and 0 <= number < len(selectable_tasks):
                actual_index = selectable_tasks[number]
                task = user_tasks.items[actual_index]
                # Toggle status to IMPORTANT
                if task.status == Status.IMPORTANT:
                    user_tasks.toggle_item_status(task.item_id, Status.NORMAL)
                    # Sync to Notion if applicable
                    if hasattr(task, 'notion_id') and task.notion_id and notion_saver:
                        # Find a non-important status from options
                        if hasattr(task, 'notion_status_options') and task.notion_status_options:
                            for opt in task.notion_status_options:
                                if opt.get("name") not in ["High", "Urgent"]:
                                    notion_saver.update_status(task.notion_id, opt.get("name"))
                                    task.current_notion_status = opt.get("name")
                                    break
                else:
                    user_tasks.toggle_item_status(task.item_id, Status.IMPORTANT)
                    # Sync to Notion if applicable
                    if hasattr(task, 'notion_id') and task.notion_id and notion_saver:
                        # Find High or Urgent status
                        if hasattr(task, 'notion_status_options') and task.notion_status_options:
                            for opt in task.notion_status_options:
                                if opt.get("name") in ["High", "Urgent"]:
                                    notion_saver.update_status(task.notion_id, opt.get("name"))
                                    task.current_notion_status = opt.get("name")
                                    break
                user_tasks.changed = True
                screen.refresh_now = True
        if screen.key == 'l':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_LOW)
            # Map number to actual task index (skipping headers)
            selectable_tasks = [i for i, t in enumerate(user_tasks.items) if not (hasattr(t, 'is_header') and t.is_header)]
            if number is not None and 0 <= number < len(selectable_tasks):
                actual_index = selectable_tasks[number]
                task = user_tasks.items[actual_index]
                user_tasks.toggle_item_status(task.item_id, Status.UNIMPORTANT)
                user_tasks.changed = True
                screen.refresh_now = True
        if screen.key == 'u':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_RES)
            # Map number to actual task index (skipping headers)
            selectable_tasks = [i for i, t in enumerate(user_tasks.items) if not (hasattr(t, 'is_header') and t.is_header)]
            if number is not None and 0 <= number < len(selectable_tasks):
                actual_index = selectable_tasks[number]
                task = user_tasks.items[actual_index]
                user_tasks.toggle_item_status(task.item_id, Status.NORMAL)
                user_tasks.changed = True
                screen.refresh_now = True
        if screen.key in ['d', 'v']:
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_DONE)
            # Map number to actual task index (skipping headers)
            selectable_tasks = [i for i, t in enumerate(user_tasks.items) if not (hasattr(t, 'is_header') and t.is_header)]
            if number is not None and 0 <= number < len(selectable_tasks):
                actual_index = selectable_tasks[number]
                task = user_tasks.items[actual_index]
                task_name = task.name
                old_status = task.status
                
                # Log status change attempt
                try:
                    from calcure.debug_logger import debug_logger
                    debug_logger.log_event("TASK_STATUS_CHANGE", f"Changing status of task #{number} (ID: {task.item_id}): '{task_name}' from {old_status.name}")
                except:
                    pass
                
                # Toggle status to DONE
                if task.status == Status.DONE:
                    user_tasks.toggle_item_status(task.item_id, Status.NORMAL)
                    new_status = Status.NORMAL
                    # Sync to Notion if applicable
                    if hasattr(task, 'notion_id') and task.notion_id and notion_saver:
                        # Find a non-Done status from options
                        if hasattr(task, 'notion_status_options') and task.notion_status_options:
                            for opt in task.notion_status_options:
                                if opt.get("name") not in ["Done", "Completed"]:
                                    try:
                                        notion_saver.update_status(task.notion_id, opt.get("name"))
                                        task.current_notion_status = opt.get("name")
                                        try:
                                            from calcure.debug_logger import debug_logger
                                            debug_logger.log_event("NOTION_STATUS_SYNC", f"Synced Notion task {task.notion_id} status to '{opt.get('name')}'")
                                        except:
                                            pass
                                    except Exception as e:
                                        try:
                                            from calcure.debug_logger import debug_logger
                                            debug_logger.log_error("NOTION_SYNC_ERROR", f"Failed to sync Notion status: {e}", e)
                                        except:
                                            pass
                                    break
                else:
                    user_tasks.toggle_item_status(task.item_id, Status.DONE)
                    new_status = Status.DONE
                    # Sync to Notion if applicable
                    if hasattr(task, 'notion_id') and task.notion_id and notion_saver:
                        try:
                            notion_saver.update_status(task.notion_id, "Done")
                            task.current_notion_status = "Done"
                            try:
                                from calcure.debug_logger import debug_logger
                                debug_logger.log_event("NOTION_STATUS_SYNC", f"Synced Notion task {task.notion_id} status to 'Done'")
                            except:
                                pass
                        except Exception as e:
                            try:
                                from calcure.debug_logger import debug_logger
                                debug_logger.log_error("NOTION_SYNC_ERROR", f"Failed to sync Notion status to Done: {e}", e)
                            except:
                                pass
                
                user_tasks.changed = True
                screen.refresh_now = True
                
                try:
                    from calcure.debug_logger import debug_logger
                    debug_logger.log_event("TASK_STATUS_CHANGED", f"Task #{number} (ID: {task.item_id}): '{task_name}' status changed from {old_status.name} to {new_status.name}")
                except:
                    pass

        # New: Change Notion Status via Menu
        if screen.key == 'c':
            number = input_integer(stdscr, screen.y_max-2, 0, "Number of task to change status: ")
            if user_tasks.is_valid_number(number):
                task = user_tasks.items[number]
                if not task.is_header and task.notion_id and task.notion_status_options:
                    # Display options
                    clear_line(stdscr, screen.y_max-2, 0)
                    # Simple horizontal list or cycling? Space is limited.
                    # Let's try listing them with indices
                    options_str = " | ".join([f"{i+1}.{opt['name']}" for i, opt in enumerate(task.notion_status_options)])
                    # If too long, cut it?
                    if len(options_str) > screen.x_max:
                        options_str = options_str[:screen.x_max-5] + "..."
                    
                    choice = input_integer(stdscr, screen.y_max-2, 0, f"Select status ({options_str}): ")
                    if choice is not None and 0 < choice <= len(task.notion_status_options):
                        selected_status = task.notion_status_options[choice-1]
                        status_name = selected_status['name']
                        
                        # Update Notion
                        if notion_saver:
                            notion_saver.update_status(task.notion_id, status_name)
                            
                        # Update local status approximation
                        if status_name == "Done":
                            user_tasks.toggle_item_status(task.item_id, Status.DONE)
                        elif status_name in ["High", "Urgent"]:
                            user_tasks.toggle_item_status(task.item_id, Status.IMPORTANT)
                        else:
                            user_tasks.toggle_item_status(task.item_id, Status.NORMAL)
                        
                        task.current_notion_status = status_name

        # Toggle task privacy:
        if screen.key == '.':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_PRIVACY)
            selectable_tasks = [i for i, t in enumerate(user_tasks.items) if not (hasattr(t, 'is_header') and t.is_header)]
            if number is not None and 0 <= number < len(selectable_tasks):
                actual_index = selectable_tasks[number]
                task_id = user_tasks.items[actual_index].item_id
                user_tasks.toggle_item_privacy(task_id)

        # Modify the task:
        if screen.key in ['x']:
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_DEL)
            selectable_tasks = [i for i, t in enumerate(user_tasks.items) if not (hasattr(t, 'is_header') and t.is_header)]
            if number is not None and 0 <= number < len(selectable_tasks):
                actual_index = selectable_tasks[number]
                task = user_tasks.items[actual_index]
                task_id = task.item_id
                task_name = task.name
                
                # Log deletion attempt
                try:
                    from calcure.debug_logger import debug_logger
                    debug_logger.log_event("TASK_DELETE_ATTEMPT", f"Attempting to delete task #{number} (ID: {task_id}): '{task_name}'")
                except:
                    pass
                
                # Ask for confirmation
                from calcure.dialogues import ask_confirmation
                from calcure.translations.en import MSG_TS_DEL_ALL
                confirmed = ask_confirmation(stdscr, f"Really delete task '{task_name}'? (y/n) ", cf.ASK_CONFIRMATIONS)
                
                if confirmed:
                    # Mark Notion tasks as deleted so they don't reload
                    if hasattr(task, 'notion_id') and task.notion_id:
                        task._deleted = True
                        try:
                            from calcure.debug_logger import debug_logger
                            debug_logger.log_event("TASK_DELETE_NOTION", f"Marking Notion task {task.notion_id} as deleted")
                        except:
                            pass
                    
                    user_tasks.delete_item(task_id)
                    user_tasks.changed = True
                    screen.refresh_now = True
                    
                    try:
                        from calcure.debug_logger import debug_logger
                        debug_logger.log_event("TASK_DELETE_SUCCESS", f"Successfully deleted task #{number} (ID: {task_id}): '{task_name}'")
                    except:
                        pass
                else:
                    try:
                        from calcure.debug_logger import debug_logger
                        debug_logger.log_event("TASK_DELETE_CANCELLED", f"User cancelled deletion of task #{number}: '{task_name}'")
                    except:
                        pass
        if screen.key == 'm':
            number_from = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_MOVE)
            selectable_tasks = [i for i, t in enumerate(user_tasks.items) if not (hasattr(t, 'is_header') and t.is_header)]
            if number_from is not None and 0 <= number_from < len(selectable_tasks):
                clear_line(stdscr, screen.y_max-2)
                number_to = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_MOVE_TO)
                if number_to is not None and 0 <= number_to < len(selectable_tasks):
                    actual_from = selectable_tasks[number_from]
                    actual_to = selectable_tasks[number_to]
                    user_tasks.move_task(actual_from, actual_to)
        if screen.key in ['e', 'r']:
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_EDIT)
            selectable_tasks = [i for i, t in enumerate(user_tasks.items) if not (hasattr(t, 'is_header') and t.is_header)]
            if number is not None and 0 <= number < len(selectable_tasks):
                actual_index = selectable_tasks[number]
                task_id = user_tasks.items[actual_index].item_id
                clear_line(stdscr, actual_index+2, screen.x_min)
                new_name = input_string(stdscr, actual_index+2, screen.x_min, cf.TODO_ICON+' ', screen.x_max-4)
                user_tasks.rename_item(task_id, new_name)

        # Subtask operations:
        if screen.key == 'S':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_TOG)
            selectable_tasks = [i for i, t in enumerate(user_tasks.items) if not (hasattr(t, 'is_header') and t.is_header)]
            if number is not None and 0 <= number < len(selectable_tasks):
                actual_index = selectable_tasks[number]
                task_id = user_tasks.items[actual_index].item_id
                user_tasks.toggle_subtask_state(task_id)
        if screen.key == 'A':
            number = input_integer(stdscr, screen.y_max-2, 0, MSG_TS_SUB)
            if user_tasks.is_valid_number(number):
                clear_line(stdscr, screen.y_max-2, 0)
                task_name = input_string(stdscr, screen.y_max-2, 0, MSG_TS_TITLE, screen.x_max-len(MSG_TS_TITLE)-2)
                task_id = user_tasks.generate_id()
                user_tasks.add_subtask(Task(task_id, task_name, Status.NORMAL, Timer([]), False), number)
        screen.selection_mode = False

    # Otherwise, we check for user input:
    else:
        # Key should already be set by main loop for unified workflow
        # Don't read key again - use the one already set
        if screen.key is None:
            return  # No key available, skip processing

        # Unified keybinding: t = create task (works from unified view)
        if screen.key == "t":
            # Calculate position in task list area - find where Local Tasks section starts
            # Journal pane starts at x_min, y starts at 0
            task_y_pos = 1  # Start after "JOURNAL" header (y=0 is header)
            task_y_pos += 1  # "━━━ Local Tasks ━━━" header
            # Input should appear at the top of the local tasks list (after header)
            
            clear_line(stdscr, task_y_pos, screen.x_min)
            max_width = screen.x_max - screen.x_min - 4
            task_name = input_string(stdscr, task_y_pos, screen.x_min, cf.TODO_ICON+' ', max_width)
            if task_name:
                task_id = user_tasks.generate_id()
                # Ensure new tasks are local (no notion_id) so they appear in local section
                new_task = Task(task_id, task_name, Status.NORMAL, Timer([]), False, notion_id=None)
                
                # Insert at the beginning of the list (position 0) so new tasks appear at top
                user_tasks.items.insert(0, new_task)
                
                user_tasks.changed = True
                screen.refresh_now = True
                
                # Log task creation
                try:
                    from calcure.debug_logger import debug_logger
                    debug_logger.log_event("TASK_CREATE", f"Created local task (ID: {task_id}): '{task_name}' at position 0")
                except:
                    pass
            # Don't process this key further
            return
        
        # If we need to select a task, change to selection mode:
        # Note: 't' removed from selection_keys since it's now for creating tasks
        # Also: Don't set selection_mode if we're already in selection_mode (to avoid double prompts)
        if not screen.selection_mode:
            selection_keys = ['T', 'h', 'l', 'v', 'u', 'i', 's', 'S', 'd', 'x', 'e', 'r', 'c', 'A', 'm', '.', 'f', 'F']
            # Filter out header tasks from selection
            selectable_tasks = [t for t in user_tasks.items if not (hasattr(t, 'is_header') and t.is_header)]
            if screen.key in selection_keys and selectable_tasks:
                screen.selection_mode = True
                return  # Exit early to wait for next keypress

        # Keep 'a' for backward compatibility (though unified workflow uses 't' for tasks)
        if screen.key == "a":
            clear_line(stdscr, len(user_tasks.items) + 2, screen.x_min)
            task_name = input_string(stdscr, len(user_tasks.items) + 2, screen.x_min, cf.TODO_ICON+' ', screen.x_max - 4)
            if task_name:
                task_id = user_tasks.generate_id()
                # Ensure new tasks are local (no notion_id) so they appear in local section
                user_tasks.add_item(Task(task_id, task_name, Status.NORMAL, Timer([]), False, notion_id=None))

        # Bulk operations:
        if screen.key in ["V", "D"]:
            confirmed = ask_confirmation(stdscr, MSG_TS_EDT_ALL, cf.ASK_CONFIRMATIONS)
            if confirmed:
                user_tasks.change_all_statuses(Status.DONE)
        if screen.key == "U":
            confirmed = ask_confirmation(stdscr, MSG_TS_EDT_ALL, cf.ASK_CONFIRMATIONS)
            if confirmed:
                user_tasks.change_all_statuses(Status.NORMAL)
        if screen.key == "L":
            confirmed = ask_confirmation(stdscr, MSG_TS_EDT_ALL, cf.ASK_CONFIRMATIONS)
            if confirmed:
                user_tasks.change_all_statuses(Status.UNIMPORTANT)
        if screen.key in ["I", "H"]:
            confirmed = ask_confirmation(stdscr, MSG_TS_EDT_ALL, cf.ASK_CONFIRMATIONS)
            if confirmed:
                user_tasks.change_all_statuses(Status.IMPORTANT)
        if screen.key in ["X"]:
            confirmed = ask_confirmation(stdscr, MSG_TS_DEL_ALL, cf.ASK_CONFIRMATIONS)
            if confirmed:
                user_tasks.delete_all_items()

        # Imports:
        if screen.key == "C":
            confirmed = ask_confirmation(stdscr, MSG_TS_IM, cf.ASK_CONFIRMATIONS)
            if confirmed:
                importer.import_tasks_from_calcurse()
                screen.refresh_now = True
        # if screen.key == "W":
            # confirmed = ask_confirmation(stdscr, MSG_TS_TW, cf.ASK_CONFIRMATIONS)
            # if confirmed:
                # importer.import_tasks_from_taskwarrior()
                # screen.refresh_now = True

        # Reload:
        if screen.key in ["Q"]:
            screen.reload_data = True
            screen.refresh_now = True

        # Other actions:
        if vim_style_exit(stdscr, screen):
            confirmed = ask_confirmation(stdscr, MSG_EXIT, cf.ASK_CONFIRMATION_TO_QUIT)
            screen.state = AppState.EXIT if confirmed else screen.state
        if screen.key == "*":
            screen.privacy = not screen.privacy
        if screen.key in [" ", "KEY_BTAB"]:
            screen.state = AppState.CALENDAR
        if screen.key == "?":
            screen.state = AppState.HELP
        if screen.key == "q":
            confirmed = ask_confirmation(stdscr, MSG_EXIT, cf.ASK_CONFIRMATION_TO_QUIT)
            screen.state = AppState.EXIT if confirmed else screen.state
        if screen.key in ["/"]:
            screen.split = not screen.split
            screen.refresh_now = True


@safe_run
def control_help_screen(stdscr, screen):
    """Process user input on the help screen"""
    # Getting user's input:
    screen.key = stdscr.getkey()

    # Handle vim-style exit on "ZZ" and "ZQ":
    if vim_style_exit(stdscr, screen):
        confirmed = ask_confirmation(stdscr, MSG_EXIT, cf.ASK_CONFIRMATION_TO_QUIT)
        screen.state = AppState.EXIT if confirmed else screen.state

    # Handle keys to exit the help screen:
    if screen.key in [" ", "?", "q", "^[", "\x7f"]:
        screen.state = AppState.CALENDAR


@safe_run
def control_welcome_screen(stdscr, screen):
    """Process user input on the welcome screen"""
    # Getting user's input:
    screen.key = stdscr.getkey()

    # Handle key to call help screen:
    if screen.key in ["?"]:
        screen.state = AppState.HELP

    # Otherwise, just start the program:
    else:
        screen.state = AppState.CALENDAR
