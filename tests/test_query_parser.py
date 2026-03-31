import unittest

from json_object_mapper.query import (
    apply_filter,
    coerce_condition_value,
    compare,
    parse_condition,
    tokenize,
)


class TestQueryParser(unittest.TestCase):
    def test_tokenize_index_and_property(self):
        self.assertEqual(tokenize("users[0].name"), ["users", 0, "name"])

    def test_tokenize_wildcard(self):
        self.assertEqual(tokenize("users[*].name"), ["users", "*", "name"])

    def test_tokenize_filter(self):
        self.assertEqual(tokenize("users[?age > 25]"), ["users", {"filter": "age > 25"}])

    def test_parse_condition(self):
        self.assertEqual(parse_condition("age >= 25"), ("age", ">=", 25))

    def test_apply_filter(self):
        items = [
            {"name": "Kobby", "age": 29},
            {"name": "Ama", "age": 22},
        ]
        self.assertEqual(apply_filter(items, "age > 25"), [{"name": "Kobby", "age": 29}])

    def test_tokenize_unclosed_bracket_raises(self):
        with self.assertRaises(ValueError):
            tokenize("users[0")

    def test_tokenize_empty_filter_raises(self):
        with self.assertRaises(ValueError):
            tokenize("users[?]")

    def test_tokenize_unsupported_bracket_token_raises(self):
        with self.assertRaises(ValueError):
            tokenize("users[abc]")

    def test_parse_condition_with_string_value(self):
        self.assertEqual(parse_condition("name == 'Ama'"), ("name", "==", "Ama"))

    def test_parse_condition_with_float_value(self):
        self.assertEqual(parse_condition("score >= 91.5"), ("score", ">=", 91.5))

    def test_parse_condition_with_bool_and_null(self):
        self.assertEqual(parse_condition("active == true"), ("active", "==", True))
        self.assertEqual(parse_condition("nickname == null"), ("nickname", "==", None))

    def test_parse_condition_invalid_operator_raises(self):
        with self.assertRaises(ValueError):
            parse_condition("age ~~ 10")

    def test_coerce_condition_value_negative_int(self):
        self.assertEqual(coerce_condition_value("-42"), -42)

    def test_compare_type_error_is_false(self):
        self.assertFalse(compare("abc", ">", 10))

    def test_apply_filter_skips_non_dict_items(self):
        items = [{"age": 10}, "invalid", 2, {"age": 30}]
        self.assertEqual(apply_filter(items, "age >= 20"), [{"age": 30}])


if __name__ == "__main__":
    unittest.main()
