use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use std::fmt;
use thiserror::Error;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum RiskLevel {
    Low,
    Medium,
    High,
    Critical,
}

impl fmt::Display for RiskLevel {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            RiskLevel::Low => write!(f, "LOW"),
            RiskLevel::Medium => write!(f, "MEDIUM"),
            RiskLevel::High => write!(f, "HIGH"),
            RiskLevel::Critical => write!(f, "CRITICAL"),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DetectionMatch {
    pub pattern_name: String,
    pub pattern_type: String,
    pub matched_text: String,
    pub position: (usize, usize),
    pub confidence: f32,
}

impl DetectionMatch {
    pub fn new(
        pattern_name: impl Into<String>,
        pattern_type: impl Into<String>,
        matched_text: impl Into<String>,
        position: (usize, usize),
        confidence: f32,
    ) -> Self {
        Self {
            pattern_name: pattern_name.into(),
            pattern_type: pattern_type.into(),
            matched_text: matched_text.into(),
            position,
            confidence,
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DetectionResult {
    pub risk_level: RiskLevel,
    pub confidence: f32,
    pub matches: Vec<DetectionMatch>,
    pub processing_time_ms: f32,
    pub detector_name: String,
}

impl DetectionResult {
    pub fn new(detector_name: impl Into<String>) -> Self {
        Self {
            risk_level: RiskLevel::Low,
            confidence: 0.0,
            matches: Vec::new(),
            processing_time_ms: 0.0,
            detector_name: detector_name.into(),
        }
    }

    pub fn with_risk_level(mut self, risk_level: RiskLevel) -> Self {
        self.risk_level = risk_level;
        self
    }

    pub fn with_confidence(mut self, confidence: f32) -> Self {
        self.confidence = confidence;
        self
    }

    pub fn with_match(mut self, detection_match: DetectionMatch) -> Self {
        self.matches.push(detection_match);
        self
    }

    pub fn with_processing_time(mut self, time_ms: f32) -> Self {
        self.processing_time_ms = time_ms;
        self
    }
}

#[async_trait]
pub trait Detector: Send + Sync {
    fn name(&self) -> &'static str;
    fn version(&self) -> &'static str;
    async fn detect(&self, input: &str) -> Result<DetectionResult, DetectorError>;
    fn risk_threshold(&self) -> f32 {
        0.7
    }
}

#[derive(Debug, Error)]
pub enum DetectorError {
    #[error("Detection timeout exceeded")]
    Timeout,
    #[error("Invalid input: {0}")]
    InvalidInput(String),
    #[error("Internal error: {0}")]
    Internal(String),
}

// Analyzer types
#[derive(Debug, Clone)]
pub struct AnalyzerConfig {
    pub parallel_execution: bool,
    pub timeout_ms: u64,
    pub aggregate_strategy: AggregateStrategy,
}

impl Default for AnalyzerConfig {
    fn default() -> Self {
        Self {
            parallel_execution: true,
            timeout_ms: 5000,
            aggregate_strategy: AggregateStrategy::MaxRisk,
        }
    }
}

#[derive(Debug, Clone, Copy)]
pub enum AggregateStrategy {
    MaxRisk,
    Weighted,
    Unanimous,
}

#[derive(Debug)]
pub struct AnalysisResult {
    pub overall_risk: RiskLevel,
    pub overall_confidence: f32,
    pub detector_results: Vec<DetectionResult>,
    pub total_processing_time_ms: f32,
}

#[derive(Debug, Error)]
pub enum AnalyzerError {
    #[error("Analysis timeout exceeded")]
    Timeout,
    #[error("All detectors failed")]
    AllDetectorsFailed,
    #[error("Configuration error: {0}")]
    ConfigError(String),
}

pub mod analyzer;
pub use analyzer::Analyzer;