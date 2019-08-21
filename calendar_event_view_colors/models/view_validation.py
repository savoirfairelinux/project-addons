""" View validation code (using assertions, not the RNG schema). """

import collections
import logging
import os

from lxml import etree
from odoo import tools
from odoo.tools import view_validation

_logger = logging.getLogger(__name__)


_validators = collections.defaultdict(list)
_relaxng_cache = {}

original_relaxng = view_validation.relaxng


def relaxng(view_type):
    """ Return a validator for the given view type, or None.
       Override the relaxng to load a new calendar_view.rng file
       with new js_class attribute"""
    if view_type not in _relaxng_cache:
        # local modification
        if view_type == 'calendar':
            rng_path = os.path.join(
                'calendar_event_view_colors', 'rng', '%s_view.rng' % view_type)
        else:
            rng_path = os.path.join('base', 'rng', '%s_view.rng' % view_type)
        # end local modification
        with tools.file_open(rng_path) as frng:
            try:
                relaxng_doc = etree.parse(frng)
                _relaxng_cache[view_type] = etree.RelaxNG(relaxng_doc)
            except Exception:
                _logger.exception(
                    'Failed to load RelaxNG XML schema for views validation')
                _relaxng_cache[view_type] = None
    return _relaxng_cache[view_type]


view_validation.relaxng = relaxng
