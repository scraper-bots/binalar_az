import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_csv('binalar_listings.csv')

print("="*80)
print("DATASET OVERVIEW")
print("="*80)
print(f"Total Listings: {len(df):,}")
print(f"Columns: {list(df.columns)}")
print(f"\nData Types:\n{df.dtypes}")
print(f"\nMissing Values:\n{df.isnull().sum()}")

print("\n" + "="*80)
print("BUSINESS KEY METRICS")
print("="*80)

# Extract city from title
df['city'] = df['title'].str.split(' / ').str[0]
print(f"\nTop 10 Cities by Listing Count:")
print(df['city'].value_counts().head(10))

# Extract property type from title
df['property_type'] = df['title'].str.split(' / ').str[-1]
print(f"\nTop 10 Property Types:")
print(df['property_type'].value_counts().head(10))

# Price analysis
df['price_clean'] = pd.to_numeric(df['price_raw'], errors='coerce')
print(f"\nPrice Statistics (AZN):")
print(df['price_clean'].describe())
print(f"Listings with price: {df['price_clean'].notna().sum():,} ({df['price_clean'].notna().sum()/len(df)*100:.1f}%)")

# Room analysis
df['rooms_clean'] = pd.to_numeric(df['rooms'], errors='coerce')
print(f"\nRoom Distribution:")
print(df['rooms_clean'].value_counts().sort_index().head(10))

# Area analysis
df['area_clean'] = pd.to_numeric(df['area'], errors='coerce')
print(f"\nArea Statistics (sqm):")
print(df['area_clean'].describe())

# Price per sqm
df['price_per_sqm'] = df['price_clean'] / df['area_clean']
print(f"\nPrice per SQM Statistics (AZN):")
print(df['price_per_sqm'].describe())

# Date analysis
df['date_parsed'] = pd.to_datetime(df['date'], format='%d.%m.%Y', errors='coerce')
print(f"\nDate Range:")
print(f"Earliest: {df['date_parsed'].min()}")
print(f"Latest: {df['date_parsed'].max()}")
print(f"\nListings by Month:")
print(df['date_parsed'].dt.to_period('M').value_counts().sort_index().tail(10))

# Save cleaned data for chart generation
df.to_csv('binalar_listings_clean.csv', index=False)
print("\n" + "="*80)
print("Cleaned data saved to: binalar_listings_clean.csv")
print("="*80)
