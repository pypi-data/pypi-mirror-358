// ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
// ┃ ██████ ██████ ██████       █      █      █      █      █ █▄  ▀███ █       ┃
// ┃ ▄▄▄▄▄█ █▄▄▄▄▄ ▄▄▄▄▄█  ▀▀▀▀▀█▀▀▀▀▀ █ ▀▀▀▀▀█ ████████▌▐███ ███▄  ▀█ █ ▀▀▀▀▀ ┃
// ┃ █▀▀▀▀▀ █▀▀▀▀▀ █▀██▀▀ ▄▄▄▄▄ █ ▄▄▄▄▄█ ▄▄▄▄▄█ ████████▌▐███ █████▄   █ ▄▄▄▄▄ ┃
// ┃ █      ██████ █  ▀█▄       █ ██████      █      ███▌▐███ ███████▄ █       ┃
// ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
// ┃ Copyright (c) 2017, the Perspective Authors.                              ┃
// ┃ ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌ ┃
// ┃ This file is part of the Perspective library, distributed under the terms ┃
// ┃ of the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0). ┃
// ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

use std::sync::Arc;

use futures::future::BoxFuture;
use perspective_server::{Server, ServerResult};
use pollster::FutureExt;
use pyo3::IntoPyObjectExt;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyAny;

use super::session_sync::{PyConnectionSync, PySession};
use crate::client::client_async::AsyncClient;

#[pyclass(subclass, module = "perspective")]
#[derive(Clone)]
pub struct PyServer {
    pub server: Server,
}

#[pymethods]
impl PyServer {
    #[new]
    #[pyo3(signature = (on_poll_request=None))]
    pub fn new(on_poll_request: Option<Py<PyAny>>) -> Self {
        Self {
            server: Server::new(on_poll_request.map(|f| {
                let f = Arc::new(f);
                Arc::new(move |server: &Server| {
                    let f = f.clone();
                    let server = server.clone();
                    Box::pin(async move {
                        Python::with_gil(|py| {
                            f.call1(py, (PyServer { server }.into_py_any(py).unwrap(),))
                        })?;
                        Ok(())
                    }) as BoxFuture<'static, ServerResult<()>>
                })
                    as Arc<dyn Fn(&Server) -> BoxFuture<'static, ServerResult<()>> + Send + Sync>
            })),
        }
    }

    pub fn new_session(&self, _py: Python, response_cb: Py<PyAny>) -> PySession {
        let session = self
            .server
            .new_session(PyConnectionSync(response_cb.into()))
            .block_on();

        let session = Arc::new(std::sync::RwLock::new(Some(session)));
        PySession { session }
    }

    pub fn new_local_client(&self) -> PyResult<crate::client::client_sync::Client> {
        let client = crate::client::client_sync::Client(AsyncClient::new_from_client(
            self.server
                .new_local_client()
                .take()
                .map_err(PyValueError::new_err)?,
        ));

        Ok(client)
    }

    pub fn poll(&self, py: Python<'_>) -> PyResult<()> {
        py.allow_threads(|| {
            self.server
                .poll()
                .block_on()
                .map_err(|e| PyValueError::new_err(format!("{}", e)))
        })
    }
}
