from collections import OrderedDict as OrderedDict
from mobject.geometry import Arrow
from mobject.mobject import Mobject
from animation.creation import ShowCreation
from animation.creation import Uncreate
from animation.transform import ReplacementTransform
from utils.simple_functions import update_without_overwrite
import copy
import sys
import warnings


class Component(Mobject):
    """
    Components are customizable Mobjects, designed to make creating data
    structures simpler. Each Component contains one or more subcomponents or
    submobjects, which results in a hierarchical organization of each. This
    makes it possible to operate on Components as data stuctures with methods
    such as ``Graph.set_node_label()`` rather than collections of Circles and
    Lines.
    """
    # modifications to self.CONFIG will persist for future mobjects
    CONFIG = {
        "scale_factor": 1
    }

    def __init__(self, *args, **kwargs):
        # components are responsible for creating their own "unique enough"
        # keys
        self.key = self.make_key(*args)
        self.assert_primitive(self.key)
        self.labels = OrderedDict()

        # attributes are stored in the mobject, not the component. we call this
        # here so components can be added and removed like regular mobjects
        Mobject.__init__(self)
        delattr(self, "color")
        delattr(self, "name")
        delattr(self, "dim")
        delattr(self, "target")

        self.update_attrs(
            update_without_overwrite(kwargs, self.CONFIG), animate=False)

    @staticmethod
    def assert_primitive(self):
        # implemented by subclasses
        raise NotImplementedError

    def make_key(self):
        # implemented by subclasses
        raise NotImplementedError

    def update_attrs(self, dic=None, animate=True):
        """
        ``update_attrs()`` is the key method for components. It should be
        written such that a calling ``update_attrs()`` on the top-level
        Component makes all the desired updates to each subcomponent
        automatically.
        """
        if dic is None:
            dic = OrderedDict()
        labels_dict = self.generate_labels_dict(dic)
        new_mob = self.generate_mobject(dic, labels_dict)
        anims = self.update_mobject(new_mob, animate=animate)
        anims.extend(self.update_labels(labels_dict, animate=animate, dic=dic))
        return anims

    def set_label(self, name, label, animate=True, **kwargs):
        kwargs["animate"] = animate
        d = copy.deepcopy(self.labels)
        d[name] = label
        return self.set_labels(d, **kwargs)

    def update_labels(self, new_labels, **kwargs):
        assert(type(new_labels) == OrderedDict)
        # make sure labels are different
        for old_label in self.labels.values():
            for new_label in new_labels.values():
                assert(id(old_label) != id(new_label))

        anims = []
        # delete
        for key, val in new_labels.items():
            if val is None:
                anims.append(Uncreate(self.labels[key]))
                self.remove(self.labels[key])
                del new_labels[key]
                del self.labels[key]

        # scale
        for label in new_labels.values():
            if type(label) == Arrow:
                continue  # TODO
            scale_factor = self.get_label_scale_factor(label, len(new_labels))
            label.scale(scale_factor)

        # place
        new_labels = self.place_labels(new_labels, **kwargs)

        # animate
        if "animate" not in kwargs or kwargs["animate"]:
            for name in new_labels.keys():
                if name in self.labels:
                    anims.extend([ReplacementTransform(self.labels[name],
                                                       new_labels[name],
                                                       parent=self)])
                else:
                    anims.extend([ShowCreation(new_labels[name])])
                    self.add(new_labels[name])
            for name in self.labels:
                if name not in new_labels:
                    anims.extend([Uncreate(self.labels[name])])
                    self.remove(self.labels[name])
        else:
            for name in new_labels.keys():
                if name not in self.labels:
                    self.add(new_labels[name])
                else:
                    self.add(new_labels[name])
                    self.remove(self.labels[name])
            for name in self.labels:
                if name not in new_labels:
                    self.remove(self.labels[name])
        self.labels = new_labels
        return anims

    def place_labels(self, new_labels):
        # implemented by subclass
        raise NotImplementedError

    def get_label(self, name):
        return self.labels.get(name, None)

    def get_label_scale_factor(self, label, num_labels):
        raise NotImplementedError

    def get_center(self):
        print("You called get_center() on a Component rather than its mobject",
              file=sys.stderr)
        print("This is probably not what you want", file=sys.stderr)
        breakpoint(context=7)
