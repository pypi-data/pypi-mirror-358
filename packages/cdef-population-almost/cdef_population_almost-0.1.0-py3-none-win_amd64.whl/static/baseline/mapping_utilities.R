#!/usr/bin/env Rscript
# ==============================================================================
# Mapping Utilities for Danish Registry Data
# ==============================================================================
# This script loads and provides mapping functions for Danish registry codes
# including countries, education (ISCED), employment (SOCIO13), civil status,
# regions, and other demographic variables.
# 
# All mappings are loaded from JSON files in static/mappings/
# ==============================================================================

# Load required libraries
suppressPackageStartupMessages({
  library(jsonlite)
  library(dplyr)
  library(stringr)
  library(readr)
})

# ==============================================================================
# MAPPING DATA LOADER
# ==============================================================================

#' Load all mapping files from static directory
#' @param mappings_path Path to the mappings directory
#' @return Named list containing all mappings
load_all_mappings <- function(mappings_path = "static/mappings") {
  
  cat("Loading mapping files from:", mappings_path, "\n")
  
  # Initialize mappings list
  mappings <- list()
  
  # Define JSON mapping files to load
  json_files <- c(
    "countries", "isced", "socio13", "koen", "civst", 
    "reg", "fm_mark", "hustype", "statsb", "icd10", 
    "scd", "plads"
  )
  
  # Load JSON files
  for (file_name in json_files) {
    file_path <- file.path(mappings_path, paste0(file_name, ".json"))
    if (file.exists(file_path)) {
      tryCatch({
        mappings[[file_name]] <- fromJSON(file_path, flatten = TRUE)
        cat("✓ Loaded", file_name, "mapping\n")
      }, error = function(e) {
        warning(paste("Failed to load", file_name, ":", e$message))
        mappings[[file_name]] <- list()
      })
    } else {
      warning(paste("Mapping file not found:", file_path))
      mappings[[file_name]] <- list()
    }
  }
  
  # Load CSV files (like ICD-10 codes)
  csv_files <- c("icd10-codes_DA")
  for (file_name in csv_files) {
    file_path <- file.path(mappings_path, paste0(file_name, ".csv"))
    if (file.exists(file_path)) {
      tryCatch({
        mappings[[str_replace(file_name, "-", "_")]] <- read_csv(file_path, col_types = cols(.default = "c"))
        cat("✓ Loaded", file_name, "mapping\n")
      }, error = function(e) {
        warning(paste("Failed to load", file_name, ":", e$message))
        mappings[[str_replace(file_name, "-", "_")]] <- data.frame()
      })
    }
  }
  
  cat("Mapping files loaded successfully!\n")
  return(mappings)
}

# ==============================================================================
# COUNTRY OF ORIGIN MAPPING FUNCTIONS
# ==============================================================================

#' Map country codes to country names and regions
#' @param country_codes Vector of country codes
#' @param mappings Mappings list from load_all_mappings()
#' @param output_language "en" for English, "da" for Danish
#' @return Character vector of country names or regions
map_countries <- function(country_codes, mappings, output_language = "en") {
  
  country_map <- mappings$countries
  
  # Map to country names first
  country_names <- sapply(country_codes, function(code) {
    if (is.na(code)) return(NA)
    country_map[[as.character(code)]] %||% "Unknown"
  })
  
  # For English output, create regional groupings
  if (output_language == "en") {
    result <- case_when(
      is.na(country_codes) ~ "Missing/Unknown",
      country_codes == "5100" ~ "Denmark",
      country_codes %in% c("5110", "5120", "5130", "5140", "5150") ~ "Nordic Countries",
      str_detect(country_codes, "^51[6-9]|^52|^53") ~ "Other European",
      str_detect(country_codes, "^54") ~ "Middle East/North Africa",
      str_detect(country_codes, "^55") ~ "Sub-Saharan Africa",
      str_detect(country_codes, "^56") ~ "Asia",
      str_detect(country_codes, "^57") ~ "Americas",
      str_detect(country_codes, "^58") ~ "Oceania",
      TRUE ~ "Other/Unknown"
    )
  } else {
    # Return Danish names
    result <- ifelse(is.na(country_names), "Ukendt", country_names)
  }
  
  return(result)
}

#' Get detailed country categories for analysis
#' @param country_codes Vector of country codes
#' @param mappings Mappings list
#' @return Factor with detailed country categories
categorize_countries_detailed <- function(country_codes, mappings) {
  categories <- map_countries(country_codes, mappings, "en")
  factor(categories, levels = c(
    "Denmark", "Nordic Countries", "Other European", 
    "Middle East/North Africa", "Sub-Saharan Africa", 
    "Asia", "Americas", "Oceania", "Other/Unknown", "Missing/Unknown"
  ))
}

# ==============================================================================
# EDUCATION MAPPING FUNCTIONS (ISCED)
# ==============================================================================

#' Get standard education factor levels (single source of truth)
#' @return Character vector of factor levels in proper order
get_education_factor_levels <- function() {
  c(
    "Primary/Lower Secondary (ISCED 1-2)",
    "Upper Secondary/Post-Secondary (ISCED 3-4)",
    "Bachelor/Master (ISCED 5-6)",
    "Master/Doctoral (ISCED 7-8)",
    "Missing/Unknown"
  )
}

#' Convert ISCED numbers to grouped education categories
#' @param isced_numbers Vector of ISCED numbers (as character)
#' @return Factor with education categories
isced_to_grouped_categories <- function(isced_numbers) {
  
  # Convert ISCED numbers to grouped categories
  # Consolidate all missing/unknown/not classified into single category
  categories <- case_when(
    is.na(isced_numbers) ~ "Missing/Unknown",
    isced_numbers %in% c("1", "2") ~ "Primary/Lower Secondary (ISCED 1-2)",
    isced_numbers %in% c("3", "4") ~ "Upper Secondary/Post-Secondary (ISCED 3-4)",
    isced_numbers %in% c("5", "6") ~ "Bachelor/Master (ISCED 5-6)",
    isced_numbers %in% c("7", "8") ~ "Master/Doctoral (ISCED 7-8)",
    isced_numbers == "9" ~ "Missing/Unknown",  # Not classified -> Missing/Unknown
    TRUE ~ "Missing/Unknown"  # Any other unknown values
  )
  
  # Return as ordered factor
  factor(categories, levels = get_education_factor_levels())
}

#' Map education codes to ISCED levels
#' @param education_codes Vector of education codes (HFAUDD)
#' @param mappings Mappings list
#' @param output_type "isced_number", "isced_category", or "grouped"
#' @return Vector of education categories
map_education <- function(education_codes, mappings, output_type = "grouped") {
  
  isced_map <- mappings$isced
  
  # Map to ISCED numbers first
  isced_numbers <- sapply(education_codes, function(code) {
    if (is.na(code)) return(NA)
    isced_map[[as.character(code)]] %||% "9"
  })
  
  if (output_type == "isced_number") {
    return(isced_numbers)
  }
  
  if (output_type == "isced_category") {
    # Detailed ISCED categories
    categories <- case_when(
      is.na(isced_numbers) ~ "Missing/Unknown",
      isced_numbers == "1" ~ "ISCED 1: Primary Education",
      isced_numbers == "2" ~ "ISCED 2: Lower Secondary",
      isced_numbers == "3" ~ "ISCED 3: Upper Secondary",
      isced_numbers == "4" ~ "ISCED 4: Post-Secondary Non-Tertiary",
      isced_numbers == "5" ~ "ISCED 5: Short-cycle Tertiary",
      isced_numbers == "6" ~ "ISCED 6: Bachelor/Long-cycle Tertiary",
      isced_numbers == "7" ~ "ISCED 7: Master Level",
      isced_numbers == "8" ~ "ISCED 8: Doctoral Level",
      isced_numbers == "9" ~ "Not Classified",
      TRUE ~ "Unknown"
    )
    return(categories)
  }
  
  # Grouped categories (default)
  isced_to_grouped_categories(isced_numbers)
}

#' Get highest education in household
#' @param father_education Father's education code
#' @param mother_education Mother's education code
#' @param mappings Mappings list
#' @return Factor with highest household education
get_highest_household_education <- function(father_education, mother_education, mappings) {
  
  # Get ISCED numbers for both parents
  father_isced <- as.numeric(map_education(father_education, mappings, "isced_number"))
  mother_isced <- as.numeric(map_education(mother_education, mappings, "isced_number"))
  
  # Handle missing values and "Not Classified" (treat as 0 for comparison)
  father_isced[is.na(father_isced) | father_isced == 9] <- 0
  mother_isced[is.na(mother_isced) | mother_isced == 9] <- 0
  
  # Get highest ISCED level
  highest_isced <- pmax(father_isced, mother_isced, na.rm = TRUE)
  
  # Convert back to character for consistent processing
  highest_isced_char <- as.character(highest_isced)
  highest_isced_char[highest_isced == 0] <- NA
  
  # Use the same categorization function
  isced_to_grouped_categories(highest_isced_char)
}

# ==============================================================================
# EMPLOYMENT MAPPING FUNCTIONS (SOCIO13)
# ==============================================================================

#' Get standard employment factor levels (single source of truth)
#' @return Character vector of factor levels in proper order
get_employment_factor_levels <- function() {
  c(
    "Self-employed",
    "Employees", 
    "Unemployed/Benefits",
    "Students/Education",
    "Pensioners",
    "Missing/Unknown"
  )
}

#' Convert SOCIO13 codes to grouped employment categories
#' @param socio13_codes Vector of SOCIO13 codes (as numeric)
#' @return Factor with employment categories
socio13_to_grouped_categories <- function(socio13_codes) {
  
  # Convert SOCIO13 codes to meaningful grouped categories
  # Based on official Danish Statistics SOCIO13 classification
  categories <- case_when(
    is.na(socio13_codes) ~ "Missing/Unknown",
    socio13_codes == 0 ~ "Missing/Unknown",  # Not in AKM
    
    # Self-employed (110-120)
    socio13_codes >= 110 & socio13_codes <= 120 ~ "Self-employed",
    
    # Employees (131-139) - all types of employees
    socio13_codes >= 131 & socio13_codes <= 139 ~ "Employees",
    
    # Unemployed and social benefits (210-330)
    socio13_codes %in% c(210, 220, 330) ~ "Unemployed/Benefits",
    
    # Students and education (310)
    socio13_codes == 310 ~ "Students/Education",
    
    # Pensioners (321-323)
    socio13_codes >= 321 & socio13_codes <= 323 ~ "Pensioners",
    
    # Other categories (410, 420) -> Missing/Unknown
    socio13_codes %in% c(410, 420) ~ "Missing/Unknown",
    
    # Any other unknown values
    TRUE ~ "Missing/Unknown"
  )
  
  # Return as ordered factor
  factor(categories, levels = get_employment_factor_levels())
}

#' Map SOCIO13 codes to employment categories
#' @param socio13_codes Vector of SOCIO13 codes
#' @param mappings Mappings list
#' @param output_type "detailed", "grouped", or "binary"
#' @return Vector of employment categories
map_employment <- function(socio13_codes, mappings, output_type = "grouped") {
  
  socio13_map <- mappings$socio13
  
  if (output_type == "detailed") {
    # Return detailed Danish descriptions from mapping file
    detailed <- sapply(socio13_codes, function(code) {
      if (is.na(code)) return("Missing/Unknown")
      socio13_map[[as.character(code)]] %||% "Missing/Unknown"
    })
    return(detailed)
  }
  
  # Convert to numeric for categorization
  numeric_codes <- as.numeric(socio13_codes)
  
  if (output_type == "binary") {
    # Simple employed vs not employed
    result <- case_when(
      is.na(numeric_codes) ~ "Missing/Unknown",
      numeric_codes >= 110 & numeric_codes <= 139 ~ "Employed",
      TRUE ~ "Not Employed"
    )
    return(result)
  }
  
  # Grouped categories (default)
  socio13_to_grouped_categories(numeric_codes)
}

# ==============================================================================
# DEMOGRAPHIC MAPPING FUNCTIONS
# ==============================================================================

#' Map gender codes to readable labels
#' @param gender_codes Vector of gender codes
#' @param mappings Mappings list
#' @param output_language "en" for English, "da" for Danish
#' @return Character vector of gender labels
map_gender <- function(gender_codes, mappings, output_language = "en") {
  
  if (output_language == "en") {
    result <- case_when(
      is.na(gender_codes) ~ "Missing/Unknown",
      gender_codes %in% c("1", "M") ~ "Male",
      gender_codes %in% c("2", "F") ~ "Female",
      TRUE ~ "Other/Unknown"
    )
  } else {
    result <- case_when(
      is.na(gender_codes) ~ "Ukendt",
      gender_codes %in% c("1", "M") ~ "Mand",
      gender_codes %in% c("2", "F") ~ "Kvinde",
      TRUE ~ "Andet/Ukendt"
    )
  }
  
  return(result)
}

#' Map civil status codes to categories
#' @param civil_status_codes Vector of civil status codes
#' @param mappings Mappings list
#' @param output_language "en" for English, "da" for Danish
#' @return Character vector of civil status categories
map_civil_status <- function(civil_status_codes, mappings, output_language = "en") {
  
  civst_map <- mappings$civst
  
  if (output_language == "en") {
    result <- case_when(
      is.na(civil_status_codes) ~ "Missing/Unknown",
      civil_status_codes == "U" ~ "Single/Unmarried",
      civil_status_codes %in% c("G", "P") ~ "Married/Partnership",
      civil_status_codes == "F" ~ "Divorced",
      civil_status_codes == "E" ~ "Widowed",
      civil_status_codes == "D" ~ "Deceased",
      TRUE ~ "Other/Unknown"
    )
  } else {
    # Return Danish descriptions from mapping
    result <- sapply(civil_status_codes, function(code) {
      if (is.na(code)) return("Ukendt")
      civst_map[[as.character(code)]] %||% "Ukendt"
    })
  }
  
  return(result)
}

#' Map region codes to region names
#' @param region_codes Vector of region codes
#' @param mappings Mappings list
#' @param output_language "en" for English, "da" for Danish
#' @return Character vector of region names
map_regions <- function(region_codes, mappings, output_language = "en") {
  
  reg_map <- mappings$reg
  
  if (output_language == "da") {
    # Return Danish region names
    result <- sapply(region_codes, function(code) {
      if (is.na(code)) return("Ukendt")
      reg_map[[as.character(code)]] %||% "Ukendt"
    })
  } else {
    # Convert to English
    result <- case_when(
      is.na(region_codes) ~ "Missing/Unknown",
      region_codes == "81" ~ "North Jutland",
      region_codes == "82" ~ "Central Jutland", 
      region_codes == "83" ~ "Southern Denmark",
      region_codes == "84" ~ "Capital Region",
      region_codes == "85" ~ "Zealand",
      TRUE ~ "Other/Unknown"
    )
  }
  
  return(result)
}

# ==============================================================================
# AGE GROUPING FUNCTIONS
# ==============================================================================

#' Create age groups for children
#' @param ages Vector of ages in years
#' @param group_type "detailed", "broad", or "custom"
#' @return Factor with age groups
create_child_age_groups <- function(ages, group_type = "detailed") {
  
  if (group_type == "detailed") {
    categories <- case_when(
      is.na(ages) ~ "Missing",
      ages < 1 ~ "0 years",
      ages >= 1 & ages < 2 ~ "1 year",
      ages >= 2 & ages < 3 ~ "2 years",
      ages >= 3 & ages < 4 ~ "3 years",
      ages >= 4 & ages < 5 ~ "4 years",
      ages >= 5 & ages < 6 ~ "5 years",
      ages >= 6 ~ "6+ years",
      TRUE ~ "Missing"
    )
    levels_order <- c("0 years", "1 year", "2 years", "3 years", "4 years", "5 years", "6+ years", "Missing")
  } else if (group_type == "broad") {
    categories <- case_when(
      is.na(ages) ~ "Missing",
      ages < 1 ~ "Infants (0 years)",
      ages >= 1 & ages < 3 ~ "Toddlers (1-2 years)",
      ages >= 3 & ages < 6 ~ "Preschool (3-5 years)",
      ages >= 6 ~ "School age (6+ years)",
      TRUE ~ "Missing"
    )
    levels_order <- c("Infants (0 years)", "Toddlers (1-2 years)", "Preschool (3-5 years)", "School age (6+ years)", "Missing")
  }
  
  return(factor(categories, levels = levels_order))
}

#' Create age groups for parents
#' @param ages Vector of ages in years
#' @return Factor with parent age groups
create_parent_age_groups <- function(ages) {
  categories <- case_when(
    is.na(ages) ~ "Missing",
    ages < 20 ~ "<20 years",
    ages >= 20 & ages < 25 ~ "20-24 years",
    ages >= 25 & ages < 30 ~ "25-29 years",
    ages >= 30 & ages < 35 ~ "30-34 years",
    ages >= 35 & ages < 40 ~ "35-39 years",
    ages >= 40 & ages < 45 ~ "40-44 years",
    ages >= 45 & ages < 50 ~ "45-49 years",
    ages >= 50 ~ "50+ years",
    TRUE ~ "Missing"
  )
  
  levels_order <- c("<20 years", "20-24 years", "25-29 years", "30-34 years", 
                   "35-39 years", "40-44 years", "45-49 years", "50+ years", "Missing")
  
  return(factor(categories, levels = levels_order))
}

# ==============================================================================
# FAMILY STRUCTURE FUNCTIONS
# ==============================================================================

#' Categorize family size
#' @param family_sizes Vector of family sizes (number of children)
#' @return Factor with family size categories
categorize_family_size <- function(family_sizes) {
  categories <- case_when(
    is.na(family_sizes) ~ "Missing",
    family_sizes == 1 ~ "Only child",
    family_sizes == 2 ~ "2 children",
    family_sizes == 3 ~ "3 children",
    family_sizes >= 4 ~ "4+ children",
    TRUE ~ "Missing"
  )
  
  levels_order <- c("Only child", "2 children", "3 children", "4+ children", "Missing")
  return(factor(categories, levels = levels_order))
}

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

#' Null coalescing operator
#' @param x First value
#' @param y Second value (default)
#' @return x if not NULL, otherwise y
`%||%` <- function(x, y) {
  if (is.null(x) || length(x) == 0) y else x
}

#' Create birth decade from birth year
#' @param birth_years Vector of birth years
#' @return Character vector of birth decades
create_birth_decades <- function(birth_years) {
  decades <- paste0(floor(birth_years / 10) * 10, "s")
  decades[is.na(birth_years)] <- "Missing"
  return(decades)
}

#' Export function to test mappings
#' @param mappings_path Path to mappings directory
test_mappings <- function(mappings_path = "static/mappings") {
  
  cat("Testing mapping utilities...\n")
  
  # Load mappings
  mappings <- load_all_mappings(mappings_path)
  
  # Test sample values
  test_countries <- c("5100", "5110", "5390", NA)
  test_education <- c("300", "400", "500", NA)
  test_socio13 <- c(110, 210, 310, NA)
  test_gender <- c("1", "2", "M", "F", NA)
  test_civil <- c("G", "U", "F", NA)
  test_regions <- c("81", "84", "85", NA)
  
  cat("\n--- Testing Results ---\n")
  cat("Countries:", paste(map_countries(test_countries, mappings), collapse = ", "), "\n")
  cat("Education:", paste(map_education(test_education, mappings), collapse = ", "), "\n")
  cat("Employment:", paste(map_employment(test_socio13, mappings), collapse = ", "), "\n")
  cat("Gender:", paste(map_gender(test_gender, mappings), collapse = ", "), "\n")
  cat("Civil Status:", paste(map_civil_status(test_civil, mappings), collapse = ", "), "\n")
  cat("Regions:", paste(map_regions(test_regions, mappings), collapse = ", "), "\n")
  
  cat("\nMapping utilities test completed!\n")
  return(mappings)
}

# Export main function for easy loading
if (!exists("MAPPINGS_LOADED")) {
  MAPPINGS_LOADED <- TRUE
  cat("Mapping utilities loaded. Use load_all_mappings() to initialize.\n")
}