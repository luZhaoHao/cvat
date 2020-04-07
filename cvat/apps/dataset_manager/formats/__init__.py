
# Copyright (C) 2020 Intel Corporation
#
# SPDX-License-Identifier: MIT

from datumaro.components.project import Environment
from datumaro.util import to_snake_case

dm_env = Environment()


class _Format:
    NAME = ''
    EXT = ''
    VERSION = ''
    DISPLAY_NAME = '{name} {ext} {version}'
    TAG = ''

class Exporter(_Format):
    def __call__(self, dst_file, task_data, **options):
        raise NotImplementedError()

class Importer(_Format):
    def __call__(self, src_file, task_data, **options):
        raise NotImplementedError()

def _wrap_format(f_or_cls, klass, name, version, ext, display_name, tag):
    import inspect
    if inspect.isclass(f):
        assert hasattr(f_or_cls, '__call__')
        target = f_or_cls
    elif inspect.isfunction(f_or_cls):
        class wrapper(klass):
            # pylint: disable=arguments-differ
            def __call__(self, *args, **kwargs):
                f_or_cls(*args, **kwargs)

        wrapper.__name__ = f_or_cls.__name__
        wrapper.__module__ = f_or_cls.__module__
        target = wrapper
    else:
        assert inspect.isclass(f_or_cls) or inspect.isfunction(f_or_cls)

    target.NAME = name or klass.NAME or f_or_cls.__name__
    target.VERSION = version or klass.VERSION
    target.EXT = ext or klass.EXT
    target.DISPLAY_NAME = (display_name or klass.DISPLAY_NAME).format(
        name=name, version=version, ext=ext)
    target.TAG = tag or to_snake_case(target.NAME)
    assert all([target.NAME, target.VERSION, target.EXT, target.DISPLAY_NAME,
        target.TAG])
    return target

EXPORT_FORMATS = {}
def exporter(name, version, ext, display_name=None, tag=None):
    assert name not in EXPORT_FORMATS, "Export format '%s' already registered" % name
    def wrap_with_params(f_or_cls):
        t = _wrap_format(f_or_cls, Exporter, tag=tag,
            name=name, ext=ext, version=version, display_name=display_name)
        EXPORT_FORMATS[t.TAG] = t
        return t
    return wrap_with_params

IMPORT_FORMATS = {}
def importer(name, version, ext, display_name=None, tag=None):
    assert name not in IMPORT_FORMATS, "Import format '%s' already registered" % name
    def wrap_with_params(f_or_cls):
        t = _wrap_format(f_or_cls, Importer, tag=tag,
            name=name, ext=ext, version=version, display_name=display_name)
        IMPORT_FORMATS[t.TAG] = t
        return t
    return wrap_with_params

def make_importer(name):
    return IMPORT_FORMATS[name]()

def make_exporter(name):
    return EXPORT_FORMATS[name]()


import cvat.apps.dataset_manager.formats.coco
import cvat.apps.dataset_manager.formats.cvat
import cvat.apps.dataset_manager.formats.datumaro
import cvat.apps.dataset_manager.formats.labelme
import cvat.apps.dataset_manager.formats.mask
import cvat.apps.dataset_manager.formats.mot
import cvat.apps.dataset_manager.formats.pascal_voc
import cvat.apps.dataset_manager.formats.tfrecord
import cvat.apps.dataset_manager.formats.yolo