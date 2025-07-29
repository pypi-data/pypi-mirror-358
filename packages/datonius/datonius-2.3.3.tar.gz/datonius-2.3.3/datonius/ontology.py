import owlready2
from rdflib import Graph
import logging
import requests
import json


from contextlib import contextmanager
from pathlib import Path
import csv

log = logging.getLogger()

ontology_url = "https://github.com/FoodOntology/foodon/raw/master/foodon-base.owl"
ontology_synonyms = "https://github.com/FoodOntology/foodon/raw/master/foodon-synonyms.tsv"

# ontology_repo = "https://github.com/FoodOntology/foodon.git"

repo_api = "https://api.github.com/repos/FoodOntology/foodon/releases/latest"

class StaleOntologyError(Exception):
    pass

@contextmanager
def load_ontology(local_ont = Path.home().absolute() / ".datonius" / "ontology", tries=1):
    res = requests.get(repo_api)
    res.raise_for_status()
    repo_info = res.json()
    local_ont.mkdir(parents=True, exist_ok=True)
    # onto = owlready2.get_ontology(ontology_url).load()
    try:
        with open(local_ont / "metadata.json") as info_file:
            ont_info = json.load(info_file)
            if ont_info['version'] != repo_info['tag_name']:
                raise StaleOntologyError(f"stored version is {ont_info['version']}, current version is {repo_info['tag_name']}")
            with open(local_ont / "foodon-synonyms.tsv", encoding="UTF-8") as syn_file:
                struct = list(csv.reader(syn_file, dialect="excel", delimiter="\t"))
            with open(local_ont / "foodon-base.owl") as onto_file:
                onto = Graph()
                onto.parse(onto_file, format="application/rfc+xml")
            yield onto, struct
    except (StaleOntologyError, FileNotFoundError, json.decoder.JSONDecodeError) as e:
        log.warning(e)
        if not tries:
            raise Exception("Couldn't retreive FoodON ontology files.") from e
        with open(local_ont / "metadata.json", 'w') as info_file, open(local_ont / "foodon-synonyms.tsv", 'wb') as syn_file, open(local_ont / "foodon-base.owl", 'wb') as onto_file:
            res = requests.get(ontology_synonyms)
            res.raise_for_status()
            syn_file.write(res.content)
            res = requests.get(ontology_url)
            res.raise_for_status()
            onto_file.write(res.content)
            json.dump( dict(version = repo_info['tag_name']), info_file)
        with load_ontology(local_ont, tries-1) as onto, struct:
            yield onto, struct

if __name__ == '__main__':
    with load_ontology() as (onto, _):
        # print(dir(onto))
        # print(vars(onto.search_one(iri="*03530088")))
        pass



"""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> PREFIX OBO: <http://purl.obolibrary.org/obo/>
PREFIX xmls: <http://www.w3.org/2001/XMLSchema#>
SELECT DISTINCT ?ontology_id ?label WHERE {?ontology_id rdfs:label ?label}
"""