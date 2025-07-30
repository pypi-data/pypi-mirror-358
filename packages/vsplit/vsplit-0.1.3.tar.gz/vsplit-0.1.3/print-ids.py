#!/usr/bin/env python

from Bio import SeqIO
from vsplit import chunk_from_env

for record in SeqIO.parse(chunk_from_env(), "fasta"):
    print(record.id)
    break
