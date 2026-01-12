# Azure AI Foundry Agent Web Application - 프로젝트 분석 문서

## 목차

1. [개요](#1-개요)
2. [기술 스택](#2-기술-스택)
3. [디렉토리 구조](#3-디렉토리-구조)
4. [아키텍처](#4-아키텍처)
5. [주요 컴포넌트](#5-주요-컴포넌트)
6. [인증 및 보안](#6-인증-및-보안)
7. [배포](#7-배포)
8. [설정 파일](#8-설정-파일)

---

## 1. 개요

### 프로젝트 정보

| 항목 | 내용 |
|------|------|
| **프로젝트명** | Azure AI Foundry Agent Web Application |
| **유형** | AI 통합 풀스택 웹 애플리케이션 |
| **목적** | Azure AI Foundry Agent Service와 통합된 인증 기반 채팅 인터페이스 제공 |

### 주요 특징

- Azure AI 기반 대화형 애플리케이션
- Microsoft Entra ID 인증
- 단일 컨테이너 배포 아키텍처
- Azure Developer CLI(azd)를 통한 신속한 배포
- 클라우드 의존성 없는 로컬 개발 지원

---

## 2. 기술 스택

### 프론트엔드

| 기술 | 버전 | 용도 |
|------|------|------|
| React | 19.2.1 | UI 프레임워크 |
| TypeScript | 5.9.3 | 타입 안전성 |
| Vite | 7.2.6 | 빌드 도구 |
| MSAL React | 3.0.23 | Microsoft 인증 |
| Fluent UI | 9.72.8 | Microsoft 디자인 시스템 |
| Fluent Copilot | 0.30.2 | 채팅 UI 컴포넌트 |
| react-markdown | 10.1.0 | 마크다운 렌더링 |

### 백엔드

| 기술 | 버전 | 용도 |
|------|------|------|
| ASP.NET Core | 9.0 | 웹 프레임워크 |
| Azure.AI.Projects | 1.2.0-beta.1 | AI Foundry 통합 |
| Microsoft.Identity.Web | 4.1.1 | JWT 인증 |
| Azure.Identity | 1.17.1 | Azure 자격 증명 |
| OpenTelemetry | 1.14.0 | 원격 측정 |

### 인프라 및 배포

| 기술 | 용도 |
|------|------|
| Bicep | Infrastructure as Code |
| Azure Developer CLI | 배포 자동화 |
| Docker | 컨테이너화 |
| Azure Container Apps | 호스팅 |
| Azure Container Registry | 이미지 저장소 |

---

## 3. 디렉토리 구조

```
az-foundry-agent-webapp-py/
│
├── backend/                              # ASP.NET Core API
│   ├── WebApp.Api/
│   │   ├── Program.cs                    # 메인 엔트리포인트
│   │   ├── appsettings.json              # 설정 템플릿
│   │   ├── Models/                       # 데이터 모델
│   │   │   ├── ChatRequest.cs            # 사용자 메시지 입력
│   │   │   ├── ChatResponse.cs           # 에이전트 응답
│   │   │   ├── AgentMetadata.cs          # 에이전트 정보
│   │   │   ├── ConversationModels.cs     # 대화 구조
│   │   │   └── ErrorResponse.cs          # RFC 7807 에러
│   │   └── Services/
│   │       └── AzureAIAgentService.cs    # AI 통합 및 스트리밍
│   ├── WebApp.ServiceDefaults/           # 공유 인프라
│   └── WebApp.sln                        # 솔루션 파일
│
├── frontend/                             # React + TypeScript + Vite
│   ├── src/
│   │   ├── App.tsx                       # 루트 컴포넌트
│   │   ├── main.tsx                      # 엔트리포인트
│   │   ├── config/
│   │   │   ├── authConfig.ts             # MSAL 설정
│   │   │   └── themes.ts                 # 테마 설정
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx         # 메인 채팅 UI
│   │   │   ├── AgentPreview.tsx          # 에이전트 헤더
│   │   │   ├── ThemeProvider.tsx         # 테마 컨텍스트
│   │   │   ├── chat/                     # 채팅 컴포넌트
│   │   │   │   ├── ChatInput.tsx
│   │   │   │   ├── UserMessage.tsx
│   │   │   │   ├── AssistantMessage.tsx
│   │   │   │   ├── FilePreview.tsx
│   │   │   │   ├── UsageInfo.tsx
│   │   │   │   └── StarterMessages.tsx
│   │   │   ├── core/                     # 재사용 컴포넌트
│   │   │   │   ├── ErrorBoundary.tsx
│   │   │   │   ├── ErrorMessage.tsx
│   │   │   │   ├── Markdown.tsx
│   │   │   │   ├── SettingsPanel.tsx
│   │   │   │   ├── ThemePicker.tsx
│   │   │   │   └── AgentIcon.tsx
│   │   │   └── icons/                    # 커스텀 SVG 아이콘
│   │   ├── contexts/                     # React Context
│   │   │   ├── AppContext.tsx
│   │   │   └── ThemeContext.tsx
│   │   ├── hooks/                        # 커스텀 훅
│   │   │   ├── useAppState.ts
│   │   │   ├── useAuth.ts
│   │   │   └── useChat.ts
│   │   ├── services/
│   │   │   └── chatService.ts            # API 클라이언트
│   │   ├── types/                        # 타입 정의
│   │   ├── utils/                        # 유틸리티
│   │   │   ├── sseParser.ts              # SSE 파싱
│   │   │   ├── errorHandler.ts
│   │   │   └── fileAttachments.ts
│   │   └── reducers/                     # 상태 리듀서
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── infra/                                # Bicep IaC
│   ├── main.bicep                        # 메인 오케스트레이터
│   ├── main-app.bicep                    # Container App 배포
│   ├── main-infrastructure.bicep         # ACR + 환경
│   ├── core/                             # 재사용 모듈
│   │   ├── host/
│   │   │   └── container-app.bicep
│   │   └── security/
│   │       └── role-assignment.bicep
│   └── main.parameters.json
│
├── deployment/                           # 배포 자동화
│   ├── hooks/
│   │   ├── preprovision.ps1              # Entra 앱 + AI 검색
│   │   ├── postprovision.ps1             # Docker 빌드 및 배포
│   │   ├── postdown.ps1                  # 정리
│   │   └── modules/
│   │       └── New-EntraAppRegistration.ps1
│   ├── scripts/
│   │   ├── start-local-dev.ps1           # 로컬 개발 시작
│   │   ├── deploy.ps1                    # 코드 변경 배포
│   │   ├── list-agents.ps1               # 에이전트 목록
│   │   └── build-and-deploy-container.ps1
│   ├── docker/
│   │   ├── frontend.Dockerfile           # 멀티스테이지 빌드
│   │   └── backend.Dockerfile
│   └── AGENTS.md
│
├── .vscode/                              # VS Code 설정
├── .github/                              # GitHub 템플릿
├── azure.yaml                            # AZD 매니페스트
└── README.md
```

---

## 4. 아키텍처

### 고수준 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────────┐
│                    AZURE CONTAINER APPS                         │
│  ┌────────────────────────────────────────────────────────┐    │
│  │           Single Container (Port 8080)                 │    │
│  │                                                         │    │
│  │  ┌─────────────────┐        ┌──────────────────────┐  │    │
│  │  │  React App      │        │   ASP.NET Core API   │  │    │
│  │  │  (wwwroot)      │◄──────►│  - Auth + JWT        │  │    │
│  │  │  - SSO redirect │        │  - Chat endpoints    │  │    │
│  │  │  - Hot reload   │        │  - Agent metadata    │  │    │
│  │  │  - Chat UI      │        │  - SSE streaming     │  │    │
│  │  └─────────────────┘        └──────────────────────┘  │    │
│  │           ▲                           │                │    │
│  │           │                           ▼                │    │
│  │           │                  ┌──────────────────────┐  │    │
│  │           │                  │ AzureAIAgentService  │  │    │
│  │           │                  │ (Token + Streaming)  │  │    │
│  │           │                  └──────────────────────┘  │    │
│  └────────────┼──────────────────────┬───────────────────┘    │
│               │                      │                         │
└───────────────┼──────────────────────┼─────────────────────────┘
                │                      │
         ┌──────▼──────┐      ┌────────▼──────────┐
         │  Microsoft  │      │ Azure AI Foundry  │
         │  Entra ID   │      │ Agent Service     │
         │  (Auth)     │      │ (RBAC via Managed │
         │             │      │  Identity)        │
         └─────────────┘      └───────────────────┘
```

### 데이터 흐름

#### 인증 흐름 (PKCE)

```
1. 프론트엔드 → 미인증 사용자를 Entra ID로 리다이렉트
2. 사용자 로그인 → Chat.ReadWrite 스코프 권한 부여
3. Entra ID → 인가 코드 + PKCE 상태 반환
4. MSAL → 코드를 ID + 액세스 토큰으로 교환 (localStorage 저장)
5. 모든 API 요청 → Authorization: Bearer <token> 헤더 포함
```

#### 채팅 스트리밍 흐름

```
1. 프론트엔드 → ChatRequest 전송 (메시지 + conversationId + 이미지)
2. 백엔드 → JWT 토큰 검증 (스코프, 클레임)
3. AzureAIAgentService:
   - 신규 대화인 경우 conversationId 생성
   - Azure AI Foundry Agent Service 호출
   - Server-Sent Events로 응답 스트리밍
4. SSE 이벤트 유형: conversationId, chunk, usage, done, error
5. 프론트엔드 → SSE 파싱 및 실시간 채팅 UI 업데이트
```

### 아키텍처 패턴

| 패턴 | 설명 |
|------|------|
| **단일 컨테이너** | React 앱을 ASP.NET wwwroot에 번들링, 배포 복잡성 감소 |
| **Managed Identity + RBAC** | 코드에 비밀번호 없음, Azure가 자격 증명 자동 주입 |
| **Server-Sent Events** | 실시간 채팅 응답 스트리밍 |
| **Bicep 모듈** | 재사용 가능한 IaC 컴포지션 패턴 |

---

## 5. 주요 컴포넌트

### 컴포넌트 상호작용

| 컴포넌트 | 역할 | 통신 대상 |
|----------|------|-----------|
| `main.tsx` | MSAL 초기화, 인증 설정 | `App.tsx`, `MsalProvider` |
| `App.tsx` | 라우트 가드, 에이전트 메타데이터 로딩 | `/api/agent`, `AppContext` |
| `ChatInterface.tsx` | 메인 UI 레이아웃 | `ChatInput`, `AssistantMessage`, `UserMessage` |
| `useAppState()` | 전역 인증 + 테마 상태 | `AppContext`, MSAL 훅 |
| `useAuth()` | 토큰 획득 | MSAL, `/api/chat/stream` |
| `chatService.ts` | HTTP 클라이언트 래퍼 | `/api/chat/stream`, `/api/agent` |
| `AzureAIAgentService` | AI 통합 | Azure AI Foundry SDK, `AIProjectClient` |
| `Program.cs` | 미들웨어 파이프라인 | 모든 엔드포인트, 정적 파일 제공 |

### 핵심 파일 상세

#### `backend/WebApp.Api/Program.cs`
- ASP.NET Core 호스트 설정
- JWT 인증 미들웨어 구성
- API 엔드포인트 정의
- 정적 파일 제공 설정

#### `backend/WebApp.Api/Services/AzureAIAgentService.cs`
- Azure AI Foundry SDK 통합
- 대화 생성 및 관리
- SSE 스트리밍 로직
- 토큰 자격 증명 처리

#### `frontend/src/components/ChatInterface.tsx`
- 메인 채팅 UI 레이아웃
- 메시지 렌더링
- 스트리밍 상태 관리
- 사용자 입력 처리

#### `frontend/src/hooks/useChat.ts`
- 채팅 API 상호작용
- SSE 연결 관리
- 메시지 상태 관리

---

## 6. 인증 및 보안

### 인증 모델

| 항목 | 상세 |
|------|------|
| **프로토콜** | OAuth 2.0 PKCE (SPA 모범 사례) |
| **ID 제공자** | Microsoft Entra ID |
| **스코프** | `Chat.ReadWrite` (위임된 권한) |
| **토큰 저장** | localStorage (SPA용) |

### 권한 부여

```csharp
// 백엔드 JWT 검증
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddMicrosoftIdentityWebApi(builder.Configuration);

// 엔드포인트 보호
app.MapPost("/api/chat/stream", ...)
    .RequireAuthorization(policy =>
        policy.RequireAuthenticatedUser()
              .RequireScope("Chat.ReadWrite"));
```

### Azure 접근 방식

| 환경 | 자격 증명 |
|------|-----------|
| **프로덕션** | ManagedIdentityCredential (비밀번호 없음) |
| **개발** | ChainedTokenCredential (AzureCli → AzureDeveloperCli) |
| **RBAC 역할** | Cognitive Services User |

### 보안 고려사항

- PKCE로 코드 가로채기 공격 방지
- JWT 토큰 스코프 및 클레임 검증
- Managed Identity로 비밀번호 노출 방지
- CORS 정책 적용

---

## 7. 배포

### 로컬 개발

```powershell
# 로컬 개발 서버 시작
./deployment/scripts/start-local-dev.ps1
```

**실행 흐름:**
1. `.env` 파일 로드 (azd 환경 또는 로컬)
2. 백엔드 시작: `dotnet run` (포트 8080, watch 모드)
3. 프론트엔드 시작: `npm run dev` (포트 5173, Vite HMR)
4. 프론트엔드가 `/api/*`를 `http://localhost:8080`으로 프록시
5. 사용자 → `http://localhost:5173` → MSAL 리다이렉트 → Entra 로그인

### 클라우드 배포 (azd up)

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: preprovision.ps1                                  │
│  - Entra ID 앱 등록 생성                                    │
│  - AI Foundry 리소스 검색                                   │
│  - .env 파일 생성 (AI_AGENT_ENDPOINT, AI_AGENT_ID)          │
│  - ENTRA_SPA_CLIENT_ID, ENTRA_TENANT_ID 출력                │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: provision (자동 Bicep)                            │
│  - 리소스 그룹 생성                                         │
│  - ACR (컨테이너 레지스트리) 배포                           │
│  - Container Apps 환경 배포                                 │
│  - Container App 생성 (플레이스홀더 이미지)                 │
│  - Managed Identity RBAC 할당                               │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: postprovision.ps1                                 │
│  - build-and-deploy-container.ps1 호출                      │
│  - Docker 감지 또는 ACR 클라우드 빌드 사용                  │
│  - 멀티스테이지 빌드: React → .NET → 런타임 컨테이너        │
│  - ACR에 이미지 푸시                                        │
│  - Container App 새 이미지로 업데이트                       │
└─────────────────────────────────────────────────────────────┘
                              ▼
            결과: HTTPS://<app>.azurecontainerapps.io
```

### 코드만 업데이트 (deploy.ps1)

```powershell
./deployment/scripts/deploy.ps1
```

**실행 흐름:**
1. React + .NET 재빌드
2. 멀티스테이지 Docker 빌드
3. ACR에 푸시
4. Container App 업데이트 (인프라 변경 없음)

### Docker 빌드 구조

```dockerfile
# Stage 1: React 빌드
FROM node:22-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: .NET 빌드
FROM mcr.microsoft.com/dotnet/sdk:9.0-alpine AS backend-build
WORKDIR /app
COPY backend/ ./
RUN dotnet publish -c Release -o /app/publish

# Stage 3: 런타임
FROM mcr.microsoft.com/dotnet/aspnet:9.0-alpine
WORKDIR /app
COPY --from=backend-build /app/publish .
COPY --from=frontend-build /app/frontend/dist ./wwwroot
EXPOSE 8080
ENTRYPOINT ["dotnet", "WebApp.Api.dll"]
```

---

## 8. 설정 파일

### 프로젝트 루트

| 파일 | 용도 |
|------|------|
| `azure.yaml` | AZD 매니페스트 (`azd up` 엔트리포인트) |
| `.env` (자동 생성) | 런타임 시크릿 (커밋 안 함) |

### 백엔드 설정

| 파일 | 용도 |
|------|------|
| `appsettings.json` | 설정 스키마 (시크릿 없음) |
| `appsettings.Development.json` | 개발 환경 설정 |
| `launchSettings.json` | VS 디버그 프로필 |

### 프론트엔드 설정

| 파일 | 용도 |
|------|------|
| `package.json` | npm 의존성 + 스크립트 |
| `vite.config.ts` | Vite + 백엔드 프록시 |
| `tsconfig.json` | TypeScript strict 모드 |
| `.env.local` (개발 전용) | 로컬 Entra 자격 증명 |

### 인프라 설정

| 파일 | 용도 |
|------|------|
| `infra/main.bicep` | Bicep 엔트리포인트 |
| `infra/main.parameters.json` | 기본 파라미터 값 |
| `infra/abbreviations.json` | 리소스 명명 규칙 |

### 환경 변수

#### 백엔드 (.env)

```env
AI_AGENT_ENDPOINT=https://<project>.services.ai.azure.com
AI_AGENT_ID=<agent-id>
ENTRA_SPA_CLIENT_ID=<client-id>
ENTRA_TENANT_ID=<tenant-id>
```

#### 프론트엔드 (.env.local)

```env
VITE_ENTRA_CLIENT_ID=<client-id>
VITE_ENTRA_TENANT_ID=<tenant-id>
VITE_ENTRA_SCOPE=api://<client-id>/Chat.ReadWrite
```

---

## 부록: 명령어 참조

### 개발

```powershell
# 로컬 개발 시작
./deployment/scripts/start-local-dev.ps1

# 에이전트 목록 확인
./deployment/scripts/list-agents.ps1
```

### 배포

```powershell
# 전체 프로비저닝 (인프라 + 앱)
azd up

# 코드만 배포
./deployment/scripts/deploy.ps1

# 리소스 정리
azd down
```

### 프론트엔드

```bash
cd frontend
npm install       # 의존성 설치
npm run dev       # 개발 서버
npm run build     # 프로덕션 빌드
npm run lint      # 린트 검사
```

### 백엔드

```bash
cd backend
dotnet restore    # 의존성 복원
dotnet build      # 빌드
dotnet run        # 실행
dotnet watch      # 핫 리로드 실행
```

---

*문서 생성일: 2026-01-12*
