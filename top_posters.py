import re

def post_counts():
	# only includes posts with an email in header
	SENDER_REGEX = re.compile('From:\s*("?(?P<name>.*?)"?)\s*'
							  '(<?(?P<email>\S*@\S*?)>?)\s*\n')

	senders = {}
	with open('latest.mbox', 'r') as archive:
		with open('senders.txt', 'w') as outfile:
			for line in archive.readlines():
				result = SENDER_REGEX.match(line)
				if result:
					name = result.group('name')
					email = result.group('email')
					if not(name):
						name = email
					if senders.get(name):
						if email not in senders[name]['emails']:
							senders[name]['emails'].append(email)
						senders[name]['count'] += 1
					else:
						senders[name] = {'emails': [email], 'count': 1}
	return senders

def get_top(n):
	counts = sorted(post_counts().items(), key=lambda x: x[1]['count'], reverse=True)
	return counts[:n]