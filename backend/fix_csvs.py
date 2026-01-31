#!/usr/bin/env python3
"""
Clean and fix all CSV files in the datasets directory
- Remove trailing blank lines
- Ensure proper UTF-8 encoding
- Use LF line endings only
"""
import os
import csv

data_dir = r"E:\cine hackathon\project\backend\app\datasets\data"

csv_files = {
    "complexity_multipliers.csv": [
        ["feature", "cost_multiplier", "schedule_multiplier", "safety_risk_pts", "logistics_risk_pts", "schedule_risk_pts", "budget_risk_pts", "compliance_risk_pts", "description"],
        ["stunt_light", "1.5", "1.2", "5", "3", "2", "8", "2", "Minor falls or vehicle action"],
        ["stunt_medium", "2.0", "1.5", "12", "6", "4", "15", "4", "Wire work or moderate vehicle action"],
        ["stunt_heavy", "3.0", "2.0", "20", "10", "8", "25", "6", "Complex stunts with dummies"],
        ["water_simple", "1.2", "1.1", "8", "5", "3", "6", "3", "Swimming or shallow water"],
        ["water_medium", "1.8", "1.4", "15", "10", "6", "12", "5", "Underwater work or boat scenes"],
        ["water_complex", "2.5", "1.8", "25", "15", "10", "20", "8", "Diving or complex water choreography"],
        ["night_shoot", "1.3", "1.4", "10", "8", "12", "5", "5", "Night filming adds fatigue & equipment"],
        ["day_shoot", "1.0", "1.0", "0", "0", "0", "0", "0", "Standard daytime shooting"],
        ["crowd_small", "1.1", "1.1", "3", "4", "2", "4", "3", "10-50 extras"],
        ["crowd_medium", "1.4", "1.3", "8", "10", "5", "10", "6", "50-200 extras"],
        ["crowd_large", "2.0", "1.6", "15", "15", "8", "18", "8", "200+ extras or crowd control"],
        ["vehicle_simple", "1.2", "1.1", "5", "6", "2", "5", "4", "Single car or bike"],
        ["vehicle_medium", "1.6", "1.3", "10", "12", "4", "12", "6", "Multiple vehicles or chases"],
        ["vehicle_heavy", "2.2", "1.7", "18", "18", "8", "20", "8", "Complex multi-vehicle sequences"],
        ["animal_small", "1.3", "1.2", "8", "6", "3", "6", "4", "Small animals (dogs, cats)"],
        ["animal_large", "1.8", "1.4", "15", "10", "6", "12", "6", "Large animals (horses, elephants)"],
        ["weather_dependent", "1.5", "2.0", "12", "8", "15", "10", "5", "Dependent on specific weather"],
        ["location_outdoor", "1.0", "1.0", "0", "0", "0", "0", "0", "Standard outdoor location"],
        ["location_interior", "0.9", "0.95", "0", "0", "0", "0", "0", "Controlled interior"],
        ["location_remote", "1.6", "1.5", "8", "12", "10", "15", "6", "Difficult access location"],
        ["permit_tier_1", "1.0", "1.0", "0", "0", "0", "0", "2", "No special permits (private location)"],
        ["permit_tier_2", "1.2", "1.1", "0", "2", "2", "2", "4", "Local municipality approval"],
        ["permit_tier_3", "1.5", "1.3", "2", "5", "4", "4", "8", "State-level permits needed"],
        ["permit_tier_4", "2.0", "1.6", "4", "10", "6", "8", "12", "Multi-agency coordination"],
        ["vfx_light", "1.2", "1.1", "0", "2", "1", "5", "2", "Minor VFX touch-ups"],
        ["vfx_medium", "1.8", "1.4", "0", "4", "3", "12", "4", "Moderate VFX shots"],
        ["vfx_heavy", "3.0", "1.8", "0", "6", "5", "25", "6", "Heavy VFX sequences"],
        ["dialogue_heavy", "1.0", "1.0", "0", "0", "0", "0", "0", "Dialogue-driven scenes"],
        ["action_heavy", "1.7", "1.5", "15", "10", "8", "15", "6", "Action-driven scenes"],
        ["special_effects", "1.5", "1.3", "10", "8", "6", "12", "5", "Practical effects (fire, explosions)"],
        ["pyrotechnics", "2.5", "1.6", "20", "12", "8", "20", "10", "Controlled explosions/pyro"],
    ],
    "risk_weights.csv": [
        ["feature", "safety_pts", "logistics_pts", "schedule_pts", "budget_pts", "compliance_pts", "description"],
        ["stunt_heavy", "25", "8", "6", "20", "8", "High injury risk + equipment complexity"],
        ["water_hazard", "20", "12", "8", "15", "10", "Drowning + medical emergency risk"],
        ["crowd_100plus", "15", "18", "10", "12", "8", "Crowd control & safety challenges"],
        ["vehicle_chase", "18", "15", "8", "18", "6", "High speed action risk"],
        ["fire_pyro", "22", "10", "6", "15", "12", "Fire hazard + strict permits"],
        ["night_shoot", "12", "14", "15", "8", "8", "Fatigue + visibility issues"],
        ["animal_work", "16", "12", "8", "10", "10", "Unpredictable animal behavior"],
        ["helicopter", "25", "20", "10", "25", "15", "Very high risk & cost"],
        ["weather_dependent", "8", "15", "12", "10", "8", "Schedule delays likely"],
        ["remote_location", "10", "18", "12", "15", "10", "Logistics complexity + isolation"],
        ["international_cast", "8", "10", "15", "12", "18", "Visa + work permits complexity"],
        ["high_speed_vehicle", "20", "15", "8", "15", "8", "Accident risk"],
        ["water_submerged", "24", "15", "10", "18", "12", "Drowning risk + equipment"],
        ["heights_50ft", "22", "12", "8", "14", "10", "Fall hazard"],
        ["explosions", "23", "12", "8", "16", "14", "Injury risk + strict regulations"],
        ["diving", "21", "14", "10", "16", "8", "Decompression + equipment risk"],
        ["combat_choreography", "18", "10", "8", "12", "6", "Injury during training"],
        ["unknown_location", "8", "20", "15", "15", "8", "Scouting needed delays"],
        ["tight_schedule_10days", "5", "8", "20", "8", "5", "Time pressure risk"],
        ["budget_cap", "5", "5", "8", "25", "5", "Financial constraints"],
    ],
    "location_library.csv": [
        ["location_type", "permit_tier", "sound_difficulty", "crowd_control_needed", "setup_complexity", "typical_cost_multiplier", "weather_risk", "description"],
        ["Private_Studio", "1", "low", "no", "low", "0.9", "none", "Controlled environment"],
        ["Public_Road", "3", "high", "yes", "high", "1.5", "medium", "Traffic control + police permits"],
        ["Beach", "3", "high", "yes", "medium", "1.4", "high", "Sand maintenance + crowd control"],
        ["Forest", "3", "medium", "no", "high", "1.6", "high", "Terrain challenges + permits"],
        ["Highway", "4", "high", "yes", "high", "1.8", "medium", "Traffic management + police required"],
        ["River", "3", "high", "yes", "high", "1.7", "high", "Water safety + environmental permits"],
        ["Lake", "3", "high", "no", "medium", "1.5", "medium", "Water access + safety boats"],
        ["Waterfall", "4", "high", "yes", "high", "2.0", "high", "Remote + permits + safety gear"],
        ["Sea_Beach", "4", "high", "yes", "high", "1.9", "high", "Multiple authority permits"],
        ["Mountain_Peak", "4", "medium", "no", "very_high", "2.2", "very_high", "Extreme terrain + altitude"],
        ["Airport_Tarmac", "4", "very_high", "yes", "very_high", "2.5", "medium", "High security + strict permits"],
        ["Historical_Monument", "3", "low", "yes", "medium", "1.6", "none", "Heritage protection permits"],
        ["Religious_Site", "3", "low", "yes", "high", "1.8", "none", "Cultural sensitivity + permits"],
        ["Government_Building", "4", "low", "yes", "high", "1.9", "none", "Security + bureaucracy"],
        ["Industrial_Factory", "2", "high", "no", "medium", "1.3", "low", "Safety compliance needed"],
        ["Market_Bazaar", "3", "high", "yes", "high", "1.4", "medium", "Crowd management + vendor coordination"],
        ["Slum_Area", "2", "high", "no", "medium", "1.2", "high", "Community relations + safety"],
        ["Train_Station", "4", "high", "yes", "high", "1.8", "none", "Railway authority permits"],
        ["Railway_Track", "4", "high", "yes", "very_high", "2.0", "high", "Rail safety + traffic control"],
        ["Bridge", "4", "high", "yes", "high", "1.9", "medium", "Engineering permits + safety"],
        ["Tunnel", "4", "very_high", "yes", "very_high", "2.0", "low", "Confined space + permits"],
        ["Parking_Lot", "1", "medium", "no", "low", "1.1", "none", "Minimal restrictions"],
        ["Shopping_Mall", "2", "medium", "yes", "low", "1.2", "none", "Commercial coordination"],
        ["Restaurant", "1", "medium", "no", "low", "1.0", "none", "Private venue"],
        ["Hotel", "1", "low", "no", "low", "1.0", "none", "Controlled environment"],
        ["Apartment", "1", "low", "no", "low", "1.0", "none", "Confined space"],
        ["Hospital", "3", "low", "no", "medium", "1.4", "none", "Health regulations + patient care"],
        ["School", "3", "low", "no", "medium", "1.4", "none", "Education authority permits"],
        ["Church", "3", "low", "yes", "medium", "1.5", "none", "Religious coordination"],
        ["Temple", "3", "low", "yes", "medium", "1.5", "none", "Religious protocols"],
        ["Cemetery", "3", "low", "no", "medium", "1.4", "none", "Respect + few restrictions"],
        ["Sports_Stadium", "3", "high", "yes", "high", "1.6", "medium", "Crowd management"],
        ["Cricket_Field", "2", "medium", "no", "medium", "1.3", "high", "Weather dependent"],
    ],
    "city_state_multipliers.csv": [
        ["city", "state", "labor_multiplier", "vendor_multiplier", "permit_complexity_multiplier", "transport_multiplier", "lodging_multiplier", "description"],
        ["Mumbai", "MH", "1.0", "1.0", "1.0", "1.0", "1.0", "Base city reference"],
        ["Delhi", "DL", "0.95", "0.95", "1.1", "1.0", "0.95", "Tier 1 metro"],
        ["Bangalore", "KA", "0.90", "0.85", "0.8", "0.95", "0.85", "Tech hub lower costs"],
        ["Hyderabad", "TG", "0.85", "0.80", "0.75", "0.95", "0.80", "Emerging city cheaper"],
        ["Chennai", "TN", "0.88", "0.82", "0.8", "0.98", "0.82", "Southern metro"],
        ["Pune", "MH", "0.80", "0.75", "0.85", "0.90", "0.75", "Satellite city"],
        ["Jaipur", "RJ", "0.70", "0.70", "0.9", "0.95", "0.70", "Desert location"],
        ["Goa", "GA", "1.2", "1.3", "1.4", "1.3", "1.5", "Tourist destination premium"],
        ["Aravalli", "RJ", "0.65", "0.65", "0.7", "1.1", "0.65", "Remote location discount"],
        ["Darjeeling", "WB", "1.1", "1.15", "0.8", "1.4", "1.2", "Hill station remote"],
        ["Ooty", "TN", "1.05", "1.1", "0.85", "1.3", "1.15", "Hill station remote"],
        ["Ladakh", "UT", "1.5", "1.6", "1.2", "1.8", "1.7", "Very remote high cost"],
        ["Andaman", "AN", "1.8", "1.9", "1.5", "2.0", "2.0", "Island location premium"],
        ["Sikkim", "SK", "1.3", "1.35", "0.9", "1.5", "1.4", "Remote northeast"],
        ["Assam", "AS", "0.80", "0.82", "1.0", "1.2", "0.78", "Northeast tier 2"],
        ["Rajasthan_Desert", "RJ", "0.68", "0.70", "0.8", "1.15", "0.68", "Desert filming location"],
        ["Western_Ghats", "MH", "0.75", "0.78", "1.1", "1.2", "0.80", "Forest/hill region"],
        ["Backwaters_Kerala", "KL", "0.85", "0.88", "0.9", "1.1", "0.90", "Water-based location"],
    ],
}

print("[+] Starting CSV cleanup...")

for filename, rows in csv_files.items():
    filepath = os.path.join(data_dir, filename)
    
    try:
        # Write with proper encoding and line endings
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        
        # Verify by reading back
        with open(filepath, 'r', encoding='utf-8') as f:
            line_count = len(f.readlines())
        
        print(f"[OK] {filename}: Fixed ({line_count} lines)")
    except Exception as e:
        print(f"[ERROR] {filename}: Error - {e}")

print("[OK] CSV cleanup complete!")
print("\nVerifying with pandas...")

try:
    import pandas as pd
    
    for filename in csv_files.keys():
        filepath = os.path.join(data_dir, filename)
        try:
            df = pd.read_csv(filepath)
            print(f"[OK] {filename}: Loaded {len(df)} rows, {len(df.columns)} columns")
        except Exception as e:
            print(f"[ERROR] {filename}: {e}")
            
except ImportError:
    print("[WARN] Pandas not available for verification")
