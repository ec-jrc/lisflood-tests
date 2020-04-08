import os
from pprint import pformat
from pathlib import Path
from itertools import chain

import pytest

from listests import logger


def pytest_addoption(parser):
    parser.addoption('-P', '--python', type=lambda p: Path(p), help='Path to python binary', default='python')
    parser.addoption('-L', '--lisflood', type=lambda p: Path(p).absolute(), help='Path to main lisf1.py script')

    # pathroot is needed even if test doesn't run any simulation, since we need it to find the MaskMap
    parser.addoption('-R', '--pathroot', type=lambda p: Path(p).absolute(), help='Path to Root static data directory.',
                     required=True)
    parser.addoption('-S', '--pathstatic', type=lambda p: Path(p).absolute(),
                     help='Path to Lisflood static data (e.g. maps)')
    parser.addoption('-M', '--pathmeteo', type=lambda p: Path(p).absolute(), help='Path to Lisflood meteo forcings')
    parser.addoption('-I', '--pathinit', type=lambda p: Path(p).absolute(), help='Path to Lisflood init data')
    parser.addoption('-O', '--pathout', type=lambda p: Path(p).absolute(), help='Path to Lisflood results',
                     required=True)

    parser.addoption('-X', '--reference', type=lambda p: Path(p).absolute(), help='Path to Lisflood oracle results',
                     required=True)
    parser.addoption('-T', '--runtype', help='Test Type: e.g. EC6=EFAS Cold 6hourly run; '
                                             'GCD-s=GloFAS Cold Daily short run',
                     choices=['ECD', 'EC6', 'GCD', 'GCD5y', 'ECD-s', 'EC6-s', 'GCD-s', ])

    parser.addoption('--rtol', help='Relative Tolerance (e.g. 0.001)', type=float, default=0.01)
    parser.addoption('--atol', help='Absolute Tolerance (e.g. 0.001)', type=float, default=0.00001)


@pytest.fixture(scope='class', autouse=True)
def options(request):
    options = dict()
    options['python'] = request.config.getoption('--python')
    options['lisflood'] = request.config.getoption('--lisflood')
    options['pathroot'] = request.config.getoption('--pathroot')
    options['pathmeteo'] = request.config.getoption('--pathmeteo') or options['pathroot']
    options['pathstatic'] = request.config.getoption('--pathstatic') or options['pathroot']
    options['pathout'] = request.config.getoption('--pathout') or options['pathroot']
    options['pathinit'] = request.config.getoption('--pathinit') or options['pathroot']
    options['reference'] = request.config.getoption('--reference')
    options['runtype'] = request.config.getoption('--runtype')
    options['rtol'] = request.config.getoption('--rtol')
    options['atol'] = request.config.getoption('--atol')

    if not options['pathout'].exists():
        options['pathout'].mkdir(parents=True)
    elif options['pathout'].exists() and options['lisflood'] is not None and options['lisflood'].exists():
        logger.warning('Removing older result from %s', options['pathout'].as_posix())
        for f in chain(options['pathout'].glob('*.nc'), options['pathout'].glob('*.tss')):
            logger.warning('removing %s', f.as_posix())
            os.unlink(f)
    elif options['pathout'].exists() and options['lisflood'] is None:
        logger.info('Comparing existing results: %s and %s', options['pathout'], options['reference'])
    request.cls.options = options
    logger.info(pformat(options))
    return options
