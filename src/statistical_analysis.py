import numpy as np
from scipy import stats
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')


class StatisticalAnalyzer:

    @staticmethod
    def compute_confidence_interval(
        data: List[float],
        confidence_level: float = 0.95
    ) -> Tuple[float, float, float]:
        data_array = np.array(data)
        n = len(data_array)

        if n == 0:
            return 0.0, 0.0, 0.0

        mean = np.mean(data_array)

        if n == 1:
            return mean, mean, mean

        std_err = stats.sem(data_array)

        ci = std_err * stats.t.ppf((1 + confidence_level) / 2, n - 1)

        return mean, mean - ci, mean + ci

    @staticmethod
    def perform_t_test(
        sample1: List[float],
        sample2: List[float],
        paired: bool = False
    ) -> Dict[str, float]:
        if paired:
            statistic, p_value = stats.ttest_rel(sample1, sample2)
        else:
            statistic, p_value = stats.ttest_ind(sample1, sample2)

        mean1 = np.mean(sample1)
        mean2 = np.mean(sample2)

        effect_size = (mean1 - mean2) / np.sqrt((np.var(sample1) + np.var(sample2)) / 2)

        return {
            't_statistic': statistic,
            'p_value': p_value,
            'significant_at_0.05': p_value < 0.05,
            'significant_at_0.01': p_value < 0.01,
            'effect_size_cohens_d': effect_size,
            'mean_difference': mean1 - mean2,
            'mean_sample1': mean1,
            'mean_sample2': mean2
        }

    @staticmethod
    def perform_anova(
        samples: List[List[float]],
        labels: List[str] = None
    ) -> Dict:
        f_statistic, p_value = stats.f_oneway(*samples)

        grand_mean = np.mean([val for sample in samples for val in sample])

        ss_between = sum(
            len(sample) * (np.mean(sample) - grand_mean) ** 2
            for sample in samples
        )

        ss_within = sum(
            sum((val - np.mean(sample)) ** 2 for val in sample)
            for sample in samples
        )

        ss_total = ss_between + ss_within

        eta_squared = ss_between / ss_total if ss_total > 0 else 0

        results = {
            'f_statistic': f_statistic,
            'p_value': p_value,
            'significant_at_0.05': p_value < 0.05,
            'significant_at_0.01': p_value < 0.01,
            'eta_squared': eta_squared,
            'num_groups': len(samples),
            'total_samples': sum(len(s) for s in samples)
        }

        if labels:
            results['group_means'] = {
                label: np.mean(sample)
                for label, sample in zip(labels, samples)
            }
            results['group_stds'] = {
                label: np.std(sample)
                for label, sample in zip(labels, samples)
            }

        return results

    @staticmethod
    def compute_descriptive_statistics(data: List[float]) -> Dict[str, float]:
        data_array = np.array(data)

        if len(data_array) == 0:
            return {
                'count': 0,
                'mean': 0.0,
                'std': 0.0,
                'min': 0.0,
                'max': 0.0,
                'median': 0.0,
                'q1': 0.0,
                'q3': 0.0,
                'iqr': 0.0,
                'skewness': 0.0,
                'kurtosis': 0.0
            }

        return {
            'count': len(data_array),
            'mean': float(np.mean(data_array)),
            'std': float(np.std(data_array)),
            'min': float(np.min(data_array)),
            'max': float(np.max(data_array)),
            'median': float(np.median(data_array)),
            'q1': float(np.percentile(data_array, 25)),
            'q3': float(np.percentile(data_array, 75)),
            'iqr': float(np.percentile(data_array, 75) - np.percentile(data_array, 25)),
            'skewness': float(stats.skew(data_array)),
            'kurtosis': float(stats.kurtosis(data_array))
        }

    @staticmethod
    def compute_improvement_percentage(
        baseline: float,
        improved: float,
        higher_is_better: bool = True
    ) -> float:
        if baseline == 0:
            return 0.0

        if higher_is_better:
            return ((improved - baseline) / baseline) * 100
        else:
            return ((baseline - improved) / baseline) * 100

    @staticmethod
    def perform_wilcoxon_test(
        sample1: List[float],
        sample2: List[float]
    ) -> Dict[str, float]:
        statistic, p_value = stats.wilcoxon(sample1, sample2)

        median1 = np.median(sample1)
        median2 = np.median(sample2)

        return {
            'w_statistic': statistic,
            'p_value': p_value,
            'significant_at_0.05': p_value < 0.05,
            'significant_at_0.01': p_value < 0.01,
            'median_sample1': median1,
            'median_sample2': median2,
            'median_difference': median1 - median2
        }

    @staticmethod
    def compute_correlation(
        x: List[float],
        y: List[float],
        method: str = 'pearson'
    ) -> Dict[str, float]:
        if method == 'pearson':
            correlation, p_value = stats.pearsonr(x, y)
        elif method == 'spearman':
            correlation, p_value = stats.spearmanr(x, y)
        elif method == 'kendall':
            correlation, p_value = stats.kendalltau(x, y)
        else:
            raise ValueError(f"Unknown correlation method: {method}")

        return {
            'correlation': correlation,
            'p_value': p_value,
            'significant_at_0.05': p_value < 0.05,
            'method': method
        }

    @staticmethod
    def normalize_data(
        data: List[float],
        method: str = 'zscore'
    ) -> np.ndarray:
        data_array = np.array(data)

        if method == 'zscore':
            mean = np.mean(data_array)
            std = np.std(data_array)
            if std == 0:
                return np.zeros_like(data_array)
            return (data_array - mean) / std

        elif method == 'minmax':
            min_val = np.min(data_array)
            max_val = np.max(data_array)
            if max_val == min_val:
                return np.zeros_like(data_array)
            return (data_array - min_val) / (max_val - min_val)

        elif method == 'robust':
            median = np.median(data_array)
            q1 = np.percentile(data_array, 25)
            q3 = np.percentile(data_array, 75)
            iqr = q3 - q1
            if iqr == 0:
                return np.zeros_like(data_array)
            return (data_array - median) / iqr

        else:
            raise ValueError(f"Unknown normalization method: {method}")

    @staticmethod
    def detect_outliers(
        data: List[float],
        method: str = 'iqr',
        threshold: float = 1.5
    ) -> List[int]:
        data_array = np.array(data)

        if method == 'iqr':
            q1 = np.percentile(data_array, 25)
            q3 = np.percentile(data_array, 75)
            iqr = q3 - q1

            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr

            outliers = [
                i for i, val in enumerate(data_array)
                if val < lower_bound or val > upper_bound
            ]

        elif method == 'zscore':
            mean = np.mean(data_array)
            std = np.std(data_array)

            if std == 0:
                return []

            z_scores = np.abs((data_array - mean) / std)
            outliers = [i for i, z in enumerate(z_scores) if z > threshold]

        else:
            raise ValueError(f"Unknown outlier detection method: {method}")

        return outliers

    @staticmethod
    def compute_bootstrap_ci(
        data: List[float],
        statistic_func=np.mean,
        num_bootstrap: int = 10000,
        confidence_level: float = 0.95
    ) -> Tuple[float, float, float]:
        data_array = np.array(data)
        n = len(data_array)

        if n == 0:
            return 0.0, 0.0, 0.0

        bootstrap_statistics = []

        for _ in range(num_bootstrap):
            sample = np.random.choice(data_array, size=n, replace=True)
            bootstrap_statistics.append(statistic_func(sample))

        bootstrap_statistics = np.array(bootstrap_statistics)

        stat_value = statistic_func(data_array)

        alpha = 1 - confidence_level
        lower = np.percentile(bootstrap_statistics, 100 * alpha / 2)
        upper = np.percentile(bootstrap_statistics, 100 * (1 - alpha / 2))

        return stat_value, lower, upper

    @staticmethod
    def compare_algorithms(
        results: Dict[str, List[float]],
        metric_name: str,
        higher_is_better: bool = True
    ) -> Dict:
        algorithm_names = list(results.keys())
        samples = [results[name] for name in algorithm_names]

        anova_result = StatisticalAnalyzer.perform_anova(samples, algorithm_names)

        pairwise_comparisons = {}
        for i, name1 in enumerate(algorithm_names):
            for j, name2 in enumerate(algorithm_names):
                if i < j:
                    key = f"{name1}_vs_{name2}"
                    pairwise_comparisons[key] = StatisticalAnalyzer.perform_t_test(
                        samples[i], samples[j]
                    )

        descriptive_stats = {
            name: StatisticalAnalyzer.compute_descriptive_statistics(sample)
            for name, sample in zip(algorithm_names, samples)
        }

        confidence_intervals = {
            name: StatisticalAnalyzer.compute_confidence_interval(sample)
            for name, sample in zip(algorithm_names, samples)
        }

        best_algorithm = algorithm_names[0]
        best_value = np.mean(samples[0])

        for name, sample in zip(algorithm_names, samples):
            mean_val = np.mean(sample)
            if higher_is_better:
                if mean_val > best_value:
                    best_value = mean_val
                    best_algorithm = name
            else:
                if mean_val < best_value:
                    best_value = mean_val
                    best_algorithm = name

        return {
            'metric_name': metric_name,
            'anova': anova_result,
            'pairwise_comparisons': pairwise_comparisons,
            'descriptive_statistics': descriptive_stats,
            'confidence_intervals': confidence_intervals,
            'best_algorithm': best_algorithm,
            'best_value': best_value,
            'higher_is_better': higher_is_better
        }
