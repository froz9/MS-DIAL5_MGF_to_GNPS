# process_area_file.R

# Load required libraries silently
suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(readr))

# Get command line arguments
args <- commandArgs(trailingOnly = TRUE)

# Check if the correct number of arguments is provided
if (length(args) != 2) {
  stop("Usage: Rscript process_TXT_file.R <input_file> <output_file>", call. = FALSE)
}

# Assign arguments to variables
input_file_path <- args[1]
output_file_path <- args[2]

# Read the input file specified by the command line argument
area <- read.delim(input_file_path, header = FALSE)

# 1. Define the values to be removed (from the 4th row)
columns_remove <- c("Average" , "Stdev")

# 2. Identify the columns to keep based on the values in row 4
columns_to_keep <- ! (area[4, ] %in% columns_remove)

# 3. Subset the data frame to keep only the desired COLUMNS
area_modified <- area[, columns_to_keep]

# 4. Remove the 4th ROW from the newly modified data frame
area_modified <- area_modified[-4, ]

gnps_cols <- c("Alignment ID", "Average Rt(min)", "Average Mz", "Metabolite name",
               "Adduct ion name", "Post curation result", "Fill %", "MS/MS included",
               "Formula", "Ontology", "INCHIKEY", "SMILES",
               "Comment", "Isotope tracking parent ID", "Isotope tracking weight number", "Dot product",
               "Reverse dot product", "Fragment presence %", "S/N average", "Spectrum reference file name",
               "MS1 isotopic spectrum")

# Select only necessary features for GNPS1
area_modified <- area_modified[,-c(9:10,15:18,20:21,24:28)]
area_modified[4,1:21] <- gnps_cols

# Remove features without an MS2 (where MS/MS included is "null")
rows_to_keep <- area_modified[, 22] != "null"
area_final <- area_modified[rows_to_keep, ]

# Write the final table to the output file specified by the command line argument
write.table(area_final, file = output_file_path,
            sep = "\t", col.names = FALSE, row.names = FALSE, quote = FALSE)