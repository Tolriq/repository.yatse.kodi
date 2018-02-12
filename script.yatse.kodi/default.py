# -*- coding: utf-8 -*-
import sys

from lib import utils
from lib import share
from lib.utils import logger

logger.info("Starting script version: %s", utils.ADDON_VERSION)

argument = {}
for arg in sys.argv[1:]:
    argInfo = arg.split('=')
    argument[argInfo[0]] = argInfo[1]

logger.info("Parameters: %s" % argument)

commands = { 'share' : share.run }

commands[argument['action']](argument)
