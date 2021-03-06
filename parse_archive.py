from dateutil.parser import parse
from datetime import datetime
import re
import sqlite3

def post_counts(start_date, end_date):
    # only includes posts with an email in header
    EMPTY_REGEX = re.compile('^\n$')
    SENDER_REGEX = re.compile('^From:\s*("?(?P<name>.*?)"?)\s*'
                              '(<?(?P<email>\S*@\S*?)>?)\s*\n$')
    DATE_REGEX = re.compile('^X-List-Received-Date:\s*(?P<date>.*\d+:\d+:\d+)\s+.*')

    senders = {}
    with open('latest.mbox', 'r') as archive:
        cur_sender = None
        cur_date = None
        for line in archive.xreadlines():
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

def update_counts():
    db = sqlite3.connect('top_posters.db')
    db.row_factory = sqlite3.Row
    with db:
        with open('schema.sql') as f:
            db.cursor().executescript(f.read())

        cur_date = datetime.now()
        month_start = datetime(cur_date.year, cur_date.month, 1)
        if cur_date.month < 9:
            semester_start = datetime(cur_date.year, 1, 20)
            year_start = datetime(cur_date.year - 1, 8, 20)
        else:
            semester_start = datetime(cur_date.year, 8, 20)
            year_start = datetime(cur_date.year, 8, 20)

        date_ranges = [
                        ('month', month_start),
                        ('semester', semester_start),
                        ('year', year_start),
                        ('all_time', datetime.min),
                      ]

        for table_name, start_date in date_ranges:
            for poster in get_top(start_date=start_date, n=50):
                poster_data = (poster[0], poster[1]['count'])
                query = 'insert into ' + table_name + ' values (null, ?, ?)'
                db.execute(query, poster_data)

if __name__ == '__main__':
    update_counts()

