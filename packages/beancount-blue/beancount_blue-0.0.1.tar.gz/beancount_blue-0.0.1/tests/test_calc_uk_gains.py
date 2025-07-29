import unittest

from beancount import loader
from beancount.core.amount import Amount
from beancount.core.data import Transaction
from beancount.core.number import D

from beancount_blue.calc_uk_gains import calc_gains


class TestCalcUkGains(unittest.TestCase):
    @loader.load_doc()
    def test_simple_gain_calculation(self, entries, _, options_map):
        """
        option "booking_method" "NONE"
        plugin "beancount.plugins.auto_accounts"
        ;2022-12-31 commodity X
        ;  name: "Tradeable entity"
        ;  asset-class: "stock"

        2023/1/25 * "Acquisition"
          Assets:Test1  10 X {{ 10.00 GBP }}
          Assets:Test1  -10.00 GBP

        2023/2/25 * "Redemption"
          Assets:Test1  -4 X {{ 74.80 GBP }}
          Assets:Test1  74.80 GBP
        """

        config = """{
                'accounts': {
                        'Assets:Test1': { 'method': 'cost_avg',
                                          'counterAccount': 'Equity:Gains'},
                        'Assets:Test2': { 'method': 'cost_avg',
                                          'counterAccount': 'Equity:Gains'},
                }
        }"""

        (gain_transactions, errors) = calc_gains(entries, options_map, config)

        self.assertEqual(3, len(gain_transactions))
        gain_txn = gain_transactions[2]

        if not isinstance(gain_txn, Transaction):
            self.assertTrue(False, "invalid type")
            return

        self.assertEqual(3, len(gain_txn.postings))

        self.assertEqual(3, len(gain_txn.postings))

        # Sort postings by account name for predictable order
        postings = sorted(gain_txn.postings, key=lambda p: p.account)

        for p in gain_txn.postings:
            print(p)

        # Check the posting to the asset account (cost basis adjustment)
        self.assertEqual("Assets:Test1", postings[0].account)
        self.assertEqual(Amount(D("-4"), "X"), postings[0].units)
        self.assertEqual(Amount(D("1.00"), "GBP"), postings[0].cost)

        self.assertEqual("Assets:Test1", postings[1].account)
        self.assertEqual(Amount(D("74.80"), "GBP"), postings[1].units)

        # Check the posting to the gains account
        self.assertEqual("Equity:Gains", postings[2].account)
        self.assertEqual(Amount(D("-70.80"), "GBP"), postings[2].units)


# Tests:
# High priority:
# - Test applied adjustments with expected adjustments for the transactions
# - This needs to be for the base cost average approach
#   (other approaches can be tested in isolation)
# Low priority:
# - Separate tests for cost base averaging
# Low priority:
# - ensure accounts and commodities are filtered the right way
