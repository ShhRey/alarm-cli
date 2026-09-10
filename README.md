# CLI Alarm Clock

A lightweight **Python CLI Alarm Clock** that lets you schedule, list, and cancel alarms from the terminal. The project is intentionally small, modular, and easy to reason about: it runs a REPL, persists alarms to a JSON file, and uses a background thread to trigger alarms in real time.

---

## Table of Contents

- [Project Overview](#project-overview)
- [File Structure](#file-structure)
- [Features](#features)
- [Implementation Flow](#implementation-flow)
- [Usage and Examples](#usage-and-examples)
- [User Stories](#user-stories)
- [Testing and Validation](#testing-and-validation)
- [Improvement Roadmap](#improvement-roadmap)
- [Development Notes](#development-notes)
- [License](#license)

---

## Project Overview

**Goal:** Build a usable CLI alarm clock demonstrating clear engineering decisions, thread-safe state management, and simple persistence — while documenting the design and thought process.

**Key ideas:**
- CLI-only (no web UI, no DB).
- Background scheduler thread to trigger alarms.
- JSON file persistence (`alarms.json`) for portability and simplicity.
- Modular code with separation of concerns for easier testing and maintenance.

---

## File Structure

```text
CLI/
├── main.py         # CLI entry point and REPL
├── parser.py       # Time and CLI-argument parsing utilities
├── model.py        # Alarm dataclass, enums, serialization
├── scheduler.py    # Background thread that triggers alarms
├── service.py      # Thread-safe business logic and persistence coordination
├── storage.py      # JSON load/save for alarms.json
└── pycache/        # Python bytecode cache (auto-generated)
```

**Brief Responsibilities:**
- **`main.py`**: REPL, command dispatch, lifecycle orchestration.
- **`parser.py`**: `HH:MM` parsing with rollover; optional `key=value` parsing.
- **`model.py`**: `Alarm` dataclass, `AlarmType`, `AlarmStatus`, `to_dict`/`from_dict`.
- **`scheduler.py`**: `AlarmScheduler` daemon thread; polls every second and triggers alarms.
- **`service.py`**: `AlarmService` with `RLock` for thread safety; `set`, `list`, `cancel`, `update`.
- **`storage.py`**: `load_alarms()` and `save_alarms()` to `alarms.json`.

---

## Features

- **Set alarms** (one-time and daily recurring).
- **List alarms** with time, name, type, and status.
- **Cancel alarms** by scheduled time.
- **Persistence** to `alarms.json` so alarms survive restarts.
- **Background scheduler** that checks alarms every second and triggers notifications (console + system bell).
- **Sane CLI UX**: quoted arguments supported via `shlex`, automatic rollover for past times, validation for inputs.

---

## Implementation Flow

1. **Start-up**
   - `main.py` initializes `AlarmService` and starts `AlarmScheduler` (daemon thread).
   - `AlarmService` loads persisted alarms from `alarms.json` using `storage.load_alarms()`.
2. **User Interaction**
   - REPL accepts commands: `set`, `list`, `cancel`, `help`, `exit`.
   - `shlex.split` tokenizes input so quoted strings are preserved.
3. **Parsing**
   - `parser.parse_time_string("HH:MM")` converts to a `datetime`. If the time has already passed today, it rolls forward to tomorrow.
   - `parser.parse_optional_args([...])` extracts `name`, `msg`, `snooze`, and `type` with validation.
4. **Business Logic**
   - `service.set_alarm(...)` creates an `Alarm` instance, appends it to the in-memory list, and persists via `storage.save_alarms()`.
   - `service.cancel_alarm(datetime)` marks the first matching active alarm as `CANCELLED` and persists.
5. **Scheduling & Triggering**
   - `AlarmScheduler` polls `service.list_alarms()` every second.
   - When `alarm.time <= now` and `alarm.status == ACTIVE`:
     - Print notification and emit system bell.
     - If `alarm_type == DAILY`: advance `alarm.time` by 1 day and keep `ACTIVE`.
     - Else: set `status = TRIGGERED`.
     - Persist changes via `service.update_alarm_state()`.

---

## Usage and Examples

### Requirements
- **Python 3.10+** (for modern typing syntax).
- No external dependencies.

### Run
```bash
python main.py
```

### Commands

**Set a one-time alarm**
```bash
set 07:30 name="Morning" msg="Time to run" snooze=10 type=once
```

**Set a daily alarm**
```bash
set 09:00 name="Standup" msg="Daily standup" type=daily
```

**List alarms**
```bash
list
```

**Cancel an alarm**
```bash
cancel 07:30
```

**Help**
```bash
help
```

**Exit**
```bash
exit
```

> **Notes on time parsing:**  
> Time format: 24-hour `HH:MM`.  
> If you set a time that already passed today, the parser automatically schedules it for tomorrow to avoid immediate firing.

---

## User Stories

### 1. Morning Run (One-time)
*As a user, I want to set a one-time alarm for tomorrow morning so I wake up for a run.*
- **Command:**
  ```bash
  set 06:00 name="Run" msg="Time to run" snooze=10 type=once
  ```
- **Expected:**
  - Alarm saved to `alarms.json`.
  - At `06:00` CLI prints `⏰ ALARM TRIGGERED [Run]: Time to run` and emits a beep.
  - Alarm status becomes triggered.

### 2. Daily Standup (Recurring)
*As a user, I want a daily reminder for my standup meeting.*
- **Command:**
  ```bash
  set 09:00 name="Standup" msg="Daily standup" type=daily
  ```
- **Expected:**
  - Triggers at `09:00` each day.
  - After triggering, `alarm.time` is advanced by 24 hours and remains active.

### 3. Cancel Mistaken Alarm
*As a user, I accidentally set an alarm and want to cancel it.*
- **Command:**
  ```bash
  cancel 07:30
  ```
- **Expected:**
  - If an active alarm exists with the exact scheduled datetime, it is marked cancelled and persisted.
  - If not found, CLI reports no match.

### 4. Quick Demo Setup
*As a presenter, I want to demonstrate the alarm triggering immediately.*
- **Command:**
  ```bash
  set 10:33 name="Demo" msg="Demo alarm" type=once
  ```
- **Expected:**
  - Within a minute the CLI prints the trigger message and the system bell sounds.

---

## Testing and Validation

**Suggested unit tests (pytest)**
- **Parser:**
  - `parse_time_string("23:59")` when current time is earlier should schedule today.
  - `parse_time_string("00:00")` when current time is 00:01 should schedule tomorrow.
  - `parse_optional_args(['snooze=0'])` should raise `ValueError`.
- **Model:**
  - `Alarm.to_dict()` and `Alarm.from_dict()` round-trip test.
- **Service:**
  - `set_alarm` persists to disk and `load_alarms` returns the same alarm.
  - `cancel_alarm` marks status and persists.
- **Scheduler (integration):**
  - Use a clock abstraction or monkeypatch `datetime.now()` to simulate time and assert triggers and recurrence behavior.

**Manual validation**
- Inspect `alarms.json` after setting alarms to confirm ISO 8601 timestamps and fields.
- Restart the program to confirm alarms are reloaded and scheduler resumes.

---

## Improvement Roadmap

**High priority**
- Add unit tests and CI integration.
- Improve cancellation matching (allow time-of-day or name-based cancellation).
- Introduce a clock abstraction for deterministic tests.

**Medium priority**
- Replace polling with a priority queue scheduler or `threading.Event` to sleep until the next alarm.
- Make storage atomic (write to temp file and rename).
- Add timezone-aware datetimes using `zoneinfo`.

**Low priority**
- Interactive snooze prompt at trigger time.
- Desktop notifications or cross-platform sound playback.
- Support richer recurrence rules (weekly, monthly) using `dateutil.rrule`.

---

---

## License
This project is provided as-is for demonstration and learning purposes. You may copy, modify, and use the code under the terms you prefer for personal or educational use. If you plan to publish or distribute, consider adding an explicit license (e.g., MIT, Apache 2.0).