import csv

def boa_checking(input_filename, output_filename, month):
    """Format is some stuff we don't care about for first n lines, then a blank
    line, and then the csv stuff we are interested in.

    The csv has Date, Description, Amount, Total Balance"""

    month = str(month)
    def test(xs):
        return xs[0].startswith(month) or xs[0].startswith('0%s' % month)

    def transform(xs):
        return xs[0:3]

    def preprocess_func(reader):
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

    _csv_read_write(input_filename, output_filename, test, transform,
                    preprocess_func)

def boa_credit_card(input_filename, output_filename, month):
    """Format is one line for description and then the contents.

    Posted Date, Reference Number, Payee, Address, Amount"""

    month = str(month)
    def test(xs):
        return xs[0].startswith(month) or xs[0].startswith('0%s' % month)

    def transform(xs):
        return [xs[0], xs[2], xs[4]]

    _csv_read_write(input_filename, output_filename, test, transform, None)

def chase_credit_card(input_filename, output_filename, month):
    """Format is one line for description then contents.

    Type, Trans Date, Post Date, Description, Amount"""

    month = str(month)
    def test(xs):
        return xs[1].startswith(month) or xs[1].startswith('0%s' % month)

    def transform(xs):
        return [xs[1], xs[3], xs[4]]

    _csv_read_write(input_filename, output_filename, test, transform, None)

def _csv_read_write(input_filename, output_filename, test, transform,
                    preprocess_func):
    """Helper function which handles reading a csv file and writing to another
    file.

    input_filename is the name of input file.
    output_filename is the name of the output file.
    test is a function which takes a list and returns a bool. This will be
        called on the input csv file rows to determine whether we want to write
        them to the output.
    transform is a function that takes a list and returns another list. This
        function is used to transform the list from the input csv file to the
        one for the output csv file.
    preprocess_func is a function that takes a reader and will be called before
        we begin reading the input csv file and writing the output csv file.
        It is intended to be used to preprocess the input csv file."""
    with open(input_filename, 'rb') as in_file:
        reader = csv.reader(in_file)
        if preprocess_func:
            preprocess_func(reader)
        with open(output_filename, 'wb') as out_file:
            writer = csv.writer(out_file)
            for row in reader:
                if row and test(row):
                    writer.writerow(transform(row))
