# ===== MAIN DiD ANALYSIS SCRIPT =====
# Complete difference-in-differences analysis for CDEF population data
# Author: Tobias Kragholm
# Date: 2025-06-26

# Load required libraries
suppressPackageStartupMessages({
  library(tidyverse)
  library(lubridate)
  library(broom)
  library(sandwich)
  library(lmtest)
  library(modelsummary)
  library(ggplot2)
  library(scales)
  library(glue)
})

# Source all DiD analysis modules
cat("🚀 Loading DiD Analysis Modules\n")
cat("=" %>% rep(50) %>% paste(collapse = ""), "\n")

source("scripts/analysis/did/01_panel_creation.R")
source("scripts/analysis/did/02_income_panel.R")
source("scripts/analysis/did/03_covariates.R")
source("scripts/analysis/did/04_did_models.R")
source("scripts/analysis/did/05_event_study.R")
source("scripts/analysis/did/06_robust_inference.R")
source("scripts/analysis/did/07_visualization.R")
source("scripts/analysis/did/08_reporting.R")

cat("✅ All modules loaded successfully!\n\n")

# ===== DATA LOADING FUNCTION =====

#' Load data files for DiD analysis from enrichment output
#' @return List of data frames needed for analysis
load_data_files_for_did <- function() {

  cat("🔄 Loading data files for DiD analysis...\n")

  # Define data paths (matching baseline script structure)
  input_path <- "cohort_output/enrichment_output"

  # Check if enrichment output exists
  if (!dir.exists(input_path)) {
    stop("❌ Enrichment output directory not found: ", input_path,
         "\n   Please run the baseline characteristics pipeline first.")
  }

  # Load basic data (contains match_id, case info, treatment timing)
  basic_file <- file.path(input_path, "basic.csv")
  if (!file.exists(basic_file)) {
    stop("❌ Basic data file not found: ", basic_file)
  }

  basic_data <- read_csv(basic_file, show_col_types = FALSE) %>%
    mutate(
      case_index_date = as.Date(case_index_date),
      case_birth_date = as.Date(case_birth_date)
    )

  cat("✅ Loaded basic data:", nrow(basic_data), "matched pairs\n")

  # Create child_data by expanding basic data to include both cases and controls
  child_data <- basic_data %>%
    # Create case records
    transmute(
      match_id = match_id,
      individual_type = "case",
      pnr = case_pnr,
      case_index_date = case_index_date,
      birth_date = case_birth_date
    ) %>%
    # Add control records (need to expand for multiple controls per case)
    bind_rows(
      basic_data %>%
        transmute(
          match_id = match_id,
          individual_type = "control",
          pnr = control_pnr,
          case_index_date = case_index_date,
          birth_date = NA  # Control birth dates would need separate loading
        )
    )

  cat("✅ Created child data:", nrow(child_data), "individuals\n")

  # Load income data
  income_file <- file.path(input_path, "income.csv")
  if (!file.exists(income_file)) {
    stop("❌ Income data file not found: ", income_file)
  }

  income_data <- read_csv(income_file, show_col_types = FALSE) %>%
    # Filter to parent data only (exclude self records)
    filter(relationship %in% c("mother", "father")) %>%
    mutate(
      year = as.numeric(year),
      total_income = as.numeric(total_income),
      salary = as.numeric(salary)
    )

  cat("✅ Loaded income data:", nrow(income_data), "parent-year observations\n")

  # Load demographics data
  demographics_file <- file.path(input_path, "demographics.csv")
  if (!file.exists(demographics_file)) {
    stop("❌ Demographics data file not found: ", demographics_file)
  }

  demographics_data <- read_csv(demographics_file, show_col_types = FALSE) %>%
    filter(relationship %in% c("mother", "father")) %>%
    mutate(
      year = as.numeric(year),
      age = as.numeric(age)
    )

  cat("✅ Loaded demographics data:", nrow(demographics_data), "parent-year observations\n")

  # Load education data
  education_file <- file.path(input_path, "education.csv")
  if (!file.exists(education_file)) {
    cat("⚠️ Education data file not found, creating empty structure\n")
    education_data <- tibble(
      match_id = character(),
      individual_type = character(),
      relationship = character(),
      year = numeric(),
      hfaudd_code = character()
    )
  } else {
    education_data <- read_csv(education_file, show_col_types = FALSE) %>%
      filter(relationship %in% c("mother", "father")) %>%
      mutate(year = as.numeric(year))

    cat("✅ Loaded education data:", nrow(education_data), "parent-year observations\n")
  }

  # Load employment data
  employment_file <- file.path(input_path, "employment.csv")
  if (!file.exists(employment_file)) {
    cat("⚠️ Employment data file not found, creating empty structure\n")
    employment_data <- tibble(
      match_id = character(),
      individual_type = character(),
      relationship = character(),
      year = numeric(),
      socio13_code = character()
    )
  } else {
    employment_data <- read_csv(employment_file, show_col_types = FALSE) %>%
      filter(relationship %in% c("mother", "father")) %>%
      mutate(year = as.numeric(year))

    cat("✅ Loaded employment data:", nrow(employment_data), "parent-year observations\n")
  }

  # Summary statistics
  cat("\n📊 Data Loading Summary:\n")
  cat("   - Matched pairs:", length(unique(basic_data$match_id)), "\n")
  cat("   - Total individuals:", nrow(child_data), "\n")
  cat("   - Income observations:", nrow(income_data), "\n")
  cat("   - Years covered:", range(income_data$year, na.rm = TRUE), "\n")
  cat("   - Parents with income data:",
      length(unique(paste(income_data$match_id, income_data$individual_type, income_data$relationship))), "\n")

  return(list(
    child_data = child_data,
    parent_data = tibble(),  # Not needed in current structure
    income_data = income_data,
    demographics_data = demographics_data,
    education_data = education_data,
    employment_data = employment_data
  ))
}

# ===== MAIN ANALYSIS FUNCTION =====

#' Run complete DiD analysis (all phases)
#' @param run_full_analysis Whether to run all phases including computationally intensive ones
#' @return Complete results object
run_complete_did_analysis <- function(run_full_analysis = TRUE) {

  cat("🚀 Starting Complete DiD Analysis\n")
  cat("=" %>% rep(60) %>% paste(collapse = ""), "\n")

  # Load data
  cat("\n📁 Phase 0: Data Loading\n")
  data_list <- load_data_files_for_did()

  # Phase 1: Create panel dataset
  cat("\n📊 Phase 1: Data Structure Transformation\n")
  panel_data <- create_panel_dataset(
    data_list$child_data,
    data_list$parent_data,
    data_list$income_data,
    data_list$demographics_data
  )

  # Phase 2: Create parent panel with income
  cat("\n💰 Phase 2: Income Data Panel Construction\n")
  parent_panel <- create_parent_panel(panel_data, data_list$income_data)

  # Phase 3: Add baseline covariates
  cat("\n🔧 Phase 3: Control Variables Integration\n")
  enhanced_panel <- add_baseline_covariates(
    parent_panel,
    data_list$demographics_data,
    data_list$education_data,
    data_list$employment_data
  )

  # Phase 4: Run DiD models
  cat("\n📈 Phase 4: Econometric Models Implementation\n")
  models <- run_did_models(enhanced_panel)

  # Phase 5: Event study analysis
  cat("\n📊 Phase 5: Event Study Analysis\n")
  event_study_results <- run_event_study(enhanced_panel)
  dynamic_effects_results <- dynamic_effects_analysis(enhanced_panel)

  # Phase 6: Robust inference and validation
  cat("\n🔬 Phase 6: Robust Inference & Validation\n")
  robust_inference_results <- implement_robust_inference(models, enhanced_panel)
  balance_test_results <- run_balance_tests(enhanced_panel)

  # Optional computationally intensive analyses
  randomization_inference_results <- NULL
  ddd_results <- NULL

  if (run_full_analysis) {
    cat("   🎲 Running randomization inference (may take several minutes)...\n")
    randomization_inference_results <- run_randomization_inference(enhanced_panel, n_permutations = 100)

    cat("   ⚖️ Running DDD analysis...\n")
    ddd_results <- run_ddd_analysis(enhanced_panel)
  }

  # Compile all results
  did_results <- list(
    panel_data = enhanced_panel,
    models = models,
    event_study = event_study_results,
    dynamic_effects = dynamic_effects_results,
    robust_inference = robust_inference_results,
    balance_tests = balance_test_results,
    randomization_inference = randomization_inference_results,
    ddd = ddd_results,
    data_validation = list(
      n_observations = nrow(enhanced_panel),
      n_unique_parents = length(unique(enhanced_panel$parent_id)),
      treatment_control_ratio = table(enhanced_panel$treatment),
      time_coverage = range(enhanced_panel$year)
    )
  )

  # Phase 7: Create visualizations
  cat("\n📊 Phase 7: Visualization & Reporting\n")
  plots <- create_did_visualizations(did_results)

  # Phase 8: Save results
  cat("\n💾 Phase 8: Save Results\n")
  save_did_results(did_results, plots)

  cat("\n🎉 Complete DiD Analysis Finished Successfully!\n")
  cat("=" %>% rep(60) %>% paste(collapse = ""), "\n")
  cat("📄 Main results: output/did_formal_results.md\n")
  cat("📊 Plots saved to: output/figures/\n")
  cat("📋 Tables saved to: output/tables/\n")
  cat("📁 Panel data: output/did_panel_data.csv\n")

  return(list(
    results = did_results,
    plots = plots
  ))
}

# ===== PHASE-BY-PHASE EXECUTION FUNCTIONS =====

#' Run analysis phases 1-4 only
run_did_phases_1to4 <- function() {

  cat("🚀 Running DiD Analysis - Phases 1-4\n")

  data_list <- load_data_files_for_did()
  panel_data <- create_panel_dataset(data_list$child_data, data_list$parent_data,
                                    data_list$income_data, data_list$demographics_data)
  parent_panel <- create_parent_panel(panel_data, data_list$income_data)
  enhanced_panel <- add_baseline_covariates(parent_panel, data_list$demographics_data,
                                           data_list$education_data, data_list$employment_data)
  models <- run_did_models(enhanced_panel)

  return(list(panel_data = enhanced_panel, models = models))
}

#' Run analysis phases 1-6 only
run_did_phases_1to6 <- function() {

  cat("🚀 Running DiD Analysis - Phases 1-6\n")

  phase1to4_results <- run_did_phases_1to4()
  event_study_results <- run_event_study(phase1to4_results$panel_data)
  dynamic_effects_results <- dynamic_effects_analysis(phase1to4_results$panel_data)
  robust_inference_results <- implement_robust_inference(phase1to4_results$models,
                                                        phase1to4_results$panel_data)
  balance_test_results <- run_balance_tests(phase1to4_results$panel_data)

  return(list(
    panel_data = phase1to4_results$panel_data,
    models = phase1to4_results$models,
    event_study = event_study_results,
    dynamic_effects = dynamic_effects_results,
    robust_inference = robust_inference_results,
    balance_tests = balance_test_results
  ))
}

# ===== VALIDATION FUNCTIONS =====

#' Validate DiD analysis setup and data
#' @param results DiD results object
validate_did_analysis <- function(results) {

  cat("🔍 Validating DiD Analysis\n")

  validation_report <- list()

  # Check sample sizes
  validation_report$sample_sizes <- results$panel_data %>%
    group_by(relationship, treatment) %>%
    summarise(
      n_observations = n(),
      n_unique_parents = n_distinct(parent_id),
      mean_years_observed = n() / n_distinct(parent_id),
      .groups = "drop"
    )

  # Check treatment timing consistency
  validation_report$treatment_timing <- results$panel_data %>%
    filter(treatment == 1) %>%
    group_by(parent_id) %>%
    summarise(
      first_treatment_year = min(year[post == 1]),
      consistent_timing = length(unique(treatment_year)) == 1,
      .groups = "drop"
    ) %>%
    summarise(
      all_consistent = all(consistent_timing),
      treatment_year_range = paste(range(first_treatment_year), collapse = " - ")
    )

  # Check data quality
  validation_report$data_quality <- results$panel_data %>%
    summarise(
      missing_income_pct = mean(is.na(wage_income)) * 100,
      negative_income_pct = mean(wage_income < 0, na.rm = TRUE) * 100,
      zero_income_pct = mean(wage_income == 0, na.rm = TRUE) * 100,
      extreme_income_pct = mean(abs(wage_income) > 1000, na.rm = TRUE) * 100
    )

  cat("📊 Validation Summary:\n")
  print(validation_report)

  return(validation_report)
}

# ===== EXECUTION MESSAGES =====

cat("\n🎯 Main Functions Available:\n")
cat("   📋 run_complete_did_analysis() - Full analysis (all phases)\n")
cat("   📋 run_did_phases_1to4() - Basic setup and models only\n")
cat("   📋 run_did_phases_1to6() - All except intensive computations\n")
cat("   📋 validate_did_analysis(results) - Validate analysis results\n")
cat("\n💡 Quick Start:\n")
cat("   results <- run_complete_did_analysis(run_full_analysis = FALSE)\n")
cat("   validation <- validate_did_analysis(results$results)\n")
cat("\n📝 Note: Implement load_data_files_for_did() with your actual data loading logic\n")

cat("\n✅ DiD Analysis Main Script Loaded Successfully!\n")
cat("🚀 Ready to run complete analysis!\n")
