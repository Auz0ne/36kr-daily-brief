"""CLI tool to manage newsletter subscribers."""

import json
import re
import sys

SUBSCRIBERS_FILE = "subscribers.json"


def load_subscribers() -> list[str]:
    try:
        with open(SUBSCRIBERS_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_subscribers(subscribers: list[str]):
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(subscribers, f, indent=2)


def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


def add(email: str):
    email = email.strip().lower()
    if not is_valid_email(email):
        print(f"Invalid email: {email}")
        sys.exit(1)
    subscribers = load_subscribers()
    if email in subscribers:
        print(f"Already subscribed: {email}")
        return
    subscribers.append(email)
    save_subscribers(subscribers)
    print(f"Added: {email}")


def remove(email: str):
    email = email.strip().lower()
    subscribers = load_subscribers()
    if email not in subscribers:
        print(f"Not found: {email}")
        sys.exit(1)
    subscribers.remove(email)
    save_subscribers(subscribers)
    print(f"Removed: {email}")


def list_all():
    subscribers = load_subscribers()
    if not subscribers:
        print("No subscribers yet.")
        return
    print(f"{len(subscribers)} subscriber(s):")
    for s in subscribers:
        print(f"  {s}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python manage_subscribers.py add <email>")
        print("  python manage_subscribers.py remove <email>")
        print("  python manage_subscribers.py list")
        sys.exit(1)

    command = sys.argv[1]
    if command == "add":
        if len(sys.argv) < 3:
            print("Usage: python manage_subscribers.py add <email>")
            sys.exit(1)
        add(sys.argv[2])
    elif command == "remove":
        if len(sys.argv) < 3:
            print("Usage: python manage_subscribers.py remove <email>")
            sys.exit(1)
        remove(sys.argv[2])
    elif command == "list":
        list_all()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
