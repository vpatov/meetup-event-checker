import requests
import time
import requests
import sys
from datetime import datetime
from meetup_scrape import MeetupEventRSVPInfo, am_i_going, get_meetup_event_rsvp_info
from colorama.ansi import Fore as C
import traceback
from dotenv import load_dotenv                                                                                                                                        
import os  

load_dotenv()

# Constants
TWILLIO_ACCOUNT_SID = os.getenv('TWILLIO_ACCOUNT_SID')
TWILLIO_TOKEN = os.getenv('TWILLIO_TOKEN')
TWILLIO_PHONE_TO = os.getenv('TWILLIO_PHONE_TO')
TWILLIO_PHONE_FROM = os.getenv('TWILLIO_PHONE_FROM')

if not TWILLIO_ACCOUNT_SID or not TWILLIO_TOKEN or not TWILLIO_PHONE_TO or not TWILLIO_PHONE_FROM:
    print("Please set TWILLIO_ACCOUNT_SID, TWILLIO_TOKEN, TWILLIO_PHONE_TO, and TWILLIO_PHONE_FROM in your environment variables.")
    sys.exit(1)

try:
    MEETUP_URL = sys.argv[1]
    if len(sys.argv) == 3:
        EVENT_ID = sys.argv[2]
    else:
        parts = [p for p in MEETUP_URL.split("/") if p]
        EVENT_ID = parts[-1]
        if not EVENT_ID.isdigit():
            raise ValueError(f"Invalid event ID: {EVENT_ID}")
except Exception as e:
    print(e)
    print("Usage: python send_text.py <meetup_url> <event_id>")
    sys.exit(1)


def send_sms(body: str) -> None:
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILLIO_ACCOUNT_SID}/Messages.json"
    payload = {"To": TWILLIO_PHONE_TO, "From": TWILLIO_PHONE_FROM, "Body": body}

    response = requests.post(url, data=payload, auth=(TWILLIO_ACCOUNT_SID, TWILLIO_TOKEN))
    response.raise_for_status()
    print("SMS sent successfully")


def make_rsvp_sms_body(count, limit):
    return f"rsvps: {count}, limit: {limit}\ngo get em you dirty dog\ncheck meetup {MEETUP_URL}"

def make_event_over_sms_body():
    return f"Event is over, and/or RSVPs are closed. Shutting down bot. {MEETUP_URL}"

def main():
    """
    Main monitoring loop that checks RSVP count and sends SMS if count changes
    """
    polls = 0
    retry_interval_sec = 60
    consecutive_messages_sent = 0
    while True:
        try:
            if am_i_going(EVENT_ID):
                print(C.LIGHTCYAN_EX + "You are already going to this event! Exiting script" + C.RESET)
                exit(0)

            rsvp_info: MeetupEventRSVPInfo = get_meetup_event_rsvp_info(EVENT_ID)

            polls += 1

            if rsvp_info.state == "PAST":
                print(C.RED + "Event is over" + C.RESET)
                sms_body = make_event_over_sms_body()
                send_sms(sms_body)
                exit(0)

            if rsvp_info.count < rsvp_info.limit:
                print(C.BLUE + datetime.now().isoformat() + C.RESET)
                print(C.GREEN + "Found a spot!!" + C.RESET)
                if consecutive_messages_sent < 4:
                    retry_interval_sec += 120
                    sms_body = make_rsvp_sms_body(rsvp_info.count, rsvp_info.limit)
                    send_sms(sms_body)
                    consecutive_messages_sent += 1
                else:
                    print("Too many messages sent, waiting for a while")
            else:
                print(C.BLUE + datetime.now().isoformat() + C.RESET)
                print(
                    f"Event is full - total_spots: "
                    + f"{C.YELLOW + str(rsvp_info.limit) + C.RESET}, rsvps: {C.RED + str(rsvp_info.count) + C.RESET}"
                )
                print(
                    f"Performed {polls} poll(s). Trying again in {retry_interval_sec} seconds..."
                )
                retry_interval_sec = 60
                consecutive_messages_sent = 0

        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
            # print exception traceback

        print(C.LIGHTYELLOW_EX + "sleeping for " + str(retry_interval_sec) + " seconds..." + C.RESET)
        time.sleep(retry_interval_sec)


if __name__ == "__main__":
    main()
