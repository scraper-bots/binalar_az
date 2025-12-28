import pandas as pd
import numpy as np
import re

# Load the dataset
df = pd.read_csv('binalar_listings.csv')

# Parse title to extract more information
def parse_title(title):
    if pd.isna(title):
        return None, None, None
    parts = str(title).split(' / ')
    city = parts[0] if len(parts) > 0 else None
    region = parts[1] if len(parts) > 1 else None
    prop_type = parts[-1] if len(parts) > 0 else None
    return city, region, prop_type

df[['city', 'region', 'property_type']] = df['title'].apply(lambda x: pd.Series(parse_title(x)))

# Clean numeric fields
df['rooms_clean'] = pd.to_numeric(df['rooms'], errors='coerce')
df['area_clean'] = pd.to_numeric(df['area'], errors='coerce')
df['date_parsed'] = pd.to_datetime(df['date'], format='%d.%m.%Y', errors='coerce')

# Extract month and year
df['year_month'] = df['date_parsed'].dt.to_period('M')
df['month'] = df['date_parsed'].dt.month
df['year'] = df['date_parsed'].dt.year

print("="*80)
print("DETAILED BUSINESS INSIGHTS")
print("="*80)

# 1. Geographic distribution with percentages
print("\n1. GEOGRAPHIC MARKET DISTRIBUTION")
print("-" * 80)
city_dist = df['city'].value_counts().head(15)
city_pct = (city_dist / len(df) * 100).round(1)
for city, count in city_dist.items():
    print(f"{city:20s}: {count:6,} listings ({city_pct[city]:5.1f}%)")

# 2. Property type distribution
print("\n2. PROPERTY TYPE DISTRIBUTION")
print("-" * 80)
prop_dist = df['property_type'].value_counts().head(10)
prop_pct = (prop_dist / len(df) * 100).round(1)
for ptype, count in prop_dist.items():
    print(f"{ptype:25s}: {count:6,} listings ({prop_pct[ptype]:5.1f}%)")

# 3. Room distribution analysis
print("\n3. ROOM CONFIGURATION ANALYSIS")
print("-" * 80)
room_dist = df['rooms_clean'].value_counts().sort_index()
for rooms, count in room_dist.items():
    pct = count / df['rooms_clean'].notna().sum() * 100
    print(f"{int(rooms):2d} rooms: {count:6,} listings ({pct:5.1f}%)")

# 4. Area statistics by property type
print("\n4. AREA ANALYSIS BY PROPERTY TYPE")
print("-" * 80)
area_by_type = df.groupby('property_type')['area_clean'].agg(['count', 'mean', 'median', 'min', 'max'])
area_by_type = area_by_type.sort_values('count', ascending=False).head(6)
print(area_by_type.to_string())

# 5. Monthly listing trends
print("\n5. LISTING ACTIVITY BY MONTH (Last 12 Months)")
print("-" * 80)
monthly = df.groupby('year_month').size().tail(12)
for period, count in monthly.items():
    print(f"{period}: {count:6,} listings")

# 6. Top regions by city
print("\n6. TOP REGIONS IN MAJOR CITIES")
print("-" * 80)
for city in ['Bakı', 'Sumqayıt', 'Gəncə']:
    print(f"\n{city}:")
    city_regions = df[df['city'] == city]['region'].value_counts().head(5)
    for region, count in city_regions.items():
        if pd.notna(region):
            print(f"  {region:30s}: {count:6,} listings")

# 7. Room distribution by city
print("\n7. ROOM DISTRIBUTION IN TOP CITIES")
print("-" * 80)
for city in ['Bakı', 'Sumqayıt', 'Abşeron', 'Xırdalan']:
    city_data = df[df['city'] == city]
    avg_rooms = city_data['rooms_clean'].mean()
    median_rooms = city_data['rooms_clean'].median()
    print(f"{city:15s}: Avg {avg_rooms:.1f} rooms | Median {median_rooms:.0f} rooms")

# 8. Property type by city
print("\n8. PROPERTY TYPE MIX BY TOP CITIES")
print("-" * 80)
for city in ['Bakı', 'Sumqayıt', 'Gəncə', 'Abşeron']:
    city_data = df[df['city'] == city]
    top_types = city_data['property_type'].value_counts().head(3)
    print(f"\n{city}:")
    for ptype, count in top_types.items():
        pct = count / len(city_data) * 100
        print(f"  {ptype:25s}: {count:6,} ({pct:4.1f}%)")

# 9. Contact information availability
print("\n9. DATA COMPLETENESS")
print("-" * 80)
print(f"Listings with phone: {df['phone'].notna().sum():6,} ({df['phone'].notna().sum()/len(df)*100:5.1f}%)")
print(f"Listings with rooms: {df['rooms_clean'].notna().sum():6,} ({df['rooms_clean'].notna().sum()/len(df)*100:5.1f}%)")
print(f"Listings with area:  {df['area_clean'].notna().sum():6,} ({df['area_clean'].notna().sum()/len(df)*100:5.1f}%)")
print(f"Listings with desc:  {df['description'].notna().sum():6,} ({df['description'].notna().sum()/len(df)*100:5.1f}%)")

# Save for visualization
df.to_csv('binalar_listings_clean.csv', index=False)
print("\n" + "="*80)
print("Analysis complete!")
print("="*80)
