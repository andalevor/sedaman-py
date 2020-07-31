from ctypes import cdll, c_void_p, c_size_t, c_double, Structure, Union, c_int8, c_int16, c_int32, c_int64, c_uint8, c_uint16, c_uint32, c_uint64, c_float, c_double, c_int, c_char_p, c_bool, c_char_p, create_string_buffer, POINTER

libsedaman = cdll.LoadLibrary('libsedaman.so')


class Error(Exception):
    def __init__(self, arg):
        self.args = arg


class ISEGY:
    def __init__(self, file_name):
        sedaman_ISEGY_new = libsedaman.sedaman_ISEGY_new
        sedaman_ISEGY_new.restype = c_void_p
        sedaman_ISEGY_new.argtypes = [c_void_p, c_char_p]
        sedaman_ISEGY_has_trace = libsedaman.sedaman_ISEGY_has_trace
        sedaman_ISEGY_has_trace.restype = c_bool
        sedaman_ISEGY_has_trace.argtypes = [c_void_p, c_char_p]
        sedaman_ISEGY_read_trace = libsedaman.sedaman_ISEGY_read_trace
        sedaman_ISEGY_read_trace.restype = c_void_p
        sedaman_ISEGY_read_trace.argtypes = [c_void_p, c_char_p]
        sedaman_ISEGY_delete = libsedaman.sedaman_ISEGY_delete
        sedaman_ISEGY_delete.argtypes = [c_void_p]
        self.ISEGY_has_trace = sedaman_ISEGY_has_trace
        self.ISEGY_read_trace = sedaman_ISEGY_read_trace
        self.ISEGY_delete = sedaman_ISEGY_delete
        err = create_string_buffer(256)
        self.ISEGY = sedaman_ISEGY_new(file_name.encode(), err)
        if self.ISEGY == 0:
            raise Exception(err.value.decode())

    def __del__(self):
        self.ISEGY_delete(self.ISEGY)

    def has_trace(self):
        return self.ISEGY_has_trace(self.ISEGY)

    def read_trace(self):
        err = c_char_p(0)
        c_trc = self.ISEGY_read_trace(self.ISEGY, err)
        return Trace(c_trc)


class OSEGYRev0:
    def __init__(self, file_name, text_header=None, bin_header=None):
        if text_header == None and bin_header == None:
            sedaman_OSEGYRev0_new = libsedaman.sedaman_OSEGYRev0_new
            self.OSEGYRev0 = sedaman_OSEGYRev0_new(file_name.encode())
        elif bin_header == None:
            sedaman_OSEGYRev0_new = libsedaman.sedaman_OSEGYRev0_new_with_text_header
            self.OSEGYRev0 = sedaman_OSEGYRev0_new(
                file_name.encode(), text_header)
        else:
            sedaman_OSEGYRev0_new = libsedaman.sedaman_OSEGYRev0_new_with_text_and_bin_headers
            self.OSEGYRev0 = sedaman_OSEGYRev0_new(
                file_name.encode(), text_header, bin_header)
        sedaman_OSEGYRev0_new.restype = c_void_p
        sedaman_OSEGYRev0_write_trace = libsedaman.sedaman_OSEGYRev0_write_trace
        sedaman_OSEGYRev0_write_trace.argtypes = [c_void_p, c_void_p, c_void_p]
        sedaman_OSEGYRev0_delete = libsedaman.sedaman_OSEGYRev0_delete
        sedaman_OSEGYRev0_delete.argtypes = [c_void_p]
        self.OSEGYRev0_write_trace = sedaman_OSEGYRev0_write_trace
        self.OSEGYRev0_delete = sedaman_OSEGYRev0_delete

    def __del__(self):
        self.OSEGYRev0_delete(self.OSEGYRev0)

    def write_trace(self, trace):
        err = c_char_p()
        self.OSEGYRev0_write_trace(self.OSEGYRev0, trace.c_trc, err)


class Trace:
    def __init__(self, c_trc):
        self.c_trc = c_trc
        self.samples = Trace.Samples(self.c_trc)
        self.header = Trace.Header(self.c_trc)
        sedaman_Trace_delete = libsedaman.sedaman_Trace_delete
        sedaman_Trace_delete.argtypes = [c_void_p]
        self.trc_delete = sedaman_Trace_delete

    def __del__(self):
        self.trc_delete(self.c_trc)

    class Header:
        def __init__(self, c_trc):
            self.c_trc = c_trc
            sedaman_Trace_Header_get_value = libsedaman.sedaman_Trace_Header_get_value
            sedaman_Trace_Header_get_value.restype = ValueHolder
            sedaman_Trace_Header_get_value.argtypes = [c_void_p, c_void_p]
            self.get_val = sedaman_Trace_Header_get_value

        def get_value(self, key):
            holder = self.get_val(self.c_trc, key.encode())
            if holder.type == 0:
                return 'no such header'
            elif holder.type == 1:
                return holder.val.i8
            elif holder.type == 2:
                return holder.val.i16
            elif holder.type == 3:
                return holder.val.i32
            elif holder.type == 4:
                return holder.val.i64
            elif holder.type == 5:
                return holder.val.u8
            elif holder.type == 6:
                return holder.val.u16
            elif holder.type == 7:
                return holder.val.u32
            elif holder.type == 8:
                return holder.val.u64
            elif holder.type == 9:
                return holder.val.f32
            elif holder.type == 10:
                return holder.val.f64

    class Samples:
        def __init__(self, c_trc):
            self.c_trc = c_trc
            sedaman_Trace_samples_num = libsedaman.sedaman_Trace_samples_num
            sedaman_Trace_samples_num.restype = c_size_t
            sedaman_Trace_samples_num.argtypes = [c_void_p]
            self.get_samples_num = sedaman_Trace_samples_num
            sedaman_Trace_get_sample = libsedaman.sedaman_Trace_get_sample
            sedaman_Trace_get_sample.restype = c_double
            sedaman_Trace_get_sample.argtypes = [c_void_p]
            self.get_sample = sedaman_Trace_get_sample

        def __getitem__(self, key):
            return self.get_sample(self.c_trc, key)

        def number(self):
            return self.get_samples_num(self.c_trc)


class Value(Union):
    _fields_ = [('i8', c_int8),
                ('i16', c_int16),
                ('i32', c_int32),
                ('i64', c_int64),
                ('u8', c_uint8),
                ('u16', c_uint16),
                ('u32', c_uint32),
                ('u64', c_uint64),
                ('f32', c_float),
                ('f64', c_double)]


class ValueHolder(Structure):
    _fields_ = [('type', c_int),
                ('val', Value)]
