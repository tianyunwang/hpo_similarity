"""
Copyright (c) 2015 Wellcome Trust Sanger Institute

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import os
import json
import argparse

def get_options():
    
    parser = argparse.ArgumentParser(description="prepare the HPO terms from" \
        "probands in the DDD study.")
    parser.add_argument("--phenotypes", required=True, help="Path to table of" \
        "phenotypes per proband, including child HPO terms.")
    parser.add_argument("--sample-ids", help="Path to file that"
        "maps between sample IDs for participants in the DDD study.")
    parser.add_argument("--trios", help="Path to file that"
        "defines the probands in exome-sequenced trios.")
    parser.add_argument("--out", required=True)
    
    args = parser.parse_args()
    
    return args

def prepare_participants_hpo_terms(pheno_path, alt_id_path, trio_path, output_path):
    """ loads patient HPO terms
    
    Args:
        pheno_path: path to patient pheotype file, containing one line per
            proband, with HPO codes as a field in the line.
        alt_id_path: path to set of alternate IDs for each individual
        trio_path: path to set of alternate IDs for each individual
        output_path: path to save HPO terms per proband as JSON-encoded file.
    """
    
    alt_ids = load_alt_id_map(alt_id_path)
    trio_probands = load_trio_probands(trio_path)
    
    # load the phenotype data for each participant
    handle = open(pheno_path, "r")
    
    # get the positions of the columns in the list of header labels
    header = handle.readline().strip().split("\t")
    proband_column = header.index("patient_id")
    child_hpo_column = header.index("child_hpo")
    
    hpo_by_proband = {}
    for line in handle:
        line = line.split("\t")
        proband_id = line[proband_column]
        child_terms = line[child_hpo_column]
        
        # don't use probands who lack HPO terms
        if child_terms == "NA" or child_terms == '' or child_terms == '-':
            continue
        
        # swap the proband across to the DDD ID if it exists
        if proband_id in alt_ids:
            proband_id = alt_ids[proband_id]
        
        # if we are only looking at probands in the trios, make sure that the
        # current proband is one from a trio.
        if trio_probands is not None and proband_id not in trio_probands:
            continue
        
        if "|" in child_terms:
            child_terms = child_terms.split("|")
        else:
            child_terms = [child_terms]
        
        hpo_by_proband[proband_id] = child_terms
    
    with open(output_path, "w") as output:
        json.dump(hpo_by_proband, output, indent=4, sort_keys=True)

def load_alt_id_map(alt_id_path):
    """ loads the decipher to DDD ID mapping file.
    
    Args:
        alt_id_path: path to file containing alternate IDs (ie DECIPHER IDs) for
            each proband.
    
    Returns:
        dictionary of DDD IDs, indexed by their DECIPHER ID.
    """
    
    alt_ids = {}
    
    if alt_id_path is None:
        return alt_ids
    
    with open(alt_id_path) as handle:
        header = handle.readline().strip().split('\t')
        decipher_col = header.index('decipher_id')
        ddd_col = header.index('person_stable_id')
        
        for line in handle:
            line = line.split("\t")
            ref_id = line[ddd_col]
            alt_id = line[decipher_col]
            
            alt_ids[alt_id] = ref_id
    
    return alt_ids

def load_trio_probands(trio_path):
    """ load the DDD IDs for probands in trios
    
    Args:
        trio_path: path to file listing trios, or None if no path was passed in.
        
    Returns:
        set of proband IDs, or None if we lack a trio list
    """
    
    if trio_path is None:
        return None
    
    proband_ids = set()
    with open(trio_path) as handle:
        for line in handle:
            line = line.split("\t")
            proband_ids.add(line[1])
    
    return proband_ids

def main():
    args = get_options()
    prepare_participants_hpo_terms(args.phenotypes, args.sample_ids, \
        args.trios, args.out)

if __name__ == "__main__":
    main()
