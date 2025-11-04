import pprint
from alg_vis.libs.schema_parser import VSDXParser


if __name__ == "__main__":
    """
    Test script for the VSDXParser class.

    This script initializes the parser with a .vsdx file and prints the extracted schema.
    """
    VSDX_FILE_PATH = "test.vsdx"

    print(f"Parser initialization for file: {VSDX_FILE_PATH}")
    parser = VSDXParser(VSDX_FILE_PATH)
    schema_page1 = parser.parse()
    pprint.pprint(schema_page1)