from Bio.UniProt import GOA

with open('./mgi.gaf') as handle:
    test = list(GOA.gafiterator(handle))
