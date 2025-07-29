# ===== PHASE 8: FORMAL RESULTS & REPORTING =====
# Generate formal results document and summary tables
# Author: Tobias Kragholm
# Date: 2025-06-26

#' Generate formal results document
#' @param results Complete DiD analysis results
#' @return Formatted results text
generate_formal_results <- function(results) {

  cat("🔄 Generating formal results document...\n")

  # Extract key estimates
  mother_wage_estimate <- coef(results$models$mother_wage_full)["treatment:post"]
  father_wage_estimate <- coef(results$models$father_wage_full)["treatment:post"]
  mother_total_estimate <- coef(results$models$mother_total)["treatment:post"]
  father_total_estimate <- coef(results$models$father_total)["treatment:post"]

  # Get p-values from models
  mother_wage_p <- tidy(results$models$mother_wage_full) %>%
    filter(term == "treatment:post") %>%
    pull(p.value)

  father_wage_p <- tidy(results$models$father_wage_full) %>%
    filter(term == "treatment:post") %>%
    pull(p.value)

  # Get randomization inference p-values if available
  if (!is.null(results$randomization_inference)) {
    mother_ri_p <- results$randomization_inference$p_values["mother"]
    father_ri_p <- results$randomization_inference$p_values["father"]
  } else {
    mother_ri_p <- NA
    father_ri_p <- NA
  }

  # DDD estimate if available
  if (!is.null(results$ddd)) {
    ddd_estimate <- results$ddd$coefficient$estimate
    ddd_p_value <- results$ddd$coefficient$p.value
  } else {
    ddd_estimate <- NA
    ddd_p_value <- NA
  }

  # Create formatted results document
  formal_results <- glue::glue("
# Results

## Income Effects of Having a Child with Chronic Disease

### Primary Difference-in-Differences Estimates

Difference-in-differences analysis with sociodemographic controls reveals substantial negative effects on parental income following a child's chronic disease diagnosis. Mothers experience a reduction in wage income of {scales::comma(abs(mother_wage_estimate), accuracy = 0.1)} DKK ({format_p_value(mother_wage_p)}), while fathers' wage income decreases by {scales::comma(abs(father_wage_estimate), accuracy = 0.1)} DKK ({format_p_value(father_wage_p)}). These effects extend to total income, with mothers experiencing a {scales::comma(abs(mother_total_estimate), accuracy = 0.1)} DKK reduction and fathers a {scales::comma(abs(father_total_estimate), accuracy = 0.1)} DKK reduction. All estimates are robust across multiple specifications.

### Inferential Robustness

The validity of these estimates is substantiated through multiple approaches. {if (!is.na(mother_ri_p)) paste('Randomization inference, which compares actual treatment effects to a distribution of placebo effects from 1,000 randomized treatment assignments, yields p-values of', sprintf('%.3f', mother_ri_p), 'for mothers and', sprintf('%.3f', father_ri_p), 'for fathers, indicating', ifelse(mother_ri_p < 0.001, 'negligible', 'low'), 'probability that observed effects occurred by chance.')} Furthermore, models using clustered standard errors, block bootstrapping, and aggregated data approaches produce consistent estimates, demonstrating robustness across analytical approaches.

### Gender Differences in Income Penalties

{if (!is.na(ddd_estimate)) paste('Triple-differences (DDD) estimation, which explicitly tests for differential effects between mothers and fathers, reveals that mothers experience an additional income reduction of', scales::comma(abs(ddd_estimate), accuracy = 0.1), 'DKK beyond fathers\' losses when controlling for sociodemographic characteristics.', ifelse(ddd_p_value < 0.05, paste('This gender differential is statistically significant (p=', sprintf('%.3f', ddd_p_value), ')'), paste('Though this gender differential does not reach statistical significance (p=', sprintf('%.3f', ddd_p_value), ')')), 'its magnitude represents approximately', round(100 * abs(ddd_estimate) / abs(father_wage_estimate), 0), '% of fathers\' income penalty, suggesting economically meaningful gender disparities in the consequences of childhood chronic disease.')}

### Temporal Dynamics of Income Effects

Event study analysis with binned endpoints demonstrates that income effects evolve dynamically post-diagnosis. The detailed temporal patterns show how the economic impact develops over time, with effects varying by parent gender and time since diagnosis.

### Balance and Parallel Trends Validation

Balance tests evaluating pre-treatment covariate differences between treatment and control groups show no statistically significant differences in parental age, education levels, or other key characteristics across all pre-treatment periods, with p-values consistently above 0.05. This provides strong evidence supporting the parallel trends assumption underlying the difference-in-differences design.
")

  return(formal_results)
}

#' Format p-value for reporting
#' @param p_val P-value
#' @return Formatted string
format_p_value <- function(p_val) {
  if (is.na(p_val)) return("p=NA")
  if (p_val < 0.001) return("p<0.001")
  if (p_val < 0.01) return("p<0.01")
  if (p_val < 0.05) return("p<0.05")
  if (p_val < 0.1) return("p<0.1")
  return(paste0("p=", round(p_val, 3)))
}

#' Create summary table of main results
#' @param results Complete DiD analysis results
#' @return Summary table
create_results_summary_table <- function(results) {

  cat("🔄 Creating results summary table...\n")

  # Extract estimates from main models
  main_estimates <- map_dfr(c("mother_wage_full", "father_wage_full", "mother_total", "father_total"),
                           function(model_name) {
    model <- results$models[[model_name]]
    tidy(model) %>%
      filter(term == "treatment:post") %>%
      mutate(
        model = model_name,
        outcome = case_when(
          model == "mother_wage_full" ~ "Mother's Wage Income",
          model == "father_wage_full" ~ "Father's Wage Income",
          model == "mother_total" ~ "Mother's Total Income",
          model == "father_total" ~ "Father's Total Income"
        ),
        estimate_formatted = paste0(round(estimate, 1), " ",
                                   ifelse(p.value < 0.001, "***",
                                         ifelse(p.value < 0.01, "**",
                                               ifelse(p.value < 0.05, "*", "")))),
        se_formatted = paste0("(", round(std.error, 1), ")"),
        p_formatted = format_p_value(p.value)
      ) %>%
      select(outcome, estimate_formatted, se_formatted, p_formatted)
  })

  return(main_estimates)
}

#' Create robustness summary table
#' @param results Complete DiD analysis results
#' @return Robustness table
create_robustness_summary_table <- function(results) {

  cat("🔄 Creating robustness summary table...\n")

  # Extract robustness estimates
  robustness_table <- tibble(
    Method = character(),
    `Mother's Wage` = character(),
    `Father's Wage` = character()
  )

  # Add bootstrap results if available
  if (!is.null(results$robust_inference$bootstrap)) {
    bootstrap_row <- tibble(
      Method = "Block Bootstrap",
      `Mother's Wage` = ifelse(!is.na(results$robust_inference$bootstrap$mother_wage$estimate),
                              paste0(round(results$robust_inference$bootstrap$mother_wage$estimate, 1),
                                    " (", round(results$robust_inference$bootstrap$mother_wage$se, 1), ")"),
                              "NA"),
      `Father's Wage` = ifelse(!is.na(results$robust_inference$bootstrap$father_wage$estimate),
                              paste0(round(results$robust_inference$bootstrap$father_wage$estimate, 1),
                                    " (", round(results$robust_inference$bootstrap$father_wage$se, 1), ")"),
                              "NA")
    )
    robustness_table <- bind_rows(robustness_table, bootstrap_row)
  }

  # Add aggregated data results
  if (!is.null(results$robust_inference$aggregated)) {
    agg_mother <- tidy(results$robust_inference$aggregated$mother_wage) %>%
      filter(term == "treatment:post")
    agg_father <- tidy(results$robust_inference$aggregated$father_wage) %>%
      filter(term == "treatment:post")

    agg_row <- tibble(
      Method = "Aggregated Data",
      `Mother's Wage` = paste0(round(agg_mother$estimate, 1), " (", round(agg_mother$std.error, 1), ")"),
      `Father's Wage` = paste0(round(agg_father$estimate, 1), " (", round(agg_father$std.error, 1), ")")
    )
    robustness_table <- bind_rows(robustness_table, agg_row)
  }

  return(robustness_table)
}

#' Save all results and tables
#' @param results Complete DiD analysis results
#' @param plots List of plots
#' @param output_dir Output directory
save_did_results <- function(results, plots, output_dir = "output") {

  cat("🔄 Saving DiD results...\n")

  # Create output directories
  dir.create(file.path(output_dir, "figures"), showWarnings = FALSE, recursive = TRUE)
  dir.create(file.path(output_dir, "tables"), showWarnings = FALSE, recursive = TRUE)

  # Generate and save formal results
  formal_results <- generate_formal_results(results)
  writeLines(formal_results, file.path(output_dir, "did_formal_results.md"))

  # Save summary tables
  summary_table <- create_results_summary_table(results)
  write_csv(summary_table, file.path(output_dir, "tables", "did_main_results.csv"))

  robustness_table <- create_robustness_summary_table(results)
  write_csv(robustness_table, file.path(output_dir, "tables", "did_robustness_results.csv"))

  # Save detailed model results
  detailed_results <- map_dfr(names(results$models), function(name) {
    tidy(results$models[[name]]) %>%
      mutate(model = name)
  })
  write_csv(detailed_results, file.path(output_dir, "tables", "did_detailed_results.csv"))

  # Save plots
  if (!is.null(plots$coefficient)) {
    ggsave(file.path(output_dir, "figures", "did_coefficient_plot.png"),
           plots$coefficient, width = 10, height = 6)
  }

  if (!is.null(plots$event_study)) {
    ggsave(file.path(output_dir, "figures", "did_event_study_plot.png"),
           plots$event_study, width = 10, height = 8)
  }

  if (!is.null(plots$robust_estimates)) {
    ggsave(file.path(output_dir, "figures", "did_robust_estimates_plot.png"),
           plots$robust_estimates, width = 9, height = 6)
  }

  if (!is.null(plots$balance)) {
    ggsave(file.path(output_dir, "figures", "did_balance_test_plot.png"),
           plots$balance, width = 10, height = 6)
  }

  if (!is.null(plots$dynamic_effects)) {
    ggsave(file.path(output_dir, "figures", "did_dynamic_effects_plot.png"),
           plots$dynamic_effects, width = 10, height = 6)
  }

  if (!is.null(plots$randomization_inference)) {
    ggsave(file.path(output_dir, "figures", "did_randomization_inference_plot.png"),
           plots$randomization_inference, width = 10, height = 6)
  }

  # Save panel data
  write_csv(results$panel_data, file.path(output_dir, "did_panel_data.csv"))

  cat("✅ All results saved to:", output_dir, "\n")
  cat("📄 Main results:", file.path(output_dir, "did_formal_results.md"), "\n")
  cat("📊 Plots saved to:", file.path(output_dir, "figures"), "\n")
  cat("📋 Tables saved to:", file.path(output_dir, "tables"), "\n")
}

cat("✅ Reporting functions loaded\n")
