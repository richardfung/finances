import csv

def boa_checking(input_filename, output_filename, month):
    """Format is some stuff we don't care about for first n lines, then a blank
    line, and then the csv stuff we are interested in.

    The csv has Date, Description, Amount, Total Balance"""

    def test(xs):
        return xs[0].startswith(month) or xs[0].startswith('0%s' % month)

    def transform(xs):
        return xs[0:3]

    with open(input_filename, 'rb') as in_file:
        reader = csv.reader(in_file)
        # Skip past the first blank line
        while reader.next():
            pass
        # Remove the description line
        if reader.next() != ['Date', 'Description', 'Amount', 'Running Bal.']:
            raise ValueError('Expected description line. ' +
                             'Did the format change?')

        # Remove the "beginning balance" line
        if not reader.next()[1].startswith('Beginning balance as of'):
            raise ValueError('Expected beginning balance line. ' +
                             'Did the format change?')

        with open(output_filename, 'wb') as out_file:
            writer = csv.writer(out_file)
            for row in reader:
                if test(row):
                    writer.writerow(transform(row))
