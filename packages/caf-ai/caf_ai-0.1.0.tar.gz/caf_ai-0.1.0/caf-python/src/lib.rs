use caf_core::{DetectionMatch as CoreDetectionMatch, DetectionResult as CoreDetectionResult, RiskLevel as CoreRiskLevel};
use caf_sdk::CAFDetector as CoreCAFDetector;
use pyo3::prelude::*;
use std::collections::HashMap;
use tokio::runtime::Runtime;

#[pyclass]
#[derive(Clone)]
pub struct RiskLevel {
    inner: CoreRiskLevel,
}

#[pymethods]
impl RiskLevel {
    #[classattr]
    const LOW: &'static str = "LOW";
    #[classattr]
    const MEDIUM: &'static str = "MEDIUM";
    #[classattr]
    const HIGH: &'static str = "HIGH";
    #[classattr]
    const CRITICAL: &'static str = "CRITICAL";

    #[getter]
    fn value(&self) -> String {
        match self.inner {
            CoreRiskLevel::Low => "LOW".to_string(),
            CoreRiskLevel::Medium => "MEDIUM".to_string(),
            CoreRiskLevel::High => "HIGH".to_string(),
            CoreRiskLevel::Critical => "CRITICAL".to_string(),
        }
    }

    fn __str__(&self) -> String {
        self.value()
    }

    fn __repr__(&self) -> String {
        format!("RiskLevel.{}", self.value())
    }

    fn __eq__(&self, other: &Self) -> bool {
        self.inner == other.inner
    }

    fn __hash__(&self) -> u64 {
        self.inner as u64
    }
}

impl From<CoreRiskLevel> for RiskLevel {
    fn from(risk: CoreRiskLevel) -> Self {
        Self { inner: risk }
    }
}

#[pyclass]
#[derive(Clone)]
pub struct DetectionMatch {
    #[pyo3(get)]
    pub pattern_name: String,
    #[pyo3(get)]
    pub pattern_type: String,
    #[pyo3(get)]
    pub matched_text: String,
    #[pyo3(get)]
    pub position: (usize, usize),
    #[pyo3(get)]
    pub confidence: f32,
}

#[pymethods]
impl DetectionMatch {
    fn __str__(&self) -> String {
        format!(
            "DetectionMatch(pattern_type='{}', pattern_name='{}', confidence={:.2})",
            self.pattern_type, self.pattern_name, self.confidence
        )
    }

    fn __repr__(&self) -> String {
        self.__str__()
    }

    fn to_dict(&self) -> HashMap<String, PyObject> {
        Python::with_gil(|py| {
            let mut dict = HashMap::new();
            dict.insert("pattern_name".to_string(), self.pattern_name.clone().into_py(py));
            dict.insert("pattern_type".to_string(), self.pattern_type.clone().into_py(py));
            dict.insert("matched_text".to_string(), self.matched_text.clone().into_py(py));
            dict.insert("position".to_string(), self.position.into_py(py));
            dict.insert("confidence".to_string(), self.confidence.into_py(py));
            dict
        })
    }
}

impl From<CoreDetectionMatch> for DetectionMatch {
    fn from(m: CoreDetectionMatch) -> Self {
        Self {
            pattern_name: m.pattern_name,
            pattern_type: m.pattern_type,
            matched_text: m.matched_text,
            position: m.position,
            confidence: m.confidence,
        }
    }
}

#[pyclass]
#[derive(Clone)]
pub struct DetectionResult {
    #[pyo3(get)]
    pub risk_level: RiskLevel,
    #[pyo3(get)]
    pub confidence: f32,
    #[pyo3(get)]
    pub matches: Vec<DetectionMatch>,
    #[pyo3(get)]
    pub processing_time_ms: f32,
    #[pyo3(get)]
    pub detector_name: String,
}

#[pymethods]
impl DetectionResult {
    #[getter]
    fn risk(&self) -> RiskLevel {
        self.risk_level.clone()
    }

    #[getter]
    fn matched_patterns(&self) -> Vec<String> {
        self.matches.iter().map(|m| m.pattern_type.clone()).collect()
    }

    #[getter]
    fn reason(&self) -> String {
        if self.matches.is_empty() {
            "No threats detected".to_string()
        } else {
            let patterns: Vec<String> = self.matches.iter().map(|m| m.pattern_type.clone()).collect();
            format!("Detected: {}", patterns.join(", "))
        }
    }

    fn __str__(&self) -> String {
        format!(
            "DetectionResult(risk={}, confidence={:.2}, matches={})",
            self.risk_level.value(),
            self.confidence,
            self.matches.len()
        )
    }

    fn __repr__(&self) -> String {
        self.__str__()
    }

    fn to_dict(&self) -> HashMap<String, PyObject> {
        Python::with_gil(|py| {
            let mut dict = HashMap::new();
            dict.insert("risk_level".to_string(), self.risk_level.value().into_py(py));
            dict.insert("confidence".to_string(), self.confidence.into_py(py));
            dict.insert("matches".to_string(), 
                self.matches.iter().map(|m| m.to_dict()).collect::<Vec<_>>().into_py(py));
            dict.insert("processing_time_ms".to_string(), self.processing_time_ms.into_py(py));
            dict.insert("detector_name".to_string(), self.detector_name.clone().into_py(py));
            dict.insert("reason".to_string(), self.reason().into_py(py));
            dict.insert("matched_patterns".to_string(), self.matched_patterns().into_py(py));
            dict
        })
    }
}

impl From<CoreDetectionResult> for DetectionResult {
    fn from(result: CoreDetectionResult) -> Self {
        Self {
            risk_level: result.risk_level.into(),
            confidence: result.confidence,
            matches: result.matches.into_iter().map(|m| m.into()).collect(),
            processing_time_ms: result.processing_time_ms,
            detector_name: result.detector_name,
        }
    }
}

#[pyclass]
pub struct AnalysisResult {
    #[pyo3(get)]
    pub overall_risk: RiskLevel,
    #[pyo3(get)]
    pub overall_confidence: f32,
    pub detector_results: Vec<DetectionResult>,
    #[pyo3(get)]
    pub total_processing_time_ms: f32,
}

#[pymethods]
impl AnalysisResult {
    #[getter]
    fn risk(&self) -> RiskLevel {
        self.overall_risk.clone()
    }

    #[getter]
    fn confidence(&self) -> f32 {
        self.overall_confidence
    }

    #[getter]
    fn reason(&self) -> String {
        if self.detector_results.is_empty() {
            "No threats detected".to_string()
        } else {
            let mut patterns = Vec::new();
            for result in &self.detector_results {
                for pattern_match in &result.matches {
                    if !patterns.contains(&pattern_match.pattern_type) {
                        patterns.push(pattern_match.pattern_type.clone());
                    }
                }
            }
            if patterns.is_empty() {
                "No threats detected".to_string()
            } else {
                format!("Detected: {}", patterns.join(", "))
            }
        }
    }

    #[getter]
    fn matched_detectors(&self) -> Vec<String> {
        self.detector_results.iter()
            .filter(|r| !r.matches.is_empty())
            .map(|r| r.detector_name.clone())
            .collect()
    }

    #[getter]
    fn detector_results(&self) -> Vec<DetectionResult> {
        self.detector_results.clone()
    }

    fn __str__(&self) -> String {
        format!(
            "AnalysisResult(risk={}, confidence={:.2}, detectors={})",
            self.overall_risk.value(),
            self.overall_confidence,
            self.detector_results.len()
        )
    }

    fn __repr__(&self) -> String {
        self.__str__()
    }
}

impl From<caf_core::AnalysisResult> for AnalysisResult {
    fn from(result: caf_core::AnalysisResult) -> Self {
        Self {
            overall_risk: result.overall_risk.into(),
            overall_confidence: result.overall_confidence,
            detector_results: result.detector_results.into_iter().map(|r| r.into()).collect(),
            total_processing_time_ms: result.total_processing_time_ms,
        }
    }
}

#[pyclass]
pub struct CAFDetector {
    detector: CoreCAFDetector,
    runtime: Runtime,
}

#[pymethods]
impl CAFDetector {
    #[new]
    pub fn new() -> PyResult<Self> {
        let runtime = Runtime::new()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                format!("Failed to create async runtime: {}", e)
            ))?;
        
        Ok(Self {
            detector: CoreCAFDetector::new(),
            runtime,
        })
    }

    pub fn analyze(&self, text: &str) -> PyResult<AnalysisResult> {
        self.runtime.block_on(async {
            self.detector
                .analyze(text)
                .await
                .map(|result| result.into())
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    format!("Analysis failed: {}", e)
                ))
        })
    }

    pub fn analyze_sync(&self, text: &str) -> PyResult<AnalysisResult> {
        self.analyze(text)
    }

    #[getter]
    pub fn version(&self) -> String {
        env!("CARGO_PKG_VERSION").to_string()
    }

    #[getter]
    pub fn name(&self) -> String {
        "CAF-AI Detector".to_string()
    }

    pub fn __str__(&self) -> String {
        format!("CAFDetector(version={})", self.version())
    }

    pub fn __repr__(&self) -> String {
        self.__str__()
    }
}

// Module creation function
#[pymodule]
fn _internal(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<CAFDetector>()?;
    m.add_class::<DetectionResult>()?;
    m.add_class::<DetectionMatch>()?;
    m.add_class::<AnalysisResult>()?;
    m.add_class::<RiskLevel>()?;
    
    // Add version info
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add("__author__", "CAF-AI Contributors")?;
    
    Ok(())
}