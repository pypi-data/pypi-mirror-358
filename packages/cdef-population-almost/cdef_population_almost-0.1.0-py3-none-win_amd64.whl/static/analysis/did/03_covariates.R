# ===== PHASE 3: CONTROL VARIABLES INTEGRATION =====
# Baseline covariates integration functions
# Author: Tobias Kragholm
# Date: 2025-06-26

# Source mapping utilities
source("scripts/baseline/mapping_utilities.R")

#' Add baseline covariates to panel data
#' @param panel_data Panel data with income information
#' @param demographics_data Time series demographic data
#' @param education_data Time series education data
#' @param employment_data Time series employment data
#' @return Enhanced panel with baseline covariates
add_baseline_covariates <- function(panel_data, demographics_data, education_data, employment_data) {

  cat("🔄 Adding baseline covariates...\n")

  # Get baseline (pre-treatment) demographics
  baseline_demographics <- demographics_data %>%
    inner_join(
      panel_data %>%
        select(match_id, individual_type, treatment_year) %>%
        distinct(),
      by = c("match_id", "individual_type")
    ) %>%
    filter(year <= treatment_year) %>%
    group_by(match_id, individual_type, relationship) %>%
    slice_max(year, with_ties = FALSE) %>%
    ungroup() %>%
    select(match_id, individual_type, relationship,
           baseline_age = age, country_of_origin, civil_status)

  # Get baseline education (using mapping utilities)
  baseline_education <- education_data %>%
    inner_join(
      panel_data %>% select(match_id, individual_type, treatment_year) %>% distinct(),
      by = c("match_id", "individual_type")
    ) %>%
    filter(year <= treatment_year) %>%
    group_by(match_id, individual_type, relationship) %>%
    slice_max(year, with_ties = FALSE) %>%
    ungroup() %>%
    mutate(
      # Use mapping utilities for consistent education coding
      education_isced = map_numeric(hfaudd_code, get_isced_mapping(), "isced_number", default = NA)
    ) %>%
    select(match_id, individual_type, relationship, education_isced)

  # Get baseline employment
  baseline_employment <- employment_data %>%
    inner_join(
      panel_data %>% select(match_id, individual_type, treatment_year) %>% distinct(),
      by = c("match_id", "individual_type")
    ) %>%
    filter(year <= treatment_year) %>%
    group_by(match_id, individual_type, relationship) %>%
    slice_max(year, with_ties = FALSE) %>%
    ungroup() %>%
    mutate(
      # Convert employment to factor
      employment_socio13 = as.factor(socio13_code)
    ) %>%
    select(match_id, individual_type, relationship, employment_socio13)

  # Join all baseline variables
  enhanced_panel <- panel_data %>%
    left_join(baseline_demographics,
              by = c("match_id", "individual_type", "relationship")) %>%
    left_join(baseline_education,
              by = c("match_id", "individual_type", "relationship")) %>%
    left_join(baseline_employment,
              by = c("match_id", "individual_type", "relationship"))

  # Report covariate coverage
  covariate_coverage <- enhanced_panel %>%
    summarise(
      age_coverage = mean(!is.na(baseline_age)) * 100,
      education_coverage = mean(!is.na(education_isced)) * 100,
      employment_coverage = mean(!is.na(employment_socio13)) * 100,
      country_coverage = mean(!is.na(country_of_origin)) * 100
    )

  cat("📊 Baseline covariate coverage:\n")
  cat("   - Age:", round(covariate_coverage$age_coverage, 1), "%\n")
  cat("   - Education:", round(covariate_coverage$education_coverage, 1), "%\n")
  cat("   - Employment:", round(covariate_coverage$employment_coverage, 1), "%\n")
  cat("   - Country of origin:", round(covariate_coverage$country_coverage, 1), "%\n")

  return(enhanced_panel)
}

cat("✅ Covariate integration functions loaded\n")
