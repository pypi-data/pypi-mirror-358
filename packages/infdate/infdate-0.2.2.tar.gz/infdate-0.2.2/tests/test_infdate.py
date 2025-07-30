# -None*- coding: utf-8 -*-

"""
Tests for the infdate module
"""

import datetime

import secrets
import unittest

from math import inf, isnan, nan
from time import mktime, struct_time
from unittest.mock import Mock, call, patch

import infdate


MAX_ORDINAL = datetime.date.max.toordinal()

# This is an error message from Python itself
_NAN_INT_CONVERSION_ERROR_RE = "^cannot convert float NaN to integer$"


def random_deterministic_date() -> infdate.GenericDate:
    """Helper function: create a random deterministic Date"""
    return infdate.fromordinal(secrets.randbelow(MAX_ORDINAL) + 1)


class VerboseTestCase(unittest.TestCase):
    """Testcase showinf maximum differences"""

    def setUp(self):
        """set maxDiff"""
        self.maxDiff = None  # pylint: disable=invalid-name ; name from unittest module


class GenericDateBase(VerboseTestCase):
    """GenericDate objects - base functionality"""

    def test_nan_not_allowed(self):
        """test initialization with nan"""
        self.assertRaisesRegex(
            ValueError, _NAN_INT_CONVERSION_ERROR_RE, infdate.GenericDate, nan
        )

    def test_toordinal(self):
        """initialization and .toordinal() method"""
        num = 1.23
        gd = infdate.GenericDate(num)
        self.assertEqual(gd.toordinal(), 1)

    # pylint: disable=comparison-with-itself ; to show lt/gt ↔ le/ge difference

    def test_lt(self):
        """gd_instance1 < gd_instance2 capability"""
        for iteration in range(1, 1001):
            random_date = random_deterministic_date()
            with self.subTest(
                "compared to <-inf>", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(infdate.MIN < random_date)
                self.assertFalse(random_date < infdate.MIN)
            #
            with self.subTest(
                "compared to <inf>", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(random_date < infdate.MAX)
                self.assertFalse(infdate.MAX < random_date)
            #
            with self.subTest(
                "compared to itself", iteration=iteration, random_date=random_date
            ):
                self.assertFalse(random_date < random_date)
            #
        #

    def test_le(self):
        """less than or equal"""
        for iteration in range(1, 1001):
            random_date = random_deterministic_date()
            with self.subTest(
                "compared to <-inf>", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(infdate.MIN <= random_date)
                self.assertFalse(random_date <= infdate.MIN)
            #
            with self.subTest(
                "compared to <inf>", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(random_date <= infdate.MAX)
                self.assertFalse(infdate.MAX <= random_date)
            #
            with self.subTest(
                "compared to itself", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(random_date <= random_date)
            #
        #

    def test_gt(self):
        """greater than"""
        for iteration in range(1, 1001):
            random_date = random_deterministic_date()
            with self.subTest(
                "compared to <-inf>", iteration=iteration, random_date=random_date
            ):
                self.assertFalse(infdate.MIN > random_date)
                self.assertTrue(random_date > infdate.MIN)
            #
            with self.subTest(
                "compared to <inf>", iteration=iteration, random_date=random_date
            ):
                self.assertFalse(random_date > infdate.MAX)
                self.assertTrue(infdate.MAX > random_date)
            #
            with self.subTest(
                "compared to itself", iteration=iteration, random_date=random_date
            ):
                self.assertFalse(random_date > random_date)
            #
        #

    def test_ge(self):
        """greater than or equal"""

        for iteration in range(1, 1001):
            random_date = random_deterministic_date()
            with self.subTest(
                "compared to <-inf>", iteration=iteration, random_date=random_date
            ):
                self.assertFalse(infdate.MIN >= random_date)
                self.assertTrue(random_date >= infdate.MIN)
            #
            with self.subTest(
                "compared to <inf>", iteration=iteration, random_date=random_date
            ):
                self.assertFalse(random_date >= infdate.MAX)
                self.assertTrue(infdate.MAX >= random_date)
            #
            with self.subTest(
                "compared to itself", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(random_date <= random_date)
            #
        #

    def test_ne(self):
        """not equal"""
        for iteration in range(1, 1001):
            random_date = random_deterministic_date()
            with self.subTest(
                "compared to <-inf>", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(infdate.MIN != random_date)
            #
            with self.subTest(
                "compared to <inf>", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(infdate.MAX != random_date)
            #
            with self.subTest(
                "compared to itself", iteration=iteration, random_date=random_date
            ):
                self.assertFalse(infdate.MIN != infdate.MIN)
                self.assertFalse(infdate.MAX != infdate.MAX)
                self.assertFalse(random_date != random_date)
            #
        #

    def test_eq(self):
        """equal"""
        random_date = random_deterministic_date()
        with self.subTest("compared to <-inf>", random_date=random_date):
            self.assertFalse(infdate.MIN == random_date)
        #
        with self.subTest("compared to <inf>", random_date=random_date):
            self.assertFalse(infdate.MAX == random_date)
        #
        with self.subTest("compared to itself", random_date=random_date):
            self.assertTrue(infdate.MIN == infdate.MIN)
            self.assertTrue(infdate.MAX == infdate.MAX)
            self.assertTrue(random_date == random_date)
        #

    # pylint: enable=comparison-with-itself

    def test_bool(self):
        """bool(gd_instance) capability"""
        gd = infdate.GenericDate(3.579)
        self.assertFalse(gd)

    def test_hash(self):
        """bool(gd_instance) capability"""
        gd = infdate.GenericDate(0.5)
        self.assertEqual(hash(gd), hash("date with ordinal 0"))

    def test_repr(self):
        """repr(gd_instance) capability"""
        for base, expected_display in (
            (inf, "inf"),
            (-inf, "-inf"),
            (9.81, "9"),
            (314, "314"),
        ):
            gd = infdate.GenericDate(base)
            with self.subTest(
                "representation of",
                base=base,
                expected_display=expected_display,
            ):
                self.assertEqual(repr(gd), f"GenericDate({expected_display})")
            #
        #

    def test_str(self):
        """str(gd_instance) capability"""
        gd = infdate.GenericDate(777)
        mocked_isoformat_result = "[777]"
        with patch.object(gd, "isoformat") as mock_isoformat:
            mock_isoformat.return_value = mocked_isoformat_result
            result = str(gd)
            self.assertEqual(result, mocked_isoformat_result)
            mock_isoformat.assert_called_with()
        #

    def test_isoformat(self):
        """.isoformat() method"""
        gd = infdate.GenericDate(777)
        mocked_strftime_result = "[777]"
        with patch.object(gd, "strftime") as mock_strftime:
            mock_strftime.return_value = mocked_strftime_result
            result = str(gd)
            self.assertEqual(result, mocked_strftime_result)
            mock_strftime.assert_called_with(infdate.ISO_DATE_FORMAT)
        #

    def test_strftime(self):
        """.strftime() method"""
        gd = infdate.GenericDate(-inf)
        self.assertRaises(NotImplementedError, gd.strftime, "")

    def test_replace(self):
        """.replace() method"""
        gd = infdate.GenericDate(inf)
        self.assertRaises(NotImplementedError, gd.replace, year=1)


class GenericDateArithmetics(VerboseTestCase):
    """GenericDate objects - arithmetics"""

    # pylint: disable=protected-access ; ok for testing

    def test_add_days(self):
        """._add_days() method"""
        for base, delta, expected_result_ordinal, expected_call, expected_self in (
            (inf, -inf, -inf, -inf, False),
            (inf, inf, inf, None, True),
            (inf, 2.5, inf, None, True),
            (-inf, inf, inf, inf, False),
            (-inf, -inf, -inf, None, True),
            (-inf, 77.98, -inf, None, True),
            (9.81, inf, inf, inf, False),
            (9.81, -inf, -inf, -inf, False),
            (1.234, 7.89, 8, 8, False),
            (7.62, 0, 7, None, True),
            (1.234, -5.678, -4, -4, False),
            (3.14, -0, 3, None, True),
        ):
            with patch.object(infdate, "fromordinal") as mock_fromordinal:
                gd = infdate.GenericDate(base)
                mock_fromordinal.return_value = infdate.GenericDate(
                    expected_result_ordinal
                )
                result = gd._add_days(delta)
                with self.subTest(
                    "result",
                    base=base,
                    delta=delta,
                    expected_result_ordinal=expected_result_ordinal,
                ):
                    self.assertEqual(result.toordinal(), expected_result_ordinal)
                #
                if expected_call:
                    with self.subTest(
                        "fromordinal() call with",
                        base=base,
                        delta=delta,
                        expected_call=expected_call,
                    ):
                        mock_fromordinal.assert_called_with(expected_call)
                    #
                elif expected_self:
                    with self.subTest(
                        "self returned",
                        base=base,
                        delta=delta,
                        expected_self=expected_self,
                    ):
                        self.assertIs(result, gd)
                    #
                #
            #
        #

    def test_add_and_radd(self):
        """gd_instance + delta capability"""
        for base, delta in (
            (inf, inf),
            (inf, -inf),
            (inf, 2.5),
            (-inf, -inf),
            (-inf, inf),
            (-inf, 77.98),
            (9.81, -inf),
            (9.81, inf),
            (1.234, -7.89),
            (7.62, -0),
            (1.234, 5.678),
            (3.14, 0.0),
        ):
            gd = infdate.GenericDate(base)
            with patch.object(gd, "_add_days") as mock_adder:
                _ = gd + delta
                with self.subTest(
                    f"GenericDate({base}) + {delta} → Gen…()._add_days({delta}) call"
                ):
                    mock_adder.assert_called_with(delta)
                #
                _ = delta + gd
                with self.subTest(
                    f"{delta} + GenericDate({base}) → Gen…()._add_days({delta}) call"
                ):
                    mock_adder.assert_called_with(delta)
                #
            #
        #

    def test_sub_number(self):
        """gd_instance - number capability"""
        for base, delta, expected_result_ordinal, expected_call, expected_self in (
            (inf, inf, -inf, -inf, False),
            (inf, -inf, inf, None, True),
            (inf, 2.5, inf, None, True),
            (-inf, -inf, inf, inf, False),
            (-inf, inf, -inf, None, True),
            (-inf, 77.98, -inf, None, True),
            (9.81, -inf, inf, inf, False),
            (9.81, inf, -inf, -inf, False),
            (1.234, -7.89, 8, 7.89, False),
            (7.62, -0, 7, None, True),
            (1.234, 5.678, -4, -5.678, False),
            (3.14, 0.0, 3, None, True),
        ):
            gd = infdate.GenericDate(base)
            with patch.object(gd, "_add_days") as mock_adder:
                if expected_self:
                    mock_adder.return_value = gd
                else:
                    mock_adder.return_value = infdate.GenericDate(
                        expected_result_ordinal
                    )
                #
                result = gd - delta
                with self.subTest(
                    "result",
                    base=base,
                    delta=delta,
                    expected_result_ordinal=expected_result_ordinal,
                ):
                    self.assertEqual(result.toordinal(), expected_result_ordinal)
                #
                if expected_call:
                    with self.subTest(
                        "._add_days() call with",
                        base=base,
                        delta=delta,
                        expected_call=expected_call,
                    ):
                        mock_adder.assert_called_with(expected_call)
                    #
                elif expected_self:
                    with self.subTest(
                        "self returned",
                        base=base,
                        delta=delta,
                        expected_self=expected_self,
                    ):
                        self.assertIs(result, gd)
                    #
                #
            #
        #

    def test_sub_date(self):
        """gd_instance1 - gd_instance2 capability"""
        for first, second, expected_result in (
            (inf, inf, nan),
            (inf, -inf, inf),
            (inf, 2.5, inf),
            (-inf, -inf, nan),
            (-inf, inf, -inf),
            (-inf, 77.98, -inf),
            (9.81, -inf, inf),
            (9.81, inf, -inf),
            (1.234, -7.89, 8),
            (7.62, -0, 7),
            (1.234, 5.678, -4),
            (3.14, 0.0, 3),
        ):
            gd1 = infdate.GenericDate(first)
            gd2 = infdate.GenericDate(second)
            result = gd1 - gd2
            with self.subTest(
                "result",
                first=first,
                second=second,
                expected_result=expected_result,
            ):
                if isnan(expected_result):
                    self.assertTrue(isnan(result))
                else:
                    self.assertEqual(result, expected_result)
                #
            #
        #

    def test_sub_stdlib_date(self):
        """gd_instance - stdlib_date capability"""
        for gd_ordinal, stdlib_date_ordinal, expected_result in (
            (inf, 981, inf),
            (-inf, 733981, -inf),
            (12, 1234, -1222),
            (762, 1, 761),
            (99999.99, 7777, 92222),
        ):
            gd_instance = infdate.GenericDate(gd_ordinal)
            stdlib_date = datetime.date.fromordinal(stdlib_date_ordinal)
            result = gd_instance - stdlib_date
            with self.subTest(
                "result",
                gd_ordinal=gd_ordinal,
                stdlib_date_ordinal=stdlib_date_ordinal,
                expected_result=expected_result,
            ):
                self.assertEqual(result, expected_result)
            #
        #

    def test_rsub_stdlib_date(self):
        """stdlib_date - gd_instance capability"""
        for stdlib_date_ordinal, gd_ordinal, expected_result in (
            (981, -inf, inf),
            (981, inf, -inf),
            (1234, -7.89, 1241),
            (762, -0, 762),
            (1234, 5.678, 1229),
            (314, 0.0, 314),
        ):
            stdlib_date = datetime.date.fromordinal(stdlib_date_ordinal)
            gd_instance = infdate.GenericDate(gd_ordinal)
            result = stdlib_date - gd_instance
            with self.subTest(
                "result",
                stdlib_date_ordinal=stdlib_date_ordinal,
                gd_ordinal=gd_ordinal,
                expected_result=expected_result,
            ):
                self.assertEqual(result, expected_result)
            #
        #


class InfinityDate(VerboseTestCase):
    """InfinityDate class"""

    def test_repr(self):
        """repr(id_instance) capability"""
        for params, expected_result in (
            ({}, "InfinityDate(past_bound=False)"),
            ({"past_bound": False}, "InfinityDate(past_bound=False)"),
            ({"past_bound": True}, "InfinityDate(past_bound=True)"),
        ):
            infd = infdate.InfinityDate(**params)
            with self.subTest(
                "representation", params=params, expected_result=expected_result
            ):
                self.assertEqual(repr(infd), expected_result)
            #
        #

    def test_strftime(self):
        """.strftime() method"""
        for past_bound, expected_result in (
            (False, "<inf>"),
            (True, "<-inf>"),
        ):
            infd = infdate.InfinityDate(past_bound=past_bound)
            with self.subTest(
                "strftime", past_bound=past_bound, expected_result=expected_result
            ):
                self.assertEqual(infd.strftime(""), expected_result)
            #
        #

    def test_replace(self):
        """.replace() method"""
        infd = infdate.InfinityDate()
        self.assertRaisesRegex(
            TypeError,
            r"^InfinityDate instances do not support .replace\(\)$",
            infd.replace,
            month=12,
        )


class RealDate(VerboseTestCase):
    """RealDate class"""

    def test_attributes(self):
        """initinalization and attributes"""
        for year, month, day in (
            (1996, 6, 25),
            (1, 1, 1),
            (9999, 12, 31),
        ):
            rd = infdate.RealDate(year, month, day)
            with self.subTest("year attribute", rd=rd, year=year):
                self.assertEqual(rd.year, year)
            #
            with self.subTest("month attribute", rd=rd, month=month):
                self.assertEqual(rd.month, month)
            #
            with self.subTest("day attribute", rd=rd, day=day):
                self.assertEqual(rd.day, day)
            #
        #
        for invalid_year in (-327, 0, 10000):
            with self.subTest("value error", invalid_year=invalid_year):
                self.assertRaises(ValueError, infdate.RealDate, invalid_year, 1, 1)
            #
        #

    def test_proxied_methods(self):
        """Method proxied from datetime.date:
        self.timetuple = self.__wrapped_date_object.timetuple
        self.weekday = self.__wrapped_date_object.weekday
        self.isoweekday = self.__wrapped_date_object.isoweekday
        self.isocalendar = self.__wrapped_date_object.isocalendar
        self.ctime = self.__wrapped_date_object.ctime
        """
        rd = infdate.RealDate(2025, 6, 25)
        for method_name, expected_result in (
            ("timetuple", struct_time((2025, 6, 25, 0, 0, 0, 2, 176, -1))),
            ("weekday", 2),
            ("isoweekday", 3),
            ("isocalendar", (2025, 26, 3)),
            ("ctime", "Wed Jun 25 00:00:00 2025"),
        ):
            with self.subTest(method_name, expected_result=expected_result):
                if isinstance(expected_result, tuple):
                    self.assertTupleEqual(getattr(rd, method_name)(), expected_result)
                else:
                    self.assertEqual(getattr(rd, method_name)(), expected_result)
                #
            #
        #

    def test_repr(self):
        """repr(rd_instance) capability"""
        for year, month, day, expected_parentheses_content in (
            (1996, 6, 25, "1996, 6, 25"),
            (1, 1, 1, "1, 1, 1"),
            (9999, 12, 31, "9999, 12, 31"),
        ):
            rd = infdate.RealDate(year, month, day)
            with self.subTest(
                "representation",
                year=year,
                month=month,
                day=day,
                expected_parentheses_content=expected_parentheses_content,
            ):
                self.assertEqual(repr(rd), f"RealDate({expected_parentheses_content})")
            #
        #

    def test_bool(self):
        """bool(rd_instance) capabiliry"""
        for year, month, day in (
            (1996, 6, 25),
            (1, 1, 1),
            (9999, 12, 31),
        ):
            with self.subTest("bool", year=year, month=month, day=day):
                self.assertTrue(infdate.RealDate(year, month, day))
            #
        #

    # pylint: disable=protected-access ; required for testing

    def test_strftime(self):
        """.strftime() method"""
        for year, month, day, format_, expected_result in (
            (1996, 6, 25, "", "1996-06-25"),
            (1, 2, 3, "%m/%d/%y", "3/2/01"),
            (9999, 12, 31, "%d.%m.%y", "31.12.99"),
        ):
            rd = infdate.RealDate(year, month, day)
            with patch.object(rd, "_wrapped_date_object") as mock_date:
                mock_date.strftime.return_value = expected_result
                result = rd.strftime(format_)
                with self.subTest(
                    "result value",
                    rd=rd,
                    format_=format_,
                    expected_result=expected_result,
                ):
                    self.assertEqual(result, expected_result)
                #
                with self.subTest(
                    "mocked_call",
                    rd=rd,
                    format_=format_,
                    expected_result=expected_result,
                ):
                    self.assertListEqual(
                        mock_date.mock_calls,
                        [call.strftime(format_ or infdate.ISO_DATE_FORMAT)],
                    )
                #
            #
        #

    def test_replace(self):
        """.strftime() method"""
        for year, month, day, replace_args, expected_result in (
            (1996, 6, 25, {"month": 1}, infdate.RealDate(1996, 1, 25)),
            (1, 2, 3, {"day": 28}, infdate.RealDate(1, 2, 28)),
            (9999, 12, 31, {"year": 2023, "month": 7}, infdate.RealDate(2023, 7, 31)),
        ):
            with patch.object(infdate, "from_datetime_object") as mock_factory:
                rd = infdate.RealDate(year, month, day)
                mock_factory.return_value = expected_result
                result = rd.replace(**replace_args)
                with self.subTest(
                    "result value",
                    rd=rd,
                    replace_args=replace_args,
                    expected_result=expected_result,
                ):
                    self.assertEqual(result, expected_result)
                #
                internal_replace_args = {
                    "year": expected_result.year,
                    "month": expected_result.month,
                    "day": expected_result.day,
                }
                with self.subTest(
                    "mocked_call",
                    rd=rd,
                    replace_args=replace_args,
                    internal_replace_args=internal_replace_args,
                ):
                    mock_factory.assert_called_with(
                        rd._wrapped_date_object.replace(**internal_replace_args)
                    )
                #
            #
        #

    def test_random_date_within_limits(self):
        """The following relation
        infdate.MIN < infdate.REAL_MIN <= real_date_instance <= …
        … infdate.REAL_MAX < infdate.MAX
        should always be True
        """
        for iteration in range(1, 10000):
            random_date = random_deterministic_date()
            with self.subTest(
                "date within limits", iteration=iteration, random_date=random_date
            ):
                self.assertTrue(
                    infdate.MIN
                    < infdate.REAL_MIN
                    <= random_date
                    <= infdate.REAL_MAX
                    < infdate.MAX
                )
            #
        #


class FactoryFunctions(VerboseTestCase):
    """Factory functions in the module"""

    @patch.object(infdate, "RealDate")
    def test_from_datetime_object(self, mock_real_date):
        """from_datetime_object() factory function"""
        for year, month, day in (
            (1996, 6, 25),
            (1, 1, 1),
            (9999, 12, 31),
        ):
            mocked_date = Mock(year=year, month=month, day=day)
            infdate.from_datetime_object(mocked_date)
            mock_real_date.assert_called_with(year, month, day)
        #

    def test_from_native_type(self):
        """from_native_type() factory function"""
        for native_data, params, expected_result in (
            ("2022-12-31T23:59:59.321Z", {}, (2022, 12, 31)),
            ("2023-05-23T11:00:15.654321Z", {}, (2023, 5, 23)),
            ("2008-04-06", {"fmt": "%Y-%m-%d"}, (2008, 4, 6)),
            (inf, {}, infdate.MAX),
            (-inf, {}, infdate.MIN),
            (None, {}, infdate.MAX),
            (None, {"past_bound": False}, infdate.MAX),
            (None, {"past_bound": True}, infdate.MIN),
        ):
            if isinstance(native_data, str):
                with (
                    patch("infdate.datetime") as mock_datetime,
                    patch.object(infdate, "from_datetime_object") as mock_factory,
                ):
                    with self.subTest(
                        "Real date",
                        native_data=native_data,
                        params=params,
                        expected_result=expected_result,
                    ):
                        mocked_intermediate_result = Mock()
                        mock_datetime.strptime.return_value = mocked_intermediate_result
                        mock_factory.return_value = expected_result
                        result = infdate.from_native_type(native_data, **params)
                        mock_datetime.strptime.assert_called_with(
                            native_data,
                            params.get("fmt", infdate.ISO_DATETIME_FORMAT_UTC),
                        )
                        mock_factory.assert_called_with(mocked_intermediate_result)
                        self.assertEqual(result, expected_result)
                    #
                #
            else:
                with self.subTest(
                    "Infinity",
                    native_data=native_data,
                    params=params,
                    expected_result=expected_result,
                ):
                    self.assertIs(
                        infdate.from_native_type(native_data, **params), expected_result
                    )
                #
            #
        #
        for source in (1, -7, 3.5, True, False):
            with self.subTest("unhandled value", source=source):
                self.assertRaisesRegex(
                    ValueError,
                    f"^Don’t know how to convert {source!r} into a date$",
                    infdate.from_native_type,
                    source,
                )
            #
        #

    @patch("infdate.date")
    @patch.object(infdate, "from_datetime_object")
    def test_fromtimestamp(self, mock_factory, mock_date):
        """test_fromtimestamp() factory function"""
        for timestamp, expected_result in (
            (-inf, infdate.MIN),
            (inf, infdate.MAX),
            (1e500, infdate.MAX),
        ):
            with self.subTest(
                "infinity", timestamp=timestamp, expected_result=expected_result
            ):
                self.assertIs(infdate.fromtimestamp(timestamp), expected_result)
            #
        #
        for stdlib_date in (
            datetime.date.min,
            datetime.date(1000, 1, 1),
            datetime.date(2022, 2, 22),
            datetime.date.max,
        ):
            timestamp = mktime(stdlib_date.timetuple())
            with self.subTest(
                "regular_result", timestamp=timestamp, stdlib_date=stdlib_date
            ):
                mocked_final_result = Mock(
                    year=stdlib_date.year, month=stdlib_date.month, day=stdlib_date.day
                )
                mock_date.fromtimestamp.return_value = stdlib_date
                mock_factory.return_value = mocked_final_result
                self.assertEqual(infdate.fromtimestamp(timestamp), mocked_final_result)
                mock_date.fromtimestamp.assert_called_with(timestamp)
                mock_factory.assert_called_with(stdlib_date)
            #
        #

    def test_fromtimestamp_errors(self):
        """test_fromtimestamp() factory function errors"""
        for timestamp in (
            mktime(datetime.date.min.timetuple()) - 1,
            mktime(datetime.date.max.timetuple()) + 86400,
        ):
            with self.subTest(
                "unsupported date, re-raised value error", timestamp=timestamp
            ):
                self.assertRaises(
                    ValueError,
                    infdate.fromtimestamp,
                    timestamp,
                )
            #
        #

    @patch("infdate.date")
    @patch.object(infdate, "from_datetime_object")
    def test_fromordinal(self, mock_factory, mock_date):
        """fromordinal() factory function"""
        for ordinal, expected_result in (
            (-inf, infdate.MIN),
            (inf, infdate.MAX),
            (1e500, infdate.MAX),
        ):
            with self.subTest(
                "infinity", ordinal=ordinal, expected_result=expected_result
            ):
                self.assertIs(infdate.fromordinal(ordinal), expected_result)
            #
        #
        for ordinal, intermediate_result in (
            (2.1, datetime.date(1, 1, 2)),
            (730120.0, datetime.date(2000, 1, 1)),
        ):
            with self.subTest(
                "fromordinal", ordinal=ordinal, intermediate_result=intermediate_result
            ):
                mocked_final_result = Mock()
                mock_date.fromordinal.return_value = intermediate_result
                mock_factory.return_value = mocked_final_result
                self.assertEqual(infdate.fromordinal(ordinal), mocked_final_result)
                mock_date.fromordinal.assert_called_with(int(ordinal))
                mock_factory.assert_called_with(intermediate_result)
            #
        #
        default_overflow_re = "^RealDate value out of range$"
        for ordinal, exception_class, error_re in (
            (-1, OverflowError, default_overflow_re),
            (0, OverflowError, default_overflow_re),
            (1234567890, OverflowError, default_overflow_re),
            (nan, ValueError, _NAN_INT_CONVERSION_ERROR_RE),
        ):
            with self.subTest("overflow error", ordinal=ordinal):
                self.assertRaisesRegex(
                    exception_class,
                    error_re,
                    infdate.fromordinal,
                    ordinal,
                )
            #
        #

    @patch.object(infdate, "date")
    @patch.object(infdate, "from_datetime_object")
    def test_fromisoformat(self, mock_factory, mock_date):
        """fromisoformat() factory function"""
        for source, expected_object in (
            ("<inf>", infdate.MAX),
            ("<-inf>", infdate.MIN),
        ):
            with self.subTest(
                "fromisoformat", source=source, expected_object=expected_object
            ):
                self.assertIs(infdate.fromisoformat(source), expected_object)
            #
        #
        for source, expected_date in (
            ("2019-12-04", datetime.date(2019, 12, 4)),
            ("20191204", datetime.date(2019, 12, 4)),
            ("2021-W01-1", datetime.date(2021, 1, 4)),
        ):
            with self.subTest(
                "fromisoformat", source=source, expected_date=expected_date
            ):
                mock_date.fromisoformat.return_value = expected_date
                infdate.fromisoformat(source)
                mock_date.fromisoformat.assert_called_with(source)
                mock_factory.assert_called_with(expected_date)
            #
        #

    @patch.object(infdate, "date")
    @patch.object(infdate, "from_datetime_object")
    def test_fromisocalendar(self, mock_factory, mock_date):
        """fromisocalendar() factory function"""
        for year, week, weekday, expected_date in (
            (2004, 1, 1, datetime.date(2003, 12, 29)),
            (2004, 1, 7, datetime.date(2004, 1, 4)),
            (2004, 53, 3, datetime.date(2004, 12, 29)),
        ):
            with self.subTest(
                "fromisocalendar",
                year=year,
                week=week,
                weekday=weekday,
                expected_date=expected_date,
            ):
                mock_date.fromisocalendar.return_value = expected_date
                infdate.fromisocalendar(year, week, weekday)
                mock_date.fromisocalendar.assert_called_with(year, week, weekday)
                mock_factory.assert_called_with(expected_date)
            #
        #

    @patch.object(infdate, "date")
    @patch.object(infdate, "from_datetime_object")
    def test_today(self, mock_factory, mock_date):
        """today() factory function"""
        mocked_date = Mock(year=2025, month=6, day=17)
        mock_date.today.return_value = mocked_date
        infdate.today()
        mock_date.today.assert_called_with()
        mock_factory.assert_called_with(mocked_date)
