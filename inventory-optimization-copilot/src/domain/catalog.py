"""Shared fictional catalog data for deterministic generators."""

from __future__ import annotations

# (category, subcategory, product_name, base_unit_cost, supplier_category)
PRODUCT_CATALOG: list[tuple[str, str, str, float, str]] = [
    ("Tires", "All-Season", "Tour Plus 215/60R16", 89.99, "Tires"),
    ("Tires", "Performance", "Sport Grip 245/40R18", 124.50, "Tires"),
    ("Tires", "Winter", "SnowTrack 205/55R16", 98.75, "Tires"),
    ("Tires", "Commercial", "Fleet HD 225/75R16", 142.00, "Tires"),
    ("Brake Parts", "Pads", "Ceramic Brake Pad Set - Front", 34.25, "Brake Parts"),
    ("Brake Parts", "Rotors", "Vented Brake Rotor 11.8in", 48.90, "Brake Parts"),
    ("Brake Parts", "Calipers", "Reman Brake Caliper - Rear", 72.50, "Brake Parts"),
    ("Brake Parts", "Hardware", "Brake Hardware Kit", 12.40, "Brake Parts"),
    ("Batteries", "Automotive", "PowerStart 24F", 119.99, "Batteries"),
    ("Batteries", "AGM", "AGM 47H6", 189.00, "Batteries"),
    ("Batteries", "Marine", "Deep Cycle Marine 27DC", 145.50, "Batteries"),
    ("Batteries", "Standard", "Economy Battery 35R", 89.00, "Batteries"),
    ("Filters", "Oil", "Premium Oil Filter PF-2234", 8.75, "Filters"),
    ("Filters", "Air", "Engine Air Filter AF-9921", 14.20, "Filters"),
    ("Filters", "Cabin", "Cabin Air Filter CF-1180", 16.50, "Filters"),
    ("Filters", "Fuel", "Inline Fuel Filter FF-330", 11.90, "Filters"),
    ("Fluids", "Motor Oil", "Synthetic Motor Oil 5W-30 5qt", 28.99, "Fluids"),
    ("Fluids", "Coolant", "Extended Life Coolant 1gal", 18.50, "Fluids"),
    ("Fluids", "Brake Fluid", "DOT 4 Brake Fluid 12oz", 6.25, "Fluids"),
    ("Fluids", "Transmission", "ATF+4 Transmission Fluid 1qt", 9.80, "Fluids"),
    ("Tools", "Hand Tools", "3/8in Drive Socket Set 40pc", 54.00, "Tools"),
    ("Tools", "Diagnostic", "OBD-II Code Reader Pro", 129.00, "Tools"),
    ("Tools", "Power Tools", "Impact Wrench 1/2in 20V", 199.00, "Tools"),
    ("Tools", "Lifts", "Hydraulic Floor Jack 3-Ton", 165.00, "Tools"),
    ("Shop Supplies", "Cleaning", "Brake Cleaner 19oz", 5.50, "Shop Supplies"),
    ("Shop Supplies", "Safety", "Nitrile Gloves Box/100", 18.75, "Shop Supplies"),
    (
        "Shop Supplies",
        "Fasteners",
        "Assorted Clip & Retainer Kit",
        22.40,
        "Shop Supplies",
    ),
    ("Shop Supplies", "Lubricants", "Multi-Purpose Grease 14oz", 7.90, "Shop Supplies"),
    ("Accessories", "Wipers", "Beam Wiper Blade 22in", 19.99, "Accessories"),
    ("Accessories", "Belts", "Serpentine Belt 6-Rib 68in", 24.50, "Accessories"),
    ("Accessories", "Lighting", "LED Headlight Bulb H11 Pair", 39.00, "Accessories"),
    ("Accessories", "Floor Mats", "All-Weather Floor Mat Set", 49.99, "Accessories"),
]

# (location_id, location_name, location_type, region)
LOCATIONS: list[tuple[str, str, str, str]] = [
    ("LOC-001", "DC-NY", "Distribution Center", "Northeast"),
    ("LOC-002", "DC-NJ", "Distribution Center", "Northeast"),
    ("LOC-003", "DC-PA", "Distribution Center", "Northeast"),
    ("LOC-004", "Store-Bronx", "Retail Store", "NYC Metro"),
    ("LOC-005", "Store-Queens", "Retail Store", "NYC Metro"),
    ("LOC-006", "Store-Brooklyn", "Retail Store", "NYC Metro"),
    ("LOC-007", "Store-Manhattan", "Retail Store", "NYC Metro"),
    ("LOC-008", "Store-WhitePlains", "Retail Store", "NYC Metro"),
    ("LOC-009", "Store-Yonkers", "Retail Store", "NYC Metro"),
    ("LOC-010", "Store-Newark", "Retail Store", "New Jersey"),
    ("LOC-011", "Store-Stamford", "Retail Store", "Connecticut"),
]

SUPPLIER_TEMPLATES: list[tuple[str, str, str]] = [
    ("SUP-001", "Northline Parts Cooperative", "General"),
    ("SUP-002", "Metro Brake & Rotor Supply", "Brake Parts"),
    ("SUP-003", "Atlantic Battery Wholesale", "Batteries"),
    ("SUP-004", "FilterPro Distribution", "Filters"),
    ("SUP-005", "Summit Fluids Group", "Fluids"),
    ("SUP-006", "ProTool Industrial Supply", "Tools"),
    ("SUP-007", "ShopWorks Consumables", "Shop Supplies"),
    ("SUP-008", "DriveRight Accessories Inc.", "Accessories"),
    ("SUP-009", "FleetTread Tire Partners", "Tires"),
    ("SUP-010", "Harbor Supply Logistics", "General"),
]

CUSTOMER_SEGMENTS = [
    "Retail Walk-In",
    "Fleet Account",
    "Wholesale Counter",
    "E-Commerce",
    "Internal Transfer",
]

PO_STATUSES = [
    "Draft",
    "Approved",
    "Open",
    "Partially Received",
    "Received",
    "Late",
    "Cancelled",
    "Closed",
]

COUNT_STATUSES = [
    "Scheduled",
    "Completed",
    "Overdue",
    "Recount Required",
    "Missed",
]

REVIEW_STATUSES = ["Pending Review", "Approved", "Rejected", "Escalated"]

RECEIPT_STATUSES = ["Complete", "Partial", "Late", "Rejected", "Quality Hold"]

DEMAND_PATTERNS = [
    "stable",
    "trending",
    "seasonal",
    "intermittent",
    "promotional",
    "stockout_constrained",
    "no_recent_demand",
]

COUNTER_NAMES = [
    "Alex Rivera",
    "Jordan Kim",
    "Sam Patel",
    "Taylor Nguyen",
    "Casey Morgan",
]

BUYERS = ["D. Cruz", "M. Santos", "R. Bennett", "K. Okafor"]

PAYMENT_TERMS = ["Net 30", "Net 45", "Net 60", "2/10 Net 30"]

STATUS_SCENARIOS: list[dict[str, int]] = [
    {
        "quantity_on_hand": 3,
        "min_stock": 12,
        "max_stock": 48,
        "age_days": 25,
        "demand_90_day": 18,
    },
    {
        "quantity_on_hand": 22,
        "min_stock": 8,
        "max_stock": 40,
        "age_days": 410,
        "demand_90_day": 0,
    },
    {
        "quantity_on_hand": 85,
        "min_stock": 10,
        "max_stock": 35,
        "age_days": 245,
        "demand_90_day": 6,
    },
    {
        "quantity_on_hand": 72,
        "min_stock": 10,
        "max_stock": 35,
        "age_days": 95,
        "demand_90_day": 14,
    },
    {
        "quantity_on_hand": 28,
        "min_stock": 10,
        "max_stock": 40,
        "age_days": 210,
        "demand_90_day": 2,
    },
    {
        "quantity_on_hand": 24,
        "min_stock": 10,
        "max_stock": 45,
        "age_days": 40,
        "demand_90_day": 22,
    },
]
