import os
import shutil
import base64
import boldqc
import logging
from boldqc.bids import BIDS
import boldqc.tasks as tasks
from executors.models import Job

logger = logging.getLogger(__name__)

class Task(tasks.BaseTask):
    def __init__(self, infile, outdir, tempdir=None, pipenv=None):
        self._infile = infile
        super().__init__(outdir, tempdir, pipenv)

    def build(self):
        sidecar = BIDS.sidecar_for_image(self._infile)
        mask_threshold = boldqc.get_mask_threshold(sidecar)
        cmd = [
            'selfie',
            '--lock',
            '--output-file', self._prov,
            'stackcheck_ext.sh',
            '-p',
            '-M',
            '-T',
            '-X',
            '-f', self._infile,
            '-o', self._outdir,
            '-s', str(4),
            '-N', str(99),
            '-t', str(mask_threshold)
        ]
        cmd.append(self._infile)
        logger.debug(cmd)
        if self._pipenv:
            os.chdir(self._pipenv)
            cmd[:0] = ['pipenv', 'run']
        logdir = self.logdir()
        # copy json sidecar into output logs directory
        destination = os.path.join(logdir, os.path.basename(sidecar))
        logger.debug('copying %s to %s', sidecar, destination)
        shutil.copy2(sidecar, destination)
        # return job object
        log = os.path.join(logdir, 'niftiqa.log')
        self.job = Job(
            name='stackcheck_ext',
            time='1440',
            memory='3G',
            command=cmd,
            output=log,
            error=log
        )

