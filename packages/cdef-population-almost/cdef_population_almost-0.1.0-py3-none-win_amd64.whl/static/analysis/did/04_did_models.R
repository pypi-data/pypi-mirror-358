# ===== PHASE 4: ECONOMETRIC MODELS IMPLEMENTATION =====
# Main DiD models replicating previous specifications
# Author: Tobias Kragholm
# Date: 2025-06-26

#' Run main DiD models replicating previous specifications
#' @param panel_data Enhanced panel data with all covariates
#' @return List of fitted models
run_did_models <- function(panel_data) {

  cat("🔄 Running DiD models...\n")

  # Create separate datasets for mothers and fathers
  mother_data <- panel_data %>% filter(relationship == "mother")
  father_data <- panel_data %>% filter(relationship == "father")

  cat("📊 Sample sizes - Mothers:", nrow(mother_data), "observations\n")
  cat("📊 Sample sizes - Fathers:", nrow(father_data), "observations\n")

  # Mother's wage models (matching previous specifications)
  model_simple_mother <- lm(
    wage_income ~ treatment + post + treatment:post,
    data = mother_data
  )

  model_full_mother <- lm(
    wage_income ~ treatment + post + treatment:post +
      baseline_age + employment_socio13 + education_isced,
    data = mother_data
  )

  # Father's wage models
  model_simple_father <- lm(
    wage_income ~ treatment + post + treatment:post,
    data = father_data
  )

  model_full_father <- lm(
    wage_income ~ treatment + post + treatment:post +
      baseline_age + employment_socio13 + education_isced,
    data = father_data
  )

  # Total income models
  model_mother_total <- lm(
    income ~ treatment + post + treatment:post +
      baseline_age + employment_socio13 + education_isced,
    data = mother_data
  )

  model_father_total <- lm(
    income ~ treatment + post + treatment:post +
      baseline_age + employment_socio13 + education_isced,
    data = father_data
  )

  # Sensitivity analysis models
  # 1. Zero-floored income versions
  model_mother_wage_floored <- lm(
    wage_income_floored ~ treatment + post + treatment:post +
      baseline_age + employment_socio13 + education_isced,
    data = mother_data
  )

  model_father_wage_floored <- lm(
    wage_income_floored ~ treatment + post + treatment:post +
      baseline_age + employment_socio13 + education_isced,
    data = father_data
  )

  # 2. Models with negative income indicators
  model_mother_neg_control <- lm(
    wage_income ~ treatment + post + treatment:post +
      baseline_age + employment_socio13 + education_isced +
      wage_negative,
    data = mother_data
  )

  model_father_neg_control <- lm(
    wage_income ~ treatment + post + treatment:post +
      baseline_age + employment_socio13 + education_isced +
      wage_negative,
    data = father_data
  )

  models <- list(
    # Standard models
    mother_wage_simple = model_simple_mother,
    mother_wage_full = model_full_mother,
    father_wage_simple = model_simple_father,
    father_wage_full = model_full_father,
    mother_total = model_mother_total,
    father_total = model_father_total,

    # Sensitivity models
    mother_wage_floored = model_mother_wage_floored,
    father_wage_floored = model_father_wage_floored,
    mother_neg_control = model_mother_neg_control,
    father_neg_control = model_father_neg_control
  )

  # Extract and display key DiD estimates
  did_estimates <- map_dfr(names(models), function(name) {
    model <- models[[name]]
    coef_summary <- tidy(model) %>%
      filter(term == "treatment:post") %>%
      mutate(model_name = name)
    return(coef_summary)
  })

  cat("📊 Key DiD estimates (treatment:post coefficients):\n")
  did_estimates %>%
    select(model_name, estimate, std.error, p.value) %>%
    mutate(
      estimate = round(estimate, 1),
      std.error = round(std.error, 1),
      p.value = ifelse(p.value < 0.001, "<0.001", round(p.value, 3))
    ) %>%
    print()

  return(models)
}

#' Extract DiD estimate from model for reporting
#' @param model Fitted lm model
#' @param outcome_name Name of outcome variable
#' @return Tibble with formatted estimate
extract_did_estimate <- function(model, outcome_name) {
  tidy(model) %>%
    filter(term == "treatment:post") %>%
    mutate(
      outcome = outcome_name,
      formatted_estimate = paste0(round(estimate, 1),
                                 ifelse(p.value < 0.001, "***",
                                       ifelse(p.value < 0.01, "**",
                                             ifelse(p.value < 0.05, "*", ""))))
    ) %>%
    select(outcome, estimate, std.error, p.value, formatted_estimate)
}

cat("✅ DiD models functions loaded\n")
