import flask
from flask import Flask, jsonify, render_template, request

import json
#import fetcher

# open stream for confirmation
import urllib

# boto SQS 
import boto.sqs
from boto.sqs.message import Message


application = Flask(__name__)

# global list 
resultsFromSQS = []

# / is the home page of PieTwitt
@application.route('/')
def index():
	print "Home sweet home."
	return flask.render_template('index.html')


# /map displays heatmap of all tweets
@application.route('/map/<keywords>')
def displayMap(keywords):
	# allTweets = []
	print "resultsFromSQS = ", resultsFromSQS

	return flask.render_template('map.html', keywords=keywords, allTweets = resultsFromSQS)


# SNS HTTP request endpoint: subscribe, unsubscribe, notification
@application.route('/kitkat', methods = ['POST', 'GET'])
def sns():
	headers = request.headers
	print "headers", headers
	print "request", request
	arn = headers.get('X-Amz-Sns-Topic-Arn')
	print "before request.data"
	obj = json.loads(request.data)
	if arn:
		snsType = headers.get('X-Amz-Sns-Message-Type')
		if snsType == 'SubscriptionConfirmation':
			subscribe_url = obj[u'SubscribeURL']

			f = urllib.urlopen(subscribe_url)
			myfile = f.read()
			print myfile

			return '', 200

		elif snsType == 'Notification':
			notification_id = obj[u'MessageId']
        	message = obj[u'Message']
        	print message

        	

        	conn = boto.sqs.connect_to_region("us-east-1")
        	q = conn.get_queue('kitkat_SQS')
        	print "made connection"

    		global resultsFromSQS
        	for i in range(3):
        		rs = q.get_messages(message_attributes=['text','sentimentStat','geoLat','geoLong'])
        		text = rs[0].message_attributes['text']['string_value']
        		geoLat = rs[0].message_attributes['geoLat']['string_value']
        		geoLong = rs[0].message_attributes['geoLong']['string_value']
        		sentimentStat = rs[0].message_attributes['sentimentStat']['string_value']

        		resultsFromSQS.append({
        			'text': text,
        			'geoLat': geoLat,
        			'geoLong': geoLong,
        			'sentimentStat': sentimentStat
        			})

    		return '', 200
	else:
		return '', 404



if __name__ == '__main__':
	try: 
		application.config["DEBUG"] = True
		application.run(host='0.0.0.0', port=9090)
		#application.run(host='199.58.86.213', port=5000)


	except:
		print "application.run failed"

