import logging
import os
import sys
import warnings

if sys.platform == 'darwin':
    os.environ['QT_MAC_WANTS_LAYER'] = '1'

    class QtWarningFilter(logging.Filter):
        def filter(self, record):
            return not (
                record.getMessage().find("Layer-backing is always enabled") >= 0
            )

    logging.getLogger().addFilter(QtWarningFilter())

    warnings.filterwarnings("ignore", message="Layer-backing is always enabled")

from napari_nifti_viewer._version import __version__
from napari_nifti_viewer._widget import NiftiViewerWidget

__all__ = ["NiftiViewerWidget", "__version__"]
