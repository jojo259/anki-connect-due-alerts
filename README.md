# functionality

alerts the user on Discord when they have cards due on Anki

uses Python and interfaces with Anki using Anki-Connect

# setup

- install Anki-Connect as an addon to Anki: https://foosoft.net/projects/anki-connect/
- open Anki (Anki must be running for Anki-Connect to function)
- copy `.env.example` and rename the new file to `.env`
- fill in the variables in `.env`:
  - discordWebhookUrl: the URL of the Discord webhook which the program will send alerts to
  - loopIntervalMinutes: the interval (minutes) between each time the program will check if you have cards due
  - sendAlertMinIntervalMinutes: the minimum interval (minutes) between each time the program will alert if you have cards due (should always be equal to or greater than loop interval minutes)
  - userDiscordId: your Discord ID which the program will tag in the Discord alert
  - tagAtDueCountAbove: when the total number of due cards is greater than this, the program will alert you
  - monitorDeckNames: comma-separated (no space) list of deck names which this program will alert for; leave blank for all decks
- install required Python modules with `pip install -r requirements.txt`
- run `main.py` with Python
