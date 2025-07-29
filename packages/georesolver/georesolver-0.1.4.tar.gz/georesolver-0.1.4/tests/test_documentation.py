from georesolver import PlaceResolver

resolver = PlaceResolver(verbose=True)

# Resolve a place name
lat, lon = resolver.resolve("London", country_code="GB", place_type="city")
print(f"Coordinates: {lat}, {lon}")