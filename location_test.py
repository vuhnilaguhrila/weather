import geocoder

myloc = geocoder.ip('me')
print(myloc.city)