#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test StationXML creation
"""
from pathlib import Path
import glob
import unittest
import inspect
# from pprint import pprint
import xml.etree.ElementTree as ET
from CompareXMLTree import XmlTree
import warnings
from argparse import Namespace
import pytest

from obsinfo.console_scripts.stationxml import main as make_StationXML
from obsinfo.misc.datapath import (Datapath)


warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
verbose = False

     
testing_path = Path(__file__).parent / "data_xml"
subnetwork_files_path = (Path(__file__).resolve().parents[1] /
                                "_examples" / 'subnetwork_files')
instrumentation_files_path = (Path(__file__).resolve().parents[1] /
                                "_examples" / 'instrumentation_files')
ns = Namespace()
ns.quiet = True
ns.remote = False
ns.verbose = False
ns.station = False
ns.test = False
ns.output = None

@pytest.mark.parametrize("fname", ["EXAMPLE_typical.subnetwork.yaml",
                                   "EXAMPLE_essential.subnetwork.yaml"])
def test_makeSTATIONXML(fname):
    """
    Test STATIONXML creation.
    """

    ns.input_filename = [str(subnetwork_files_path / fname)]
    make_StationXML(ns, Datapath(str(instrumentation_files_path)))

    compare = XmlTree()
    # excluded elements
    # excludes = ["Created", "Real", "Imaginary", "Numerator",
    #             "CreationDate", "Description", "Module"]
    # excludes_attributes = ["startDate", "endDate"]
    excludes = ["Created", "Module"]
    excludes_attributes = []

    excludes = [compare.add_ns(x) for x in excludes]
    for stxml in glob.glob("*.xml"):
        xml1 = ET.parse(stxml)
        xml2 = ET.parse(testing_path / stxml)
        assert compare.xml_compare(compare.getroot(xml1), compare.getroot(xml2),
                                   excludes=excludes,
                                   excludes_attributes=excludes_attributes) is True
        Path(stxml).unlink()
