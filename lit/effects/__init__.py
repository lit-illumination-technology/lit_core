import os
import glob

effects_path = os.path.dirname(os.path.abspath(__file__))
modules = glob.glob(os.path.join(effects_path, "**", "*.py"), recursive=True)
relative_paths = [f[len(effects_path) + 1 : -3] for f in modules if os.path.isfile(f)]
split_paths = [os.path.normpath(p).split(os.sep) for p in relative_paths]
effects = ["lit.effects.{}".format(".".join(p)) for p in split_paths if p[-1][0] != "_"]
