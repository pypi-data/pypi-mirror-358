import os
import re
import numpy as np

def parse_auto_report(f):
    data = dict()
    with open(f) as fo:
        content = fo.read().split(os.linesep)
    for line in content:
        line = line.strip()
        if not line: continue
        key,value = re.match('^(.*?)\s+(.*)$', line).groups()
        data[key] = value
    return data

def parse_slice_report(f):
    start_line = re.compile('^slice\s+voxels\s+mean\s+stdev\s+snr\s+min\s+max\s+#out$')
    end_line = re.compile('^VOXEL.*$')
    data = list()
    with open(f) as fo:
        for line in fo:
            line = line.strip()
            if start_line.match(line):
                break
        for line in fo:
            line = line.strip()
            if end_line.match(line):
                break
            if line:
                data.append([float(x) for x in line.split()])
        data = np.array(data)
    return {
        'qc_Min': str(np.min(data[:,5])),
        'qc_Max': str(np.max(data[:,6]))
    }

