use std::{
    convert::Infallible,
    sync::{atomic::AtomicBool, Arc},
};

use meocap_driver::{
    host::{LoggerListener, MeoHost},
    MeoDriver, TrackerReport,
};
use nusb::MaybeFuture;
use protocol::TrackerIndex;
use pyo3::{exceptions::PyTypeError, prelude::*};
use tokio::sync::{Mutex, RwLock};
use trackers::TrackerGroup;

const MEOCAP_PID_VID: (u16, u16) = (0x81d3, 0x303a);

#[pyclass]
pub struct Meocap {
    device: Arc<Mutex<Device>>,
    group: Arc<RwLock<Option<TrackerGroup<MeoDriver>>>>,
    host: Arc<MeoHost>,
}

fn points_parser(value: &str) -> Result<Box<[TrackerIndex]>, Infallible> {
    Ok(value.split(",").map(|p| point_to_idx(p.trim())).collect())
}

fn point_to_idx(s: &str) -> TrackerIndex {
    match s {
        "LH" => TrackerIndex::LeftHand,
        "RH" => TrackerIndex::RightHand,
        "LF" => TrackerIndex::LeftFoot,
        "RF" => TrackerIndex::RightFoot,
        "LLA" => TrackerIndex::LeftLowerArm,
        "RLA" => TrackerIndex::RightLowerArm,
        "LUA" => TrackerIndex::LeftUpperArm,
        "RUA" => TrackerIndex::RightUpperArm,
        "LLL" => TrackerIndex::LeftLowerLeg,
        "RLL" => TrackerIndex::RightLowerLeg,
        "LUL" => TrackerIndex::LeftUpperLeg,
        "RUL" => TrackerIndex::RightUpperLeg,
        "CH" => TrackerIndex::Chest,
        "HE" => TrackerIndex::Head,
        "HI" => TrackerIndex::Hips,
        _ => panic!("Unexpected point expression"),
    }
}

#[pymethods]
impl Meocap {
    #[new]
    pub fn new() -> PyResult<Self> {
        let mut device_list = nusb::list_devices().wait()?;
        let device = device_list
            .find(|d| d.vendor_id() == MEOCAP_PID_VID.1 && d.product_id() == MEOCAP_PID_VID.0)
            .ok_or(PyErr::new::<pyo3::exceptions::PyIOError, _>(
                "Receiver not found",
            ))?;
        let device = device.open().wait()?;

        let connected = Arc::new(AtomicBool::new(false));
        pyo3_async_runtimes::tokio::get_runtime().block_on(async move {
            Ok(Self {
                device: Arc::new(Mutex::new(Device::NotConnected)),
                host: Arc::new(MeoHost::new(device, Arc::new(LoggerListener), connected)
                    .await
                    .unwrap(),
                ),
                group: Arc::new(RwLock::new(None))
            })
        })
    }

    pub fn status(&self) -> PyResult<String> {
        let device = self.device.blocking_lock();
        Ok(match &*device {
            Device::NotConnected => "not connected",
            Device::Connected => "connected",
            Device::Reporting => "reporting data",
        }
        .to_owned())
    }

    /// This function will automatically connected to a recognized receiver.
    pub fn connect<'a>(slf: PyRef<'a, Self>, group: &'a str) -> PyResult<Bound<'a, PyAny>> {
        let host = slf.host.clone();
        let device = slf.device.clone();
        let tg = slf.group.clone();
        let py = slf.py();

        let group = points_parser(group).unwrap();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            match host.connect_trackers(group.as_ref()).await {
                Ok(g) => {
                    *device.lock().await = Device::Connected;
                    *tg.write().await = Some(g);
                    Ok(())
                }
                Err(e) => Err(PyTypeError::new_err(e.to_string())),
            }
        })
    }

    /// Start data collecting, you can only invoke this function when connected.
    pub fn start(slf: PyRef<'_, Self>) -> PyResult<Bound<'_, PyAny>> {
        let host = slf.host.clone();
        let device = slf.device.clone();
        pyo3_async_runtimes::tokio::future_into_py(slf.py(), async move {
            match host.start_trackers().await {
                Ok(_) => {
                    *device.lock().await = Device::Reporting;
                    Ok(())
                }
                Err(e) => Err(PyTypeError::new_err(e.to_string())),
            }
        })
    }

    /// Poll one frame from the sensor report buffer, you can only call this function after
    /// data collection is started
    pub fn poll(&self) -> PyResult<Vec<(Report, bool)>> {
        let mut device = self.device.blocking_lock();
        let lock = self.group.blocking_read();
        let g = match &mut *device {
            Device::Connected => return Err(PyTypeError::new_err("Device not started.")),
            Device::NotConnected => return Err(PyTypeError::new_err("Device not connected.")),
            Device::Reporting => lock.as_ref().unwrap(),
        };

        Ok(g.poll()
            .ok_or(PyTypeError::new_err("Error polling the last frame"))?
            .into_iter()
            .map(|w| (Report::from(w.0), w.1))
            .collect())
    }
}

#[pyclass(get_all)]
#[derive(Debug)]
pub struct Report {
    acc: (f32, f32, f32),
    rot: (f32, f32, f32, f32),
    #[cfg(feature = "raw")]
    raw_acc: (f32, f32, f32),
    #[cfg(feature = "raw")]
    gyro: (f32, f32, f32),
    #[cfg(feature = "raw")]
    mag: (f32, f32, f32),
    accuracy: u8,
    location: String,
}

impl From<TrackerReport> for Report {
    fn from(value: TrackerReport) -> Self {
        Self {
            acc: (value.acc.x, value.acc.y, value.acc.z),
            rot: (
                value.rot_9axis.w,
                value.rot_9axis.i,
                value.rot_9axis.j,
                value.rot_9axis.k,
            ),
            accuracy: value.accuracy as u8,
            #[cfg(feature = "raw")]
            raw_acc: (value.raw_acc.x, value.raw_acc.y, value.raw_acc.z),
            #[cfg(feature = "raw")]
            mag: (value.mag.x, value.mag.y, value.mag.z),
            #[cfg(feature = "raw")]
            gyro: (value.gyro.x, value.gyro.y, value.gyro.z),
            location: format!("{:?}", value.location),
        }
    }
}

#[pymethods]
impl Report {
    pub fn __repr__(&self) -> PyResult<String> {
        Ok(format!("{:?}", self))
    }
}

pub enum Device {
    NotConnected,
    Connected,
    Reporting,
}

/// Enable logging for underlying driver. Available levels are "info", "debug" and "error"
#[pyfunction]
pub fn enable_log(level: &str) -> PyResult<()> {
    let level = match level.to_ascii_lowercase().as_str() {
        "debug" => log::Level::Debug,
        "info" => log::Level::Info,
        "error" => log::Level::Error,
        _ => return Err(PyTypeError::new_err("incorrect level param")),
    };

    simple_logger::init_with_level(level).expect("Do not set log multiple times");
    Ok(())
}

/// A Python module implemented in Rust.
#[pymodule]
fn pymeocap(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Meocap>()?;
    m.add_function(wrap_pyfunction!(enable_log, m)?)?;
    Ok(())
}
