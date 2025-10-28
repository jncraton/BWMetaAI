# Build Verification

This document explains how to verify that the Python 3 build produces identical output to the Python 2 build.

## Verification Steps

To verify that builds are reproducible and produce identical output:

1. Build the project:
   ```bash
   make clean
   make
   ```

2. Generate checksums of the output files:
   ```bash
   sha256sum build/aiscript.bin build/patch_rt.mpq
   ```

3. Compare the checksums with the reference values below.

## Reference Checksums (Python 3 Build)

These checksums were generated from a clean build using Python 3.12.3 on Ubuntu 24.04:

```
cf162d5eaf73b1f333ddf7317a44296c05658aa5ee0a6a3196238785bd054fb1  build/aiscript.bin
4524930427332fe3dad1c2ad893cd446b824928d08add671cdedcbd60e849604  build/patch_rt.mpq
```

### File Sizes

- `aiscript.bin`: 38,398 bytes (truncated to 64,050 bytes in the final MPQ)
- `patch_rt.mpq`: ~999 KB

## Notes

- The build is deterministic for a given set of source files and build environment
- Minor variations in checksums may occur due to differences in:
  - Node.js version (JavaScript build step)
  - System architecture or libraries
  - Timestamp-related data in MPQ files

If you observe significant differences in file sizes or the build fails, please open an issue with details about your build environment.
