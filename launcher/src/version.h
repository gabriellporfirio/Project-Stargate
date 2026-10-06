#ifndef PMC_VERSION_H
#define PMC_VERSION_H

/* Versions are MAJOR.MINOR (1.0, 1.1, 2.0); PATCH is only for a hotfix.
   Keep in step with assemblyIdentity in launcher.manifest and
   CHECKER_VERSION in app/helpers/analyzer.py (tests/test_version.py). */
#define PMC_VERSION_MAJOR 1
#define PMC_VERSION_MINOR 0
#define PMC_VERSION_PATCH 0
#define PMC_VERSION_STRING "1.0"

#endif
