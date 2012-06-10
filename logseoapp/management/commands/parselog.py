"""parses an apache access log file for database consumption.

The return dictionary from the parse function;

    {
    'engine': 'Google',
    'http': 'http://google.com/search?q=search+string',
    'ip': '212.74.15.68',
    'rank': '5', # if 0 this means no rank was parsed
    'reftime': '21:56:32',
    'phrase': 'search string',
    'refdate': '2011-05-01',
    'page': '/blog/index.html',
    }

  parse_log(): takes logfile as a parameter, parses it, calls update_list()
  update_list(): removes unneeded dict values, and calls the following functions;
    get_name_query_rank(): get search engine name, query, rank (if present else 0)
    get_date_format(): splits apache date into date and time and reformats for our db
    get_request_path(): pull the requested path from %r apache field

"""
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from logseoapp.models import LogSeRank, Engine, Kw, Page
from datetime import datetime
import glob
import urllib
import urlparse
import re
import apachelog
import sys
import searchengines

#filename = 'access.20110501'
class Command(BaseCommand):
    args = '<logfile logfile ...>'
    help = 'parses logfile for insert/update db'


    def handle(self, *args, **options):
        self.dicts = ""
        for filename in glob.glob('/home/kurt/websites/logseo/logseoapp/management/commands/access.*'):
            self.dicts = parse_log(filename)

        for d in self.dicts:

            print d
            print "\n"


def parse_log(filename):
    """ parse log file for database """
    # log format = r'%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"'

    p = apachelog.parser(apachelog.formats['extended'])
    log_list = []

    for line in open(filename):
        try:
            data = p.parse(line)
            log_list.append(data)
        except:
            sys.stderr.write("Unable to parse %s" % line)

    return update_list(log_list)

def update_list(log_list):
    """ remove from logfile dict stuff we don't want, add what we do want """

    for d in log_list:

        del d['%l'],d['%u'],d['%>s'],d['%b'],d['%{User-agent}i']
        d['ip']   = d.pop('%h')
        d['http'] = d.pop('%{Referer}i')

        try:
            d['engine'],d['phrase'],d['rank'] = get_name_query_rank(d)
        except:
            pass

    new_log_list = [d for d in log_list if d.get('engine') and d.get('phrase')]

    for d in new_log_list: #2nd for loop so we work on smaller list

        try:
            d['refdate'],d['reftime'] = get_date_format(d)
            d['page'] =  get_request_path(d)

            del d['%t'],d['%r']
        except:
            pass

    #[record.update({'page': get_request_path(d)}) for record in log_list]

    return new_log_list

def get_name_query_rank(log_dict):
    """ parse (%{Referer}i) for search engine name, querystring, rank """

    o = urlparse.urlparse(log_dict['http'])
    domain_s = o.netloc.split(".")

    if "www" in o.netloc:
        domain = '.'.join(domain_s[1:])

    else:
        domain = '.'.join(domain_s[0:])

    q = searchengines.SE_LOOKUPS[domain]['q']
    q_list = dict(urlparse.parse_qsl(o.query))

    if domain in searchengines.SE_LOOKUPS and q in q_list:
        engine = searchengines.SE_LOOKUPS[domain]['name']
        phrase =q_list[q]

    if 'cd' in q_list:
        rank = q_list['cd']
    else:
        rank = 0

    return engine,phrase,rank

def get_date_format(log_dict):
    """ parse apache logline (%t) """
    date_pattern = re.compile(r'\d{2}\/\w{3}\/\d{4}:\d{2}:\d{2}:\d{2}')

    for match in date_pattern.findall(log_dict['%t']):

        try:
            df = datetime.strptime(match, '%d/%b/%Y:%H:%M:%S')
            date_format = df.strftime('%Y-%m-%d')
            time_format = df.strftime('%H:%M:%S')

        except ValueError:
            pass # ignore, this isn't a date

    return date_format, time_format


def get_request_path(log_dict):
    """ parse apache logline (%r) """

    path_pattern = re.compile(r'\/.*\s')

    for match in path_pattern.findall(log_dict['%r']):

        try:
            page = match.strip()

        except ValueError:
            pass # ignore

    return page
