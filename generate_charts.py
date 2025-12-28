import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set professional style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

# Load cleaned data
print("Loading data...")
df = pd.read_csv('binalar_listings_clean.csv')

# Parse dates and categorize data
df['date_parsed'] = pd.to_datetime(df['date_parsed'])
df['year_month'] = pd.to_datetime(df['year_month'].astype(str))
df['rooms_clean'] = pd.to_numeric(df['rooms_clean'], errors='coerce')
df['area_clean'] = pd.to_numeric(df['area_clean'], errors='coerce')

print(f"Creating visualizations from {len(df):,} listings...\n")

# ============================================================================
# CHART 1: Market Share by Top Cities
# ============================================================================
print("1. Generating Market Share by City...")
fig, ax = plt.subplots(figsize=(12, 7))
city_counts = df['city'].value_counts().head(12)
city_pct = (city_counts / len(df) * 100).round(1)

colors = sns.color_palette("rocket_r", n_colors=len(city_counts))
bars = ax.barh(range(len(city_counts)), city_counts.values, color=colors)
ax.set_yticks(range(len(city_counts)))
ax.set_yticklabels(city_counts.index)
ax.set_xlabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Real Estate Market Share by City\nTotal Market: 31,151 Listings',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3)

# Add value labels
for i, (count, pct) in enumerate(zip(city_counts.values, city_pct.values)):
    ax.text(count + 100, i, f'{count:,} ({pct}%)',
            va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/01_market_share_by_city.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 2: Property Type Distribution
# ============================================================================
print("2. Generating Property Type Distribution...")
fig, ax = plt.subplots(figsize=(12, 7))
prop_counts = df['property_type'].value_counts().head(10)
prop_pct = (prop_counts / len(df) * 100).round(1)

colors = sns.color_palette("mako_r", n_colors=len(prop_counts))
bars = ax.barh(range(len(prop_counts)), prop_counts.values, color=colors)
ax.set_yticks(range(len(prop_counts)))
ax.set_yticklabels(prop_counts.index)
ax.set_xlabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Property Type Distribution Across Market',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3)

# Add value labels
for i, (count, pct) in enumerate(zip(prop_counts.values, prop_pct.values)):
    ax.text(count + 100, i, f'{count:,} ({pct}%)',
            va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/02_property_type_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 3: Room Configuration Analysis
# ============================================================================
print("3. Generating Room Configuration Analysis...")
fig, ax = plt.subplots(figsize=(12, 7))

# Group rooms into categories for business clarity
def categorize_rooms(rooms):
    if pd.isna(rooms):
        return 'Unknown'
    elif rooms == 1:
        return '1 Room'
    elif rooms == 2:
        return '2 Rooms'
    elif rooms == 3:
        return '3 Rooms'
    elif rooms == 4:
        return '4 Rooms'
    elif rooms >= 5:
        return '5+ Rooms'
    return 'Unknown'

df['room_category'] = df['rooms_clean'].apply(categorize_rooms)
room_order = ['1 Room', '2 Rooms', '3 Rooms', '4 Rooms', '5+ Rooms']
room_counts = df['room_category'].value_counts().reindex(room_order, fill_value=0)
room_pct = (room_counts / room_counts.sum() * 100).round(1)

colors = sns.color_palette("viridis", n_colors=len(room_counts))
bars = ax.bar(range(len(room_counts)), room_counts.values, color=colors, edgecolor='black', linewidth=1.5)
ax.set_xticks(range(len(room_counts)))
ax.set_xticklabels(room_counts.index, fontsize=11, fontweight='bold')
ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Property Size Distribution by Room Count\nMost Properties Have 2-4 Rooms',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)

# Add value labels
for i, (count, pct) in enumerate(zip(room_counts.values, room_pct.values)):
    ax.text(i, count + 100, f'{count:,}\n({pct}%)',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/03_room_configuration.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 4: Monthly Listing Activity Trend
# ============================================================================
print("4. Generating Monthly Listing Activity Trend...")
fig, ax = plt.subplots(figsize=(14, 7))

monthly_counts = df.groupby('year_month').size().sort_index()
months = [m.strftime('%b %Y') for m in monthly_counts.index]

ax.plot(range(len(monthly_counts)), monthly_counts.values,
        marker='o', linewidth=3, markersize=8, color='#2E86AB', markerfacecolor='#A23B72')
ax.fill_between(range(len(monthly_counts)), monthly_counts.values, alpha=0.3, color='#2E86AB')

ax.set_xticks(range(len(monthly_counts)))
ax.set_xticklabels(months, rotation=45, ha='right', fontsize=10)
ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Market Activity Timeline: Listing Volume Growth\n5x Growth from Oct 2024 to Jul 2025',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3)

# Add value labels for key points
for i in [0, len(monthly_counts)//2, -1]:
    ax.text(i, monthly_counts.values[i] + 100, f'{monthly_counts.values[i]:,}',
            ha='center', va='bottom', fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))

plt.tight_layout()
plt.savefig('charts/04_monthly_activity_trend.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 5: Property Type Mix in Top Cities
# ============================================================================
print("5. Generating Property Type Mix by City...")
fig, ax = plt.subplots(figsize=(14, 8))

top_cities = ['Bakı', 'Sumqayıt', 'Gəncə', 'Abşeron', 'Xırdalan']
top_property_types = ['Həyət evi - Villa', 'Yeni tikili', 'Köhnə tikili', 'Torpaq']

# Create data matrix
data_matrix = []
for city in top_cities:
    city_data = df[df['city'] == city]
    row = []
    for ptype in top_property_types:
        count = len(city_data[city_data['property_type'] == ptype])
        row.append(count)
    data_matrix.append(row)

data_matrix = np.array(data_matrix)
x = np.arange(len(top_cities))
width = 0.6

colors = ['#E63946', '#F1A208', '#2A9D8F', '#264653']
bottom = np.zeros(len(top_cities))

for i, ptype in enumerate(top_property_types):
    ax.bar(x, data_matrix[:, i], width, label=ptype, bottom=bottom, color=colors[i])
    bottom += data_matrix[:, i]

ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Property Type Composition in Major Markets\nDifferent Cities Have Different Market Preferences',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(top_cities, fontsize=11, fontweight='bold')
ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('charts/05_property_mix_by_city.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 6: Top Regions in Bakı
# ============================================================================
print("6. Generating Top Regions in Bakı...")
fig, ax = plt.subplots(figsize=(12, 7))

baku_data = df[df['city'] == 'Bakı']
region_counts = baku_data['region'].value_counts().head(10)

colors = sns.color_palette("coolwarm", n_colors=len(region_counts))
bars = ax.barh(range(len(region_counts)), region_counts.values, color=colors)
ax.set_yticks(range(len(region_counts)))
ax.set_yticklabels(region_counts.index)
ax.set_xlabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Hottest Regions in Bakı Real Estate Market\nSabunçu Leads with 1,737 Listings',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3)

# Add value labels
for i, count in enumerate(region_counts.values):
    ax.text(count + 20, i, f'{count:,}', va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/06_top_regions_baku.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 7: Average Property Size by Type
# ============================================================================
print("7. Generating Average Property Size by Type...")
fig, ax = plt.subplots(figsize=(12, 7))

# Filter out extreme outliers for meaningful business insights
df_filtered = df[(df['area_clean'] > 0) & (df['area_clean'] < 500)]
prop_types_main = ['Yeni tikili', 'Köhnə tikili', 'Həyət evi - Villa', 'Obyekt - Ofis']
area_by_type = df_filtered[df_filtered['property_type'].isin(prop_types_main)].groupby('property_type')['area_clean'].agg(['mean', 'median'])
area_by_type = area_by_type.reindex(prop_types_main)

x = np.arange(len(area_by_type))
width = 0.35

bars1 = ax.bar(x - width/2, area_by_type['mean'], width, label='Average Size', color='#0077B6', edgecolor='black')
bars2 = ax.bar(x + width/2, area_by_type['median'], width, label='Typical Size (Median)', color='#00B4D8', edgecolor='black')

ax.set_ylabel('Area (Square Meters)', fontsize=12, fontweight='bold')
ax.set_title('Property Size Analysis by Type\nVillas Are 2-3x Larger Than Apartments',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(area_by_type.index, fontsize=10, fontweight='bold', rotation=15, ha='right')
ax.legend(fontsize=10, loc='upper right')
ax.grid(axis='y', alpha=0.3)

# Add value labels
for i, (mean_val, med_val) in enumerate(zip(area_by_type['mean'], area_by_type['median'])):
    ax.text(i - width/2, mean_val + 5, f'{mean_val:.0f}m²',
            ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.text(i + width/2, med_val + 5, f'{med_val:.0f}m²',
            ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/07_property_size_by_type.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 8: Quarter-over-Quarter Growth
# ============================================================================
print("8. Generating Quarterly Growth Analysis...")
fig, ax = plt.subplots(figsize=(12, 7))

df['quarter'] = df['date_parsed'].dt.to_period('Q')
quarterly_counts = df.groupby('quarter').size()
quarters = [str(q) for q in quarterly_counts.index]

colors_q = ['#355C7D' if i % 2 == 0 else '#6C5B7B' for i in range(len(quarterly_counts))]
bars = ax.bar(range(len(quarterly_counts)), quarterly_counts.values, color=colors_q, edgecolor='black', linewidth=1.5)

ax.set_xticks(range(len(quarterly_counts)))
ax.set_xticklabels(quarters, fontsize=11, fontweight='bold', rotation=45, ha='right')
ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Quarterly Market Activity Comparison\nSteady Growth Across All Quarters',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)

# Add value labels
for i, count in enumerate(quarterly_counts.values):
    ax.text(i, count + 100, f'{count:,}', ha='center', va='bottom',
            fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/08_quarterly_growth.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 9: Room Distribution in Major Cities
# ============================================================================
print("9. Generating Room Distribution Comparison...")
fig, ax = plt.subplots(figsize=(14, 7))

top_cities_rooms = ['Bakı', 'Sumqayıt', 'Abşeron', 'Xırdalan']
room_categories = ['1 Room', '2 Rooms', '3 Rooms', '4 Rooms', '5+ Rooms']

data_rooms = []
for city in top_cities_rooms:
    city_data = df[df['city'] == city]
    row = []
    for cat in room_categories:
        count = len(city_data[city_data['room_category'] == cat])
        row.append(count)
    data_rooms.append(row)

data_rooms = np.array(data_rooms)
x = np.arange(len(room_categories))
width = 0.2

colors_cities = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
for i, city in enumerate(top_cities_rooms):
    offset = width * (i - 1.5)
    ax.bar(x + offset, data_rooms[i], width, label=city, color=colors_cities[i], edgecolor='black')

ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_xlabel('Room Configuration', fontsize=12, fontweight='bold')
ax.set_title('Room Configuration Preferences Across Major Cities\n3-Room Properties Dominate All Markets',
             fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(room_categories, fontsize=11, fontweight='bold')
ax.legend(fontsize=10, loc='upper right', framealpha=0.9)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('charts/09_room_distribution_cities.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 10: Market Activity by Day of Week
# ============================================================================
print("10. Generating Listing Activity by Day of Week...")
fig, ax = plt.subplots(figsize=(12, 7))

df['day_of_week'] = df['date_parsed'].dt.day_name()
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_counts = df['day_of_week'].value_counts().reindex(day_order, fill_value=0)

colors_days = sns.color_palette("Spectral", n_colors=7)
bars = ax.bar(range(len(day_counts)), day_counts.values, color=colors_days, edgecolor='black', linewidth=1.5)

ax.set_xticks(range(len(day_counts)))
ax.set_xticklabels(day_counts.index, fontsize=11, fontweight='bold')
ax.set_ylabel('Number of Listings', fontsize=12, fontweight='bold')
ax.set_title('Listing Activity Pattern by Day of Week\nIdentifying Peak Posting Days',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)

# Add value labels
for i, count in enumerate(day_counts.values):
    ax.text(i, count + 100, f'{count:,}', ha='center', va='bottom',
            fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/10_activity_by_weekday.png', dpi=300, bbox_inches='tight')
plt.close()

print("\n" + "="*80)
print("ALL CHARTS GENERATED SUCCESSFULLY!")
print("="*80)
print("Charts saved to: charts/")
print("Total charts created: 10")
print("="*80)
