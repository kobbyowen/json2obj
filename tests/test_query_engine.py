import unittest

from json_object_mapper import JSONObjectMapper


class TestQueryEngine(unittest.TestCase):
    def setUp(self):
        self.data = {
            "users": [
                {
                    "name": "Kobby",
                    "age": 29,
                    "skills": ["python", "aws"],
                    "score": 91.5,
                    "active": True,
                    "nickname": None,
                    "profile": {
                        "preferences": {
                            "theme": "dark",
                            "notifications": {"email": True, "sms": False},
                        },
                        "addresses": [
                            {"city": "Accra", "geo": {"lat": 5.6037, "lng": -0.187}},
                            {"city": "Kumasi", "geo": {"lat": 6.6885, "lng": -1.6244}},
                        ],
                    },
                    "projects": [
                        {
                            "name": "atlas",
                            "repos": [
                                {"name": "api", "stars": 120},
                                {"name": "worker", "stars": 55},
                            ],
                        },
                        {
                            "name": "pulse",
                            "repos": [{"name": "dashboard", "stars": 80}],
                        },
                    ],
                },
                {
                    "name": "Ama",
                    "age": 22,
                    "skills": ["design"],
                    "score": 88.0,
                    "active": False,
                    "nickname": "A",
                    "profile": {
                        "preferences": {
                            "theme": "light",
                            "notifications": {"email": False, "sms": True},
                        },
                        "addresses": [{"city": "Tamale", "geo": {"lat": 9.4075, "lng": -0.8533}}],
                    },
                    "projects": [
                        {
                            "name": "canvas",
                            "repos": [{"name": "ui-kit", "stars": 65}],
                        }
                    ],
                },
                {
                    "name": "Jo",
                    "skills": [],
                    "active": True,
                    "profile": {"preferences": {"theme": "dark"}},
                    "projects": [],
                },
            ],
            "teams": {
                "backend": [{"name": "Kobby"}],
                "design": [{"name": "Ama"}],
            },
        }
        self.obj = JSONObjectMapper(self.data)

    def test_query_wildcard_names(self):
        self.assertEqual(self.obj.query("users[*].name"), ["Kobby", "Ama", "Jo"])

    def test_query_filter(self):
        self.assertEqual(self.obj.query("users[?age > 25].name"), ["Kobby"])

    def test_query_nested_wildcard_flatten(self):
        self.assertEqual(self.obj.query("users[*].skills[*]"), ["python", "aws", "design"])

    def test_query_first(self):
        self.assertEqual(self.obj.query("users[0].name", first=True), "Kobby")

    def test_query_default(self):
        self.assertEqual(self.obj.query("invalid.path", default=[]), [])

    def test_exists(self):
        self.assertTrue(self.obj.exists("users[0].name"))

    def test_count(self):
        self.assertEqual(self.obj.count("users[*]"), 3)

    def test_compile(self):
        compiled = self.obj.compile("users[*].name")
        self.assertEqual(compiled(self.obj), ["Kobby", "Ama", "Jo"])

    def test_query_safe_missing_branch(self):
        self.assertEqual(self.obj.query("users[*].profile.preferences.locale.timezone"), [])

    def test_query_out_of_range_index(self):
        self.assertEqual(self.obj.query("users[99].name"), [])

    def test_query_filter_string_equals(self):
        self.assertEqual(self.obj.query("users[?name == 'Ama'].name"), ["Ama"])

    def test_query_filter_not_equals(self):
        self.assertEqual(self.obj.query("users[?name != 'Ama'].name"), ["Kobby", "Jo"])

    def test_query_filter_boolean(self):
        self.assertEqual(self.obj.query("users[?active == true].name"), ["Kobby", "Jo"])

    def test_query_filter_null(self):
        self.assertEqual(self.obj.query("users[?nickname == null].name"), ["Kobby"])

    def test_query_filter_float(self):
        self.assertEqual(self.obj.query("users[?score >= 90.0].name"), ["Kobby"])

    def test_query_invalid_filter_is_safe(self):
        self.assertEqual(self.obj.query("users[?age ~~ 10].name"), [])

    def test_query_root_dict_wildcard(self):
        self.assertEqual(self.obj.query("teams.*[*].name"), ["Kobby", "Ama"])

    def test_query_first_without_default(self):
        self.assertIsNone(self.obj.query("users[99].name", first=True))

    def test_query_first_with_default(self):
        self.assertEqual(self.obj.query("users[99].name", first=True, default="missing"), "missing")

    def test_exists_false(self):
        self.assertFalse(self.obj.exists("users[?age < 0].name"))

    def test_compile_rejects_non_mapper(self):
        compiled = self.obj.compile("users[*].name")
        with self.assertRaises(TypeError):
            compiled({"users": []})

    def test_compile_reusable_on_another_mapper(self):
        compiled = self.obj.compile("users[*].name")
        another = JSONObjectMapper({"users": [{"name": "Esi"}]})
        self.assertEqual(compiled(another), ["Esi"])

    def test_query_deep_property_path(self):
        self.assertEqual(self.obj.query("users[0].profile.preferences.theme"), ["dark"])

    def test_query_deep_index_access(self):
        self.assertEqual(self.obj.query("users[0].profile.addresses[1].geo.lat"), [6.6885])

    def test_query_multi_wildcard_deep_flatten(self):
        self.assertEqual(
            self.obj.query("users[*].projects[*].repos[*].name"),
            ["api", "worker", "dashboard", "ui-kit"],
        )

    def test_query_filter_then_deep_path(self):
        self.assertEqual(self.obj.query("users[?age >= 25].profile.preferences.theme"), ["dark"])


if __name__ == "__main__":
    unittest.main()
