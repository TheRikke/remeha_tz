from unittest import TestCase, mock

from datamap import Translator, datamap


def needs_translation(string_to_test):
    if string_to_test.startswith('unknown') or string_to_test == '-':
        return False
    return True


class TestTranslator(TestCase):
    def test_datamap_translation_en(self):
        """
        Test that all entries in datamap have english translations
        """
        with mock.patch('datamap.locale') as locale_mock:
            locale_mock.getdefaultlocale.return_value = ['en_US', 'UTF8']
            translator = Translator()
            for datamap_entry in datamap:
                value_type_name = datamap_entry[2]
                if isinstance(value_type_name, list):
                    for sub_value_type_name in value_type_name:
                        if needs_translation(sub_value_type_name):
                            self.assertTrue(translator.has_translation(sub_value_type_name),
                                            msg='No english translation for "{}"'.format(sub_value_type_name))
                else:
                    if needs_translation(value_type_name):
                        self.assertTrue(translator.has_translation(value_type_name),
                                        msg='No english translation for "{}"'.format(value_type_name))
                    if isinstance(datamap_entry[4], dict):
                        for select_entry in datamap_entry[4]:
                            if needs_translation(datamap_entry[4][select_entry]):
                                self.assertTrue(translator.has_translation(datamap_entry[4][select_entry]),
                                                msg='No english translation for "{}"'.format(datamap_entry[4][select_entry]))


    def test_datamap_translation_de(self):
        """
        Test that all entries in datamap have english translations
        """
        with mock.patch('datamap.locale') as locale_mock:
            locale_mock.getdefaultlocale.return_value = ['de_DE', 'UTF8']
            translator = Translator()
            for datamap_entry in datamap:
                value_type_name = datamap_entry[2]
                if isinstance(value_type_name, list):
                    for sub_value_type_name in value_type_name:
                        if needs_translation(sub_value_type_name):
                            self.assertTrue(translator.has_translation(sub_value_type_name),
                                            msg='No german translation for "{}"'.format(sub_value_type_name))
                else:
                    if needs_translation(value_type_name):
                        self.assertTrue(translator.has_translation(value_type_name),
                                        msg='No german translation for "{}"'.format(value_type_name))
                    if isinstance(datamap_entry[4], dict):
                        for select_entry in datamap_entry[4]:
                            if needs_translation(datamap_entry[4][select_entry]):
                                self.assertTrue(translator.has_translation(datamap_entry[4][select_entry]),
                                                msg='No german translation for "{}"'.format(datamap_entry[4][select_entry]))

    def test_translation_if_no_locale_given_use_english(self):
        """
        Test that all entries in datamap have english translations
        """
        with mock.patch('datamap.locale') as locale_mock:
            locale_mock.getdefaultlocale.return_value = [None, None]
            translator = Translator()
            self.assertEqual(translator.translate('locking_mode'), 'Locking mode.')
