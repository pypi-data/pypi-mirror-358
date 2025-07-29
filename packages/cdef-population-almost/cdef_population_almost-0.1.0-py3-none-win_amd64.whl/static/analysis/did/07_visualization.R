# ===== PHASE 7: VISUALIZATION & REPORTING =====
# Publication-ready plots and visualization functions
# Author: Tobias Kragholm
# Date: 2025-06-26

#' Create main coefficient plot for DiD estimates
#' @param models List of fitted models
#' @return ggplot object
create_coefficient_plot <- function(models) {

  cat("🔄 Creating coefficient plot...\n")

  # Extract DiD estimates from all models
  did_estimates <- map_dfr(names(models), function(model_name) {
    model <- models[[model_name]]
    coef_data <- tidy(model, conf.int = TRUE) %>%
      filter(term == "treatment:post") %>%
      mutate(
        model_name = model_name,
        outcome = case_when(
          str_detect(model_name, "mother.*wage") ~ "Mother's Wage",
          str_detect(model_name, "father.*wage") ~ "Father's Wage",
          str_detect(model_name, "mother.*total") ~ "Mother's Total Income",
          str_detect(model_name, "father.*total") ~ "Father's Total Income",
          TRUE ~ "Other"
        ),
        model_type = case_when(
          str_detect(model_name, "simple") ~ "Simple",
          str_detect(model_name, "full") ~ "With Controls",
          str_detect(model_name, "floored") ~ "Floored Income",
          str_detect(model_name, "neg_control") ~ "Negative Control",
          TRUE ~ "Standard"
        )
      )
  })

  # Create coefficient plot
  plot <- ggplot(did_estimates, aes(x = outcome, y = estimate, color = model_type)) +
    geom_point(position = position_dodge(width = 0.5), size = 3) +
    geom_errorbar(
      aes(ymin = conf.low, ymax = conf.high),
      position = position_dodge(width = 0.5),
      width = 0.2
    ) +
    geom_hline(yintercept = 0, linetype = "dashed", color = "gray50") +
    coord_flip() +
    scale_y_continuous(labels = scales::label_number(scale = 1/1000, suffix = "k")) +
    labs(
      title = "DiD Treatment Effect Estimates Across Income Types",
      subtitle = "Points show coefficient estimates with 95% confidence intervals",
      x = NULL,
      y = "Estimated Treatment Effect (thousands DKK)",
      color = "Model Type"
    ) +
    theme_minimal() +
    theme(
      legend.position = "bottom",
      plot.title = element_text(size = 14, face = "bold"),
      plot.subtitle = element_text(size = 10, color = "gray30"),
      panel.grid.minor = element_blank(),
      axis.title = element_text(face = "bold"),
      axis.text.y = element_text(face = "bold")
    ) +
    scale_color_brewer(palette = "Set1")

  return(plot)
}

#' Create event study plot
#' @param event_coefficients Event study coefficients
#' @return ggplot object
create_event_study_plot <- function(event_coefficients) {

  cat("🔄 Creating event study plot...\n")

  plot <- ggplot(event_coefficients, aes(x = time, y = estimate, color = parent)) +
    geom_point(position = position_dodge(width = 0.3), size = 3) +
    geom_errorbar(
      aes(ymin = conf.low, ymax = conf.high),
      width = 0.2, position = position_dodge(width = 0.3)
    ) +
    geom_line(position = position_dodge(width = 0.3)) +
    geom_hline(yintercept = 0, linetype = "dashed", color = "gray50") +
    geom_vline(xintercept = -0.5, linetype = "dashed", color = "gray50") +
    facet_wrap(~parent, scales = "free_y", ncol = 1) +
    labs(
      title = "Event Study: Dynamic Treatment Effects",
      subtitle = "Difference between treatment and control groups by event time",
      x = "Time Relative to Treatment",
      y = "Estimated Effect (thousands DKK)",
      color = "Parent"
    ) +
    theme_minimal() +
    theme(
      legend.position = "bottom",
      plot.title = element_text(size = 14, face = "bold"),
      plot.subtitle = element_text(size = 10, color = "gray30"),
      strip.text = element_text(size = 11, face = "bold")
    ) +
    scale_color_brewer(palette = "Set1") +
    scale_x_continuous(breaks = function(x) seq(min(x), max(x), 1))

  return(plot)
}

#' Create robust estimates comparison plot
#' @param robust_inference Robust inference results
#' @return ggplot object
create_robust_comparison_plot <- function(robust_inference) {

  cat("🔄 Creating robust estimates comparison plot...\n")

  # Extract estimates from different methods
  robust_estimates <- bind_rows(
    # Bootstrap results
    tibble(
      method = "Block Bootstrap",
      outcome = c("Mother's Wage", "Father's Wage"),
      estimate = c(robust_inference$bootstrap$mother_wage$estimate,
                   robust_inference$bootstrap$father_wage$estimate),
      std.error = c(robust_inference$bootstrap$mother_wage$se,
                    robust_inference$bootstrap$father_wage$se)
    ),

    # Aggregated data results
    tidy(robust_inference$aggregated$mother_wage) %>%
      filter(term == "treatment:post") %>%
      mutate(method = "Aggregated Data", outcome = "Mother's Wage"),

    tidy(robust_inference$aggregated$father_wage) %>%
      filter(term == "treatment:post") %>%
      mutate(method = "Aggregated Data", outcome = "Father's Wage")
  ) %>%
  filter(!is.na(estimate))

  if (nrow(robust_estimates) > 0) {
    plot <- ggplot(robust_estimates, aes(x = method, y = estimate, color = outcome)) +
      geom_point(size = 3, position = position_dodge(width = 0.5)) +
      geom_errorbar(
        aes(ymin = estimate - 1.96*std.error,
            ymax = estimate + 1.96*std.error),
        width = 0.2,
        position = position_dodge(width = 0.5)
      ) +
      geom_hline(yintercept = 0, linetype = "dashed") +
      coord_flip() +
      scale_y_continuous(labels = scales::label_number(scale = 1/1000, suffix = "k")) +
      labs(
        title = "DiD Estimates Across Different Methods",
        subtitle = "Point estimates with 95% confidence intervals",
        x = NULL,
        y = "Estimated Treatment Effect (thousands DKK)",
        color = "Outcome"
      ) +
      theme_minimal() +
      theme(
        legend.position = "bottom",
        plot.title = element_text(size = 14, face = "bold"),
        plot.subtitle = element_text(size = 10, color = "gray30"),
        panel.grid.minor = element_blank(),
        axis.title = element_text(face = "bold")
      ) +
      scale_color_brewer(palette = "Set1")
  } else {
    plot <- ggplot() +
      labs(title = "No robust estimates available for plotting") +
      theme_minimal()
  }

  return(plot)
}

#' Create balance test plot
#' @param balance_results Balance test results
#' @return ggplot object
create_balance_plot <- function(balance_results) {

  cat("🔄 Creating balance test plot...\n")

  if (nrow(balance_results) > 0) {
    plot <- ggplot(balance_results, aes(x = time, y = estimate, color = variable_label)) +
      geom_point(position = position_dodge(width = 0.3)) +
      geom_errorbar(
        aes(ymin = conf.low, ymax = conf.high),
        width = 0.2, position = position_dodge(width = 0.3)
      ) +
      geom_hline(yintercept = 0, linetype = "dashed", color = "gray50") +
      geom_vline(xintercept = -0.5, linetype = "dashed", color = "gray50") +
      facet_wrap(~parent, ncol = 1) +
      labs(
        title = "Balance Test: Covariate Differences by Event Time",
        subtitle = "Testing for differential trends in covariates",
        x = "Time Relative to Treatment",
        y = "Estimated Difference",
        color = "Covariate"
      ) +
      theme_minimal() +
      theme(
        legend.position = "bottom",
        plot.title = element_text(size = 14, face = "bold"),
        plot.subtitle = element_text(size = 10, color = "gray30")
      ) +
      scale_color_brewer(palette = "Set2") +
      scale_x_continuous(breaks = seq(-5, 5, 1))
  } else {
    plot <- ggplot() +
      labs(title = "No balance test results available for plotting") +
      theme_minimal()
  }

  return(plot)
}

#' Create dynamic effects plot
#' @param dynamic_coefficients Dynamic effects coefficients
#' @return ggplot object
create_dynamic_effects_plot <- function(dynamic_coefficients) {

  cat("🔄 Creating dynamic effects plot...\n")

  plot <- ggplot(dynamic_coefficients, aes(x = time, y = estimate, color = parent, shape = bin_type)) +
    geom_point(size = 3, position = position_dodge(width = 0.3)) +
    geom_errorbar(
      aes(ymin = conf.low, ymax = conf.high),
      width = 0.2, position = position_dodge(width = 0.3)
    ) +
    geom_line(
      data = dynamic_coefficients %>% filter(bin_type == "Regular"),
      position = position_dodge(width = 0.3)
    ) +
    geom_hline(yintercept = 0, linetype = "dashed", color = "gray50") +
    geom_vline(xintercept = -0.5, linetype = "dashed", color = "gray50") +
    labs(
      title = "Dynamic Treatment Effects with Binned Endpoints",
      subtitle = "Long-run effects with binned distant periods",
      x = "Time Relative to Treatment",
      y = "Estimated Effect (thousands DKK)",
      color = "Parent",
      shape = "Period Type"
    ) +
    theme_minimal() +
    theme(
      legend.position = "bottom",
      plot.title = element_text(size = 14, face = "bold"),
      plot.subtitle = element_text(size = 10, color = "gray30")
    ) +
    scale_color_brewer(palette = "Set1") +
    scale_shape_manual(values = c("Pre-bin" = 17, "Regular" = 19, "Post-bin" = 15))

  return(plot)
}

#' Create randomization inference plot
#' @param ri_results Randomization inference results
#' @return ggplot object
create_randomization_inference_plot <- function(ri_results) {

  cat("🔄 Creating randomization inference plot...\n")

  # Create distribution plot
  ri_data <- ri_results$permuted_effects %>%
    select(mother_effect, father_effect) %>%
    pivot_longer(everything(), names_to = "parent", values_to = "effect") %>%
    mutate(
      parent = ifelse(parent == "mother_effect", "Mother", "Father")
    ) %>%
    filter(!is.na(effect))

  actual_effects_df <- tibble(
    parent = c("Mother", "Father"),
    actual = c(ri_results$actual_effects["mother"], ri_results$actual_effects["father"])
  )

  plot <- ggplot(ri_data, aes(x = effect)) +
    geom_histogram(bins = 50, alpha = 0.7, fill = "lightblue") +
    geom_vline(data = actual_effects_df, aes(xintercept = actual),
               color = "red", linetype = "dashed", size = 1) +
    facet_wrap(~parent, scales = "free", ncol = 1) +
    labs(
      title = "Randomization Inference: Distribution of Placebo Effects",
      subtitle = "Red line shows actual treatment effect",
      x = "Treatment Effect (thousands DKK)",
      y = "Frequency"
    ) +
    theme_minimal() +
    theme(
      plot.title = element_text(size = 14, face = "bold"),
      plot.subtitle = element_text(size = 10, color = "gray30"),
      strip.text = element_text(size = 11, face = "bold")
    )

  return(plot)
}

#' Create all DiD visualizations
#' @param results Complete DiD results
#' @return List of plots
create_did_visualizations <- function(results) {

  cat("🔄 Creating all DiD visualizations...\n")

  plots <- list(
    coefficient = create_coefficient_plot(results$models),
    event_study = create_event_study_plot(results$event_study$coefficients),
    robust_estimates = create_robust_comparison_plot(results$robust_inference),
    balance = create_balance_plot(results$balance_tests),
    dynamic_effects = create_dynamic_effects_plot(results$dynamic_effects$coefficients)
  )

  # Add randomization inference plot if available
  if (!is.null(results$randomization_inference)) {
    plots$randomization_inference <- create_randomization_inference_plot(results$randomization_inference)
  }

  cat("✅ All visualizations created\n")

  return(plots)
}

cat("✅ Visualization functions loaded\n")
