import zipfile
from lxml import etree
import collections
from typing import Dict, List, Union


class VSDXParser:
    """
    A parser for extracting blocks and connections from a .vsdx file.

    Attributes:
        file_path (str): Path to the .vsdx file.
        ns (dict): XML namespaces used for parsing Visio files.
    """

    def __init__(self, file_path: str):
        """
        Initialize the VSDXParser with the path to the .vsdx file.

        Args:
            file_path (str): Path to the .vsdx file.
        """
        self.file_path = file_path
        self.ns = {'v': 'http://schemas.microsoft.com/office/visio/2012/main'}

    def parse(self, page_name: str = "page1.xml") -> Dict[str, List[Dict[str, Union[str, None]]]]:
        """
        Parse the .vsdx file and extract blocks and connections.

        Args:
            page_name (str): Name of the page XML file to parse. Defaults to "page1.xml".

        Returns:
            Dict[str, List[Dict[str, Union[str, None]]]]: A dictionary containing blocks and connections.
        """
        try:
            with zipfile.ZipFile(self.file_path, 'r') as vsdx_zip:
                page_path = f'visio/pages/{page_name}'

                if page_path not in vsdx_zip.namelist():
                    print(f"Error: File '{page_path}' not found in the .vsdx archive.")
                    pages = [f for f in vsdx_zip.namelist() if f.startswith('visio/pages/page') and f.endswith('.xml')]
                    if not pages:
                        print("Error: No page files (page...xml) found.")
                        return {"blocks": [], "connections": []}
                    page_path = pages[0]
                    print(f"Using the first found page instead: {page_path}")

                with vsdx_zip.open(page_path) as page_xml:
                    tree = etree.parse(page_xml)
                    return self._extract_schema(tree)

        except zipfile.BadZipFile:
            print(f"Error: File '{self.file_path}' is not a valid .vsdx archive.")
        except etree.XMLSyntaxError as e:
            print(f"Error: XML parsing error. {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        return {"blocks": [], "connections": []}

    def detect_block_type(self,shape_name, text):
        text = (text or "").strip().lower()
        name = (shape_name or "").lower()

        if "start" in text or any(n in name for n in ["terminator"]):
            return "start"
        if "stop" in text or "koniec" in text:
            return "stop"
        if any(n in name for n in ["decision","diamond"]) or any(op in text for op in [">", "<", "==", "!=","?"]):
            return "decision"
        if any(n in name for n in ["data","rectangle"]) or any(w in text for w in ["wczytaj", "wyświetl", "podaj","wypisz","wprowadź","zwróć", "read", "input", "return", "display"]):
            return "io"
        if "process" in name or any(pr in text for pr in ["=","dodaj","pobierz","usuń","utwórz","wybieramy","ustaw","przenieś", "add", "extract", "create", "select", "set"]):
            return "process"
        return "unknown"

    def _extract_schema(self, tree: etree._ElementTree) -> Dict[str, List[Dict[str, Union[str, None]]]]:
        """
        Extract blocks and connections from the parsed XML tree.

        Args:
            tree (etree._ElementTree): The parsed XML tree.

        Returns:
            Dict[str, List[Dict[str, Union[str, None]]]]: A dictionary containing blocks and connections.
        """
        all_shapes = {}

        for shape in tree.xpath('//v:Shape', namespaces=self.ns):
            shape_id = shape.get("ID")

            text_elements = shape.xpath('.//v:Text/text()', namespaces=self.ns)
            shape_text = "".join(text_elements).strip().replace('\n', ' ')
            shape_type = self.detect_block_type(shape.get("NameU"), shape_text)

            if not shape_text:
                shape_text = shape.get("NameU", "")

            all_shapes[shape_id] = {
                "id": shape_id,
                "name": shape.get("NameU"),
                "text": shape_text,
                "type": shape_type,
            }

        connections_map = collections.defaultdict(dict)
        connector_ids = set()

        for connect in tree.xpath('//v:Connect', namespaces=self.ns):
            connector_id = connect.get("FromSheet")
            block_id = connect.get("ToSheet")
            from_cell = connect.get("FromCell")

            connector_ids.add(connector_id)

            if from_cell and "Begin" in from_cell:
                connections_map[connector_id]["from_block_id"] = block_id
            elif from_cell and "End" in from_cell:
                connections_map[connector_id]["to_block_id"] = block_id

        final_blocks = []
        for shape_id, shape_data in all_shapes.items():
            if shape_id not in connector_ids:
                final_blocks.append(shape_data)

        final_connections = []
        for conn_id, conn_data in connections_map.items():
            connector_text = all_shapes.get(conn_id, {}).get("text", "")

            final_connections.append({
                "connector_id": conn_id,
                "from_block_id": conn_data.get("from_block_id"),
                "to_block_id": conn_data.get("to_block_id"),
                "text": connector_text
            })

        return {"blocks": final_blocks, "connections": final_connections}
