# ===== PHASE 5: EVENT STUDY ANALYSIS =====
# Event study and dynamic effects functions
# Author: Tobias Kragholm
# Date: 2025-06-26

#' Run improved event study design with binned endpoints
#' @param panel_data Enhanced panel data with all covariates
#' @return List with event study models and coefficients
run_event_study <- function(panel_data) {

  cat("🔄 Running event study analysis...\n")

  # Create relative time factor with -1 as reference
  event_data <- panel_data %>%
    mutate(
      rel_time_factor = relevel(factor(time_to_treatment), ref = "-1"),
      # Create binned endpoints for distant periods
      rel_time_binned = case_when(
        time_to_treatment < -3 ~ -4,  # Pre-treatment bin
        time_to_treatment > 5 ~ 6,   # Post-treatment bin
        TRUE ~ time_to_treatment
      ),
      rel_time_binned_factor = relevel(factor(rel_time_binned), ref = "-1")
    ) %>%
    # Filter to reasonable event window
    filter(time_to_treatment >= -5 & time_to_treatment <= 10)

  cat("📊 Event study sample - Mothers:",
      sum(event_data$relationship == "mother"), "observations\n")
  cat("📊 Event study sample - Fathers:",
      sum(event_data$relationship == "father"), "observations\n")

  # Mother's event study with full interactions
  mother_event <- lm(
    wage_income ~ rel_time_binned_factor * treatment +
      baseline_age + employment_socio13 + education_isced + factor(year),
    data = event_data %>% filter(relationship == "mother")
  )

  # Father's event study
  father_event <- lm(
    wage_income ~ rel_time_binned_factor * treatment +
      baseline_age + employment_socio13 + education_isced + factor(year),
    data = event_data %>% filter(relationship == "father")
  )

  # Extract dynamic effects coefficients
  extract_event_coefficients <- function(model, parent_type) {
    tidy(model, conf.int = TRUE) %>%
      filter(str_detect(term, "rel_time_binned_factor.*:treatment")) %>%
      mutate(
        time_raw = str_extract(term, "-?\\d+"),
        time = as.numeric(time_raw),
        parent = parent_type,
        bin_type = case_when(
          time == -4 ~ "Pre-bin",
          time == 6 ~ "Post-bin",
          TRUE ~ "Regular"
        )
      )
  }

  # Combine results
  event_coefficients <- bind_rows(
    extract_event_coefficients(mother_event, "Mother"),
    extract_event_coefficients(father_event, "Father")
  )

  cat("📊 Event study coefficients extracted:", nrow(event_coefficients), "estimates\n")

  return(list(
    models = list(mother = mother_event, father = father_event),
    coefficients = event_coefficients,
    data = event_data
  ))
}

#' Implement dynamic treatment effects analysis
#' @param panel_data Enhanced panel data
#' @param max_lag Maximum periods after treatment
#' @param max_lead Maximum periods before treatment
#' @return List of dynamic effects models
dynamic_effects_analysis <- function(panel_data, max_lag = 5, max_lead = 3) {

  cat("🔄 Running dynamic effects analysis...\n")

  # Create binned endpoints for distant periods
  dynamic_data <- panel_data %>%
    mutate(
      rel_time_binned = case_when(
        time_to_treatment < -max_lead ~ -max_lead - 1,
        time_to_treatment > max_lag ~ max_lag + 1,
        TRUE ~ time_to_treatment
      ),
      rel_time_factor = factor(rel_time_binned),
      rel_time_factor = relevel(rel_time_factor, toString(-1))
    ) %>%
    filter(time_to_treatment >= -(max_lead + 2) & time_to_treatment <= (max_lag + 2))

  # Run dynamic effects models
  mother_dynamic <- lm(
    wage_income ~ rel_time_factor * treatment +
      baseline_age + employment_socio13 + education_isced + factor(year),
    data = dynamic_data %>% filter(relationship == "mother")
  )

  father_dynamic <- lm(
    wage_income ~ rel_time_factor * treatment +
      baseline_age + employment_socio13 + education_isced + factor(year),
    data = dynamic_data %>% filter(relationship == "father")
  )

  # Extract coefficients
  extract_dynamic_coefficients <- function(model, parent_type, max_lag, max_lead) {
    tidy(model, conf.int = TRUE) %>%
      filter(str_detect(term, "rel_time_factor.*:treatment")) %>%
      mutate(
        time_raw = str_extract(term, "-?\\d+"),
        time = as.numeric(time_raw),
        parent = parent_type,
        bin_type = case_when(
          time == -max_lead - 1 ~ "Pre-bin",
          time == max_lag + 1 ~ "Post-bin",
          TRUE ~ "Regular"
        )
      )
  }

  dynamic_coefficients <- bind_rows(
    extract_dynamic_coefficients(mother_dynamic, "Mother", max_lag, max_lead),
    extract_dynamic_coefficients(father_dynamic, "Father", max_lag, max_lead)
  )

  cat("📊 Dynamic effects coefficients:", nrow(dynamic_coefficients), "estimates\n")

  return(list(
    models = list(mother = mother_dynamic, father = father_dynamic),
    coefficients = dynamic_coefficients
  ))
}

cat("✅ Event study functions loaded\n")
