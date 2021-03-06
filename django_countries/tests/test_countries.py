# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase

from django_countries import countries, Countries


EXPECTED_COUNTRY_COUNT = 249
FIRST_THREE_COUNTRIES = [
    ('AF', 'Afghanistan'),
    ('AX', 'Åland Islands'),
    ('AL', 'Albania'),
]


class BaseTest(TestCase):

    def setUp(self):
        del countries.countries

    def tearDown(self):
        del countries.countries


class TestCountriesObject(BaseTest):

    def test_countries_len(self):
        self.assertEqual(len(countries), EXPECTED_COUNTRY_COUNT)

    def test_countries_sorted(self):
        self.assertEqual(list(countries)[:3], FIRST_THREE_COUNTRIES)

    def test_countries_limit(self):
        with self.settings(
                COUNTRIES_ONLY={'NZ': 'New Zealand', 'NV': 'Neverland'}):
            self.assertEqual(list(countries), [
                ('NV', 'Neverland'),
                ('NZ', 'New Zealand'),
            ])
            self.assertEqual(len(countries), 2)

    def test_countries_custom_removed_len(self):
        with self.settings(COUNTRIES_OVERRIDE={'AU': None}):
            self.assertEqual(len(countries), EXPECTED_COUNTRY_COUNT - 1)

    def test_countries_custom_added_len(self):
        with self.settings(COUNTRIES_OVERRIDE={'XX': 'Neverland'}):
            self.assertEqual(len(countries), EXPECTED_COUNTRY_COUNT + 1)

    def test_countries_getitem(self):
        countries[0]

    def test_countries_slice(self):
        sliced = countries[10:20:2]
        self.assertEqual(len(sliced), 5)

    def test_countries_custom_ugettext_evaluation(self):

        class FakeLazyUGetText(object):

            def __bool__(self):  # pragma: no cover
                raise ValueError("Can't evaluate lazy_ugettext yet")

            __nonzero__ = __bool__

        with self.settings(COUNTRIES_OVERRIDE={'AU': FakeLazyUGetText()}):
            countries.countries

    def test_ioc_countries(self):
        from ..ioc_data import check_ioc_countries
        check_ioc_countries(verbosity=0)

    def test_initial_iter(self):
        # Use a new instance so nothing is cached
        dict(Countries())

    def test_flags(self):
        from ..data import check_flags
        check_flags(verbosity=0)

    def test_common_names(self):
        from ..data import check_common_names
        check_common_names()

    def test_alpha2(self):
        self.assertEqual(countries.alpha2('NZ'), 'NZ')
        self.assertEqual(countries.alpha2('nZ'), 'NZ')
        self.assertEqual(countries.alpha2('Nzl'), 'NZ')
        self.assertEqual(countries.alpha2(554), 'NZ')
        self.assertEqual(countries.alpha2('554'), 'NZ')

    def test_alpha2_invalid(self):
        self.assertEqual(countries.alpha2('XX'), '')

    def test_alpha2_override(self):
        with self.settings(COUNTRIES_OVERRIDE={'AU': None}):
            self.assertEqual(countries.alpha2('AU'), '')

    def test_alpha2_override_new(self):
        with self.settings(COUNTRIES_OVERRIDE={'XX': 'Neverland'}):
            self.assertEqual(countries.alpha2('XX'), 'XX')

    def test_fetch_by_name(self):
        self.assertEqual(countries.by_name('United States'), 'US')

    def test_fetch_by_name_i18n(self):
        self.assertEqual(countries.by_name('Estados Unidos', language='es'), 'US')

    def test_fetch_by_name_no_match(self):
        self.assertEqual(countries.by_name('Neverland'), '')


class CountriesFirstTest(BaseTest):

    def test_countries_first(self):
        with self.settings(COUNTRIES_FIRST=['NZ', 'AU']):
            self.assertEqual(
                list(countries)[:5],
                [
                    ('NZ', 'New Zealand'),
                    ('AU', 'Australia'),
                ] + FIRST_THREE_COUNTRIES)

    def test_countries_first_break(self):
        with self.settings(COUNTRIES_FIRST=['NZ', 'AU'],
                           COUNTRIES_FIRST_BREAK='------'):
            self.assertEqual(
                list(countries)[:6],
                [
                    ('NZ', 'New Zealand'),
                    ('AU', 'Australia'),
                    ('', '------'),
                ] + FIRST_THREE_COUNTRIES)

    def test_countries_first_some_valid(self):
        with self.settings(COUNTRIES_FIRST=['XX', 'NZ', 'AU'],
                           COUNTRIES_FIRST_BREAK='------'):
            countries_list = list(countries)
        self.assertEqual(
            countries_list[:6],
            [
                ('NZ', 'New Zealand'),
                ('AU', 'Australia'),
                ('', '------'),
            ] + FIRST_THREE_COUNTRIES)
        self.assertEqual(len(countries_list), EXPECTED_COUNTRY_COUNT + 1)

    def test_countries_first_no_valid(self):
        with self.settings(COUNTRIES_FIRST=['XX'],
                           COUNTRIES_FIRST_BREAK='------'):
            countries_list = list(countries)
        self.assertEqual(countries_list[:3], FIRST_THREE_COUNTRIES)
        self.assertEqual(len(countries_list), EXPECTED_COUNTRY_COUNT)

    def test_countries_first_repeat(self):
        with self.settings(COUNTRIES_FIRST=['NZ', 'AU'],
                           COUNTRIES_FIRST_REPEAT=True):
            countries_list = list(countries)
        self.assertEqual(len(countries_list), EXPECTED_COUNTRY_COUNT + 2)
        sorted_codes = [item[0] for item in countries_list[2:]]
        sorted_codes.index('NZ')
        sorted_codes.index('AU')

    def test_countries_first_len(self):
        with self.settings(COUNTRIES_FIRST=['NZ', 'AU', 'XX']):
            self.assertEqual(len(countries), EXPECTED_COUNTRY_COUNT + 2)

    def test_countries_first_break_len(self):
        with self.settings(COUNTRIES_FIRST=['NZ', 'AU', 'XX'],
                           COUNTRIES_FIRST_BREAK='------'):
            self.assertEqual(len(countries), EXPECTED_COUNTRY_COUNT + 3)

    def test_countries_first_break_len_no_valid(self):
        with self.settings(COUNTRIES_FIRST=['XX'],
                           COUNTRIES_FIRST_BREAK='------'):
            self.assertEqual(len(countries), EXPECTED_COUNTRY_COUNT)
