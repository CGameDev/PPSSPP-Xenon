# Source provenance and attribution

PPSSPP Xenon is a community Xbox 360 port/modernization project derived from
PPSSPP. It is not an official PPSSPP or Microsoft product.

M1 vendors unmodified stb_truetype v1.26 with upstream license (MIT option),
restores the original owner's archive and adds GPL-2.0-or-later staging/build
tools and compatibility glue. Donor/FFmpeg source is assembled in ignored local
staging with its original notices. No SDK material or generated binary is
committed. The M0-specific provenance below remains historical.

- Legacy implementation reference: `metalex10/PPSSPP-X360`, commit
  `540db97d96136b2139e5f12dd3c0bb18f2e1cd1f`. M0 copies only its unmodified
  GPLv2 license text as `LICENSE`; no emulator implementation is imported yet.
- Modern PPSSPP reference: `hrydgard/ppsspp`, fixed tag `v1.20.4`. No backport.
- Owner-provided Xbox archive: existing Base64 preservation remains untouched.
  Integrity failure prevents its use. Existing source ownership/notices remain
  in force; M0 does not relicense those archived files.
- New Python tooling/tests in M0: GPL-2.0-or-later, indicated in the source.
- New UI study: original markup/styles and fictional geometric artwork. No
  commercial title art, CCLOS private assets, SDK material or font binaries are
  included. System fonts are referenced by name only.

On eventual full import retain donor `LICENSE`, `LICENSE.TXT`, file notices and
all dependency license files. Record corresponding-source and dependency license
obligations before distributing a binary; this checkpoint distributes none.
