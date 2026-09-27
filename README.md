# SoDam-RhinoGo — Rhino 7 모델링 안내서

**한국어 기본 안내서 · 2026-09-27 기준.** 영어판: [Markdown](README.en.md) · [HTML](README.en.html). 이 안내서는 [HTML판](README.html)과 같은 내용을 담습니다.

SoDam-RhinoGo는 **Codex의 로컬 마켓플레이스에서 설치하는 스킬 플러그인**입니다. Windows용 Rhino 7에서 예제 건축 파빌리온을 만들고, `.3dm` 파일과 검사 보고서를 저장합니다. Rhino 안에서 만드는 전체 예제와 Rhino 없이 만드는 작은 오프라인 예제가 있습니다. 독립 실행형 웹사이트나 Rhino 내부의 `.rhp` 플러그인은 아닙니다.

> **현재 확인 상태:** 이 컴퓨터에서 로컬 마켓플레이스 등록, 플러그인 설치·활성화, 설치된 복사본의 테스트 14개, Rhino 7 전체 예제 67개 객체 생성, 저장 파일 재검사를 확인했습니다. Codex 데스크톱의 플러그인 선택 화면·자동 자연어 호출, Rhino 화면의 시각적 품질, 원본 Rhino MCP의 Rhino 7 연결, Grasshopper 정의 파일, 공개 마켓플레이스 배포는 확인되지 않았습니다. 아래 명령은 현재 구현된 기능에 한정합니다.

## 목차

1. [처음 보는 용어](#terms)
2. [사전 준비물과 다운로드](#prerequisites)
3. [프로젝트 받기와 설치](#installation)
4. [5분 빠른 시작](#quick-start)
5. [실행·사용·명령어](#usage)
6. [파일 위치와 결과 확인](#files)
7. [워크플로우·아키텍처](#architecture)
8. [보안과 데이터 흐름](#security)
9. [업데이트 내용](#updates)
10. [문제 해결](#troubleshooting)
11. [자주 묻는 질문](#faq)
12. [저작권·라이선스·상업적 이용](#license)
13. [검증 범위와 공식 자료](#evidence)

<a id="terms"></a>
## 1. 처음 보는 용어

| 용어 | 쉬운 뜻 |
| --- | --- |
| Rhino 7 | 건축·제품 등의 3D 형태를 만들고 `.3dm` 파일을 여는 프로그램. 별도 설치·사용권이 필요합니다. |
| Codex | 말로 작업을 요청하거나 명령을 실행하는 AI 도구. 데스크톱 앱 또는 CLI(명령줄)를 사용합니다. |
| 로컬 마켓플레이스 | 이 컴퓨터의 프로젝트 폴더에 있는 플러그인 목록. 공개 인터넷 상점에 게시된 상태가 아닙니다. |
| 스킬 플러그인 | Codex가 읽는 작업 지침과 실행 스크립트 묶음. Rhino 자체에 설치하는 `.rhp` 파일과 다릅니다. |
| PowerShell | Windows에서 명령을 입력하는 창. 시작 메뉴에서 `PowerShell`을 검색해 엽니다. |
| `.3dm` | Rhino 모델 파일. 이 프로젝트는 Rhino 7 형식(archive version 70)으로 저장합니다. |
| `.venv` | 프로젝트만 사용하는 Python 환경. 다른 Python 설치를 바꾸지 않습니다. |
| 감사(audit) | 만든 모델과 **저장된 파일**을 각각 검사하는 과정. 보고서의 `overall_pass: true`가 검사 통과를 뜻합니다. |

<a id="prerequisites"></a>
## 2. 사전 준비물과 다운로드

1. **Windows PC와 Rhino 7:** 전체 예제는 `C:\Program Files\Rhino 7\System\Rhino.exe`를 찾습니다. [McNeel 공식 다운로드](https://www.rhino3d.com/en/download/)의 **Legacy Downloads → Rhino 7**에서 설치 파일을 찾고, 본인의 Rhino 사용권으로 활성화하세요. 이 경로가 다르면 현재 실행 스크립트는 시작 전에 오류를 냅니다. 작은 오프라인 예제만 실행할 때는 Rhino 프로그램이 없어도 됩니다.
2. **Python 3.12(64비트 권장):** [Python 공식 Windows 다운로드](https://www.python.org/downloads/windows/)에서 3.12 계열 설치 프로그램을 받으세요. 설치 후 PowerShell에서 `py -3.12 --version`을 입력해 확인합니다. 이 컴퓨터에서는 3.12.9로 테스트했습니다. Rhino 내부 스크립트는 Rhino 7의 IronPython으로 실행되며, 이 Python 3.12는 설치·저장 파일 검사에 사용합니다.
3. **Codex 데스크톱 또는 CLI:** [Codex 앱 안내](https://learn.chatgpt.com/docs/app)와 [Codex CLI 안내](https://learn.chatgpt.com/docs/codex/cli)를 따라 설치·로그인하세요. `codex --version`이 작동해야 아래 마켓플레이스 명령을 쓸 수 있습니다. Codex 없이도 아래 수동 PowerShell 실행은 가능합니다.
4. **이 프로젝트 폴더:** 현재 구현본의 위치는 `D:\AI_Dev_Work\2026y\26y_09m_29d_SoDam-RhinoGo`입니다. 새 PC에는 이 **수정본 폴더 전체**를 안전한 백업에서 복사해야 합니다. 비공개 저장소 주소는 https://github.com/sodam-ai/SoDam-RhinoGo-Codex 이며 접근 권한이 있는 사람만 받을 수 있습니다. 공개 다운로드 주소는 없습니다. 원본 [GitHub 저장소](https://github.com/leoyang1984/rhino-architectural-modeling)는 Rhino 8 참고본이므로 이것만 내려받아서는 현재 Rhino 7 플러그인이 설치되지 않습니다.
5. **첫 설치 시 인터넷:** `pip`가 `rhino3dm>=8.35,<9`를 다운로드할 때 필요합니다. 이미 이 컴퓨터의 `.venv`에 설치되어 있으면 다시 내려받지 않아도 됩니다. Rhino 및 Codex의 로그인·사용권 통신은 각 제품의 설정과 약관을 따릅니다.

<a id="installation"></a>
## 3. 프로젝트 받기와 설치

**중요:** `upstream-source/`는 변경하지 않은 원본 참고용 복제본이고, 최상위 폴더가 Rhino 7 수정본입니다. 둘을 합치거나 원본 정리 명령으로 최상위 폴더를 지우지 마세요. 작업 파일은 `work/`에 새 이름으로 저장합니다.

PowerShell을 열고 다음을 **한 줄씩** 실행합니다. 이미 설치했다면 `codex plugin list`로 먼저 확인하고 중복 설치 명령은 건너뛰세요.

```powershell
Set-Location 'D:\AI_Dev_Work\2026y\26y_09m_29d_SoDam-RhinoGo'
codex plugin marketplace add (Get-Location).Path
codex plugin add sodam-rhinogo@sodam-rhinogo
codex plugin list
```

목록에서 `sodam-rhinogo@sodam-rhinogo`가 설치·활성화됐는지 확인합니다. 새 Codex 작업을 열어 `SoDam-RhinoGo 스킬로 Rhino 7 파빌리온을 새 파일에 만들고 live/saved 검사 결과를 알려줘`라고 요청할 수 있습니다. **자연어 한 번으로 전체 흐름이 데스크톱 화면에서 작동하는지는 아직 검증되지 않았습니다.** 확실히 재현 가능한 방법은 다음 절의 PowerShell 명령입니다. 플러그인의 설치 복사본은 Codex 캐시에 있으며 원본 소스 폴더와 별개입니다. 소스를 고친 뒤에는 플러그인을 새 버전으로 다시 설치·검증해야 수정 내용이 설치본에 반영됩니다.

수동 명령을 쓰려면 프로젝트 루트에 전용 Python 환경을 준비합니다. 이미 `.venv\Scripts\python.exe`가 있다면 첫 줄을 건너뛰세요.

```powershell
Set-Location 'D:\AI_Dev_Work\2026y\26y_09m_29d_SoDam-RhinoGo'
if (-not (Test-Path '.\.venv\Scripts\python.exe')) { py -3.12 -m venv .venv }
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

`No broken requirements found.`가 표시되면 의존성 검사에 통과한 것입니다. 설치된 **플러그인 복사본**으로 직접 실행할 때는 그 복사본의 `SKILL.md`가 지시하는 별도 `.venv`가 필요합니다. Codex에게 첫 사용 시 확인·설치하도록 요청하거나 설치본의 스킬 폴더에서 같은 명령을 실행하세요. 프로젝트 루트 `.venv`와 설치본 `.venv`는 서로 다릅니다.

<a id="quick-start"></a>
## 4. 5분 빠른 시작

아래는 **Rhino 7에서 전체 예제를 실제 생성**하는 경로입니다. `work/`가 없다면 결과물용으로만 만듭니다. `Get-Date`가 매번 새 이름을 만들어 기존 모델을 보존합니다. Rhino 실행·사용권 확인에 따라 5분 이상 걸릴 수 있습니다.

```powershell
Set-Location 'D:\AI_Dev_Work\2026y\26y_09m_29d_SoDam-RhinoGo'
if (-not (Test-Path '.\work')) { New-Item -ItemType Directory '.\work' | Out-Null }
$model = ".\work\pavilion-$(Get-Date -Format yyyyMMdd-HHmmss).3dm"
.\scripts\launch_rhino7_live.ps1 -OutputFile $model
```

성공하면 `Passed : True`, `Objects : 67`, 모델 경로, live/saved 검사 보고서 경로가 나옵니다. 파일 탐색기에서 `work`를 열고 해당 `.3dm`을 Rhino 7의 **파일 → 열기**로 확인하세요. 보고서 통과와 화면의 미관은 별개입니다. 실제 화면을 직접 보고 치수·방향·누락된 객체가 없는지 확인합니다.

<a id="usage"></a>
## 5. 실행·사용·명령어

### 전체 모델과 검사

`launch_rhino7_live.ps1`은 입력·파일명 검사 → Rhino 7 실행 → 전체 모델 생성 → Rhino 문서 검사 → `.3dm` 저장 → 저장 파일 재검사 순서로 동작합니다. 출력 폴더가 먼저 있어야 하며 `.3dm`으로 끝나는 **새 파일명**을 쓰세요. 기본 대기 시간은 120초이고 `-TimeoutSeconds 180`처럼 1~3600초로 조정할 수 있습니다. 기존 `.3dm`이나 같은 이름의 보고서가 있으면 덮어쓰지 않고 중단합니다.

```powershell
.\scripts\launch_rhino7_live.ps1 -OutputFile '.\work\pavilion-my-first.3dm' -TimeoutSeconds 180
```

### 치수·개수만 바꾼 변형 모델

메모장으로 `work\my-parameters.json` 같은 **새 파일**을 만들고 아래 내용을 저장합니다. JSON은 큰따옴표와 쉼표를 그대로 사용합니다. 기입하지 않은 값은 기본값을 사용합니다. 단위는 mm, 각도는 도입니다.

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

허용 키와 기본값은 `assets/sodam_rhinogo_parameters.py`에 있습니다. `frame_count`는 2 이상, `louver_count_per_side`는 1 이상입니다. 숫자는 유한해야 하고, 각도 절댓값은 360도 이하이며, 총 객체 수는 2000개 이하입니다. 치수·입구 여유·프레임 간격도 검사합니다. 잘못된 JSON이나 허용되지 않는 수치는 Rhino를 실행하기 전에 오류로 중단됩니다.

기준 모델과 변형 모델의 **live audit JSON**을 비교할 때는 실제 파일명을 넣습니다. 같은 이름의 비교 보고서를 덮어쓰지 않습니다.

```powershell
.\.venv\Scripts\python.exe .\scripts\compare_model_metrics.py '.\work\BASE.audit.json' '.\work\VARIANT.audit.json' --expect-change object_count --expect-same units --output '.\work\my-comparison.json'
```

`BASE`와 `VARIANT`는 실제 생성된 이름으로 바꾸세요. 파일 전체 차이와 기대값의 통과 여부가 출력됩니다. `--tolerance`는 0 이상의 유한한 숫자만 받습니다.

### Rhino 없이 작은 모델 만들기

이 경로는 `rhino3dm`으로 **41개 객체**의 간단한 예제를 만듭니다. 전체 67개 객체 Rhino 실행 경로와 다른 모델입니다. 새 출력 폴더를 지정해야 합니다.

```powershell
$offline = ".\work\offline-$(Get-Date -Format yyyyMMdd-HHmmss)"
.\scripts\first_run.ps1 -OutputDir $offline
```

### 테스트 명령

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m pip check
```

별도 `package.json`·웹 빌드·DB 마이그레이션은 이 프로젝트의 실행 경로에 없습니다.

### 환경 변수·빌드·비공개 저장소 이용

일반 사용자는 `.env`나 API 키를 만들 필요가 없습니다. 실행기는 내부적으로 `RHINO7_OUTPUT_3DM`(새 모델 경로)과 `RHINO7_PARAMS_JSON`(검증된 입력 JSON 경로)을 실행 중에만 설정하고 이전 값을 복원합니다. `RHINO7_IDEMPOTENCE_REPORT`는 개발자의 반복 실행 검사 보고서 경로입니다. 비밀키나 고객 자료를 환경 변수·JSON·`work/` 결과물에 넣지 마세요.

이 프로젝트에는 별도의 컴파일·웹 빌드·DB 이전 단계가 없습니다. 위의 Python 환경 설치와 테스트가 실행 전 준비입니다. **비공개 GitHub에 코드를 보관하는 일은 공개 플러그인 배포가 아닙니다.** 다른 PC에서는 저장소 접근 권한을 가진 사람이 비공개 저장소를 받은 뒤 Rhino 7·Python·Codex를 따로 설치하고, 이 안내의 마켓플레이스 등록과 `.venv` 설치를 다시 실행합니다. `.venv/`, `work/`, 모델·보고서는 Git에서 제외되므로 별도 백업이 필요합니다. Release와 공개 배포 패키지는 아직 없습니다.

<a id="files"></a>
## 6. 파일 위치와 결과 확인

| 위치(프로젝트 최상위 폴더 기준) | 하는 일 |
| --- | --- |
| `README.md`, `README.html`, `README.en.md`, `README.en.html` | 이 안내서의 한국어·영어 Markdown/HTML판. |
| `.agents/plugins/marketplace.json` | 로컬 마켓플레이스 목록. |
| `plugins/sodam-rhinogo/.codex-plugin/plugin.json` | Codex 플러그인 이름·버전·표시 정보. |
| `plugins/sodam-rhinogo/skills/sodam-rhinogo/` | 설치본에 포함되는 스킬 지침·스크립트·테스트. |
| `RHINO7_README.md`, `SKILL.md` | 개발자용 Rhino 7 상세 안내와 스킬 운영 지침. |
| `assets/parametric-pavilion-rhino7.py`, `assets/sodam_rhinogo_parameters.py` | 전체 모델 생성 코드와 기본값·입력 검사. |
| `scripts/launch_rhino7_live.ps1`, `scripts/run_full_rhino7.py` | Rhino 7 전체 실행 경로. |
| `scripts/audit_architectural_model_rhino7.py`, `scripts/audit_saved_rhino7.py` | 열린 Rhino 문서와 저장 파일을 따로 검사. |
| `scripts/first_run.ps1`, `scripts/generate_rhino7_model.py`, `scripts/inspect_rhino7_model.py` | 작은 오프라인 모델 생성·검사. |
| `scripts/compare_model_metrics.py`, `tests/` | 변형 비교와 자동 테스트. |
| `requirements.txt`, `.venv/` | Python 의존성과 프로젝트 전용 환경. `.venv/`는 Git에서 제외. |
| `work/` | 모델과 JSON 보고서. Git에서 제외되므로 따로 백업해야 합니다. |
| `upstream-source/` | 변경하지 않은 원본 GitHub 참고본. **수정본이나 실행 위치가 아닙니다.** |
| `LICENSE`, `LICENSE-MIT`, `NOTICE.md`와 플러그인 내부 사본 | Apache 2.0 수정본·MIT 원본 고지와 출처 안내. |

전체 실행 결과는 같은 기본 이름의 `.3dm`, `.build.json`, `.audit.json`, `.saved-audit.json` 네 파일입니다. `.audit.json`은 열린 문서, `.saved-audit.json`은 디스크에 저장된 파일을 검사합니다. 두 보고서에서 `overall_pass: true`를 확인하세요. JSON은 메모장으로 열 수 있습니다. `.3dm`은 Rhino 7에서 엽니다. 파일명만 같고 내용이 다를 수 있으므로 보고서와 모델을 한 묶음으로 보관하세요.

<a id="architecture"></a>
## 7. 워크플로우·아키텍처

```text
사용자 요청 / PowerShell 명령
        ↓
Codex 로컬 마켓플레이스 → SoDam-RhinoGo 스킬
        ↓
파라미터·출력 경로 사전 검사
        ↓
Rhino 7 + RhinoCommon 모델 생성 (또는 rhino3dm 오프라인 생성)
        ↓
열린 문서 독립 검사 → 새 .3dm 저장 → 저장 파일 독립 재검사
        ↓
work/ 모델 + JSON 보고서 → 사람이 Rhino 화면에서 최종 확인
```

기본 전체 모델은 mm 단위의 파빌리온입니다. 프레임·기둥·보·서까래·루버·참조 객체에 이름과 레이어를 붙입니다. Rhino 실행 경로는 RhinoCommon/IronPython을 사용하고, 오프라인 경로는 Python 3.12/rhino3dm을 사용합니다. **Grasshopper `.gh` 정의는 포함되지 않으며**, 원본 Rhino MCP 연결은 이 Rhino 7 경로에서 검증되지 않았습니다. 하나의 Rhino 문서는 한 번에 한 실행 흐름만 수정하세요. 같은 설정으로 다시 만드는 반복 실행 검사는 객체 수·이름이 바뀌지 않는지 확인합니다.

<a id="security"></a>
## 8. 보안과 데이터 흐름

- 모델·매개변수·JSON 보고서는 지정한 로컬 경로에 저장됩니다. 이 프로젝트 자체에는 로그인 화면, 웹 서버, DB, API 키 입력, 자체 클라우드 업로드 코드가 없습니다.
- Codex에 입력한 대화와 파일 접근, Rhino 사용권 확인, Python 패키지 다운로드는 각각 **Codex·McNeel·Python 패키지 공급 경로의 설정**을 따릅니다. 따라서 전체 과정이 항상 오프라인이라고 가정하지 마세요.
- 플러그인은 로컬 파일 읽기·모델 쓰기를 요청할 수 있습니다. 설치 전에 `.agents/plugins/marketplace.json`의 `source.path`가 `./plugins/sodam-rhinogo`인지 확인하고, 신뢰하는 프로젝트에서만 실행하세요.
- 비밀번호·토큰·개인 키를 모델 이름, 파라미터 JSON, Codex 요청, 보고서, README에 넣지 마세요. `.env`와 `work/`는 Git에서 제외되지만, 공유 전에 직접 파일·Git 변경 목록을 다시 확인해야 합니다.
- 파일은 자동 암호화되지 않습니다. 중요 모델은 별도 위치에 복사해 백업하세요. 기존 모델·보고서가 있으면 실행기가 덮어쓰기를 거부하지만, 백업을 대신하지는 않습니다.
- 이전 점검에서는 소스 65개와 작업 보고서 103개의 대표적 민감정보 패턴을 검사해 일치 항목이 없었습니다. 이는 모든 비밀정보의 부재를 증명하는 검사가 아닙니다.

<a id="updates"></a>
## 9. 업데이트 내용

<details><summary>현재 Rhino 7 재구축에서 추가·변경된 내용 펼치기</summary><ul><li>Rhino 8 중심 원본을 별도 <code>upstream-source/</code>에 보존하고, 최상위 폴더에 Rhino 7 수정본을 구축했습니다.</li><li>로컬 Codex 마켓플레이스와 <code>sodam-rhinogo@sodam-rhinogo</code> 스킬 플러그인을 구성했습니다.</li><li>Rhino 7의 전체 67객체 예제, 41객체 오프라인 예제, 열린 문서와 저장 파일의 독립 검사를 추가했습니다.</li><li>파라미터·객체 수 제한, 기존 파일 덮어쓰기 방지, 변형 비교, 반복 실행 검사, 단위 테스트 14개를 추가했습니다.</li><li>현재 설치본의 버전 표시는 <code>0.1.0+codex.20260927110134</code>입니다. 새 코드로 갱신하면 설치본 버전·검증 결과를 다시 확인해야 합니다.</li></ul></details>

<a id="troubleshooting"></a>
## 10. 문제 해결

| 증상 | 확인·대처 |
| --- | --- |
| `codex` 명령을 찾지 못함 | Codex CLI 설치·로그인을 공식 안내대로 마치고 PowerShell을 새로 여세요. 수동 모델 생성은 Codex 없이도 가능합니다. |
| 플러그인이 목록에 없음 | 프로젝트 최상위에서 마켓플레이스 등록 명령을 다시 확인하고 `codex plugin marketplace list`, `codex plugin list`를 실행하세요. 데스크톱 앱은 다시 열어 새 작업에서 확인하세요. |
| 설치됐지만 원하는 최신 코드가 아님 | 설치본은 별도 캐시입니다. 소스 수정만으로 자동 갱신된다고 가정하지 마세요. 버전과 설치본 내용을 확인한 뒤 플러그인 업데이트 절차를 밟으세요. |
| `py -3.12`가 없음 | Python 3.12를 설치하고 새 PowerShell에서 버전을 확인하세요. 다른 Python 환경을 임의로 바꾸지 마세요. |
| `Rhino 7 is not installed` | 위의 정확한 `Rhino.exe` 위치와 Rhino 7 설치·사용권을 확인하세요. Rhino 8만 설치된 PC에서는 전체 실행 경로가 맞지 않습니다. |
| `Output parent directory must already exist` | `work/` 같은 출력 폴더를 먼저 만드세요. 구현본을 다른 폴더로 옮기지는 마세요. |
| `Preserving existing model/report` | 정상적인 덮어쓰기 방지입니다. 기존 파일을 지우지 말고 출력 이름을 새로 정하세요. |
| `parameter validation failed` | JSON 문법, 키 이름, 숫자 범위, 입구 폭·기둥 간격·총 객체 수를 확인하세요. `assets/sodam_rhinogo_parameters.py`의 기본값을 참고하세요. |
| Rhino가 종료되거나 시간 초과 | Rhino 7을 직접 열어 사용권·오류창을 확인하세요. 새 출력 이름으로 다시 시도하고 필요하면 `-TimeoutSeconds 180`으로 늘리세요. 부분 생성된 파일은 보존하고 새 이름으로 재시도하세요. |
| `.audit.json`은 통과, `.saved-audit.json`은 실패 | 저장 파일 검사가 실패한 것입니다. 모델을 최종본으로 쓰지 말고 보고서의 실패 항목을 확인한 뒤 새 이름으로 재생성하세요. |
| 모델이 화면에서 이상함 | 검사 통과가 미관을 보장하지 않습니다. Rhino에서 원근·평면·입면으로 열어 보고, 치수와 레이어를 확인하세요. |

<a id="faq"></a>
## 11. 자주 묻는 질문

**Q. Rhino 8이 꼭 필요한가요?**

A. 현재 전체 실행 경로는 설치된 **Rhino 7**을 사용합니다. `rhino3dm` 패키지 버전이 8.x여도 출력 `.3dm`은 Rhino 7 형식으로 저장·재검사했습니다.

**Q. Grasshopper를 설치해야 하나요?**

A. 현재 스크립트에는 Grasshopper `.gh` 정의나 실행 단계가 없습니다. 지금 확인한 사용 경로에는 필요하지 않습니다.

**Q. Codex 플러그인만 설치하면 Rhino 안에 버튼이 생기나요?**

A. 아니요. 이것은 Codex 스킬 플러그인이며 Rhino `.rhp` 플러그인이 아닙니다. Codex의 요청 또는 PowerShell 스크립트로 Rhino를 실행합니다.

**Q. 휴대폰에서 실행할 수 있나요?**

A. 현재 전체 모델 실행기는 Windows의 Rhino 7 경로를 사용합니다. 모바일 직접 실행 기능은 없습니다. HTML 안내서는 모바일 브라우저로 읽을 수 있습니다.

**Q. 인터넷 없이도 되나요?**

A. 의존성이 이미 설치된 오프라인 모델 생성은 가능할 수 있지만, 첫 패키지 설치와 Codex·Rhino의 로그인·사용권 통신은 별도입니다. 완전한 오프라인 운영은 검증하지 않았습니다.

**Q. 원본 GitHub 저장소를 업데이트하면 이 수정본도 바뀌나요?**

A. 자동으로 바뀌지 않습니다. 원본은 `upstream-source/`의 참고본이며 수정본·설치 캐시는 따로 관리합니다.

**Q. 보고서가 통과하면 시공해도 되나요?**

A. 아니요. 이 검사는 개념 모델의 객체·형상·저장 상태를 확인합니다. 구조·법규·시공성·제작 가능성은 자격 있는 전문가의 별도 검토가 필요합니다.

<a id="license"></a>
## 12. 저작권·라이선스·상업적 이용

1. **적용 라이선스와 저작권자:** 이 Rhino 7 수정본과 SoDam-RhinoGo 플러그인의 SoDam AI Studio 기여 부분은 **Apache License, Version 2.0 (SPDX: Apache-2.0)**으로 제공합니다. 최상위와 플러그인 `LICENSE`에 [공식 Apache 2.0 본문](https://www.apache.org/licenses/LICENSE-2.0.html)과 `Copyright 2026 SoDam AI Studio` 표시가 있습니다. 원본 `leoyang1984/rhino-architectural-modeling`에서 가져온 부분의 `Copyright (c) 2026 Rhino Architectural Modeling contributors` 및 **MIT License**는 별도 [`LICENSE-MIT`](LICENSE-MIT)에 그대로 보존했습니다. Apache 표기가 원본 MIT 권리자나 모든 기여분의 권리 귀속을 바꾸지는 않습니다.
2. **사용·수정·판매·납품:** 두 라이선스의 해당 조건을 지키면 코드를 사용·수정·복제·포크·재배포하고, 상업적 서비스·교육 자료·회사 업무·고객 납품에 활용할 수 있습니다. 복사본을 배포할 때 Apache 2.0 본문, 원본 MIT 저작권·허락 고지, 해당하는 `NOTICE.md` 고지를 함께 제공하고 수정 사실을 표시하세요. Apache 2.0에는 저작권 및 특허 관련 조건도 있으므로 본문을 확인하세요. 이 안내는 Rhino·고객 자료·생성 결과물의 권리를 보장하지 않습니다.
3. **하면 안 되는 일:** 원본 MIT 고지나 적용되는 Apache/NOTICE 고지를 제거하지 마세요. 이 저장소의 라이선스로 Rhino 실행 파일·사용권 키·McNeel 문서, 타인의 상표·이미지, 고객 자료를 배포할 수 있다고 주장하지 마세요. SoDam-RhinoGo는 McNeel의 공식 제품이나 보증이 아닙니다. 비공개 자료·개인정보·API 키를 공개 예제에 넣지 마세요.
4. **별도 프로그램과 의존성:** Rhino 7의 설치·사용·동시 접속·사용권 유형은 [Rhino 7 EULA](https://www.rhino3d.com/7/eula/)와 본인 계약에 따릅니다. 이 프로젝트는 공개 API를 사용하며 Rhino 비공개 바이너리의 역컴파일 권한을 주지 않습니다. `requirements.txt`의 직접 의존성은 `rhino3dm>=8.35,<9` 하나이고, 이 PC에 설치된 `8.35.0`의 메타데이터 및 포함 라이선스는 MIT입니다. 패키지 바이너리를 함께 배포한다면 정확한 배포 버전의 고지를 다시 확인하세요. Codex 계정·외부 API/SDK·서비스 요금제와 약관은 각각 별개입니다.
5. **새 자료와 AI 결과물:** 점검한 소스에는 묶음 이미지·아이콘·폰트·영상·음원·외부 3D 모델이 없었습니다. 나중에 추가하는 모델·텍스처·템플릿·프롬프트·스크린샷·AI 생성 코드/문서/이미지/모델은 출처, 저작권, 상업적 허락, 표시 의무, 유사 저작물 침해 가능성을 최종 사용 전에 개별 확인하세요. `work/` 생성물과 고객 입력은 이번 소스 조사에서 제외했습니다.
6. **공개·납품 전 확인:** 원본 MIT 고지와 사용자 지정 Apache 2.0 표기를 파일에서 확인했지만, Rhino 7 수정 코드의 모든 기여자 권리·고객 계약·입력 자료·생성 결과물 권리는 파일만으로 확정할 수 없습니다. 현재 GitHub 업로드는 **비공개 저장소**를 대상으로 합니다. 공개 전환·판매·고객 납품 전에는 권리 사슬과 Rhino 사용권 유형을 확인하고 **법무/전문가 검토 필요** 항목을 해결하세요. 모델 검사 통과는 건축 인허가·구조 안전·시공 승인이 아닙니다.
7. **보증과 책임:** Apache 2.0 및 원본 MIT의 보증 배제·책임 제한은 각각 해당 본문을 따릅니다. **참고용·법적 효력 보장 안 함, 사용자 책임·변호사 확인 권장.**

<a id="evidence"></a>
## 13. 검증 범위와 공식 자료

- 이 컴퓨터에서 확인: 로컬 플러그인 설치·활성화, 설치본 단위 테스트 14개, Python 의존성 검사, Rhino 7 전체 예제 67개 객체와 저장 파일 감사, 오프라인 예제 41개 객체와 Rhino 7 형식 저장. 기존 파일 덮어쓰기 거부도 확인했습니다.
- 아직 확인하지 못함: Codex 데스크톱 화면 선택·자연어 전체 호출, Rhino 화면의 시각적 결과, 원본 Rhino MCP의 Rhino 7 연결, Grasshopper, 공개 배포·다른 PC 설치. 설치와 실제 작동을 구분해 판단하세요.
- 공식 참고: [Codex 플러그인 패키징](https://developers.openai.com/plugins/build/plugins), [Rhino 다운로드](https://www.rhino3d.com/en/download/), [Rhino 7 EULA](https://www.rhino3d.com/7/eula/), [Python Windows 다운로드](https://www.python.org/downloads/windows/), [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0.html), [원본 MIT 라이선스](https://spdx.org/licenses/MIT.html). 이 문서는 2026-09-27의 파일·검증 상태를 설명합니다. 공식 사이트의 설치·약관 내용은 바뀔 수 있으므로 실제 설치·배포 시 다시 확인하세요.
