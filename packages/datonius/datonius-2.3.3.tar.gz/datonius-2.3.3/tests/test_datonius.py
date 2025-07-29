#!/usr/bin/env python

"""Tests for `datonius` package."""


import unittest

from datonius import datonius as d
from datonius import cli
from datonius import util
from datonius import ontology


class TestMixin:
    """Tests for `datonius` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.ctx = d.make_connection(":memory:")
        self.db = self.ctx.__enter__()

    def tearDown(self):
        """Tear down test fixtures, if any."""
        self.ctx.__exit__(None, None, None)

class TestBasic(TestMixin, unittest.TestCase):

    def test_add_a_sample(self):
        self.assertEqual(d.Sample.create(oradss_id=1, _row_checksum="NOTNULL").id, 1)

class TestTaxon(TestMixin, unittest.TestCase):
    "Test Taxon parsing"


    def testGenus(self):
        self.assertEqual(d.Taxon.of("Salmonella").rank, 'genus')

    def testSp(self):
        self.assertEqual(d.Taxon.of('Salmonella', 'sp.').rank, 'genus')

    def testSpecies(self):
        self.assertEqual(d.Taxon.of("Salmonella", "enterica").rank, 'species')

    def testSubspecies(self):
        self.assertEqual(d.Taxon.of("Salmonella", "enterica", subspecies='enterica').rank, 'subspecies')

    def testSubsubspecies(self):
        self.assertEqual(d.Taxon.of("Salmonella", "enterica", serovar='nothing').rank, 'serovar')
        self.assertEqual(d.Taxon.of("Salmonella", "enterica", serotype='nothing').rank, 'serotype')

    def testRecursion(self):
        f = d.Taxon.create(name='Enterobacteriaceae', rank='family')
        f.save()

        g = d.Taxon.of("Salmonella")
        g.supertaxon = f
        g.save()

        t = d.Taxon.of("Salmonella", "enterica", subspecies="enterica", serovar="Typhimurium")
        t.save()

        assert t in list(d.Taxon.get(name='enterica',rank='subspecies').subtaxa)
        self.assertEqual(g.supertaxon.rank, 'family')
        self.assertListEqual(
            [taxon.rank for taxon in t._recurse()],
            ['family', 'genus', 'species', 'subspecies', 'serovar']
        )


class TestCli(unittest.TestCase):
    "Test CLI"

    def testLookup(self):
        "Test lookup subcommand"

    def testTax(self):
        "Test tax subcommand"

    def testOntology(self):
        "Test ontology subcommand"

class TestUtil(TestBasic):

    def testIsolateToDict(self):
        "Test isolate_to_dict function"

    def testSampleToDict(self):
        "Test sample_to_dict function"

    def testLookup(self):
        "Test lookup function"

    def testTax(self):
        "Test tax function"

    def testOntology(self):
        "Test ontology function"

class TestOntology(unittest.TestCase):

    def setUp(self):
        self.ctx = ontology.load_ontology()
        self.onto, self.struc = self.ctx.__enter__()

    def tearDown(self):
        self.ctx.__exit__(None, None, None)

    @unittest.skip("SSL")
    def test_search_one(self):
        self.assertEqual(self.onto.search_one(iri="*03530088")._name, "FOODON_03530088")

    @unittest.skip("SSL")
    def test_from_name_to_subnames(self):
        assert False
