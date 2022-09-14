from pathlib import Path
from typing import Dict

import kconfiglib


class YaFct:
    def __init__(self, k_config_model_file: Path, k_config_file: Path = None):
        """
        :param k_config_model_file: Feature model definition (KConfig format)
        :param k_config_file: User feature selection configuration file
        """
        if not k_config_model_file.exists():
            raise FileNotFoundError(f"File {k_config_model_file} does not exist.")
        self.config = kconfiglib.Kconfig(k_config_model_file)
        if k_config_file:
            if not k_config_file.exists():
                raise FileNotFoundError(f"File {k_config_file} does not exist.")
            self.config.load_config(k_config_file, replace=False)

    def get_json_values(self) -> Dict:
        config_dict = {}

        def write_node(node):
            sym = node.item
            if not isinstance(sym, kconfiglib.Symbol):
                return

            if sym.config_string:
                val = sym.str_value
                if sym.type in [kconfiglib.BOOL, kconfiglib.TRISTATE]:
                    val = (val != 'n')
                elif sym.type == kconfiglib.HEX:
                    val = int(val, 16)
                elif sym.type == kconfiglib.INT:
                    val = int(val)
                config_dict[sym.name] = val

        for n in self.config.node_iter(False):
            write_node(n)
        return config_dict
