"""
Report generation for prompt optimization.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import csv
import io

from ..types import Experiment, AnalysisReport, TestResult


logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates comprehensive reports for prompt optimization.
    
    Features:
    - HTML report generation
    - CSV/JSON export
    - Executive summaries
    - Detailed analytics
    - Custom report templates
    """
    
    def __init__(self):
        """Initialize the report generator."""
        self.logger = logging.getLogger(__name__)
    
    def generate_experiment_report(
        self,
        experiment: Experiment,
        analysis: AnalysisReport,
        results: List[TestResult],
        format: str = "html"
    ) -> str:
        """
        Generate a comprehensive experiment report.
        
        Args:
            experiment: Experiment object
            analysis: Analysis report
            results: Test results
            format: Report format (html, json, csv)
            
        Returns:
            Generated report content
        """
        if format == "html":
            return self._generate_html_report(experiment, analysis, results)
        elif format == "json":
            return self._generate_json_report(experiment, analysis, results)
        elif format == "csv":
            return self._generate_csv_report(experiment, analysis, results)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_html_report(
        self,
        experiment: Experiment,
        analysis: AnalysisReport,
        results: List[TestResult]
    ) -> str:
        """Generate HTML report."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Experiment Report: {experiment.name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #e8f4f8; border-radius: 3px; }}
        .success {{ color: green; }}
        .warning {{ color: orange; }}
        .error {{ color: red; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Experiment Report: {experiment.name}</h1>
        <p><strong>Status:</strong> {experiment.status.value}</p>
        <p><strong>Created:</strong> {experiment.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Description:</strong> {experiment.description or 'No description'}</p>
    </div>
    
    <div class="section">
        <h2>Executive Summary</h2>
        <div class="metric">
            <strong>Total Samples:</strong> {analysis.total_samples}
        </div>
        <div class="metric">
            <strong>Confidence Level:</strong> {analysis.confidence_level:.1%}
        </div>
        <div class="metric">
            <strong>Best Variant:</strong> {analysis.best_variant or 'None'}
        </div>
        <div class="metric">
            <strong>Duration:</strong> {analysis.duration_days:.1f} days
        </div>
    </div>
    
    <div class="section">
        <h2>Variants</h2>
        <table>
            <tr>
                <th>Variant</th>
                <th>Template</th>
                <th>Version</th>
            </tr>
        """
        
        for variant in experiment.variants:
            html += f"""
            <tr>
                <td>{variant.name}</td>
                <td>{variant.template[:100]}{'...' if len(variant.template) > 100 else ''}</td>
                <td>{variant.version}</td>
            </tr>
            """
        
        html += """
        </table>
    </div>
    
    <div class="section">
        <h2>Statistical Significance</h2>
        <table>
            <tr>
                <th>Variant A</th>
                <th>Variant B</th>
                <th>P-Value</th>
                <th>Significant</th>
                <th>Effect Size</th>
            </tr>
        """
        
        for sig_result in analysis.significance_results:
            significance_class = "success" if sig_result.is_significant else "warning"
            html += f"""
            <tr>
                <td>{sig_result.variant_a}</td>
                <td>{sig_result.variant_b}</td>
                <td>{sig_result.p_value:.4f}</td>
                <td class="{significance_class}">{'Yes' if sig_result.is_significant else 'No'}</td>
                <td>{sig_result.effect_size:.3f}</td>
            </tr>
            """
        
        html += """
        </table>
    </div>
    
    <div class="section">
        <h2>Recommendations</h2>
        <ul>
        """
        
        for recommendation in analysis.recommendations:
            html += f"<li>{recommendation}</li>"
        
        html += """
        </ul>
    </div>
    
    <div class="section">
        <h2>Metrics Summary</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
        """
        
        for metric_name, metric_data in analysis.metrics_summary.items():
            if isinstance(metric_data, dict):
                for sub_metric, value in metric_data.items():
                    html += f"""
                    <tr>
                        <td>{metric_name} - {sub_metric}</td>
                        <td>{value:.4f}</td>
                    </tr>
                    """
            else:
                html += f"""
                <tr>
                    <td>{metric_name}</td>
                    <td>{metric_data}</td>
                </tr>
                """
        
        html += """
        </table>
    </div>
    
    <div class="section">
        <h2>Recent Results</h2>
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Variant</th>
                <th>Quality Score</th>
                <th>Latency (ms)</th>
                <th>Cost (USD)</th>
            </tr>
        """
        
        # Show last 10 results
        recent_results = sorted(results, key=lambda r: r.timestamp, reverse=True)[:10]
        for result in recent_results:
            html += f"""
            <tr>
                <td>{result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</td>
                <td>{result.variant_name}</td>
                <td>{result.quality_score:.3f if result.quality_score else 'N/A'}</td>
                <td>{result.latency_ms:.1f}</td>
                <td>${result.cost_usd:.4f}</td>
            </tr>
            """
        
        html += """
        </table>
    </div>
    
    <div class="section">
        <p><em>Report generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
    </div>
</body>
</html>
        """
        
        return html
    
    def _generate_json_report(
        self,
        experiment: Experiment,
        analysis: AnalysisReport,
        results: List[TestResult]
    ) -> str:
        """Generate JSON report."""
        report_data = {
            "experiment": {
                "id": experiment.id,
                "name": experiment.name,
                "description": experiment.description,
                "status": experiment.status.value,
                "created_at": experiment.created_at.isoformat(),
                "started_at": experiment.started_at.isoformat() if experiment.started_at else None,
                "completed_at": experiment.completed_at.isoformat() if experiment.completed_at else None,
                "variants": [
                    {
                        "name": v.name,
                        "template": v.template,
                        "version": v.version,
                        "parameters": v.parameters,
                        "metadata": v.metadata
                    }
                    for v in experiment.variants
                ],
                "config": {
                    "traffic_split": experiment.config.traffic_split,
                    "min_sample_size": experiment.config.min_sample_size,
                    "significance_level": experiment.config.significance_level,
                    "max_duration_days": experiment.config.max_duration_days,
                    "provider": experiment.config.provider.value,
                    "model": experiment.config.model
                }
            },
            "analysis": {
                "best_variant": analysis.best_variant,
                "confidence_level": analysis.confidence_level,
                "total_samples": analysis.total_samples,
                "duration_days": analysis.duration_days,
                "significance_results": [
                    {
                        "variant_a": sr.variant_a,
                        "variant_b": sr.variant_b,
                        "is_significant": sr.is_significant,
                        "p_value": sr.p_value,
                        "confidence_interval": sr.confidence_interval,
                        "effect_size": sr.effect_size,
                        "power": sr.power,
                        "sample_size": sr.sample_size
                    }
                    for sr in analysis.significance_results
                ],
                "metrics_summary": analysis.metrics_summary,
                "recommendations": analysis.recommendations
            },
            "results_summary": {
                "total_results": len(results),
                "quality_scores": {
                    "avg": sum(r.quality_score for r in results if r.quality_score) / len([r for r in results if r.quality_score]) if any(r.quality_score for r in results) else 0,
                    "min": min((r.quality_score for r in results if r.quality_score), default=0),
                    "max": max((r.quality_score for r in results if r.quality_score), default=0)
                },
                "latency": {
                    "avg": sum(r.latency_ms for r in results) / len(results),
                    "min": min(r.latency_ms for r in results),
                    "max": max(r.latency_ms for r in results)
                },
                "cost": {
                    "total": sum(r.cost_usd for r in results),
                    "avg": sum(r.cost_usd for r in results) / len(results)
                },
                "tokens": {
                    "total": sum(r.tokens_used for r in results),
                    "avg": sum(r.tokens_used for r in results) / len(results)
                }
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return json.dumps(report_data, indent=2)
    
    def _generate_csv_report(
        self,
        experiment: Experiment,
        analysis: AnalysisReport,
        results: List[TestResult]
    ) -> str:
        """Generate CSV report."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write experiment info
        writer.writerow(["Experiment Information"])
        writer.writerow(["ID", experiment.id])
        writer.writerow(["Name", experiment.name])
        writer.writerow(["Status", experiment.status.value])
        writer.writerow(["Created", experiment.created_at.isoformat()])
        writer.writerow([])
        
        # Write analysis summary
        writer.writerow(["Analysis Summary"])
        writer.writerow(["Best Variant", analysis.best_variant or "None"])
        writer.writerow(["Confidence Level", f"{analysis.confidence_level:.1%}"])
        writer.writerow(["Total Samples", analysis.total_samples])
        writer.writerow(["Duration (days)", f"{analysis.duration_days:.1f}"])
        writer.writerow([])
        
        # Write significance results
        writer.writerow(["Statistical Significance"])
        writer.writerow(["Variant A", "Variant B", "P-Value", "Significant", "Effect Size"])
        for sig_result in analysis.significance_results:
            writer.writerow([
                sig_result.variant_a,
                sig_result.variant_b,
                f"{sig_result.p_value:.4f}",
                "Yes" if sig_result.is_significant else "No",
                f"{sig_result.effect_size:.3f}"
            ])
        writer.writerow([])
        
        # Write recommendations
        writer.writerow(["Recommendations"])
        for recommendation in analysis.recommendations:
            writer.writerow([recommendation])
        writer.writerow([])
        
        # Write results data
        writer.writerow(["Results Data"])
        writer.writerow([
            "Timestamp", "Variant", "User ID", "Quality Score", 
            "Latency (ms)", "Cost (USD)", "Tokens Used"
        ])
        for result in results:
            writer.writerow([
                result.timestamp.isoformat(),
                result.variant_name,
                result.user_id,
                f"{result.quality_score:.3f}" if result.quality_score else "N/A",
                f"{result.latency_ms:.1f}",
                f"{result.cost_usd:.4f}",
                result.tokens_used
            ])
        
        return output.getvalue()
    
    def generate_executive_summary(
        self,
        experiment: Experiment,
        analysis: AnalysisReport
    ) -> str:
        """
        Generate an executive summary.
        
        Args:
            experiment: Experiment object
            analysis: Analysis report
            
        Returns:
            Executive summary text
        """
        summary = f"""
EXECUTIVE SUMMARY
================

Experiment: {experiment.name}
Status: {experiment.status.value}
Duration: {analysis.duration_days:.1f} days
Total Samples: {analysis.total_samples}

KEY FINDINGS:
- Best performing variant: {analysis.best_variant or 'None identified'}
- Confidence level: {analysis.confidence_level:.1%}
- Number of significant comparisons: {len([sr for sr in analysis.significance_results if sr.is_significant])}

RECOMMENDATIONS:
"""
        
        for i, recommendation in enumerate(analysis.recommendations, 1):
            summary += f"{i}. {recommendation}\n"
        
        if not analysis.recommendations:
            summary += "No specific recommendations at this time.\n"
        
        summary += f"\nReport generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return summary 