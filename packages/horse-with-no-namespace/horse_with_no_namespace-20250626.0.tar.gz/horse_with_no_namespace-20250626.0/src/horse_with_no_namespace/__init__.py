# SPDX-FileCopyrightText: 2025 David Glick <david@glicksoftware.com>
#
# SPDX-License-Identifier: MIT

# This is loaded by ~horse_with_no_namespace.pth,
# which is loaded by Python's `site` module
# when it is installed in a site-packages folder.

# It's important that the .pth file starts with a tilde.
# This makes sure that it is loaded after other .pth files.
# (This is not guaranteed by Python,
# but the site module sorts the files before processing them,
# and that hasn't changed recently.)

import pkgutil
import sys

logged = False


def apply():
    # The Python site module can call us more than once.
    # We need to actually do this the last time,
    # But we only want to show the notice once.
    global logged
    if not logged:
        print(
            "🐎 This Python uses horse-with-no-namespace "
            "to make pkg_resources namespace packages compatible "
            "with PEP 420 namespace packages.",
            file=sys.stderr,
        )
        logged = True

    # Only patch pkg_resources if it is installed...
    # (To do: at some point pkg_resources will be removed from setuptools.
    # Then we might have to add our own fake module.)
    try:
        import pkg_resources
    except ImportError:
        pass
    else:
        # Patch pkg_resources.declare_namespace
        # to update __path__ using pkgutil.extend_path instead
        def declare_namespace(packageName):
            parent_locals = sys._getframe(1).f_locals
            # Sometimes declare_namespace is called from pkg_resources itself;
            # then there is no __path__ which needs to be updated.
            if "__path__" in parent_locals:
                parent_locals["__path__"] = pkgutil.extend_path(
                    parent_locals["__path__"], packageName
                )

        pkg_resources.declare_namespace = declare_namespace

    # Remove existing namespace package modules that were already created
    # by other .pth files, possibly with an incomplete __path__
    for name, module in list(sys.modules.items()):
        loader = getattr(module, "__loader__", None)
        if loader and loader.__class__.__name__ == "NamespaceLoader":
            del sys.modules[name]
