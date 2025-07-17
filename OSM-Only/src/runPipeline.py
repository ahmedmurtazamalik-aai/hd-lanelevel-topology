import os
import sys

if len(sys.argv) != 2:
    print("Usage: python run_pipeline.py <tif_path>")
    sys.exit(1)

tif_path = sys.argv[1]

print("Running lane to polyline conversion...")
os.system(f"python laneToPolyline.py {tif_path}")

print("Running graph builder...")
os.system("python graphBuilder.py")

print("Running junction detection...")
os.system("python junctionDetection.py")

print("Running connections building...")
os.system("python connectionBuilder.py")

print("Running OpenDRIVE exporter...")
os.system("python xodrExporter.py")

print("Validating generated OpenDRIVE file...")
os.system("python xodrVerify.py")
