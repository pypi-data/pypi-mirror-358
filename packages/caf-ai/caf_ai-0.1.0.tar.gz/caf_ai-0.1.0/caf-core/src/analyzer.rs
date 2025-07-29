use crate::{
    AggregateStrategy, AnalysisResult, AnalyzerConfig, AnalyzerError,
    Detector, DetectionResult, RiskLevel,
};
use std::time::Instant;

pub struct Analyzer {
    detectors: Vec<Box<dyn Detector>>,
    config: AnalyzerConfig,
}

impl Analyzer {
    pub fn new(detectors: Vec<Box<dyn Detector>>, config: AnalyzerConfig) -> Self {
        Self { detectors, config }
    }

    pub async fn analyze(&self, input: &str) -> Result<AnalysisResult, AnalyzerError> {
        let start = Instant::now();
        let mut detector_results = Vec::new();

        if self.config.parallel_execution {
            // Implementation would go here for parallel execution
            // For now, we'll use sequential execution
        }

        // Sequential execution
        for detector in &self.detectors {
            // For now, just call detect directly without timeout
            // Timeout functionality would require tokio in caf-core
            match detector.detect(input).await {
                Ok(result) => detector_results.push(result),
                Err(_) => continue, // Skip failed detector
            }
        }

        if detector_results.is_empty() {
            return Err(AnalyzerError::AllDetectorsFailed);
        }

        // Aggregate results based on strategy
        let (overall_risk, overall_confidence) = match self.config.aggregate_strategy {
            AggregateStrategy::MaxRisk => self.aggregate_max_risk(&detector_results),
            AggregateStrategy::Weighted => self.aggregate_weighted(&detector_results),
            AggregateStrategy::Unanimous => self.aggregate_unanimous(&detector_results),
        };

        let total_processing_time_ms = start.elapsed().as_secs_f32() * 1000.0;

        Ok(AnalysisResult {
            overall_risk,
            overall_confidence,
            detector_results,
            total_processing_time_ms,
        })
    }

    fn aggregate_max_risk(&self, results: &[DetectionResult]) -> (RiskLevel, f32) {
        let mut max_risk = RiskLevel::Low;
        let mut max_confidence = 0.0;

        for result in results {
            if result.risk_level as u8 > max_risk as u8 {
                max_risk = result.risk_level;
                max_confidence = result.confidence;
            }
        }

        (max_risk, max_confidence)
    }

    fn aggregate_weighted(&self, results: &[DetectionResult]) -> (RiskLevel, f32) {
        // Weighted aggregation implementation
        self.aggregate_max_risk(results) // Simplified for now
    }

    fn aggregate_unanimous(&self, results: &[DetectionResult]) -> (RiskLevel, f32) {
        // Unanimous aggregation implementation
        self.aggregate_max_risk(results) // Simplified for now
    }
}