"""Hello Analytics Reporting API V4."""
import argparse

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from datetime import datetime, timedelta, date
import csv
from collections import OrderedDict

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = './client_secrets.json'
VIEW_ID = '131733103'


def initialize_analyticsreporting():
  """Initializes an Analytics Reporting API V4 service object.

  Returns:
    An authorized Analytics Reporting API V4 service object.
  """
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
      KEY_FILE_LOCATION, SCOPES)

  # Build the service object.
  analytics = build('analytics', 'v4', credentials=credentials)

  return analytics


def get_report(analytics):
  """Queries the Analytics Reporting API V4.

  Args:
    analytics: An authorized Analytics Reporting API V4 service object.
  Returns:
    The Analytics Reporting API V4 response.
  """
  currentDateTime = datetime.now();
  currentDate = str(date.today())
  oneHourAgo = currentDateTime - timedelta(hours=1)
  currentDateTimeISO = currentDateTime.isoformat()
  oneHourAgoISO = oneHourAgo.isoformat()
  oneDayAgo = str(date.fromordinal(date.today().toordinal()-1))

  return analytics.reports().batchGet(
      body={
        'reportRequests': [
        {
          'viewId': VIEW_ID,
          'dateRanges': [{'startDate': oneDayAgo, 'endDate': currentDate}],
          'metrics': [{'expression': 'ga:productDetailViews'}, {'expression': 'ga:metric2'}, {'expression': 'ga:productAddsToCart'}, {'expression': 'ga:productCheckouts'}, {'expression': 'ga:productRemovesFromCart'}],
          'dimensions': [{'name': 'ga:productSku'}, {'name': 'ga:dimension1'}]
        }]
      }
  ).execute()

def outputToCSV(response):
  """Parses and outputs the Analytics Reporting API V4 response to csv file.

  Args:
    response: An Analytics Reporting API V4 response.
  """

  columnNames = OrderedDict()
  columnNames['ga:productSku'] = 'Product SKU'
  columnNames['ga:dimension1'] = 'UserId'
  columnNames['ga:productDetailViews'] = 'View pdp'
  columnNames['ga:metric2'] = 'Add to wishlist'
  columnNames['ga:productAddsToCart'] = 'Add to cart'
  columnNames['ga:productCheckouts'] = 'Checkout product'
  columnNames['ga:productRemovesFromCart'] = 'Removes product from cart'

  data = []
  columns = [0] * 7
  for report in response.get('reports', []):
    columnHeader = report.get('columnHeader', {})
    dimensionHeaders = columnHeader.get('dimensions', [])
    metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

    for dimensionName in dimensionHeaders:
      newDimensionName = columnNames[dimensionName] if dimensionName in columnNames else dimensionName
      columnIndex = list(columnNames).index(dimensionName)
      columns[columnIndex] = str(newDimensionName)
    
    for metricName in metricHeaders:
      trueMetricName = metricName.get('name')
      newMetricName = columnNames[trueMetricName] if trueMetricName in columnNames else trueMetricName
      columnIndex = list(columnNames).index(trueMetricName)
      columns[columnIndex] = str(newMetricName)
    
    data.append(columns)

    for row in report.get('data', {}).get('rows', []):
      csvRow = [0] * 7
      dimensions = row.get('dimensions', [])
      dateRangeValues = row.get('metrics', [])

      for header, dimension in zip(dimensionHeaders, dimensions):
        dimensionIndex = list(columnNames).index(header)
        csvRow[dimensionIndex] = dimension

      for i, values in enumerate(dateRangeValues):
        for metricHeader, value in zip(metricHeaders, values.get('values')):
          metricIndex = list(columnNames).index(metricHeader.get('name'))
          csvRow[metricIndex] = str(value)

      data.append(csvRow)
    currentDate = str(date.today())
    oneDayAgo = str(date.fromordinal(date.today().toordinal()-1))

    with open('{0} - {1}.csv'.format(oneDayAgo, currentDate), 'w', newline='') as fp:
      a = csv.writer(fp, delimiter=',')
      a.writerows(data)

def print_response(response):
  """Parses and prints the Analytics Reporting API V4 response.

  Args:
    response: An Analytics Reporting API V4 response.
  """
  for report in response.get('reports', []):
    columnHeader = report.get('columnHeader', {})
    dimensionHeaders = columnHeader.get('dimensions', [])
    metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

    for row in report.get('data', {}).get('rows', []):
      dimensions = row.get('dimensions', [])
      dateRangeValues = row.get('metrics', [])

      for header, dimension in zip(dimensionHeaders, dimensions):
        print(header + ': ' + dimension)

      for i, values in enumerate(dateRangeValues):
        print('Date range: ' + str(i))
        for metricHeader, value in zip(metricHeaders, values.get('values')):
          print(metricHeader.get('name') + ': ' + value)


def main():
  analytics = initialize_analyticsreporting()
  response = get_report(analytics)
  # print_response(response)
  outputToCSV(response)

if __name__ == '__main__':
  main()

