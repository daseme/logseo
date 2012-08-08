from __future__ import division
#import numpy
import nltk
#from nltk import *
#from nltk.tokenize import *
from django.shortcuts import render
from logseoapp.models import LogSeRank, Kw, Page, Client
from django.db.models import Avg, Count, StdDev
from django.db import connection
from collections import defaultdict
from datetime import datetime, timedelta
import time
import qsstats
#import itertools
#import operator
from operator import itemgetter





def date_select(get_request):
    """ defaults to last month in our db, or uses date select forms """

    if 'start_date' and 'end_date' in get_request:
        start_date =  datetime.strptime(get_request['start_date'], '%Y-%m-%d').date()
        end_date   =  datetime.strptime(get_request['end_date'], '%Y-%m-%d').date()
        return start_date,end_date
    else:
        end_date = LogSeRank.objects.values('refdate').order_by('-refdate')[0]
        end_date = end_date['refdate'] # possible we don't have a full month here
        start_date = end_date.replace(day=01) # replace day part of end_date with 01
        return start_date,end_date

def last_full_week():
    """ get last full week, start date, end date, in our database """

    latest_sunday  = LogSeRank.objects.values('refdate').filter(refdate__week_day=1). \
                                     order_by('-refdate')[0]
    latest_sunday  = latest_sunday['refdate']

    week_ago       = latest_sunday - timedelta(days=6)
    return latest_sunday,week_ago


def process_time_series(query, start_date, end_date, date_field="refdate", agg_field="", agg_interval="weeks"):
    """ process qsstats object into json

    """

    qss = qsstats.QuerySetStats(query, date_field, agg_field)
    time_series = qss.time_series(start_date, end_date, agg_interval) # aggregate by weeks (default is days)

    # do some formatting cleanup of qsstats ->convert to epoch time (not dealing with local time!!)
    return [ {"x":time.mktime(e[0].timetuple()), "y":e[1]} for e in time_series ]

def bigram_stats(query):
    """ return ip-weighted bigram scores for this week last week
        accepts query like:
        LogSeRank.objects.values('phrase_id__phrase'). \
                          filter(refdate__range=[week_ago,now_date]). \
                          annotate(num_ips=Count('ip', distinct = True))
    """

    stop_words = nltk.corpus.stopwords.words('english') + [
    '.',
    ',',
    '--',
    '\'s',
    '?',
    ')',
    '(',
    ':',
    '\'',
    '\'re',
    '"',
    '-',
    '}',
    '{',
    ]

    # assign django query to var
    phrase_obj = query

    # create ip-weighted list of phrases
    # not the most efficient method
    phrase_list = [p['phrase_id__phrase'].lower()
                   for p in phrase_obj
                   for i in xrange(1,p['num_ips'])]

    # remove stop words
    phrase_list = [' '.join(w for w in phrase.split() if w.lower() not in stop_words)
                  for phrase in phrase_list]

    # tokenize phrases, creates list of lists
    tok_phrases = [nltk.tokenize.word_tokenize(p) for p in phrase_list]

    # generate bigrams
    bigram_phrases = [nltk.bigrams(p) for p in tok_phrases]

    # flatten list of lists, so we can score across the lists
    bigram_words = [item for sublist in bigram_phrases for item in sublist]

    bigram_scores = nltk.FreqDist(bigram_words)

    return dict(bigram_scores)

def home(request):
    """ retrieve stats for home page,
    restricted to last full week (mon-sun) in our data-set """

    # get the latest week in our db
    latest_sunday,week_ago = last_full_week()
    two_wks_ago    = latest_sunday - timedelta(days=13)

    """
    ips
    """
    ips_ts       = LogSeRank.objects.values('ip','refdate'). \
                                 filter(refdate__range=[week_ago,latest_sunday]). \
                                 distinct()
    ips_chart    = process_time_series(ips_ts, week_ago, latest_sunday,'refdate',Count('ip', distinct = True),'days')
    ips_cnt   = ips_ts.count()

    ips_last  = LogSeRank.objects.values('ip','refdate'). \
                                 filter(refdate__range=[two_wks_ago,week_ago]). \
                                 distinct()
    ips_last_cnt = ips_last.count()
    ip_diff = ips_cnt - ips_last_cnt

    """
    search engines
    """
    se_ts       = LogSeRank.objects.values('engine_id','refdate'). \
                                 filter(refdate__range=[week_ago,latest_sunday]). \
                                 distinct()
    se_chart       = process_time_series(se_ts, week_ago, latest_sunday,'refdate',Count('engine_id', distinct = True),'days')
    se_cnt      = se_ts.count()
    se_last     = LogSeRank.objects.values('engine_id','refdate'). \
                                 filter(refdate__range=[two_wks_ago,week_ago]). \
                                 distinct()
    se_last_cnt = se_last.count()
    se_diff     = se_cnt - se_last_cnt

    """
    landing pages
    """
    lp_ts       = LogSeRank.objects.values('page_id','refdate'). \
                                 filter(refdate__range=[week_ago,latest_sunday]). \
                                 distinct()
    lp_chart       = process_time_series(lp_ts, week_ago, latest_sunday,'refdate',Count('page_id', distinct = True),'days')
    lp_cnt      = lp_ts.count()
    lp_last     = LogSeRank.objects.values('page_id','refdate'). \
                                 filter(refdate__range=[two_wks_ago,week_ago]). \
                                 distinct()
    lp_last_cnt = lp_last.count()
    lp_diff     = lp_cnt - lp_last_cnt

    """
    new kw data
    """
    kw_new_table  = LogSeRank.objects.values('phrase_id','phrase_id__phrase','phrase_id__first_seen'). \
                                      annotate(num_ips=Count('ip', distinct = True)). \
                                      filter(phrase_id__first_seen__range=[week_ago,latest_sunday]) . \
                                      order_by('-num_ips')[:5]

    kw_new_cnt    = Kw.objects.filter(first_seen__range=[week_ago,latest_sunday]).count()
    kw_new_ts     = Kw.objects.values('first_seen','phrase')
    kw_new_chart = process_time_series(kw_new_ts,week_ago, latest_sunday,'first_seen',
                                         Count('id', distinct = True),'days')

    """
    new google kw data
    """
    kw_g_new     = LogSeRank.objects.values('phrase_id','phrase_id__phrase','phrase_id__first_seen'). \
                                   annotate(num_ips=Count('ip', distinct = True)). \
                                     filter(engine_id__engine__contains = 'Google',
                                            phrase_id__first_seen__range=[week_ago,latest_sunday]) . \
                                   order_by('-num_ips').distinct()
    kw_g_new_cnt = kw_g_new.count()

    kw_g_new_chart     = process_time_series(kw_g_new, week_ago, latest_sunday,'refdate',
                                             Count('phrase_id', distinct = True),'days')

    """
    new google ranked kw data
    """
    kw_gr_new     = LogSeRank.objects.values( 'phrase_id','phrase_id__phrase','phrase_id__first_seen'). \
                                    annotate(  num_ips=Count('ip', distinct = True)). \
                                      filter(  engine_id__engine__contains = 'Google',
                                               position__gt = 0,
                                               phrase_id__first_seen__range=[week_ago,latest_sunday]) . \
                                    order_by(  '-num_ips')
    kw_gr_new_cnt = kw_gr_new.count()

    kw_gr_new_chart     = process_time_series(kw_gr_new, week_ago, latest_sunday,'refdate',
                                             Count('phrase_id', distinct = True),'days')

    """
    new bing kw data
    """
    kw_b_new     = LogSeRank.objects.values('phrase_id','phrase_id__phrase','phrase_id__first_seen'). \
                                   annotate(num_ips=Count('ip', distinct = True)). \
                                     filter(engine_id__engine__contains = 'Bing',
                                            phrase_id__first_seen__range=[week_ago,latest_sunday]) . \
                                   order_by('-num_ips').distinct()
    kw_b_new_cnt = kw_b_new.count()

    kw_b_new_chart     = process_time_series(kw_b_new, week_ago, latest_sunday,'refdate',
                                             Count('phrase_id', distinct = True),'days')

    """
    missing kw data
    """
    last_week      = Kw.objects.values('id','phrase').filter(last_seen__range=[week_ago,latest_sunday])
    last_week_cnt  = Kw.objects.filter(last_seen__range=[week_ago,latest_sunday]).count()
    wk_bf_last     = Kw.objects.values('id','phrase').filter(last_seen__range=[two_wks_ago,week_ago])
    wk_bf_last_cnt = Kw.objects.filter(last_seen__range=[two_wks_ago,week_ago]).count()

    # keep all in wk_bf_last if not in last_week
    unique         = [{'phrase':x['phrase'],'phrase_id':x['id']} for x in wk_bf_last if x not in last_week]
    unique_cnt     = len(unique)

    """
    bigram data
    """
    bigram_this_wk = bigram_stats(LogSeRank.objects.values('phrase_id__phrase'). \
                                               filter(refdate__range=[week_ago,latest_sunday]). \
                                               annotate(num_ips=Count('ip', distinct = True)))
    bigram_last_wk = bigram_stats(LogSeRank.objects.values('phrase_id__phrase'). \
                                               filter(refdate__range=[two_wks_ago,week_ago]). \
                                               annotate(num_ips=Count('ip', distinct = True)))

    # subtract last weeks word cnt from this weeks word cnt to find diff
    bigram_diff    = { k:int(bigram_this_wk.get(k,0)) - int(bigram_last_wk.get(k,0))
                      for k in set(bigram_last_wk) | set(bigram_this_wk) }
    bigram_gainers = sorted(bigram_diff.items(), key=itemgetter(1), reverse=True)
    bigram_losers  = sorted(bigram_diff.items(), key=itemgetter(1), reverse=False)


    #debug lines
    sql             = connection.queries


    return render(request,'index.html', { 'sql':sql, 'kw_new_table':kw_new_table, 'kw_new_cnt':kw_new_cnt,'unique':unique,
                                          'last_week':last_week,'wk_bf_last':wk_bf_last,'week_ago':week_ago,
                                          'latest_date':latest_sunday,'ips_chart':ips_chart,'ips_cnt':ips_cnt,
                                          'se_chart':se_chart,'se_cnt':se_cnt,'ip_diff':ip_diff,'se_diff':se_diff,
                                          'kw_new_chart':kw_new_chart,'last_week_cnt':last_week_cnt,
                                          'lp_chart':lp_chart,'lp_diff':lp_diff,'lp_cnt':lp_cnt,
                                          'kw_g_new':kw_g_new,'kw_g_new_cnt':kw_g_new_cnt, 'kw_g_new_chart':kw_g_new_chart,
                                          'kw_gr_new':kw_gr_new,'kw_gr_new_cnt':kw_gr_new_cnt,
                                          'kw_gr_new_chart':kw_gr_new_chart,
                                          'kw_b_new':kw_b_new,'kw_b_new_cnt':kw_b_new_cnt,
                                          'kw_b_new_chart':kw_b_new_chart,
                                          'wk_bf_last_cnt':wk_bf_last_cnt,'unique_cnt':unique_cnt,
                                          'bigram_gainers':bigram_gainers,'bigram_losers':bigram_losers })


def get_ranks(request=None, start_date="", end_date=""):
    """ get rank data for kws, default dates set in date_select() fx """

    start_date,end_date = date_select(request.GET)
    dates    = LogSeRank.objects.values('refdate').distinct()

    """
    datatable data
    """


    ip_count = LogSeRank.objects.values(  'phrase_id','phrase_id__phrase'). \
                                 filter(   position__gt = 0,
                                           engine_id__engine__contains = 'Google',
                                           refdate__range=(start_date, end_date)). \
                                 annotate( num_ips=Count('ip', distinct = True),
                                           num_rank=Count('position'),
                                           avg_rank=Avg('position'),
                                           st_rank = StdDev('position')). \
                                 order_by('phrase_id__phrase') # FUCKING WORKS


    for dict in ip_count:
        num_ratio = dict['num_rank'] / dict['num_ips']
        dict['ratio'] = round(num_ratio, 2)

    phrase_ip   = LogSeRank.objects.annotate(num_ips=Count('ip')).aggregate(Avg('num_ips'))

    """
    chart / time series data
    """
    all_phrase    = LogSeRank.objects.values('id','phrase_id','refdate').distinct()

    rank_phrase   = LogSeRank.objects.values('phrase_id','refdate').filter(position__gt = 0).distinct()

    ranks_ts  = LogSeRank.objects.values('position','refdate'). \
                                  filter(position__gt = 0, refdate__range=[start_date,end_date])

    avg_position = process_time_series(ranks_ts,start_date,end_date,'refdate',Avg('position'))
    # make ranks negative so lower ranks show higher on the chart
    avg_position = [ {"x":e['x'], "y":e['y']*-1} for e in avg_position ]
    all_phrase   = process_time_series(all_phrase,start_date,end_date)
    rank_phrase  = process_time_series(rank_phrase,start_date,end_date)



    #debug lines
    sql       = connection.queries

    return render(request,'ranks.html', { 'sql':sql,'phrase_ip':phrase_ip,
                                               'start_date':start_date,'end_date':end_date,
                                               'ip_cnts':ip_count, 'dates':dates,
                                               'rank_phrase':rank_phrase,'all_phrase':all_phrase,
                                               'avg_position':avg_position})

def get_phrase(request, phrase):
    """ get data on a particular kw query

    """

    start_date,end_date = date_select(request.GET)
    dates    = LogSeRank.objects.values('refdate').distinct()


    phrase_name = Kw.objects.values('id','phrase').filter(pk = phrase)

    ranking_ts    = LogSeRank.objects.values('position', 'refdate'). \
                                    filter(position__gt = 0,
                                           phrase_id = phrase,
                                           refdate__range=(start_date, end_date)). \
                                    order_by('refdate')
    rankings   = process_time_series(ranking_ts,start_date,end_date,'refdate',Avg('position'))

    pages       = LogSeRank.objects.values('page_id__page', 'position', 'refdate'). \
                                    filter(position__gt = 0,
                                           phrase_id = phrase,
                                           refdate__range=(start_date, end_date)). \
                                    distinct(). \
                                    order_by('page_id__page','refdate')

    #debug lines
    #sql = connection.queries


    return render(request,'phrase.html', { 'dates':dates, 'start_date':start_date,'end_date':end_date,'phrase_name':phrase_name, 'rankings':rankings, 'pages':pages})



def get_landing_pages(request, start_date="", end_date=""):
    """ get landing pages data """

    start_date,end_date = date_select(request.GET)

    dates         = LogSeRank.objects.values('refdate').distinct()

    landing_pages = LogSeRank.objects.values('page_id', 'page_id__page'). \
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

    return render(request,'landing_pages.html', { 'sql':sql,'start_date':start_date,'end_date':end_date,
                                                    'dates':dates, 'combo':combo,'t_series':t_series})

def get_page(request, page):
    """ get specific page data """

    start_date,end_date = date_select(request.GET)

    dates         = LogSeRank.objects.values('refdate').distinct()

    page_name = Page.objects.values('id','page').filter(pk = page)

    rankings  = LogSeRank.objects.values('position', 'refdate'). \
                                    filter(page_id = page, position__gt = 0,refdate__range=(start_date, end_date)). \
                                    order_by('refdate')

    kws       = LogSeRank.objects.values('phrase_id','phrase_id__phrase'). \
                                    filter(page_id = page, refdate__range=(start_date, end_date)). \
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


    return render(request, 'page.html', { 'sql':sql,'dates':dates, 'start_date':start_date,'end_date':end_date, 'page_name':page_name,'kws':combo,
        'rankings':rankings})

