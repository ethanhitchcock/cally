# Calcure

Modern TUI calendar and task manager with customizable interface. Manages your events and tasks, displays birthdays from your [abook](https://abook.sourceforge.io/), and can import events and tasks from [calcurse](https://github.com/lfos/calcurse). Now with **live data connectors** for real-time synchronization with external services like Notion.

[See documentation](https://anufrievroman.gitbook.io/calcure/) for more information.

![screenshot](screenshot.png)

## Features

### Core Features
- **Unified Workflow**: Single-screen view with calendar and tasks always visible - no mode switching required
- **Weekly View**: Toggle between monthly and weekly calendar views (`w` key)
- **Vim keys**: Full vim-style navigation support
- **Live Data Connectors**: Real-time synchronization with external services (currently Notion)
- **ICS Calendar Sync**: Read-only display of events from cloud calendars (.ics files)
- **Operation with fewest key presses possible**: Streamlined keyboard shortcuts
- **Todo list with subtasks, deadlines, and timers**: Full-featured task management
- **Birthdays of your abook contacts**: Automatic birthday display
- **Import of events and tasks from calcurse**: Legacy import support
- **Icons according to the name** ✈ ⛷ ⛱
- **Private events and tasks** •••••
- **Plain text database**: CSV files for cloud sync
- **Customizable colors, icons, and other features**: Extensive customization
- **Resize and mobile friendly**: Responsive terminal UI
- **Current weather** ⛅
- **Support for [Persian calendar](https://en.wikipedia.org/wiki/Iranian_calendars)**

### New Features & Improvements

#### Live Data Integration
- **Notion Integration**: 
  - Live task synchronization with Notion databases
  - Filter tasks by assignee (e.g., "Ethan Hitchcock")
  - Automatic exclusion of completed tasks
  - Project-based task grouping with human-readable project names
  - Status synchronization: changes in Calcure sync to Notion
  - Change Notion task status via menu (`c` key)
  - Deleted tasks persist across restarts

#### Enhanced Event Management
- **Event Creation with Times**: 
  - Create events with specific start and end times
  - All-day event support (press Enter to skip time)
  - Default 1-hour duration for timed events
  - Date → Title → Start Time → End Time workflow

#### Improved Task Management
- **Smart Task Organization**:
  - Tasks appear at the top of the list when created
  - Visual separation between local and Notion tasks
  - Project headers for Notion tasks (non-selectable)
  - Correct task numbering in selection mode
  - Task deletion confirmation dialogs

#### User Interface Enhancements
- **Visual Refresh Indicator**: Shows "⟳ Reloading data..." during data refresh
- **Context-Sensitive Help**: Keybindings displayed based on current context
- **Unified Keybindings**: 
  - `t` - Create task (works from anywhere)
  - `a` - Add event (works from anywhere)
  - `A` - Add recurring event
  - `Q` - Manual refresh of live data
  - `w` - Toggle weekly/monthly view
  - `d/v` - Mark task as done (then enter task number)
  - `x` - Delete task/event (then enter number)
  - `c` - Change Notion task status

#### Debug & Logging
- **Comprehensive Debug Logging**: 
  - Verbose logging to `calcure_debug.log`
  - ICS event loading details (every event logged)
  - Task load/save operations
  - Error tracking and crash reporting
  - Input timeout handling

#### Data Persistence
- **Local Tasks**: Automatically saved to CSV
- **Notion Tasks**: Live synchronization, not saved locally
- **Deleted Task Tracking**: Notion tasks marked as deleted persist across restarts

## Installation

### Linux and Mac OS

There are several ways to install:

`pipx install calcure` - the up-to-date version from PyPi. You may need to install `pipx` first.

`yay -S calcure` - [AUR package](https://aur.archlinux.org/packages/calcure) is available. Upvote to support the project!

`calcure` is also available as NixOS package.

### Windows

1. Install [Windows Terminal](https://apps.microsoft.com/detail/9n0dx20hk701?hl=en-US&gl=US) app from the Microsoft Store.
2. Install [Python 3.x](https://apps.microsoft.com/search/publisher?name=Python+Software+Foundation&hl=en-us&gl=US) also from the Microsoft Store (if you just type `python` in the Windows Terminal app it will offer you to install)
3. Install the program and libraries by typing in the Windows Terminal `pip install windows-curses calcure`
4. Now you can finally run it by typing in the Windows Terminal `python -m calcure`

### Upgrade to the most recent version

`pipx upgrade calcure`

### Dependencies

- `python` 3.10 and higher (usually already installed)
- `holidays`, `jdatetime`, and `icalendar` python libraries (should be installed automatically with the calcure)
- `windows-curses` on Windows
- `requests` and `python-dotenv` for live data connectors (Notion integration)

## Configuration

### Environment Variables (for Live Data Connectors)

Create a `.env` file in the calcure directory with your API credentials:

```bash
# Notion Integration
NOTION_API_KEY=secret_xxxxxxxxxxxxx
NOTION_DATABASE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### Settings

[Example of config.ini file](https://anufrievroman.gitbook.io/calcure/default-config) and [explanations of all settings](https://anufrievroman.gitbook.io/calcure/settings) are available in the documentation.
On the first run, program will create a `config.ini` file where you can edit parameters, colors, and icons at `~/.config/calcure/config.ini`.

## Usage

Run `calcure` in your terminal. You may need to restart your terminal after the install.

### Key Bindings

#### General
- `t` - Create new task
- `a` - Add event
- `A` - Add recurring event
- `*` - Toggle global privacy
- `?` - Toggle help
- `Q` - Reload data (refresh Notion tasks and ICS calendars)
- `q` - Quit

#### Calendar Navigation
- `n` / `j` / `→` - Next month/day/week
- `p` / `k` / `←` - Previous month/day/week
- `w` - Toggle weekly/monthly view
- `v` - Toggle daily/monthly view
- `R` - Return to current month/day
- `g` / `G` - Go to specific date

#### Event Management
- `a` - Add event (prompts: date → title → start time → end time)
- `A` - Add recurring event
- `x` - Delete event (press `x`, then enter event number)
- `e` / `r` - Edit/rename event
- `m` / `M` - Move event
- `h` / `i` - Mark event as high priority
- `l` - Mark event as low priority
- `d` - Mark event as done
- `.` - Toggle event privacy

#### Task Management
- `t` - Create new task (appears at top of list)
- `d` / `v` - Mark task as done (press `d`/`v`, then enter task number)
- `x` - Delete task (press `x`, then enter task number - confirmation required)
- `h` / `i` - Mark task as important
- `l` - Mark task as low priority
- `u` - Reset task status
- `e` / `r` - Edit/rename task
- `c` - Change Notion task status (select from available statuses)
- `T` - Start/pause timer for task
- `f` / `F` - Add/remove task deadline
- `m` - Move task
- `.` - Toggle task privacy
- `s` - Toggle subtask state
- `S` - Add subtask

### Syncing with Cloud Calendars

[This page in documentation](https://anufrievroman.gitbook.io/calcure/syncing-with-clouds) shows examples how to sync and display in read-only mode events and tasks from Nextcloud, Google, and other calendars.

**Note**: ICS calendar links are read-only. To push events to calendars, use calendar-specific APIs (Google Calendar API, CalDAV, Microsoft Graph API).

### Notion Integration

Calcure can sync tasks from Notion databases in real-time:

1. **Setup**: 
   - Create a `.env` file with your Notion API key and database ID
   - Configure your Notion database with these properties:
     - "Task name" (title)
     - "Status" (select)
     - "Due date" (date) - optional
     - "Project" (relation) - optional
     - "Responsible" (person) - for filtering

2. **Features**:
   - Tasks filtered by assignee automatically
   - Completed tasks excluded automatically
   - Tasks grouped by project with readable project names
   - Status changes sync bidirectionally
   - Deleted tasks persist across restarts

3. **Usage**:
   - Tasks load automatically on startup
   - Press `Q` to manually refresh
   - Press `c` to change Notion task status
   - Press `d`/`v` to mark as done (syncs to Notion)
   - Press `h`/`i` to mark as important (syncs to Notion)

### User Arguments

[Various user arguments](https://anufrievroman.gitbook.io/calcure/user-arguments) can be added started in special mods add tasks and events etc.

### Debug Logging

All operations are logged to `calcure_debug.log` in the calcure directory:
- Data loading (events, tasks, ICS calendars, Notion)
- Task operations (create, delete, status changes)
- Event operations
- Errors and crashes
- ICS event details (every event loaded)

Check this file if you encounter issues or want to see what data is being loaded.

### Setting daily reminders

You can try [this project](https://github.com/sponkurtus2/calcxporte_r) to recieve daily reminders of events in your Calcure.

### Troubleshooting

[Typical problems and solutions](https://anufrievroman.gitbook.io/calcure/troubleshooting) are described in documentation. If you faced a new problem, don't hesitate to open an issue.

**Common Issues**:
- **ICS events not showing**: Check `calcure_debug.log` for filtering details. Events are filtered by date - ensure you're viewing the correct month.
- **Tasks not persisting**: Check `calcure_debug.log` for save/load operations. Ensure tasks are local (not Notion tasks) to be saved to CSV.
- **Notion tasks not loading**: Verify `.env` file has correct `NOTION_API_KEY` and `NOTION_DATABASE_ID`. Check debug log for API errors.

## Contribution

[Full information about contribution](https://anufrievroman.gitbook.io/calcure/contribution) is available in the documentation.

## Support

I am not a professional developer and work on open-source projects in my free time. If you'd like to support the development, consider donations via [buymeacoffee](https://www.buymeacoffee.com/angryprofessor) or cryptocurrencies:

- BTC `bc1qpkzmutdqfxkce34skt09vll97s5smpa0r2tyzj`
- ETH `0x6f1Ce9cA181458Fc153a5f7cBF88044736C3b00C`
- BNB `0x40f22c372758E35C905458cAF8BB17f51ac133d1`
- LTC `ltc1qtu33qyv2xlzxda5mmrmk943zpksq8q75tuh85p`
- XMR `4AHRhpNYUZcPVN78rbUWAzBuvMKQdpwStS5L3kjunnBMWWW2pjYBko1RUF6nQVpgQPdfAkM3jrEWrWKDHz1h4Ucd4gFCZ9j`

## Recent Changes

### Version Highlights

- **Unified Workflow**: Removed state switching - calendar and tasks always visible together
- **Weekly View**: New weekly calendar view showing 7 days at a glance
- **Notion Integration**: Live task synchronization with Notion databases
- **Enhanced Event Creation**: Support for timed events with start/end times
- **Improved Task Management**: Better organization, numbering, and persistence
- **Debug Logging**: Comprehensive logging for troubleshooting
- **Visual Feedback**: Refresh indicators and context-sensitive help
