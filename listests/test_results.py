import os
import uuid
from pathlib import Path
from pprint import pprint

from bs4 import BeautifulSoup
import pytest

from lisfloodutilities.compare import NetCDFComparator, TSSComparator

from listests import logger, run_command, settings_files


"""
How to run:

pytest test_results.py -s
  -L /workarea/lisflood_versions/1_e5eb9f03/lisf1.py  # Path to lisf1.py main script
  -R /workarea/EFAS/  # Path to root (PathRoot in settings_files file)
  -M /workarea/EFAS/EFAS_forcings/   # Path to meteo forcings
  -O /workarea/lf_results/1_e5eb9f03/   # Path to output folder
  -P /workarea/virtualenvs/lisflood27/bin/python   # Path to python binary
  -I /workarea/lf_results/reference/EFAS/InitSafe/   # Path to init folder
  -X /workarea/lf_results/reference/EFAS/out_daily  # Path to reference data (Oracle data)
  -T ECD  # kind of simulation: Efas Cold Daily in this case

"""


@pytest.mark.usefixtures("options")
class TestRun:

    @classmethod
    def setup_class(cls):
        # run lisflood
        pybin = cls.options['python']
        lisflood_py = cls.options['lisflood']
        pathout = cls.options['pathout']
        cls.settings_xml = cls.get_settings()
        cell = cls.settings_xml.select('lfuser textvar[name="MaskMap"]')[0]
        cls.mask_map = cell.attrs['value'].replace('$(PathRoot)', str(cls.options['pathroot']))

        # Generating XML settings_files on fly from template
        uid = uuid.uuid4()
        filename = f'./settings_{uid}.xml'
        with open(filename, 'w') as dest:
            dest.write(cls.settings_xml.prettify())
        cls.settings_filepath = Path(filename).absolute()

        if not lisflood_py:
            if not pathout:
                raise ValueError('If --lisflood/-L option is not set you must pass --pathout/-O argument'
                                 ' to point to existing LISFLOOD results')
            # no need to run lisflood; just compare existing results
            return

        # Compile kinematic wave
        compile_krw = lisflood_py.parent.joinpath('hydrological_modules/compile_kinematic_wave_parallel_tools.py') if lisflood_py else None
        kw_dir = lisflood_py.parent.joinpath('lisflood/hydrological_modules/')
        lis_dir = lisflood_py.parent
        compile_cmd = ' '.join((f'cd {kw_dir} &&', pybin.as_posix(), compile_krw.name, 'build_ext', '--inplace'))
        run_command(compile_cmd)

        logger.info('\n\n')
        logger.info(' ============================== START OF LISFLOOD OUTPUT ============================== ')
        lisflood_cmd = ' '.join((f'cd {lis_dir} &&', pybin.as_posix(), 'lisf1.py', cls.settings_filepath.as_posix()))
        run_command(lisflood_cmd)
        logger.info(' ============================== END OF LISFLOOD OUTPUT ================================ ')

    @classmethod
    def teardown_class(cls):
        os.remove(cls.settings_filepath)

    @classmethod
    def get_settings(cls):
        """
        Return XML representation of settings_files file, based on BeautifulSoup4
        """
        # -s suffix means 'small window'
        settings_key = cls.options["runtype"]
        settings_file = settings_files[settings_key]
        with open(settings_file) as tpl:
            soup = BeautifulSoup(tpl, 'lxml-xml')
            for textvar in ('PathRoot', 'PathMeteo', 'PathOut', 'PathStatic', 'PathInit'):
                for tag in soup.find_all("textvar", {'name': textvar}):
                    tag['value'] = cls.options[textvar.lower()]
        return soup

    def test_rep_maps(self):
        # check all nc. maps in output folder
        logger.info('\n\n')
        logger.info(' ============================== START NETCDF TESTS ================================== ')
        comparator = NetCDFComparator(self.mask_map, rtol=self.options['rtol'], atol=self.options['atol'])
        diffs = comparator.compare_dirs(self.options['reference'], self.options['pathout'], skip_missing=False)
        if diffs:
            pprint(diffs)
        assert not diffs

    def test_tss(self):
        # check all TSS in output folder
        logger.info('\n\n')
        logger.info(' ============================= START TSS TESTS ===================================== ')
        comparator = TSSComparator()
        diffs = comparator.compare_dirs(self.options['reference'], self.options['pathout'], skip_missing=False)
        if diffs:
            pprint(diffs)
        assert not diffs
