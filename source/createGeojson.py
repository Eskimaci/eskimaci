import json
import sys


def main(nazovSuboru='output', longLat=True):
    suradnizeInput = input('vloz suradnice:')
    suradnizeInput = suradnizeInput.replace(' ', ',')
    suradnizeInput = suradnizeInput.replace('\n', ',')

    suradnizeInput = suradnizeInput.split(',')
    surZip = zip(suradnizeInput[0::3], suradnizeInput[1::3], suradnizeInput[2::3])
    suradnice = []
    if longLat:
        for x in surZip:
            suradnice.append([float(x[0]), float(x[1])])
    else:
        for x in surZip:
            suradnice.append([float(x[1]), float(x[0])])

    suradniceGeoJson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [suradnice]
                }
            }
        ]
    }
    with open(f'static/geojson/{nazovSuboru}.geojson', 'w') as geojsonFile:
        json.dump(suradniceGeoJson, geojsonFile, indent=4)


if __name__ == '__main__':
    argv = sys.argv
    if len(argv) == 1:
        main()
        sys.exit()
    if argv[1] == '--help':
        print(
            'Pouzitie: python createGeojson.py nazovSuboru --longlat alebo --latlong \n--longlat: zadavat suradnice v poradi dlzka, sirka\n--latlong: zadavat suradnice v poradi sirka, dlzka')
        sys.exit()
    if argv[1] != '--help' and len(argv) == 2:
        main(argv[1], longLat=True)
        sys.exit()
    if argv[2] == '--longlat':
        main(longLat=True)
    if argv[2] == '--latlong':
        main(longLat=False)
