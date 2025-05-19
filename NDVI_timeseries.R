setwd("C:/Users/sebastiaan_verbessel/PycharmProjects/Labelme")
ts <- read.csv("NDVI_TimeSeries_Trees.csv", header = TRUE, sep = ",")

# Load necessary libraries
library(ggplot2)
library(dplyr)
library(tidyr)  # For filling in missing dates

# Convert 'date' column to Date class
ts$date <- as.Date(ts$date)
ts <- ts[ts$NDVI != -9999,]

plot(ts$date, ts$NDVI, col = factor(ts$vitality))

# Group data by Date and Binary Group (date and vitality), then calculate the mean and SEM for NDVI
summary_df <- ts %>%
  group_by(date, vitality) %>%
  summarise(
    mean_NDVI = mean(NDVI, na.rm = TRUE),
    sem_NDVI = sd(NDVI, na.rm = TRUE) / sqrt(n()),  # Compute Standard Error of the Mean (SEM)
    .groups = 'drop'
  ) %>%
  complete(date, vitality, fill = list(mean_NDVI = NA, sem_NDVI = NA))  # Ensure all dates are present

# Create the line plot with error bars (using SEM instead of SD)
ggplot(summary_df, aes(x = date, y = mean_NDVI, color = factor(vitality), group = vitality)) +
  geom_line(na.rm = TRUE) +  # Ensures missing values don't break the lines
  geom_point() +  # Add points for clarity
  geom_errorbar(aes(ymin = mean_NDVI - sem_NDVI, ymax = mean_NDVI + sem_NDVI), width = 0.1, na.rm = TRUE) +  # Error bars with SEM
  labs(
    x = "Middle date composite", 
    y = "Mean NDVI with SEM", 
    color = "Vitality", 
    title = "Mean NDVI of 30 day composities (medium value sampling) with standard error by date for alive and dead Pine Trees"
  ) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))  # Rotate x-axis labels for better readability
