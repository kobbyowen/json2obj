import unittest

from json_object_mapper import JSONObjectMapper, QueryableList


class TestQueryableList(unittest.TestCase):
    def setUp(self):
        self.data = {
            "users": [
                {"name": "Kobby", "age": 29, "profile": {"age": 29, "city": "Accra"}},
                {"name": "Ama", "age": 22, "profile": {"age": 22, "city": "Tamale"}},
                {"name": "Kobby", "age": 35, "profile": {"age": 35, "city": "Kumasi"}},
            ]
        }
        self.obj = JSONObjectMapper(self.data)

    def test_users_is_queryable_list(self):
        self.assertIsInstance(self.obj.users, QueryableList)

    def test_filter_eq(self):
        results = self.obj.users.filter(name="Ama")
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().name, "Ama")

    def test_filter_operator_gt(self):
        results = self.obj.users.filter(age__gt=25)
        self.assertEqual([item.name for item in results], ["Kobby", "Kobby"])

    def test_filter_operator_lte(self):
        results = self.obj.users.filter(age__lte=29)
        self.assertEqual([item.name for item in results], ["Kobby", "Ama"])

    def test_filter_multiple_conditions(self):
        results = self.obj.users.filter(name="Kobby", age__gte=30)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().age, 35)

    def test_filter_chainable(self):
        result = self.obj.users.filter(age__gt=20).filter(name="Kobby")
        self.assertIsInstance(result, QueryableList)
        self.assertEqual([item.age for item in result], [29, 35])

    def test_get_single(self):
        result = self.obj.users.get(name="Ama")
        self.assertEqual(result.age, 22)

    def test_get_no_match_raises(self):
        with self.assertRaises(ValueError):
            self.obj.users.get(name="Missing")

    def test_get_multiple_match_raises(self):
        with self.assertRaises(ValueError):
            self.obj.users.get(name="Kobby")

    def test_first_last(self):
        self.assertEqual(self.obj.users.first().name, "Kobby")
        self.assertEqual(self.obj.users.last().name, "Kobby")

    def test_count(self):
        self.assertEqual(self.obj.users.count(), 3)

    def test_nested_field_support(self):
        results = self.obj.users.filter(profile__age__gt=30)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().name, "Kobby")

    def test_nested_field_missing_is_safe(self):
        results = self.obj.users.filter(profile__country="GH")
        self.assertEqual(results.count(), 0)

    def test_queryable_list_on_nested_list(self):
        mapped = JSONObjectMapper({"groups": [{"members": [{"name": "A"}, {"name": "B"}]}]})
        members = mapped.groups[0].members
        self.assertIsInstance(members, QueryableList)
        self.assertEqual(members.filter(name="B").first().name, "B")


if __name__ == "__main__":
    unittest.main()
