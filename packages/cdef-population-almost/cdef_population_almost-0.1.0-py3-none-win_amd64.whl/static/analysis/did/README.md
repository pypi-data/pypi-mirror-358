# DiD Analysis Modules

This directory contains modular functions for the difference-in-differences analysis, broken down by analytical phase.

## Module Structure

### 01_panel_creation.R
- `create_panel_dataset()` - Transform CDEF data to panel format
- Creates treatment timing variables and yearly observations

### 02_income_panel.R  
- `create_parent_panel()` - Create parent-level panel with income data
- Joins income data and creates analysis variables (thousands DKK)

### 03_covariates.R
- `add_baseline_covariates()` - Add baseline demographics, education, employment
- Uses mapping utilities for consistent variable coding

### 04_did_models.R
- `run_did_models()` - Main DiD regression models
- `extract_did_estimate()` - Helper for extracting estimates
- Includes sensitivity analysis models (floored income, negative controls)

### 05_event_study.R
- `run_event_study()` - Event study with binned endpoints
- `dynamic_effects_analysis()` - Dynamic treatment effects
- Implements relative time factors and interaction models

### 06_robust_inference.R
- `implement_robust_inference()` - Clustered SEs, bootstrap, aggregated data
- `run_balance_tests()` - Test parallel trends assumption
- `run_randomization_inference()` - Permutation-based validation
- `run_ddd_analysis()` - Triple-differences for gender effects

### 07_visualization.R
- `create_coefficient_plot()` - Main DiD estimates plot
- `create_event_study_plot()` - Event study visualization  
- `create_robust_comparison_plot()` - Robustness checks
- `create_balance_plot()` - Balance test visualization
- `create_dynamic_effects_plot()` - Dynamic effects with binned endpoints
- `create_randomization_inference_plot()` - RI distribution plots
- `create_did_visualizations()` - Creates all plots

### 08_reporting.R
- `generate_formal_results()` - Publication-ready results document
- `create_results_summary_table()` - Main estimates table
- `create_robustness_summary_table()` - Robustness checks table
- `save_did_results()` - Save all outputs to files

## Usage

### Load all modules via main script:
```r
source("scripts/analysis/did_analysis_main.R")
```

### Run complete analysis:
```r
results <- run_complete_did_analysis(run_full_analysis = TRUE)
```

### Run specific phases:
```r
# Basic setup and models only
basic_results <- run_did_phases_1to4()

# All except computationally intensive analyses  
extended_results <- run_did_phases_1to6()
```

### Validate results:
```r
validation <- validate_did_analysis(results$results)
```

## Output Structure

```
output/
├── did_formal_results.md           # Publication-ready results
├── did_panel_data.csv              # Analysis dataset
├── figures/
│   ├── did_coefficient_plot.png
│   ├── did_event_study_plot.png
│   ├── did_robust_estimates_plot.png
│   ├── did_balance_test_plot.png
│   ├── did_dynamic_effects_plot.png
│   └── did_randomization_inference_plot.png
└── tables/
    ├── did_main_results.csv        # Summary of key estimates
    ├── did_robustness_results.csv  # Robustness checks
    └── did_detailed_results.csv    # All model coefficients
```

## Implementation Notes

1. **Data Loading**: Implement `load_data_files_for_did()` in the main script with your actual data loading logic
2. **Dependencies**: Requires mapping utilities from `scripts/baseline/mapping_utilities.R`
3. **Computational Intensity**: Set `run_full_analysis = FALSE` to skip randomization inference for faster testing
4. **Modular Design**: Each module can be sourced independently for testing specific components

## Integration with Baseline Pipeline

The DiD analysis integrates with the existing robust baseline characteristics pipeline by:
- Using the same mapping utilities for education and employment coding
- Leveraging the validated data enrichment process
- Building on the established case-control matching structure