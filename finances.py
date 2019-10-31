from collections import namedtuple

import argparse
import csv
import io
import re
import sys

def main():
    parser = argparse.ArgumentParser(description=('Converts csv files from '
    'different banks to the same format to be parsed by Google Sheets'))
    parser.add_argument(
            'input_file',
            help='input name of csv file')
    parser.add_argument(
            '--month',
            '-m',
            dest='month',
            type=int,
            help=('The month we care about. All rows from other months will '
                  'be ignored'))
    parser.add_argument(
            '--fmt',
            dest='format',
            type=str,
            choices=function_name_map.keys(),
            help=('The format of the file. If none given, we try to '
                  'intelligently figure it out.'))
    args = parser.parse_args()
    if not re.fullmatch('[01]?\d', str(args.month)):
        argparse.ArgumentParser.error('Invalid month')
    sys.stdout.write(transform(args.input_file, args.month, args.format))

def amex_credit_card(input_filename, month):
    """Format is just contents.

    date, ?, description, ?, ?, amount, ????????..."""
    test = _make_month_test(0, month)

    def transform(xs):
        return [xs[0], xs[2],
                '-' + xs[5] if xs[5][0] != '-' else xs[5][1:]]

    return _csv_transform(input_filename, test, transform,
                          None)

def boa_credit_card(input_filename, month):
    """Format is one line for description and then the contents.

    Posted Date, Reference Number, Payee, Address, Amount"""

    test = _make_month_test(0, month)

    def transform(xs):
        return [xs[0], xs[2], xs[4]]

    return _csv_transform(input_filename, test, transform,
                          None)

def chase_checking(input_filename, month):
    """Format is one line for description then contents.

    Details,Posting Date,Description,Amount,Type,Balance,Check or Slip"""
    test = _make_month_test(1, month)

    transform = lambda xs: [xs[1], xs[2], xs[3]]
    return _csv_transform(input_filename, test, transform, None)

def chase_credit_card(input_filename, month):
    """Format is one line for description then contents.

    Trans Date, Post Date, Description, Category, Type, Amount"""

    test = _make_month_test(0, month)

    def transform(xs):
        return [xs[0], xs[2], xs[5]]

    return _csv_transform(input_filename, test, transform,
                          None)

def test_output(s):
    """Given string s, tests whether this is the csv format that we expect.
    That is, it should return lines of the form [date, description, amount]"""
    s = io.StringIO(s, newline=None)
    reader = csv.reader(s)
    date_re = re.compile('\d\d?/\d\d?/(\d{2}|\d{4})')
    amount_re = re.compile('-?\d+\.\d{2}')
    non_empty = False
    for row in reader:
        non_empty = True
        if not (date_re.fullmatch(row[0]) and len(row[1]) > 0 and
                amount_re.fullmatch(row[2])):
            return False
    return non_empty

def transform(input_filename, month, fmt):
    """ Transforms the csv file with filename input_filename to output which
    should pass test_output. This will try all the various types of csv formats
    and return an error if none or more than one are valid and otherwise returns
    the only valid transformation."""
    FunctionMapping = namedtuple('FunctionMapping', ['function', 'name'])
    if not fmt:
        transforms = [FunctionMapping(function_name_map[n], n) for n in function_name_map]
    else:
        transforms = [FunctionMapping(function_name_map[fmt], fmt)]
    solutions = [(t(input_filename, month), n) for (t, n) in transforms]
    valid_solutions = [x for x in solutions if x[0] is not None]
    if not valid_solutions:
        raise ValueError('no valid solutions found!')
    elif len(valid_solutions) > 1:
        raise ValueError('multiple valid solutions found: ' + str([x[1] for x in valid_solutions]))
    return valid_solutions[0][0]

def _csv_transform(input_filename, test, transform, preprocess_func):
    # TODO do we need to catch and close?
    output_file = io.StringIO(newline=None)
    try:
        _csv_read_write_file(input_filename, output_file, test, transform,
                             preprocess_func)
        val = output_file.getvalue()
        return val if test_output(val) else None
    except Exception as e:
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
    """ Returns a simple function that tests whether a string starts with
    the given month in integer format."""
    month = str(month)
    def test(xs):
        return xs[pos].startswith(month) or xs[pos].startswith('0' + month)
    return test

function_name_map = {'amex_cc': amex_credit_card,
                     'boa_cc': boa_credit_card,
                     'chase_cc': chase_credit_card,
                     'chase_checking': chase_checking}

if __name__ == '__main__':
    main()
