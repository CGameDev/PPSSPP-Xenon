# stb_truetype dependency

Unmodified `stb_truetype.h` v1.26, recovered from upstream `nothings/stb` commit
`6e9f34d5429cf16790ec43c9bac3f1ee4ad1f760`:

https://github.com/nothings/stb/blob/6e9f34d5429cf16790ec43c9bac3f1ee4ad1f760/stb_truetype.h

SHA-256: `ecd30b05e0dd4fea3a13c26810dd9e1992dc379049482c393d5a19e6b5090aab`.
The adjacent upstream `LICENSE` retains both offered licenses; this project uses
the MIT option. The verified owner launcher already references this API but the
legacy donor omits its header. M1 adds the missing dependency without changing
the original archive. It is copied only when preparing the compatibility build.

The header warns against untrusted fonts. Preserve the launcher's fixed,
application-owned font asset path; this checkpoint does not add a font picker or
accept arbitrary font uploads. No font binaries are distributed here.
