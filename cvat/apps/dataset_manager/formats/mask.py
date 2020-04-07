# Copyright (C) 2019 Intel Corporation
#
# SPDX-License-Identifier: MIT

from tempfile import TemporaryDirectory

from pyunpack import Archive

from cvat.apps.dataset_manager.bindings import CvatTaskDataExtractor, \
    import_dm_annotations
from cvat.apps.dataset_manager.formats import dm_env, exporter, importer
from cvat.apps.dataset_manager.util import make_zip_archive
from datumaro.components.project import Dataset


@exporter(name='MASK', ext='ZIP', version='1.1')
def _export(dst_file, task_data, save_images=False):
    extractor = CvatTaskDataExtractor(task_data, include_images=save_images)
    envt = dm_env.transforms
    extractor = extractor.transform(envt.get('polygons_to_masks'))
    extractor = extractor.transform(envt.get('boxes_to_masks'))
    extractor = extractor.transform(envt.get('merge_instance_segments'))
    extractor = extractor.transform(envt.get('id_from_image_name'))
    extractor = Dataset.from_extractors(extractor) # apply lazy transforms
    with TemporaryDirectory() as temp_dir:
        converter = dm_env.make_converter('voc_segmentation',
            apply_colormap=True, label_map='source', save_images=save_images)
        converter(extractor, save_dir=temp_dir)

        make_zip_archive(temp_dir, dst_file)

@importer(name='MASK', ext='ZIP', version='1.1')
def _import(src_file, task_data):
    with TemporaryDirectory() as tmp_dir:
        Archive(src_file.name).extractall(tmp_dir)

        dm_dataset = dm_env.make_importer('voc')(tmp_dir).make_dataset()
        masks_to_polygons = dm_env.transforms.get('masks_to_polygons')
        dm_dataset = dm_dataset.transform(masks_to_polygons)
        import_dm_annotations(dm_dataset, task_data)