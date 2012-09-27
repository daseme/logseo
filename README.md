# Django LogSeo #


## V0.5 underway ##

LogSeo is a tool for exploring query-sets recorded in your apache access logs.  It provides a variety of summary
stats and time-series data for exploring your keyword traffic.


## Current Features: ##

-   Parses apache log file / loads database
-   Variety of summary stats related to query traffic
    - ip count
    - stdev
    - rank and rank trends
    - recently discovered queries
    - queries that have dropped out
    - Search engine identification
    - Ranking data when provided by Google searches
-   Keyword tagging ability provided by django-taggit
-   Pretty time-series charts provided by Rickshaw

## Planned Features: ##

-   Watchlist - select search queries and/or landing pages to 'watch'
-   Google Analytics data integration (in progress)
-   Auto-clustering/tagging of keyword data


## Core Components: ##

The app is broken down into several main parts.

-  A custom management function for parseing log files and loading the db
-  A front-end dashboard for exploring


## Usage: ##

### Quickstart: ###

Download django-logseo and install as you would any Django project

Get nltk stopwords corpus:

$ python
>> import nltk
>> nltk.download('stopwords')

Drop some log files into logseoapp/management/commands/logs

Run ./manage.py parselog

Spool up the test server and explore your data!



## Development: ##

This is my first Django app and is being developed in my spare time.  It is based on a much more narrowly defined 
Perl/PHP/JS app that I use for exploratory SEO-related activities with my clients.  So it is a 'learning Django' app for me, but I hope you find it useful.

You are encouraged to join in !


