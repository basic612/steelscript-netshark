#!/usr/bin/env python

# Copyright (c) 2015 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.



"""
This script shows the simplest way to create a custom view on a NetShark and
retrieve its data. It creates a simple top talker view by processing the remote
file specified on the command line (use the shark_info.py script to list the
files on the appliance), and then saves the data on a csv file that can be
opened in excel.
"""

from steelscript.netshark.core.app import NetSharkApp
from steelscript.netshark.core.types import Value, Key
from steelscript.netshark.core.viewutils import write_csv

CSV_FILE_NAME = "result.csv"


class CreateView(NetSharkApp):
    def add_options(self, parser):
        super(CreateView, self).add_options(parser)
        parser.add_option('--file', help='filename to open')

    def validate_args(self):
        """ Ensure columns are included
        """
        super(CreateView, self).validate_args()

        if not self.options.file:
            self.parser.error('Filename of file on NetShark machine required ("--file").')

    def main(self):
        # Open the remote file
        source = self.netshark.get_file(self.options.file)

        # Specify the column list
        columns = [
            # Views are similar in concept to SQL tables, and the one we are
            # creating has only one key, the source IP address. This means that
            # data will be grouped by source IP.
            # Note that we support auto-completion on column names! If you want
            # to try it, put a breakpoint on the line below and then type
            # "sk.columns." in the debugger. That will work in any inteactive
            # python editor as well (e.g. eclipse, bpython, dreampie...).
            Key(self.netshark.columns.ip.src),

            # Each of the rows in the view is going to have a value column
            # containing the amount of bytes.
            Value(self.netshark.columns.generic.bytes),
        ]

        # Create the view
        v = self.netshark.create_view(source, columns)

        # Retrieve the view data.
        # Aggregated=True means that we want the view data in a single big
        # sample, suitable to be represented in a barchart. The default value
        # for aggregated is False and would give us single-second values ready
        # to be charted in a stripchart.
        output = v.get_data(aggregated=True)

        # Save the view data to disk.
        # Note that, in addition to the data, we need to provide the legend,
        #  which is necessary to decode it.
        write_csv(CSV_FILE_NAME, v.get_legend(), output)
        print "View data written to file " + CSV_FILE_NAME

        # Done! We can close the view.
        v.close()


if __name__ == '__main__':
    CreateView().run()
