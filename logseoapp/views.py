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



def get_ranks(request, start_date="", end_date=""):
    """ get rank data for kws, defaults to entire data-set """

    if 'start_date' and 'end_date' in request.GET:
        start_date = request.GET['start_date']
        end_date   = request.GET['end_date']
    else:
        start_date = '2011-06-01'
        end_date   = '2011-07-31'

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



    #debug lines
    sql       = connection.queries
    #phrases = Kws.objects.filter(Q(phrase__startswith = 'nsac',tags__name__in=["branded"])).values()
    #pc = LogSeRank.objects.filter(engine_id__engine__contains='Google').select_related()  # -> WORKS


    return render_to_response('ranks.py', { 'sql':sql,'phrase_ip':phrase_ip,
                                               'start_date':start_date,'end_date':end_date,
                                               'ip_cnts':ip_count, 'dates':dates})

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

    landing_pages = LogSeRank.objects.values('page_id', 'page_id__page'). \
                                      filter(refdate__range=(start_date, end_date))

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


    #debug lines
    sql = connection.queries

    return render_to_response('landing_pages.py', { 'sql':sql,'start_date':start_date,'end_date':end_date,
                                                    'dates':dates, 'combo':combo})

def get_page(request, page):
    page_name = Page.objects.values('id','page').filter(pk = page)

    rankings  = LogSeRank.objects.values('position', 'refdate'). \
                                    filter(page_id = page, position__gt = 0). \
                                    order_by('refdate')

    kws       = LogSeRank.objects.values(  'phrase_id','phrase_id__phrase', 'position', 'refdate'). \
                                    filter(   page_id = page, position__gt = 0). \
                                    distinct(). \
                                    order_by('phrase_id__phrase','refdate')

    ip_cnt    = kws.annotate(num_ip=Count('ip', distinct = True))

    gcount    = kws.filter(engine_id__engine__contains = 'Google'). \
                                      annotate(num_google=Count('engine_id'))

    d = defaultdict(dict)
    for item in (kws,ip_cnt,gcount):
        for elem in item:
            d[elem['phrase_id']].update(elem)
    combo = d.values()


    """
    key = itemgetter('gender')
    iter = groupby(sorted(people, key=key), key=key)

    for gender, people in iter:
        print '===', gender, '==='
        for person in people:
            print person
    """
    #debug lines
    sql = connection.queries


    return render_to_response('page.py', { 'sql':sql,'page_name':page_name,'kws':kws,
                                            'rankings':rankings})

