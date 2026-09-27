# SoDam-RhinoGo — Rhino 7 Modeling Guide

**English guide · status as of 2026-09-27.** Korean edition: [Markdown](README.md) · [HTML](README.html). This guide contains the same information as its [HTML edition](README.en.html).

SoDam-RhinoGo is a **skill plugin installed from a local Codex marketplace**. It creates an example architectural pavilion in Rhino 7 for Windows and saves a `.3dm` model and audit reports. It has a full example built inside Rhino and a smaller offline example built without Rhino. It is neither a standalone website nor a Rhino `.rhp` plugin.

> **What has been verified:** On this computer, we verified local marketplace registration, plugin installation and enabled state, 14 tests of the installed copy, creation of 67 objects in Rhino 7, and reopening and auditing the saved file. The Codex desktop plugin picker and automatic natural-language invocation, visual quality of the Rhino viewport, the original Rhino MCP connection to Rhino 7, a Grasshopper definition, and public marketplace distribution have not been verified. The commands below cover the features currently implemented.

## Contents

1. [Basic terms](#terms)
2. [Prerequisites and downloads](#prerequisites)
3. [Obtaining and installing the project](#installation)
4. [Five-minute quick start](#quick-start)
5. [Running, using, and commands](#usage)
6. [File locations and checking results](#files)
7. [Workflow and architecture](#architecture)
8. [Security and data flow](#security)
9. [Update summary](#updates)
10. [Troubleshooting](#troubleshooting)
11. [Frequently asked questions](#faq)
12. [Copyright, licenses, and commercial use](#license)
13. [Verification scope and official sources](#evidence)

<a id="terms"></a>
## 1. Basic terms

| Term | Plain-language meaning |
| --- | --- |
| Rhino 7 | A program for creating 3D architectural or product forms and opening `.3dm` files. It requires a separate installation and license. |
| Codex | An AI tool to request work in words or run commands. You can use its desktop app or CLI (command line). |
| Local marketplace | A plugin catalog stored in this computer's project folder. It has not been published in a public online directory. |
| Skill plugin | A bundle of instructions and scripts read by Codex. It differs from a `.rhp` plugin installed into Rhino itself. |
| PowerShell | A Windows command window. Search for `PowerShell` in the Start menu to open it. |
| `.3dm` | A Rhino model file. This project writes Rhino 7 format (archive version 70). |
| `.venv` | A Python environment used only by this project; it does not change other Python installations. |
| Audit | A check of both the model being built and the **file saved to disk**. `overall_pass: true` in a report means that audit passed. |

<a id="prerequisites"></a>
## 2. Prerequisites and downloads

1. **Windows PC and Rhino 7:** The full example expects `C:\Program Files\Rhino 7\System\Rhino.exe`. Find the installer under **Legacy Downloads → Rhino 7** on [McNeel's official download page](https://www.rhino3d.com/en/download/), then activate it using your own Rhino license. If installed elsewhere, the current launcher fails before starting. You do not need the Rhino application for the small offline example.
2. **Python 3.12 (64-bit recommended):** Get a 3.12-series installer from the [official Python Windows downloads](https://www.python.org/downloads/windows/). After installation, check `py -3.12 --version` in PowerShell. This computer was tested with 3.12.9. Scripts inside Rhino use Rhino 7's IronPython; Python 3.12 is used for installation and saved-file audits.
3. **Codex desktop or CLI:** Follow the [Codex app guide](https://learn.chatgpt.com/docs/app) and [Codex CLI guide](https://learn.chatgpt.com/docs/codex/cli) to install and sign in. `codex --version` must work for the marketplace commands below. You can still run the manual PowerShell commands without Codex.
4. **This project folder:** The current implementation is at `D:\AI_Dev_Work\2026y\26y_09m_29d_SoDam-RhinoGo`. On another PC, copy the **entire modified project folder** from a safe backup. The private repository is https://github.com/sodam-ai/SoDam-RhinoGo-Codex; only authorized users can download it. There is no public download address. The [original GitHub repository](https://github.com/leoyang1984/rhino-architectural-modeling) is a Rhino 8 reference; downloading only that repository does not install this Rhino 7 plugin.
5. **Internet on first installation:** `pip` needs it to download `rhino3dm>=8.35,<9`. If it is already installed in this computer's `.venv`, you do not need to download it again. Rhino and Codex sign-in and license communication follow each product's settings and terms.

<a id="installation"></a>
## 3. Obtaining and installing the project

**Important:** `upstream-source/` is an unchanged reference clone of the original. The top-level folder is the modified Rhino 7 project. Do not merge the two or remove the top-level folder when cleaning up an old original installation. Save working files under `work/` with new names.

Open PowerShell and run the following **one line at a time**. If already installed, check `codex plugin list` first and skip duplicate installation commands.

```powershell
Set-Location 'D:\AI_Dev_Work\2026y\26y_09m_29d_SoDam-RhinoGo'
codex plugin marketplace add (Get-Location).Path
codex plugin add sodam-rhinogo@sodam-rhinogo
codex plugin list
```

Confirm that `sodam-rhinogo@sodam-rhinogo` is installed and enabled. Open a new Codex task and ask, `Use SoDam-RhinoGo to build a Rhino 7 pavilion in a new file and report the live and saved audits.` **The full one-prompt natural-language flow in the desktop UI has not yet been verified.** The reproducible method is the PowerShell sequence in the next section. Codex stores an installed plugin copy in its cache, separate from the source project folder. After editing the source, reinstall and verify a new plugin version for those edits to reach the installed copy.

For manual commands, prepare a dedicated Python environment in the project root. Skip the first line if `.venv\Scripts\python.exe` already exists.

```powershell
Set-Location 'D:\AI_Dev_Work\2026y\26y_09m_29d_SoDam-RhinoGo'
if (-not (Test-Path '.\.venv\Scripts\python.exe')) { py -3.12 -m venv .venv }
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

`No broken requirements found.` means the dependency check passed. To run the **installed plugin copy** directly, its `SKILL.md` requires a separate `.venv` under the installed skill folder. Ask Codex to check and create it on first use, or run the same setup commands in that folder. The project-root `.venv` and installed-copy `.venv` are different.

<a id="quick-start"></a>
## 4. Five-minute quick start

This is the route that **actually generates the full example inside Rhino 7**. If `work/` is missing, create it only for outputs. `Get-Date` gives each model a new name so existing models are preserved. Rhino startup and license checks may make this take longer than five minutes.

```powershell
Set-Location 'D:\AI_Dev_Work\2026y\26y_09m_29d_SoDam-RhinoGo'
if (-not (Test-Path '.\work')) { New-Item -ItemType Directory '.\work' | Out-Null }
$model = ".\work\pavilion-$(Get-Date -Format yyyyMMdd-HHmmss).3dm"
.\scripts\launch_rhino7_live.ps1 -OutputFile $model
```

On success you should see `Passed : True`, `Objects : 67`, and paths to the model and live/saved audit reports. Open `work` in File Explorer and use **File → Open** in Rhino 7 to inspect the `.3dm`. Passing an audit does not establish visual quality. Look at the viewport yourself and check dimensions, direction, and missing objects.

<a id="usage"></a>
## 5. Running, using, and commands

### Full model and audits

`launch_rhino7_live.ps1` checks inputs and file names → starts Rhino 7 → builds the full model → audits the Rhino document → saves `.3dm` → independently audits the saved file. The output parent folder must already exist. Choose a **new name** ending in `.3dm`. The default timeout is 120 seconds; use `-TimeoutSeconds 180` to set a value from 1 to 3600 seconds. An existing `.3dm` or report with the same base name causes an error instead of an overwrite.

```powershell
.\scripts\launch_rhino7_live.ps1 -OutputFile '.\work\pavilion-my-first.3dm' -TimeoutSeconds 180
```

### Parameter-only variant

In Notepad, create a **new file** such as `work\my-parameters.json` and save the text below. Keep the double quotes and commas as shown. Values you omit use the defaults. Dimensions are in mm; angles are in degrees.

```json
{
  "length": 15000,
  "frame_count": 9,
  "ridge_height": 5000,
  "louver_count_per_side": 12,
  "louver_angle_deg": 45,
  "entrance_width": 3000,
  "entrance_offset": 200
}
```

```powershell
$variant = ".\work\pavilion-variant-$(Get-Date -Format yyyyMMdd-HHmmss).3dm"
.\scripts\launch_rhino7_live.ps1 -OutputFile $variant -ParametersFile '.\work\my-parameters.json'
```

Allowed keys and defaults are in `assets/sodam_rhinogo_parameters.py`. `frame_count` must be at least 2 and `louver_count_per_side` at least 1. Numbers must be finite, the angle's absolute value at most 360 degrees, and the total at most 2,000 objects. Dimensions, entrance clearance, and frame spacing are checked too. Invalid JSON or out-of-range values stop before Rhino starts.

To compare the **live audit JSON** of a baseline and a variant, substitute the real file names. An existing comparison report is not overwritten.

```powershell
.\.venv\Scripts\python.exe .\scripts\compare_model_metrics.py '.\work\BASE.audit.json' '.\work\VARIANT.audit.json' --expect-change object_count --expect-same units --output '.\work\my-comparison.json'
```

Replace `BASE` and `VARIANT` with the actual generated names. The command prints all differences and whether expectations passed. `--tolerance` accepts only finite numbers at least zero.

### Small model without Rhino

This route uses `rhino3dm` to create a simpler **41-object** example. It is different from the full 67-object Rhino route. Give it a new output folder.

```powershell
$offline = ".\work\offline-$(Get-Date -Format yyyyMMdd-HHmmss)"
.\scripts\first_run.ps1 -OutputDir $offline
```

### Test commands

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m pip check
```

There is no separate `package.json`, web build, or database migration in this project's runtime path.

### Environment variables, build, and private repository use

Ordinary users do not need a `.env` file or API key. The launcher temporarily sets `RHINO7_OUTPUT_3DM` (new model path) and `RHINO7_PARAMS_JSON` (validated input JSON path), then restores their prior values. `RHINO7_IDEMPOTENCE_REPORT` is a developer path for the repeat-build test report. Do not put secrets or customer material in environment variables, JSON, or `work/` outputs.

There is no separate compile, web build, or database migration step. Installing the Python environment and running the tests above prepares the runtime. **Storing code in a private GitHub repository is not publishing a public plugin.** On another PC, a person with access may obtain the private repository, install Rhino 7, Python, and Codex separately, then repeat the local marketplace registration and `.venv` installation here. Git excludes `.venv/`, `work/`, models, and reports; back those up separately. No Release or public distribution package exists yet.

<a id="files"></a>
## 6. File locations and checking results

| Location (relative to project root) | Purpose |
| --- | --- |
| `README.md`, `README.html`, `README.en.md`, `README.en.html` | Korean and English Markdown/HTML editions of this guide. |
| `.agents/plugins/marketplace.json` | Local marketplace catalog. |
| `plugins/sodam-rhinogo/.codex-plugin/plugin.json` | Codex plugin name, version, and display metadata. |
| `plugins/sodam-rhinogo/skills/sodam-rhinogo/` | Skill instructions, scripts, and tests included in the installed copy. |
| `RHINO7_README.md`, `SKILL.md` | Developer-oriented Rhino 7 detail and skill operating instructions. |
| `assets/parametric-pavilion-rhino7.py`, `assets/sodam_rhinogo_parameters.py` | Full-model construction, defaults, and input checks. |
| `scripts/launch_rhino7_live.ps1`, `scripts/run_full_rhino7.py` | Full Rhino 7 execution route. |
| `scripts/audit_architectural_model_rhino7.py`, `scripts/audit_saved_rhino7.py` | Separate checks of the open document and saved file. |
| `scripts/first_run.ps1`, `scripts/generate_rhino7_model.py`, `scripts/inspect_rhino7_model.py` | Small offline model generation and inspection. |
| `scripts/compare_model_metrics.py`, `tests/` | Variant comparison and automated tests. |
| `requirements.txt`, `.venv/` | Python dependency and project environment; `.venv/` is Git-ignored. |
| `work/` | Models and JSON reports; Git-ignored, so back them up separately. |
| `upstream-source/` | Unchanged original GitHub reference. **It is not the modified project or its runtime root.** |
| `LICENSE`, `LICENSE-MIT`, `NOTICE.md` and plugin copies | Apache 2.0 port, upstream MIT, and provenance notices. |

A full run creates four files with the same base name: `.3dm`, `.build.json`, `.audit.json`, and `.saved-audit.json`. `.audit.json` checks the open document; `.saved-audit.json` checks the file on disk. Look for `overall_pass: true` in both reports. JSON opens in Notepad; `.3dm` opens in Rhino 7. Keep a model and its reports together because matching names alone cannot prove matching contents.

<a id="architecture"></a>
## 7. Workflow and architecture

```text
User request / PowerShell command
        ↓
Codex local marketplace → SoDam-RhinoGo skill
        ↓
Parameter and output-path preflight checks
        ↓
Rhino 7 + RhinoCommon model generation (or offline rhino3dm generation)
        ↓
Independent live audit → new .3dm save → independent saved-file audit
        ↓
work/ model + JSON reports → human visual check in Rhino
```

The default full model is a pavilion measured in mm. Frames, columns, beams, rafters, louvers, and reference objects have names and layers. The Rhino route uses RhinoCommon/IronPython; the offline route uses Python 3.12/rhino3dm. **No Grasshopper `.gh` definition is included**, and the original Rhino MCP transport has not been verified with this Rhino 7 route. Use only one writer for a Rhino document at a time. The repeated-build check tests whether identical settings keep object counts and names stable.

<a id="security"></a>
## 8. Security and data flow

- Models, parameters, and JSON reports are stored at the selected local paths. The project itself has no sign-in page, web server, database, API-key input, or built-in cloud upload code.
- Codex prompts and file access, Rhino license checks, and Python package downloads follow **the settings and terms of Codex, McNeel, and the package provider** respectively. Do not assume the whole process is always offline.
- The plugin can request local file reads and model writes. Before installation, check that `source.path` in `.agents/plugins/marketplace.json` is `./plugins/sodam-rhinogo`; run it only from a project you trust.
- Do not put passwords, tokens, or private keys in model names, parameter JSON, Codex prompts, reports, or README files. `.env` and `work/` are Git-ignored, but check actual files and Git changes again before sharing.
- Files are not automatically encrypted. Back up important models to a separate location. The launcher refuses to overwrite existing models and reports, but that does not replace a backup.
- A previous check scanned 65 source files and 103 work reports for representative secret patterns and found no matches. This is not proof that every possible secret is absent.

<a id="updates"></a>
## 9. Update summary

<details><summary>Expand the Rhino 7 rebuild changes</summary><ul><li>Preserved the Rhino 8-oriented original under a separate <code>upstream-source/</code> reference and built the Rhino 7 version at the project root.</li><li>Configured a local Codex marketplace and the <code>sodam-rhinogo@sodam-rhinogo</code> skill plugin.</li><li>Added the full 67-object Rhino 7 example, a 41-object offline example, and independent live-document and saved-file audits.</li><li>Added parameter and object-count limits, overwrite prevention, variant comparison, repeat-build checks, and 14 unit tests.</li><li>The currently installed version reads <code>0.1.0+codex.20260927110134</code>. Recheck the installed version and test results after updating source code.</li></ul></details>

<a id="troubleshooting"></a>
## 10. Troubleshooting

| Symptom | Check and remedy |
| --- | --- |
| `codex` command not found | Complete Codex CLI setup and sign-in using the official guide, then open a new PowerShell. Manual model generation works without Codex. |
| Plugin not listed | Confirm the marketplace registration from the project root, then run `codex plugin marketplace list` and `codex plugin list`. Reopen the desktop app and check in a new task. |
| Installed plugin does not contain your newest edits | The installed copy has a separate cache. Source edits alone are not proof of an update. Check the version and copy, then follow the plugin update process. |
| `py -3.12` not found | Install Python 3.12 and verify its version in a new PowerShell. Do not change an unrelated Python environment. |
| `Rhino 7 is not installed` | Check the exact `Rhino.exe` path above and your Rhino 7 installation/license. The full launcher does not target a PC with Rhino 8 alone. |
| `Output parent directory must already exist` | Create an output directory such as `work/` first. Do not relocate the implementation to a different folder. |
| `Preserving existing model/report` | This is expected overwrite protection. Keep the existing file and choose a new output name. |
| `parameter validation failed` | Check JSON syntax, key names, numeric limits, entrance width, column spacing, and total object count. Refer to defaults in `assets/sodam_rhinogo_parameters.py`. |
| Rhino exits or times out | Open Rhino 7 yourself to check license or error dialogs. Retry with a new output name and, if needed, `-TimeoutSeconds 180`. Preserve partial files and retry under a new name. |
| `.audit.json` passes but `.saved-audit.json` fails | The saved-file audit failed. Do not treat the model as final; inspect failed checks and regenerate under a new name. |
| Model looks wrong on screen | Passing an audit does not guarantee visual quality. Inspect perspective, plan, and elevations in Rhino and check dimensions and layers. |

<a id="faq"></a>
## 11. Frequently asked questions

**Q. Do I need Rhino 8?**

A. The current full route uses installed **Rhino 7**. Even though the `rhino3dm` package is version 8.x, we wrote and re-audited `.3dm` files in Rhino 7 archive format.

**Q. Must I install Grasshopper?**

A. Current scripts contain no Grasshopper `.gh` definition or execution step. It is not required for the verified route.

**Q. Does installing the Codex plugin add a button inside Rhino?**

A. No. This is a Codex skill plugin, not a Rhino `.rhp` plugin. A Codex request or PowerShell script starts Rhino.

**Q. Can I run it on a phone?**

A. The current full launcher uses Rhino 7 on Windows. There is no direct mobile execution feature. You can read the HTML guide in a mobile browser.

**Q. Can everything run without internet?**

A. Offline generation may work with dependencies already installed, but first package installation and Codex/Rhino sign-in or license traffic are separate. Fully offline operation has not been verified.

**Q. Does updating the original GitHub repository update this port?**

A. No. The original under `upstream-source/` is only a reference. The port and installed cache are managed separately.

**Q. Is a passing report enough to build the pavilion?**

A. No. The audit checks conceptual model objects, geometry, and saving. Structural safety, codes, buildability, and fabrication require separate review by qualified professionals.

<a id="license"></a>
## 12. Copyright, licenses, and commercial use

1. **Licenses and copyright:** SoDam AI Studio's contributions to this Rhino 7 port and SoDam-RhinoGo plugin are offered under the **Apache License, Version 2.0 (SPDX: Apache-2.0)**. The root and plugin `LICENSE` files contain the [official Apache 2.0 text](https://www.apache.org/licenses/LICENSE-2.0.html) and `Copyright 2026 SoDam AI Studio`. Material derived from `leoyang1984/rhino-architectural-modeling` retains `Copyright (c) 2026 Rhino Architectural Modeling contributors` and the **MIT License** in the separate [`LICENSE-MIT`](LICENSE-MIT). Applying Apache to the port does not replace the upstream MIT rights or establish ownership of every contribution.
2. **Use, modification, sale, and delivery:** Subject to the applicable conditions of both licenses, you may use, modify, copy, fork, redistribute, and use the code in commercial services, teaching, company work, and customer deliveries. When distributing copies, include the Apache 2.0 text, upstream MIT copyright and permission notice, and applicable `NOTICE.md` notices; mark modifications. Apache 2.0 also has copyright and patent conditions, so read its full text. This guidance does not grant rights to Rhino, customer materials, or generated outputs.
3. **Do not:** Do not remove the upstream MIT notice or applicable Apache/NOTICE notices. Do not claim this repository's licenses permit redistribution of Rhino executables, license keys, McNeel documentation, third-party marks or images, or customer materials. SoDam-RhinoGo is not an official McNeel product or endorsement. Do not put private data, personal information, or API keys in public examples.
4. **Separate software and dependencies:** Installing and using Rhino 7, concurrent sessions, and license type follow the [Rhino 7 EULA](https://www.rhino3d.com/7/eula/) and your own agreement. This project uses public APIs and grants no right to decompile proprietary Rhino binaries. The only direct `requirements.txt` dependency is `rhino3dm>=8.35,<9`; installed `8.35.0` metadata and included license on this PC say MIT. Recheck notices for the exact version if bundling package binaries. Codex accounts, external APIs/SDKs, service plans, and terms are separate.
5. **New materials and AI outputs:** No bundled image, icon, font, video, audio, or third-party 3D model was found in the reviewed source. For any later model, texture, template, prompt, screenshot, or AI-generated code/document/image/model, check origin, copyright, commercial permission, attribution, and possible similarity to protected works before final use. Generated `work/` files and customer inputs were outside this source review.
6. **Before publication or delivery:** The upstream MIT notice and user-specified Apache 2.0 designation were verified in files, but those files alone cannot establish rights of every contributor to the Rhino 7 code or rights under customer contracts, input assets, and generated outputs. This GitHub upload targets a **private repository**. Before public release, sale, or customer delivery, verify the chain of rights and Rhino license type and resolve matters needing **legal or specialist review**. A passing model audit is not a building permit, structural safety finding, or construction approval.
7. **Warranty and liability:** The disclaimers and liability limits in Apache 2.0 and upstream MIT each apply to their respective material. **This is general reference information, not a legally binding conclusion; you are responsible for use and should consult a lawyer.**

<a id="evidence"></a>
## 13. Verification scope and official sources

- Verified on this computer: local plugin installation and enabled state, 14 tests in the installed copy, Python dependency check, 67-object full Rhino 7 build and saved-file audit, 41-object offline build written in Rhino 7 format, and rejection of an existing output path.
- Not yet verified: Codex desktop picker and full natural-language invocation, visual Rhino viewport result, original Rhino MCP connection to Rhino 7, Grasshopper, public release, or installation on another PC. Distinguish an installed state from actual execution.
- Official references: [Codex plugin packaging](https://developers.openai.com/plugins/build/plugins), [Rhino downloads](https://www.rhino3d.com/en/download/), [Rhino 7 EULA](https://www.rhino3d.com/7/eula/), [Python Windows downloads](https://www.python.org/downloads/windows/), and the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0.html), and the [upstream MIT license](https://spdx.org/licenses/MIT.html). This guide describes files and verification as of 2026-09-27. Recheck official installation and legal terms when installing or distributing because they can change.
