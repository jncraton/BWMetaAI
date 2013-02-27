import csv
import json

f = open( 'units.csv', 'r' )
reader = csv.DictReader( f )
out = json.dumps( [ row for row in reader ] )
print out