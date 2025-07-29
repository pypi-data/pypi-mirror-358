import argparse
import importlib
import os
import sys
from collections import OrderedDict
from pathlib import Path

import omegaconf
from box import Box
from omegaconf import ListMergeMode, OmegaConf
from omegaconf.dictconfig import DictConfig
from pyhocon import ConfigFactory


def instantiate_from_pretrained(conf):
    string = conf.target
    ckpt_path = conf.path
    module, cls_name = string.rsplit(".", 1)
    cls = getattr(importlib.import_module(module, package=None), cls_name)
    return cls.from_pretrained(ckpt_path)


def instantiate_from_config(config, **kwargs):
    if "target" not in config:
        raise KeyError("Expected key `target` to instantiate.")
    return get_obj_from_str(config["target"])(**config.get("params", dict()), **kwargs)


def get_obj_from_str(string, reload=False):
    module, cls = string.rsplit(".", 1)
    if reload:
        module_imp = importlib.import_module(module)
        importlib.reload(module_imp)
    return getattr(importlib.import_module(module, package=None), cls)


def _convert_str(s):
    try:
        return int(s)
    except:
        pass
    try:
        return float(s)
    except:
        pass
    return s


def _resolve_fields(sub_conf, prefix=None):
    complete_fields = dict()
    for k in sub_conf:
        if prefix is None:
            new_prefix = k
        else:
            new_prefix = f"{prefix}.{k}"
        if isinstance(sub_conf[k], OrderedDict):
            complete_fields.update(_resolve_fields(sub_conf[k], new_prefix))
        else:
            complete_fields[new_prefix] = type(sub_conf[k])
    return complete_fields


def _convert_arg(val, conversion):
    if conversion == "str2list":
        val_list = (
            val.strip()
            .replace("]", "")
            .replace("[", "")
            .replace(")", "")
            .replace("(", "")
            .split(",")
        )
        val_list = [_convert_str(s) for s in val_list]
        return val_list
    else:
        return val


def _update_subdict(subdict, key, val):
    if "." in key:
        subkeys = key.split(".")
        _update_subdict(subdict[subkeys[0]], ".".join(subkeys[1:]), val)
    else:
        subdict[key] = val


def _convert_entries(conf, resolve_path=True):
    for k, v in conf.items():
        if isinstance(v, (Box, DictConfig)):
            conf[k] = _convert_entries(v, resolve_path)
        else:
            if v == "None":
                conf[k] = None
            if resolve_path and isinstance(v, str) and ("~" in v):
                conf[k] = os.path.expanduser(v)
    return conf


def full_key_set(conf, full_key: str, value):
    sub_keys = full_key.split(".")
    sub_conf = conf
    for sub_key in sub_keys[:-1]:
        sub_conf = sub_conf[sub_key]
    sub_conf[sub_keys[-1]] = value
    return conf


def full_key_get(conf, full_key: str):
    sub_keys = full_key.split(".")
    sub_conf = conf
    for sub_key in sub_keys[:-1]:
        sub_conf = sub_conf[sub_key]
    return sub_conf[sub_keys[-1]]


def _resolve_references(conf, conf_fn, root_conf=None, parent_key=None):
    if root_conf is None:
        root_conf = conf
    for k, v in conf.items():
        full_k = f"{parent_key}.{k}" if parent_key is not None else k
        if isinstance(v, omegaconf.dictconfig.DictConfig):
            root_conf = full_key_set(
                root_conf, full_k, _resolve_references(v, conf_fn, root_conf, full_k)
            )
        if isinstance(k, str) and k == "import":
            # support a/b/c.sub_dict1.sub_dict2
            # and a.b.c.sub_dict1.sub_dict2
            # and a/b/c -> load all entries
            # and a/b/c.v -> load specific entry
            if "/" in v:
                path_prefix = v.split("/")[:-1]
                path_postfix = v.split("/")[-1]
            else:
                path_prefix = []
                path_postfix = v
            path_elems = path_postfix.split(".")
            # resolve where

            is_resolved = False
            for sub_idx in range(0, len(path_elems)):
                for root_dir in ["conf", ".", Path(conf_fn).parent]:
                    sub_conf_fn = Path(
                        root_dir, *path_prefix, *path_elems[: len(path_elems) - sub_idx]
                    ).with_suffix(".yaml")
                    if sub_conf_fn.exists():
                        sub_conf = OmegaConf.load(sub_conf_fn)
                        sub_conf = _resolve_references(
                            sub_conf,
                            sub_conf_fn,
                        )
                        sub_ref = ".".join(path_elems[len(path_elems) - sub_idx :])
                        resolved_entry = (
                            full_key_get(sub_conf, sub_ref)
                            if sub_ref != ""
                            else sub_conf
                        )
                        # resolved_name = path_elems[-1]
                        is_resolved = True
                    if is_resolved:
                        break
                if is_resolved:
                    break
            if not is_resolved:
                raise Exception(f"Could not resolve: {v}")
            if parent_key is not None:
                del full_key_get(root_conf, parent_key)[k]
                root_conf = full_key_set(
                    root_conf,
                    parent_key,
                    OmegaConf.merge(
                        resolved_entry, full_key_get(root_conf, parent_key)
                    ),
                )
            else:
                del root_conf[k]
                root_conf = OmegaConf.merge(resolved_entry, root_conf)

    return full_key_get(root_conf, parent_key) if parent_key is not None else root_conf


def argconf_parse_omega(conf_fn, argv, resolve_path=False):
    if not OmegaConf.has_resolver("eval"):
        OmegaConf.register_new_resolver("eval", eval)  # eval as default resolver
    base_conf = OmegaConf.load(conf_fn)
    base_conf = _resolve_references(base_conf, conf_fn)
    cli_conf = OmegaConf.from_cli(argv)
    cli_conf = _resolve_references(cli_conf, conf_fn)

    remaining_cli_conf = {}
    for key, value in cli_conf.items():
        if key.startswith("++"):  # list entry inserted at the beginning
            list_conf = {key[1:]: [value]}
            base_conf = OmegaConf.merge(
                list_conf, base_conf, list_merge_mode=ListMergeMode.EXTEND
            )
        elif key.startswith("+"):  # list entry appended
            list_conf = {key[1:]: [value]}
            base_conf = OmegaConf.merge(
                base_conf, list_conf, list_merge_mode=ListMergeMode.EXTEND
            )
        ###
        else:
            remaining_cli_conf[key] = value

    conf = OmegaConf.merge(base_conf, remaining_cli_conf)

    conf = Box(OmegaConf.to_object(conf))
    conf = _convert_entries(conf, resolve_path)
    if conf_fn is not None:
        conf.conf = conf_fn
    return conf


def argconf_parse_hocon(
    conf_fn=None, ignore_unknown=False, parse_args=True, resolve_path=True
):
    if conf_fn is None:
        # load config name
        # support [--conf and first argument]
        conf_parser = argparse.ArgumentParser()
        conf_parser.add_argument("conf", type=str)
        conf_args = conf_parser.parse_known_args()[0]
        CONF_OPTIONAL = "--conf" in conf_parser.parse_known_args()[1]
        conf = ConfigFactory.parse_file(conf_args.conf)
    else:
        # load specific configuration
        conf = ConfigFactory.parse_file(conf_fn)
        CONF_OPTIONAL = True
        parse_args = False

    if parse_args:
        # load config
        parser = argparse.ArgumentParser()
        # parser.add_argument("--conf", type=str)
        if CONF_OPTIONAL:
            parser.add_argument("--conf", type=str)
        else:
            parser.add_argument("conf", type=str)
        # parser.add_argument("--conf", type=str)

        complete_fields = _resolve_fields(conf)  # nested . notation

        # create short names for reference
        shorted_fields = dict()
        suffix_list = [
            complete_name.split(".")[-1] for complete_name in complete_fields
        ]
        short2complete = dict()

        for complete_name, field_type in complete_fields.items():
            suffix = complete_name.split(".")[-1]
            if suffix_list.count(suffix) == 1:
                shorted_fields[suffix] = field_type
                short2complete[suffix] = complete_name
            else:
                shorted_fields[complete_name] = field_type
                short2complete[complete_name] = complete_name

        convert_dict = dict()
        # create arguments for argparse with short/complete names
        for short_name, field_type in shorted_fields.items():
            complete_name = short2complete[short_name]
            if field_type in [str, int, float]:
                parser.add_argument(
                    f"-{short_name}", f"-{complete_name}", type=field_type
                )
            if field_type == type(None):
                parser.add_argument(f"-{short_name}", f"-{complete_name}", type=str)

            if field_type == bool:
                parser.add_argument(
                    f"-{short_name}", f"-{complete_name}", action="store_true"
                )
            if field_type in [list, tuple]:
                parser.add_argument(f"-{short_name}", f"-{complete_name}", type=str)
                convert_dict[short_name] = "str2list"

        try:
            if ignore_unknown:
                args = parser.parse_known_args()[0]
            else:
                args = parser.parse_args()
        except:
            # nested include
            parser.add_argument("conf", type=str)
            if ignore_unknown:
                args = parser.parse_known_args()[0]
            else:
                args = parser.parse_args()
        # load argparse arguments and convert fields
        for arg_name, arg_val in args._get_kwargs():
            if arg_name == "conf":
                conf["conf"] = arg_val
            elif arg_val is not None and (
                shorted_fields[arg_name] is not bool or arg_val
            ):
                if arg_name in convert_dict:
                    arg_val = _convert_arg(arg_val, convert_dict[arg_name])
                _update_subdict(conf, short2complete[arg_name], arg_val)

    # return box object with nested . access
    conf = Box(conf, box_dots=True)
    # convert "None" to None ()
    conf = _convert_entries(conf, resolve_path=resolve_path)
    if conf_fn is not None:
        conf.conf = conf_fn
    return conf


def argconf_parse(
    conf_fn=None,
    ignore_unknown=False,
    parse_args=True,
    resolve_path=True,
    backend=None,
    cli_overwrite=True,  # allow overwrite of passed config via CLI
):
    # Check if the first argument is a configuration file
    if cli_overwrite and (
        len(sys.argv) > 1
        and any([sys.argv[1].endswith(suffix) for suffix in [".conf", ".yaml", ".yml"]])
        and ("=" not in sys.argv[1])
    ):
        conf_fn = sys.argv[1]
        argv = sys.argv[2:]
    # Raise an error if no default configuration file is provided and also no
    # configuration file is provided as an argument
    elif conf_fn is None:
        raise RuntimeError(
            "No default configuration provided to argconf_parse, and also the first "
            f"argument '{sys.argv[1]}' is not a .yaml or .conf configuration file."
        )
    # No configuration file provided as an argument, but default conf_fn is provided
    else:
        conf_fn = str(conf_fn)
        argv = sys.argv[1:]
    if backend is None:
        if conf_fn.endswith(".conf"):
            backend = "hocon"
        else:
            backend = "omega"

    if backend == "hocon":
        return argconf_parse_hocon(conf_fn, ignore_unknown, parse_args, resolve_path)
    elif backend == "omega":
        return argconf_parse_omega(conf_fn, argv, resolve_path)
    else:
        raise NotImplementedError(f"Backend not supported: {backend}")
