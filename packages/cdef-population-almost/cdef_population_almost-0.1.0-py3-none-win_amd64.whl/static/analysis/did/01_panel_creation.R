# ===== PHASE 1: DATA STRUCTURE TRANSFORMATION =====
# Panel data creation functions for DiD analysis
# Author: Tobias Kragholm
# Date: 2025-06-26

#' Transform current CDEF data to panel format
#' @param child_data Basic child data with match_id, individual_type, case_index_date
#' @param parent_data Parent demographic data
#' @param income_data Time series income data
#' @param demographics_data Time series demographic data
#' @return Panel dataset with treatment timing variables
create_panel_dataset <- function(child_data, parent_data, income_data, demographics_data) {

  cat("🔄 Creating core panel structure...\n")

  # Create the core panel structure
  panel_data <- child_data %>%
    # Create treatment timing variable
    mutate(
      treatment_year = year(case_index_date),
      never_treated = ifelse(individual_type == "control", 0, treatment_year),
      treatment = ifelse(individual_type == "case", 1, 0)
    ) %>%
    # Expand to create yearly observations (reasonable time window around treatment)
    crossing(year = 2000:2023) %>%
    # Create time-to-treatment variable
    mutate(
      time_to_treatment = year - treatment_year,
      treated = ifelse(individual_type == "case" & year >= treatment_year, 1, 0),
      post = ifelse(time_to_treatment >= 0, 1, 0),
      # Create unit identifier for DiD
      id = match_id
    ) %>%
    # Filter to reasonable time window (±10 years around treatment)
    filter(time_to_treatment >= -10 & time_to_treatment <= 10) %>%
    # Add case index date for reference
    select(id, match_id, individual_type, year, treatment_year, case_index_date,
           time_to_treatment, treatment, treated, post, never_treated)

  cat("✅ Panel structure created with", nrow(panel_data), "observations\n")
  cat("📊 Treatment years range:", range(panel_data$treatment_year[panel_data$treatment == 1]), "\n")
  cat("📊 Time window:", range(panel_data$time_to_treatment), "years around treatment\n")

  return(panel_data)
}

cat("✅ Panel creation functions loaded\n")
