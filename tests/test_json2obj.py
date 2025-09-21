import unittest

from json2obj import JSONAccessError, JSONObjectMapper


class TestJSONObjectMapper(unittest.TestCase):
    def test_attr_access(self):
        m = JSONObjectMapper({"a": {"b": 1}})
        self.assertEqual(m.a.b, 1)

    def test_list_indexing(self):
        m = JSONObjectMapper({"xs": [{"v": 1}, {"v": 2}]})
        self.assertEqual(m.xs[1].v, 2)

    def test_invalid_attr(self):
        m = JSONObjectMapper({"a": 1})
        with self.assertRaises(JSONAccessError):
            _ = m.not_here

    def test_non_identifier_key(self):
        m = JSONObjectMapper({"not-valid!": 3})
        self.assertEqual(m.get("not-valid!"), 3)
        with self.assertRaises(JSONAccessError):
            _ = getattr(m, "not-valid!")

    def test_set_readonly(self):
        m = JSONObjectMapper({"a": 1}, readonly=True)
        with self.assertRaises(AttributeError):
            m.a = 2
        with self.assertRaises(AttributeError):
            m["a"] = 2

    def test_merge(self):
        m = JSONObjectMapper({"a": 1})
        m.merge({"b": 2})
        self.assertEqual(m.b, 2)

    def test_to_from_json(self):
        m = JSONObjectMapper.from_json('{"x": 7, "y": {"z": 9}}')
        self.assertEqual(m.y.z, 9)
        s = m.to_json()
        self.assertIn('"x": 7', s)

    def test_get_path(self):
        m = JSONObjectMapper({"u": {"n": {"a": [{"me": "k"}]}}})
        self.assertEqual(m.get_path("u.n.a[0].me"), "k")
        self.assertEqual(m.get_path("u.missing", default=None), None)

    def test_default_factory_no_autocreate(self):
        m = JSONObjectMapper({}, default_factory=dict)
        self.assertEqual(m.profile.to_dict(), {})
        self.assertNotIn("profile", m.to_dict())

    def test_default_factory_with_autocreate(self):
        m = JSONObjectMapper({}, default_factory=dict, autocreate_missing=True)
        _ = m.profile
        self.assertIn("profile", m.to_dict())
        m.profile.settings = {"theme": "dark"}
        self.assertEqual(m.get_path("profile.settings.theme"), "dark")

    def test_default_factory_readonly(self):
        m = JSONObjectMapper({}, default_factory=dict, autocreate_missing=True, readonly=True)
        _ = m.profile
        self.assertNotIn("profile", m.to_dict())

    def test_set_path_simple_create_parents(self):
        m = JSONObjectMapper({})
        m.set_path("a.b[0].c", 10)
        self.assertEqual(m.get_path("a.b[0].c"), 10)
        self.assertEqual(m.to_dict(), {"a": {"b": [{"c": 10}]}})

    def test_set_path_replace_value(self):
        m = JSONObjectMapper({"a": {"b": [{"c": 1}]}})
        m.set_path("a.b[0].c", 2)
        self.assertEqual(m.get_path("a.b[0].c"), 2)

    def test_set_path_no_create_parents_errors(self):
        m = JSONObjectMapper({})
        with self.assertRaises(KeyError):
            m.set_path("a.b.c", 1, create_parents=False)
        m = JSONObjectMapper({"a": {}})
        with self.assertRaises(TypeError):
            m.set_path("a[0].c", 1, create_parents=False)
        m = JSONObjectMapper({"a": {"b": []}})
        with self.assertRaises(IndexError):
            m.set_path("a.b[2].c", 1, create_parents=False)

    def test_set_path_list_growth(self):
        m = JSONObjectMapper({"xs": []})
        m.set_path("xs[2]", 99)
        self.assertEqual(m.to_dict(), {"xs": [None, None, 99]})

    def test_del_path_dict_key(self):
        m = JSONObjectMapper({"a": {"b": 1, "c": 2}})
        m.del_path("a.b")
        self.assertEqual(m.to_dict(), {"a": {"c": 2}})

    def test_del_path_list_index(self):
        m = JSONObjectMapper({"xs": [10, 20, 30]})
        m.del_path("xs[1]")
        self.assertEqual(m.to_dict(), {"xs": [10, 30]})

    def test_del_path_missing_silent(self):
        m = JSONObjectMapper({"a": {"b": 1}})
        m.del_path("a.c")
        self.assertEqual(m.to_dict(), {"a": {"b": 1}})

    def test_del_path_missing_raise(self):
        m = JSONObjectMapper({"a": {"b": 1}})
        with self.assertRaises(KeyError):
            m.del_path("a.c", raise_on_missing=True)
        m2 = JSONObjectMapper({"xs": [1]})
        with self.assertRaises(IndexError):
            m2.del_path("xs[5]", raise_on_missing=True)

    def test_set_path_readonly_raises(self):
        m = JSONObjectMapper({}, readonly=True)
        with self.assertRaises(AttributeError):
            m.set_path("a.b", 1)

    def test_del_path_readonly_raises(self):
        m = JSONObjectMapper({"a": {"b": 1}}, readonly=True)
        with self.assertRaises(AttributeError):
            m.del_path("a.b")


if __name__ == "__main__":
    unittest.main()
