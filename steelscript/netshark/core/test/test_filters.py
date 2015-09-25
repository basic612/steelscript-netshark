# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.



import unittest
import steelscript.netshark.core.filters as filters


class FilterTests(unittest.TestCase):
    def test_timefilter(self):
        filters.TimeFilter.parse_range('last 5 minutes')
