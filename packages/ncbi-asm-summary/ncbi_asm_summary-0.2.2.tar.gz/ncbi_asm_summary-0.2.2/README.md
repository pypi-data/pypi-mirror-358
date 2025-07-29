# Installation

```sh
git clone https://github.com/evoquant/ncbi_asm_summary.git
cd ncbi_asm_summary
pip install .
```


# Usage


## Stream from remote NCBI server, in terminal
Stream the GenGank assembly summary file from NCBI, can limit the columns the number of rows.

```python
gbsummary \
        --db genbank \
        --nrows 2 \
        --columns assembly_accession bioproject biosample
```

```
2025-06-25 09:53:05,522 - INFO - First 2 rows, assembly and FTP columns, from genbank...
2025-06-25 09:53:05,522 - INFO - Streaming download from https://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/assembly_summary_genbank.txt
GCA_000001215.4 PRJNA13812      SAMN02803731
GCA_000001405.29        PRJNA31257      na
```

Stream the RefSeq assembly summary file from NCBI, can limit the columns the number of rows.

```python
gbsummary \
        --db refseq \
        --nrows 2 \
        --columns assembly_accession bioproject biosample
```

```
2025-06-25 09:54:47,206 - INFO - First 2 rows, assembly and FTP columns, from refseq...
2025-06-25 09:54:47,206 - INFO - Streaming download from https://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/assembly_summary_refseq.txt
GCF_000001215.4 PRJNA164        SAMN02803731
GCF_000001405.40        PRJNA168        na
```
These can be used in a pipeline, for example to download certain columns and save them to a file. Leave out the `--nrows` option to download the full file. Include the `--header` option to include the header row (column names) in the output.

```bash
gbsummary \
        --db genbank \
        --columns assembly_accession bioproject biosample \
        > genbank_summary.txt
```

## Use as a Python library

### Stream from remote NCBI server

```python
from ncbi_asm_summary.reader import AssemblySummaryStream

f = AssemblySummaryStream(db="refseq")

# Only print the first result for the example
for i in f.stream():
    print(i)
    break 
```

```python
AssemblySummary(assembly_accession='GCF_000001215.4', bioproject='PRJNA164', biosample='SAMN02803731', wgs_master='na', refseq_category='reference genome', taxid='7227', species_taxid='7227', organism_name='Drosophila melanogaster', infraspecific_name='na', isolate='na', version_status='latest', assembly_level='Chromosome', release_type='Major', genome_rep='Full', seq_rel_date='2014-08-01', asm_name='Release 6 plus ISO1 MT', asm_submitter='The FlyBase Consortium/Berkeley Drosophila Genome Project/Celera Genomics', gbrs_paired_asm='GCA_000001215.4', paired_asm_comp='identical', ftp_path='https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/215/GCF_000001215.4_Release_6_plus_ISO1_MT', excluded_from_refseq='na', relation_to_type_material='na', asm_not_live_date='na', assembly_type='haploid', group='invertebrate', genome_size='143706478', genome_size_ungapped='142553500', gc_percent='42.000000', replicon_count='7', scaffold_count='1869', contig_count='1869', annotation_provider='FlyBase', annotation_name='FlyBase Release 6.54', annotation_date='2023-12-26', total_gene_count='17872', protein_coding_gene_count='13962', non_coding_gene_count='3543', pubmed_id='10731132;12537568;12537572;12537573;12537574;16110336;17569856;17569867;25589440;26109356;26109357')
```


### Stream from local copy

```python
from ncbi_asm_summary.reader import AssemblySummaryStream

path = "/home/chase/Downloads/assembly_summary_genbank_20250619_1057.txt.gz"

f = AssemblySummaryStream(file_path=path)

# Only print the first result for the example
for i in f.stream():
    print(i)
    break  
```

```python
AssemblySummary(assembly_accession='GCA_000001215.4', bioproject='PRJNA13812', biosample='SAMN02803731', wgs_master='na', refseq_category='reference genome', taxid='7227', species_taxid='7227', organism_name='Drosophila melanogaster', infraspecific_name='na', isolate='na', version_status='latest', assembly_level='Chromosome', release_type='Major', genome_rep='Full', seq_rel_date='2014-08-01', asm_name='Release 6 plus ISO1 MT', asm_submitter='The FlyBase Consortium/Berkeley Drosophila Genome Project/Celera Genomics', gbrs_paired_asm='GCF_000001215.4', paired_asm_comp='identical', ftp_path='https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/001/215/GCA_000001215.4_Release_6_plus_ISO1_MT', excluded_from_refseq='na', relation_to_type_material='na', asm_not_live_date='na', assembly_type='haploid', group='invertebrate', genome_size='143706478', genome_size_ungapped='142553500', gc_percent='42.000000', replicon_count='7', scaffold_count='1869', contig_count='1869', annotation_provider='FlyBase', annotation_name='FlyBase Release 6.54', annotation_date='2023-12-13', total_gene_count='17872', protein_coding_gene_count='13962', non_coding_gene_count='3543', pubmed_id='10731132;12537568;12537572;12537573;12537574;16110336;17569856;17569867;25589440;26109356;26109357')
```

# Table Columns

assembly_accession  
bioproject  
biosample  
wgs_master  
refseq_category  
taxid  
species_taxid  
organism_name  
infraspecific_name  
isolate  
version_status  
assembly_level  
release_type  
genome_rep  
seq_rel_date  
asm_name  
asm_submitter  
gbrs_paired_asm  
paired_asm_comp  
ftp_path  
excluded_from_refseq  
relation_to_type_material  
asm_not_live_date  
assembly_type  
group  
genome_size  
genome_size_ungapped  
gc_percent  
replicon_count  
scaffold_count  
contig_count  
annotation_provider  
annotation_name  
annotation_date  
total_gene_count  
protein_coding_gene_count  
non_coding_gene_count  
pubmed_id  
