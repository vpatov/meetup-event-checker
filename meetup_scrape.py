from dataclasses import dataclass
import json
import requests
from dotenv import load_dotenv                                                                                                                                        
import os  

load_dotenv()

MY_NAME = os.getenv('MY_NAME')
MY_MEMBER_ID = os.getenv('MY_MEMBER_ID')

if MY_NAME is None or MY_MEMBER_ID is None:
    raise ValueError("MY_NAME and MY_MEMBER_ID must be set in the environment variables")

@dataclass
class MeetupEventRSVPInfo:
    count: int
    limit: int
    state: str

    def __str__(self):
        return (
            f"RSVPs: {self.count}, RSVP Limit: {self.limit}, RSVP State: {self.state}"
        )


def perform_meetup_request(payload: dict) -> dict:
    url = "https://www.meetup.com/gql2"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Accept": "*/*",
        "Accept-Language": "en-US",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/json",
        "Origin": "https://www.meetup.com",
        "Connection": "keep-alive",
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()




def am_i_going(event_id: str):
    payload = {
    "operationName": "getEventByIdForAttendees",
    "variables": {
        "eventId": event_id,
        "filter": {
            "rsvpStatus": [
                "YES",
                "ATTENDED"
            ]
        },
        "sort": {
            "sortField": "RSVP_ID",
            "sortOrder": "ASC"
        },
        "first": 50
    },
    "extensions": {
        "persistedQuery": {
            "version": 1,
            "sha256Hash": "9c61aaab3afd4f2aba0533bcd4c1d00e31613425f6cf2d9cfa109689da5ebedf"
        }
    }
    }

    response = perform_meetup_request(payload)
    attendees: list[dict] | None = (
        response.get('data',{})
        .get('event',{})
        .get('rsvps',{})
        .get('edges',None)
    )

    if attendees is None:
        raise Exception("could not find attendee info: " + json.dumps(response))
    
    if not isinstance(attendees, list):
        raise Exception("attendees is not a list: " + json.dumps(response))
    
    def is_me(edge: dict):
        member: dict = edge.get('node', {}).get('member', {})
        return member.get('name') == MY_NAME or member.get('id') == MY_MEMBER_ID

    found_me = any(filter(is_me, attendees))
    return found_me



def get_meetup_event_rsvp_info(event_id: str):
    payload = {
        "operationName": "getEventHomeClientOnly",
        "variables": {"eventId": event_id},
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "8d5f83748da7cad0f72dce06aa2131756f3eec8aa971180364b3d7102067644c",
            }
        },
    }
    response = perform_meetup_request(payload)
    event_venue_info: dict | None = (
        response.get("data", {})
        .get("event", {})
        .get("venues", [{}])[0]
        .get("eventVenueOptions")
    )
    if event_venue_info is None:
        raise Exception("could not find event venue info: " + json.dumps(response))
    rsvps = event_venue_info.get("goingCount")
    rsvp_limit = event_venue_info.get("rsvpLimit")
    rsvp_state = response.get("data", {}).get("event", {}).get("rsvpState")

    return MeetupEventRSVPInfo(count=rsvps, limit=rsvp_limit, state=rsvp_state)
