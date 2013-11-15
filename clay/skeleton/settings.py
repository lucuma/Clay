# Project settings

## Do not show HTML fragments in the final build or in the _index.html
FILTER_PARTIALS=True

## Ignore the views listed here when building, even if they are full HTML pages
## You can use patterns here eg: "deprecated/*"
FILTER = [
  'base.html'
]

## When building, force the inclusion of all the HTML partials listed here.
## You can use patterns here eg: "alert-*.html"
INCLUDE = [
]
  #

## Server
host=0.0.0.0
port=8080

## Your own settings here
