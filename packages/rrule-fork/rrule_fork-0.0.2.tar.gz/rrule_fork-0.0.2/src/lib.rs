use std::panic;
use ::rrule::Tz;
use chrono::{DateTime, Datelike, TimeZone, Timelike};
use pyo3::{
    prelude::*,
    types::{PyDateAccess, PyDateTime, PyList, PyTimeAccess, PyTzInfoAccess},
};

#[pyclass]
struct RRuleSet(::rrule::RRuleSet);

#[pymethods]
impl RRuleSet {
    pub fn between<'py>(
        &self,
        py: Python<'py>,
        start: &Bound<'py, PyDateTime>,
        end: &Bound<'py, PyDateTime>,
        limit: u16,
    ) -> Bound<'py, PyList> {
        let start = pydatetime_to_chrono(start).unwrap();
        let end = pydatetime_to_chrono(end).unwrap();

        let result = self.0.clone().after(start).before(end).all(limit).dates;

        PyList::new_bound(
            py,
            result
                .into_iter()
                .map(|datetime| chrono_to_pydatetime(py, datetime)),
        )
    }
}

fn chrono_to_pydatetime<'py>(py: Python<'py>, datetime: DateTime<Tz>) -> Bound<'_, PyDateTime> {
    let info;
    let tzinfo = match &datetime.timezone() {
        Tz::Local(_) => None,
        Tz::Tz(tz) => {
            info = tz.to_object(py);
            Some(info.downcast_bound(py).unwrap())
        }
    };

    PyDateTime::new_bound(
        py,
        datetime.year(),
        datetime.month() as u8,
        datetime.day() as u8,
        datetime.hour() as u8,
        datetime.minute() as u8,
        datetime.second() as u8,
        0,
        tzinfo,
    )
    .unwrap()
}

fn pydatetime_to_chrono(pydatetime: &Bound<'_, PyDateTime>) -> PyResult<DateTime<Tz>> {
    let tz = match pydatetime.get_tzinfo_bound() {
        Some(tzinfo) => Tz::Tz(tzinfo.extract()?),
        None => Tz::LOCAL,
    };

    let result = tz
        .with_ymd_and_hms(
            pydatetime.get_year(),
            pydatetime.get_month() as u32,
            pydatetime.get_day() as u32,
            pydatetime.get_hour() as u32,
            pydatetime.get_minute() as u32,
            pydatetime.get_second() as u32,
        )
        .earliest()
        .unwrap();

    Ok(result)
}

#[pyfunction]
fn build_rruleset(dtstart: &Bound<'_, PyDateTime>, lines: Vec<String>) -> Option<RRuleSet> {
    let start = pydatetime_to_chrono(dtstart).unwrap();

    let result = panic::catch_unwind(|| {
        let mut rruleset = ::rrule::RRuleSet::new(start);
        rruleset = rruleset.set_from_string(&lines.join("\n")).unwrap();
        Some(RRuleSet(rruleset))
    });
    result.unwrap_or(None)
}

#[pymodule]
fn rrule(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<RRuleSet>()?;
    m.add_function(wrap_pyfunction!(build_rruleset, m)?)?;
    Ok(())
}
