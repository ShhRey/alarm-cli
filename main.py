"""
Module: main.py
Description: CLI entry point handling REPL user input, command dispatch,
             and lifecycle orchestration.
"""

import shlex

from parser import parse_optional_args, parse_time_string
from scheduler import AlarmScheduler
from service import AlarmService


def print_help() -> None:
    """Display available CLI commands and usage examples."""
    print("\n=== Alarm Clock CLI ===")
    print("Commands:")
    print('  set HH:MM name="Wake Up" msg="Gym time" snooze=10 type=daily')
    print("  list")
    print("  cancel HH:MM")
    print("  exit\n")


def main() -> None:
    """Initialize services, start background scheduler, and run command REPL."""
    service = AlarmService()
    scheduler = AlarmScheduler(service)
    scheduler.start()

    print_help()

    try:
        while True:
            try:
                user_input = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting alarm clock...")
                break

            if not user_input:
                continue

            try:
                parts = shlex.split(user_input)
            except ValueError as exc:
                print(f"Invalid command syntax: {exc}")
                continue

            action = parts[0].lower()

            if action == "set":
                handle_set(service, parts)
            elif action == "list":
                handle_list(service)
            elif action == "cancel":
                handle_cancel(service, parts)
            elif action in ("exit", "quit"):
                break
            elif action == "help":
                print_help()
            else:
                print(f"Unknown command: '{action}'. Type 'help' for options.")

    finally:
        scheduler.stop()
        scheduler.join()


def handle_set(service: AlarmService, parts: list[str]) -> None:
    """Handle the 'set' command to schedule a new alarm."""
    if len(parts) < 2:
        print('Usage: set HH:MM name="Wake Up" msg="Gym time"')
        return

    alarm_time = parse_time_string(parts[1])
    if alarm_time is None:
        print("Invalid time format. Use 24-hour HH:MM format.")
        return

    try:
        options = parse_optional_args(parts[2:])
        alarm = service.set_alarm(
            alarm_time=alarm_time,
            name=options["name"],
            message=options["message"],
            snooze_minutes=options["snooze"],
            alarm_type=options["alarm_type"],
        )
    except ValueError as exc:
        print(f"Unable to create alarm: {exc}")
        return

    print(
        f"✔ Alarm '{alarm.name}' successfully set for "
        f"{alarm.time.strftime('%Y-%m-%d %H:%M')} "
        f"({alarm.alarm_type.value})"
    )


def handle_list(service: AlarmService) -> None:
    """Handle the 'list' command to display all configured alarms."""
    alarms = service.list_alarms()

    if not alarms:
        print("No alarms configured.")
        return

    print("\nConfigured Alarms:")
    print("-" * 55)
    for alarm in alarms:
        print(
            f"{alarm.time.strftime('%Y-%m-%d %H:%M')} | "
            f"{alarm.name:<12} | "
            f"Type: {alarm.alarm_type.value:<5} | "
            f"Status: {alarm.status.value}"
        )
    print("-" * 55)


def handle_cancel(service: AlarmService, parts: list[str]) -> None:
    """Handle the 'cancel' command to disable an active alarm by time."""
    if len(parts) < 2:
        print("Usage: cancel HH:MM")
        return

    alarm_time = parse_time_string(parts[1])
    if alarm_time is None:
        print("Invalid time format. Use 24-hour HH:MM format.")
        return

    if service.cancel_alarm(alarm_time):
        print("✔ Alarm cancelled successfully.")
    else:
        print("No active alarm found matching that time.")


if __name__ == "__main__":
    main()