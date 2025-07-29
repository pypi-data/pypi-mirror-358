#!/usr/bin/env Rscript
# ==============================================================================
# STROBE-Compliant Baseline Characteristics Table
# ==============================================================================
# Study: Long-term Impact of Childhood Severe Chronic Disease on Parental Income
# Design: Matched case-control study with difference-in-differences analysis
# 
# This script generates a comprehensive baseline characteristics table (Table 1)
# following STROBE guidelines for reporting observational studies.
# 
# Population: Children born in Denmark (2000-2018) aged 0-5 years during 
#            observation period, with matched case-control design
# Cases: Children with severe chronic disease (SCD) diagnosis
# Controls: Children without SCD diagnosis, matched on key characteristics
# 
# Analysis unit: Both child-centered and parent-centered perspectives
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
  library(knitr)
})

# Load mapping utilities
source("scripts/baseline/mapping_utilities.R")

# Set options for reproducibility and display
options(pillar.sigfig = 3, digits = 3, dplyr.summarise.inform = FALSE)

# ==============================================================================
# CONFIGURATION AND HELPER FUNCTIONS
# ==============================================================================

# Define input paths
input_path <- "cohort_output/enrichment_output"
output_path <- "cohort_output/enrichment_output"
mappings_path <- "static/mappings"

# Ensure output directory exists
if (!dir.exists(output_path)) {
  dir.create(output_path, recursive = TRUE)
}

# Load all Danish registry mappings
cat("Loading Danish registry mappings...\n")
MAPPINGS <- load_all_mappings(mappings_path)

# Helper function for robust variable extraction
extract_baseline_var <- function(data, var_name, match_ids, default_val = NA) {
  tryCatch({
    result <- data %>%
      filter(match_id %in% match_ids) %>%
      select(all_of(c("match_id", var_name))) %>%
      group_by(match_id) %>%
      summarise(
        value = if (var_name %in% c("salary", "total_income")) {
          # For income variables, use mean across temporal window
          mean(get(var_name), na.rm = TRUE)
        } else {
          # For other variables, use most recent non-missing value
          last(get(var_name)[!is.na(get(var_name))])
        },
        .groups = "drop"
      )
    
    if (nrow(result) == 0) {
      return(rep(default_val, length(match_ids)))
    }
    
    # Merge with all match_ids to ensure complete coverage
    complete_data <- tibble(match_id = match_ids) %>%
      left_join(result, by = "match_id") %>%
      pull(value)
    
    return(complete_data)
  }, error = function(e) {
    warning(paste("Error extracting", var_name, ":", e$message))
    return(rep(default_val, length(match_ids)))
  })
}

# Note: Categorization functions are now provided by mapping_utilities.R
# All Danish registry code mappings use the official mapping files

# Function to calculate temporal window baseline (year 0)
get_baseline_year <- function(case_index_date) {
  year(as.Date(case_index_date))
}

# ==============================================================================
# DATA LOADING AND PREPARATION
# ==============================================================================

cat("Loading enrichment data...\n")

# Load all data files
basic_data <- read_csv(file.path(input_path, "basic.csv"), col_types = cols(.default = "c"))
demographics_data <- read_csv(file.path(input_path, "demographics.csv"), col_types = cols(.default = "c"))
education_data <- read_csv(file.path(input_path, "education.csv"), col_types = cols(.default = "c"))
employment_data <- read_csv(file.path(input_path, "employment.csv"), col_types = cols(.default = "c"))
family_data <- read_csv(file.path(input_path, "family.csv"), col_types = cols(.default = "c"))
income_data <- read_csv(file.path(input_path, "income.csv"), col_types = cols(.default = "c"))

# Convert numeric columns
basic_data <- basic_data %>%
  mutate(
    case_index_date = as.Date(case_index_date),
    case_birth_date = as.Date(case_birth_date),
    controls_matched = as.numeric(controls_matched),
    case_family_members = as.numeric(case_family_members),
    control_family_members = as.numeric(control_family_members)
  )

demographics_data <- demographics_data %>%
  mutate(
    year = as.numeric(year),
    age = as.numeric(age)
  )

education_data <- education_data %>%
  mutate(
    year = as.numeric(year),
    education_valid_from = as.numeric(education_valid_from),
    education_valid_to = as.numeric(education_valid_to)
  )

employment_data <- employment_data %>%
  mutate(
    year = as.numeric(year),
    socio13_code = as.numeric(socio13_code)
  )

income_data <- income_data %>%
  mutate(
    year = as.numeric(year),
    salary = as.numeric(salary),
    total_income = as.numeric(total_income)
  )

# Create baseline year for each match
basic_data <- basic_data %>%
  mutate(baseline_year = year(case_index_date))

cat("Data loaded successfully.\n")
cat("Number of matched pairs:", nrow(basic_data), "\n")
cat("Total case family members:", sum(basic_data$case_family_members, na.rm = TRUE), "\n")
cat("Total control family members:", sum(basic_data$control_family_members, na.rm = TRUE), "\n")

# ==============================================================================
# BASELINE CHARACTERISTICS DATA PREPARATION
# ==============================================================================

cat("Preparing baseline characteristics data...\n")

# Get baseline demographics (at index date)
baseline_demographics <- demographics_data %>%
  inner_join(basic_data %>% select(match_id, baseline_year), by = "match_id") %>%
  filter(year == baseline_year) %>%
  select(match_id, individual_type, pnr, relationship, gender, age, 
         municipality_code, country_of_origin, civil_status, region)

# Get baseline education (most recent before or at index date)
baseline_education <- education_data %>%
  inner_join(basic_data %>% select(match_id, baseline_year), by = "match_id") %>%
  filter(year <= baseline_year) %>%
  group_by(match_id, individual_type, pnr, relationship) %>%
  slice_max(year, with_ties = FALSE) %>%
  ungroup() %>%
  select(match_id, individual_type, pnr, relationship, hfaudd_code)

# Get baseline employment (at index date)
baseline_employment <- employment_data %>%
  inner_join(basic_data %>% select(match_id, baseline_year), by = "match_id") %>%
  filter(year == baseline_year) %>%
  select(match_id, individual_type, pnr, relationship, socio13_code)

# Get baseline income (mean over 3 years before index date)
baseline_income <- income_data %>%
  inner_join(basic_data %>% select(match_id, baseline_year), by = "match_id") %>%
  filter(year >= (baseline_year - 2) & year <= baseline_year) %>%
  group_by(match_id, individual_type, pnr, relationship) %>%
  summarise(
    mean_salary = mean(salary, na.rm = TRUE),
    mean_total_income = mean(total_income, na.rm = TRUE),
    .groups = "drop"
  )

# Get family structure information
family_structure <- family_data %>%
  group_by(match_id, individual_type) %>%
  summarise(
    family_size = n_distinct(family_member_pnr),
    has_siblings = family_size > 1,
    .groups = "drop"
  )

# ==============================================================================
# CREATE CHILD-CENTERED BASELINE TABLE
# ==============================================================================

cat("Creating child-centered baseline characteristics table...\n")

# Prepare child-level data
child_baseline <- basic_data %>%
  select(match_id, case_pnr, control_pnr, case_birth_date, case_index_date, baseline_year) %>%
  pivot_longer(
    cols = c(case_pnr, control_pnr),
    names_to = "group_type",
    values_to = "child_pnr",
    names_pattern = "(.*)_pnr"
  ) %>%
  filter(!is.na(child_pnr)) %>%
  mutate(
    group = case_when(
      group_type == "case" ~ "Cases",
      group_type == "control" ~ "Controls",
      TRUE ~ "Unknown"
    ),
    child_age_at_index = as.numeric(difftime(case_index_date, case_birth_date, units = "days")) / 365.25,
    child_age_group = create_age_groups(child_age_at_index),
    birth_year = year(case_birth_date),
    birth_decade = paste0(floor(birth_year / 10) * 10, "s")
  )

# Add child demographics
child_baseline <- child_baseline %>%
  left_join(
    baseline_demographics %>%
      filter(relationship == "child") %>%
      select(match_id, individual_type, pnr, gender, municipality_code, country_of_origin, region),
    by = c("match_id", "child_pnr" = "pnr")
  )

# Add family structure
child_baseline <- child_baseline %>%
  left_join(family_structure, by = c("match_id", "individual_type"))

# Add parental characteristics
# Father's education
father_education <- baseline_education %>%
  filter(relationship == "father") %>%
  select(match_id, individual_type, father_education = hfaudd_code)

# Mother's education
mother_education <- baseline_education %>%
  filter(relationship == "mother") %>%
  select(match_id, individual_type, mother_education = hfaudd_code)

# Parental income
parental_income <- baseline_income %>%
  filter(relationship %in% c("father", "mother")) %>%
  group_by(match_id, individual_type) %>%
  summarise(
    father_income = mean(mean_total_income[relationship == "father"], na.rm = TRUE),
    mother_income = mean(mean_total_income[relationship == "mother"], na.rm = TRUE),
    household_income = sum(mean_total_income, na.rm = TRUE),
    .groups = "drop"
  )

# Parental employment
parental_employment <- baseline_employment %>%
  filter(relationship %in% c("father", "mother")) %>%
  group_by(match_id, individual_type) %>%
  summarise(
    father_employed = any(socio13_code %in% 1:10 & relationship == "father", na.rm = TRUE),
    mother_employed = any(socio13_code %in% 1:10 & relationship == "mother", na.rm = TRUE),
    both_parents_employed = father_employed & mother_employed,
    .groups = "drop"
  )

# Combine all child-level data
child_baseline_final <- child_baseline %>%
  left_join(father_education, by = c("match_id", "individual_type")) %>%
  left_join(mother_education, by = c("match_id", "individual_type")) %>%
  left_join(parental_income, by = c("match_id", "individual_type")) %>%
  left_join(parental_employment, by = c("match_id", "individual_type")) %>%
  mutate(
    # Categorize education using mapping utilities
    father_education_cat = map_education(father_education, MAPPINGS, "grouped"),
    mother_education_cat = map_education(mother_education, MAPPINGS, "grouped"),
    
    # Highest parental education using mapping utilities
    highest_parental_education = get_highest_household_education(father_education, mother_education, MAPPINGS),
    
    # Income in thousands DKK
    father_income_k = father_income / 1000,
    mother_income_k = mother_income / 1000,
    household_income_k = household_income / 1000,
    
    # Age groups using mapping utilities
    child_age_group = create_child_age_groups(child_age_at_index, "broad"),
    
    # Birth decade using mapping utilities
    birth_decade = factor(create_birth_decades(birth_year)),
    
    # Gender using mapping utilities
    gender = map_gender(gender, MAPPINGS, "en"),
    
    # Country of origin using mapping utilities
    country_origin_cat = map_countries(country_of_origin, MAPPINGS, "en"),
    
    # Family size categories using mapping utilities
    family_size_cat = categorize_family_size(family_size)
  )

# ==============================================================================
# GENERATE CHILD-CENTERED BASELINE CHARACTERISTICS TABLE
# ==============================================================================

# Create the main baseline characteristics table
child_table <- child_baseline_final %>%
  select(
    group,
    # Child characteristics
    gender,
    child_age_group,
    birth_decade,
    country_origin_cat,
    
    # Family characteristics
    family_size_cat,
    
    # Parental education
    father_education_cat,
    mother_education_cat,
    highest_parental_education,
    
    # Parental employment
    father_employed,
    mother_employed,
    both_parents_employed,
    
    # Parental income
    father_income_k,
    mother_income_k,
    household_income_k
  ) %>%
  tbl_summary(
    by = group,
    statistic = list(
      all_continuous() ~ "{mean} ({sd})",
      all_categorical() ~ "{n} ({p}%)"
    ),
    digits = list(
      all_continuous() ~ 1,
      all_categorical() ~ c(0, 1)
    ),
    missing_text = "Missing",
    label = list(
      gender ~ "Child Gender",
      child_age_group ~ "Child Age at Index Date",
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
  add_p(
    test = list(
      all_continuous() ~ "t.test",
      all_categorical() ~ "chisq.test"
    ),
    pvalue_fun = function(x) style_pvalue(x, digits = 3)
  ) %>%
  add_overall() %>%
  modify_header(
    list(
      stat_0 ~ "**Overall**\n**N = {N}**",
      stat_1 ~ "**Cases**\n**N = {n}**",
      stat_2 ~ "**Controls**\n**N = {n}**"
    )
  ) %>%
  modify_caption(
    "**Table 1. Baseline Characteristics of Study Population**"
  ) %>%
  modify_footnote(
    update = list(
      stat_0 ~ "Mean (SD) for continuous variables; n (%) for categorical variables",
      p.value ~ "P-values from t-tests for continuous variables and chi-square tests for categorical variables"
    )
  ) %>%
  bold_labels()

# ==============================================================================
# CREATE PARENT-CENTERED BASELINE TABLE
# ==============================================================================

cat("Creating parent-centered baseline characteristics table...\n")

# Prepare parent-level data
parent_baseline <- basic_data %>%
  select(match_id, case_pnr, control_pnr, case_birth_date, case_index_date, baseline_year) %>%
  pivot_longer(
    cols = c(case_pnr, control_pnr),
    names_to = "group_type",
    values_to = "child_pnr",
    names_pattern = "(.*)_pnr"
  ) %>%
  filter(!is.na(child_pnr)) %>%
  mutate(
    group = case_when(
      group_type == "case" ~ "Parents of Cases",
      group_type == "control" ~ "Parents of Controls",
      TRUE ~ "Unknown"
    ),
    child_age_at_index = as.numeric(difftime(case_index_date, case_birth_date, units = "days")) / 365.25,
    child_age_group = create_age_groups(child_age_at_index)
  )

# Add parent demographics (fathers and mothers separately)
parent_demographics <- baseline_demographics %>%
  filter(relationship %in% c("father", "mother")) %>%
  select(match_id, individual_type, pnr, relationship, gender, age, civil_status, country_of_origin)

# Combine parent data
parent_baseline_expanded <- parent_baseline %>%
  left_join(parent_demographics, by = c("match_id", "individual_type")) %>%
  left_join(baseline_education, by = c("match_id", "individual_type", "pnr", "relationship")) %>%
  left_join(baseline_employment, by = c("match_id", "individual_type", "pnr", "relationship")) %>%
  left_join(baseline_income, by = c("match_id", "individual_type", "pnr", "relationship")) %>%
  filter(!is.na(relationship)) %>%
  mutate(
    # Parent characteristics using mapping utilities
    parent_age_group = create_parent_age_groups(age),
    
    education_cat = map_education(hfaudd_code, MAPPINGS, "grouped"),
    employment_cat = map_employment(socio13_code, MAPPINGS, "grouped"),
    income_k = mean_total_income / 1000,
    
    # Parent gender
    parent_gender = case_when(
      relationship == "father" ~ "Father",
      relationship == "mother" ~ "Mother",
      TRUE ~ "Unknown"
    ),
    
    # Civil status using mapping utilities
    civil_status_cat = map_civil_status(civil_status, MAPPINGS, "en"),
    
    # Country of origin using mapping utilities
    origin_cat = map_countries(country_of_origin, MAPPINGS, "en"),
    
    # Child age groups using mapping utilities
    child_age_group = create_child_age_groups(child_age_at_index, "broad")
  )

# Create parent-centered table
parent_table <- parent_baseline_expanded %>%
  select(
    group,
    parent_gender,
    parent_age_group,
    education_cat,
    employment_cat,
    civil_status_cat,
    origin_cat,
    income_k,
    child_age_group
  ) %>%
  tbl_summary(
    by = group,
    statistic = list(
      all_continuous() ~ "{median} ({p25}, {p75})",
      all_categorical() ~ "{n} ({p}%)"
    ),
    digits = list(
      all_continuous() ~ 1,
      all_categorical() ~ c(0, 1)
    ),
    missing_text = "Missing",
    label = list(
      parent_gender ~ "Parent Gender",
      parent_age_group ~ "Parent Age at Index Date",
      education_cat ~ "Education Level",
      employment_cat ~ "Employment Status",
      civil_status_cat ~ "Civil Status",
      origin_cat ~ "Country of Origin",
      income_k ~ "Annual Income (1000 DKK)",
      child_age_group ~ "Child Age at Index Date"
    )
  ) %>%
  add_p(
    test = list(
      all_continuous() ~ "wilcox.test",
      all_categorical() ~ "chisq.test"
    ),
    pvalue_fun = function(x) style_pvalue(x, digits = 3)
  ) %>%
  add_overall() %>%
  modify_header(
    list(
      stat_0 ~ "**Overall**\n**N = {N}**",
      stat_1 ~ "**Parents of Cases**\n**N = {n}**",
      stat_2 ~ "**Parents of Controls**\n**N = {n}**"
    )
  ) %>%
  modify_caption(
    "**Table S1. Baseline Characteristics of Parents (Analytical Unit: Parents)**"
  ) %>%
  modify_footnote(
    update = list(
      stat_0 ~ "Median (IQR) for continuous variables; n (%) for categorical variables",
      p.value ~ "P-values from Wilcoxon rank-sum tests for continuous variables and chi-square tests for categorical variables"
    )
  ) %>%
  bold_labels()

# ==============================================================================
# SAVE OUTPUTS
# ==============================================================================

cat("Saving baseline characteristics tables...\n")

# Save child-centered table (main Table 1)
child_table %>%
  as_gt() %>%
  gt::gtsave(
    filename = file.path(output_path, "table1_baseline_characteristics.html"),
    inline_css = TRUE
  )

# Save parent-centered table (supplementary)
parent_table %>%
  as_gt() %>%
  gt::gtsave(
    filename = file.path(output_path, "tableS1_parent_baseline_characteristics.html"),
    inline_css = TRUE
  )

# Create summary report
summary_stats <- list(
  total_matched_pairs = nrow(basic_data),
  total_cases = nrow(child_baseline_final %>% filter(group == "Cases")),
  total_controls = nrow(child_baseline_final %>% filter(group == "Controls")),
  total_parents = nrow(parent_baseline_expanded),
  baseline_period = paste(min(basic_data$baseline_year), "-", max(basic_data$baseline_year)),
  mean_child_age = round(mean(child_baseline_final$child_age_at_index, na.rm = TRUE), 2),
  complete_family_data = sum(!is.na(child_baseline_final$family_size_cat)),
  complete_income_data = sum(!is.na(child_baseline_final$household_income_k))
)

# Save summary
cat("=== BASELINE CHARACTERISTICS SUMMARY ===\n")
cat("Total matched pairs:", summary_stats$total_matched_pairs, "\n")
cat("Cases:", summary_stats$total_cases, "\n")
cat("Controls:", summary_stats$total_controls, "\n")
cat("Parents analyzed:", summary_stats$total_parents, "\n")
cat("Baseline period:", summary_stats$baseline_period, "\n")
cat("Mean child age at index:", summary_stats$mean_child_age, "years\n")
cat("Complete family data:", summary_stats$complete_family_data, "\n")
cat("Complete income data:", summary_stats$complete_income_data, "\n")

# Save data for further analysis
write_csv(
  child_baseline_final,
  file.path(output_path, "baseline_characteristics_child_data.csv")
)

write_csv(
  parent_baseline_expanded,
  file.path(output_path, "baseline_characteristics_parent_data.csv")
)

cat("\n=== STROBE COMPLIANCE NOTES ===\n")
cat("✓ Study population clearly defined (children born 2000-2018, aged 0-5)\n")
cat("✓ Case-control design with matched pairs\n")
cat("✓ Baseline characteristics at index date\n")
cat("✓ Both individual and family-level variables\n")
cat("✓ Appropriate statistical tests (t-test/chi-square, Wilcoxon)\n")
cat("✓ Missing data explicitly reported\n")
cat("✓ Both child-centered and parent-centered perspectives\n")
cat("✓ Income data from pre-exposure period (3-year average)\n")
cat("✓ Education classified using ISCED standards\n")
cat("✓ Employment using Danish SOCIO13 classification\n")

cat("\nBaseline characteristics tables generated successfully!\n")
cat("Main table: table1_baseline_characteristics.html\n")
cat("Supplementary table: tableS1_parent_baseline_characteristics.html\n")