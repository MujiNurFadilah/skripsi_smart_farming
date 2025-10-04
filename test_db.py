from database import FuzzyDatabase

# Test database functionality
db = FuzzyDatabase()

# Get all calculations
calculations = db.get_all_calculations()
print(f'Total calculations: {len(calculations)}')

if calculations:
    print('First calculation:', calculations[0])
else:
    print('No calculations found')

# Get statistics
stats = db.get_calculation_statistics()
print('Statistics:', stats)