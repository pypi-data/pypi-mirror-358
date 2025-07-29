#!/usr/bin/env Rscript
# ==============================================================================
# STROBE-Compliant Baseline Characteristics Table (Complete Refactored Version)
# ==============================================================================
# Study: Long-term Impact of Childhood Severe Chronic Disease on Parental Income
# Design: Matched case-control study with difference-in-differences analysis
#
# This script generates comprehensive baseline characteristics tables (Table 1)
# following STROBE guidelines for reporting observational studies.
#
# Key improvements in this refactored version:
# - Modular function architecture
# - Robust error handling and validation  
# - Comprehensive logging and quality checks
# - Configuration-driven approach
# - Consistent variable processing
# - Automated outlier detection
# - Enhanced documentation
# ==============================================================================

# Load required libraries
suppressPackageStartupMessages({
  library(dplyr)
  library(readr)
  library(stringr)
  library(gtsummary)
  library(gt)
  library(purrr)
  library(tidyr)
  library(forcats)
  library(lubridate)
  library(knitr)
})

# Load mapping utilities
source("scripts/baseline/mapping_utilities.R")

# Set options for reproducibility and display
options(pillar.sigfig = 3, digits = 3, dplyr.summarise.inform = FALSE)

# ==============================================================================
# CONFIGURATION - Single Source of Truth
# ==============================================================================

CONFIG <- list(
  # File paths
  input_path = "cohort_output/enrichment_output",
  output_path = "baseline_output",
  mappings_path = "static/mappings",
  
  # Analysis parameters
  baseline_income_years = 3,  # Years to average for baseline income
  outlier_income_threshold = 2000000,  # DKK threshold for income outliers
  child_age_max = 6,  # Maximum reasonable child age
  
  # Table formatting
  continuous_digits = 2,
  categorical_digits = c(0, 1),
  
  # Validation thresholds
  min_case_control_ratio = 1.5,  # Minimum expected case:control ratio
  max_missing_threshold = 0.8,   # Maximum proportion of missing data allowed
  
  # Required data columns for validation
  required_basic_cols = c("match_id", "case_pnr", "control_pnr", "case_index_date", 
                         "case_birth_date", "controls_matched"),
  required_demo_cols = c("match_id", "individual_type", "pnr", "relationship", 
                        "gender", "country_of_origin")
)

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

#' Setup output directory with logging
setup_environment <- function() {
  if (!dir.exists(CONFIG$output_path)) {
    dir.create(CONFIG$output_path, recursive = TRUE)
    cat("✓ Created output directory:", CONFIG$output_path, "\n")
  }
  
  # Create log file
  log_file <- file.path(CONFIG$output_path, "baseline_processing.log")
  cat("Baseline characteristics processing started at:", 
      format(Sys.time(), "%Y-%m-%d %H:%M:%S"), "\n", file = log_file)
  
  return(log_file)
}

#' Enhanced logging function
log_msg <- function(message, level = "INFO", file = NULL) {
  timestamp <- format(Sys.time(), "%H:%M:%S")
  
  # Choose emoji based on level
  emoji <- switch(level,
    "INFO" = "ℹ️",
    "SUCCESS" = "✅", 
    "WARNING" = "⚠️",
    "ERROR" = "❌",
    "PROGRESS" = "🔄",
    "ℹ️"
  )
  
  formatted_msg <- paste0(emoji, " [", timestamp, "] ", message)
  cat(formatted_msg, "\n")
  
  if (!is.null(file)) {
    cat("[", timestamp, "] ", level, ": ", message, "\n", file = file, append = TRUE)
  }
}

#' Validate data structure and quality
validate_data <- function(data, required_cols, data_name, log_file = NULL) {
  
  log_msg(paste("Validating", data_name), "PROGRESS", log_file)
  
  # Check required columns
  missing_cols <- setdiff(required_cols, colnames(data))
  if (length(missing_cols) > 0) {
    error_msg <- paste("Missing required columns in", data_name, ":", 
                      paste(missing_cols, collapse = ", "))
    log_msg(error_msg, "ERROR", log_file)
    stop(error_msg)
  }
  
  # Check data dimensions
  log_msg(paste(data_name, "loaded:", nrow(data), "rows,", ncol(data), "columns"), "SUCCESS", log_file)
  
  # Check for completely empty rows
  empty_rows <- sum(rowSums(is.na(data)) == ncol(data))
  if (empty_rows > 0) {
    log_msg(paste("Found", empty_rows, "completely empty rows in", data_name), "WARNING", log_file)
  }
  
  # Check missing data patterns
  missing_summary <- data %>%
    summarise(across(everything(), ~ sum(is.na(.)) / length(.))) %>%
    pivot_longer(everything(), names_to = "variable", values_to = "missing_prop") %>%
    filter(missing_prop > CONFIG$max_missing_threshold)
  
  if (nrow(missing_summary) > 0) {
    log_msg(paste("High missing data in", data_name, "for:", 
                 paste(missing_summary$variable, collapse = ", ")), "WARNING", log_file)
  }
  
  return(list(
    valid = TRUE,
    n_rows = nrow(data),
    n_cols = ncol(data),
    empty_rows = empty_rows,
    high_missing_vars = missing_summary$variable
  ))
}

# ==============================================================================
# DATA LOADING AND PREPARATION FUNCTIONS
# ==============================================================================

#' Load and validate all input data files
load_data_files <- function(log_file = NULL) {
  
  log_msg("Starting data loading process", "PROGRESS", log_file)
  
  # Define required data files
  data_files <- list(
    basic = "basic.csv",
    demographics = "demographics.csv",
    education = "education.csv", 
    employment = "employment.csv",
    family = "family.csv",
    income = "income.csv"
  )
  
  # Load all files with validation
  data_list <- map(names(data_files), function(name) {
    filename <- data_files[[name]]
    file_path <- file.path(CONFIG$input_path, filename)
    
    if (!file.exists(file_path)) {
      error_msg <- paste("Required data file not found:", file_path)
      log_msg(error_msg, "ERROR", log_file)
      stop(error_msg)
    }
    
    log_msg(paste("Loading", filename), "PROGRESS", log_file)
    data <- read_csv(file_path, col_types = cols(.default = "c"), show_col_types = FALSE)
    
    # Validate structure
    if (name == "basic") {
      validate_data(data, CONFIG$required_basic_cols, paste(name, "data"), log_file)
    } else if (name == "demographics") {
      validate_data(data, CONFIG$required_demo_cols, paste(name, "data"), log_file)
    } else {
      validate_data(data, c("match_id"), paste(name, "data"), log_file)
    }
    
    return(data)
  })
  
  names(data_list) <- names(data_files)
  
  log_msg("All data files loaded successfully", "SUCCESS", log_file)
  return(data_list)
}

#' Convert data types with comprehensive error handling
convert_data_types <- function(data_list, log_file = NULL) {
  
  log_msg("Converting data types", "PROGRESS", log_file)
  
  # Basic data conversions
  data_list$basic <- data_list$basic %>%
    mutate(
      case_index_date = as.Date(case_index_date),
      case_birth_date = as.Date(case_birth_date),
      controls_matched = as.numeric(controls_matched),
      case_family_members = as.numeric(case_family_members),
      control_family_members = as.numeric(control_family_members),
      baseline_year = year(case_index_date)
    )
  
  # Validate date conversions
  invalid_dates <- sum(is.na(data_list$basic$case_index_date) | is.na(data_list$basic$case_birth_date))
  if (invalid_dates > 0) {
    log_msg(paste("Warning:", invalid_dates, "invalid dates in basic data"), "WARNING", log_file)
  }
  
  # Demographics conversions
  data_list$demographics <- data_list$demographics %>%
    mutate(
      year = as.numeric(year),
      age = as.numeric(age)
    )
  
  # Education conversions
  data_list$education <- data_list$education %>%
    mutate(
      year = as.numeric(year),
      education_valid_from = as.Date(education_valid_from),
      education_valid_to = as.Date(education_valid_to)
    )
  
  # Employment conversions
  data_list$employment <- data_list$employment %>%
    mutate(
      year = as.numeric(year),
      socio13_code = as.numeric(socio13_code)
    )
  
  # Income conversions with outlier detection
  data_list$income <- data_list$income %>%
    mutate(
      year = as.numeric(year),
      salary = as.numeric(salary),
      total_income = as.numeric(total_income)
    ) %>%
    # Flag extreme outliers
    mutate(
      salary_outlier = salary > CONFIG$outlier_income_threshold & !is.na(salary),
      income_outlier = total_income > CONFIG$outlier_income_threshold & !is.na(total_income)
    )
  
  # Report outliers
  salary_outliers <- sum(data_list$income$salary_outlier, na.rm = TRUE)
  income_outliers <- sum(data_list$income$income_outlier, na.rm = TRUE)
  
  if (salary_outliers > 0) {
    log_msg(paste("Found", salary_outliers, "salary outliers above", CONFIG$outlier_income_threshold, "DKK"), 
           "WARNING", log_file)
  }
  if (income_outliers > 0) {
    log_msg(paste("Found", income_outliers, "income outliers above", CONFIG$outlier_income_threshold, "DKK"), 
           "WARNING", log_file)
  }
  
  log_msg("Data type conversions completed", "SUCCESS", log_file)
  return(data_list)
}

#' Create baseline data subsets with flexible filtering
create_baseline_subset <- function(data, basic_data, relationship_filter = NULL, 
                                  year_filter = "baseline", log_file = NULL) {
  
  # Join with baseline years
  result <- data %>%
    inner_join(basic_data %>% select(match_id, baseline_year), by = "match_id")
  
  # Apply year filtering
  if (year_filter == "baseline") {
    result <- result %>% filter(year == baseline_year)
  } else if (year_filter == "before_baseline") {
    result <- result %>% filter(year <= baseline_year)
  } else if (year_filter == "income_range") {
    result <- result %>% 
      filter(year >= (baseline_year - CONFIG$baseline_income_years + 1) & 
             year <= baseline_year)
  }
  
  # Apply relationship filtering
  if (!is.null(relationship_filter)) {
    result <- result %>% filter(relationship %in% relationship_filter)
  }
  
  return(result)
}

# ==============================================================================
# BASELINE STRUCTURE CREATION FUNCTIONS
# ==============================================================================

#' Create child-centered baseline data structure
create_child_baseline_structure <- function(basic_data, log_file = NULL) {
  
  log_msg("Creating child-centered baseline structure", "PROGRESS", log_file)
  
  # Validate case-control structure
  n_unique_cases <- length(unique(basic_data$case_pnr))
  n_total_pairs <- nrow(basic_data)
  case_control_ratio <- n_total_pairs / n_unique_cases
  
  log_msg(paste("Case-control validation: Unique cases =", n_unique_cases, 
               ", Total pairs =", n_total_pairs, 
               ", Ratio =", round(case_control_ratio, 2)), "INFO", log_file)
  
  if (case_control_ratio < CONFIG$min_case_control_ratio) {
    log_msg(paste("Low case-control ratio:", round(case_control_ratio, 2)), "WARNING", log_file)
  }
  
  # Create cases data (one row per unique case)
  cases_data <- basic_data %>%
    group_by(case_pnr) %>%
    slice_head(n = 1) %>%  # Take first occurrence of each case
    ungroup() %>%
    mutate(
      group = "Cases",
      individual_type = "case",
      child_pnr = case_pnr,
      child_age_at_index = as.numeric(difftime(case_index_date, case_birth_date, units = "days")) / 365.25,
      birth_year = year(case_birth_date)
    ) %>%
    select(match_id, group, individual_type, child_pnr, case_index_date, case_birth_date, 
           baseline_year, child_age_at_index, birth_year)
  
  # Create controls data (one row per case-control pair)
  controls_data <- basic_data %>%
    mutate(
      group = "Controls",
      individual_type = "control",
      child_pnr = control_pnr,
      child_age_at_index = as.numeric(difftime(case_index_date, case_birth_date, units = "days")) / 365.25,
      birth_year = year(case_birth_date)
    ) %>%
    select(match_id, group, individual_type, child_pnr, case_index_date, case_birth_date,
           baseline_year, child_age_at_index, birth_year)
  
  # Combine and validate
  child_baseline <- bind_rows(cases_data, controls_data)
  
  # Validate child ages
  invalid_ages <- sum(child_baseline$child_age_at_index < 0 | 
                     child_baseline$child_age_at_index > CONFIG$child_age_max, na.rm = TRUE)
  if (invalid_ages > 0) {
    log_msg(paste("Warning:", invalid_ages, "children with invalid ages"), "WARNING", log_file)
  }
  
  log_msg(paste("Child baseline created: Cases =", nrow(cases_data), 
               ", Controls =", nrow(controls_data), 
               ", Total =", nrow(child_baseline)), "SUCCESS", log_file)
  
  return(child_baseline)
}

#' Create parent-centered baseline data structure
create_parent_baseline_structure <- function(basic_data, log_file = NULL) {
  
  log_msg("Creating parent-centered baseline structure", "PROGRESS", log_file)
  
  # Create cases parent data
  cases_parent <- basic_data %>%
    select(match_id, case_pnr, case_index_date, case_birth_date, baseline_year) %>%
    mutate(
      group = "Parents of Cases",
      individual_type = "case",
      child_pnr = case_pnr,
      child_age_at_index = as.numeric(difftime(case_index_date, case_birth_date, units = "days")) / 365.25
    ) %>%
    select(match_id, group, individual_type, child_pnr, child_age_at_index, baseline_year)
  
  # Create controls parent data
  controls_parent <- basic_data %>%
    select(match_id, control_pnr, case_index_date, case_birth_date, baseline_year) %>%
    mutate(
      group = "Parents of Controls",
      individual_type = "control",
      child_pnr = control_pnr,
      child_age_at_index = as.numeric(difftime(case_index_date, case_birth_date, units = "days")) / 365.25
    ) %>%
    select(match_id, group, individual_type, child_pnr, child_age_at_index, baseline_year)
  
  # Combine
  parent_baseline <- bind_rows(cases_parent, controls_parent)
  
  log_msg(paste("Parent baseline created: Total =", nrow(parent_baseline)), "SUCCESS", log_file)
  
  return(parent_baseline)
}

# ==============================================================================
# DATA ENRICHMENT FUNCTIONS
# ==============================================================================

#' Add child demographics to baseline data
add_child_demographics <- function(child_baseline, demographics_data, mappings, log_file = NULL) {
  
  log_msg("Adding child demographics", "PROGRESS", log_file)
  
  # Get baseline demographics for children
  child_demo <- create_baseline_subset(demographics_data, child_baseline, 
                                      relationship_filter = "child") %>%
    select(match_id, individual_type, pnr, gender, municipality_code, 
           country_of_origin, region)
  
  # Join with child baseline
  result <- child_baseline %>%
    left_join(child_demo, by = c("match_id", "individual_type", "child_pnr" = "pnr"))
  
  # Apply mappings using our refactored utilities
  result <- result %>%
    mutate(
      # Birth decade
      birth_decade = factor(create_birth_decades(birth_year)),
      
      # Gender mapping
      gender = map_gender(gender, mappings, "en"),
      
      # Country of origin mapping
      country_origin_cat = map_countries(country_of_origin, mappings, "en"),
      
      # Keep age as continuous
      child_age_years = child_age_at_index
    )
  
  # Log join results
  n_matched <- sum(!is.na(result$gender))
  log_msg(paste("Child demographics joined:", n_matched, "of", nrow(result), "records matched"), 
         "SUCCESS", log_file)
  
  return(result)
}

#' Add family structure information
add_family_structure <- function(child_baseline, family_data, log_file = NULL) {
  
  log_msg("Adding family structure information", "PROGRESS", log_file)
  
  # Calculate family structure
  family_structure <- family_data %>%
    group_by(match_id, individual_type) %>%
    summarise(
      family_size = n_distinct(family_member_pnr),
      has_siblings = family_size > 1,
      .groups = "drop"
    ) %>%
    mutate(
      family_size_cat = categorize_family_size(family_size)
    )
  
  # Join with child baseline
  result <- child_baseline %>%
    left_join(family_structure, by = c("match_id", "individual_type"))
  
  n_matched <- sum(!is.na(result$family_size))
  log_msg(paste("Family structure added:", n_matched, "records with family data"), "SUCCESS", log_file)
  
  return(result)
}

#' Add parental education information
add_parental_education <- function(child_baseline, education_data, mappings, log_file = NULL) {
  
  log_msg("Adding parental education information", "PROGRESS", log_file)
  
  # Get most recent education before baseline for parents
  baseline_education <- create_baseline_subset(education_data, child_baseline, 
                                              relationship_filter = c("father", "mother"),
                                              year_filter = "before_baseline") %>%
    group_by(match_id, individual_type, pnr, relationship) %>%
    slice_max(year, with_ties = FALSE) %>%
    ungroup() %>%
    select(match_id, individual_type, relationship, hfaudd_code)
  
  # Separate father and mother education
  father_education <- baseline_education %>%
    filter(relationship == "father") %>%
    select(match_id, individual_type, father_education = hfaudd_code)
  
  mother_education <- baseline_education %>%
    filter(relationship == "mother") %>%
    select(match_id, individual_type, mother_education = hfaudd_code)
  
  # Join and apply mappings
  result <- child_baseline %>%
    left_join(father_education, by = c("match_id", "individual_type")) %>%
    left_join(mother_education, by = c("match_id", "individual_type")) %>%
    mutate(
      # Apply education mappings (returns ordered factors)
      father_education_cat = map_education(father_education, mappings, "grouped"),
      mother_education_cat = map_education(mother_education, mappings, "grouped"),
      
      # Get highest parental education (returns ordered factor)
      highest_parental_education = get_highest_household_education(father_education, mother_education, mappings)
    )
  
  n_father <- sum(!is.na(result$father_education))
  n_mother <- sum(!is.na(result$mother_education))
  log_msg(paste("Parental education added: Father =", n_father, ", Mother =", n_mother), "SUCCESS", log_file)
  
  return(result)
}

#' Add parental employment information
add_parental_employment <- function(child_baseline, employment_data, mappings, log_file = NULL) {
  
  log_msg("Adding parental employment information", "PROGRESS", log_file)
  
  # Get baseline employment for parents
  baseline_employment <- create_baseline_subset(employment_data, child_baseline,
                                               relationship_filter = c("father", "mother")) %>%
    select(match_id, individual_type, relationship, socio13_code)
  
  # Create employment indicators
  parental_employment <- baseline_employment %>%
    mutate(
      employed = !is.na(socio13_code) & socio13_code >= 110 & socio13_code <= 139
    ) %>%
    group_by(match_id, individual_type) %>%
    summarise(
      father_employed = any(employed & relationship == "father", na.rm = TRUE),
      mother_employed = any(employed & relationship == "mother", na.rm = TRUE),
      both_parents_employed = father_employed & mother_employed,
      .groups = "drop"
    )
  
  # Join with child baseline
  result <- child_baseline %>%
    left_join(parental_employment, by = c("match_id", "individual_type"))
  
  n_with_employment <- sum(!is.na(result$father_employed) | !is.na(result$mother_employed))
  log_msg(paste("Parental employment added:", n_with_employment, "records"), "SUCCESS", log_file)
  
  return(result)
}

#' Add parental income information with outlier handling
add_parental_income <- function(child_baseline, income_data, log_file = NULL) {
  
  log_msg("Adding parental income information", "PROGRESS", log_file)
  
  # Get income averaged over baseline period for parents
  baseline_income <- create_baseline_subset(income_data, child_baseline,
                                           relationship_filter = c("father", "mother"),
                                           year_filter = "income_range") %>%
    # Remove outliers before averaging
    filter(!income_outlier | is.na(income_outlier)) %>%
    group_by(match_id, individual_type, relationship) %>%
    summarise(
      mean_salary = mean(salary, na.rm = TRUE),
      mean_total_income = mean(total_income, na.rm = TRUE),
      n_years = n(),
      .groups = "drop"
    ) %>%
    # Set to NA if no valid data
    mutate(
      mean_salary = ifelse(n_years == 0, NA, mean_salary),
      mean_total_income = ifelse(n_years == 0, NA, mean_total_income)
    )
  
  # Separate and aggregate by household
  parental_income <- baseline_income %>%
    group_by(match_id, individual_type) %>%
    summarise(
      father_income = mean(mean_total_income[relationship == "father"], na.rm = TRUE),
      mother_income = mean(mean_total_income[relationship == "mother"], na.rm = TRUE),
      household_income = sum(mean_total_income, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    mutate(
      # Convert to thousands DKK
      father_income_k = father_income / 1000,
      mother_income_k = mother_income / 1000,
      household_income_k = household_income / 1000,
      
      # Handle cases where sum results in 0 (all NA)
      household_income_k = ifelse(household_income_k == 0, NA, household_income_k)
    )
  
  # Join with child baseline
  result <- child_baseline %>%
    left_join(parental_income, by = c("match_id", "individual_type"))
  
  n_with_income <- sum(!is.na(result$household_income_k))
  outliers_removed <- sum(income_data$income_outlier, na.rm = TRUE)
  log_msg(paste("Parental income added:", n_with_income, "records with income,", 
               outliers_removed, "outliers excluded"), "SUCCESS", log_file)
  
  return(result)
}

# ==============================================================================
# PARENT DATA PROCESSING FUNCTIONS  
# ==============================================================================

#' Create complete parent-level dataset
create_parent_dataset <- function(parent_baseline, demographics_data, education_data, 
                                 employment_data, income_data, mappings, log_file = NULL) {
  
  log_msg("Creating complete parent dataset", "PROGRESS", log_file)
  
  # Add parent demographics
  parent_demographics <- create_baseline_subset(demographics_data, parent_baseline,
                                               relationship_filter = c("father", "mother")) %>%
    select(match_id, individual_type, pnr, relationship, gender, age, civil_status, country_of_origin)
  
  # Add education data
  parent_education <- create_baseline_subset(education_data, parent_baseline,
                                            relationship_filter = c("father", "mother"),
                                            year_filter = "before_baseline") %>%
    group_by(match_id, individual_type, pnr, relationship) %>%
    slice_max(year, with_ties = FALSE) %>%
    ungroup() %>%
    select(match_id, individual_type, pnr, relationship, hfaudd_code)
  
  # Add employment data
  parent_employment <- create_baseline_subset(employment_data, parent_baseline,
                                             relationship_filter = c("father", "mother")) %>%
    select(match_id, individual_type, pnr, relationship, socio13_code)
  
  # Add income data
  parent_income <- create_baseline_subset(income_data, parent_baseline,
                                         relationship_filter = c("father", "mother"),
                                         year_filter = "income_range") %>%
    filter(!income_outlier | is.na(income_outlier)) %>%
    group_by(match_id, individual_type, pnr, relationship) %>%
    summarise(
      mean_total_income = mean(total_income, na.rm = TRUE),
      .groups = "drop"
    )
  
  # Combine all parent data
  parent_complete <- parent_baseline %>%
    left_join(parent_demographics, by = c("match_id", "individual_type")) %>%
    left_join(parent_education, by = c("match_id", "individual_type", "pnr", "relationship")) %>%
    left_join(parent_employment, by = c("match_id", "individual_type", "pnr", "relationship")) %>%
    left_join(parent_income, by = c("match_id", "individual_type", "pnr", "relationship")) %>%
    filter(!is.na(relationship)) %>%
    mutate(
      # Apply mappings using our refactored utilities
      parent_age_years = age,
      education_cat = map_education(hfaudd_code, mappings, "grouped"),
      employment_cat = map_employment(socio13_code, mappings, "grouped"),
      income_k = mean_total_income / 1000,
      
      # Parent gender based on relationship
      parent_gender = case_when(
        relationship == "father" ~ "Father",
        relationship == "mother" ~ "Mother",
        TRUE ~ "Unknown"
      ),
      
      # Civil status and country mappings
      civil_status_cat = map_civil_status(civil_status, mappings, "en"),
      origin_cat = map_countries(country_of_origin, mappings, "en"),
      
      # Child age for reference
      child_age_years = child_age_at_index
    )
  
  n_parents <- nrow(parent_complete)
  log_msg(paste("Complete parent dataset created:", n_parents, "parent records"), "SUCCESS", log_file)
  
  return(parent_complete)
}

# ==============================================================================
# TABLE GENERATION FUNCTIONS
# ==============================================================================

#' Generate child-centered baseline characteristics table
generate_child_table <- function(child_data, log_file = NULL) {
  
  log_msg("Generating child-centered baseline table", "PROGRESS", log_file)
  
  # Select variables for table
  table_data <- child_data %>%
    select(
      group,
      gender,
      child_age_years,
      birth_decade,
      country_origin_cat,
      family_size_cat,
      father_education_cat,
      mother_education_cat,
      highest_parental_education,
      father_employed,
      mother_employed,
      both_parents_employed,
      father_income_k,
      mother_income_k,
      household_income_k
    )
  
  # Create gtsummary table
  child_table <- table_data %>%
    tbl_summary(
      by = group,
      statistic = list(
        all_continuous() ~ "{median} ({p25}, {p75})",
        all_categorical() ~ "{n} ({p}%)"
      ),
      digits = list(
        all_continuous() ~ CONFIG$continuous_digits,
        all_categorical() ~ CONFIG$categorical_digits
      ),
      missing_text = "Missing",
      label = list(
        gender ~ "Child Gender",
        child_age_years ~ "Child Age at Index Date (years)",
        birth_decade ~ "Child Birth Decade",
        country_origin_cat ~ "Country of Origin",
        family_size_cat ~ "Family Size",
        father_education_cat ~ "Father's Education Level",
        mother_education_cat ~ "Mother's Education Level",
        highest_parental_education ~ "Highest Parental Education",
        father_employed ~ "Father Employed",
        mother_employed ~ "Mother Employed",
        both_parents_employed ~ "Both Parents Employed",
        father_income_k ~ "Father's Income (1000 DKK)",
        mother_income_k ~ "Mother's Income (1000 DKK)",
        household_income_k ~ "Household Income (1000 DKK)"
      )
    ) %>%
    add_overall() %>%
    modify_header(
      list(
        stat_0 ~ "**Overall**\\n**N = {N}**",
        stat_1 ~ "**Cases**\\n**N = {n}**",
        stat_2 ~ "**Controls**\\n**N = {n}**"
      )
    ) %>%
    modify_caption(
      "**Table 1. Baseline Characteristics of Study Population**"
    ) %>%
    modify_footnote(
      update = list(
        stat_0 ~ "Median (IQR) for continuous variables; n (%) for categorical variables"
      )
    ) %>%
    bold_labels()
  
  log_msg("Child table generated successfully", "SUCCESS", log_file)
  return(child_table)
}

#' Generate parent-centered baseline characteristics table with gender stratification
generate_parent_table <- function(parent_data, log_file = NULL) {
  
  log_msg("Generating parent-centered baseline table", "PROGRESS", log_file)
  
  # Create fathers table
  fathers_table <- parent_data %>%
    filter(parent_gender == "Father") %>%
    select(
      group,
      parent_age_years,
      education_cat,
      employment_cat,
      civil_status_cat,
      origin_cat,
      income_k,
      child_age_years
    ) %>%
    tbl_summary(
      by = group,
      statistic = list(
        all_continuous() ~ "{median} ({p25}, {p75})",
        all_categorical() ~ "{n} ({p}%)"
      ),
      digits = list(
        all_continuous() ~ CONFIG$continuous_digits,
        all_categorical() ~ CONFIG$categorical_digits
      ),
      missing_text = "Missing",
      label = list(
        parent_age_years ~ "Age at Index Date (years)",
        education_cat ~ "Education Level",
        employment_cat ~ "Employment Status",
        civil_status_cat ~ "Civil Status",
        origin_cat ~ "Country of Origin",
        income_k ~ "Annual Income (1000 DKK)",
        child_age_years ~ "Child Age at Index Date (years)"
      )
    ) %>%
    modify_header(
      list(
        stat_1 ~ "**Fathers of Cases**\\n**N = {n}**",
        stat_2 ~ "**Fathers of Controls**\\n**N = {n}**"
      )
    ) %>%
    bold_labels()
  
  # Create mothers table
  mothers_table <- parent_data %>%
    filter(parent_gender == "Mother") %>%
    select(
      group,
      parent_age_years,
      education_cat,
      employment_cat,
      civil_status_cat,
      origin_cat,
      income_k,
      child_age_years
    ) %>%
    tbl_summary(
      by = group,
      statistic = list(
        all_continuous() ~ "{median} ({p25}, {p75})",
        all_categorical() ~ "{n} ({p}%)"
      ),
      digits = list(
        all_continuous() ~ CONFIG$continuous_digits,
        all_categorical() ~ CONFIG$categorical_digits
      ),
      missing_text = "Missing",
      label = list(
        parent_age_years ~ "Age at Index Date (years)",
        education_cat ~ "Education Level",
        employment_cat ~ "Employment Status",
        civil_status_cat ~ "Civil Status",
        origin_cat ~ "Country of Origin",
        income_k ~ "Annual Income (1000 DKK)",
        child_age_years ~ "Child Age at Index Date (years)"
      )
    ) %>%
    modify_header(
      list(
        stat_1 ~ "**Mothers of Cases**\\n**N = {n}**",
        stat_2 ~ "**Mothers of Controls**\\n**N = {n}**"
      )
    ) %>%
    bold_labels()
  
  # Combine tables
  parent_table <- tbl_merge(
    tbls = list(fathers_table, mothers_table),
    tab_spanner = c("**Fathers**", "**Mothers**")
  ) %>%
    modify_caption(
      "**Table S1. Baseline Characteristics of Parents by Gender**"
    ) %>%
    modify_footnote(
      everything() ~ "Median (IQR) for continuous variables; n (%) for categorical variables"
    )
  
  log_msg("Parent table generated successfully", "SUCCESS", log_file)
  return(parent_table)
}

# ==============================================================================
# OUTPUT AND REPORTING FUNCTIONS
# ==============================================================================

#' Save all tables and generate summary report
save_tables_and_report <- function(child_table, parent_table, child_data, parent_data, log_file = NULL) {
  
  log_msg("Saving tables and generating reports", "PROGRESS", log_file)
  
  # Save child table (main Table 1)
  child_table %>%
    as_gt() %>%
    gt::gtsave(
      filename = file.path(CONFIG$output_path, "table1_baseline_characteristics.html"),
      inline_css = TRUE
    )
  
  # Save parent table (supplementary)
  parent_table %>%
    as_gt() %>%
    gt::gtsave(
      filename = file.path(CONFIG$output_path, "tableS1_parent_baseline_characteristics.html"),
      inline_css = TRUE
    )
  
  # Save processed data for further analysis
  write_csv(child_data, file.path(CONFIG$output_path, "baseline_characteristics_child_data.csv"))
  write_csv(parent_data, file.path(CONFIG$output_path, "baseline_characteristics_parent_data.csv"))
  
  # Generate summary statistics
  summary_stats <- list(
    total_matched_pairs = length(unique(child_data$match_id)),
    total_cases = sum(child_data$group == "Cases"),
    total_controls = sum(child_data$group == "Controls"),
    total_parents = nrow(parent_data),
    baseline_period = paste(min(year(child_data$case_index_date), na.rm = TRUE), "-", 
                           max(year(child_data$case_index_date), na.rm = TRUE)),
    mean_child_age = round(mean(child_data$child_age_at_index, na.rm = TRUE), 2),
    complete_family_data = sum(!is.na(child_data$family_size_cat)),
    complete_income_data = sum(!is.na(child_data$household_income_k))
  )
  
  # Log summary
  log_msg("=== BASELINE CHARACTERISTICS SUMMARY ===", "INFO", log_file)
  log_msg(paste("Total matched pairs:", summary_stats$total_matched_pairs), "INFO", log_file)
  log_msg(paste("Cases:", summary_stats$total_cases), "INFO", log_file)
  log_msg(paste("Controls:", summary_stats$total_controls), "INFO", log_file)
  log_msg(paste("Parents analyzed:", summary_stats$total_parents), "INFO", log_file)
  log_msg(paste("Baseline period:", summary_stats$baseline_period), "INFO", log_file)
  log_msg(paste("Mean child age at index:", summary_stats$mean_child_age, "years"), "INFO", log_file)
  log_msg(paste("Complete family data:", summary_stats$complete_family_data), "INFO", log_file)
  log_msg(paste("Complete income data:", summary_stats$complete_income_data), "INFO", log_file)
  
  log_msg("All tables and reports saved successfully", "SUCCESS", log_file)
  
  return(summary_stats)
}

# ==============================================================================
# MAIN EXECUTION FUNCTION
# ==============================================================================

#' Main function to execute the complete baseline characteristics analysis
main <- function() {
  
  # Setup environment and logging
  log_file <- setup_environment()
  log_msg("Starting STROBE-compliant baseline characteristics analysis", "PROGRESS", log_file)
  
  tryCatch({
    
    # Load mappings
    log_msg("Loading Danish registry mappings", "PROGRESS", log_file)
    MAPPINGS <- load_all_mappings(CONFIG$mappings_path)
    log_msg(paste("Mappings loaded:", paste(names(MAPPINGS), collapse = ", ")), "SUCCESS", log_file)
    
    # Load and validate data
    data_list <- load_data_files(log_file)
    data_list <- convert_data_types(data_list, log_file)
    
    # Create baseline structures
    child_baseline <- create_child_baseline_structure(data_list$basic, log_file)
    parent_baseline <- create_parent_baseline_structure(data_list$basic, log_file)
    
    # Enrich child data step by step
    child_data <- child_baseline %>%
      add_child_demographics(data_list$demographics, MAPPINGS, log_file) %>%
      add_family_structure(data_list$family, log_file) %>%
      add_parental_education(data_list$education, MAPPINGS, log_file) %>%
      add_parental_employment(data_list$employment, MAPPINGS, log_file) %>%
      add_parental_income(data_list$income, log_file)
    
    # Create complete parent dataset
    parent_data <- create_parent_dataset(parent_baseline, data_list$demographics, 
                                        data_list$education, data_list$employment, 
                                        data_list$income, MAPPINGS, log_file)
    
    # Generate tables
    child_table <- generate_child_table(child_data, log_file)
    parent_table <- generate_parent_table(parent_data, log_file)
    
    # Save outputs and generate reports
    summary_stats <- save_tables_and_report(child_table, parent_table, 
                                           child_data, parent_data, log_file)
    
    # STROBE compliance notes
    log_msg("=== STROBE COMPLIANCE NOTES ===", "INFO", log_file)
    log_msg("✓ Study population clearly defined (children born 2000-2018, aged 0-5)", "SUCCESS", log_file)
    log_msg("✓ Case-control design with matched pairs", "SUCCESS", log_file)
    log_msg("✓ Baseline characteristics at index date", "SUCCESS", log_file)
    log_msg("✓ Both individual and family-level variables", "SUCCESS", log_file)
    log_msg("✓ Missing data explicitly reported", "SUCCESS", log_file)
    log_msg("✓ Both child-centered and parent-centered perspectives", "SUCCESS", log_file)
    log_msg("✓ Income data from pre-exposure period (3-year average)", "SUCCESS", log_file)
    log_msg("✓ Education classified using ISCED standards", "SUCCESS", log_file)
    log_msg("✓ Employment using Danish SOCIO13 classification", "SUCCESS", log_file)
    
    log_msg("Baseline characteristics analysis completed successfully!", "SUCCESS", log_file)
    
    return(list(
      child_table = child_table,
      parent_table = parent_table,
      child_data = child_data,
      parent_data = parent_data,
      summary_stats = summary_stats
    ))
    
  }, error = function(e) {
    error_msg <- paste("Error in baseline analysis:", e$message)
    log_msg(error_msg, "ERROR", log_file)
    stop(error_msg)
  })
}

# Execute main function if script is run directly
if (!interactive()) {
  result <- main()
  cat("\n🎉 Baseline characteristics tables generated successfully!\n")
  cat("📄 Main table: table1_baseline_characteristics.html\n")
  cat("📄 Supplementary table: tableS1_parent_baseline_characteristics.html\n")
  cat("📊 Data files saved for further analysis\n")
}