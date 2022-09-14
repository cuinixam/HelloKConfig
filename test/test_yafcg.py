import textwrap

from src.yafct import YaFct
from test.utils import TestUtils


class TestYaFct:
    def test_create_json(self):
        out_dir = TestUtils.create_clean_test_dir('')
        feature_model_file = out_dir.write_file("""
        config NAME
            string "Just the name"
            default "John Smith"
        config STATUS
            string "Defines your status"
            default "ALIVE"
        """, 'kconfig.txt')
        iut = YaFct(feature_model_file)
        assert iut.get_json_values() == {'NAME': 'John Smith', 'STATUS': 'ALIVE'}

    def test_load_user_config_file(self):
        out_dir = TestUtils.create_clean_test_dir('')
        feature_model_file = out_dir.write_file("""
        config NAME
            string "Just the name"
            default "No Name"
        """, 'kconfig.txt')
        user_config = out_dir.write_file("""
CONFIG_UNKNOWN="y"
CONFIG_NAME="John Smith" 
        """, 'user.config')

        iut = YaFct(feature_model_file, user_config)
        assert iut.get_json_values() == {'NAME': 'John Smith'}

    def test_load_user_config_file_with_malformed_content(self):
        """
        All lines in the user configuration file starting with whitespaces will be ignored
        """
        out_dir = TestUtils.create_clean_test_dir('')
        feature_model_file = out_dir.write_file("""
        config NAME
            string "Just the name"
            default "No Name"
        """, 'kconfig.txt')
        user_config = out_dir.write_file("""
 CONFIG_NAME="John Smith" 
        """, 'user.config')

        iut = YaFct(feature_model_file, user_config)
        assert iut.get_json_values() == {'NAME': 'No Name'}

    def test_boolean_without_description(self):
        """
        A configuration without description can not be selected by the user
        """
        out_dir = TestUtils.create_clean_test_dir('')
        feature_model_file = out_dir.write_file("""
        mainmenu "This is the main menu"
            menu "First menu"
                config FIRST_BOOL
                    bool
                config FIRST_NAME
                    string "You can select this"
                config SECOND_NAME
                    string
            endmenu
        """, 'kconfig.txt')
        user_config = out_dir.write_file(textwrap.dedent("""
        CONFIG_FIRST_BOOL=y
        CONFIG_FIRST_NAME="Dude"
        CONFIG_SECOND_NAME="King"
        """), 'user.config')

        iut = YaFct(feature_model_file, user_config)
        assert iut.get_json_values() == {'FIRST_NAME': 'Dude'}

    def test_boolean_with_description(self):
        """
        A configuration with description can be selected by the user
        """
        out_dir = TestUtils.create_clean_test_dir('')
        feature_model_file = out_dir.write_file("""
        mainmenu "This is the main menu"
            menu "First menu"
                config FIRST_BOOL
                    bool "You can select this"
                config FIRST_NAME
                    string "You can select this also"
            endmenu
        """, 'kconfig.txt')
        user_config = out_dir.write_file(textwrap.dedent("""
        CONFIG_FIRST_BOOL=y
        CONFIG_FIRST_NAME="Dude"
        """), 'user.config')

        iut = YaFct(feature_model_file, user_config)
        assert iut.get_json_values() == {'FIRST_NAME': 'Dude', 'FIRST_BOOL': True}

    def test_define_boolean_choices(self):
        """
        Using a boolean choice will define a boolean for every value.
        Only the choices with a 'prompt' are selectable.
        There is a warning generated for choices without a 'prompt'.
        """
        out_dir = TestUtils.create_clean_test_dir('')
        feature_model_file = out_dir.write_file("""
        choice APP_VERSION
            prompt "application version"
            default APP_VERSION_1
            help
                Currently there are several application version supported.
                Select the one that matches your needs.
    
            config APP_VERSION_1
                bool
                prompt "app v1"
            config APP_VERSION_2
                bool
                prompt "app v2"
            # This is not selectable because it has no prompt 
            config APP_VERSION_3
                bool
        endchoice
        """, 'kconfig.txt')
        user_config = out_dir.write_file(textwrap.dedent("""
        CONFIG_APP_VERSION="APP_VERSION_1"
        """), 'user.config')

        iut = YaFct(feature_model_file, user_config)
        assert iut.get_json_values() == {'APP_VERSION_1': True, 'APP_VERSION_2': False}

    def test_define_string_choices(self):
        """
        A choice can only be of type bool or tristate.
        One can use string but a warning will be issued.
        """
        out_dir = TestUtils.create_clean_test_dir('')
        feature_model_file = out_dir.write_file("""
        choice APP_VERSION
            prompt "application version"
            default APP_VERSION_1
            help
                Currently there are several application version supported.
                Select the one that matches your needs.
    
            config APP_VERSION_1
                string
                prompt "app v1"
            config APP_VERSION_2
                string
                prompt "app v2"
        endchoice
        """, 'kconfig.txt')
        user_config = out_dir.write_file(textwrap.dedent("""
        CONFIG_APP_VERSION="APP_VERSION_1"
        CONFIG_APP_VERSION_1="VERSION_NEW"
        """), 'user.config')

        iut = YaFct(feature_model_file, user_config)
        assert iut.get_json_values() == {'APP_VERSION_1': 'VERSION_NEW', 'APP_VERSION_2': ''}

    def test_define_tristate_choices(self):
        """
        For KConfig, `bool` and `tristate` types are represented as JSON Booleans,
        the third `tristate` state is not supported.
        """
        out_dir = TestUtils.create_clean_test_dir('')
        feature_model_file = out_dir.write_file("""
        choice APP_VERSION
            prompt "application version"
            default APP_VERSION_1
            help
                Currently there are several application version supported.
                Select the one that matches your needs.
    
            config APP_VERSION_1
                tristate
                prompt "app v1"
            config APP_VERSION_2
                tristate
                prompt "app v2"
        endchoice
        """, 'kconfig.txt')
        user_config = out_dir.write_file(textwrap.dedent("""
        CONFIG_APP_VERSION="APP_VERSION_1"
        """), 'user.config')

        iut = YaFct(feature_model_file, user_config)
        assert iut.get_json_values() == {'APP_VERSION_1': True, 'APP_VERSION_2': False}
