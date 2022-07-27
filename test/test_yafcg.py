from src.yafct import YaFct
from test.utils import TestUtils


class TestYaFct:
    def test_create_json(self):
        out_dir = TestUtils.create_clean_test_dir('')
        k_config_file = out_dir.write_file("""
        config NAME
            string "Just the name"
            default "John Smith"
        config STATUS
            string "Defines your status"
            default "ALIVE"
        """, 'kconfig.txt')
        iut = YaFct(k_config_file)
        assert iut.get_json_values() == {'NAME': 'John Smith', 'STATUS': 'ALIVE'}
