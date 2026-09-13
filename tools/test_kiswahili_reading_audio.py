import unittest

from generate_kiswahili_reading_audio import rewrite_for_reading, roman_to_int


class ReadingRewriteTests(unittest.TestCase):
    def assert_rewrite(self, original: str, expected: str, text_id: str | None = None) -> None:
        spoken, changes = rewrite_for_reading(original, text_id)
        self.assertEqual(spoken, expected)
        self.assertTrue(changes)

    def test_roman_numerals(self) -> None:
        self.assert_rewrite("(i) lala fofofo", "moja. lala fofofo")
        self.assert_rewrite("(iv) kale", "nne. kale")
        self.assert_rewrite("(xiii) swali", "kumi na tatu. swali")
        self.assert_rewrite("iv. Salamu ya awali", "nne. Salamu ya awali")

    def test_letter_labels(self) -> None:
        self.assert_rewrite("A.", "aa")
        self.assert_rewrite("b. mlo wa asubuhi", "bee. mlo wa asubuhi")
        self.assert_rewrite("c. cheni", "chee. cheni")
        self.assert_rewrite("(c) cheni", "chee. cheni")
        self.assert_rewrite("(d) fedha", "dee. fedha")

    def test_kifungu_references(self) -> None:
        self.assert_rewrite(
            "Oanisha Kifungu A na Kifungu B",
            "Oanisha Kifungu aa na Kifungu bee",
        )

    def test_blank_marker(self) -> None:
        self.assert_rewrite("(ii) Jibu [[blank:item-2]]", "mbili. Jibu dash")

    def test_scoped_ellipsis_blank(self) -> None:
        self.assert_rewrite(
            "1. …….. walipokuwa ……..",
            "1. dash walipokuwa dash",
            "pg088_n0021",
        )

    def test_input_blank(self) -> None:
        self.assert_rewrite("(a)", "aa. dash", "pg105_n0064")

    def test_sample_separator(self) -> None:
        self.assert_rewrite(
            "Mfano: moyo – mioyo",
            "Mfano: moyo, dash, mioyo",
            "pg109_n0004",
        )

    def test_repeat_and_range(self) -> None:
        self.assert_rewrite("Sema x 2", "Sema mara mbili")
        self.assert_rewrite("jedwali la 1- 8", "jedwali la moja hadi nane")

    def test_supplement_content_is_recorded(self) -> None:
        spoken, changes = rewrite_for_reading(
            "Andika kwa usahihi maneno yaliyokosewa.", "pg097_n0057"
        )
        self.assertEqual(spoken, "Andika kwa usahihi maneno yaliyokosewa.")
        self.assertIn("supplement", changes)

    def test_page_12_accessible_table_audio(self) -> None:
        spoken, changes = rewrite_for_reading(
            "Tunga sentensi kumi kwa kutumia jedwali lifuatalo:", "pg011_n0003"
        )
        self.assertIn("Jedwali lina safu tatu na mistari mitano", spoken)
        self.assertEqual(changes, ("accessible_context",))

        easy_spoken, easy_changes = rewrite_for_reading(
            "Tunga sentensi 10 kwa kutumia jedwali hili:",
            "pg011_n0003_easy_read",
        )
        self.assertEqual(easy_spoken, spoken)
        self.assertEqual(easy_changes, changes)

    def test_generated_table_context_wraps_existing_rewrite(self) -> None:
        import generate_kiswahili_reading_audio as audio

        original_loader = audio.load_table_audio_contexts
        try:
            audio.load_table_audio_contexts = lambda: {
                "pg999_n0001": {
                    "prefix": "Mstari wa kwanza, safu ya pili.",
                    "suffix": "Jedwali lina safu mbili.",
                }
            }
            spoken, changes = audio.rewrite_for_reading("(iv)", "pg999_n0001")
            self.assertEqual(
                spoken,
                "Mstari wa kwanza, safu ya pili. nne Jedwali lina safu mbili.",
            )
            self.assertIn("roman", changes)
            self.assertIn("table_context", changes)
        finally:
            audio.load_table_audio_contexts = original_loader

    def test_non_label_abbreviation_is_unchanged(self) -> None:
        spoken, changes = rewrite_for_reading("S.L.P. 35094")
        self.assertEqual(spoken, "S.L.P. 35094")
        self.assertEqual(changes, ())

    def test_invalid_roman_is_rejected(self) -> None:
        self.assertIsNone(roman_to_int("iix"))


if __name__ == "__main__":
    unittest.main()
