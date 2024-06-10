# Load the CSV file into a DataFrame
import pandas as pd


df = pd.read_csv('case_studies/stylized_EU/inputs/generation_availability.csv')

df = df[df['technology'] == 'SunPV']

df["hour"] = df['time_step'] % 24

# Group by technology and calculate statistics for availability
stats = df.groupby('hour')['availability'].agg(['mean', 'std'])

print("Statistics for availability by technology:")
stats.to_csv("sun_distribution.csv")