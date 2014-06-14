from dateutil.parser import parse
from datetime import datetime
import re

def post_counts(start_date, end_date):
    # only includes posts with an email in header
    EMPTY_REGEX = re.compile('^\n$')
    SENDER_REGEX = re.compile('^From:\s*("?(?P<name>.*?)"?)\s*'
                              '(<?(?P<email>\S*@\S*?)>?)\s*\n$')
    DATE_REGEX = re.compile('^X-List-Received-Date:\s*(?P<date>.*\d+:\d+:\d+)\s+.*')

    senders = {}
    with open('latest.mbox', 'r') as archive:
        with open('post_counts.txt', 'w') as outfile:
            cur_sender = None
            cur_date = None
            for line in archive.readlines():
                parsed_sender = SENDER_REGEX.match(line)
                if parsed_sender:
                    cur_sender = parsed_sender
                else:
                    parsed_date = DATE_REGEX.match(line)
                    if parsed_date:
                        try:
                            cur_date = parse(parsed_date.group('date'))
                        except ValueError:
                            print parsed_date.group('date')
                    elif EMPTY_REGEX.match(line):
                        if cur_sender and cur_date and start_date < cur_date < end_date:
                            name = cur_sender.group('name')
                            email = cur_sender.group('email')
                            if not name:
                                name = email
                            if senders.get(name):
                                if email not in senders[name]['emails']:
                                    senders[name]['emails'].append(email)
                                senders[name]['count'] += 1
                            else:
                                senders[name] = {'emails': [email], 'count': 1}
                            cur_sender = None
                            cur_date = None
    return senders

def get_top(start_date=datetime.min, end_date=datetime.now(), n=None):
    counts = post_counts(start_date, end_date)
    counts = sorted(counts.items(), key=lambda x: x[1]['count'], reverse=True)
    return counts[:n]