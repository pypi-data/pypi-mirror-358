import re
import os
import io
import sys
import glob
import yaml
import json
import lxml
import shutil
import zipfile
import logging
from lxml import etree
from boldqc.bids import BIDS
import boldqc.parsers as parsers

logger = logging.getLogger(__name__)

class Report:
    def __init__(self, bids, sub, ses, run):
        self.module = os.path.dirname(__file__)
        self.bids = bids
        self.sub = sub
        self.run = run
        self.ses = ses if ses else ''
 
    def getdirs(self):
        self.dirs = {
            'boldqc': None
        }
        d = os.path.join(
            self.bids,
            'derivatives',
            'boldqc',
            'sub-' + self.sub.replace('sub-', ''),
            'ses-' + self.ses.replace('ses-', ''),
            'func'
        )
        basename = BIDS.basename(**{
            'sub': self.sub,
            'ses': self.ses,
            'run': self.run,
            'mod': 'bold'
        })
        dirname = os.path.join(d, basename)
        logger.debug('looking for %s', dirname)
        if os.path.exists(dirname):
            self.dirs['boldqc'] = dirname
        logger.debug('boldqc dir: %s', self.dirs['boldqc'])

    def build_assessment(self, output):
        '''
        Build XNAT assessment

        :param output: Base output directory
        '''
        basename = BIDS.basename(**{
            'sub': self.sub,
            'ses': self.ses,
            'run': self.run,
            'mod': 'bold'
        })
        self.getdirs()
        if not self.dirs['boldqc']:
            raise AssessmentError('need boldqc data to build assessment')

        # initialize namespaces
        ns = {
            None: 'http://www.neuroinfo.org/neuroinfo',
            'xs': 'http://www.w3.org/2001/XMLSchema',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xnat': 'http://nrg.wustl.edu/xnat',
            'neuroinfo': 'http://www.neuroinfo.org/neuroinfo'
        }

        # read json sidecar for scan number
        boldqc_ds = self.datasource('boldqc')
        logger.info('boldqc info %s', '|'.join(boldqc_ds.values()))

        # assessment id
        aid = '{0}_BOLD_{1}_EQC'.format(
            boldqc_ds['experiment'],
            boldqc_ds['scan']
        )
        logger.info('Assessor ID %s', aid)

        # root element
        xnatns = '{%s}' % ns['xnat']
        root = etree.Element('BOLDQC', nsmap=ns)
        root.attrib['project'] = boldqc_ds['project']
        root.attrib['ID'] = aid
        root.attrib['label'] = aid
        # get start date and time from morph provenance
        fname = os.path.join(self.dirs['boldqc'], 'logs', 'provenance.json')
        with open(fname) as fo:
            prov = json.load(fo)
        # add date and time
        etree.SubElement(root, xnatns + 'date').text = prov['start_date']
        etree.SubElement(root, xnatns + 'time').text = prov['start_time']
        # compile a list of files to be added to xnat:out section
        resources = [
            {
                'source': os.path.join(self.dirs['boldqc'], f'{basename}_mean.nii.gz'),
                'dest': os.path.join('mean-nifti', f'{aid}_mean.nii.gz')
            },
            {
                'source': os.path.join(self.dirs['boldqc'], f'{basename}_mean_thumbnail.png'),
                'dest': os.path.join('mean-image', f'{aid}_mean_thumbnail.png')
            },
            {
                'source': os.path.join(self.dirs['boldqc'], f'{basename}_mean_slice.txt'),
                'dest': os.path.join('mean-slice-data', f'{aid}_mean_slice.txt')
            },
            {
                'source': os.path.join(self.dirs['boldqc'], f'{basename}_mean_slice.png'),
                'dest': os.path.join('mean-slice-image', f'{aid}_mean_slice.png')
            },
            {
                'source': os.path.join(self.dirs['boldqc'], f'{basename}_mask.nii.gz'),
                'dest': os.path.join('mask-nifti', f'{aid}_mask.nii.gz')
            },
            {
                'source': os.path.join(self.dirs['boldqc'], f'{basename}_mask_thumbnail.png'),
                'dest': os.path.join('mask-image', f'{aid}_mask_thumbnail.png')
            },
            {
                'source': os.path.join(self.dirs['boldqc'], f'{basename}_snr.nii.gz'),
                'dest': os.path.join('snr-nifti', f'{aid}_snr.nii.gz')
            },
            {
                'source': os.path.join(self.dirs['boldqc'], f'{basename}_snr_thumbnail.png'),
                'dest': os.path.join('snr-image', f'{aid}_snr_thumbnail.png')
            },
            {
                'source': os.path.join(self.dirs['boldqc'], f'{basename}_stdev.nii.gz'),
                'dest': os.path.join('stdev-nifti', f'{aid}_stdev.nii.gz')
            },
            {
                'source': os.path.join(self.dirs['boldqc'], f'{basename}_stdev_thumbnail.png'),
                'dest': os.path.join('stdev-image', f'{aid}_stdev_thumbnail.png')
            },
            {
                'source': os.path.join(self.dirs['boldqc'], f'{basename}_motion.png'),
                'dest': os.path.join('motion-image', f'{aid}_motion.png')
            },
            {
                'source': os.path.join(self.dirs['boldqc'], f'{basename}_slope.nii.gz'),
                'dest': os.path.join('slope-nifti', f'{aid}_slope.nii.gz')
            },
            {
                'source': os.path.join(self.dirs['boldqc'], f'{basename}_slope_thumbnail.png'),
                'dest': os.path.join('slope-image', f'{aid}_slope_thumbnail.png')
            },
            {
                'source': os.path.join(self.dirs['boldqc'], f'{basename}_auto_report.txt'),
                'dest': os.path.join('auto-report', f'{aid}_auto_report.txt')
            },
            {
                'source': os.path.join(self.dirs['boldqc'], f'{basename}_slice_report.txt'),
                'dest': os.path.join('slice-report', f'{aid}_slice_report.txt')
            }
        ]

        floatfmt = lambda x: '{:f}'.format(float(x))

        # parse auto_report
        auto_report_file = os.path.join(self.dirs['boldqc'], f'{basename}_auto_report.txt')
        auto_report = parsers.parse_auto_report(auto_report_file)
        # parse slice_report
        slice_report_file = os.path.join(self.dirs['boldqc'], f'{basename}_slice_report.txt')
        slice_report = parsers.parse_slice_report(slice_report_file)
        # start building XML
        xnatns = '{%s}' % ns['xnat']
        etree.SubElement(root, xnatns + 'imageSession_ID').text = boldqc_ds['experiment_id']
        etree.SubElement(root, 'bold_scan_id').text = boldqc_ds['scan']
        etree.SubElement(root, 'session_label').text = boldqc_ds['experiment']
        etree.SubElement(root, 'Size').text = auto_report['InputFileSize']
        etree.SubElement(root, 'N_Vols').text = auto_report['N_Vols']
        etree.SubElement(root, 'Skip').text = auto_report['Skip']
        etree.SubElement(root, 'qc_N_Tps').text = auto_report['qc_N_Tps']
        etree.SubElement(root, 'qc_thresh').text = floatfmt(auto_report['qc_thresh'])
        etree.SubElement(root, 'qc_nVox').text = auto_report['qc_nVox']
        etree.SubElement(root, 'qc_Mean').text = floatfmt(auto_report['qc_Mean'])
        etree.SubElement(root, 'qc_Max').text = floatfmt(slice_report['qc_Max'])
        etree.SubElement(root, 'qc_Min').text = floatfmt(slice_report['qc_Min'])
        etree.SubElement(root, 'qc_Stdev').text = floatfmt(auto_report['qc_Stdev'])
        etree.SubElement(root, 'qc_sSNR').text = floatfmt(auto_report['qc_sSNR'])
        etree.SubElement(root, 'qc_vSNR').text = floatfmt(auto_report['qc_vSNR'])
        etree.SubElement(root, 'qc_slope').text = floatfmt(auto_report['qc_slope'])
        etree.SubElement(root, 'mot_N_Tps').text = auto_report['mot_N_Tps']
        etree.SubElement(root, 'mot_rel_x_mean').text = floatfmt(auto_report['mot_rel_x_mean'])
        etree.SubElement(root, 'mot_rel_x_sd').text = floatfmt(auto_report['mot_rel_x_sd'])
        etree.SubElement(root, 'mot_rel_x_max').text = floatfmt(auto_report['mot_rel_x_max'])
        etree.SubElement(root, 'mot_rel_x_1mm').text = auto_report['mot_rel_x_1mm']
        etree.SubElement(root, 'mot_rel_x_5mm').text = auto_report['mot_rel_x_5mm']
        etree.SubElement(root, 'mot_rel_y_mean').text = floatfmt(auto_report['mot_rel_y_mean'])
        etree.SubElement(root, 'mot_rel_y_sd').text = floatfmt(auto_report['mot_rel_y_sd'])
        etree.SubElement(root, 'mot_rel_y_max').text = floatfmt(auto_report['mot_rel_y_max'])
        etree.SubElement(root, 'mot_rel_y_1mm').text = auto_report['mot_rel_y_1mm']
        etree.SubElement(root, 'mot_rel_y_5mm').text = auto_report['mot_rel_y_5mm']
        etree.SubElement(root, 'mot_rel_z_mean').text = floatfmt(auto_report['mot_rel_z_mean'])
        etree.SubElement(root, 'mot_rel_z_sd').text = floatfmt(auto_report['mot_rel_z_sd'])
        etree.SubElement(root, 'mot_rel_z_max').text = floatfmt(auto_report['mot_rel_z_max'])
        etree.SubElement(root, 'mot_rel_z_1mm').text = auto_report['mot_rel_z_1mm']
        etree.SubElement(root, 'mot_rel_z_5mm').text = auto_report['mot_rel_z_5mm']
        etree.SubElement(root, 'mot_rel_xyz_mean').text = floatfmt(auto_report['mot_rel_xyz_mean'])
        etree.SubElement(root, 'mot_rel_xyz_sd').text = floatfmt(auto_report['mot_rel_xyz_sd'])
        etree.SubElement(root, 'mot_rel_xyz_max').text = floatfmt(auto_report['mot_rel_xyz_max'])
        etree.SubElement(root, 'mot_rel_xyz_1mm').text = auto_report['mot_rel_xyz_1mm']
        etree.SubElement(root, 'mot_rel_xyz_5mm').text = auto_report['mot_rel_xyz_5mm']
        etree.SubElement(root, 'rot_rel_x_mean').text = floatfmt(auto_report['rot_rel_x_mean'])
        etree.SubElement(root, 'rot_rel_x_sd').text = floatfmt(auto_report['rot_rel_x_sd'])
        etree.SubElement(root, 'rot_rel_x_max').text = floatfmt(auto_report['rot_rel_x_max'])
        etree.SubElement(root, 'rot_rel_y_mean').text = floatfmt(auto_report['rot_rel_y_mean'])
        etree.SubElement(root, 'rot_rel_y_sd').text = floatfmt(auto_report['rot_rel_y_sd'])
        etree.SubElement(root, 'rot_rel_y_max').text = floatfmt(auto_report['rot_rel_y_max'])
        etree.SubElement(root, 'rot_rel_z_mean').text = floatfmt(auto_report['rot_rel_z_mean'])
        etree.SubElement(root, 'rot_rel_z_sd').text = floatfmt(auto_report['rot_rel_z_sd'])
        etree.SubElement(root, 'rot_rel_z_max').text = floatfmt(auto_report['rot_rel_z_max'])
        etree.SubElement(root, 'mot_abs_x_mean').text = floatfmt(auto_report['mot_abs_x_mean'])
        etree.SubElement(root, 'mot_abs_x_sd').text = floatfmt(auto_report['mot_abs_x_sd'])
        etree.SubElement(root, 'mot_abs_x_max').text = floatfmt(auto_report['mot_abs_x_max'])
        etree.SubElement(root, 'mot_abs_y_mean').text = floatfmt(auto_report['mot_abs_y_mean'])
        etree.SubElement(root, 'mot_abs_y_sd').text = floatfmt(auto_report['mot_abs_y_sd'])
        etree.SubElement(root, 'mot_abs_y_max').text = floatfmt(auto_report['mot_abs_y_max'])
        etree.SubElement(root, 'mot_abs_z_mean').text = floatfmt(auto_report['mot_abs_z_mean'])
        etree.SubElement(root, 'mot_abs_z_sd').text = floatfmt(auto_report['mot_abs_z_sd'])
        etree.SubElement(root, 'mot_abs_z_max').text = floatfmt(auto_report['mot_abs_z_max'])
        etree.SubElement(root, 'mot_abs_xyz_mean').text = floatfmt(auto_report['mot_abs_xyz_mean'])
        etree.SubElement(root, 'mot_abs_xyz_sd').text = floatfmt(auto_report['mot_abs_xyz_sd'])
        etree.SubElement(root, 'mot_abs_xyz_max').text = floatfmt(auto_report['mot_abs_xyz_max'])
        etree.SubElement(root, 'rot_abs_x_mean').text = floatfmt(auto_report['rot_abs_x_mean'])
        etree.SubElement(root, 'rot_abs_x_sd').text = floatfmt(auto_report['rot_abs_x_sd'])
        etree.SubElement(root, 'rot_abs_x_max').text = floatfmt(auto_report['rot_abs_x_max'])
        etree.SubElement(root, 'rot_abs_y_mean').text = floatfmt(auto_report['rot_abs_y_mean'])
        etree.SubElement(root, 'rot_abs_y_sd').text = floatfmt(auto_report['rot_abs_y_sd'])
        etree.SubElement(root, 'rot_abs_y_max').text = floatfmt(auto_report['rot_abs_y_max'])
        etree.SubElement(root, 'rot_abs_z_mean').text = floatfmt(auto_report['rot_abs_z_mean'])
        etree.SubElement(root, 'rot_abs_z_sd').text = floatfmt(auto_report['rot_abs_z_sd'])
        etree.SubElement(root, 'rot_abs_z_max').text = floatfmt(auto_report['rot_abs_z_max'])

        # write assessor to output mount location.
        xmlstr = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        assessor_dir = os.path.join(output, 'assessor')
        os.makedirs(assessor_dir, exist_ok=True)
        assessment_xml = os.path.join(assessor_dir, 'assessment.xml')
        logger.debug(f'writing {assessment_xml}')
        with open(assessment_xml, 'wb') as fo:
            fo.write(xmlstr)

        # copy resources to output mount location
        resources_dir = os.path.join(output, 'resources')
        os.makedirs(resources_dir, exist_ok=True)
        logger.debug(f'copying resources into {resources_dir}')
        for resource in resources:
            src = resource['source']
            dest = os.path.join(resources_dir, resource['dest'])
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copyfile(src, dest)

    def datasource(self, task):
        basename = os.path.basename(self.dirs[task])
        sidecar = os.path.join(self.dirs[task], 'logs', basename + '.json')
        if not os.path.exists(sidecar):
            raise FileNotFoundError(sidecar)
        with open(sidecar) as fo:
            js = json.load(fo)
        return js['DataSource']['application/x-xnat']

    def protocol(self, task):
        basename = os.path.basename(self.dirs[task])
        sidecar = os.path.join(self.dirs[task], 'logs', basename + '.json')
        if not os.path.exists(sidecar):
            raise FileNotFoundError(sidecar)
        with open(sidecar) as fo:
            js = json.load(fo)
        return js['ProtocolName']

class AssessmentError(Exception):
    pass
