from __future__ import division
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from datetime import timedelta
# logseo utility functions
from utils.view import date_select, client_select, last_full_week
from utils.view import metrics_processing_row1, metrics_processing_row2
from utils.view import bigram_stats, process_time_series, get_datatables_records
from logseoapp.models import LogSeRank, Kw, Page, Client
from logseoapp.forms import ClientChoice
from django.db.models import Avg, Count, StdDev, Min, Max
from collections import defaultdict
from operator import itemgetter
import json
from django.db import connection


@login_required
def home(request, client_id=""):
    """ retrieve stats for home page,
    restricted to last full week (mon-sun) in our data-set """

    # client from form
    client_id = client_select(request.GET)

    form = ClientChoice(initial={'client_list': client_id})

    # client name
    client = Client.objects.values('name').filter(pk=client_id)

    # latest week in our db
    latest_sunday, week_ago = last_full_week(client_id)
    two_wks_ago    = latest_sunday - timedelta(days=13)

    # row 1 metrics
    metrics_row1 = [{'field':'ip', 'metric_name':'Organic Visitors'},
                    {'field':'engine_id', 'metric_name':'Search Engines'},
                    {'field':'page_id', 'metric_name':'Pages Visited'},
                    {'field':'phrase_id', 'metric_name':'Search Queries'}]
    metrics_row1_dict = metrics_processing_row1(metrics_row1, client_id)

    # row 2 metrics
    metrics_row2 = [{'engine':'', 'position':-1, 'metric_name':'New Queries'},  # all engines
                    {'engine':'Google', 'position':-1, 'metric_name':'New Google Queries'},
                    {'engine':'Google', 'position':0, 'metric_name':'New Google Ranked Queries'},
                    {'engine':'Bing', 'position':-1, 'metric_name':'New Bing Queries'}]
    metrics_row2_dict = metrics_processing_row2(metrics_row2, client_id)

    """
    missing kw data
    """
    last_week      = Kw.objects.values('id', 'phrase') \
                               .filter(last_seen__range=[week_ago, latest_sunday],
                                       client_id=client_id)

    last_week_cnt  = Kw.objects.filter(last_seen__range=[week_ago, latest_sunday],
                                       client_id=client_id).count()

    wk_bf_last     = Kw.objects.values('id', 'phrase') \
                               .filter(last_seen__range=[two_wks_ago, week_ago],
                                       client_id=client_id)

    wk_bf_last_cnt = Kw.objects.filter(last_seen__range=[two_wks_ago, week_ago],
                                       client_id=client_id) \
                               .count()

    # keep all in wk_bf_last if not in last_week
    unique         = [{'phrase':x['phrase'], 'phrase_id':x['id']}
                      for x in wk_bf_last
                      if x not in last_week]

    unique_cnt     = len(unique)

    """
    bigram data
    """
    bigram_this_wk = bigram_stats(LogSeRank.objects
                                           .values('phrase_id__phrase')
                                           .filter(refdate__range=[week_ago, latest_sunday],
                                                   client_id=client_id)
                                           .annotate(num_ips=Count('ip', distinct=True)))

    bigram_last_wk = bigram_stats(LogSeRank.objects
                                           .values('phrase_id__phrase')
                                           .filter(refdate__range=[two_wks_ago, week_ago],
                                                   client_id=client_id)
                                           .annotate(num_ips=Count('ip', distinct=True)))

    # subtract last weeks word cnt from this weeks word cnt to find diff
    bigram_diff    = {k: int(bigram_this_wk.get(k, 0)) - int(bigram_last_wk.get(k, 0))
                      for k in set(bigram_last_wk) | set(bigram_this_wk)}
    bigram_gainers = sorted(bigram_diff.items(), key=itemgetter(1), reverse=True)
    bigram_losers  = sorted(bigram_diff.items(), key=itemgetter(1), reverse=False)

    # landing pages
    pages_query = LogSeRank.objects \
                           .values('page_id', 'page_id__page') \
                           .annotate(num_ips=Count('ip', distinct=True)) \
                           .filter(client_id=client_id)\
                           .order_by('-num_ips').distinct()

    sql = connection.queries

    return render(request, 'dashboard/index.html', {'form': form,
                                                    'client_id': client_id,
                                                    'metrics_row1_dict': metrics_row1_dict,
                                                    'metrics_row2_dict': metrics_row2_dict,
                                                    'client': client,
                                                    'unique': unique,
                                                    'sql': sql,
                                                    'last_week': last_week,
                                                    'wk_bf_last': wk_bf_last,
                                                    'week_ago': week_ago,
                                                    'latest_date': latest_sunday,
                                                    'last_week_cnt': last_week_cnt,
                                                    'wk_bf_last_cnt': wk_bf_last_cnt,
                                                    'unique_cnt': unique_cnt,
                                                    'bigram_gainers': bigram_gainers,
                                                    'bigram_losers': bigram_losers,
                                                    'pages_query': pages_query})


def home_engine_detail(request, engine, client_id="", ranked=""):
    """ retrieve all search queries for a given search engine """

    # client from form
    client_id = client_select(request.GET)

    form = ClientChoice(initial={'client_list': client_id})

    # client name
    client = Client.objects.values('name').filter(pk=client_id)

    # latest week in our db
    latest_sunday, week_ago = last_full_week(client_id)

    # engine name from url

    if engine != 'all':
        metrics = [{'engine':engine, 'position':-1, 'metric_name':"New " + engine + " Queries"}]

    else:
        metrics = [{'engine':'', 'position':-1, 'metric_name':'New Queries'}]

    data = metrics_processing_row2(metrics, client_id)

    return render(request, 'dashboard/engine_detail.html', {'week_ago': week_ago,
                                                            'latest_date': latest_sunday,
                                                            'form': form,
                                                            'client': client,
                                                            'client_id': client_id,
                                                            'data': data})


def get_queries(request):
    """ get rank data for kws, default dates set in date_select() fx """

    """
    common code that needs to learn abotu DRY
    """
    # client from form
    client_id = client_select(request.GET)

    form = ClientChoice(initial={'client_list': client_id})

    # client name
    client = Client.objects.values('name').filter(pk=client_id)

    start_date, end_date, first_data_date, last_data_date = date_select(request.GET, client_id)

    """
    unique view code
    """

    """
    chart / time series data
    """
    all_phrase = LogSeRank.objects \
                          .values('id', 'phrase_id', 'refdate') \
                          .filter(client_id=client_id) \
                          .distinct()

    # make ranks negative so lower ranks show higher on the chart
    all_phrase = process_time_series(all_phrase, start_date, end_date)

    return render(request, 'queries.html', {'start_date': start_date,
                                            'end_date': end_date,
                                            'first_data_date': first_data_date,
                                            'last_data_date': last_data_date,
                                            'form': form,
                                            'client': client,
                                            'client_id': client_id,
                                            'all_phrase': all_phrase})


def get_queries_datatable(request):
    """ produces the datatable section of get_queries """

    """
    common code that needs to learn abotu DRY
    """
    # client from form
    client_id = client_select(request.GET)

    # client name

    start_date, end_date, first_data_date, last_data_date = date_select(request.GET, client_id)

    #prepare the params

    #initial querySet
    querySet = LogSeRank.objects \
                        .values('phrase_id', 'phrase_id__phrase') \
                        .filter(refdate__range=(start_date, end_date),
                                client_id=client_id) \
                        .annotate(num_ips=Count('ip', distinct=True),
                                  num_pages=Count('page_id', distinct=True),
                                  num_engines=Count('engine_id', distinct=True)) \
                        .order_by('phrase_id__phrase')

    #columnIndexNameMap is required for correct sorting behavior
    columnIndexNameMap = {0: 'phrase_id__phrase', 1: 'num_ips', 2: 'num_pages', 3: 'num_engines'}
    #path to template used to generate json (optional)
    jsonTemplatePath = 'queries_json.txt'

    #call to generic function from utils
    return get_datatables_records(request, querySet, columnIndexNameMap, jsonTemplatePath)


def get_ranks(request, page, start_date="", end_date=""):
    """ get rank data for kws, default dates set in date_select() fx """

    """
    common code that needs to learn abotu DRY
    """
    # client from form
    client_id = client_select(request.GET)

    form = ClientChoice(initial={'client_list': client_id})

    # client name
    client = Client.objects.values('name').filter(pk=client_id)

    start_date, end_date, first_data_date, last_data_date = date_select(request.GET, client_id)

    """
    unique view code
    """

    """
    chart / time series data
    """
    all_phrase = LogSeRank.objects \
                          .values('id', 'phrase_id', 'refdate') \
                          .filter(client_id=client_id) \
                          .distinct()

    rank_phrase = LogSeRank.objects \
                           .values('phrase_id', 'refdate') \
                           .filter(position__gt=0,
                                   client_id=client_id) \
                           .distinct()

    position_ts = LogSeRank.objects \
                           .values('position', 'refdate') \
                           .filter(position__gt=0,
                                   refdate__range=[start_date, end_date],
                                   client_id=client_id)

    position_chart = process_time_series(position_ts,
                                         start_date,
                                         end_date,
                                         'refdate',
                                         Avg('position'))

    largest_position = max(item['y'] for item in position_chart)

    # make ranks negative so lower ranks show higher on the chart
    #position_chart = [{"x":e['x'], "y":e['y'] * -1} for e in position_chart]
    all_phrase   = process_time_series(all_phrase, start_date, end_date)
    rankphrase_chart  = process_time_series(rank_phrase, start_date, end_date)

    return render(request, 'ranks.html', {'start_date': start_date,
                                          'end_date': end_date,
                                          'first_data_date': first_data_date,
                                          'last_data_date': last_data_date,
                                          'form': form,
                                          'client': client,
                                          'client_id': client_id,
                                          'largest_position': largest_position,
                                          'page': page,
                                          'id': id,
                                          'rankphrase_chart': rankphrase_chart,
                                          'all_phrase': all_phrase,
                                          'position_chart': position_chart})


def get_ranks_datatable(request, page):
    """ produces the datatable section of get_ranks """

    """
    common code that needs to learn abotu DRY
    """
    # client from form
    client_id = client_select(request.GET)

    # client name

    start_date, end_date, first_data_date, last_data_date = date_select(request.GET, client_id)

    #prepare the params

    if page == 'queries':
        id = 'phrase_id'
        value = 'phrase_id__phrase'

    else:
        id = 'page_id'
        value = 'page_id__page'

    # initial querySet
    # retrieves all search queries and visitors for which we have a rank in the given time-frame
    # does not retrieve a count of all visitors
    # who have come through the search query during the time-frame
    querySet = LogSeRank.objects \
                        .values(id, value) \
                        .filter(position__gt=0,
                                refdate__range=[start_date, end_date],
                                client_id=client_id) \
                        .annotate(num_ips=Count('ip', distinct=True),
                                  num_rank=Count('position'),
                                  avg_rank=Avg('position'),
                                  st_rank=StdDev('position'),
                                  min_rank=Min('position'),
                                  max_rank=Max('position')) \
                        .order_by(value)

    #columnIndexNameMap is required for correct sorting behavior
    columnIndexNameMap = {0: value,
                          1: 'engine_id',
                          2: 'num_ips',
                          3: 'num_rank',
                          4: 'avg_rank',
                          5: 'st_rank',
                          6: 'min_rank'}

    #path to template used to generate json (optional)
    jsonTemplatePath = 'ranks_json.txt'

    #call to generic function from utils
    return get_datatables_records(request, querySet, columnIndexNameMap, jsonTemplatePath)


def get_phrase(request, phrase):
    """ get data on a particular search query """

    """
    common code that needs to learn abotu DRY
    """
    # client from form
    client_id = client_select(request.GET)

    form = ClientChoice(initial={'client_list': client_id})

    # client name
    client = Client.objects.values('name').filter(pk=client_id)

    start_date, end_date, first_data_date, last_data_date = date_select(request.GET, client_id)

    """
    unique view code
    """
    phrase_name = Kw.objects.values('id', 'phrase', 'first_seen', 'last_seen').filter(pk=phrase)

    rank_ts = LogSeRank.objects \
                       .values('position', 'refdate') \
                       .filter(phrase_id=phrase,
                               position__gt=0,
                               refdate__range=[start_date, end_date]) \
                       .order_by('refdate')

    rankings_chart = process_time_series(rank_ts, start_date, end_date, 'refdate', Avg('position'))
    largest_position = max(item['y'] for item in rankings_chart)

    rankings = LogSeRank.objects \
                        .values('position') \
                        .filter(position__gt=0,
                                phrase_id=phrase,
                                refdate__range=[start_date, end_date]) \
                        .order_by('refdate')

    ip_ts = LogSeRank.objects \
                     .values('refdate', 'ip') \
                     .filter(phrase_id=phrase,
                             client_id=client_id,
                             refdate__range=[start_date, end_date]) \
                     .order_by('refdate')

    ip_chart = process_time_series(ip_ts, start_date, end_date, 'refdate',
                                   Count('ip', distinct=True))

    ip_chart = json.dumps(ip_chart, sort_keys=True)

    pages = LogSeRank.objects \
                     .values('page_id', 'page_id__page', 'position', 'refdate') \
                     .filter(phrase_id=phrase,
                             refdate__range=(start_date, end_date)) \
                     .order_by('page_id__page', 'refdate')

    # convert queryset to list and remove ranks of '0' for sparkline
    # NO - the reason i am not eliminating 0 rank from queryset is to get ALL the pages assoc with
    # a phrase, not just ranked, HOWEVER, I don't want to chart ranks of 0, so if a page has only
    # one appearance in the dictionary and a position of zero I want to keep it

    #pages = list(pages)
    #pages = [ e['position'] = 'na' for e in pages if e['position'] = 0 ]

    return render(request, 'phrase.html', {'start_date': start_date,
                                           'end_date': end_date,
                                           'first_data_date': first_data_date,
                                           'last_data_date': last_data_date,
                                           'form': form,
                                           'client': client,
                                           'client_id': client_id,
                                           'ip_chart': ip_chart,
                                           'phrase_name': phrase_name,
                                           'rankings': rankings,
                                           'rankings_chart': rankings_chart,
                                           'largest_position': largest_position,
                                           'pages': pages})


def get_landing_pages(request, start_date="", end_date=""):
    """ get landing pages data """

    """
    common code that needs to learn abotu DRY
    """
    # client from form
    client_id = client_select(request.GET)

    form = ClientChoice(initial={'client_list': client_id})

    # client name
    client = Client.objects.values('name').filter(pk=client_id)

    start_date, end_date, first_data_date, last_data_date = date_select(request.GET, client_id)

    """
    unique view code
    """

    landing_pages = LogSeRank.objects \
                             .values('page_id', 'page_id__page') \
                             .filter(refdate__range=[start_date, end_date],
                                     client_id=client_id) \
                             .distinct()

    gcount        = landing_pages.filter(engine_id__engine__contains='Google') \
                                 .annotate(num_google=Count('engine_id'))

    bing_cnt      = landing_pages.filter(engine_id__engine__contains='Bing') \
                                 .annotate(num_bing=Count('engine_id'))

    yahoo_cnt     = landing_pages.filter(engine_id__engine__contains='Yahoo') \
                                 .annotate(num_yahoo=Count('engine_id'))

    phrase_cnt    = landing_pages.annotate(num_phrase=Count('phrase_id', distinct=True))

    ip_cnt        = landing_pages.annotate(num_ip=Count('ip', distinct=True))

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

    t_series = process_time_series(landing_pages, start_date, end_date)
    t_series = json.dumps(t_series, sort_keys=True)

    return render(request, 'landing_pages.html', {'start_date': start_date,
                                                  'end_date': end_date,
                                                  'first_data_date': first_data_date,
                                                  'last_data_date': last_data_date,
                                                  'form': form,
                                                  'client': client,
                                                  'client_id': client_id,
                                                  'combo': combo,
                                                  't_series': t_series})


def get_page(request, page):
    """ get data for single landing page """

    """
    common code that needs to learn abotu DRY
    """
    # client from form
    client_id = client_select(request.GET)

    form = ClientChoice(initial={'client_list': client_id})

    # client name
    client = Client.objects.values('name').filter(pk=client_id)

    start_date, end_date, first_data_date, last_data_date = date_select(request.GET, client_id)

    """
    unique view code
    """

    page_name = Page.objects.values('id', 'page').filter(pk=page)

    rank_ts  = LogSeRank.objects \
                        .values('position', 'refdate') \
                        .filter(page_id=page,
                                position__gt=0,
                                refdate__range=[start_date, end_date]) \
                        .order_by('refdate')

    rankings_chart = process_time_series(rank_ts, start_date, end_date, 'refdate', Avg('position'))
    largest_position = max(item['y'] for item in rankings_chart)

    ip_ts = LogSeRank.objects \
                     .values('refdate') \
                     .filter(refdate__range=[start_date, end_date],
                             page_id=page,
                             client_id=client_id) \
                     .annotate(num_ips=Count('ip', distinct=True)) \
                     .order_by('refdate')

    ip_chart = process_time_series(ip_ts, start_date, end_date)

    ip_chart = json.dumps(ip_chart, sort_keys=True)

    kws       = LogSeRank.objects \
                         .values('phrase_id', 'phrase_id__phrase') \
                         .filter(page_id=page,
                                 refdate__range=(start_date, end_date)) \
                         .distinct() \
                         .order_by('phrase_id__phrase')

    ip_cnt    = kws.annotate(num_ip=Count('ip', distinct=True))

    gcount    = kws.filter(engine_id__engine__contains='Google') \
                   .annotate(num_google=Count('engine_id'))

    bing_cnt  = kws.filter(engine_id__engine__contains='Bing') \
                   .annotate(num_bing=Count('engine_id'))

    yahoo_cnt = kws.filter(engine_id__engine__contains='Yahoo') \
                   .annotate(num_yahoo=Count('engine_id'))

    d = defaultdict(dict)
    for item in (kws, ip_cnt, gcount, bing_cnt, yahoo_cnt):
        for elem in item:
            d[elem['phrase_id']].update(elem)
    combo = d.values()

    return render(request, 'page.html', {'start_date': start_date,
                                         'end_date': end_date,
                                         'first_data_date': first_data_date,
                                         'last_data_date': last_data_date,
                                         'form': form,
                                         'client': client,
                                         'client_id': client_id,
                                         'ip_chart': ip_chart,
                                         'rankings_chart': rankings_chart,
                                         'largest_position': largest_position,
                                         'page_name': page_name,
                                         'kws': combo})


def get_watchlist(request):
    """ get/create watchlist """

    return render(request, 'watchlist.html', {})
