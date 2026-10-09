"""
Script to generate realistic test datasets in sample_data/ directory.
Produces:
1. sample_data/campus_survey.kml (Polygons, LineStrings, Points, ExtendedData)
2. sample_data/nature_reserve.kml (Multi-part geometries, hiking trails, conservation zones)
3. sample_data/parcels_shapefile.zip (Zipped shapefile with .shp, .shx, .dbf, .prj)
4. sample_data/corridors_shapefile.zip (Linear infrastructure network shapefile)
"""
import os
import zipfile
from pathlib import Path
import shapefile

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

# 1. Generate campus_survey.kml
CAMPUS_KML = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Metropolitan University Campus Survey</name>
    <description>Cadastral and asset survey containing administrative boundaries, pathways, and landmark points.</description>
    
    <!-- Polygon: Main Academic Quad -->
    <Placemark>
      <name>Main Academic Quad</name>
      <description>Central green zone and student commons</description>
      <ExtendedData>
        <Data name="FacilityCode"><value>QUAD-01</value></Data>
        <Data name="Zone"><value>Recreational Green</value></Data>
        <Data name="MaintainedBy"><value>Campus Grounds Dept</value></Data>
      </ExtendedData>
      <Polygon>
        <extrude>1</extrude>
        <altitudeMode>clampToGround</altitudeMode>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>
              -122.2580,37.8720,0
              -122.2560,37.8720,0
              -122.2560,37.8705,0
              -122.2580,37.8705,0
              -122.2580,37.8720,0
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>

    <!-- Polygon: Science Complex (with interior courtyard hole) -->
    <Placemark>
      <name>Science Complex</name>
      <description>Laboratory buildings with central atrium courtyard</description>
      <ExtendedData>
        <Data name="FacilityCode"><value>SCI-BLD</value></Data>
        <Data name="Floors"><value>4</value></Data>
      </ExtendedData>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>
              -122.2595,37.8735,0
              -122.2582,37.8735,0
              -122.2582,37.8725,0
              -122.2595,37.8725,0
              -122.2595,37.8735,0
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
        <innerBoundaryIs>
          <LinearRing>
            <coordinates>
              -122.2591,37.8732,0
              -122.2586,37.8732,0
              -122.2586,37.8728,0
              -122.2591,37.8728,0
              -122.2591,37.8732,0
            </coordinates>
          </LinearRing>
        </innerBoundaryIs>
      </Polygon>
    </Placemark>

    <!-- Polygon with unclosed ring to test automatic repair -->
    <Placemark>
      <name>Botanical Research Greenhouse</name>
      <description>Controlled flora experiment enclosure (unclosed ring)</description>
      <ExtendedData>
        <Data name="Code"><value>BIO-GREEN</value></Data>
      </ExtendedData>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>
              -122.2555,37.8715,0
              -122.2545,37.8715,0
              -122.2545,37.8708,0
              -122.2555,37.8708,0
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>

    <!-- LineString: North-South Pedestrian Promenade -->
    <Placemark>
      <name>North-South Pedestrian Promenade</name>
      <description>Primary illuminated pedestrian corridor</description>
      <ExtendedData>
        <Data name="Surface"><value>Paved Brick</value></Data>
        <Data name="Width_m"><value>6.5</value></Data>
      </ExtendedData>
      <LineString>
        <tessellate>1</tessellate>
        <coordinates>
          -122.2570,37.8745,0
          -122.2570,37.8725,0
          -122.2568,37.8700,0
          -122.2565,37.8680,0
        </coordinates>
      </LineString>
    </Placemark>

    <!-- LineString: Strawberry Creek Pathway -->
    <Placemark>
      <name>Strawberry Creek Pathway</name>
      <description>Meandering streamside nature trail</description>
      <ExtendedData>
        <Data name="Surface"><value>Crushed Gravel</value></Data>
      </ExtendedData>
      <LineString>
        <coordinates>
          -122.2600,37.8710,0
          -122.2588,37.8712,0
          -122.2575,37.8716,0
          -122.2560,37.8714,0
          -122.2548,37.8719,0
        </coordinates>
      </LineString>
    </Placemark>

    <!-- Point: Memorial Bell Tower -->
    <Placemark>
      <name>Memorial Campanile Bell Tower</name>
      <description>Iconic campus observation tower and geodetic landmark</description>
      <ExtendedData>
        <Data name="Height_m"><value>93.6</value></Data>
        <Data name="YearBuilt"><value>1914</value></Data>
      </ExtendedData>
      <Point>
        <coordinates>-122.2578,37.8721,93.6</coordinates>
      </Point>
    </Placemark>

    <!-- Point: Solar Weather Station -->
    <Placemark>
      <name>Atmospheric Monitoring Station #4</name>
      <description>Micro-climate telemetry sensor</description>
      <ExtendedData>
        <Data name="SensorType"><value>Davis Vantage Pro2</value></Data>
      </ExtendedData>
      <Point>
        <coordinates>-122.2550,37.8730,0</coordinates>
      </Point>
    </Placemark>

  </Document>
</kml>
"""

# 2. Generate nature_reserve.kml
NATURE_KML = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Redwood Wilderness Conservation Reserve</name>
    <Placemark>
      <name>Eagle Ridge Sanctuary</name>
      <description>Restricted wildlife preserve</description>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>
              -121.950,36.550,0
              -121.920,36.550,0
              -121.920,36.520,0
              -121.950,36.520,0
              -121.950,36.550,0
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
    <Placemark>
      <name>Ridgecrest Crestline Trail</name>
      <LineString>
        <coordinates>
          -121.960,36.560,0
          -121.940,36.545,0
          -121.930,36.530,0
          -121.915,36.510,0
        </coordinates>
      </LineString>
    </Placemark>
    <Placemark>
      <name>Lookout Ranger Post</name>
      <Point>
        <coordinates>-121.935,36.535,450</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>
"""

# Standard WGS84 .prj content
WGS84_PRJ = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'


def generate_parcels_shapefile():
    """Create zoned parcels polygon shapefile and zip it."""
    temp_dir = SAMPLE_DIR / "_temp_parcels"
    temp_dir.mkdir(parents=True, exist_ok=True)
    shp_base = temp_dir / "parcels"

    w = shapefile.Writer(str(shp_base), shapeType=shapefile.POLYGON)
    w.field("PARCEL_ID", "C", size=20)
    w.field("ZONING", "C", size=30)
    w.field("OWNER", "C", size=50)
    w.field("VALUATION", "N", decimal=2)

    # Parcel 1: Commercial Tech Hub
    w.poly([
        [
            [-74.0080, 40.7120],
            [-74.0040, 40.7120],
            [-74.0040, 40.7090],
            [-74.0080, 40.7090],
            [-74.0080, 40.7120],
        ]
    ])
    w.record("P-1001", "Commercial C-4", "Metropolis Development Corp", 18500000.0)

    # Parcel 2: Residential Heights
    w.poly([
        [
            [-74.0035, 40.7120],
            [-73.9990, 40.7120],
            [-73.9990, 40.7085],
            [-74.0035, 40.7085],
            [-74.0035, 40.7120],
        ]
    ])
    w.record("P-1002", "Residential High-Density R-5", "Urban Housing Authority", 12400000.0)

    # Parcel 3: Civic Park Commons
    w.poly([
        [
            [-74.0075, 40.7080],
            [-74.0000, 40.7080],
            [-74.0000, 40.7050],
            [-74.0075, 40.7050],
            [-74.0075, 40.7080],
        ]
    ])
    w.record("P-1003", "Public Parks & Recreation", "City Parks Department", 4500000.0)

    w.close()

    # Write .prj
    with open(temp_dir / "parcels.prj", "w") as f:
        f.write(WGS84_PRJ)

    # Create ZIP archive
    zip_path = SAMPLE_DIR / "parcels_shapefile.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for ext in [".shp", ".shx", ".dbf", ".prj"]:
            file_to_zip = temp_dir / f"parcels{ext}"
            if file_to_zip.exists():
                zf.write(file_to_zip, arcname=f"parcels{ext}")
                file_to_zip.unlink()

    # Clean up temp dir
    try:
        temp_dir.rmdir()
    except Exception:
        pass


def generate_corridors_shapefile():
    """Create transportation corridors line shapefile and zip it."""
    temp_dir = SAMPLE_DIR / "_temp_corridors"
    temp_dir.mkdir(parents=True, exist_ok=True)
    shp_base = temp_dir / "corridors"

    w = shapefile.Writer(str(shp_base), shapeType=shapefile.POLYLINE)
    w.field("ROUTE_ID", "C", size=20)
    w.field("CLASS", "C", size=30)
    w.field("LANES", "N")

    # Highway Corridor
    w.line([
        [
            [-74.0150, 40.7150],
            [-74.0100, 40.7110],
            [-74.0050, 40.7070],
            [-73.9980, 40.7020],
        ]
    ])
    w.record("HWY-101", "Arterial Expressway", 6)

    # Transit Rail Line
    w.line([
        [
            [-74.0120, 40.7180],
            [-74.0080, 40.7130],
            [-74.0020, 40.7080],
            [-73.9950, 40.7040],
        ]
    ])
    w.record("METRO-BLUE", "Rapid Transit Rail", 2)

    w.close()

    # Write .prj
    with open(temp_dir / "corridors.prj", "w") as f:
        f.write(WGS84_PRJ)

    # Create ZIP archive
    zip_path = SAMPLE_DIR / "corridors_shapefile.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for ext in [".shp", ".shx", ".dbf", ".prj"]:
            file_to_zip = temp_dir / f"corridors{ext}"
            if file_to_zip.exists():
                zf.write(file_to_zip, arcname=f"corridors{ext}")
                file_to_zip.unlink()

    try:
        temp_dir.rmdir()
    except Exception:
        pass


def main():
    print("Generating sample datasets...")
    # Write KMLs
    with open(SAMPLE_DIR / "campus_survey.kml", "w", encoding="utf-8") as f:
        f.write(CAMPUS_KML)
    print("Created sample_data/campus_survey.kml")

    with open(SAMPLE_DIR / "nature_reserve.kml", "w", encoding="utf-8") as f:
        f.write(NATURE_KML)
    print("Created sample_data/nature_reserve.kml")

    # Write Shapefile ZIPs
    generate_parcels_shapefile()
    print("Created sample_data/parcels_shapefile.zip")

    generate_corridors_shapefile()
    print("Created sample_data/corridors_shapefile.zip")
    print("All sample datasets generated successfully.")


if __name__ == "__main__":
    main()
