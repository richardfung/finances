import csv
import io
from optparse import OptionParser
import re
import sys

def main():
    usage = 'Usage: %prog input_file month'
    parser = OptionParser(usage=usage)
    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error('Incorrect number of arguments')
    [input_filename, month] = args[:]
    if not re.fullmatch('[01]?\d', month):
        parser.error('Invalid month')
    print(transform(input_filename, month))

def amex_credit_card(input_filename, month):
    """Format is just contents.

    date, ?, description, ?, ?, ?, ?, amount, ????????..."""
    test = _make_month_test(0, month)

    def transform(xs):
        return [xs[0].split()[0], xs[2],
                '-' + xs[7] if xs[7][0] != '-' else xs[7][1:]]

    return _csv_transform(input_filename, test, transform,
                          None)

def boa_checking(input_filename, month):
    """Format is some stuff we don't care about for first n lines, then a blank
    line, and then the csv stuff we are interested in.

    The csv has Date, Description, Amount, Total Balance"""

    month = str(month)
    test = _make_month_test(0, month)

    def transform(xs):
        return xs[0:3]

    def preprocess_func(reader):
        # Skip past the first blank line
        while next(reader):
            pass
        # Remove the description line
        if next(reader) != ['Date', 'Description', 'Amount', 'Running Bal.']:
            raise ValueError('Expected description line. ' +
                             'Did the format change?')

        # Remove the "beginning balance" line
        if not next(reader)[1].startswith('Beginning balance as of'):
            raise ValueError('Expected beginning balance line. ' +
                             'Did the format change?')

    return _csv_transform(input_filename, test, transform,
                          preprocess_func)

def boa_credit_card(input_filename, month):
    """Format is one line for description and then the contents.

    Posted Date, Reference Number, Payee, Address, Amount"""

    test = _make_month_test(0, month)

    def transform(xs):
        return [xs[0], xs[2], xs[4]]

    return _csv_transform(input_filename, test, transform,
                          None)

def chase_credit_card(input_filename, month):
    """Format is one line for description then contents.

    Type, Trans Date, Post Date, Description, Amount"""

    test = _make_month_test(1, month)

    def transform(xs):
        return [xs[1], xs[3], xs[4]]

    return _csv_transform(input_filename, test, transform,
                          None)

def test_output(s):
    """Given string s, tests whether this is the csv format that we expect.
    That is, it should return lines of the form [date, description, amount]"""
    s = io.StringIO(s, newline=None)
    reader = csv.reader(s)
    date_re = re.compile('\d{2}/\d{2}/\d{4}')
    amount_re = re.compile('-?\d+\.\d{2}')
    non_empty = False
    for row in reader:
        non_empty = True
        if not (date_re.fullmatch(row[0]) and len(row[1]) > 0 and
                amount_re.fullmatch(row[2])):
            return False
    return non_empty

def transform(input_filename, month):
    """ Transforms the csv file with filename input_filename to output which
    should pass test_output. This will try all the various types of csv formats
    and return an error if none or more than one are valid and otherwise returns
    the only valid transformation."""
    transforms = [amex_credit_card, boa_checking, boa_credit_card,
                  chase_credit_card]
    solutions = [t(input_filename, month) for t in transforms]
    valid_solutions = [x for x in solutions if x is not None]
    if not valid_solutions or len(valid_solutions) > 1:
        raise ValueError("# of valid solutions: %d" % len(valid_solutions))
    return valid_solutions[0]

def _csv_transform(input_filename, test, transform, preprocess_func):
    # TODO do we need to catch and close?
    output_file = io.StringIO(newline=None)
    try:
        _csv_read_write_file(input_filename, output_file, test, transform,
                             preprocess_func)
        val = output_file.getvalue()
        return val if test_output(val) else None
    except:
        return None

def _csv_read_write_file(input_filename, output_file, test, transform,
                    preprocess_func):
    """Helper function which handles reading a csv file and writing to another
    file.

    input_filename is the name of input file.
    test is a function which takes a list and returns a bool. This will be
        called on the input csv file rows to determine whether we want to write
        them to the output.
    transform is a function that takes a list and returns another list. This
        function is used to transform the list from the input csv file to the
        one for the output csv file.
    preprocess_func is a function that takes a reader and will be called before
        we begin reading the input csv file and writing the output csv file.
        It is intended to be used to preprocess the input csv file."""
    with open(input_filename, 'r') as in_file:
        reader = csv.reader(in_file)
        if preprocess_func:
            preprocess_func(reader)
        writer = csv.writer(output_file)
        for row in reader:
            if row and test(row):
                writer.writerow(transform(row))

def _make_month_test(pos, month):
    month = str(month)
    def test(xs):
        return xs[pos].startswith(month) or xs[pos].startswith('0%s' % month)
    return test

if __name__ == '__main__':
    main()
