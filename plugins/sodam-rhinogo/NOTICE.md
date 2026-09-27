# Source and third-party notices

This notice accompanies SoDam AI Studio's Apache License, Version 2.0 port and preserves attribution for the MIT-licensed upstream material. It imposes no additional license restrictions. See `LICENSE` and `LICENSE-MIT` for the complete license texts.

## Project source

- SoDam AI Studio: `Copyright 2026 SoDam AI Studio` for its contributions to the Rhino 7 port and Codex plugin packaging, offered under Apache License, Version 2.0.
- Upstream project: `leoyang1984/rhino-architectural-modeling` at https://github.com/leoyang1984/rhino-architectural-modeling . Reference revision checked locally: `9faa760402a422262ae7f23cf53cd61a7334bf7f`.
- Upstream notice: `Copyright (c) 2026 Rhino Architectural Modeling contributors`. Its MIT copyright and permission notice are preserved verbatim in `LICENSE-MIT` and must accompany copies or substantial portions of that material.
- The Apache designation does not claim sole ownership of upstream code. Files alone do not establish the identity, rights, or consent of every contributor to later modifications. Verify the chain of rights before public release or customer delivery where required.

## Separately licensed software

- `rhino3dm`: `requirements.txt` requests `>=8.35,<9`; the inspected installation is `8.35.0`. Installed metadata says MIT and includes a license file. Source: https://github.com/mcneel/rhino3dm . Recheck the actual version and included notices if bundling wheels or binaries.
- Rhino 7: proprietary McNeel application, not included here. A separate Rhino license and applicable terms are required: https://www.rhino3d.com/7/eula/ . Do not package Rhino binaries or license keys.
- Codex: separate application/service. Its installation, account, and service terms are not granted by this repository's code licenses.

## Materials and outputs

Reviewed source consists of Python/PowerShell code, Markdown/HTML documentation, JSON/YAML configuration, and text templates. No bundled image, icon, font, audio, video, or third-party model asset was found in the reviewed source. This inventory does not cover future additions or ignored `work/` outputs.

Before publishing, selling, teaching with, or delivering generated models, prompts, AI-assisted code/content, screenshots, or customer materials, verify origin, rights, attribution, privacy, contract restrictions, and similarity to protected works. Do not include secrets or private customer data in public examples.

When distributing modified Apache-licensed material, retain applicable copyright, license, and NOTICE information and mark changed files as required by Apache License, Version 2.0. Preserve the original MIT notice separately. This file does not grant rights to third-party products or materials.
