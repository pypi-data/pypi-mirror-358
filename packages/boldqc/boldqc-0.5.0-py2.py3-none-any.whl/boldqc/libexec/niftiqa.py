#!/usr/bin/env python

import matplotlib
matplotlib.use("Agg")

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import hashlib
import math
import nibabel
import numpy
import os
import sys
import datetime
try:
    import Image
except ImportError:
    from PIL import Image

class ProcessingHistory:
    def __init__(self, message='', parent=None, caller_info=None, css_class='prov-history', frame=0):
        self._message = message
        self._parent = parent
        self._caller_info = caller_info
        self._css_class = css_class
        self._children = []
        if caller_info is None:
            self._caller_info = self.__caller_str(frame)
        return None

    def __caller_str(self,frame=0):
        frame += 1
        callee = sys._getframe(frame)
        try:
            caller = sys._getframe(frame + 1)
            caller = ("Function "+str(caller.f_code.co_name)
                      +"() at line "+str(caller.f_lineno)
                      +" in '"+str(caller.f_code.co_filename)
                      +"'")
        except ValueError as e:
            caller = "Some undetermined function"
        return (caller
                +" called "+str(callee.f_code.co_name)
                +"() at line "+str(callee.f_lineno)
                +" in '"+str(callee.f_code.co_filename)+"'")


    def get_message(self): return self._message

    def get_caller_info(self): return self._caller_info

    def add(self,history_or_message, caller_info=None, frame=0):
        frame += 2
        if isinstance(history_or_message, ProcessingHistory):
            child = history_or_message
        else:
            if caller_info is None:
                self._caller_info = self.__caller_str(frame)
            child = ProcessingHistory(history_or_message,self,caller_info)
        # print "HISTORY: '%s' %s" %(child.get_message(), child.get_caller_info())
        self._children.append(child)
        return child

    def get_children(self): return self._children

    def get_children_as_html(self):
        if len(self.get_children()) == 0:
            return ''
        html = ''
        html_start = '<ol class="%s">' %(self._css_class)
        html_end = '</ol>'
        for child in self.get_children():
            html += child.as_html()
        return html_start + html + html_end

    def escape_xml(self,xml):
        """
        Returns the given XML/HTML with ampersands, quotes and carets encoded.
        Paraphrased from
        http://stackoverflow.com/questions/275174/how-do-i-perform-html-decoding-encoding-using-python-django
        """
        return xml.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

    def as_html(self):
        if self._parent is None:
            # Root node is a special case
            if len(self.get_children()) == 0:
                return '<span class="%s">Processing History%s: No History Available</span>' %(
                self._css_class,
                self.escape_xml(self.get_message())
                )
            html_start = '<span class="%s">Processing History%s:<ol class="%s">' %(
                self._css_class,
                self.escape_xml(self.get_message()),
                self._css_class,
                )
            html_end = '</ol></span>'
        else:
            html_message = '<span title="%s" class="%s-msg">%s</span>' %(
                self.escape_xml(self.get_caller_info()),
                self._css_class,
                self.escape_xml(self.get_message())
                )
            html_start = '<li class="%s">%s' %(
                self._css_class,
                html_message,
                )
            html_end = '</li>'
        return html_start + self.get_children_as_html() + html_end


class NeuroImageFileBase:
    _verbosity = 0

    def set_verbosity(self,val):
        _verbosity = val
        return self

    def get_verbosity(): return _verbosity

    def get_output_dir(self): 

        if (self._output_dir is None):
            return self.get_dirname()

        return self._output_dir

    def __init__(self,
                 parent,
                 title,
                 description,
                 can_be_in_img_tag = False,
                 suffix = '',
                 basename = '',
                 dirname = '',
                 extension = '',
                 output_dir = None
                ):
        self._can_be_in_img_tag = can_be_in_img_tag
        self._parent = parent
        self._suffix = suffix
        self._output_dir = output_dir
        if basename is None:
            if parent is None:
                self._basename = 'UNKNOWN_BASENAME_ERROR'
            else:
                self._basename = parent.get_basename()
        else:
            self._basename = basename
        if dirname is None:
            if parent is None:
                self._dirname = ''
            else:
                self._dirname = parent.get_dirname()
        else:
            self._dirname = dirname
        self._extension = extension
        self._needs_saving = True
        self._saved_files = []
        self._children = []
        if parent is not None:
            parent.add_child(self)
            self._history = ProcessingHistory(parent=parent._history)
        else:
            self._history = ProcessingHistory(parent=None)
        if True:
            parent_str = 'None'
            parent_child_count = 0
            if parent is not None:
                parent_str = os.path.basename(parent.get_filename())
                parent_child_count = len(parent.get_children())
            # print "NeuroImageFileBase(parent='%s',title='%s') parent children: %s" %(parent_str,title,parent_child_count) 
        # print "NeuroImageFileBase.__init__: dirname='%s', basename='%s', suffix='%s'" %(self._dirname, self._basename , self._suffix)
        self._css = '''<style type="text/css">
body { background:#DDDDEE; }
table {
  margin: 8px 2px 8px 2px;
  padding: 1px;
  font: normal 0.9em tahoma, arial, sans-serif;
  line-height:1.4em;
  border-collapse:collapse;
  border:1px solid #AAAAAA;
  color: #4F6480;
  background: #ADBBCA;
}
table caption {
  margin: 0px;
  height: 22px;
  padding: 0;
  color: #4F6480;
  line-height: 2em;
  text-align: left;
  font: bold 150% georgia, serif;
  text-transform: uppercase;
  letter-spacing: 0.14em;
}
thead tr th {
  padding: 1px 2px 2px 2px;
  border: 1px solid #ADBBCA;
  color: #FFFFFF;
  background: #5E7796;
}
tbody tr td {
  margin:1px;
  background: #E9ECEE;
}
tbody tr:nth-child(odd) td {
  background: #DDDDEE;
  color: #4F6480;
}
tbody tr:hover td {
  background: #FFFFFF;
}
tbody tr td:hover {
  background: #DDDDDD;
}
tbody tr th {
  padding: 1px;
  background: #F0F0F0;
  border: 1px solid #ADBBCA;
}
tbody tr th a:link {
  font: bold 0.9em tahoma, arial, sans-serif;
  color: #5E7796;
  text-decoration: underline;
}
tbody tr th a:visited {
  font: bold 0.9em tahoma, arial, sans-serif;
  color: #5E7796;
  text-decoration: none;
}
tbody tr th a:hover {
  font: bold 0.9em tahoma, arial, sans-serif;
  color: #5E7796;
  text-decoration: none;
}
tbody tr th a:active {
  font: bold 0.9em tahoma, arial, sans-serif;
  color: #5E7796;
  text-decoration: line-through;
}
tbody tr td a:link {
  font: normal 0.9em tahoma, arial, sans-serif;
  color: #808000;
  text-decoration: underline;
}
tbody tr td a:visited {
  font: normal 0.9em tahoma, arial, sans-serif;
  color: #808000;
  text-decoration: none;
}
tbody tr td a:hover {
  font: normal 0.9em tahoma, arial, sans-serif;
  color: #808000;
  text-decoration: none;
}
tbody tr td a:active {
  font: normal 0.9em tahoma, arial, sans-serif;
  color: #808000;
  text-decoration: underline;
}
</style>
'''
        return None

    def _set_attr_str(self,attr_name,attr_val):
        attr_val = str(attr_val)
        if attr_name not in self.__dict__ or self.__dict__[attr_name] != attr_val:
            self.__dict__[attr_name] = attr_val
        return self

    def _set_attr_int(self,attr_name,attr_val):
        try:
            attr_int = int(attr_val)
        except:
            called_function = sys._getframe(2).f_code.co_name
            calling_lineno = sys._getframe(3).f_lineno
            calling_file = sys._getframe(3).f_filename
            calling_function = sys._getframe(3).f_code.co_name
            raise ValueError("%(attr_name)s must be a int (or castable to a int). %(calling_function)s"+
                             "called %(called_function)s() at line %(calling_lineno)d"
                             +" in '%(calling_file)s" %(locals()))
        if attr_name not in self.__dict__ or self.__dict__[attr_name] != attr_int:
            self.__dict__[attr_name] = attr_int
        return self

    def _set_attr_float(self,attr_name,attr_val):
        try:
            attr_float = float(attr_val)
        except:
            called_function = sys._getframe(2).f_code.co_name
            calling_lineno = sys._getframe(3).f_lineno
            calling_file = sys._getframe(3).f_filename
            calling_function = sys._getframe(3).f_code.co_name
            raise ValueError("%(attr_name)s must be a float (or castable to a float). %(calling_function)s"+
                             "called %(called_function)s() at line %(calling_lineno)d"
                             +" in '%(calling_file)s" %(locals()))
        if attr_name not in self.__dict__ or self.__dict__[attr_name] != attr_float:
            self.__dict__[attr_name] = attr_float
        return self

    def _set_attr(self,attr_name,attr_val,attr_type=None,none_ok=False):
        if attr_name in self.__dict__:
            if self.__dict__[attr_name] == attr_val:
                return self
        if attr_type is not None and not isinstance(attr_val,attr_type):
            ok = none_ok and attr_type is None
            if not ok:
                called_function = sys._getframe(2).f_code.co_name
                calling_lineno = sys._getframe(3).f_lineno
                calling_file = sys._getframe(3).f_filename
                calling_function = sys._getframe(3).f_code.co_name
                raise ValueError("%(attr_name)s must be a %(attr_type). %(calling_function)s"+
                                 "called %(called_function)s() at line %(calling_lineno)d"
                                 +" in '%(calling_file)s" %(locals()))
        self.__dict__[attr_name] = attr_val
        return self

    def __exept_isinstance(self,attr_val,attr_type,none_ok=False):
        if not isinstance(attr_val,attr_type):
            ok = none_ok and attr_type is None
            if not ok:
                called_function = sys._getframe(2).f_code.co_name
                calling_lineno = sys._getframe(3).f_lineno
                calling_file = sys._getframe(3).f_filename
                calling_function = sys._getframe(3).f_code.co_name
                raise ValueError("%(attr_name)s must be a %(attr_type). %(calling_function)s"+
                                 "called %(called_function)s() at line %(calling_lineno)d"
                                 +" in '%(calling_file)s" %(locals()))
        return self

    def split_filepath(self,filename):
        (orig_dirname,basename) = os.path.split(filename)
        dirname = os.path.abspath(orig_dirname)
        if basename == '':
            extension = ''
        else:
            (basename,extension) = os.path.splitext(basename)
            if extension == '.gz' or extension == '.bz2':
                (basename,extension2) = os.path.splitext(basename)
                extension = extension2 + extension
        return dirname, basename, extension, orig_dirname


    def set_parent(self,value): return self._set_attr('_parent',value,NeuroImageBase,none_ok=True)
    def get_parent(self): return self._parent

    def set_suffix(self,value): return self._set_attr_str('_suffix',value)
    def get_suffix(self): return self._suffix

    def set_dirname(self,value): return self._set_attr_str('_dirname',value)
    def get_dirname(self): return self._dirname

    def set_basename(self,value): return self._set_attr_str('_basename',value)
    def get_basename(self): return self._basename

    def set_extension(self,value): return self._set_attr_str('_extension',value,)
    def get_extension(self): return self._extension

    def set_needs_saving(self,value): return self._set_attr('_needs_saving',value,bool)
    def get_needs_saving(self): return self._needs_saving

    def get_history(self): return self._history

    def add_child(self,child):
        self.__exept_isinstance(child,NeuroImageFileBase)
        self._children.append(child)
        return self

    def get_children(self): return self._children

    def get_saved_files(self): return self._saved_files

    def get_saved_files_as_ol(self):
        # print "SAVED FILES: %s CHILDREN: %s for '%s'" %(len(self.get_saved_files()),self.get_filename())
        ol='<ol>';
        for filename in self.get_saved_files():
            filename = os.path.basename(filename)
            ol += '<li><a href="%s">%s</a></li>' %(filename,filename)
        for child in self.get_children():
            ol += child.get_saved_files_as_ol()
        return ol+'</ol>'

    def set_filename(self,filename):
        dirname, basename, extension, orig_dirname = self.split_filepath(filename)
        # print "filename = %s'" %(filename)
        # print "dirname = '%s'" %(dirname)
        # print "basename = '%s'" %(basename)
        # print "extension = '%s'" %(extension)
        # print "orig_dirname = '%s'" %(orig_dirname)
        self.set_dirname(dirname)
        self.set_basename(basename)
        self.set_suffix('')
        self.set_extension(extension)
        # print "self.get_dirname() = '%s'" %(self.get_dirname())
        # print "self.get_basename() = '%s'" %(self.get_basename())
        # print "self.get_extension() = '%s'" %(self.get_extension())
        # print "self.get_filename() = %s'" %(self.get_filename())
        return self

    def get_filename(self):
        return self.get_filename_root() + self._extension

    def get_output_filename_root(self):
        return os.path.join(self.get_output_dir(), self._basename + self._suffix)

    def get_filename_root(self):
        return os.path.join(self._dirname, self._basename + self._suffix)

    def _capture_file_save(self,filename,what=None):
        self._saved_files.append(filename)
        if what is not None:
            self._history.add("Saved %s for '%s' to '%s'" %(
                    what,
                    os.path.basename(self.get_filename()),
                    os.path.basename(filename) ,
                    ))
        else:
            self._history.add("Saved to '%s'" %(
                    os.path.basename(filename),
                    ))
        print(("[Saving] '%s'" % (filename)))
        return self

    def save_xml(self):
        print("WARNING: save_xml() not implemented yet!!!!!")
        return self

    def save_html(self):
        filename = self.get_output_filename_root() + "_history.html"
        self._capture_file_save(filename,'history')
        fh = open(filename,"w")
        fh.write('''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <title>'''+ self.get_basename() +''': History Report</title>
'''+self._css+'''</head>
<body>
<h1>Processing History Report for '''+ self.get_basename() +'''</h1>
''')
        fh.write("<h1>Image Processing History</h1>\n")
        fh.write(self._history.as_html())
        filename = os.path.basename(self.get_filename())
        histogram = ''
        if hasattr(self,'_histogram_filename') and self._histogram_filename is not None:
            histogram = os.path.basename(self._histogram_filename)
            histogram = '<a href="%s"><img src="%s" /></a>' %(histogram,histogram)
        if filename.endswith('.png') or filename.endswith('.svg'):
            fh.write('<h2>Image File:</h2>\n<div><a href="%s"><img src="%s" /></a>%s</div>' %(
                    filename,
                    filename,
                    histogram,
                    ))
        else:
            fh.write("<h2>Image File: <a href=\"%s\">%s</a></h2>\n" %(
                    filename,
                    filename,
                    ))
        fh.write("<h2>Saved Files:</h2>\n")
        fh.write(self.get_saved_files_as_ol())
        fh.write("</body>\n")
        fh.write("</html>\n")
        fh.close()
        return self

class TwoDimNeuroImage(NeuroImageFileBase):
    def __init__(self,
                 parent=None,
                 title=None,
                 description=None,
                 suffix = '',
                 basename = None,
                 dirname = None,
                 extension = '.png',
                 volume_idx = None,
                 max_width = None,
                 output_dir = None,
                 transparent = True,
                 ):
        NeuroImageFileBase.__init__(
            self,
            parent=parent,
            title=title,
            description=description,
            can_be_in_img_tag=True,
            suffix=suffix,
            basename=basename,
            dirname=dirname,
            extension=extension,
            output_dir=output_dir
            )

        self.set_transparent(transparent)

        if self.get_filename() == '':
            self.set_filename(parent.get_output_filename_root() + '.png')

        self._volume_idx          = volume_idx
        self._max_width           = max_width

        orig_data = self.get_parent().get_data()
        self._raw_2d_data = orig_data

        # Only allow 3D images, if it's 4D, and we were not told which volume
        # index to take, take the middle one or middle one - 1
        if volume_idx is None and len(orig_data.shape) == 4:
            volume_idx = int(orig_data.shape[3] / 2)

        if volume_idx is not None:
            # For 4D images, take the specified volume
            self._data = orig_data[:,:,:,volume_idx].copy()
        else:
            # For 3D, take the whole thing.
            self._data = orig_data.copy()
        # Flip along x and y so that it is oriented correctly for the mosaic
        self._data = self._data[::-1,::-1,:]

        # Set image parameters
        self._size_x        = self._data.shape[0]
        self._size_y        = self._data.shape[1]
        self._size_z        = self._data.shape[2]
        if self._max_width is not None:
            self._slices_across = int(self._max_width / self._size_x)
        else:
            self._slices_across = int(math.ceil(math.sqrt(self._size_z)))
        # print "Max width = %s, slice width = %s, slices across = %s, effective width = %s" %(
        #     self._max_width,
        #     self._size_x,
        #     self._slices_across,
        #     self._size_x * self._slices_across,
        #     )
        self._slices_down   = int(math.ceil(self._size_z * 1.0 / self._slices_across))
        self._image_width   = self._slices_across * self._size_x
        self._image_height  = self._slices_down * self._size_y

        data_in_2d = numpy.zeros((self._image_width,self._image_height))
        data_2d_alpha = numpy.zeros((self._image_width,self._image_height),dtype='uint8')
        for z_idx in range(self._size_z):
            # Calculate the offset for this image in this slice
            x_offset = ((
                    self._slices_across - (z_idx % self._slices_across)) * self._size_x) - self._size_x
            y_offset = int(z_idx / self._slices_across) * self._size_y
            #print "Slice %02d x_offset = %s, y_offest = %s" %(z_idx+1, x_offset, y_offset)
            for x_idx in range(self._size_x):
                for y_idx in range(self._size_y):
                    data_in_2d[x_offset + x_idx, y_offset + y_idx] = self._data[x_idx, y_idx, z_idx]
                    data_2d_alpha[x_offset + x_idx, y_offset + y_idx] = 255
        self._raw_2d_data = data_in_2d
        self._array_mask = (data_2d_alpha == 0)
        if self.get_transparent() is False:
            data_2d_alpha[:,:] = 255
        self._alpha = data_2d_alpha
        self.reset()
        return None

    def _rebuild_masked_data(self):
        self._masked_data = numpy.ma.array(self._data.copy(),mask=self._array_mask).flatten().compressed()

    def _rebuild_files(self):
        self._filename = None
        self._histogram_plot = None
        self._histogram_filename = None
        self._html_history_filename = None
        self._xml_history_filename = None

    def reset(self):
        # print "Reset image..."
        self._filename = None
        self._data = self._raw_2d_data.copy()
        self._red = None
        self._green = None
        self._blue = None
        self._above_range_data = None
        self._below_range_data = None
        self._range_min = None
        self._range_max = None
        self._range_stdev_min = None
        self._range_stdev_max = None
        self._range_stdevs = None
        self._color_out_of_range = True
        self._equalize = False
        self._fill_histogram = False
        self._ignore_zero_mins = False
        self._history = ProcessingHistory()
        self._rebuild_masked_data()
        self._rebuild_files()
        return self

    def set_parent(self,value): return self._set_attr('_parent',value,NeuroImage)


    def get_history_as_html(self,history=None):
        if history is None:
            history = self.get_history()

    def _shrink_range(self,what,range_min,range_max):
        if ( self._range_min == range_min and
             self._range_max == range_max ):
            self._history.add("Note: Attempt to set %s to same current range (from '%s' to '%s') ignored."
                              %(what,range_min,range_max))
            return self
        if ( self._range_min is not None and
             self._range_min > range_min and
             self._range_max is not None and
             self._range_max < range_max ):
            self._history.add("Note: Attempt to set %s to a larger range  than current (from '%s' to '%s') ignored."
                                    %(what,range_min,range_max))
            return self

        self._range_min = range_min
        self._range_max = range_max

        data_min = self._masked_data.min()
        data_max = self._masked_data.max()

        if data_min >= range_min and data_max <= range_max:
            self._history.add(
                "Note: Set %s, but data range was '%s' to '%s', so the data were not altered."
                %(what,data_min,data_max)
                )
            return self

        hist = self._history.add("Set %s." %(what))
        if data_min < range_min:
            if self._below_range_data is None:
               self._below_range_data = numpy.zeros(self._data.shape)
            to_change = (self._data < range_min)
            to_change_masked = (self._masked_data < range_min)
            hist.add("Increased values of %d pixels to range minimum of '%s' (dat minimum was '%s')."
                           %(to_change_masked.sum(),range_min,data_min)
                           )
            self._below_range_data[to_change] = range_min - self._data[to_change]
            self._data[to_change] = range_min
            self._masked_data[to_change_masked] = range_min
            self._rebuild_files()
        else:
            hist.add("No values below range minimum.")
        if data_max > range_max:
            if self._above_range_data is None:
               self._above_range_data = numpy.zeros(self._data.shape)
            to_change = self._data > range_max
            to_change_masked = (self._masked_data > range_max)
            hist.add("Decreased values of %d pixels to range maximum '%s' (data maximum was '%s')."
                           %(to_change_masked.sum(),range_max,data_max)
                           )
            self._above_range_data[to_change] = self._data[to_change] - range_max
            self._data[to_change] = range_max
            self._masked_data[to_change_masked] = range_max
            self._rebuild_files()
        else:
            hist.add("No values above range maximum.")
        return self

    def set_range(self,range_min,range_max):
        what = "data range from '%s' to '%s'" %(range_min,range_max)
        return self._shrink_range(what,range_min,range_max)

    def set_range_stdevs(self,range_stdevs):
        data_mean  = self._masked_data.mean()
        data_stdev = self._masked_data.std()
        range_stdev_min  = data_mean - (range_stdevs * data_stdev)
        range_stdev_max  = data_mean + (range_stdevs * data_stdev)
        what = "StDev range to +/-%s ('%s' to '%s')" %(range_stdevs,range_stdev_min,range_stdev_max)
        return self._shrink_range(what,range_stdev_min,range_stdev_max)

    def set_percentile_range(self,lower=None,upper=None):
        if lower is None and upper is None:
            raise Exception('At least one of lower or upper must be specified when calling set_percentile_range()')

        tmp_data = numpy.sort(self._masked_data)
        if lower is not None:
            lower_idx = int(
                (lower/100.0) * # change to 0.0 to 1.0 format
                (tmp_data.size - 1) # multiply by potential indexes
                + 0.5 # round the number
                )
            percentile_range_min = tmp_data[lower_idx]
        else:
            percentile_range_min = None
            lower_idx = None
        if upper is not None:
            upper_idx = int(
                (1 - (upper/100.0)) * # change to 0.0 to 1.0 format
                (tmp_data.size - 1) # multiply by potential indexes
                + 0.5 # round the number
                )
            percentile_range_max = tmp_data[upper_idx]
        else:
            percentile_range_max = None
            upper_idx = None
        # print "self._data.size='%s', tmp_data.size='%s'" %(self._data.size,tmp_data.size)
        # print "lower='%s', percentile_range_min='%s' @ index='%s'" %(lower,percentile_range_min,lower_idx)
        # print "upper='%s', percentile_range_max='%s' @ index='%s'" %(upper,percentile_range_max,upper_idx)
        what = "Percentile range from '%s%%' to '%s%%' ('%s' to '%s')" %(lower,upper,percentile_range_min,percentile_range_max)
        return self._shrink_range(what,percentile_range_min,percentile_range_max)

    def _masked_histogram(self,data):
        masked_data = numpy.ma.array(data,mask=self._array_mask).compressed()
        return numpy.histogram(masked_data,bins=256)[0]

    def save_histogram(self,transparent=True):
        filename = self.get_output_filename_root() + "_histogram.svg"
        if self._histogram_filename == filename:
            return self
        self._histogram_filename = filename
        figure = self.get_histogram()
        self._capture_file_save(self._histogram_filename,what='histogram')
        figure.savefig(filename,format="svg",transparent=transparent,bbox_inches='tight')
        return self

    def get_histogram(self,create=True):
        if self._histogram_plot is not None or not create:
            return self._histogram_plot
        width, height = (self._data.shape[0], self._data.shape[1])
        figure = Figure()
        canvas = FigureCanvas(figure)
        # Can't just use a numpy.histogram, as we don't want to count pixels with
        # alpha = 0:
        #hist = numpy.histogram(self._red,bins=256)[0]
        #hist = self._alpha_uint8_histogram(self._red)
        hist = self._masked_histogram(self._red)
        title="Intensity Histogram"
        # It seems that matplotlib.pyplot.autoscale is till not available on many
        # systems.
        ymax = hist.max()
        axis = figure.add_subplot(111)
        grayscale = numpy.array_equal(self._red, self._blue) and numpy.array_equal( self._red, self._green)
        if not grayscale:
            axis.plot(hist, linewidth=0.5, antialiased=True, color='red', label="Red")
            #hist = numpy.histogram(self._green,bins=256)[0]
            #hist = self._alpha_uint8_histogram(self._green, "Green")
            hist = self._masked_histogram(self._green)
            axis.plot(hist, linewidth=0.5, antialiased=True, color='green', label="Green")
            tmp_max = hist.max()
            if(tmp_max > ymax):
                ymax = tmp_max
            #hist = numpy.histogram(self._blue,bins=256)[0]
            #hist = self._alpha_uint8_histogram(self._blue, "Blue")
            hist = self._masked_histogram(self._blue)
            axis.plot(hist, linewidth=0.5, antialiased=True, color='blue', label="Blue")
            tmp_max = hist.max()
            if(tmp_max > ymax):
                ymax = tmp_max
            title="RGB Intensity Histogram"
            axis.legend(('Red','Green','Blue'))
        else:
            axis.plot(hist)
        # print "xmin='%s',xmax='%s',ymin='%s',ymax='%s'" %(0,255,0,ymax)
        # print "axis.dataLim.bounds=",axis.dataLim.bounds
        # print "axis.get_xlim()=",axis.get_xlim()
        # print "axis.get_ylim()=",axis.get_ylim()
        axis.set_xlim(0,255)
        axis.set_ylim(0,ymax)
        axis.grid(True,color='#CCCCCC',linewidth=1,linestyle='-')
        axis.set_xlabel("Intensity (0-255)",fontsize=10)
        axis.set_ylabel("Frequency (Pixel Count)",fontsize=10)
        axis.set_title(title,fontsize=11)
        for spine in list(axis.spines.values()):
            spine.set_color('#AAAAAA')
        for tick in axis.xaxis.get_major_ticks() + axis.yaxis.get_major_ticks():
            tick.tick1line.set_mec('#AAAAAA')
            tick.tick2line.set_mec('#AAAAAA')
            tick.label1.set_fontsize(8)
        self._histogram_plot = figure
        return self._histogram_plot

    def scale_to(self,data,scale_min,scale_max):
        data = data.copy()
        # Set min to scale_min
        data = data - (data.min() - scale_min)
        # Set max to 255
        return data * (scale_max / data.max())

    def get_rgba_array(self):
        red = self.scale_to(self._data,0.0,255.0)
        green = red.copy()
        blue = red.copy()
        alpha = self._alpha
        if self._color_out_of_range:
            hist = self._history.add("Will color values out of range.")
            if self._above_range_data is not None or self._below_range_data is not None:
                if self._above_range_data is not None:
                    indexes = (self._above_range_data > 0)
                    hist.add("Set '%s' pixels above range to red." %(int(indexes.sum())))
                    above = 1 - self.scale_to(self._above_range_data,0.0,1.0)
                    red[indexes] = 255
                    green[indexes] = green[indexes] * above[indexes]
                    blue[indexes] = blue[indexes] * above[indexes]
                if self._below_range_data is not None:
                    indexes = (self._below_range_data > 0)
                    hist.add("Set '%s' pixels below range to red." %(int(indexes.sum())))
                    below = 1 - self.scale_to(self._below_range_data,0.0,1.0)
                    blue[indexes] = 255
                    green[indexes] = green[indexes] * below[indexes]
                    red[indexes] = red[indexes] * below[indexes]
            else:
                hist.add("No values out of range, therefore none colored.")
        rgba = numpy.empty((red.shape[0],red.shape[1],4), dtype='uint8')
        for x_idx in range(red.shape[0]):
            for y_idx in range(red.shape[1]):
                rgba[x_idx,y_idx] = [red[x_idx,y_idx], green[x_idx,y_idx], blue[x_idx,y_idx], alpha[x_idx,y_idx]]
        self._red   = red.astype('uint8')
        self._blue  = blue.astype('uint8')
        self._green = green.astype('uint8')
        self._history.add("Built RGBA image data.")
        return rgba

    def ignore_zero_mins(self,value=True):
        if self._ignore_zero_mins == value:
            self._history.add("Note: Ignoring request to maintain status-quo reguarding ignoring zero minima.")
            return self
        self._set_attr('_ignore_zero_mins',value,bool)
        if not value:
            self._history.add("Note: Will not ignore current zero minima.")
            return self
        data_min = self._masked_data.min()
        if data_min != 0:
            self._history.add("Note: Minimum value for data is not zero. Will not ignore.")
            return self
        next_min = self._masked_data[self._masked_data > 0].min()
        if next_min == 1:
            self._history.add("Note: Minimum value for data is zero, but next minimum is 1. Will not ignore.")
            return self
        to_change = (self._data < next_min)
        to_change_masked = (self._masked_data < next_min)
        self._history.add("Ignoring zero minima by setting %s pixels to next-lowest value '%s'."
                                %(int(to_change.sum()),next_min)
                                )
        self._data[to_change] = next_min
        self._masked_data[to_change_masked] = next_min
        self._rebuild_files()
        return self

    def color_out_of_range(self,bool_val=True):
        self._history.add("Set color_out_of_range = '%s' (was '%s')" %(bool_val, self._color_out_of_range), frame=0)
        self._color_out_of_range = bool_val
        return self

    def set_transparent(self,value=True):
        self._history.add("Set transparent = '%s')" %(value))
        self._set_attr('_transparent',value,bool)
        return self

    def get_transparent(self):
        return self._transparent

    # Adapted from:
    # http://www.janeriksolem.net/2009/06/histogram-equalization-with-python-and.html
    def equalize(self):
        hist = self._history.add("Equalizing image histogram.")
        if self._equalize:
            hist.add("WARNING: Attempt to re-equalize data will likely only degrade image quality.")
        self._equalize = True
        # get image histogram
        image_histogram, bins = numpy.histogram(self._data.flatten(),256,normed=True)
        cdf = image_histogram.cumsum() #cumulative distribution function
        cdf = 255.0 * cdf / cdf[-1] #normalize
        # use linear interpolation of cdf to find new pixel values
        interpolated_data = numpy.interp(self._data.flatten(),bins[:-1],cdf)
        self._data = interpolated_data.reshape(self._data.shape)
        self._rebuild_masked_data()
        self._rebuild_files()
        self._cdf = cdf
        return self

    def fill_histogram(self):
        hist = self._history.add("Filling histogram.")
        if self._fill_histogram:
            hist.add("WARNING: Attempt to re-fill histogram data will likely only degrade image quality.")
        self._fill_histogram = True
        tmp_data = numpy.sort(self._masked_data.flatten())
        length = tmp_data.size
        value_map = {}
        if tmp_data.min() == 0:
            leading_zeros = int((tmp_data == 0).sum())
            value_map[0.0] = 0
        else:
            leading_zeros = 0
        non_zero_length = length - leading_zeros

        bin_size = math.floor( (non_zero_length) / 255.0 )

        intensity = 0
        last_value = None
        unique_value_count = 0
        for idx in range(leading_zeros, length):
            this_value = tmp_data[idx]
            if (idx - leading_zeros) % bin_size == 0:
                intensity += 1
            if this_value == last_value:
                continue
            unique_value_count += 1
            last_value = this_value
            value_map[last_value] = intensity
        flat_data = self._data.flat
        for idx in range(self._data.size):
            flat_data[idx] = value_map[flat_data[idx]]
        self._rebuild_masked_data()
        self._rebuild_files()
        return self

    def save(self):
        filename = self.get_output_filename_root() + '.png'
        # print "self.get_filename()='%s'" %(self.get_filename())
        # print "self.get_output_filename_root()='%s'" %(self.get_output_filename_root())
        if self.get_filename() != filename:
            self._rebuild_files()
        self.set_filename(filename)
        # print "self.get_filename()='%s'" %(self.get_filename())

        # Rotate CCL 90 degrees so it's not sideways
        img = Image.fromarray(self.get_rgba_array()).rotate(-90)
        self._capture_file_save(filename)
        img.save(filename)
        return self

    def save_all(self,suffix=None):
        if suffix is not None:
            self.set_suffix(suffix)
        self.save()
        self.save_histogram()
        self.save_html()

    def set_max_width(self,max_width):
        self._set_attr('_max_width',value,int)
        self.reset_all()
        return self

    def get_max_width(self): return self._max_width

    def set_color_out_of_range(self,value):
        return self._set_attr('_color_out_of_range',value,bool)

class NeuroImage(NeuroImageFileBase):
    def __init__(self,
                 filename_or_nibabel_nifti,
                 parent=None,
                 title=None,
                 description=None,
                 nimg=None,
                 skip=0,
                 data=None,
                 output_dir=None,
                 dirname=''
                 ):
        self._nimg = None
        self._nimg_extension = None
        self._raw_data = None
        self._skip = skip
        self._t = None
        self._x = None
        self._y = None
        self._z = None
        self._needs_saving = False
        self._mosaic_image = None
        self.clear_mask()

        NeuroImageFileBase.__init__(
            self,
            parent=parent,
            title=title,
            description=description,
            can_be_in_img_tag=False,
            output_dir=output_dir,
            dirname=dirname
            )

        if filename_or_nibabel_nifti is None:
            raise ValueError("filename_or_nibabel_nifti may not be 'None'")
        if isinstance(filename_or_nibabel_nifti,str):
            # print "NeuroImage: self.set_filename('%s')" %(filename_or_nibabel_nifti)
            self.set_filename(filename_or_nibabel_nifti)
        elif isinstance(filename_or_nibabel_nifti,nibabel.nifti1.Nifti1Image):
            self.set_image(filename_or_nibabel_nifti)
            self.set_filename(filename_or_nibabel_nifti.get_filename())
        else:
            raise ValueError("filename_or_nibabel_nifti must be a string filename or a nibabel.nifti1.Nifti1Image")

        # print "NeuroImage: self.get_filename()='%s'" %(self.get_filename())
        return None

    def clear_mask(self):
        self._array_masks = {}
        self._derived_images = {}
        self._mask_lower = None
        self._mask_upper = None
        self._mask_nans = True
        self._mask_infs = True
        self._masked_data = None
        self._masked_derived_volumes = {}
        self._slice_intensity_means = {}
        self._unmasked_derived_volumes = {}
        return self

    def _set_mask_param(self,key,value):
        # Only set if different.
        if self._mask_params[key] != value:
            print(("Setting mask parameter '%s' to '%s'" %(key,value)))
            self.clear_mask()
            self._mask_params[key] = value
        else:
            print(("Not Setting mask parameter '%s' to '%s'" %(key,value)))
        # Do this regardless, just in case a derived image was generated
        # before any mask was set.
        for img_key in self._derived_images:
            self._get_derived_image(img_key)._set_mask_param(key,value)
        return self

    def set_mask_lower(self,value): return self._set_attr_float('_mask_lower',value)
    def get_mask_lower(self): return self._mask_lower

    def set_mask_upper(self,value): return self._set_attr_float('_mask_upper',value)
    def get_mask_upper(self): return self._mask_upper

    def set_mask_nans(self,value): return self._set_attr('_mask_nans',value,bool)
    def get_mask_nans(self): return self._mask_nans

    def set_mask_infs(self,value): return self._set_attr('_mask_infs',value,bool)
    def get_mask_infs(self): return self._mask_infs

    def get_mosaic(self,
                   volume_idx = None,
                   suffix = '_thumbnail',
                   basename = None,
                   dirname = None,
                   max_width = None,
                   force_new = False,
                   output_dir = None,
                   transparent = True,
                   ):
        if self._mosaic_image is None or force_new:
            self._mosaic_image = TwoDimNeuroImage(
                parent=self,
                volume_idx=volume_idx,
                suffix=suffix,
                basename=basename,
                dirname=dirname,
                max_width=max_width,
                output_dir=self.get_output_dir(),
                transparent=transparent,
                )

        return self._mosaic_image

    def get_mean_image(self):
        if 'mean' not in self._derived_images:
            # print "[Calculate] Mean Volume for '%s'" %(self.get_filename())
            print("[Calculate] Mean Volume")
            if(1 == self._t):
                print("WARNING: Calculating mean image of one volume, maybe you meant to use a 4D image in stead of a 3D one?")
            mean_data = numpy.mean(self.get_data(),axis=3)
            self.newDerivedImage("Mean Volume",'mean',mean_data,"_mean")
        return self._derived_images['mean']

    def get_mask_image(self):
        if 'mask' not in self._derived_images:
            self.generate_masks()
        return self._derived_images['mask']

    def get_stdev_image(self):
        if 'stdev' not in self._derived_images:
            # print "[Calculate] StDev Volume for '%s'" %(self.get_filename())
            print("[Calculate] StDev Volume")
            if(1 == self._t):
                print("WARNING: Calculating StDev image of one volume, maybe you meant to use a 4D image in stead of a 3D one?")
            stdev_data = numpy.std(self.get_data(),axis=3,ddof=1)
            self.newDerivedImage("StDev Volume",'stdev',stdev_data,"_stdev")
        return self._derived_images['stdev']

    def get_snr_image(self):
        if 'snr' not in self._derived_images:
            # print "[Calculate] SNR Volume for '%s'" %(self.get_filename())
            print("[Calculate] SNR Volume")
            if(1 == self._t):
                print("WARNING: Calculating SNR image of one volume, maybe you meant to use a 4D image in stead of a 3D one?")
            snr_data = self.get_mean_image().get_data() / self.get_stdev_image().get_data()
            snr_data[numpy.isnan(snr_data)|numpy.isinf(snr_data)] = 0
            self.newDerivedImage("SNR Volume",'snr',snr_data,"_snr")
        return self._derived_images['snr']

    def get_slope_image(self):
        if 'slope' not in self._derived_images:
            # print "[Calculate] Slope Volume for '%s'" %(self.get_filename())
            print("[Calculate] Slope Volume")
            from scipy import stats
            if(1 == self._t):
                print("WARNING: Calculating Slope image of one volume, maybe you meant to use a 4D image in stead of a 3D one?")
            raw_data = self.get_data()
            shape = raw_data.shape
            slope_data = numpy.zeros([shape[0],shape[1],shape[2]])
            x_array = list(range(shape[3]))
            for x_idx in range(shape[0]):
                for y_idx in range(shape[1]):
                    for z_idx in range(shape[2]):
                        slope, intercept, r_value, p_value, std_err = stats.linregress(x_array,raw_data[x_idx,y_idx,z_idx,:])
                        slope_data[x_idx,y_idx,z_idx] = slope
            self.newDerivedImage("Slope Volume",'slope',slope_data,"_slope")
        return self._derived_images['slope']

    def generate_masks(self, key = '3d', extended_name = False):
        # Only generate / regenerate masks if needed
        if '3d' not in self._array_masks:
            # print "[Calculate] Mask Volume for '%s'" %(self.get_filename())
            print("[Calculate] Mask Volume")
            # Get the raw data.
            raw_data = self.get_data()
            is_4d = len(raw_data.shape) > 3
            # For 4D volumes (note larger dims may or may not work for some methods)
            # use the mean 3D volume
            if is_4d:
                mean_image = self.get_mean_image()
                raw_data = mean_image.get_data()
            hist = self._history.add("Generating Mask Volume for %s" % self.get_filename())
            numpy_3d_mask = numpy.zeros(raw_data.shape, dtype=bool)
            calculated_extension = "_mask"
            extension = "_mask"
            total_mask_count = 0;
            self._mask_total_count = 0
            self._mask_lower_count = 0
            print("+------------------+---------+------------+----------+------------+------------+")
            print("| Mask Variable    | Value   | Num Voxels | % Voxels | Cumulative | Cumulative |")
            print("|                  |         | Masked     | Masked   | Vox Maskd  | % Masked   |")
            print("+------------------+---------+------------+----------+------------+------------+")
            format = "| %-16s | %7s | %10s | %8s | %10s | %10s |"
            if self.get_mask_lower() is not None:
                to_mask = (raw_data <= self.get_mask_lower())
                self._mask_lower_count = int(to_mask.sum())
                self._mask_total_count += self._mask_lower_count
                numpy_3d_mask = numpy_3d_mask | to_mask
                hist.add("Masked %d of %d voxels below %s" %(to_mask.sum(),raw_data.size,self.get_mask_lower()))
                calculated_extension += "_min_%0.3f" % self.get_mask_lower()
            print(format %(
                'Lower Threshold',
                self.get_mask_lower(),
                self._mask_lower_count,
                "%0.4f%%" %(100.0*self._mask_lower_count/raw_data.size),
                self._mask_total_count,
                "%0.4f%%" %(100.0*self._mask_total_count/raw_data.size)
                ))
            self._mask_upper_count = 0
            if self.get_mask_upper() is not None:
                to_mask = (raw_data > self.get_mask_upper())
                self._mask_upper_count = int(to_mask.sum())
                self._mask_total_count += self._mask_upper_count
                numpy_3d_mask = numpy_3d_mask | to_mask
                hist.add("Masked %d of %d voxels above %s" %(to_mask.sum(),raw_data.size,self.get_mask_upper()))
                calculated_extension += "_max_%0.3f" % self.get_mask_upper()
            print(format %(
                'Upper Threshold',
                self.get_mask_upper(),
                self._mask_upper_count,
                "%0.4f%%" %(100.0*self._mask_upper_count/raw_data.size),
                self._mask_total_count,
                "%0.4f%%" %(100.0*self._mask_total_count/raw_data.size)
                ))
            self._mask_nan_count = 0
            if self.get_mask_nans():
                to_mask = (numpy.isnan(raw_data))
                self._mask_nan_count = to_mask.sum()
                self._mask_total_count += self._mask_nan_count
                numpy_3d_mask[to_mask] = True
                hist.add("Masked %d of %d voxels with NaN values" %(to_mask.sum(),raw_data.size))
                calculated_extension += "_nan"
            print(format %(
                'Mask NaNs',
                self.get_mask_nans(),
                self._mask_nan_count,
                "%0.4f%%" %(100.0*self._mask_nan_count/raw_data.size),
                self._mask_total_count,
                "%0.4f%%" %(100.0*self._mask_total_count/raw_data.size)
                ))
            if self.get_mask_infs():
                to_mask = (numpy.isinf(raw_data))
                self._mask_inf_count = to_mask.sum()
                self._mask_total_count += self._mask_inf_count
                numpy_3d_mask[to_mask] = True
                hist.add("Masked %d of %d voxels with Inf values" %(to_mask.sum(),raw_data.size))
                calculated_extension += "_inf"
            print(format %(
                'Mask Infs',
                self.get_mask_infs(),
                self._mask_inf_count,
                "%0.4f%%" %(100.0*self._mask_inf_count/raw_data.size),
                self._mask_total_count,
                "%0.4f%%" %(100.0*self._mask_total_count/raw_data.size)
                ))
            print("+------------------+---------+------------+----------+------------+------------+")
            if extended_name:
                extension = calculated_extension

            # NumPy array masks are the complement of what is normally used in neuroimaging.
            # In other words, in neuroimaging, 1 means "keep this value" and 0 means "mask it"
            # since you can multiply an image by its mask to get only values of interest which
            # are non-zero (risky if "0" is a valid un-masked value). In NumPy arrays, "1" is
            # "True" meaning mask this value, and "0" is "False" meaning don't, which is the
            # opposite, so when we save the neuroimage mask, it should be the complement of
            # the NumPy array mask and vice-versa
            mask_count = int(numpy_3d_mask.sum())
            # print " - Masked voxels: %10s of %10s (%10s%%)" %(mask_count,raw_data.size,"%0.6f"%(100.0*mask_count/raw_data.size))
            neuro_3d_mask = ~numpy_3d_mask
            self.newDerivedImage("Volume Mask",'mask',neuro_3d_mask,extension, dtype='uint8')
            self.newDerivedImage("Volume Numpy Masked Array Mask", '3d_mask',numpy_3d_mask,extension + "_numpy_3d_array", dtype='uint8')
            # If this is a 4D + image, generate the 4D mask as well.
            if is_4d:
                numpy_4d_mask = numpy.zeros(self.get_data().shape, dtype=bool)
                numpy_4d_mask[numpy_3d_mask] = 1
                self.newDerivedImage("4D Numpy Masked Array Mask",'4d_mask',numpy_4d_mask,extension + "_numpy_4d_array", dtype='uint8')
                self._array_masks['4d'] = numpy_4d_mask
                self._masked_data = numpy.ma.masked_array(self.get_data(),mask=numpy_4d_mask)
            else:
                self._masked_data = numpy.ma.masked_array(self.get_data(),mask=neuro_3d_mask)
            self._array_masks['3d'] = neuro_3d_mask
        return self._array_masks[key]

    def newDerivedImage(self,title,key,data,add_to_filename,dtype=None):
        filename = self.get_output_filename_root() + add_to_filename + self.get_extension()
        description = title+" derived from '"+str(self.get_filename())+"'"
        self._history.add("Calculated %s" % description)
        header = self.get_image().header.copy()
        nim = nibabel.Nifti1Image(data, numpy.eye(4), header)
        nim.set_filename(filename)
        if dtype is not None:
            nim.set_data_dtype(dtype)
        nim.update_header()
        new_img = NeuroImage(
            nim,
            parent=self,
            title=title,
            description=description,
            )
        new_img._parent = self
        #self.add_child(new_img)
        self._derived_images[key] = new_img
        return new_img

    def get_nifti_filename_root(self,filename):
        nimg_extension = '.nii'
        # Get the filename extension
        (basename,extension) = os.path.splitext(filename)
        extension = str.lower(extension)
        if(".gz" == extension):
            # If the first extension is ".gz", then try and get the next
            # extension
            (basename,extension) = os.path.splitext(basename)
            extension = str.lower(extension)
            # Regardless of what the next extensions is, we assume the
            # user wants compressed NiFTI-1 files unless otherwise
            # previously specified
            if self.get_extension() is None:
                nimg_extension = '.nii.gz'
            if(".nii" == extension):
                # If the next extension is .nii, all is good, basename is
                # the root
                filename_root = basename
                extension = '.nii.gz'
            else:
                # Otherwise, this is not a normal NiFTI-1 file. Keep the
                # whole filename as the root.
                filename_root = filename
        else:
            # Regardless of what the first extensions is, we assume the
            # user wants uncompressed NiFTI-1 files unless otherwise
            # previously specified
            if self.get_extension() is None:
                nimg_extension = '.nii'
            if(".nii" == extension):
                # If the first extension is .nii, all is good, basename is
                # the root
                filename_root = basename
            else:
                # Otherwise, this is not a normal NiFTI-1 file. Keep the
                # whole filename as the root.
                filename_root = filename
        if filename == filename_root:
            print(("WARNING: '%s' does not follow NiFTI-1 naming convensions. Output names may be unpredictable."
                   %(filename)))
        return filename_root, extension, nimg_extension

    def set_image(self,nimg):
        previous = self._nimg
        self._x = nimg.shape[0]
        self._y = nimg.shape[1]
        self._z = nimg.shape[2]
        if len(nimg.shape) > 3:
            self._t = nimg.shape[3]
        else:
            self._t = 1
        if(len(nimg.shape) > 4):
            self._nimg = None
            raise ValueError("ERROR: Cannot operate on NiFTI-1 images with more than 4 dimensions.")
        self._nimg = nimg
        nimg.set_data_dtype(numpy.float64)
        return previous

    def get_image(self):
        if self._nimg is None:
            if self.get_filename() == '':
                raise Exception('ERROR: Cannot get Nifti1Image object without filename')
            self.set_image(nibabel.load(self.get_filename()))
            if self._skip:
                self._raw_data = self._nimg.get_data()[:,:,:,self._skip:]
            else:
                self._raw_data = self._nimg.get_data()
        return self._nimg

    def get_number_of_slices(self):
        if self._nimg is None:
            raise Exception("ERROR: Cannot get number of slices in '%s'" %(self.get_filename()))
        return self._z

    def get_number_of_volumes(self):
        if self._nimg is None:
            raise Exception("ERROR: Cannot get number of volumes in '%s'" %(self.get_filename()))
        return self._t

    def get_data(self):
        if self._raw_data is None:
            if self._nimg is None:
                self.get_image()
            else:
                self._raw_data = self._nimg.get_data()
        return self._raw_data

    def get_masked_data(self):
        if self._masked_data is None:
            self.generate_masks()
        return self._masked_data

    def print_image_summary(self):
        slice_size = self._x * self._y
        volume_size = self._x * self._y * self._z
        number_of_slices = self._z
        number_of_frames = self._t * self._u * self._v * self._w
        middle_frame = int(number_of_frames / 2)
        print((
            "X: %4s,     Y: %4s,     Z: %4s,     T: %4s,     U: %4s,     V: %4s,     W: %4s"
            % (self._x, self._y, self._z, self._t, self._u, self._v, self._w)
            ))
        print("Sice Size ( %4s x %4s ):     %10s voxels" % (self._x, self._y, slice_size))
        print("Number of Sices:               %10s" % (number_of_slices))
        print("Number of Frames (Time Points) %10s" % (number_of_frames))
        print("Filename:                      %s" % (self.get_filename()))
        return self

    def save(self,nim=None):
        if nim is None:
            nim = self.get_image()
        self._capture_file_save(self.get_filename())
        nim.to_filename(nim.get_filename())
        return self

    def _png_data_stats(self,data):
        print(" - PNG data stats: min=%s,max=%s,mean=%s,stdev=%s" %(
            numpy.amin(data),
            numpy.amax(data),
            data.mean(),
            data.std() ))

    def _print_diff_line(self,preface,title,value_a,value_b,value_diff,value_percent_diff):
        print("%s %-20s %10s %10s %10s %10s" % (preface,title,value_a,value_b,value_diff,value_percent_diff))

    def _print_diff(self, title, value_a, value_b):
        if value_a == value_b:
            preface = " "
            value_diff = ""
            value_percent_diff = ""
        else:
            preface = ">"
            value_diff = value_a - value_b
            value_percent_diff = value_diff / value_a
            if value_a < value_b:
                value_percent_diff = value_diff / value_b
            value_percent_diff = "%0.4f%%" % (100.0 * value_percent_diff)
        self._print_diff_line(preface,title,value_a,value_b,value_diff,value_percent_diff)

    def diff_data(self, data_a, data_b):
        # Get the difference between values
        data_diff = data_a - data_b
        # Get the absolute difference of the values
        abs_diff = numpy.ones(data_diff.shape,dtype='int8')
        abs_diff[data_diff < 0] = -1
        abs_diff = data_diff * abs_diff
        # Count the number of points that are different
        diff_count = numpy.zeroes(data_diff.shape,dtype='int8')
        diff_count[data_diff != 0] = 1
        diff_count = diff_count.sum()
        self._print_diff("Maxima:",data_a.max(),data_b.max())
        self._print_diff("Minima:",data_a.min(),data_b.min())
        self._print_diff("Means:",data_a.mean(),data_b.mean())
        self._print_diff("StDev:",data_a.sd(),data_b.sd())

    def _slice_report_row_(self,row):
        return ( "%-10s %10s %10s %10s %10s %10s %10s %10s" % row )

    def _slice_report_row(self,slice_idx,voxel_count,mean,stdev,snr,min,max,outliers):
        if isinstance(slice_idx, str):
            pass
        else:
            slice_idx = "%03d" % (slice_idx+1)
        return self._slice_report_row_((slice_idx,
                                        voxel_count,
                                        "%0.2f"%mean,
                                        "%0.2f"%stdev,
                                        "%0.2f"%snr,
                                        "%0.2f"%min,
                                        "%0.2f"%max,
                                        outliers
                                        ))

    def _slice_report_header(self,title,desc,data,extended=False):
        header = ""
        if extended:
            header += "--------------------------------------------------------------------------------\n"
            header += title + "\n"
            header += "--------------------------------------------------------------------------------\n"
            header += desc + "\n"
            header += "DATA Dimensions: %s\n" %(data.shape)
            header += "Min: %s, Max: %s, Mean %s, StDev %s\n" %(data.min(),data.max(),data.mean(),data.std())
            header += "\n"
            self._print_slice_report_row_(("Slice","Num Voxels","Mean","StDev","SNR","Min","Max","Outliers"))
        else:
            self._print_slice_report_row_(("slice","voxels","mean","stdev","snr","min","max","#out"))

    def get_mean_slice_intensities(self,apply_mask=False,lower_threshold_to_zero=None):
        key = "%s:%s" %(apply_mask,lower_threshold_to_zero)
        if key in self._slice_intensity_means:
            return self._slice_intensity_means[key]

        if apply_mask:
            data = self.get_masked_data().copy()
            mask = numpy.ma.getmask(data)
        else:
            data = self.get_data().copy()

        if lower_threshold_to_zero is not None:
            data[data <= lower_threshold_to_zero] = 0

        dim_x = data.shape[0]
        dim_y = data.shape[1]
        dim_z = data.shape[2]
        dim_t = data.shape[3]

        slice_intensity_means = numpy.zeros( (dim_z,dim_t) )
        slice_voxel_counts = numpy.zeros( (dim_z), dtype='uint32' )
        slice_size = dim_x * dim_y

        if apply_mask:
            for slice_idx in range(dim_z):
                slice_voxel_counts[slice_idx] = slice_size - mask[:,:,slice_idx,0].sum()
        else:
            for slice_idx in range(dim_z):
                slice_voxel_counts[slice_idx] = slice_size

        for volume_idx in range(dim_t):
            for slice_idx in range(dim_z):
                slice_data = data[:,:,slice_idx,volume_idx]
                slice_intensity_means[slice_idx,volume_idx] = slice_data.mean()

        self._slice_intensity_means[key] = [slice_intensity_means,slice_voxel_counts,data]
        return self._slice_intensity_means[key]

    def _entropy(self,data,bins=4096):
        min_val = data.min()
        max_val = data.max()
        val_range = max_val - min_val
        if val_range < bins:
            bins = val_range
        p_vals=numpy.histogram(data,range=(min_val,max_val),bins=bins,density=True)
        return (p_vals * numpy.log2(p_vals)).sum()

    def get_unmasked_entropy(self):
        if '_unmasked_entropy' not in self:
            self._unmasked_entropy = self._entropy(self.get_data())
        return self._unmasked_entropy

    def get_masked_entropy(self):
        if '_masked_entropy' not in self:
            self._masked_entropy = self._entropy(self.get_masked_data())
        return self._masked_entropy

    def get_stackcheck_mean_slice_text(self,apply_mask=True,lower_threshold_to_zero=None):
        (slice_intensity_means, slice_voxel_counts, data) = self.get_mean_slice_intensities(apply_mask,lower_threshold_to_zero)
        text = ""
        for slice_idx in range(slice_intensity_means.shape[0]):
            text += "%d\t" %(slice_idx + 1)
            for volume_idx in range(slice_intensity_means.shape[1]):
                if(volume_idx > 0):
                    text += "\t"
                text += "%4.2f" %(slice_intensity_means[slice_idx][volume_idx])
            text += "\n"
        return text

    def save_stackcheck_mean_slice_text(self,filename=None,apply_mask=True,lower_threshold_to_zero=None):
        if filename is None:
            filename = self.get_output_filename_root() + "_mean_slice.txt"
        text = self.get_stackcheck_mean_slice_text(apply_mask,lower_threshold_to_zero)
        self._capture_file_save(filename,'mean slice data text file')
        fh = open(filename,"w")
        fh.write(text)
        fh.close()
        return self

    def get_stackcheck_mean_slice_csv(self,apply_mask=True,lower_threshold_to_zero=None):
        (slice_intensity_means, slice_voxel_counts, data) = self.get_mean_slice_intensities(apply_mask,lower_threshold_to_zero)
        csv = ""
        for slice_idx in range(slice_intensity_means.shape[0]):
            csv += "%d," %(slice_idx + 1)
            for volume_idx in range(slice_intensity_means.shape[1]):
                if(volume_idx > 0):
                    csv += ","
                csv += "%s" %(slice_intensity_means[slice_idx][volume_idx])
            csv += "\n"
        return csv

    def save_stackcheck_mean_slice_csv(self,filename=None,apply_mask=True,lower_threshold_to_zero=None):
        if filename is None:
            filename = self.get_output_filename_root() + "_mean_slice.csv"
        csv = self.get_stackcheck_mean_slice_csv(apply_mask,lower_threshold_to_zero)
        self._capture_file_save(filename,'mean slice data CSV file')
        fh = open(filename,"w")
        fh.write(csv)
        fh.close()
        return self

    def save_stackcheck_mean_slice_plot(self,
                                        filename=None,
                                        apply_mask=True,
                                        lower_threshold_to_zero=None,
                                        format='svg',
                                        transparent=True,
                                        autoscale=True,):
        if filename is None:
            filename = self.get_output_filename_root() + "_mean_slice." + format
        (slice_intensity_means, slice_voxel_counts, data) = self.get_mean_slice_intensities(apply_mask,lower_threshold_to_zero)
        self._capture_file_save(filename,'mean slice intensity plot')

        plt.plot(slice_intensity_means[:,0:].transpose(), antialiased=True, linewidth=0.5)
        plt.autoscale(tight=True)
        plt.grid(True, color='#CCCCCC', linewidth=1)
        plt.title("Mean Slice Intensity", size=12)
        plt.ylabel("Signal Intensity", size=10)
        plt.xlabel("Volumes / Time Points (N)", size=10)
        plt.setp(list(plt.axes().spines.values()), color='#AAAAAA')
        plt.tick_params(axis='both', which='major', color="#AAAAAA", labelsize=8)
        plt.savefig(filename, format=format, transparent=False, bbox_inches='tight')

        '''
        ## --- customize plot
        figure = Figure()
        canvas = FigureCanvas(figure)
        axis = figure.add_subplot(111)
        axis.set_title("Mean Slice Intensity",fontsize=12)
        axis.plot(numpy.rot90(slice_intensity_means[:,1:]-1), antialiased=True, linewidth=0.5)
        axis.set_xlabel("Volumes / Time Points (N)",fontsize=10)
        axis.set_ylabel("Signal Intensity",fontsize=10)
        axis.set_xlim(0,slice_intensity_means.shape[1] - 1)

        ## --- get min and max, ignoring NaNs
        slice_intensity_means_min=numpy.nanmin(slice_intensity_means)
        slice_intensity_means_max=numpy.nanmax(slice_intensity_means)

        if autoscale:
            axis.set_ylim(slice_intensity_means_min,slice_intensity_means_max)
        else:
            if slice_intensity_means_max > 1000:
                ax_max = slice_intensity_means_max
            else:
                ax_max = 1000
            if slice_intensity_means_min < 100:
                ax_min = slice_intensity_means_min
            else:
                ax_min = 100
            axis.set_ylim(ax_min,ax_max)
        axis.grid(True,color='#CCCCCC',linewidth=1)
        for spine in axis.spines.values():
            spine.set_color('#AAAAAA')
        for tick in axis.xaxis.get_major_ticks() + axis.yaxis.get_major_ticks():
            tick.tick1line.set_mec('#AAAAAA')
            tick.tick2line.set_mec('#AAAAAA')
            tick.label1.set_fontsize(8)
        figure.savefig(filename,format=format,transparent=transparent,bbox_inches='tight')
        '''
        return self

    def get_stackcheck_report_text(self,apply_mask=True,lower_threshold_to_zero=None,extended=False):
        my_path = os.path.abspath(__file__)
        (full_root,foo,bar) = self.get_nifti_filename_root(os.path.abspath(self.get_filename()))
        my_name = os.path.basename(my_path)
        my_checksum = hashlib.sha256(open(my_path).read().encode('utf-8')).hexdigest()

        (slice_intensity_means, slice_voxel_counts, data) = self.get_mean_slice_intensities(apply_mask,lower_threshold_to_zero)

        dim_x = data.shape[0]
        dim_y = data.shape[1]
        dim_z = data.shape[2]
        dim_t = data.shape[3]
        orig_t = dim_t + self._skip

        report  = "%s (checksum: '%s')\n" % (my_name, my_checksum)
        report += "Input %s root: \"%s\"\n" %(self.get_extension(),full_root)
        report += "z = %s, x = %s, y = %s images per slice = %s\n" % (dim_z, dim_x, dim_y, orig_t)
        report += "\n"
        report += "Timepoints = %s skip = %s count = %s\n" %(orig_t,self._skip,dim_t)
        report += "\n"
        report += "Threshold value for mask: %0.2f\n" %(self.get_mask_lower())
        report += "\n"

        if extended:
            report += "DATA Dimensions: %s\n" %(str(data.shape))
            report += "General Statistics:\n"
            data_min = data.min()
            data_max = data.max()
            data_mean = data.mean()
            data_stdev = data.std()
            data_snr = data_mean / data_stdev
            report += "  Raw Data:    Min: %8s, Max: %8s, Mean %8s, StDev %8s, SNR %8s\n" %(
                "%0.2f" % data_min,
                "%0.2f" % data_max,
                "%0.2f" % data_mean,
                "%0.2f" % data_stdev,
                "%0.2f" % data_snr,
                )
            masked_data = numpy.ma.array(self.get_data().copy(),mask=self._array_masks['4d']).flatten().compressed()
            # masked_data = self.get_masked_data()
            data_min = masked_data.min()
            data_max = masked_data.max()
            data_mean = masked_data.mean()
            data_stdev = masked_data.std()
            data_snr = data_mean / data_stdev
            report += "  Masked Data: Min: %8s, Max: %8s, Mean %8s, StDev %8s, SNR %8s\n" %(
                "%0.2f" % numpy.ma.min(masked_data),
                "%0.2f" % data_max,
                "%0.2f" % data_mean,
                "%0.2f" % data_stdev,
                "%0.2f" % data_snr,
                )
            report += "\n"
            vol_size = data.shape[0] * data.shape[1] * data.shape[2]
            img_size = vol_size * data.shape[3]
            unmasked_4d = int(self._array_masks['4d'].sum())
            unmasked_3d = int(self._array_masks['3d'].sum())
            report += "Number of Voxels Masked:\n"
            report += "  Whole 4D Volume: %10s / %10s (%8s)\n" %(
                img_size - unmasked_4d,
                img_size,
                "%0.3f%%" %(100.0*(img_size - unmasked_4d)/img_size),
)
            report += "  Per 3D Volume:   %10s / %10s (%8s)\n\n" %(
                vol_size - unmasked_3d,
                vol_size,
                "%0.3f%%" %(100.0*(vol_size - unmasked_3d)/vol_size),
                )
            report_data_format = "%8s %8s %8s %8s %8s %8s %8s %8s\n"
            report += report_data_format %('Slice','Voxels','Mean','StDev','SNR','Min','Max','Outliers')
        else:
            report_data_format = "%s       %s\t%s\t%s\t%s\t%s\t%s\t%s\n"
            report += "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" %('slice','voxels','mean','stdev','snr','min','max','#out')

        slice_count = slice_intensity_means.shape[0]
        volume_count = slice_intensity_means.shape[1]

        slice_weighted_mean_mean = 0
        slice_weighted_stdev_mean = 0
        slice_weighted_snr_mean = 0
        slice_weighted_max_mean = 0
        slice_weighted_min_mean = 0
        outlier_count = 0
        total_voxel_count = 0

        for slice_idx in range(slice_count):
            slice_data         = slice_intensity_means[slice_idx]
            slice_voxel_count  = slice_voxel_counts[slice_idx]
            slice_mean         = slice_data.mean()
            slice_stdev        = slice_data.std(ddof=1)
            slice_snr          = slice_mean / slice_stdev
            slice_min          = slice_data.min()
            slice_max          = slice_data.max()

            if numpy.isnan(slice_mean) or numpy.isinf(slice_mean):
                slice_mean=0

            if numpy.isnan(slice_stdev) or numpy.isinf(slice_stdev):
                slice_stdev=0

            if numpy.isnan(slice_snr) or numpy.isinf(slice_snr):
                slice_snr=0

            if numpy.isnan(slice_min) or numpy.isinf(slice_min):
                slice_min=0

            if numpy.isnan(slice_max) or numpy.isinf(slice_max):
                slice_max=0

            slice_outliers     = numpy.zeros(slice_data.shape,dtype='int8')
            slice_outliers[slice_data < (slice_mean - (slice_stdev * 2.5))] = 1
            slice_outliers[slice_data > (slice_mean + (slice_stdev * 2.5))] = 1
            slice_outliers     = slice_outliers.sum()

            slice_weighted_mean_mean   += (slice_mean * slice_voxel_count)
            slice_weighted_stdev_mean  += (slice_stdev * slice_voxel_count)
            slice_weighted_snr_mean    += (slice_snr * slice_voxel_count)
            slice_weighted_min_mean    += (slice_min * slice_voxel_count)
            slice_weighted_max_mean    += (slice_max * slice_voxel_count)
            outlier_count     += slice_outliers
            total_voxel_count += slice_voxel_count
            report += report_data_format %(
                "%03d" %(slice_idx + 1),
                "%d" % slice_voxel_count,
                "%0.2f" % slice_mean,
                "%0.2f" % slice_stdev,
                "%0.2f" % slice_snr,
                "%0.2f" % slice_min,
                "%0.2f" % slice_max,
                slice_outliers
                )
        report += "\n"
        if extended:
            report += report_data_format %(
                'VOXEL',
                total_voxel_count,
                "%0.2f" %(slice_weighted_mean_mean / total_voxel_count),
                "%0.2f" %(slice_weighted_stdev_mean / total_voxel_count),
                "%0.2f" %(slice_weighted_snr_mean / total_voxel_count),
                "%0.2f" %(slice_weighted_min_mean / total_voxel_count),
                "%0.2f" %(slice_weighted_max_mean / total_voxel_count),
                "%s/%s" %(outlier_count,slice_count * volume_count)
                )
        else:
            report += "VOXEL\t%d\t%s\t%s\t%s\t%s\t%s\t%s\n" %(
                total_voxel_count,
                "%4.2f" %(slice_weighted_mean_mean / total_voxel_count),
                "%4.2f" %(slice_weighted_stdev_mean / total_voxel_count),
                "%4.2f" %(slice_weighted_snr_mean / total_voxel_count),
                "%4.2f" %(slice_weighted_min_mean / total_voxel_count),
                "%4.2f" %(slice_weighted_max_mean / total_voxel_count),
                "%s/%s" %(outlier_count,slice_count * volume_count)
                )

        return report

    def save_stackcheck_report_text(self,filename=None,apply_mask=True,lower_threshold_to_zero=None,extended=False):
        if filename is None:
            filename = self.get_output_filename_root() + "_slice_report.txt"
        report_text = self.get_stackcheck_report_text(apply_mask,lower_threshold_to_zero,extended)
        self._capture_file_save(filename,'mean slice report text')
        fh = open(filename,"w")
        fh.write(report_text)
        fh.close()
        return self

    def get_stackcheck_report_html(self,apply_mask=True,lower_threshold_to_zero=None,extended=False):
        my_path = os.path.abspath(__file__)
        (full_root,foo,bar) = self.get_nifti_filename_root(os.path.abspath(self.get_filename()))
        my_name = os.path.basename(my_path)
        my_checksum = hashlib.sha256(open(my_path).read().encode('utf-8')).hexdigest()

        (slice_intensity_means, slice_voxel_counts, data) = self.get_mean_slice_intensities(apply_mask,lower_threshold_to_zero)

        dim_x = data.shape[0]
        dim_y = data.shape[1]
        dim_z = data.shape[2]
        dim_t = data.shape[3]
        orig_t = dim_t + self._skip
        unmasked_data = self.get_data().copy()
        unmasked_mean = unmasked_data.mean()
        unmasked_stdev = unmasked_data.std()

        masked_data = self.get_masked_data().copy()
        masked_mean = masked_data.mean()
        masked_stdev = masked_data.std()
        mask = (~ (numpy.ma.getmask(masked_data)) )
        mdim_x = int(mask[:,0,0,0].sum())
        mdim_y = int(mask[0,:,0,0].sum())
        mdim_z = int(mask[0,0,:,0].sum())
        mdim_t = int(mask[0,0,0,:].sum())

        slice_count = slice_intensity_means.shape[0]
        volume_count = slice_intensity_means.shape[1]

        slice_voxel_sum = 0
        for slice_idx in range(slice_count):
            slice_voxel_sum  += slice_voxel_counts[slice_idx]

        mean_voxels_per_slice = slice_voxel_sum / float(slice_count)
        tot_v = int(mask.sum())

        report = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <title>'''+ self.get_basename() +''': Mean Slice Report</title>
'''+self._css+'''</head>
<body>
<h1>Mean Slice Report for '''+ self.get_basename() +'''</h1>
<table border="0" cellspacing="1" cellpadding="1">
<tr>
  <th>Generated by</th><td>'''+ my_name +'''</td>
</tr>
<tr>
  <th>Program SHA256 Checksum</th><td>'''+ my_checksum +'''</td>
</tr>
<tr>
  <th>Generated On</th><td>'''+ datetime.datetime.now().isoformat() +'''</td>
</tr>
<tr>
  <th>Input File</th><td>'''+ self.get_filename() +'''</td>
</tr>
</table>
<table border="0" cellspacing="1" cellpadding="1">
<thead>
<tr>
  <th colspan="4">Number of Time  Points (aka Volumes)</th>
  <th colspan="4">Mask Threshold &amp; Parameters</th>
</tr>
<tr>
  <th title="The total number of time points (aka &quoy;Volumes&quot;) in the original image before skipping any.">Original</th>
  <th title="Number of timepoints (aka &quoy;Volumes&quot;) skipped/ignored for this report.">Skipped</th>
  <th title="Number of timepoints (aka &quoy;Volumes&quot;) included in this report.">Included</th>
  <th title="Voxels whose mean value falls below this were masked.">Minimum</th>
  <th title="Voxels whose mean value falls above this were masked.">Maximum</th>
  <th title="Voxels whose value was &quot;NaN&quot; were ignored.">NaNs</th>
  <th title="Voxels whose value was &quot;Infinity&quot; were ignored.">Infs</th>
</tr>
</thead>
<tbody>
<tr>
  <td align="right" title="The total number of time points (aka &quoy;Volumes&quot;) in the original image before skipping any.">'''+ str(orig_t) +'''</td>
  <td title="Number of timepoints (aka &quoy;Volumes&quot;) skipped/ignored for this report." align="right">'''+ str(self._skip) +'''</td>
  <td title="Number of timepoints (aka &quoy;Volumes&quot;) included in this report." align="right">'''+ str(dim_t) +'''</td>
  <td title="Voxels whose mean value falls below this were masked." align="right">'''+ str(self.get_mask_lower()) +'''</td>
  <td title="Voxels whose mean value falls above this were masked." align="right">'''+ str(self.get_mask_upper()) +'''</td>
  <td title="Voxels whose value was &quot;NaN&quot; were ignored." align="right">'''+ str(self.get_mask_nans()) +'''</td>
  <td title="Voxels whose value was &quot;Infinity&quot; were ignored." align="right">'''+ str(self.get_mask_infs()) +'''</td>
</tr>
<tr>
</tbody>
</table>
<table border="0" cellspacing="1" cellpadding="1">
<thead>
<tr>
  <th title="Data Set">Data Set</th>
  <th title="Size of the 1st demention (X).">X</th>
  <th title="Size of the 2nd demention (Y).">Y</th>
  <th title="Size of the 3rd demention (Z). Also refered to as the &quot;Number of Slices&quot;">Z</th>
  <th title="Size of the 4th demention (Time). Also refered to as the &quot;Number of Volumes&quot;">T</th>
  <th title="Size of a &quot;Slice&quot; (i.e., X * Y) in Voxels">Slice Size</th>
  <th title="Total number of &quot;Slices&quot; in all dimensions (i.e., Z * T)">Total Slices</th>
  <th title="Total number of Voxels in the whole image (i.e., X * Y * Z * T)">Total Voxels</th>
  <th title="The Mean value of all voxels">Mean Voxel Value</th>
  <th title="The Standard Deviation of all voxels">StDev</th>
  <th title="The Signal to Noise ratio of all voxels (i.e., Mean/StDev)">SNR</th>
</tr>
</thead>
<tbody>
<tr>
  <td title="Data Set">Unmasked Image</td>
  <td title="Size of the 1st demention (X)." align="right">'''+ str(dim_x) +'''</td>
  <td title="Size of the 2nd demention (Y)." align="right">'''+ str(dim_y) +'''</td>
  <td title="Size of the 3rd demention (Z). Also refered to as the &quot;Number of Slices&quot;" align="right">'''+ str(dim_z) +'''</td>
  <td title="Size of the 4th demention (Time). Also refered to as the &quot;Number of Volumes&quot;" align="right">'''+ str(dim_t) +'''</td>
  <td title="Mean size of a &quot;Slice&quot; in Voxels" align="right">'''+ str(dim_x * dim_y) +'''</td>
  <td title="Total number of &quot;Slices&quot; in all dimensions (i.e., Z * T)" align="right">'''+ str(dim_z * dim_t) +'''</td>
  <td title="Total number of Voxels in the whole image (i.e., X * Y * Z * T)" align="right">'''+ str(dim_x * dim_y * dim_z * dim_t) +'''</td>
  <td title="The Mean value of all voxels" align="right">'''+ "%0.4f" % (unmasked_mean)+'''</td>
  <td title="The Standard Deviation of all voxels" align="right">'''+ "%0.4f" % (unmasked_stdev)+'''</td>
  <td title="The Signal to Noise ratio of all voxels (i.e., Mean/StDev)" align="right">'''+ "%0.4f" % (unmasked_mean / unmasked_stdev)+'''</td>
</tr>
<tr>
  <td title="Data Set">Masked Image</td>
  <td title="Size of the 1st demention (X)." align="right">N/A</td>
  <td title="Size of the 2nd demention (Y)." align="right">N/A</td>
  <td title="Size of the 3rd demention (Z). Also refered to as the &quot;Number of Slices&quot;" align="right">'''+ str(dim_z) +'''</td>
  <td title="Size of the 4th demention (Time). Also refered to as the &quot;Number of Volumes&quot;" align="right">'''+ str(dim_t) +'''</td>
  <td title="Size of a &quot;Slice&quot; (i.e., X * Y) in Voxels" align="right">'''+ "%0.4f" % (mean_voxels_per_slice) +'''</td>
  <td title="Total number of &quot;Slices&quot; in all dimensions (i.e., Z * T)" align="right">'''+ str(dim_z * dim_t) +'''</td>
  <td title="Total number of Voxels in the whole image (i.e., X * Y * Z * T)" align="right">'''+ str(tot_v) +'''</td>
  <td title="The Mean value of all voxels" align="right">'''+ "%0.4f" % (masked_mean)+'''</td>
  <td title="The Standard Deviation of all voxels" align="right">'''+ "%0.4f" % (masked_stdev)+'''</td>
  <td title="The Signal to Noise ratio of all voxels (i.e., Mean/StDev)" align="right">'''+ "%0.4f" % (masked_mean / masked_stdev)+'''</td>
</tr>
</tbody>
</table>
<table border="0" cellspacing="1" cellpadding="1">
<thead>
<tr>
  <th width="12.5%" rowspan="2" title="The number of the Slice">Slice<br />Number</th>
  <th width="12.5%" rowspan="2" title="The number Voxels included in the analysys">Voxel<br />Count</th>
  <th colspan="6" title="Values in the columns below here are derived from the mean slice intensities series for each slice.">For each Slice's Mean Slice Intensity Series:</th>
</tr>
<tr>
  <th width="12.5%" title="The Mean of the Mean Slice Intensities (i.e., sum the mean value of the included voxels for each slice for each timepoint and divide by the number of timepoints).">Mean</th>
  <th width="12.5%" title="Standard Deviation of Mean Slice Intensities (i.e., Take the Stanadard Deviation for the series containing the Mean Slice Intensity at each timepoint for this Slice).">StDev</th>
  <th width="12.5%" title="Signal to Noise Ratio of Mean Slice Intensities (i.e., Mean/StDev).">SNR</th>
  <th width="12.5%" title="The maximum mean slice intensity of this slice">Min</th>
  <th width="12.5%" title="The minimum mean slice intensity of this slice">Max</th>
  <th width="12.5%" title="The number of slices that were 2.5 standard deviations above or below average">Outliers</th>
</tr>
</thead>
<tbody>
'''

        slice_weighted_mean_mean = 0
        slice_weighted_stdev_mean = 0
        slice_weighted_snr_mean = 0
        slice_weighted_max_mean = 0
        slice_weighted_min_mean = 0
        outlier_count = 0
        total_voxel_count = 0

        for slice_idx in range(slice_count):
            slice_data         = slice_intensity_means[slice_idx]
            slice_voxel_count  = slice_voxel_counts[slice_idx]
            slice_mean         = slice_data.mean()
            slice_stdev        = slice_data.std(ddof=1)
            slice_snr          = slice_mean / slice_stdev
            slice_min          = slice_data.min()
            slice_max          = slice_data.max()
            slice_outliers     = numpy.zeros(slice_data.shape,dtype='int8')
            slice_outliers[slice_data < (slice_mean - (slice_stdev * 2.5))] = 1
            slice_outliers[slice_data > (slice_mean + (slice_stdev * 2.5))] = 1
            slice_outliers     = slice_outliers.sum()

            slice_weighted_mean_mean   += (slice_mean * slice_voxel_count)
            slice_weighted_stdev_mean  += (slice_stdev * slice_voxel_count)
            slice_weighted_snr_mean    += (slice_snr * slice_voxel_count)
            slice_weighted_min_mean    += (slice_min * slice_voxel_count)
            slice_weighted_max_mean    += (slice_max * slice_voxel_count)
            outlier_count     += slice_outliers
            total_voxel_count += slice_voxel_count
            report += '''
<tr>
  <td title="The number of the Slice" align="right">%03d</td>
  <td title="The number Voxels included for this slice in the analysys" align="right">%-d</td>
  <td title="The Mean of the Mean Slice Intensities (i.e., sum the mean value of the included voxels for each slice for each timepoint and divide by the number of timepoints)." align="right">%4.2f</td>
  <td title="Standard Deviation of Mean Slice Intensities (i.e., Take the Stanadard Deviation for the series containing the Mean Slice Intensity at each timepoint for this Slice)." align="right">%4.2f</td>
  <td title="Signal to Noise Ratio of Mean Slice Intensities (i.e., Mean/StDev)." align="right">%4.2f</td>
  <td title="The maximum mean slice intensity of this slice" align="right">%4.2f</td>
  <td title="The minimum mean slice intensity of this slice" align="right">%4.2f</td>
  <td title="The number of slices that were 2.5 standard deviations above or below average" align="right">%d</td>
</tr>''' %(
                slice_idx + 1,
                slice_voxel_count,
                slice_mean,
                slice_stdev,
                slice_snr,
                slice_min,
                slice_max,
                slice_outliers
                )
        report += '''
</tbody>
<thead>
<tr>
  <th title="The total number of voxels in each volume" colspan="2" rowspan="2">Voxels per Volume</th>
  <th title="Mulitply each value in these columns by the number of voxels per slice, sum the column and divide by the voxels per volume." colspan="5">Summary: Weighted Means</th>
  <th title="Total number of slices whose mean was 2.5 standard deviations from the mean / total number of slices" rowspan="2">Total Outliers<br />Total Slices</th>
</tr>
<tr>
  <th>Mean</th>
  <th>StDev</th>
  <th>SNR</th>
  <th>Min</th>
  <th>Max</th>
</thead>
'''
        report += '''
<tr>
  <td colspan="2" align="right" title="The total number of voxels in each volume">%d</td>
  <td align="right" title="The weighted &quot;mean&quot; mean obtained by multiplying each value in this column by the number of voxels per slice, summing the column and dividing by the total voxels per volume.">%4.2f</td>
  <td align="right" title="The weighted &quot;mean&quot; standard-deviation obtained by multiplying each value in this column by the number of voxels per slice, summing the column and dividing by the total voxels per volume.">%4.2f</td>
  <td align="right" title="The weighted &quot;mean&quot; SNR (signal-to-noise = mean/stdev) obtained by multiplying each value in this column by the number of voxels per slice, summing the column and dividing by the total voxels per volume.">%4.2f</td>
  <td align="right" title="The weighted &quot;mean&quot; mimumum obtained by multiplying each value in this column by the number of voxels per slice, summing the column and dividing by the total voxels per volume.">%4.2f</td>
  <td align="right" title="The weighted &quot;mean&quot; maximum obtained by multiplying each value in this column by the number of voxels per slice, summing the column and dividing by the total voxels per volume.">%4.2f</td>
  <td align="right" title="Total number of slices whose mean was 2.5 standard deviations from the mean / total number of slices">%d / %d</td>
</tr>'''  %(
            total_voxel_count,
            slice_weighted_mean_mean / total_voxel_count,
            slice_weighted_stdev_mean / total_voxel_count,
            slice_weighted_snr_mean / total_voxel_count,
            slice_weighted_min_mean / total_voxel_count,
            slice_weighted_max_mean / total_voxel_count,
            outlier_count,
            slice_count * volume_count
            )

        report += '''
</table>
</body>
</html>'''
        return report

    def save_stackcheck_report_html(self,filename=None,apply_mask=True,lower_threshold_to_zero=None,extended=False):
        if filename is None:
            filename = self.get_output_filename_root() + "_slice_report.html"
        report_html = self.get_stackcheck_report_html(apply_mask,lower_threshold_to_zero,extended)
        self._capture_file_save(filename,'mean slice report html')
        fh = open(filename,"w")
        fh.write(report_html)
        fh.close()
        return self

def run(filename, args):
    print("================================================================================")
    print("QA/QC on '%s'" %(filename))
    transparent = (not args.png_no_transparent)
    fni = NeuroImage(filename,skip=args.skip,output_dir=args.output_dir);
    fni.set_verbosity(args.verbosity)
    fni.set_mask_lower(args.mask_lower)
    if args.mask_upper is not None:
        fni.set_mask_upper(args.mask_upper)

    if args.thumbnail_save:
        fni.get_mosaic(transparent=transparent,
                       max_width=args.png_max_width
                       ).set_color_out_of_range(False).set_percentile_range(1,2).save_all()

    if args.mean_save_nii:
        fni.get_mean_image().save()
    if args.mean_save_png or args.mean_save_histogram:
        png = fni.get_mean_image().get_mosaic(transparent=transparent,max_width=args.mean_png_max_width)
        if args.mean_png_suffix is not None:
            png.set_suffix(args.mean_png_suffix)
        if args.mean_png_color_out_of_range is not None:
            png.set_color_out_of_range(args.mean_png_color_out_of_range)
        if args.mean_png_lower_percentile is not None or args.mean_png_upper_percentile is not None:
            png.set_percentile_range(args.mean_png_lower_percentile,args.mean_png_upper_percentile)
        if args.mean_png_stdev_range is not None:
            png.set_range_stdevs(args.mean_png_stdev_range)
        if args.mean_save_png:
            png.save()
        if args.mean_save_histogram:
            png.save_histogram(transparent=transparent)
        png.save_html()
    if args.mean_save_html:
        fni.get_mean_image().save_html()
    if args.mean_save_xml:
        fni.get_mean_image().save_xml()

    if args.report_save_html:
        fni.save_stackcheck_report_html(extended=args.extended_report)
    if args.report_save_txt:
        fni.save_stackcheck_report_text(extended=args.extended_report)
    if args.mean_slice_save_csv:
        fni.save_stackcheck_mean_slice_csv()
    if args.mean_slice_save_plot:
        fni.save_stackcheck_mean_slice_plot(
            format=args.mean_slice_plot_format,
            transparent=False,
            autoscale=args.mean_slice_plot_autoscale)
    if args.mean_slice_save_txt:
        fni.save_stackcheck_mean_slice_text()

    if args.mask_save_nii:
        fni.get_mask_image().save()
    if args.mask_save_png or args.mask_save_histogram:
        png = fni.get_mask_image().get_mosaic(transparent=transparent,max_width=args.mask_png_max_width)
        if args.mask_png_suffix is not None:
            png.set_suffix(args.mask_png_suffix)
        if args.mask_png_color_out_of_range is not None:
            png.set_color_out_of_range(args.mask_png_color_out_of_range)
        if args.mask_png_lower_percentile is not None or args.mask_png_upper_percentile is not None:
            png.set_percentile_range(args.mask_png_lower_percentile,args.mask_png_upper_percentile)
        if args.mask_png_stdev_range is not None:
            png.set_range_stdevs(args.mask_png_stdev_range)
        if args.mask_save_png:
            png.save()
        if args.mask_save_histogram:
            png.save_histogram(transparent=transparent)
        png.save_html()
    if args.mask_save_html:
        fni.get_mask_image().save_html()
    if args.mask_save_xml:
        fni.get_mask_image().save_xml()

    if args.stdev_save_nii:
        fni.get_stdev_image().save()
    if args.stdev_save_png or args.stdev_save_histogram:
        png = fni.get_stdev_image().get_mosaic(transparent=transparent,max_width=args.stdev_png_max_width)
        if args.stdev_png_suffix is not None:
            png.set_suffix(args.stdev_png_suffix)
        if args.stdev_png_color_out_of_range is not None:
            png.set_color_out_of_range(args.stdev_png_color_out_of_range)
        if args.stdev_png_lower_percentile is not None or args.stdev_png_upper_percentile is not None:
            png.set_percentile_range(args.stdev_png_lower_percentile,args.stdev_png_upper_percentile)
        if args.stdev_png_stdev_range is not None:
            png.set_range_stdevs(args.stdev_png_stdev_range)
        if args.stdev_save_png:
            png.save()
        if args.stdev_save_histogram:
            png.save_histogram(transparent=transparent)
        png.save_html()
    if args.stdev_save_html:
        fni.get_stdev_image().save_html()
    if args.stdev_save_xml:
        fni.get_stdev_image().save_xml()

    if args.snr_save_nii:
        fni.get_snr_image().save()
    if args.snr_save_png or args.snr_save_histogram:
        png = fni.get_snr_image().get_mosaic(transparent=transparent,max_width=args.snr_png_max_width)
        if args.snr_png_suffix is not None:
            png.set_suffix(args.snr_png_suffix)
        if args.snr_png_color_out_of_range is not None:
            png.set_color_out_of_range(args.snr_png_color_out_of_range)
        if args.snr_png_lower_percentile is not None or args.snr_png_upper_percentile is not None:
            png.set_percentile_range(args.snr_png_lower_percentile,args.snr_png_upper_percentile)
        if args.snr_png_stdev_range is not None:
            png.set_range_snrs(args.snr_png_stdev_range)
        if args.snr_save_png:
            png.save()
        if args.snr_save_histogram:
            png.save_histogram(transparent=transparent)
        png.save_html()
    if args.snr_save_html:
        fni.get_snr_image().save_html()
    if args.snr_save_xml:
        fni.get_snr_image().save_xml()

    if args.slope_save_nii:
        fni.get_slope_image().save()
    if args.slope_save_png or args.slope_save_histogram:
        png = fni.get_slope_image().get_mosaic(transparent=transparent,max_width=args.slope_png_max_width)
        if args.slope_png_suffix is not None:
            png.set_suffix(args.slope_png_suffix)
        if args.slope_png_color_out_of_range is not None:
            png.set_color_out_of_range(args.slope_png_color_out_of_range)
        if args.slope_png_lower_percentile is not None or args.slope_png_upper_percentile is not None:
            png.set_percentile_range(args.slope_png_lower_percentile,args.slope_png_upper_percentile)
        if args.slope_png_stdev_range is not None:
            png.set_range_slopes(args.slope_png_stdev_range)
        if args.slope_save_png:
            png.save()
        if args.slope_save_histogram:
            png.save_histogram(transparent=transparent)
        png.save_html()
    if args.slope_save_html:
        fni.get_slope_image().save_html()
    if args.slope_save_xml:
        fni.get_slope_image().save_xml()

    fni.save_html()
    print("================================================================================")

def parse_arguments(args):
    import argparse
    parser = argparse.ArgumentParser(description="NiFTI-1 File Quality Assurance")

    parser.add_argument("--all", "--everything", dest='save_all', action="store_true", default=False, help="Do everything.")
    parser.add_argument("--debug", "-d", dest='debug', action="store_true", default=False, help="Turn on debugging output")
    parser.add_argument("--mask-all", dest='mask_save_all', action="store_true", default=False, help="Save all mask image files.")
    parser.add_argument("--mask-histogram", dest='mask_save_histogram', action="store_true", default=False, help="Save mask image histogram file.")
    parser.add_argument("--mask-html", dest='mask_save_html', action="store_true", default=False, help="Save mask image HTML file which includes processing history information. Will also generate the mask png and the mask histogram files.")
    parser.add_argument("--mask-nii", "-mask", dest='mask_save_nii', action="store_true", default=False, help="Save mask image nii file.")
    parser.add_argument("--mask-png", dest='mask_save_png', action="store_true", default=False, help="Save mask image png file.")
    parser.add_argument("--mask-png-color-out-of-range", dest='mask_png_color_out_of_range', action="store_true", default=None, help="Use the red channel to display values that were truncated above the range and the blue channel to display values that were truncated as being below the range. If unset, uses the value of --png-color-out-of-range.")
    parser.add_argument("--mask-png-ignore-zero-minima", dest='mask_png_ignore_zero_minima', action="store_true", default=False, help="In special cases where the image has a minimum of 0 which is an outlier that provides little information (e.g., stdev images), ignore them when creating the PNG histogram. This makes the PNG more informative")
    parser.add_argument("--mask-png-lower-percentile", dest='mask_png_lower_percentile', type=float, default=None, help="Everything below the specified percentile from the minimum value in intensity ( 100 - percentile from the maximum value) is ignored when generating the PNG image. If --mask-png-color-out-of-range is specified, values outside of this range are included but in a different color channel and will appear non-gray. If not specified, --png-lower-percentile is used.")
    parser.add_argument("--mask-png-max-width", dest='mask_png_max_width', type=int, default=None, help="Maximum width of PNG file for the mask image. If unset, uses the value of --png-max-width.")
    parser.add_argument("--mask-png-stdev-range", dest='mask_png_stdev_range', type=float, default=None, help="Only include values within plus or minus these many standard deviations from the mask when creating the PNG file. If --mask-png-color-out-of-range is specified, values outside of this range are included but in a different color channel and will appear non-gray. If not specified, --png-stdev-range is used.")
    parser.add_argument("--mask-png-suffix", dest='mask_png_suffix', type=str, default=None, help="Append the specified suffix to ethe end of the file prior to the .png extension.")
    parser.add_argument("--mask-png-upper-percentile", dest='mask_png_upper_percentile', type=float, default=None, help="Everything above the specified percentile from the maximum value in intensity ( 100 - percentile from the minimum value) is ignored when generating the PNG image. If --mask-png-color-out-of-range is specified, values outside of this range are included but in a different color channel and will appear non-gray. If not specified, --png-upper-percentile is used.")
    parser.add_argument("--mask-threshold", "--mask-lower", dest='mask_lower', type=float, default=150.0, help="The lower threshold to use for generating the image mask and/or masking the data. Anything below this threshold will be masked out. (Default: 150.0)")
    parser.add_argument("--mask-upper", dest='mask_upper', type=float, default=None, help="The upper threshold to use for generating the image mask and/or masking the data. Anything above this threshold will be masked out. (Default: None)")
    parser.add_argument("--mask-xml", dest='mask_save_xml', action="store_true", default=False, help="Save mask image information XML file.")
    parser.add_argument("--mean-all", dest='mean_save_all', action="store_true", default=False, help="Save all mean image files.")
    parser.add_argument("--mean-histogram", dest='mean_save_histogram', action="store_true", default=False, help="Save mean image histogram file.")
    parser.add_argument("--mean-html", dest='mean_save_html', action="store_true", default=False, help="Save mean image HTML file which includes processing history information. Will also generate the mean png and the mean histogram files.")
    parser.add_argument("--mean-nii", "-mean", dest='mean_save_nii', action="store_true", default=False, help="Save mean image nii file.")
    parser.add_argument("--mean-png", dest='mean_save_png', action="store_true", default=False, help="Save mean image png file.")
    parser.add_argument("--mean-png-color-out-of-range", dest='mean_png_color_out_of_range', action="store_true", default=None, help="Use the red channel to display values that were truncated above the range and the blue channel to display values that were truncated as being below the range. If unset, uses the value of --png-color-out-of-range.")
    parser.add_argument("--png-ignore-zero-minima", dest='png_ignore_zero_minima', action="store_true", default=False, help="In special cases where the image has a minimum of 0 which is an outlier that provides little information (e.g., stdev images), ignore them when creating the PNG histogram. This makes the PNG more informative")
    parser.add_argument("--mean-png-ignore-zero-minima", dest='mean_png_ignore_zero_minima', action="store_true", default=False, help="In special cases where the image has a minimum of 0 which is an outlier that provides little information (e.g., stdev images), ignore them when creating the PNG histogram. This makes the PNG more informative")
    parser.add_argument("--mean-png-lower-percentile", dest='mean_png_lower_percentile', type=float, default=None, help="Everything below the specified percentile from the minimum value in intensity ( 100 - percentile from the maximum value) is ignored when generating the PNG image. If --mean-png-color-out-of-range is specified, values outside of this range are included but in a different color channel and will appear non-gray. If not specified, --png-lower-percentile is used.")
    parser.add_argument("--mean-png-max-width", dest='mean_png_max_width', type=int, default=None, help="Maximum width of PNG file for the mean image. If unset, uses the value of --png-max-width.")
    parser.add_argument("--mean-png-stdev-range", dest='mean_png_stdev_range', type=float, default=None, help="Only include values within plus or minus these many standard deviations from the mean when creating the PNG file. If --mean-png-color-out-of-range is specified, values outside of this range are included but in a different color channel and will appear non-gray. If not specified, --png-stdev-range is used.")
    parser.add_argument("--mean-png-suffix", dest='mean_png_suffix', type=str, default=None, help="Append the specified suffix to ethe end of the file prior to the .png extension.")
    parser.add_argument("--mean-png-upper-percentile", dest='mean_png_upper_percentile', type=float, default=None, help="Everything above the specified percentile from the maximum value in intensity ( 100 - percentile from the minimum value) is ignored when generating the PNG image. If --mean-png-color-out-of-range is specified, values outside of this range are included but in a different color channel and will appear non-gray. If not specified, --png-upper-percentile is used.")
    parser.add_argument("--mean-slice-csv", dest='mean_slice_save_csv', action="store_true", default=False, help="Save the mean slice intensity data as a cama separated values (CSV) file good for use in spreadsheets with the first column being the slice number, and subsequent columns being the mean slice intensity for those slices at each time point (aka in each volume).")
    parser.add_argument("--mean-slice-plot", dest='mean_slice_save_plot', action="store_true", default=False, help="Save the mean slice intensity plot as an image (default format:SVG) for inclusion in publications, web pages, T-shirts.")
    parser.add_argument("--mean-slice-plot-format", dest='mean_slice_plot_format', required=False, default='svg', help="Specify the file format for the mean slice intensity plot. Valid values are: 'png', 'svg'. Note; PNG recommended for XNAT uploads; SVG for publications and other websites.")
    parser.add_argument("--mean-slice-plot-autoscale", dest='mean_slice_plot_autoscale', action="store_true", required=False, default=True, help="Autoscale the plot (Default).")
    parser.add_argument("--mean-slice-plot-no-autoscale", dest='mean_slice_plot_autoscale', action="store_false", required=False, default=True, help="Do not autscale.")
    parser.add_argument("--mean-slice-txt", "-plot", dest='mean_slice_save_txt', action="store_true", default=False, help="Save the mean slice intensity data as a whitespace delimited text file with the first column being the slice number, and subsequent columns being the mean slice intensity for those slices at each time point (aka in each volume).")
    parser.add_argument("--mean-xml", dest='mean_save_xml', action="store_true", default=False, help="Save mean image information XML file.")
    parser.add_argument("--mimic-slicer", dest='mimic_slicer', action="store_true", default=False, help="When creating PNG snapshots, mimic FSL \"slicer\" behavior when creating mosaic/montage images by truncating data to above and below the top and bottom 2nd percentile respectively.")
    parser.add_argument("--no-lpi", dest='no_lpi', action="store_true", default=False, help="Do not enforce LPI dimensions on input file")
    parser.add_argument("--no-swapdim", dest='no_swap_dim', action="store_true", default=False, help="Do not try and change NEUROLOGICAL imaged to RADIOLOGICAL")
    parser.add_argument("--output-dir", "-o", dest='output_dir', required=False, default=None, help="Where to put the generated files if not in the same directory as the input file")
    parser.add_argument("--png-color-out-of-range", "--png-color", dest='png_color_out_of_range', action="store_true", default=False, help="When creating PNG files, use the red channel to display values that were truncated above the range and the blue channel to display values that were truncated as being below the range.")
    parser.add_argument("--png-no-transparency", dest='png_no_transparent', action="store_true", default=False, help="When creating PNG files, do NOT use transparency to show that no slices are present (i.e., \"empty\" blocks in the mosaic will be filled with black). This also affects plots which will normally not have a background color set.")
    parser.add_argument("--png-lower-percentile", dest='png_lower_percentile', type=float, default=None, help="Everything below the specified percentile from the minimum value in intensity ( 100 - percentile from the maximum value) is ignored when generating the PNG image. If --png-color-out-of-range is specified, values outside of this range are included but in a different color channel and will appear non-gray.")
    parser.add_argument("--png-max-width", dest='png_max_width', type=int, default=None, help="Maximum width of PNG file for a PNG image.")
    parser.add_argument("--png-stdev-range", dest='png_stdev_range', type=float, default=None, help="Only include values within plus or minus these many standard deviations from the mean when creating the PNG file. If --mean-png-color-out-of-range is specified, values outside of this range are included but in a different color channel and will appear non-gray. If --png-color-out-of-range is specified, values outside of this range are included but in a different color channel and will appear non-gray.")
    parser.add_argument("--png-upper-percentile", dest='png_upper_percentile', type=float, default=None, help="Everything above the specified percentile from the maximum value in intensity ( 100 - percentile from the minimum value) is ignored when generating the PNG image. If --png-color-out-of-range is specified, values outside of this range are included but in a different color channel and will appear non-gray.")
    parser.add_argument("--report-html", dest='report_save_html', action="store_true", default=False, help="Save the mean slice intensity summary _report.html file which contains the same information as the stackcheck compatible text version but with tool-tips explaining the data and a nicer looking UI.")
    parser.add_argument("--report-txt", "-report", dest='report_save_txt', action="store_true", default=False, help="Save the mean slice intensity summary _report.txt file which is stackcheck compatible.")
    parser.add_argument("--extended-report", dest='extended_report', action="store_true", default=False, help="Include additional information in the report file(s).")
    parser.add_argument("--skip", dest='skip', type=int, default=0, help="Number of volumes to skip")
    parser.add_argument("--slope-all", dest='slope_save_all', action="store_true", default=False, help="Save all slope volume (each voxel in volume is the slope for the linear regression of the voxel values) files.")
    parser.add_argument("--slope-histogram", dest='slope_save_histogram', action="store_true", default=False, help="Save slope volume (each voxel in volume is the slope for the linear regression of the voxel values) histogram file.")
    parser.add_argument("--slope-html", dest='slope_save_html', action="store_true", default=False, help="Save slope image HTML file which includes processing history information. Will also generate the slope png and the slope histogram files.")
    parser.add_argument("--slope-nii", "-slope", dest='slope_save_nii', action="store_true", default=False, help="Save slope volume (each voxel in volume is the slope for the linear regression of the voxel values) nii file.")
    parser.add_argument("--slope-png", dest='slope_save_png', action="store_true", default=False, help="Save slope volume (each voxel in volume is the slope for the linear regression of the voxel values) png file.")
    parser.add_argument("--slope-png-color-out-of-range", dest='slope_png_color_out_of_range', action="store_true", default=None, help="Use the red channel to display values that were truncated above the range and the blue channel to display values that were truncated as being below the range. If unset, uses the value of --png-color-out-of-range.")
    parser.add_argument("--slope-png-ignore-zero-minima", dest='slope_png_ignore_zero_minima', action="store_true", default=False, help="In special cases where the image has a minimum of 0 which is an outlier that provides little information (e.g., stdev images), ignore them when creating the PNG histogram. This makes the PNG more informative")
    parser.add_argument("--slope-png-lower-percentile", dest='slope_png_lower_percentile', type=float, default=None, help="Everything below the specified percentile from the minimum value in intensity ( 100 - percentile from the maximum value) is ignored when generating the PNG image. If --slope-png-color-out-of-range is specified, values outside of this range are included but in a different color channel and will appear non-gray. If not specified, --png-lower-percentile is used.")
    parser.add_argument("--slope-png-max-width", dest='slope_png_max_width', type=int, default=None, help="Maximum width of PNG file for the slope image. If unset, uses the value of --png-max-width.")
    parser.add_argument("--slope-png-stdev-range", dest='slope_png_stdev_range', type=float, default=None, help="Only include values within plus or minus these many standard deviations from the slope when creating the PNG file. If --slope-png-color-out-of-range is specified, values outside of this range are included but in a different color channel and will appear non-gray. If not specified, --png-stdev-range is used.")
    parser.add_argument("--slope-png-suffix", dest='slope_png_suffix', type=str, default=None, help="Append the specified suffix to ethe end of the file prior to the .png extension.")
    parser.add_argument("--slope-png-upper-percentile", dest='slope_png_upper_percentile', type=float, default=None, help="Everything above the specified percentile from the maximum value in intensity ( 100 - percentile from the minimum value) is ignored when generating the PNG image. If --slope-png-color-out-of-range is specified, values outside of this range are included but in a different color channel and will appear non-gray. If not specified, --png-upper-percentile is used.")
    parser.add_argument("--slope-xml", dest='slope_save_xml', action="store_true", default=False, help="Save slope image information XML file.")
    parser.add_argument("--snr-all", dest='snr_save_all', action="store_true", default=False, help="Save all SNR (mean/stdev) volume files.")
    parser.add_argument("--snr-histogram", dest='snr_save_histogram', action="store_true", default=False, help="Save SNR (mean/stdev) volume histogram file.")
    parser.add_argument("--snr-html", dest='snr_save_html', action="store_true", default=False, help="Save SNR image HTML file which includes processing history information. Will also generate the SNR png and the SNR histogram files.")
    parser.add_argument("--snr-nii", "-snr", dest='snr_save_nii', action="store_true", default=False, help="Save SNR (mean/stdev) volume nii file.")
    parser.add_argument("--snr-png", dest='snr_save_png', action="store_true", default=False, help="Save SNR (mean/stdev) volume png file.")
    parser.add_argument("--snr-png-color-out-of-range", dest='snr_png_color_out_of_range', action="store_true", default=None, help="Use the red channel to display values that were truncated above the range and the blue channel to display values that were truncated as being below the range. If unset, uses the value of --png-color-out-of-range.")
    parser.add_argument("--snr-png-ignore-zero-minima", dest='snr_png_ignore_zero_minima', action="store_true", default=False, help="In special cases where the image has a minimum of 0 which is an outlier that provides little information (e.g., stdev images), ignore them when creating the PNG histogram. This makes the PNG more informative")
    parser.add_argument("--snr-png-lower-percentile", dest='snr_png_lower_percentile', type=float, default=None, help="Everything below the specified percentile from the minimum value in intensity ( 100 - percentile from the maximum value) is ignored when generating the PNG image. If --snr-png-color-out-of-range is specified, values outside of this range are included but in a different color channel and will appear non-gray. If not specified, --png-lower-percentile is used.")
    parser.add_argument("--snr-png-max-width", dest='snr_png_max_width', type=int, default=None, help="Maximum width of PNG file for the snr image. If unset, uses the value of --png-max-width.")
    parser.add_argument("--snr-png-stdev-range", dest='snr_png_stdev_range', type=float, default=None, help="Only include values within plus or minus these many standard deviations from the snr when creating the PNG file. If --snr-png-color-out-of-range is specified, values outside of this range are included but in a different color channel and will appear non-gray. If not specified, --png-stdev-range is used.")
    parser.add_argument("--snr-png-suffix", dest='snr_png_suffix', type=str, default=None, help="Append the specified suffix to ethe end of the file prior to the .png extension.")
    parser.add_argument("--snr-png-upper-percentile", dest='snr_png_upper_percentile', type=float, default=None, help="Everything above the specified percentile from the maximum value in intensity ( 100 - percentile from the minimum value) is ignored when generating the PNG image. If --snr-png-color-out-of-range is specified, values outside of this range are included but in a different color channel and will appear non-gray. If not specified, --png-upper-percentile is used.")
    parser.add_argument("--snr-xml", dest='snr_save_xml', action="store_true", default=False, help="Save SNR image information XML file.")
    parser.add_argument("--stdev-all", dest='stdev_save_all', action="store_true", default=False, help="Save all standard deviation volume files.")
    parser.add_argument("--stdev-histogram", dest='stdev_save_histogram', action="store_true", default=False, help="Save standard deviation volume histogram file.")
    parser.add_argument("--stdev-html", dest='stdev_save_html', action="store_true", default=False, help="Save standard deviation image HTML file which includes processing history information. Will also generate the stdev png and the stdev histogram files.")
    parser.add_argument("--stdev-nii", "-stdev", dest='stdev_save_nii', action="store_true", default=False, help="Save standard deviation volume nii file.")
    parser.add_argument("--stdev-png", dest='stdev_save_png', action="store_true", default=False, help="Save standard deviation volume png file.")
    parser.add_argument("--stdev-png-color-out-of-range", dest='stdev_png_color_out_of_range', action="store_true", default=None, help="Use the red channel to display values that were truncated above the range and the blue channel to display values that were truncated as being below the range. If unset, uses the value of --png-color-out-of-range.")
    parser.add_argument("--stdev-png-no-ignore-zero-minima", dest='stdev_png_ignore_zero_minima', action="store_true", default=False, help="In special cases where the image has a minimum of 0 which is an outlier that provides little information do NOT ignore it (unlike the default for other images) This makes the PNG histogram more like the data histogram, but at the cost of potentially severely reduced histogram range.")
    parser.add_argument("--stdev-png-lower-percentile", dest='stdev_png_lower_percentile', type=float, default=None, help="Everything below the specified percentile from the minimum value in intensity ( 100 - percentile from the maximum value) is ignored when generating the PNG image. If --stdev-png-color-out-of-range is specified, values outside of this range are included but in a different color channel and will appear non-gray. If not specified, --png-lower-percentile is used.")
    parser.add_argument("--stdev-png-max-width", dest='stdev_png_max_width', type=int, default=None, help="Maximum width of PNG file for the stdev image. If unset, uses the value of --png-max-width.")
    parser.add_argument("--stdev-png-stdev-range", dest='stdev_png_stdev_range', type=float, default=None, help="Only include values within plus or minus these many standard deviations from the stdev when creating the PNG file. If --stdev-png-color-out-of-range is specified, values outside of this range are included but in a different color channel and will appear non-gray. If not specified, --png-stdev-range is used.")
    parser.add_argument("--stdev-png-suffix", dest='stdev_png_suffix', type=str, default=None, help="Append the specified suffix to ethe end of the file prior to the .png extension.")
    parser.add_argument("--stdev-png-upper-percentile", dest='stdev_png_upper_percentile', type=float, default=None, help="Everything above the specified percentile from the maximum value in intensity ( 100 - percentile from the minimum value) is ignored when generating the PNG image. If --stdev-png-color-out-of-range is specified, values outside of this range are included but in a different color channel and will appear non-gray. If not specified, --png-upper-percentile is used.")
    parser.add_argument("--stdev-xml", dest='stdev_save_xml', action="store_true", default=False, help="Save standard deviation image information XML file.")
    parser.add_argument("--thumbnail", "--thumb", dest='thumbnail_save', action="store_true", default=False, help="Save a PNG thumbnail of the middle volume.")
    parser.add_argument("--verbose", "-v", dest='verbosity', action="count", default=0, help="Increase the verbosity of messages")
    parser.add_argument("--extended-bold-qc", "-xbc", dest='extended_bold_qc', action="store_true", default=False, help="Set defaults for ExtendedBOLDQC")

    parser.add_argument('files', nargs='*')

    args = parser.parse_args(args)

    args.output_dir = os.path.expanduser(args.output_dir)
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)        

    if args.extended_bold_qc:
        args.mask_save_nii          = True
        args.mask_save_png          = True
        args.mean_save_nii          = True
        args.mean_save_png          = True
        args.slope_save_nii         = True
        args.slope_save_png         = True
        args.snr_save_nii           = True
        args.snr_save_png           = True
        args.stdev_save_nii         = True
        args.stdev_save_png         = True
        args.mimic_slicer           = True        
        args.png_max_width          = 600
        args.png_ignore_zero_minima = True
        args.png_no_transparent     = True
        args.report_save_html       = True
        args.report_save_txt        = True
        args.report_save_xml        = True
        args.mean_slice_save_csv    = True
        args.mean_slice_save_plot   = True
        args.mean_slice_save_txt    = True
        args.mean_slice_plot_format = 'png'

    if args.save_all:
        args.thumbnail_save       = True
        args.mask_save_all        = True
        args.mean_save_all        = True
        args.slope_save_all       = True
        args.snr_save_all         = True
        args.stdev_save_all       = True
        args.report_save_html     = True
        args.report_save_txt      = True
        args.mean_slice_save_csv  = True
        args.mean_slice_save_plot = True
        args.mean_slice_save_txt  = True

    if args.mask_save_all:
        args.mask_save_histogram = True
        args.mask_save_html      = True
        args.mask_save_nii       = True
        args.mask_save_png       = True
        args.mask_save_xml       = True

    if args.mean_save_all:
        args.mean_save_histogram = True
        args.mean_save_html      = True
        args.mean_save_nii       = True
        args.mean_save_png       = True
        args.mean_save_xml       = True

    if args.slope_save_all:
        args.slope_save_histogram = True
        args.slope_save_html      = True
        args.slope_save_nii       = True
        args.slope_save_png       = True
        args.slope_save_xml       = True

    if args.snr_save_all:
        args.snr_save_histogram = True
        args.snr_save_html      = True
        args.snr_save_nii       = True
        args.snr_save_png       = True
        args.snr_save_xml       = True

    if args.stdev_save_all:
        args.stdev_save_histogram = True
        args.stdev_save_html      = True
        args.stdev_save_nii       = True
        args.stdev_save_png       = True
        args.stdev_save_xml       = True

    if args.png_lower_percentile:
        args.mask_png_lower_percentile = args.png_lower_percentile
        args.mean_png_lower_percentile = args.png_lower_percentile
        args.slope_png_lower_percentile = args.png_lower_percentile
        args.snr_png_lower_percentile = args.png_lower_percentile
        args.stdev_png_lower_percentile = args.png_lower_percentile

    if args.png_upper_percentile:
        args.mask_png_upper_percentile = args.png_upper_percentile
        args.mean_png_upper_percentile = args.png_upper_percentile
        args.slope_png_upper_percentile = args.png_upper_percentile
        args.snr_png_upper_percentile = args.png_upper_percentile
        args.stdev_png_upper_percentile = args.png_upper_percentile

    if args.mimic_slicer:
        if args.png_lower_percentile is None:
            args.png_lower_percentile = 2
        if args.png_upper_percentile is None:
            args.png_upper_percentile = 2

    if args.mask_png_lower_percentile is None:
        args.mask_png_lower_percentile = args.png_lower_percentile
    if args.mean_png_lower_percentile is None:
        args.mean_png_lower_percentile = args.png_lower_percentile
    if args.slope_png_lower_percentile is None:
        args.slope_png_lower_percentile = args.png_lower_percentile
    if args.snr_png_lower_percentile is None:
        args.snr_png_lower_percentile = args.png_lower_percentile
    if args.stdev_png_lower_percentile is None:
        args.stdev_png_lower_percentile = args.png_lower_percentile

    if args.mask_png_upper_percentile is None:
        args.mask_png_upper_percentile = args.png_upper_percentile
    if args.mean_png_upper_percentile is None:
        args.mean_png_upper_percentile = args.png_upper_percentile
    if args.slope_png_upper_percentile is None:
        args.slope_png_upper_percentile = args.png_upper_percentile
    if args.snr_png_upper_percentile is None:
        args.snr_png_upper_percentile = args.png_upper_percentile
    if args.stdev_png_upper_percentile is None:
        args.stdev_png_upper_percentile = args.png_upper_percentile

    if args.png_color_out_of_range is not None:
        if args.mask_png_color_out_of_range is None:
            args.mask_png_color_out_of_range = args.png_color_out_of_range
        if args.mean_png_color_out_of_range is None:
            args.mean_png_color_out_of_range = args.png_color_out_of_range
        if args.slope_png_color_out_of_range is None:
            args.slope_png_color_out_of_range = args.png_color_out_of_range
        if args.snr_png_color_out_of_range is None:
            args.snr_png_color_out_of_range = args.png_color_out_of_range
        if args.stdev_png_color_out_of_range is None:
            args.stdev_png_color_out_of_range = args.png_color_out_of_range

    if args.png_max_width is not None:
        if args.mask_png_max_width is None:
            args.mask_png_max_width = args.png_max_width
        if args.mean_png_max_width is None:
            args.mean_png_max_width = args.png_max_width
        if args.slope_png_max_width is None:
            args.slope_png_max_width = args.png_max_width
        if args.snr_png_max_width is None:
            args.snr_png_max_width = args.png_max_width
        if args.stdev_png_max_width is None:
            args.stdev_png_max_width = args.png_max_width

    if args.png_stdev_range is not None:
        if args.mask_png_stdev_range is None:
            args.mask_png_stdev_range = args.png_stdev_range
        if args.mean_png_stdev_range is None:
            args.mean_png_stdev_range = args.png_stdev_range
        if args.slope_png_stdev_range is None:
            args.slope_png_stdev_range = args.png_stdev_range
        if args.snr_png_stdev_range is None:
            args.snr_png_stdev_range = args.png_stdev_range
        if args.stdev_png_stdev_range is None:
            args.stdev_png_stdev_range = args.png_stdev_range

    if args.png_ignore_zero_minima is not None:
        if args.mask_png_ignore_zero_minima is None:
            args.mask_png_ignore_zero_minima = args.png_ignore_zero_minima
        if args.mean_png_ignore_zero_minima is None:
            args.mean_png_ignore_zero_minima = args.png_ignore_zero_minima
        if args.slope_png_ignore_zero_minima is None:
            args.slope_png_ignore_zero_minima = args.png_ignore_zero_minima
        if args.snr_png_ignore_zero_minima is None:
            args.snr_png_ignore_zero_minima = args.png_ignore_zero_minima
        if args.stdev_png_ignore_zero_minima is None:
            args.stdev_png_ignore_zero_minima = args.png_ignore_zero_minima
    return args

def main():
    import sys, os
    args = parse_arguments(sys.argv[1:])
    
    if len(args.files) < 1:
        print("Usage: %s file_1 [file_2 [...]]" %(os.path.basename(sys.argv[0])))
        exit(1)
    for filename in args.files:
        #run_all_default(filename)
        run(filename, args)
        #NeuroImage(filename,skip=0).set_mask_lower(150.0).save_stackcheck_report_text().save_stackcheck_report_html()


if __name__ == "__main__":
    main()
