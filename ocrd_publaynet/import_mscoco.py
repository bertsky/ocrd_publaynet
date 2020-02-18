from __future__ import absolute_import

import os.path
import numpy as np
import json
import click

from ocrd.resolver import Resolver
from ocrd.workspace import Workspace
from ocrd_models.ocrd_file import OcrdFile
from ocrd_modelfactory import page_from_image

from ocrd_models.ocrd_page import (
    CoordsType,
    TextRegionType,
    ImageRegionType,
    MetadataItemType,
    LabelsType, LabelType,
    to_xml
)
from ocrd_models.ocrd_page_generateds import (
    TableRegionType,
    TextTypeSimpleType
)
from ocrd_utils import (
    getLogger,
    points_from_polygon,
    pushd_popd,
    MIMETYPE_PAGE,
    EXT_TO_MIME
)

LOG = getLogger(__name__)

@click.command()
@click.argument('cocofile', type=click.File('rb'))
@click.argument('directory', type=click.Path(exists=True, file_okay=False, writable=True))
def convert(cocofile, directory):
    """Convert MS-COCO JSON to METS/PAGE XML files.
    
    Load JSON ``cocofile`` (in MS-COCO format)
    and chdir to ``directory`` (which it refers to).
    
    Start a METS file mets.xml with references to
    the image files (under fileGrp ``OCR-D-IMG``)
    and their corresponding PAGE-XML annotations
    (under fileGrp ``OCR-D-GT-SEG-BLOCK``), as
    parsed from ``cocofile`` and written using
    the same basename.
    """
    resolver = Resolver()
    with pushd_popd(directory):
        workspace = resolver.workspace_from_nothing('.')
        # https://github.com/ibm-aur-nlp/PubLayNet
        workspace.mets.unique_identifier = 'ocrd_PubLayNet_' + directory
        coco = json.load(cocofile)
        LOG.info('Loaded JSON for %d images with %d regions in %d categories',
                 len(coco['images']), len(coco['annotations']), len(coco['categories']))
        categories = dict()
        for cat in coco['categories']:
            categories[cat['id']] = cat['name']
        images = dict()
        for image in coco['images']:
            images[image['id']] = image
        for annotation in coco['annotations']:
            image = images[annotation['image_id']]
            regions = image.setdefault('regions', list())
            regions.append(annotation)
        LOG.info('Parsing annotations into PAGE-XML')
        for image in images.values():
            page_id = 'p' + str(image['id'])
            file_base, file_ext = os.path.splitext(image['file_name'])
            filename = file_base + '.xml'
            image_file = workspace.add_file(
                'OCR-D-IMG',
                ID='OCR-D-IMG_' + page_id,
                pageId=page_id,
                mimetype=EXT_TO_MIME[file_ext],
                local_filename=image['file_name'])
            LOG.info('Added page %s file %s of type %s',
                     image_file.pageId, image_file.local_filename, image_file.mimetype)
            pcgts = page_from_image(image_file)
            pcgts.set_pcGtsId(page_id)
            page = pcgts.get_Page()
            assert page.imageWidth == image['width']
            assert page.imageHeight == image['height']
            for region in image['regions']:
                polygon = np.array(region['segmentation'])
                polygon = np.reshape(polygon, (polygon.shape[1]//2, 2))
                coords = CoordsType(points=points_from_polygon(polygon))
                category = categories[region['category_id']]
                region_id = 'r' + str(region['id'])
                if category == 'text':
                    region = TextRegionType(id=region_id,
                                            Coords=coords,
                                            type=TextTypeSimpleType.PARAGRAPH)
                    page.add_TextRegion(region)
                elif category == 'title':
                    region = TextRegionType(id=region_id,
                                            Coords=coords,
                                            type=TextTypeSimpleType.HEADING) # CAPTION?
                    page.add_TextRegion(region)
                elif category == 'list':
                    region = TextRegionType(id=region_id,
                                            Coords=coords,
                                            type=TextTypeSimpleType.LISTLABEL) # OTHER?
                    page.add_TextRegion(region)
                elif category == 'table':
                    region = TableRegionType(id=region_id,
                                             Coords=coords)
                    page.add_TableRegion(region)
                elif category == 'figure':
                    region = ImageRegionType(id=region_id,
                                             Coords=coords)
                    page.add_ImageRegion(region)
                else:
                    raise Exception('unknown image category: %s' % category)
            page_file = workspace.add_file(
                'OCR-D-GT-SEG-BLOCK',
                ID='OCR-D-GT-SEG-BLOCK_' + page_id,
                pageId=page_id,
                mimetype=MIMETYPE_PAGE,
                local_filename=filename,
                content=to_xml(pcgts))
            LOG.info('Added page %s file %s with %d regions',
                     page_file.pageId, page_file.local_filename, len(image['regions']))
        LOG.info('All done')
        workspace.save_mets()
