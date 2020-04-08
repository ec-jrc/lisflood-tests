import logging
import subprocess
import sys


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
logger = logging.getLogger()
logger.propagate = False

settings_files = {
    'ECD': 'settings_full_efas_day.xml',
    'EC6': 'settings_full_efas_6hourly.xml',
    # 'EWD': 'settings_full_warmstart_efas_day.xml',
    # 'EW6': 'settings_full_warmstart_efas_6hourly.xml',
    'GCD': 'settings_full_glofas_day.xml',
    # 'GWD': 'settings_full_warmstart_glofas_day.xml',
    'ECD-s': 'settings_full_efas_day_short.xml',
    'EC6-s': 'settings_full_efas_6hourly_short.xml',
    # 'EWD-s': 'settings_full_warmstart_efas_day_short.xml',
    # 'EW6-s': 'settings_full_warmstart_efas_6hourly_short.xml',
    'GCD-s': 'settings_full_glofas_day_short.xml',
    # 'GWD-s': 'settings_full_warmstart_glofas_day_short.xml',
    'GCD5y': 'settings_full_glofas_day_5years.xml',
}


def run_command(cmd):
    logger.info(f'>>>>Executing....:\n{cmd}\n')
    p = subprocess.Popen(args=(cmd,),
                         stdout=subprocess.PIPE, shell=True,
                         stderr=subprocess.STDOUT, universal_newlines=True)
    # Poll process for new output until finished
    while True:
        nextline = p.stdout.readline()
        if nextline == '' and p.poll() is not None:
            break
        sys.stdout.write(nextline)
        sys.stdout.flush()
    if p.returncode:
        raise subprocess.CalledProcessError(p.returncode, cmd)
