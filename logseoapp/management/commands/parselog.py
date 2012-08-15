"""parses an apache access log file insert/update database

The search engine parsing is based on
http://search.cpan.org/~sden/URI-ParseSearchString-3.442/lib/URI/ParseSearchString.pm

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
import os
from cProfile import Profile
import pstats
from optparse import make_option
from django.core.management.base import BaseCommand #, CommandError
from logseoapp.models import LogSeRank, Engine, Kw, Page, Client
from datetime import datetime
#import glob
import urlparse
import re
import apachelog
import sys
import socket
import struct
import searchengines
import chardet
import logging

ROOT_PATH = os.path.dirname(__file__)

class Command(BaseCommand):
    #args = '<client_id >'
    #help = 'parses logfile for insert/update db'
    option_list = BaseCommand.option_list + (
    make_option('--profile',
        action='store_true',
        dest='profile',
        default=False,
        help='run profiler'),
        )


    def _handle(self, *args, **options):


        client_list,client_choice = client_choose()


        try:
            log_path_exists,client_id,client_name,log_path = client_search(client_choice,client_list)
            self.stdout.write(" you have a client id of %d and a client name of %s w log path %s" % (client_id,client_name,log_path))
            self.ready = raw_input("Ready to Start ? (yes/no) >> ")

            if self.ready == 'yes':
                self.stdout.write('yes you are ready....starting .... \n')

            else:
                self.stdout.write('ok, not ready \n')
                exit()

        except:
            client_add(client_choice)


        file_list = os.listdir(log_path)
        file_list.sort()

        for filename in file_list:

            dicts = parse_log(log_path + filename)
            parsed_list = []

            for d in dicts:

                log_phrase = d['phrase'].strip()
                encoding = chardet.detect(log_phrase)

                try:
                    encoding['encoding'] == 'ascii'
                    phrase_id      = check_phrase(log_phrase,d['refdate'],client_id)
                    engine_id      = check_engine(d['engine'])
                    page_id        = check_page(d['page'],client_id)
                    d['client_id'] = Client.objects.get(id=client_id)
                    d['phrase_id'] = Kw.objects.get(pk=phrase_id)
                    d['engine_id'] = Engine.objects.get(pk=engine_id)
                    d['page_id']   = Page.objects.get(pk=page_id)
                    parsed_list.append({'ip':d['ip'],
                                        'position':d['position'],
                                        'phrase_id':d['phrase_id'],
                                        'page_id':d['page_id'],
                                        'engine_id':d['engine_id'],
                                        'http':d['http'],
                                        'refdate':d['refdate'],
                                        'reftime':d['reftime'],
                                        'client_id':d['client_id']})

                except:
                    logging.basicConfig(filename='example.log',level=logging.INFO)
                    logging.info("Unable to parse %s" % d)
                    dicts.remove(d)


            print(" length of parsed list is %d" % len(parsed_list))
            my_objects = [LogSeRank(**vals) for vals in parsed_list]

            LogSeRank.objects.bulk_create(my_objects)

    def handle(self, *args, **options):
        """ method for profiling _handle
            python manage.py parselog --profile > parselog_stats.txt

        """

        if options['profile']:
            profiler = Profile()
            profiler.runcall(self._handle, *args, **options)

            stats = pstats.Stats(profiler)
            stats.strip_dirs().sort_stats('cumulative').print_stats()

        else:
            self._handle(*args, **options)

def client_choose():
    client_list = Client.objects.values('id','name')

    print('Select client name from the following clients:\n')

    for client in client_list:
        print(' "%d - name = %s"\n' % (client['id'],client['name']))

    client_choice = raw_input(">> ")

    return client_list,client_choice

def client_search(client, client_list):
    c_list = [element for element in client_list if element['name'] == client]

    if c_list:
        return check_log_path(c_list)
    else:
        return False

def client_add(client_choice):

    client_check = Client.objects.filter(name = client_choice)

    if client_check:
        print('We found your client, you probably need to add the path listed above')
        exit()

    else:
        print('Client not found, would you like to add this client?')


        add_client = raw_input("Add Client ? (yes/no) >> ")

        if add_client == 'yes':
            client_to_add = raw_input("What is the Client Name ? >> ")

            client_new = Client(name=client_to_add)
            client_new.save()
            x = Command()
            x._handle()

        else:
            print('will not add client, good bye \n')
            exit()

def check_log_path(c_list):
    client_id = c_list[0]['id']
    client_name = c_list[0]['name']
    log_path = ROOT_PATH + '/logs/' + client_name + '/'

    if os.path.lexists(log_path):
        log_path_exists = True
        return log_path_exists,client_id,client_name,log_path

    else:
        bad_path = True
        print('We did not find any log file in %s, pls add files then start over \n\n' % log_path)
        return bad_path


"""
 db functions
"""

def check_phrase(log_phrase,refdate,client_id):

    get_phrase = Kw.objects.values('id','phrase','last_seen').filter(phrase = log_phrase)

    #CHECK IF REFDATE > LAST_SEEN!!! Doh!
    if get_phrase.exists():

        Kw.objects.filter(phrase = log_phrase).update(last_seen = refdate)
        return get_phrase[0]['id']

    else:
        p = Kw(phrase = log_phrase, first_seen = refdate, last_seen = refdate, client_id = client_id)
        p.save()
        return p.id



def check_engine(log_engine):

    get_engine = Engine.objects.values('id','engine').filter(engine = log_engine)

    if get_engine.exists():
        return get_engine[0]['id']

    else:
        p = Engine(engine = log_engine)
        p.save()
        return p.id


def check_page(log_page, client_id):

    get_page = Page.objects.values('id','page').filter(page = log_page)

    if get_page.exists():
        return get_page[0]['id']

    else:
        p = Page(page = log_page, client_id = client_id)
        p.save()
        return p.id


"""
 parsing functions
"""
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
            logging.basicConfig(filename='example.log',level=logging.INFO)
            logging.info("Unable to parse %s" % line)
            sys.stderr.write("Unable to parse %s" % line)

    return update_list(log_list)

def update_list(log_list):
    """ remove from logfile dict stuff we don't want, add what we do want """

    for d in log_list:

        del d['%l'],d['%u'],d['%>s'],d['%b'],d['%{User-agent}i']

        try:
            d['http'] = d.pop('%{Referer}i')
            d['engine'],d['phrase'],d['position'] = get_name_query_rank(d)
            d['ip']   = d.pop('%h')
            d['ip']   = struct.unpack('>L',socket.inet_aton(d['ip']))[0]

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
        phrase = q_list[q]

    if 'cd' in q_list:
        position = int(q_list['cd'])

    else:
        position = 0

    return engine,phrase,position


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
