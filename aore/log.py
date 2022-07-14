import logging
import sys

from .settings import LOG_LEVEL

log = logging.getLogger(__name__)

# setup handler
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter(u'[%(levelname)-8s][%(asctime)s][%(filename)s:%(lineno)d] %(message)s'))

out_hdlr.setLevel(LOG_LEVEL)
log.addHandler(out_hdlr)
log.setLevel(LOG_LEVEL)
log.propagate = False
