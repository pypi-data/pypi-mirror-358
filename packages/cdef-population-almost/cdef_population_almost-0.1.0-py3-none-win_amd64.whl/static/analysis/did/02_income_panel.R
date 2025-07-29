# ===== PHASE 2: INCOME DATA PANEL CONSTRUCTION =====
# Parent-level panel with income data functions
# Author: Tobias Kragholm
# Date: 2025-06-26

#' Create parent-level panel with income data
#' @param basic_data Core panel structure from create_panel_dataset
#' @param income_data Time series income data by parent
#' @return Panel dataset with parent income data
create_parent_panel <- function(basic_data, income_data) {

  cat("🔄 Creating parent-level panel...\n")

  # Expand basic structure to yearly panel for both parents
  parent_panel <- basic_data %>%
    # Create separate rows for fathers and mothers
    crossing(relationship = c("father", "mother")) %>%
    # Add treatment timing variables
    mutate(
      # Create unique parent identifier
      parent_id = paste(match_id, individual_type, relationship, sep = "_")
    ) %>%
    # Filter to reasonable time window for analysis
    filter(time_to_treatment >= -5 & time_to_treatment <= 10)

  cat("📊 Parent panel created with", nrow(parent_panel), "parent-year observations\n")

  # Join with income data
  cat("🔄 Joining with income data...\n")

  panel_with_income <- parent_panel %>%
    left_join(
      income_data %>%
        select(match_id, individual_type, relationship, year, total_income, salary),
      by = c("match_id", "individual_type", "relationship", "year")
    ) %>%
    # Handle income data and create analysis variables
    group_by(parent_id) %>%
    arrange(year) %>%
    mutate(
      # Convert to thousands DKK (matching previous analysis units)
      income = total_income / 1000,
      wage_income = salary / 1000,

      # Create flags for negative income (for sensitivity analysis)
      income_negative = ifelse(income < 0, 1, 0),
      wage_negative = ifelse(wage_income < 0, 1, 0),

      # Create zero-floored versions
      income_floored = pmax(income, 0, na.rm = TRUE),
      wage_income_floored = pmax(wage_income, 0, na.rm = TRUE)
    ) %>%
    ungroup()

  # Report income data coverage
  income_coverage <- panel_with_income %>%
    summarise(
      wage_coverage = mean(!is.na(wage_income)) * 100,
      total_income_coverage = mean(!is.na(income)) * 100,
      negative_wage_pct = mean(wage_income < 0, na.rm = TRUE) * 100,
      zero_wage_pct = mean(wage_income == 0, na.rm = TRUE) * 100
    )

  cat("📊 Income data coverage:\n")
  cat("   - Wage income:", round(income_coverage$wage_coverage, 1), "%\n")
  cat("   - Total income:", round(income_coverage$total_income_coverage, 1), "%\n")
  cat("   - Negative wages:", round(income_coverage$negative_wage_pct, 1), "%\n")
  cat("   - Zero wages:", round(income_coverage$zero_wage_pct, 1), "%\n")

  return(panel_with_income)
}

cat("✅ Income panel functions loaded\n")
