from constants import SAVE_DIR
import dill
import os
import pyclbr
import sys


def get_previous_class_name(scene_class):
    calling_class_name = scene_class.__class__.__name__
    calling_class_module = scene_class.__class__.__module__
    module = pyclbr.readmodule(scene_class.__class__.__module__)
    classes = sorted(
        [c for c in list(module.items())
            if c[1].module == calling_class_module],
        key=lambda c: c[1].lineno,
    )
    classes = list(map(lambda c: c[0], classes))
    calling_class_index = classes.index(calling_class_name)
    if calling_class_index == 0:
        print("There is no previous class from which to load, and no save "
              "file was specified.", file=sys.stderr)
        breakpoint(context=9)
    return classes[calling_class_index - 1]


def save_state(scene_class, filename=None):
    if filename is None:
        filename = scene_class.__class__.__name__ + ".mnm"
    dill.dump(scene_class, open(os.path.join(SAVE_DIR, filename), "wb"))


def load_previous_state(scene_class, filename=None):
    if filename is None:
        filename = get_previous_class_name(scene_class) + ".mnm"
    loaded_state = dill.load(open(os.path.join(SAVE_DIR, filename), "rb"))
    scene_class.__dict__.update(loaded_state.__dict__)
