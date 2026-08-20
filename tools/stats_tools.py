import re
from typing import Dict, Any, List


def extract_statistical_claims(text: str) -> Dict[str, Any]:
    """Extract p-values, sample sizes, confidence intervals, and effect sizes using regex."""
    p_values = re.findall(r"(?i)p\s*([<>=]\s*0?\.\d+|\b=\s*0?\.\d+)", text)
    sample_sizes = re.findall(r"(?i)(?:sample size|n\s*=)\s*(\d+)", text)
    confidence_intervals = re.findall(r"(?i)(?:95%\s*CI|confidence interval|CI)\s*[:=\[]?\s*([-+]?\d*\.?\d+\s*,\s*[-+]?\d*\.?\d+)", text)
    effect_sizes = re.findall(r"(?i)(?:Cohen's d|d\s*=|R^2|r\s*=|eta^2)\s*=\s*([-+]?\d*\.?\d+)", text)
    
    # Check for variance / error bars mentioned
    has_error_bars = bool(re.search(r"(?i)(standard deviation|std dev|variance|error bar|±|\+/-)", text))
    has_significance_test = bool(re.search(r"(?i)(t-test|anova|wilcoxon|chi-square|p-value|statistically significant)", text))
    
    return {
        "p_values": p_values,
        "sample_sizes": [int(s) for s in sample_sizes],
        "confidence_intervals": confidence_intervals,
        "effect_sizes": effect_sizes,
        "has_error_bars": has_error_bars,
        "has_significance_test": has_significance_test
    }


def run_statistical_checks(extracted_stats: Dict[str, Any]) -> List[str]:
    """Apply rule-based statistical sanity checks as defined in spec."""
    flags = []
    
    # Flag n < 30
    small_samples = [n for n in extracted_stats.get("sample_sizes", []) if n < 30]
    if small_samples:
        flags.append(f"FLAG: Small sample size detected (n = {small_samples}). Statistical power may be underpowered.")

    # Flag p-values reported without effect sizes
    if extracted_stats.get("p_values") and not extracted_stats.get("effect_sizes"):
        flags.append("FLAG: p-values reported without effect size metrics (e.g. Cohen's d or R^2).")

    # Missing statistical significance test
    if not extracted_stats.get("has_significance_test"):
        flags.append("FLAG: No explicit statistical significance testing (e.g., t-test, ANOVA) detected in claims.")

    # Missing error bars or variance
    if not extracted_stats.get("has_error_bars"):
        flags.append("FLAG: Single-run or point-estimate results reported without variance, standard deviation, or error bars.")

    return flags
