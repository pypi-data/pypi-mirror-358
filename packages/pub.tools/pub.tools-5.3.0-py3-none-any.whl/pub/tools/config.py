import importlib.metadata

NO_VALUE = "<<blank>>"  # special marker
MAX_PUBS = 9000
# Biopython will put a count greater than 200 ids into a post, so we don't need to worry about request size
# But there does seem to be a 9999 limit either from Biopython or from NCBI

# set this to True to be emailed if we can't connect to NCBI to get journal info
# this will email to Entrez.email
JOURNAL_FAILURE_WARNING = False

VERSION = importlib.metadata.version("pub.tools")
