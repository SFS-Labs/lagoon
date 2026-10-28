# Verification hold — PR #1 original report

The July/August 2026 static reports are historical research artifacts.
They have **not** been independently clinically validated and must not be
used as an authoritative genetic genotype/phenotype map.

Specific confirmed correction examples:

- **SLCO1B1 rs4149056**: the reduced-function allele is **C**, not T.
  A reported CT is consistent with one copy of C *if* correctly harmonised.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC3384438/
- **DPYD rs67376798** denotes c.2846A>T, **not HapB3**.
  HapB3: rs75017182 (functional) or rs56038477 (tag SNP).
  https://pmc.ncbi.nlm.nih.gov/articles/PMC11280107/
- Avoid claims that a negative common-risk SNP establishes 'no genetic risk',
  that several correlated loci are statistically independent, or that common
  MTHFR variants diagnose micronutrient malabsorption.
- The source GRCh37 coordinate and strand conventions need independent
  per-variant verification. For example, rs2282679 is reported as A/C in a
  recent study; a consumer G/T call can indicate reversed representation
  rather than proof of a particular effect allele.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC13414278/

**Next gate:** Reconcile original genotype calls with primary raw DNA,
build-specific variant identity, validation source and evidence-strength.
If data are absent, report `UNKNOWN`, not 'normal'.
