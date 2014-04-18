# -*- coding: utf-8 -*-
# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the
# MIT License set forth at:
#   https://github.com/riverbed/flyscript-portal/blob/master/LICENSE ('License').
# This software is distributed 'AS IS' as set forth in the License.

from rvbd_portal.apps.report.models import Report
import rvbd_portal.apps.report.modules.yui3 as yui3

from steelscript.shark.appfw.datasources.shark import SharkTable
#
# Define a Shark Report and Table
#

report = Report.create('Shark DNS', position=6)

report.add_section()


### DNS Success/Failure Queries Over time
name = 'DNS Success and Failure Queries Over Time'
s = SharkTable.create(name, duration=15, resolution='1min', aggregated=False)

s.add_column('time', label='Time', iskey=True, datatype='time',
             extractor='sample_time')
s.add_column('dns_count', label='DNS Query Count', datatype='integer',
             extractor='dns.query.count', operation='sum')
s.add_column('dns_is_success', label='DNS Success', datatype='integer',
             extractor='dns.is_success', operation='none')
report.add_widget(yui3.TimeSeriesWidget, s, name, width=12)


### DNS Response Code List for Shark 1
name = 'DNS Response Codes'
s = SharkTable.create(name, duration=15, aggregated=True)

s.add_column('dns_is_success_str', label='DNS Success', iskey=True,
             datatype='string', extractor='dns.is_success_str',
             operation='none')
s.add_column('dns_total_queries', label='DNS Total Queries',
             datatype='integer', extractor='dns.query.count',
             operation='sum', issortcol=True)

report.add_widget(yui3.PieWidget, s, name, width=6)

### DNS Query Type for Shark 1
name = 'DNS Query Type'
s = SharkTable.create(name, duration=15, aggregated=True)

s.add_column('dns_query_type', label='DNS Query Type', iskey=True,
             datatype='string', extractor='dns.query.type', operation='none')
s.add_column('dns_total_queries', label='DNS Total Queries',
             datatype='integer', extractor='dns.query.count', operation='sum',
             issortcol=True)

report.add_widget(yui3.PieWidget, s, name, width=6)

### DNS Request Details Table for Shark 1
name = 'DNS Requests'
s = SharkTable.create(name, duration=15, aggregated=True)

s.add_column('dns_query_name', label='DNS Request', iskey=True,
             datatype='string', extractor='dns.query.name', issortcol=True)
s.add_column('dns_query_type', label='# Requests',
             datatype='string', extractor='dns.query.count', operation='sum')
s.add_column('dns_is_success', label='# Successful',
             datatype='integer', extractor='dns.is_success', operation='none')

report.add_widget(yui3.TableWidget, s, name, width=12)

### Response Time over Time
name = 'DNS Response Time Over Time'
s = SharkTable.create(name, duration=15, resolution='1min', aggregated=False)

s.add_column('time', label='Time', iskey=True, datatype='time',
             extractor='sample_time', operation='none')
s.add_column('dns_response_time', label='DNS Response Time (ns)',
             units='ms', extractor='dns.response_time', operation='none')

report.add_widget(yui3.TimeSeriesWidget, s, name, width=12)
