import xml.etree.ElementTree as ET
import numpy as np
import logging
from .axis import Axis
from .curve import Curve
from .map import Map

class CDF:
    def __init__(self, filename):
        """
        Initialize the CDF parser with an XML file.

        :param filename: Path to the XML file
        :raises FileNotFoundError: If the file does not exist
        :raises ValueError: If the XML is malformed
        """
        self.filename = filename
        try:
            tree = ET.parse(self.filename)
            self.root = tree.getroot()
            self.params = {}
        except FileNotFoundError:
            raise FileNotFoundError(f"XML file {filename} not found")
        except ET.ParseError:
            raise ValueError(f"Invalid XML format in {filename}")

    def parse(self):
        """
        Parse the XML file and extract parameters into a dictionary.

        :return: Dictionary of parsed parameters (VALUE, COM_AXIS, CURVE, MAP, VAL_BLK, CUBE_4, CUBOID, BOOLEAN, BLOB)
        """
        params = {
            "VALUE": {}, "COM_AXIS": {}, "CURVE": {}, "MAP": {}, 
            "VAL_BLK": {}, "CUBE_4": {}, "CUBOID": {}, "BOOLEAN": {}, "BLOB": {}
        }
        for event, elem in ET.iterparse(self.filename, events=("end",)):
            if elem.tag == "SW-INSTANCE":
                data = self.sw_instance(elem)
                category = data.get("CATEGORY", "")
                short_name = data.get("SHORT-NAME", "")
                match category:
                    case "VALUE":
                        params["VALUE"][short_name] = data
                    case "COM_AXIS" | "RES_AXIS" | "CURVE_AXIS":
                        params["COM_AXIS"][short_name] = data  # Treat all axis types similarly
                    case "CURVE":
                        params["CURVE"][short_name] = data
                    case "MAP":
                        params["MAP"][short_name] = data
                    case "VAL_BLK":
                        params["VAL_BLK"][short_name] = data
                    case "CUBE_4":
                        params["CUBE_4"][short_name] = data
                    case "CUBOID":
                        params["CUBOID"][short_name] = data
                    case "BOOLEAN":
                        params["BOOLEAN"][short_name] = data
                    case "BLOB":
                        params["BLOB"][short_name] = data
                    case _:
                        logging.warning(f"Unknown category {category} for {short_name}")
                        params[short_name] = data
                elem.clear()

        # Process parameters
        for key in params["COM_AXIS"]:
            self.params[key] = self.com_axis(params["COM_AXIS"][key])
        for key in params["CURVE"]:
            self.params[key] = self.curve(params["CURVE"][key])
        for key in params["MAP"]:
            self.params[key] = self.map(params["MAP"][key])
        for key in params["VALUE"]:
            self.params[key] = self.value(params["VALUE"][key])
        for key in params["VAL_BLK"]:
            self.params[key] = self.val_blk(params["VAL_BLK"][key])
        for key in params["CUBE_4"]:
            self.params[key] = self.cube_4(params["CUBE_4"][key])
        for key in params["CUBOID"]:
            self.params[key] = self.cuboid(params["CUBOID"][key])
        for key in params["BOOLEAN"]:
            self.params[key] = self.boolean(params["BOOLEAN"][key])
        for key in params["BLOB"]:
            self.params[key] = self.blob(params["BLOB"][key])

        return self.params

    def value(self, data):
        """
        Parse a VALUE element into a single value or list of values.

        :param data: Dictionary from SW-INSTANCE
        :return: Parsed value (float, int, or string)
        """
        values = data["SW-VALUE-CONT"]["SW-VALUES-PHYS"]
        return values if len(values) > 1 else values[0]

    def boolean(self, data):
        """
        Parse a BOOLEAN element into a Python boolean.

        :param data: Dictionary from SW-INSTANCE
        :return: Boolean value
        """
        value = data["SW-VALUE-CONT"]["SW-VALUES-PHYS"][0]
        return value.lower() == "true" if isinstance(value, str) else bool(value)

    def com_axis(self, data):
        """
        Parse a COM_AXIS, RES_AXIS, or CURVE_AXIS element into an Axis object.

        :param data: Dictionary from SW-INSTANCE
        :return: Axis object
        """
        name = data["SHORT-NAME"]
        values = data["SW-VALUE-CONT"]["SW-VALUES-PHYS"]
        return Axis(values, name)

    def curve(self, data):
        """
        Parse a CURVE element into a Curve object.

        :param data: Dictionary from SW-INSTANCE
        :return: Curve object
        :raises ValueError: If axis type is unsupported or invalid
        """
        name = data["SHORT-NAME"]
        axis = data["SW-AXIS-CONTS"][0]
        category = axis["CATEGORY"]
        match category:
            case "FIX_AXIS" | "STD_AXIS" | "RES_AXIS" | "CURVE_AXIS":
                x = Axis(axis["SW-VALUES-PHYS"], f"{name}_x")
            case "COM_AXIS":
                ref_name = axis["SW-INSTANCE-REF"]
                x = self.params.get(ref_name)
            case _:
                raise ValueError(f"Unsupported axis category {category} for curve {name}")
        if x is None:
            raise ValueError(f"Invalid axis for curve {name}")
        y = data["SW-VALUE-CONT"]["SW-VALUES-PHYS"]
        return Curve(x, y, name)

    def map(self, data):
        """
        Parse a MAP element into a Map object.

        :param data: Dictionary from SW-INSTANCE
        :return: Map object
        :raises ValueError: If axis type is unsupported or invalid
        """
        name = data["SHORT-NAME"]
        x_axis = data["SW-AXIS-CONTS"][0]
        y_axis = data["SW-AXIS-CONTS"][1]
        
        # Handle x-axis
        match x_axis["CATEGORY"]:
            case "FIX_AXIS" | "STD_AXIS":
                x = Axis(x_axis["SW-VALUES-PHYS"], f"{name}_x")
            case "COM_AXIS":
                x = self.params.get(x_axis["SW-INSTANCE-REF"])
            case _:
                raise ValueError(f"Unsupported x-axis category {x_axis['CATEGORY']} for map {name}")
        
        # Handle y-axis
        match y_axis["CATEGORY"]:
            case "FIX_AXIS" | "STD_AXIS":
                y = Axis(y_axis["SW-VALUES-PHYS"], f"{name}_y")
            case "COM_AXIS":
                y = self.params.get(y_axis["SW-INSTANCE-REF"])
            case _:
                raise ValueError(f"Unsupported y-axis category {y_axis['CATEGORY']} for map {name}")

        if x is None or y is None:
            raise ValueError(f"Invalid axis for map {name}")

        z = data["SW-VALUE-CONT"]["SW-VALUES-PHYS"]
        # Convert z to 2D array based on axis lengths
        x_len, y_len = len(x.values), len(y.values)
        try:
            z_array = np.array(z).reshape(y_len, x_len)
        except ValueError:
            raise ValueError(f"Invalid z-values shape for map {name}: expected {y_len}x{x_len}, got {len(z)} values")
        
        return Map(x, y, z_array, name)

    def val_blk(self, data):
        """
        Parse a VAL_BLK element into a numpy array.

        :param data: Dictionary from SW-INSTANCE
        :return: Numpy array of values
        """
        name = data["SHORT-NAME"]
        values = data["SW-VALUE-CONT"]["SW-VALUES-PHYS"]
        dims = [int(size) for size in data["SW-VALUE-CONT"].get("SW-ARRAYSIZE", [len(values)])]
        try:
            return np.array(values).reshape(dims)
        except ValueError:
            raise ValueError(f"Invalid shape for VAL_BLK {name}: expected {dims}, got {len(values)} values")

    def cube_4(self, data):
        """
        Parse a CUBE_4 element into a numpy array.

        :param data: Dictionary from SW-INSTANCE
        :return: Numpy array of values
        """
        name = data["SHORT-NAME"]
        values = data["SW-VALUE-CONT"]["SW-VALUES-PHYS"]
        dims = [int(size) for size in data["SW-VALUE-CONT"].get("SW-ARRAYSIZE", [len(values)])]
        try:
            return np.array(values).reshape(dims)
        except ValueError:
            raise ValueError(f"Invalid shape for CUBE_4 {name}: expected {dims}, got {len(values)} values")

    def cuboid(self, data):
        """
        Parse a CUBOID element into a numpy array.

        :param data: Dictionary from SW-INSTANCE
        :return: Numpy array of values
        """
        name = data["SHORT-NAME"]
        values = data["SW-VALUE-CONT"]["SW-VALUES-PHYS"]
        dims = [int(size) for size in data["SW-VALUE-CONT"].get("SW-ARRAYSIZE", [len(values)])]
        try:
            return np.array(values).reshape(dims)
        except ValueError:
            raise ValueError(f"Invalid shape for CUBOID {name}: expected {dims}, got {len(values)} values")

    def blob(self, data):
        """
        Parse a BLOB element into a bytes object.

        :param data: Dictionary from SW-INSTANCE
        :return: Bytes object
        """
        value = data["SW-VALUE-CONT"]["SW-VALUES-PHYS"][0]
        try:
            return bytes.fromhex(value)
        except ValueError:
            raise ValueError(f"Invalid hex string for BLOB {data['SHORT-NAME']}: {value}")

    def sw_values_phys(self, item):
        """
        Parse SW-VALUES-PHYS XML element into a list of values.

        :param item: XML element containing SW-VALUES-PHYS
        :return: List of parsed values (floats, strings, or nested lists)
        :raises ValueError: If numeric values cannot be parsed
        """
        values = []
        for child in item:
            match child.tag:
                case "VT":
                    values.append(self.vt(child))
                case "VG":
                    values.append(self.vg(child))  # Keep nested structure for arrays
                case "V":
                    try:
                        values.append(float(child.text))
                    except (ValueError, TypeError):
                        raise ValueError(f"Invalid float value in SW-VALUES-PHYS: {child.text}")
        return values

    def sw_axis_cont(self, item):
        """
        Parse an SW-AXIS-CONT element.

        :param item: XML element
        :return: Dictionary of axis data
        """
        data = {}
        for child in item:
            match child.tag:
                case "CATEGORY":
                    data["CATEGORY"] = self.category(child)
                case "UNIT-DISPLAY-NAME":
                    data["UNIT-DISPLAY-NAME"] = self.unit_display_name(child)
                case "SW-INSTANCE-REF":
                    data["SW-INSTANCE-REF"] = self.sw_instance_ref(child)
                case "SW-ARRAYSIZE":
                    data["SW-ARRAYSIZE"] = self.sw_arraysize(child)
                case "SW-VALUES-PHYS":
                    data["SW-VALUES-PHYS"] = self.sw_values_phys(child)
        return data

    def sw_instance(self, item):
        """
        Parse an SW-INSTANCE XML element into a dictionary.

        :param item: XML element (SW-INSTANCE)
        :return: Dictionary containing parsed attributes and child elements
        """
        data = {}
        for child in item:
            match child.tag:
                case "SHORT-NAME":
                    data["SHORT-NAME"] = self.short_name(child)
                case "SW-ARRAY-INDEX":
                    data["SW-ARRAY-INDEX"] = self.sw_array_index(child)
                case "LONG-NAME":
                    data["LONG-NAME"] = self.long_name(child)
                case "DISPLAY-NAME":
                    data["DISPLAY-NAME"] = self.display_name(child)
                case "CATEGORY":
                    data["CATEGORY"] = self.category(child)
                case "SW-FEATURE-REF":
                    data["SW-FEATURE-REF"] = self.sw_feature_ref(child)
                case "SW-VALUE-CONT":
                    data["SW-VALUE-CONT"] = self.sw_value_cont(child)
                case "SW-AXIS-CONTS":
                    data["SW-AXIS-CONTS"] = self.sw_axis_conts(child)
                case "SW-CS-HISTORY":
                    data["SW-CS-HISTORY"] = self.sw_cs_history(child)
                case "SW-CS-FLAGS":
                    data["SW-CS-FLAGS"] = self.sw_cs_flags(child)
                case "SW-INSTANCE-PROPS-VARIANTS":
                    data["SW-INSTANCE-PROPS-VARIANTS"] = self.sw_instance_props_variants(child)
                case _:
                    logging.debug(f"Ignored tag in SW-INSTANCE: {child.tag}")
        return data

    def sw_value_cont(self, item):
        """
        Parse an SW-VALUE-CONT element.

        :param item: XML element
        :return: Dictionary of value content
        """
        data = {}
        for child in item:
            match child.tag:
                case "UNIT-DISPLAY-NAME":
                    data["UNIT-DISPLAY-NAME"] = self.unit_display_name(child)
                case "SW-ARRAYSIZE":
                    data["SW-ARRAYSIZE"] = self.sw_arraysize(child)
                case "SW-VALUES-PHYS":
                    data["SW-VALUES-PHYS"] = self.sw_values_phys(child)
        return data

    def sw_arraysize(self, item):
        """
        Parse an SW-ARRAYSIZE element into a list of dimensions.

        :param item: XML element
        :return: List of integers
        """
        return [int(v.text) for v in item.findall("V")]

    # Existing methods (unchanged for brevity)
    def category(self, item):
        return item.text

    def unit_display_name(self, item):
        return item.text

    def sw_instance_ref(self, item):
        return item.text

    def long_name(self, item):
        return item.text

    def short_name(self, item):
        return item.text

    def display_name(self, item):
        return item.text

    def sw_feature_ref(self, item):
        return item.text

    def sw_cs_history(self, item):
        return self.csentry(item)

    def sw_cs_flags(self, item):
        return self.csentry(item)

    def csentry(self, item):
        data = {}
        for child in item:
            match child.tag:
                case "STATE":
                    data["STATE"] = self.state(child)
                case "DATE":
                    data["DATE"] = self.date(child)
                case "CSUS":
                    data["CSUS"] = self.csus(child)
                case "CSPR":
                    data["CSPR"] = self.cspr(child)
                case "CSWP":
                    data["CSWP"] = self.cswp(child)
                case "CSTO":
                    data["CSTO"] = self.csto(child)
                case "CSTV":
                    data["CSTV"] = self.cstv(child)
                case "CSPI":
                    data["CSPI"] = self.cspi(child)
                case "CSDI":
                    data["CSDI"] = self.csdi(child)
                case "REMARK":
                    data["REMARK"] = self.remark(child)
                case "SD":
                    data["SD"] = self.sd(child)
        return data

    def state(self, item):
        return item.text

    def date(self, item):
        from datetime import datetime
        try:
            return datetime.strptime(item.text, "%Y-%m-%dT%H:%M:%S")
        except (ValueError, TypeError):
            return item.text

    def csus(self, item):
        return item.text

    def cspr(self, item):
        return item.text

    def cswp(self, item):
        return item.text

    def csto(self, item):
        return item.text

    def cstv(self, item):
        return item.text

    def cspi(self, item):
        return item.text

    def csdi(self, item):
        return item.text

    def remark(self, item):
        return [self.p(child) for child in item]

    def p(self, item):
        return item.text

    def sd(self, item):
        return (item.attrib, item.text)

    def sw_instance_props_variants(self, item):
        return [self.sw_instance_props_variant(child) for child in item]

    def sw_instance_props_variant(self, item):
        return {}  # Placeholder for future implementation

    def v(self, item):
        try:
            return float(item.text)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid float value: {item.text}")

    def vt(self, item):
        return item.text

    def vg(self, item):
        values = []
        for child in item:
            match child.tag:
                case "VT":
                    values.append(self.vt(child))
                case "V":
                    values.append(self.v(child))
        return values