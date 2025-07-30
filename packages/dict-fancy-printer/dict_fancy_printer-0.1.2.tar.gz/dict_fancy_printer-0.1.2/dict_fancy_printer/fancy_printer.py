from typing import Dict
from termcolor import colored


class FancyPrinter:
    """
    class used to handle the string representation of a dict
    """

    def __init__(self) -> None:
        """
        Constructor that intialize the formattation and the colors
        """

        self.formattation = {
            "START": colored("", "white"),
            "END": colored("", "white"),
            "BEG_DICT": "\n",
            "END_DICT": "",
            "BEG_VAL_DICT": colored("> ", "blue"),
            "END_VAL_DICT": "\n",
            "BEG_KEY_DICT": "+ ",
            "END_KEY_DICT": ": ",
            "BEG_LIST": "\n",
            "END_LIST": "\n",
            "BEG_LIST_DICT_BLOCK": "\n",
            "END_LIST_DICT_BLOCK": "",
            "BEG_VAL_LIST": colored(" - ", "white"),
            "END_VAL_LIST": "\n",
            "BEG_KEY_LIST": " - ",
            "END_KEY_LIST": ": ",
            "TAB": colored("    ", "blue"),
            "SPC": " ",
        }

        self.attr_colors = {
            "KEY_DICT_COLOR": {"v0": "red", "v1": "yellow"},
            "KEY_LIST_COLOR": {"v0": "blue", "v1": "yellow"},
            "VAL_DICT_COLOR": {"v0": "green", "v1": "yellow"},
            "VAL_LIST_COLOR": {"v0": "magenta", "v1": "yellow"},
        }

        self.max_k_len = 0

    def __call__(
        self, input_dict: Dict, key_triggers: str = "", show_private: bool = False
    ) -> str:
        """
        Return a string that represents a dict, but fancyfied
        Args:
            input_dict (Dict): The ugly dictionary that needs a makeup
            key_triggers (str, optional): A list of strings that signal a change of the formattation (Example: the overridded parameters). Defaults to "".
            show_private (bool, optional): Show private attributes. Defaults to False.
        Returns:
            str: The super-fancy string that represents the input dictionary.
        """

        def _get_reduced_key_list(keys, show_private):
            # check the list of keys to se if there is something to print (according with the show private parameter)
            reduced_keys = []
            hiddens = []
            for k in keys:
                # ignore private attributes
                if not k.startswith("_") or show_private:
                    reduced_keys.append(k)
                else:
                    hiddens.append(k)

            return sorted(reduced_keys), hiddens

        def _give_color(item, TYPE, dinput, something_hidden):
            """
            some rule to color properly some variables
            """

            color = self.attr_colors[TYPE]["v0"]
            if key_triggers in something_hidden:
                if item in dinput[key_triggers].keys():
                    color = self.attr_colors[TYPE]["v1"]

            return colored(item, color)

        def _fancystring(input_dict, count, is_list=False):
            # convert keys to string
            if isinstance(input_dict, dict):
                input_dict = {str(k): v for k, v in input_dict.items()}

            ret = []

            if isinstance(input_dict, dict) and not is_list:
                reduced_keys, something_hidden = _get_reduced_key_list(
                    input_dict.keys(), show_private
                )

                if len(reduced_keys) > 0:
                    max_local_klen = max([len(x) for x in reduced_keys])

                    ret += ["BEG_DICT"]
                    for k in reduced_keys:
                        if len(k) > self.max_k_len:
                            self.max_k_len = len(k)

                        v = input_dict[k]
                        ret += (
                            (count) * ["TAB"]
                            + ["BEG_KEY_DICT"]
                            + [
                                _give_color(
                                    k, "KEY_DICT_COLOR", input_dict, something_hidden
                                )
                            ]
                            + ["END_KEY_DICT"]
                            + [f"TAB_{max_local_klen}_{len(k)}"]
                            + _fancystring(v, count + 1)
                        )
                    ret += ["END_DICT"]
                else:
                    # Handle empty dictionary case
                    ret += ["BEG_DICT", "END_DICT"]

            # if it is a vocab but inside a list
            elif isinstance(input_dict, dict) and is_list:
                reduced_keys, something_hidden = _get_reduced_key_list(
                    input_dict.keys(), show_private
                )

                if len(reduced_keys) > 0:
                    max_local_klen = max([len(x) for x in reduced_keys])

                    ret += ["BEG_LIST_DICT_BLOCK"]
                    for k in reduced_keys:
                        if len(k) > self.max_k_len:
                            self.max_k_len = len(k)

                        v = input_dict[k]
                        ret += (
                            (count) * ["TAB"]
                            + ["BEG_KEY_LIST"]
                            + [
                                _give_color(
                                    k, "KEY_LIST_COLOR", input_dict, something_hidden
                                )
                            ]
                            + ["END_KEY_LIST"]
                        )

                        ret += [f"TAB_{max_local_klen}_{len(k)}"] + _fancystring(
                            v, count + 1, False if isinstance(v, dict) else is_list
                        )
                    ret += ["END_LIST_DICT_BLOCK"]
                else:
                    # Handle empty dictionary case in list
                    ret += ["BEG_LIST_DICT_BLOCK", "END_LIST_DICT_BLOCK"]

            elif isinstance(input_dict, list):
                ret += ["BEG_LIST"]
                for v in input_dict:
                    ret += _fancystring(v, count, is_list=True)
                ret += ["END_LIST"]

            elif is_list:
                ret += count * ["TAB"]
                ret += ["BEG_VAL_LIST"]
                ret += [_give_color(input_dict, "VAL_LIST_COLOR", {}, [])]
                ret += ["END_VAL_LIST"]

            else:
                ret += ["BEG_VAL_DICT"]
                ret += [_give_color(input_dict, "VAL_DICT_COLOR", {}, [])]
                ret += ["END_VAL_DICT"]

            return ret

        # gen an ugly string
        ugly_list = (
            ["START"]
            + [str(tok) for tok in _fancystring(input_dict, count=0)]
            + ["END"]
        )

        # set tabs
        tmp = []
        ignore = False
        for tok in ugly_list:
            if ignore and tok == "TAB":
                pass
            else:
                ignore = False
                if tok.startswith("TAB_"):
                    _, localmaxklen, klen = tok.split("_")
                    klen = int(klen.strip())
                    localmaxklen = int(localmaxklen.strip())
                    toadd = localmaxklen + 1 - klen
                    tmp += ["SPC"] * toadd
                    ignore = True
                else:
                    tmp.append(tok)
        ugly_list = tmp

        [
            self.formattation[tok] if tok in self.formattation else tok
            for tok in ugly_list
        ]

        # ugly2fancy
        return "".join(
            [
                self.formattation[tok] if tok in self.formattation else tok
                for tok in ugly_list
            ]
        )
