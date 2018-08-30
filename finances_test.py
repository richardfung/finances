import finances
import os
import pytest

TEST_OUTPUT_FILE = '__test_file__.csv'
TEST_DIR = 'test_files'

def test_amex_credit_card():
    finances.amex_credit_card(os.path.join(TEST_DIR, 'amex_in.csv'),
                              TEST_OUTPUT_FILE, 8)
    _compare('amex_out.csv')

def test_boa_checking():
    finances.boa_checking(os.path.join(TEST_DIR, 'checking_in.csv'),
                          TEST_OUTPUT_FILE, 8)
    _compare('checking_out.csv')

def test_boa_credit_card():
    finances.boa_credit_card(os.path.join(TEST_DIR, 'boa_visa_in.csv'),
                             TEST_OUTPUT_FILE, 8)
    _compare('boa_visa_out.csv')

def test_chase_credit_card():
    finances.chase_credit_card(os.path.join(TEST_DIR, 'chase_in.csv'),
                             TEST_OUTPUT_FILE, 7)
    _compare('chase_out.csv')


def _compare(expected_filename):
    """Helper function which just compares the TEST_OUTPUT_FILE with the file
    that has filename expected_filename. This should be called after calling
    the function to be tested with TEST_OUTPUT_FILE as the output_filename"""
    with open(TEST_OUTPUT_FILE, 'r') as got_file:
        with open(os.path.join(TEST_DIR, expected_filename), 'r') \
                as expected_file:
            got = got_file.read()
            expected = expected_file.read()
            assert got == expected
