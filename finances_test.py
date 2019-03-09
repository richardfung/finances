import finances
import os
import pytest

TEST_DIR = 'test_files'

def test_amex_credit_card():
    _test('amex_in.csv', 'amex_out.csv', finances.amex_credit_card, 2)

def test_boa_credit_card():
    _test('boa_visa_in.csv', 'boa_visa_out.csv', finances.boa_credit_card, 8)

def test_chase_checking():
    _test('chase_checking_in.csv', 'chase_checking_out.csv', finances.chase_checking, 2)

def test_chase_credit_card():
    _test('chase_credit_card_in.csv', 'chase_credit_card_out.csv', finances.chase_credit_card, 2)

def _test(in_file, out_file, test_fun, month):
    got = test_fun(os.path.join(TEST_DIR, in_file), month)
    _compare(got, out_file)

    got = finances.transform(os.path.join(TEST_DIR, in_file), month)
    _compare(got, out_file)

def _compare(got, expected_filename):
    """Helper function which just compares got with the file that has filename
    expected_filename."""
    with open(os.path.join(TEST_DIR, expected_filename), 'r') \
            as expected_file:
        expected = expected_file.read()
        assert got == expected
