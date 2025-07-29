use pyo3::{ffi, prelude::*};

use std::{
    ffi::{c_int, c_void},
    ops::Deref,
    ptr, slice,
};

pub struct Buffer<'a>(&'a [u8]);

impl<'a> From<&'a [u8]> for Buffer<'a> {
    fn from(data: &'a [u8]) -> Self {
        Buffer(data)
    }
}

impl Deref for Buffer<'_> {
    type Target = [u8];

    fn deref(&self) -> &Self::Target {
        self.0
    }
}

impl<'py> FromPyObject<'py> for Buffer<'py> {
    fn extract_bound(ob: &Bound<'py, PyAny>) -> PyResult<Self> {
        let mut buf = ptr::null::<u8>();
        let mut len = 0usize;
        let buf = unsafe {
            error_on_minus_one(
                ob.py(),
                PyObject_AsReadBuffer(
                    ob.as_ptr(),
                    &mut buf as *mut *const _ as *mut *const c_void,
                    &mut len as *mut _ as *mut isize,
                ),
            )?;
            slice::from_raw_parts(buf, len)
        };
        Ok(Buffer(buf))
    }
}

extern "C" {
    fn PyObject_AsReadBuffer(
        obj: *mut ffi::PyObject,
        buffer: *mut *const c_void,
        buffer_len: *mut ffi::Py_ssize_t,
    ) -> c_int;
}
#[inline]
fn error_on_minus_one(py: Python, result: i32) -> PyResult<()> {
    if result == -1 {
        Err(PyErr::fetch(py))
    } else {
        Ok(())
    }
}
