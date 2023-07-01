import requests
import os
import time

import dotenv
dotenv.load_dotenv()

loopIntervalMinutes = int(os.environ['loopIntervalMinutes'])
discordWebhookUrl = os.environ['discordWebhookUrl']
userDiscordId = os.environ['userDiscordId']
tagAtDueCountAbove = int(os.environ['tagAtDueCountAbove'])

serverUrl = 'http://localhost:8765'

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
	try:
		requests.post(discordWebhookUrl, json = data, headers = {'Content-Type': 'application/json'}, timeout = 30)
	except requests.exceptions.RequestException as e:
		print(f'send discord error: {e}')

def mainLoop():
	print('running main loop')
	logStr = ''
	dueData = getDueData()
	allDecksDueCount = 0
	for deckId, data in dueData.items():
		dueNew = data['new_count']
		dueLearning = data['learn_count']
		dueReview = data['review_count']
		dueTotal = dueNew + dueLearning + dueReview
		if dueTotal > 0:
			print(f'deck has {dueTotal} due')
			allDecksDueCount += dueTotal
			extraLog = data['name'] + '\n'
			dueTypes = {'NEW': dueNew, 'LEARNING': dueLearning, 'REVIEW': dueReview}
			for dueTypeName, dueCount in dueTypes.items():
				if dueCount > 0:
					extraLog += '    ' + dueTypeName + ': ' + str(dueCount) + '\n'
			logStr += extraLog
	print(f'total due count is {allDecksDueCount}')
	if allDecksDueCount > tagAtDueCountAbove:
		sendDiscord(f'```TOTAL DUE: {allDecksDueCount}\n{logStr}```<@{userDiscordId}>')

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
