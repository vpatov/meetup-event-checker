# Meetup Bot

There are some events (mostly soccer games) that I like to regularly attend, that do _not_ allow members to join the waitlist when the event is full. This is because, purportedly, when people get on the RSVPs from the waitlist, they forget that they were on the waitlist, and thus don't know that they are now marked as attending, and then end up not showing up to the game. I would _never_ forget, but whatever (¬_¬).

Some hosts go as far as removing people from the waitlist (because they can't disable the feature altogether on MeetUp), and will remove you from the attendees marked as going if you _do_ get in off the waitlist. (╯°□°）╯︵ ┻━┻ 

Anyway, thankfully Meetup has a pretty straightforward GQL API. I didn't bother reading their docs (which I now realize are marking this API as deprecated (⊙_☉)), and just figured out the queries I need to send my inspecting the queries made by the browser when using meetup.com. Here's a script that will:
* poll the rsvps status and list of attendees for the desired meetup event
* if there are no available spots, do nothing, sleep for 3 minutes
* if there is a spot available, send a text message with link to meetup event, such that you can immediately RSVP (best next thing after waitlist)
* if there is a spot available but it sees that you are already going (presumably because you signed up after receiving the previous text), exit the script
* if the event is over or RSVPs have closed, exit the script

Thankfully, all the necessary pieces of the meetup API are unauthenticated. One day if I feel like it, I'll figure out a good way to authentication to this and then the script can just auto-rsvp on your behalf. I like the text message though, because I don't mind having the option of making a last-minute decision for signing up.

To use:
1. You will need a twillio account in order to send text messages.
2. Populate the necessary environment variables in a local .env file (refer to .env.sample to see what you need)
3. Call the script with your meetup event URL (will probably need to use a web browser to get the URL):

```bash
python bot.py <meetup_url> [<event_id>]
```

e.g.
```bash
python ./bot.py https://www.meetup.com/bushwick-inlet-brooklyn-coed-soccer-meetup/events/307025415
```

Make sure you don't include any query params, because the script gets the event ID from the last part of the URL. If for whatever reason the event ID is not the last part of your URL, or you can't be bothered to remove query params, you can also just include the event ID after the URL, e.g.

```bash
python ./bot.py https://www.meetup.com/bushwick-inlet-brooklyn-coed-soccer-meetup/events/307025415?abc=def 307025415
```