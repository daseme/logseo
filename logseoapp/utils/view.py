from __future__ import division
import nltk
from logseoapp.models import LogSeRank
from django.db.models import Count
from datetime import datetime, timedelta
import time
import qsstats

# for datatables fx
from django.db.models import Q
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils.cache import add_never_cache_headers
import json



def date_select(get_request,client_id):
    """ defaults to last week available for a client using last_full_week(),
    or uses date select forms """

    first_data_date = LogSeRank.objects.values('refdate'). \
                                     filter(client_id=client_id). \
                                     order_by('refdate')[0]
    first_data_date = first_data_date['refdate']

    last_data_date = LogSeRank.objects.values('refdate'). \
                                     filter(client_id=client_id). \
                                     order_by('-refdate')[0]
    last_data_date = last_data_date['refdate'] # possible we don't have a full month here



    if 'start_date' and 'end_date' in get_request:
        start_date =  datetime.strptime(get_request['start_date'], '%Y-%m-%d').date()
        end_date   =  datetime.strptime(get_request['end_date'], '%Y-%m-%d').date()

        #handle the case where one client has a different date range than another client
        if end_date <= last_data_date and start_date >= first_data_date:
            return start_date,end_date,last_data_date

        else:
            end_date,start_date = last_full_week(client_id)
            return start_date,end_date,last_data_date

    else:
        end_date,start_date = last_full_week(client_id)
        return start_date,end_date,last_data_date


def client_select(get_request):
    """ defaults to client_id = 1, or uses client select form """

    if 'client_list' in get_request:
        client_id =  get_request['client_list']
        return client_id
    else:
        client_id = 1
        return client_id

def last_full_week(client_id):
    """ get last full week, start date, end date, in our database """

    latest_sunday  = LogSeRank.objects.values(  'refdate'). \
                                       filter(  refdate__week_day=1,
                                                client_id=client_id). \
                                       order_by('-refdate')[0]
    latest_sunday  = latest_sunday['refdate']

    week_ago       = latest_sunday - timedelta(days=6)
    return latest_sunday,week_ago


def process_time_series(query, start_date, end_date, date_field="refdate", agg_field="", agg_interval="days"):
    """ process qsstats object into json

    """

    qss = qsstats.QuerySetStats(query, date_field, agg_field)
    time_series = qss.time_series(start_date, end_date, agg_interval) # e.g., days,weeks (default is days)

    # do some formatting cleanup of qsstats ->convert to epoch time (not dealing with local time!!)
    # note *1000 for consumption by javascript
    # note hacky +14400 so we don't get one day off errors.  needs fixing!!
    return [ {"x":(time.mktime(e[0].timetuple())+14400)*1000, "y":e[1]} for e in time_series ]

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

def metrics_processing_row1(metrics_list,client_id):
    """ processes row 1 metrics for dashboard """

    # get the latest week in our db
    latest_sunday,week_ago = last_full_week(client_id)
    two_wks_ago    = latest_sunday - timedelta(days=13)

    metric_LOD = []

    for metric in metrics_list:
        metric_d = {}
        metric_d['metric_name'] = metric['metric_name']
        query = LogSeRank.objects.values(metric['field'],'refdate'). \
                                 filter(refdate__range=[week_ago,latest_sunday],
                                        client_id=client_id).distinct()
        metric_d['query_cnt'] = query.count()
        metric_d['chart'] = process_time_series(query, week_ago, latest_sunday,'refdate',
                                                Count(metric['field'], distinct = True),'days')
        query_last = LogSeRank.objects.values(metric['field'],'refdate'). \
                                 filter(refdate__range=[two_wks_ago,week_ago],
                                        client_id=client_id).distinct()
        last_cnt = query_last.count()
        metric_d['diff'] = metric_d['query_cnt'] - last_cnt

        metric_LOD.append(metric_d)

    return sorted(metric_LOD, key=lambda x: x['metric_name'])


def metrics_processing_row2(engine_list,client_id):
    """ processes row 2 metrics for dashboard
        engine specific metrics
    """

    # get the latest week in our db
    latest_sunday,week_ago = last_full_week(client_id)


    metric_LOD = []

    for engine in engine_list:
        metric_d = {}
        metric_d['metric_name'] = engine['metric_name']
        metric_d['engine'] = engine['engine']
        query = LogSeRank.objects.values(  'phrase_id','phrase_id__phrase','phrase_id__first_seen'). \
                                  annotate( num_ips=Count('ip', distinct = True)). \
                                  filter(   engine_id__engine__contains =  engine['engine'],
                                            position__gt =  engine['position'],
                                            phrase_id__first_seen__range=[week_ago,latest_sunday],
                                            client_id=client_id). \
                                  order_by('-num_ips').distinct()
        metric_d['query_result'] = query
        metric_d['query_cnt'] = query.count()
        metric_d['chart'] =process_time_series(query,week_ago,latest_sunday,'refdate',
                                         Count('id', distinct = True),'days')

        metric_LOD.append(metric_d)

    return sorted(metric_LOD, key=lambda x: x['metric_name'])




def get_datatables_records(request, querySet, columnIndexNameMap, jsonTemplatePath = None, page = None, *args):
    """
    Usage:
        querySet: query set to draw data from.
        columnIndexNameMap: field names in order to be displayed.
        jsonTemplatePath: optional template file to generate custom json from.  If not provided it will generate the data directly from the model.

    Author: Jarod Neven: https://www.assembla.com/profile/jarrod.neven

    """
    # Get the number of columns
    cols = int(request.GET.get('iColumns',0))
    #Safety measure. If someone messes with iDisplayLength manually, we clip it to the max value of 100.
    iDisplayLength =  min(int(request.GET.get('iDisplayLength',10)),100)
    startRecord = int(request.GET.get('iDisplayStart',0)) # Where the data starts from (page)
    endRecord = startRecord + iDisplayLength  # where the data ends (end of page)

    # Pass sColumns
    keys = columnIndexNameMap.keys()
    keys.sort()
    colitems = [columnIndexNameMap[key] for key in keys]
    sColumns = ",".join(map(str,colitems))

    # Ordering data
    iSortingCols =  int(request.GET.get('iSortingCols',0))
    asortingCols = []

    if iSortingCols:

        for sortedColIndex in range(0, iSortingCols):
            sortedColID = int(request.GET.get('iSortCol_'+str(sortedColIndex),0))

            if request.GET.get('bSortable_{0}'.format(sortedColID), 'false')  == 'true':  # make sure the column is sortable first
                sortedColName = columnIndexNameMap[sortedColID]
                sortingDirection = request.GET.get('sSortDir_'+str(sortedColIndex), 'asc')

                if sortingDirection == 'desc':
                    sortedColName = '-'+sortedColName

                asortingCols.append(sortedColName)

        querySet = querySet.order_by(*asortingCols)

    # Determine which columns are searchable
    searchableColumns = []
    for col in range(0,cols):
        if request.GET.get('bSearchable_{0}'.format(col), False) == 'true': searchableColumns.append(columnIndexNameMap[col])

    # Apply filtering by value sent by user
    customSearch = request.GET.get('sSearch', '').encode('utf-8');

    if customSearch != '':
        outputQ = None
        first = True

        for searchableColumn in searchableColumns:
            kwargz = {searchableColumn+"__icontains" : customSearch}
            outputQ = outputQ | Q(**kwargz) if outputQ else Q(**kwargz)

        querySet = querySet.filter(outputQ)

    # Individual column search
    outputQ = None

    for col in range(0,cols):
        if request.GET.get('sSearch_{0}'.format(col), False) > '' and request.GET.get('bSearchable_{0}'.format(col), False) == 'true':
            kwargz = {columnIndexNameMap[col]+"__icontains" : request.GET['sSearch_{0}'.format(col)]}
            outputQ = outputQ & Q(**kwargz) if outputQ else Q(**kwargz)

    if outputQ:
        querySet = querySet.filter(outputQ)

    iTotalRecords = iTotalDisplayRecords = querySet.count() #count how many records match the final criteria
    querySet = querySet[startRecord:endRecord] #get the slice
    sEcho = int(request.GET.get('sEcho',0)) # required echo response

    if jsonTemplatePath:
        #prepare the JSON with the response, consider using : from django.template.defaultfilters import escapejs
        jstonString = render_to_string(jsonTemplatePath, locals())
        response = HttpResponse(jstonString, mimetype="application/javascript")
    else:
        aaData = []
        a = querySet.values()

        for row in a:
            rowkeys = row.keys()
            rowvalues = row.values()
            rowlist = []

            for col in range(0,len(colitems)):
                for idx, val in enumerate(rowkeys):

                    if val == colitems[col]:
                        rowlist.append(str(rowvalues[idx]))

            aaData.append(rowlist)

        response_dict = {}
        response_dict.update({'aaData':aaData})
        response_dict.update({'sEcho': sEcho, 'iTotalRecords': iTotalRecords, 'iTotalDisplayRecords':iTotalDisplayRecords, 'sColumns':sColumns})



        response =  HttpResponse(json.dumps(response_dict), mimetype='application/javascript')

    #prevent from caching datatables result
    add_never_cache_headers(response)
    return response
