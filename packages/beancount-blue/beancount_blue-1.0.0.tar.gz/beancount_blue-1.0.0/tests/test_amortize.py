import unittest

from beancount import loader

from beancount_blue.amortize import amortize


class TestAmortize(unittest.TestCase):
    @loader.load_doc()
    def test_simple_amortization(self, entries, _, options_map):
        """
        option "booking_method" "NONE"
        plugin "beancount.plugins.auto_accounts"

        2023-01-15 * "Software Purchase"
          Expenses:Software  1200.00 GBP
          Assets:Cash       -1200.00 GBP
        """

        config = """{
                'accounts': {
                        'Expenses:Software': {
                            'expense_account': 'Expenses:Software',
                            'months': 12,
                        }
                }
        }"""

        (amortization_txns, errors) = amortize(entries, options_map, config)

        for p in amortization_txns:
            print(p)

        self.assertEqual(0, len(errors))
        self.assertEqual(15, len(amortization_txns))

        # TODO: Compare to the final book.
