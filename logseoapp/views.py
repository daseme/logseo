from __future__ import division
from django.views.generic import simple
from django.shortcuts import render_to_response
from logseoapp.models import LogSeRank, Engine, Kw, Page
from django.http import HttpResponse
from django.db.models import Avg, Count, StdDev
from django.db import connection
from collections import defaultdict
from operator import itemgetter
from itertools import groupby
from datetime import datetime
import time
import qsstats


def get_home(request):
    """ retrieve stats for home page """

    pass

def process_time_series(query, start_date, end_date):
    """ process qsstats object into json """

    qss = qsstats.QuerySetStats(query, 'refdate')
    start = datetime.strptime(start_date, '%Y-%m-%d').date()
    end   = datetime.strptime(end_date, '%Y-%m-%d').date()
    time_series = qss.time_series(start, end)
    # do some formatting cleanup of qsstats ->convert to epoch time (not dealing with local time!!)
    return [ {"x":time.mktime(e[0].timetuple()), "y":e[1]} for e in time_series ]



def get_ranks(request, start_date="", end_date=""):
    """ get rank data for kws, defaults to entire data-set """

    if 'start_date' and 'end_date' in request.GET:
        start_date = request.GET['start_date']
        end_date   = request.GET['end_date']
    else:
        start_date = '2011-06-01'
        end_date   = '2011-07-31'

    """
    datatable data
    """
    dates    = LogSeRank.objects.values('refdate').distinct()

    ip_count = LogSeRank.objects.values(  'phrase_id','phrase_id__phrase','phrase_id__tags__name'). \
                                 filter(   position__gt = 0,
                                           engine_id__engine__contains = 'Google',
                                           refdate__range=(start_date, end_date)). \
                                 annotate( num_ips=Count('ip', distinct = True),
                                           num_rank=Count('position'),
                                           avg_rank=Avg('position'),
                                           st_rank = StdDev('position'))[:4000] # FUCKING WORKS

    for dict in ip_count:
        num_ratio = dict['num_rank'] / dict['num_ips']
        dict['ratio'] = round(num_ratio, 2)

    phrase_ip = LogSeRank.objects.annotate(num_ips=Count('ip')).aggregate(Avg('num_ips'))

    """
    chart / time series data
    """
    all_phrase = LogSeRank.objects.values('id','phrase_id','refdate'). \
                                    distinct()

    rank_phrase = LogSeRank.objects.values('id','phrase_id','refdate'). \
                                    filter(   position__gt = 0).distinct()

    all_phrase = process_time_series(all_phrase,start_date,end_date)
    rank_phrase = process_time_series(rank_phrase,start_date,end_date)

    #debug lines
    sql       = connection.queries

    return render_to_response('ranks.py', { 'sql':sql,'phrase_ip':phrase_ip,
                                               'start_date':start_date,'end_date':end_date,
                                               'ip_cnts':ip_count, 'dates':dates,
                                               'rank_phrase':rank_phrase,'all_phrase':all_phrase})

def get_phrase(request, phrase):
    """ View all objects """
    phrase_name = Kw.objects.values('id','phrase').filter(pk = phrase)
    rankings    = LogSeRank.objects.values('position', 'refdate'). \
                                    filter(phrase_id = phrase, position__gt = 0). \
                                    order_by('refdate')
    pages       = LogSeRank.objects.values(  'page_id__page', 'position', 'refdate'). \
                                    filter(   phrase_id = phrase, position__gt = 0). \
                                    distinct(). \
                                    order_by('page_id__page','refdate')

    #debug lines
    sql = connection.queries


    return render_to_response('phrase.py', { 'phrase_name':phrase_name, 'rankings':rankings, 'pages':pages})


def get_landing_pages(request, start_date="", end_date=""):
    """ get landing pages data """

    if 'start_date' and 'end_date' in request.GET:
        start_date = request.GET['start_date']
        end_date   = request.GET['end_date']
    else:
        start_date = '2011-06-01'
        end_date   = '2011-07-31'

    dates         = LogSeRank.objects.values('refdate').distinct()

    landing_pages = LogSeRank.objects.values('page_id', 'page_id__page','refdate'). \
                                      filter(refdate__range=(start_date, end_date)). \
                                      distinct()

    gcount        = landing_pages.filter(engine_id__engine__contains = 'Google'). \
                                      annotate(num_google=Count('engine_id'))

    bing_cnt      = landing_pages.filter(engine_id__engine__contains = 'Bing'). \
                                      annotate(num_bing=Count('engine_id'))

    yahoo_cnt     = landing_pages.filter(engine_id__engine__contains = 'Yahoo'). \
                                      annotate(num_yahoo=Count('engine_id'))

    phrase_cnt    = landing_pages.annotate(num_phrase=Count('phrase_id', distinct = True))

    ip_cnt        = landing_pages.annotate(num_ip=Count('ip', distinct = True))


    # http://stackoverflow.com/questions/5501810/join-two-lists-of-dictionaries-on-a-single-key
    d = defaultdict(dict)
    for item in (landing_pages, gcount, bing_cnt, yahoo_cnt, phrase_cnt, ip_cnt):
        for elem in item:
            d[elem['page_id']].update(elem)
    combo = d.values()

    for d in combo:
        num_ratio = d['num_ip'] / d['num_phrase']
        d['ip_per_q'] = round(num_ratio, 2)

    """
    chart / time series data
    """

    t_series = process_time_series(landing_pages,start_date,end_date)

    #debug lines
    sql = connection.queries

    return render_to_response('landing_pages.py', { 'sql':sql,'start_date':start_date,'end_date':end_date,
                                                    'dates':dates, 'combo':combo,'t_series':t_series})

def get_page(request, page):
    page_name = Page.objects.values('id','page').filter(pk = page)

    rankings  = LogSeRank.objects.values('position', 'refdate'). \
                                    filter(page_id = page, position__gt = 0). \
                                    order_by('refdate')

    kws       = LogSeRank.objects.values('phrase_id','phrase_id__phrase'). \
                                    filter(   page_id = page). \
                                    distinct(). \
                                    order_by('phrase_id__phrase')

    ip_cnt    = kws.annotate(num_ip=Count('ip', distinct = True))

    gcount    = kws.filter(engine_id__engine__contains = 'Google'). \
                                      annotate(num_google=Count('engine_id'))

    bing_cnt  = kws.filter(engine_id__engine__contains = 'Bing'). \
                                      annotate(num_bing=Count('engine_id'))

    yahoo_cnt = kws.filter(engine_id__engine__contains = 'Yahoo'). \
                                      annotate(num_yahoo=Count('engine_id'))

    d = defaultdict(dict)
    for item in (kws,ip_cnt,gcount,bing_cnt,yahoo_cnt):
        for elem in item:
            d[elem['phrase_id']].update(elem)
    combo = d.values()

    #time_series = process_time_series(ip_cnt,start_date,end_date)
    #debug lines
    sql = connection.queries


    return render_to_response('page.py', { 'sql':sql,'page_name':page_name,'kws':combo,
        'rankings':rankings})

