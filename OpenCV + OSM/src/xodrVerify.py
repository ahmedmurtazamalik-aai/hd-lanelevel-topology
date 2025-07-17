import xmlschema
import sys

def validate_xodr(xodr_file, xsd_file):
    try:
        schema = xmlschema.XMLSchema(xsd_file)
        print("Schema loaded successfully.")

        if schema.is_valid(xodr_file):
            print(f"{xodr_file} is valid according to {xsd_file}.")
        else:
            print(f"{xodr_file} is NOT valid. Validation errors:")
            for error in schema.iter_errors(xodr_file):
                print(f" - {error}")

    except xmlschema.XMLSchemaException as e:
        print("Failed to load schema.")
        print(e)

if __name__ == "__main__":
    # Edit these paths as needed
    xodr_path = "../data/output/map.xodr"
    xsd_path = "../external/OpenDRIVE_1.4H_Schema.xsd"

    validate_xodr(xodr_path, xsd_path)
