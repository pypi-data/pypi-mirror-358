"""Send an SMS for each alarm found in an ICS file."""

import argparse
import datetime as dt
import heapq
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from subprocess import PIPE, run
from time import sleep
from zoneinfo import ZoneInfo

import requests
from ics import Calendar, Event

__version__ = "0.1"


@dataclass(order=True)
class Alarm:
    ring_at: dt.datetime
    event: Event = field(compare=False)


def ensure_tz(any_date):
    """If a date has no timezone, we guess it's France."""
    if any_date.tzinfo:
        return any_date
    return any_date.replace(tzinfo=ZoneInfo("Europe/Paris"))


@dataclass
class Alarms:
    ics_url: str
    ics_username: str
    ics_password: str
    already_sent: set[str] = field(default_factory=set, init=False)
    alarms: list[Alarm] = field(default_factory=list, init=False)

    def ack(self, alarm):
        self.already_sent.add(alarm.event.uid)

    def clear(self):
        self.alarms = []

    def add_event(self, event: Event):
        if event.uid in self.already_sent:
            return
        if not event.alarms:
            return
        if not event.begin:
            return
        trigger = event.alarms[0].trigger
        if trigger is None:
            return
        if isinstance(trigger, dt.datetime):
            ring_at = trigger
        elif isinstance(trigger, dt.timedelta):
            ring_at = event.begin + trigger
        new_alarm = Alarm(ring_at=ensure_tz(ring_at), event=event)
        heapq.heappush(self.alarms, new_alarm)

    @property
    def next(self):
        return self.alarms[0]

    def refresh(self):
        self.clear()
        auth = ()
        if self.ics_username:
            auth = self.ics_username, self.ics_password
        cal = requests.get(self.ics_url, auth=auth, timeout=10).text

        # See https://github.com/nextcloud/calendar/issues/5326
        cal = re.sub(
            "RRULE:FREQ=YEARLY;UNTIL=([0-9T]+)Z;BYDAY=",
            r"RRULE:FREQ=YEARLY;UNTIL=\1;BYDAY=",
            cal,
        )
        calendar = Calendar(cal)
        now = dt.datetime.now(dt.timezone.utc)
        for event in calendar.events:
            if ensure_tz(event.end) < now:
                continue
            self.add_event(event)


@dataclass
class FreeSMS:
    user: str
    api_key: str

    def send(self, msg):
        print("Sending notification:", msg)
        if self.user is None:
            return
        response = requests.get(
            "https://smsapi.free-mobile.fr/sendmsg",
            params={"user": self.user, "pass": self.api_key, "msg": msg},
        )
        response.raise_for_status()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, help="Path to a toml config file")
    parser.add_argument(
        "--free-user",
        help="mobile.free.fr username. If not given, no sms are sent, but logging still works.",
    )
    parser.add_argument("--free-api-key", help="mobile.free.fr SMS API key")
    parser.add_argument("--ics-url", help="URL of an ICS file")
    parser.add_argument(
        "--ics-username", help="If needed, provide a username for the HTTP auth."
    )
    parser.add_argument(
        "--ics-password", help="If needed, provide a username for the HTTP auth."
    )
    args = parser.parse_args()
    if args.config:
        config = tomllib.loads(args.config.read_text(encoding="UTF-8"))
        args.free_user = config.get('free_user')
        args.free_api_key = config.get('free_api_key')
        args.ics_url = config["ics_url"]
        args.ics_username = config.get("ics_username")
        args.ics_password = config.get("ics_password")
    return args


def main():
    args = parse_args()
    free_sms = FreeSMS(args.free_user, args.free_api_key)
    alarms = Alarms(
        ics_url=args.ics_url,
        ics_username=args.ics_username,
        ics_password=args.ics_password,
    )
    while True:
        alarms.refresh()
        current = alarms.next
        if current.ring_at > dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=2):
            print("Next alarm is far away", alarms.next.ring_at, alarms.next.event.summary)
            sleep(3600)
            continue
        if current.ring_at > dt.datetime.now(dt.timezone.utc):
            print("Next alarm is", alarms.next.ring_at, alarms.next.event.summary)
            sleep_duration = max(0, (alarms.next.ring_at - dt.datetime.now(dt.timezone.utc)).total_seconds())
            print(f"Sleeping {sleep_duration}s")
            sleep(sleep_duration)
            continue
        free_sms.send(str(current.event.begin) + " " + current.event.summary)
        alarms.ack(current)


if __name__ == "__main__":
    main()
