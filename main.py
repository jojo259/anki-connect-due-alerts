import requests
import os
import time

import dotenv
dotenv.load_dotenv()

sendAlertMinIntervalMinutes = int(os.environ['sendAlertMinIntervalMinutes'])
loopIntervalMinutes = int(os.environ['loopIntervalMinutes'])
discordWebhookUrl = os.environ['discordWebhookUrl']
iftttWebhookUrl = os.environ['iftttWebhookUrl']
userDiscordId = os.environ['userDiscordId']
tagAtDueCountAbove = int(os.environ['tagAtDueCountAbove'])
monitorDeckNames = os.environ['monitorDeckNames']

if monitorDeckNames == None or monitorDeckNames == '':
	monitorDeckNames = []
else:
	monitorDeckNames = monitorDeckNames.split(',')

serverUrl = 'http://localhost:8765'
lastSentAlert = 0

def getDeckNames():
	data = {
		'version': 4,
		'action': 'deckNames',
	}
	print('getting deck names')
	return requests.post(serverUrl, json = data).json()

def getDueData():
	data = {
		'version': 4,
		'action': 'getDeckStats',
		'params': {
			'decks': getDeckNames()
		},
	}
	print('getting due data')
	return requests.post(serverUrl, json = data).json()

def sendDiscord(toSend):
	print('sending to discord')
	data = {}
	data['username'] = 'anki'
	data['content'] = toSend
	requests.post(discordWebhookUrl, json = data, headers = {'Content-Type': 'application/json'}, timeout = 30)

def triggerIfttt():
	print('triggering ifttt')
	requests.post(iftttWebhookUrl, timeout = 30)

def mainLoop():
	print('running main loop')
	global lastSentAlert
	if time.time() - lastSentAlert < sendAlertMinIntervalMinutes * 60:
		print('sent alert too recently')
		return
	logStr = ''
	dueData = getDueData()
	allDecksDueCount = 0
	for deckId, data in dueData.items():
		deckName = data['name']
		if len(monitorDeckNames) > 0 and deckName not in monitorDeckNames:
			print(f'deck {deckName} is not being monitored')
			continue
		dueNew = data['new_count']
		dueLearning = data['learn_count']
		dueReview = data['review_count']
		dueTotal = dueNew + dueLearning + dueReview
		if dueTotal > 0:
			print(f'deck {deckName} has {dueTotal} due')
			allDecksDueCount += dueTotal
			extraLog = deckName + '\n'
			dueTypes = {'NEW': dueNew, 'LEARNING': dueLearning, 'REVIEW': dueReview}
			for dueTypeName, dueCount in dueTypes.items():
				if dueCount > 0:
					extraLog += '    ' + dueTypeName + ': ' + str(dueCount) + '\n'
			logStr += extraLog
	print(f'total due count is {allDecksDueCount}')
	if allDecksDueCount > tagAtDueCountAbove:
		try:
			sendDiscord(f'```TOTAL DUE: {allDecksDueCount}\n{logStr}```<@{userDiscordId}>')
		except requests.exceptions.RequestException as e:
			triggerIfttt()
	lastSentAlert = time.time()

def runLoop():
	print('starting main loop forever')
	while True:
		try:
			mainLoop()
		except Exception as e:
			print(f'ERROR: {e}')
		print(f'sleeping for {loopIntervalMinutes} minutes')
		time.sleep(loopIntervalMinutes * 60)

if __name__ == "__main__":
	runLoop()
