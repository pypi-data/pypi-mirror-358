# ===== PHASE 6: VALIDATION & ROBUSTNESS =====
# Robust inference and validation functions
# Author: Tobias Kragholm
# Date: 2025-06-26

#' Implement robust inference methods
#' @param models List of fitted models
#' @param panel_data Panel data for clustering
#' @return List of robust inference results
implement_robust_inference <- function(models, panel_data) {

  cat("🔄 Implementing robust inference methods...\n")

  # 1. Clustered standard errors (cluster by parent_id)
  cat("   - Clustered standard errors...\n")
  robust_results <- map(models, function(model) {
    # Get the data used in the model
    model_data <- model$model

    # Match parent_id to model observations
    model_rownames <- as.numeric(rownames(model_data))
    panel_subset <- panel_data[model_rownames, ]
    cluster_var <- panel_subset$parent_id

    # Clustered standard errors
    vcov_clustered <- vcovCL(model, cluster = cluster_var)
    coef_test_clustered <- coeftest(model, vcov = vcov_clustered)

    return(coef_test_clustered)
  })

  # 2. Block bootstrap implementation
  cat("   - Block bootstrap...\n")
  bootstrap_did_income <- function(data, outcome, relationship_filter, n_bootstraps = 1000, seed = 123) {
    set.seed(seed)

    # Filter data for specific relationship
    analysis_data <- data %>% filter(relationship == relationship_filter)

    # Identify unique parent clusters
    clusters <- unique(analysis_data$parent_id)

    # Store results
    estimates <- numeric(n_bootstraps)

    # Bootstrap loop
    for(i in 1:n_bootstraps) {
      # Sample clusters with replacement
      sampled_clusters <- sample(clusters, replace = TRUE)
      # Create bootstrap sample
      boot_data <- analysis_data %>%
        filter(parent_id %in% sampled_clusters)

      # Fit model
      formula <- as.formula(paste(outcome, "~ treatment + post + treatment:post"))
      boot_model <- tryCatch({
        lm(formula, data = boot_data)
      }, error = function(e) NULL)

      # Extract DiD estimate
      if (!is.null(boot_model) && "treatment:post" %in% names(coef(boot_model))) {
        estimates[i] <- coef(boot_model)["treatment:post"]
      } else {
        estimates[i] <- NA
      }
    }

    # Calculate bootstrap CI
    valid_estimates <- estimates[!is.na(estimates)]
    if (length(valid_estimates) > 0) {
      ci <- quantile(valid_estimates, c(0.025, 0.975), na.rm = TRUE)
      se <- sd(valid_estimates, na.rm = TRUE)

      list(
        estimate = mean(valid_estimates, na.rm = TRUE),
        se = se,
        ci_lower = ci[1],
        ci_upper = ci[2],
        boot_samples = valid_estimates,
        n_valid = length(valid_estimates)
      )
    } else {
      list(estimate = NA, se = NA, ci_lower = NA, ci_upper = NA,
           boot_samples = numeric(0), n_valid = 0)
    }
  }

  bootstrap_results <- list(
    mother_wage = bootstrap_did_income(panel_data, "wage_income", "mother"),
    father_wage = bootstrap_did_income(panel_data, "wage_income", "father")
  )

  # 3. Aggregated data approach
  cat("   - Aggregated data approach...\n")
  aggregated_data <- panel_data %>%
    group_by(parent_id, treatment, post, relationship) %>%
    summarize(
      wage_income_mean = mean(wage_income, na.rm = TRUE),
      income_mean = mean(income, na.rm = TRUE),
      .groups = "drop"
    )

  aggregated_results <- list(
    mother_wage = lm(wage_income_mean ~ treatment + post + treatment:post,
                     data = aggregated_data %>% filter(relationship == "mother")),
    father_wage = lm(wage_income_mean ~ treatment + post + treatment:post,
                     data = aggregated_data %>% filter(relationship == "father"))
  )

  cat("✅ Robust inference methods completed\n")

  return(list(
    clustered = robust_results,
    bootstrap = bootstrap_results,
    aggregated = aggregated_results
  ))
}

#' Run comprehensive balance tests
#' @param panel_data Enhanced panel data
#' @return Balance test results
run_balance_tests <- function(panel_data) {

  cat("🔄 Running balance tests...\n")

  balance_vars <- c("baseline_age", "education_isced")

  balance_results <- map_dfr(balance_vars, function(var) {

    # Create relative time factor for balance testing
    balance_data <- panel_data %>%
      mutate(rel_time_factor = factor(time_to_treatment)) %>%
      filter(time_to_treatment >= -3 & time_to_treatment <= 3) %>%
      filter(!is.na(.data[[var]]))

    if (nrow(balance_data) == 0) {
      return(tibble())
    }

    formula_str <- paste(var, "~ rel_time_factor * treatment")
    formula <- as.formula(formula_str)

    # Separate models for mothers and fathers
    mother_data <- balance_data %>% filter(relationship == "mother")
    father_data <- balance_data %>% filter(relationship == "father")

    results <- tibble()

    if (nrow(mother_data) > 0) {
      mother_balance <- tryCatch({
        lm(formula, data = mother_data)
      }, error = function(e) NULL)

      if (!is.null(mother_balance)) {
        mother_coefs <- tidy(mother_balance, conf.int = TRUE) %>%
          filter(str_detect(term, ":treatment")) %>%
          mutate(parent = "Mother", variable = var)
        results <- bind_rows(results, mother_coefs)
      }
    }

    if (nrow(father_data) > 0) {
      father_balance <- tryCatch({
        lm(formula, data = father_data)
      }, error = function(e) NULL)

      if (!is.null(father_balance)) {
        father_coefs <- tidy(father_balance, conf.int = TRUE) %>%
          filter(str_detect(term, ":treatment")) %>%
          mutate(parent = "Father", variable = var)
        results <- bind_rows(results, father_coefs)
      }
    }

    return(results)
  })

  if (nrow(balance_results) > 0) {
    # Clean up variable names for reporting
    balance_results <- balance_results %>%
      mutate(
        variable_label = case_when(
          variable == "baseline_age" ~ "Baseline Age",
          variable == "education_isced" ~ "Education Level",
          TRUE ~ variable
        ),
        time = as.numeric(str_extract(term, "-?\\d+")),
        time = ifelse(is.na(time), 0, time)
      )
  }

  cat("📊 Balance tests completed:", nrow(balance_results), "coefficient estimates\n")

  return(balance_results)
}

#' Implement randomization inference for validation
#' @param panel_data Panel data
#' @param n_permutations Number of permutations
#' @return Randomization inference results
run_randomization_inference <- function(panel_data, n_permutations = 1000) {

  cat("🔄 Running randomization inference...\n")

  # Get actual treatment effects
  mother_data <- panel_data %>% filter(relationship == "mother")
  father_data <- panel_data %>% filter(relationship == "father")

  actual_mother_model <- lm(wage_income ~ treatment + post + treatment:post, data = mother_data)
  actual_father_model <- lm(wage_income ~ treatment + post + treatment:post, data = father_data)

  actual_mother_effect <- coef(actual_mother_model)["treatment:post"]
  actual_father_effect <- coef(actual_father_model)["treatment:post"]

  # Permutation loop
  set.seed(123)  # For reproducibility
  permuted_effects <- map_dfr(1:n_permutations, function(i) {

    # Randomly reassign treatment within matched pairs
    permuted_data <- panel_data %>%
      group_by(match_id) %>%
      mutate(
        # Randomly assign treatment status within each matched pair
        treatment_permuted = sample(treatment),
        # Update post indicator based on permuted treatment
        post_permuted = ifelse(treatment_permuted == 1 & time_to_treatment >= 0, 1, 0)
      ) %>%
      ungroup()

    # Run models on permuted data
    mother_permuted <- tryCatch({
      lm(wage_income ~ treatment_permuted + post_permuted + treatment_permuted:post_permuted,
         data = permuted_data %>% filter(relationship == "mother"))
    }, error = function(e) NULL)

    father_permuted <- tryCatch({
      lm(wage_income ~ treatment_permuted + post_permuted + treatment_permuted:post_permuted,
         data = permuted_data %>% filter(relationship == "father"))
    }, error = function(e) NULL)

    mother_effect <- ifelse(!is.null(mother_permuted) &&
                           "treatment_permuted:post_permuted" %in% names(coef(mother_permuted)),
                           coef(mother_permuted)["treatment_permuted:post_permuted"], NA)

    father_effect <- ifelse(!is.null(father_permuted) &&
                           "treatment_permuted:post_permuted" %in% names(coef(father_permuted)),
                           coef(father_permuted)["treatment_permuted:post_permuted"], NA)

    tibble(
      iteration = i,
      mother_effect = mother_effect,
      father_effect = father_effect
    )
  })

  # Calculate p-values (two-tailed)
  mother_p <- mean(abs(permuted_effects$mother_effect) >= abs(actual_mother_effect), na.rm = TRUE)
  father_p <- mean(abs(permuted_effects$father_effect) >= abs(actual_father_effect), na.rm = TRUE)

  cat("📊 Randomization inference p-values:\n")
  cat("   - Mother:", round(mother_p, 3), "\n")
  cat("   - Father:", round(father_p, 3), "\n")

  return(list(
    permuted_effects = permuted_effects,
    p_values = c(mother = mother_p, father = father_p),
    actual_effects = c(mother = actual_mother_effect, father = actual_father_effect)
  ))
}

#' Triple-differences (DDD) analysis for gender effects
#' @param panel_data Panel data
#' @return DDD results
run_ddd_analysis <- function(panel_data) {

  cat("🔄 Running DDD analysis...\n")

  # Create gender indicator and interactions
  ddd_data <- panel_data %>%
    mutate(
      female = ifelse(relationship == "mother", 1, 0),
      treatment_post = treatment * post,
      female_treatment = female * treatment,
      female_post = female * post,
      female_treatment_post = female * treatment * post
    )

  # Main DDD model
  ddd_model <- lm(
    wage_income ~ treatment + post + female +
      treatment_post + female_treatment + female_post + female_treatment_post +
      baseline_age + employment_socio13 + education_isced + factor(year),
    data = ddd_data
  )

  # Extract DDD coefficient (female_treatment_post)
  ddd_coefficient <- tidy(ddd_model, conf.int = TRUE) %>%
    filter(term == "female_treatment_post")

  cat("📊 DDD coefficient (gender difference):", round(ddd_coefficient$estimate, 1), "\n")
  cat("📊 DDD p-value:", round(ddd_coefficient$p.value, 3), "\n")

  return(list(model = ddd_model, coefficient = ddd_coefficient))
}

cat("✅ Robust inference functions loaded\n")
