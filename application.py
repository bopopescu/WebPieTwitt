import flask
from flask import Flask, jsonify, render_template, request

import json

# open stream for confirmation
import urllib

# boto SQS 
import boto.sqs
from boto.sqs.message import Message


application = Flask(__name__)

def readFromSQS(q):
	m = Message()
	m.message_attributes = {
		"geoLat": {
			"data_type": "String",
			"string_value": geoLat
		},
		"geoLong": {
			"data_type": "String",
			"string_value": geoLong
		},
		"sentimentStat": {
			"data_type": "String",
			"string_value": sentimentStat
		},
		"text": {
			"data_type": "String",
			"string_value": text
		}
	}
	m.set_body("Sugar rush.")
	q.write(m)

	return geoLat, geoLong, sentimentStat, text


# / is the home page of PieTwitt
@application.route('/')
def index():
	print "in index()"
	return flask.render_template('index.html')


# /map displays heatmap of all tweets
@application.route('/map')
def displayMap(keywords):
	allTweets = []
	return flask.render_template('map.html', keywords=keywords, allTweets = allTweets)

# /map displays heatmap of all tweets
@application.route('/map/<keywords>')
def displayMap(keywords):
	allTweets = []
	return flask.render_template('map.html', keywords=keywords, allTweets = allTweets)


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

        	if message:
        		# initiate worker pool right here
        		conn = boto.sqs.connect_to_region("us-east-1")
				q = conn.get_queue('kitkat_SQS')
				geoLat, geoLong, sentimentStat, text = readFromSQS(q)

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

