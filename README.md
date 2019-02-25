# bag2pc
Van de BAG naar postcode gebieden (experimenteel). Dit beoogt het genereren van postcodevlakken op basis van de BAG.

# installatie

1. `git clone git@github.com:openstate/bag2pc.git`
2. `cd bag2pc`
3. `docker-compose up -d`

# genereren

1. `docker exec bag2pc_bag2pc_1 bin/update.sh`
2. `docker exec bag2pc_bag2pc_1 python generate.py >test.geojson`

# issues

1. Het leest momenteel alleen de eerste 10.000 regels van het BAG bestand -- De compelte BAG is nog te groot
2. De gebieden worden nog niet afgekapt op de kaart van Nederland (Die is wel beschikbaar via geopandas)
3. Nog geen gebruik van NDW wegenbestand om de vlakken beter te maken
4. Nog niet alle voronoi vlakken worden terug gevonden (Ie. gekoppeld aan het originele punt zodat we weten welke vlakken bij welke postcode horen)
5. Nog niet mogeilijk om PC6, 5, 4 etc. te genereren

# contact

Breyten Ernsting <breyten@openstate.eu>
