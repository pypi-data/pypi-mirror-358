use crate::list_stream::ListStream;
use crate::read_stream::ReadStream;
use crate::tos_client::TosClient;
use crate::tos_error::{TosError, TosException};
use crate::tos_model::{ListObjectsResult, TosObject};
use crate::write_stream::WriteStream;
use pyo3::prelude::*;

mod list_stream;
mod read_stream;
mod tos_client;
mod tos_error;
mod tos_model;
mod write_stream;

#[pymodule]
#[pyo3(name = "tosnativeclient")]
fn main(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<TosClient>()?;
    m.add_class::<ListStream>()?;
    m.add_class::<ListObjectsResult>()?;
    m.add_class::<TosObject>()?;
    m.add_class::<WriteStream>()?;
    m.add_class::<ReadStream>()?;
    m.add_class::<TosError>()?;
    m.add("TosException", m.py().get_type::<TosException>())?;
    Ok(())
}
