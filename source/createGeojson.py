import json
import sys


def main(fileName='output', longLat=True):
    coordinates_input = input('Paste coordinates:')
    coordinates_input = coordinates_input.replace(' ', ',')
    coordinates_input = coordinates_input.replace('\n', ',')

    coordinates_input = coordinates_input.split(',')
    surZip = zip(coordinates_input[0::3], coordinates_input[1::3], coordinates_input[2::3])
    coordinates = []
    if longLat:
        for x in surZip:
            coordinates.append([float(x[0]), float(x[1])])
    else:
        for x in surZip:
            coordinates.append([float(x[1]), float(x[0])])

    geojson_output = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coordinates]
                }
            }
        ]
    }
    with open(f'static/geojson/{fileName}.geojson', 'w') as geojsonFile:
        json.dump(geojson_output, geojsonFile, indent=4)


if __name__ == '__main__':
    argv = sys.argv
    if len(argv) == 1:
        main()
        sys.exit()
    if argv[1] == '--help':
        print(
            'Usage: python createGeojson.py <fileName> [--longlat | --latlong]\n'
            '--longlat: Enter coordinates in longitude, latitude order.\n'
            '--latlong: Enter coordinates in latitude, longitude order.'
        )
        sys.exit()
    if argv[1] != '--help' and len(argv) == 2:
        main(argv[1], longLat=True)
        sys.exit()
    if argv[2] == '--longlat':
        main(argv[1], longLat=True)
    if argv[2] == '--latlong':
        main(argv[1], longLat=False)
