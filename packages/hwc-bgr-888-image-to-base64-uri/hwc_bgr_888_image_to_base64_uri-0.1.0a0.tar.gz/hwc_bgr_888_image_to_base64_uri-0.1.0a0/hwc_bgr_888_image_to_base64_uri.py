from __future__ import division

import base64
import io
import os
import sys

import cv2
import numpy as np

# Python 2
if sys.version_info < (3,):
    bytes = str
    string = unicode
else:
    string = str

OUTPUT_FORMAT_EXTENSIONS_TO_MIME_TYPES = {
    u'.jpg': u'image/jpg',
    u'.jpeg': u'image/jpeg',
    u'.png': u'image/png',
}


def hwc_bgr_888_image_to_base64_uri(
    image,
    max_long_edge=512,
    output_format_extension=u'.jpg',
):
    # type: (np.ndarray, int, string) -> string
    # Validate arguments
    if (
        not isinstance(image, np.ndarray)
        or image.dtype != np.uint8
        or len(image.shape) != 3
        or image.shape[2] != 3
    ):
        raise ValueError("image must be an ndarray in HWC BGR 888 format")

    if max_long_edge <= 0:
        raise ValueError("max_long_edge must be positive")
    
    output_format_extension = output_format_extension.lower()
    if output_format_extension not in OUTPUT_FORMAT_EXTENSIONS_TO_MIME_TYPES:
        raise ValueError(
            u'Unsupported output format extension %s. Supported output format extensions: %s' % (
                output_format_extension,
                u', '.join(OUTPUT_FORMAT_EXTENSIONS_TO_MIME_TYPES)
            )
        )

    # Get original dimensions
    height, width = image.shape[:2]
    original_long_edge = max(height, width)

    # Calculate scaling ratio if needed
    if original_long_edge > max_long_edge:
        scale = max_long_edge / original_long_edge
        new_width = int(width * scale)
        new_height = int(height * scale)
        # Resize
        resized_image = cv2.resize(image, (new_width, new_height))
    else:
        resized_image = image

    # Encode image as output format
    success, image_encoded_as_output_format = cv2.imencode(
        output_format_extension,
        resized_image
    )
    
    if not success:
        raise RuntimeError(
            'Failed to encode image as output format %s' % output_format_extension
        )
    
    # Then encode as base64
    image_encoded_as_output_format_base64_bytes = base64.b64encode(
        image_encoded_as_output_format.tobytes()
    )
    
    # Determine MIME type based on format
    mime_type = OUTPUT_FORMAT_EXTENSIONS_TO_MIME_TYPES[output_format_extension]
    
    # Generate URI string
    return u'data:%s;base64,%s' % (
        mime_type,
        image_encoded_as_output_format_base64_bytes.decode('ascii')
    )
