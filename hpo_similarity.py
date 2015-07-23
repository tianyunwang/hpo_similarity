""" assess similarity of HPO terms in sets of probands.

If we have a set of probands who we know share some genetic feature in a gene,
we would like to know what is the probability of them sharing sharing their
Human Phenotype Ontology (HPO; standardised phenotypes) terms.

The HPO terms form a graph, so in order to estimate similarity, we use common
ancestors of sets of terms.
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import sys
import argparse

from hpo_similarity.load_files import load_participants_hpo_terms, load_genes
from hpo_similarity.ontology import Ontology
from hpo_similarity.similarity import ICSimilarity
from hpo_similarity.permute_probands import permute_probands
from hpo_similarity.analyse_genes import analyse_genes

def get_options():
    """ get the command line switches
    """
    
    parser = argparse.ArgumentParser(description="Examines the likelihood of \
        obtaining similar HPO terms in probands with variants in the same gene.")
    parser.add_argument("--genes", dest="genes_path", required=True, \
        help="Path to JSON file listing probands per gene. See \
            data/example_genes.json for format.")
    parser.add_argument("--phenotypes", dest="phenotypes_path", required=True, \
        help="Path to JSON file listing phenotypes per proband. See \
            data/example_phenotypes.json for format.")
    parser.add_argument("--ontology", \
        default=os.path.join(os.path.dirname(__file__), "data", "hp.obo"), \
        help="path to HPO ontology obo file, see http://human-phenotype-ontology.org")
    parser.add_argument("--output", default=sys.stdout, \
        help="path to output file, defaults to standard out.")
    parser.add_argument("--permute", action="store_true", default=False,
        help="whether to permute the probands across genes, in order to assess \
            method robustness.")
    parser.add_argument("--iterations", type=int, default=100000,
        help="whether to permute the probands across genes, in order to assess \
            method robustness.")
    
    args = parser.parse_args()
    
    return args

def main():
    
    options = get_options()
    
    # build a graph of HPO terms, so we can trace paths between terms
    hpo_ontology = Ontology(options.ontology)
    hpo_graph = hpo_ontology.get_graph()
    alt_node_ids = hpo_ontology.get_alt_ids()
    obsolete_ids = hpo_ontology.get_obsolete_ids()
    
    # load HPO terms and probands for each gene
    print("loading HPO terms and probands by gene")
    hpo_by_proband = load_participants_hpo_terms(options.phenotypes_path, \
        alt_node_ids, obsolete_ids)
    probands_by_gene = load_genes(options.genes_path)
    
    if options.permute:
        probands_by_gene = permute_probands(probands_by_gene)
    
    hpo_graph = ICSimilarity(hpo_by_proband, hpo_graph)
    
    print("analysing similarity")
    try:
        analyse_genes(hpo_graph, hpo_by_proband, probands_by_gene, \
            options.output, options.iterations)
    except KeyboardInterrupt:
        sys.exit("HPO similarity exited.")

if __name__ == '__main__':
    main()
