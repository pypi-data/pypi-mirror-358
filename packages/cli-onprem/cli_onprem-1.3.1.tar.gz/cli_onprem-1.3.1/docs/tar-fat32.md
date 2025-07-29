# 📦 tar-fat32 명령어

> 💡 **빠른 시작**: `cli-onprem tar-fat32 pack ./large-file --chunk-size 2G`

## 📋 목차

- [개요](#개요)
- [사용 시나리오](#사용-시나리오)
- [사용법](#사용법)
- [옵션](#옵션)
- [예제](#예제)
- [고급 기능](#고급-기능)
- [문제 해결](#문제-해결)
- [관련 명령어](#관련-명령어)

## 개요

`tar-fat32` 명령어는 FAT32 파일 시스템의 4GB 크기 제한을 우회하여 대용량 파일을 분할 압축하고 복원하는 기능을 제공합니다.
SHA256 무결성 검증과 자동 복원 스크립트 생성을 통해 안전하고 편리한 파일 전송을 지원합니다.

### 주요 특징

- ✨ **FAT32 호환**: 4GB 제한을 우회하여 대용량 파일 처리
- ✨ **SHA256 무결성 검증**: 모든 조각에 대한 체크섬 생성 및 검증
- ✨ **자동 복원 스크립트**: 복원을 위한 독립적인 셸 스크립트 생성
- ✨ **진행률 표시**: 압축 및 복원 과정 실시간 모니터링
- ✨ **유연한 청크 크기**: 용도에 맞는 분할 크기 설정 가능

## 사용 시나리오

이 명령어는 다음과 같은 상황에서 유용합니다:

1. **FAT32 USB 전송**: 4GB 이상 파일을 FAT32 USB로 전송
2. **이메일 첨부**: 대용량 파일을 작은 조각으로 나누어 전송
3. **네트워크 전송**: 불안정한 네트워크에서 중단 없는 전송
4. **백업 분할**: 대용량 백업 파일을 관리 가능한 크기로 분할

## 사용법

### 기본 문법

```bash
cli-onprem tar-fat32 <command> <path> [OPTIONS]
```

### 빠른 예제

```bash
# 파일 분할 압축
cli-onprem tar-fat32 pack ./movie.iso --chunk-size 2G

# 파일 복원
cli-onprem tar-fat32 restore ./movie.iso.pack
```

## 옵션

### 하위 명령어

| 명령어 | 설명 | 용도 |
|--------|------|------|
| `pack` | 파일/디렉토리를 분할 압축 | 파일 분할 |
| `restore` | 분할된 파일 복원 | 파일 복원 |

### pack 명령어 옵션

| 옵션 | 약어 | 설명 | 기본값 | 예시 |
|------|------|------|--------|------|
| `--chunk-size` | `-c` | 분할 조각 크기 | `3G` | `--chunk-size 500M` |

### restore 명령어 옵션

| 옵션 | 설명 | 기본값 | 용도 |
|------|------|--------|------|
| `--purge` | 복원 성공 시 .pack 디렉토리 삭제 | `false` | 정리 |

## 예제

### 🎯 기본 사용 예제

#### 1. pack - 파일 분할 압축

```bash
# 기본 분할 (3GB 조각)
cli-onprem tar-fat32 pack large-database.sql
# 결과: large-database.sql.pack/ 디렉토리 생성

# 커스텀 조각 크기 지정
cli-onprem tar-fat32 pack ./project-backup --chunk-size 500M
# 결과: project-backup.pack/ 디렉토리 생성

# FAT32 호환 크기 (2GB)
cli-onprem tar-fat32 pack movie.mkv --chunk-size 2G
# 결과: movie.mkv.pack/ 디렉토리 생성
```

#### 2. restore - 파일 복원

```bash
# 기본 복원
cli-onprem tar-fat32 restore large-database.sql.pack
# 결과: large-database.sql 파일 복원

# 복원 후 .pack 디렉토리 삭제
cli-onprem tar-fat32 restore project-backup.pack --purge
# 결과: project-backup 복원 후 .pack 디렉토리 제거
```

### 🚀 실무 활용 예제

#### 1. 대용량 백업 파일 처리

```bash
# 10GB 데이터베이스 백업을 2GB 조각으로 분할
cli-onprem tar-fat32 pack db-backup-20250524.sql --chunk-size 2G

# 생성된 구조
ls -la db-backup-20250524.sql.pack/
# drwxr-xr-x  parts/
# -rw-r--r--  manifest.sha256
# -rw-r--r--  restore.sh
# -rw-r--r--  9876_MB

# USB에 복사 후 다른 시스템에서 복원
./db-backup-20250524.sql.pack/restore.sh --purge
```

#### 2. 독립적인 복원 스크립트 사용

```bash
# pack 생성
cli-onprem tar-fat32 pack ./important-data --chunk-size 1G

# 다른 시스템에서 CLI 도구 없이 복원
cd important-data.pack
./restore.sh

# 또는 정리와 함께 복원
./restore.sh --purge
```

#### 3. 배치 처리로 여러 파일 분할

```bash
#!/bin/bash
# 여러 파일을 일괄 분할
FILES=("video1.mp4" "video2.mp4" "video3.mp4")

for file in "${FILES[@]}"; do
  echo "Processing $file..."
  cli-onprem tar-fat32 pack "$file" --chunk-size 2G
done

# 결과: video1.mp4.pack/, video2.mp4.pack/, video3.mp4.pack/ 생성
```

### 📝 출력 예시

**pack 명령어 출력**:
```
📦 Packing movie.iso with chunk size 2G...
🗜️  Compressing... [████████████████████] 100% (8.2 GB)
✂️  Splitting into chunks... [██████████████] 100% (4 parts)
🔐 Generating SHA256 checksums... [████████] 100%
📁 Created: movie.iso.pack/
   ├── parts/ (4 files, 8.2 GB total)
   ├── manifest.sha256
   ├── restore.sh
   └── 8234_MB
```

**restore 명령어 출력**:
```
🔍 Verifying integrity... [████████████████] 100%
✅ All checksums verified
🔗 Joining parts... [██████████████████] 100%
🗜️  Decompressing... [████████████████] 100%
✅ Restored: movie.iso (8.2 GB)
🧹 Cleaned up temporary files
```

## 고급 기능

### .pack 디렉토리 구조

분할 후 생성되는 디렉토리는 다음과 같은 구조를 갖습니다:

```
filename.pack/
├── parts/          # 분할된 조각 파일들
│   ├── 0000.part
│   ├── 0001.part
│   ├── 0002.part
│   └── 0003.part
├── manifest.sha256 # SHA256 체크섬 목록
├── restore.sh      # 독립적인 복원 스크립트
└── 8234_MB         # 원본 파일 크기 표시 (빈 파일)
```

### SHA256 무결성 검증

각 조각 파일에 대해 SHA256 해시가 생성되어 manifest.sha256에 저장됩니다:

```bash
# manifest.sha256 파일 내용 예시
a1b2c3d4e5f6...  parts/0000.part
f6e5d4c3b2a1...  parts/0001.part
1234567890ab...  parts/0002.part
abcdef123456...  parts/0003.part
```

복원 시 자동으로 모든 조각의 무결성을 검증합니다.

### 독립적인 복원 스크립트

생성되는 restore.sh는 CLI 도구 없이도 독립적으로 실행 가능합니다:

```bash
#!/bin/bash
# 자동 생성된 복원 스크립트
# CLI-ONPREM 도구가 없어도 실행 가능

# SHA256 검증
echo "🔍 Verifying integrity..."
sha256sum -c manifest.sha256 || exit 1

# 파일 결합 및 압축 해제
echo "🔗 Restoring original file..."
cat parts/*.part | tar -xzf - -C ..

echo "✅ Restoration completed"
```

### 청크 크기 가이드

용도에 따른 권장 청크 크기:

| 용도 | 권장 크기 | 이유 |
|------|-----------|------|
| FAT32 USB | `2G` | FAT32의 4GB 제한 고려 |
| 이메일 첨부 | `25M` | 대부분 메일 서비스 제한 |
| 네트워크 전송 | `500M-1G` | 재전송 부담 최소화 |
| DVD 백업 | `4.3G` | DVD 용량 최대 활용 |

## 문제 해결

### 자주 발생하는 문제

#### ❌ 오류: `No space left on device`

**원인**: 디스크 공간 부족

**해결 방법**:
```bash
# 디스크 용량 확인
df -h

# 다른 위치에서 실행하거나 불필요한 파일 정리
rm -rf /tmp/large-files
cli-onprem tar-fat32 pack ./data --chunk-size 1G
```

#### ❌ 오류: `SHA256 verification failed`

**원인**: 파일 전송 중 손상 발생

**해결 방법**:
1. 손상된 조각 파일 재전송
2. manifest.sha256와 비교하여 손상된 파일 확인
3. 원본에서 해당 조각만 다시 복사

#### ❌ 오류: `Output directory already exists`

**원인**: 동일한 이름의 .pack 디렉토리가 이미 존재

**해결 방법**:
```bash
# 기존 디렉토리 제거 후 재실행
rm -rf filename.pack
cli-onprem tar-fat32 pack filename
```

### 디버깅 팁

- 💡 무결성 검증은 restore.sh에서도 자동 수행
- 💡 부분적으로 손상된 경우 해당 조각만 재전송 가능
- 💡 크기 표시 파일(예: 8234_MB)로 원본 크기 확인

## 관련 명령어

- 📌 [`docker-tar`](./docker_tar.md) - Docker 이미지를 tar로 저장 후 분할
- 📌 [`s3-share`](./s3-share.md) - 분할된 파일을 S3로 업로드
- 📌 [`helm-local`](./helm-local.md) - Helm 차트를 분할하여 전송

---

<details>
<summary>📚 추가 참고 자료</summary>

- [FAT32 파일 시스템 제한사항](https://en.wikipedia.org/wiki/File_Allocation_Table#FAT32)
- [SHA256 해시 알고리즘](https://en.wikipedia.org/wiki/SHA-2)
- [GNU tar 압축 옵션](https://www.gnu.org/software/tar/manual/tar.html)

</details>

<details>
<summary>🔄 변경 이력</summary>

- v0.11.0: 복원 스크립트 개선, 진행률 표시 추가
- v0.10.0: SHA256 무결성 검증 강화, 자동 정리 기능 추가
- v0.9.0: 초기 릴리즈

</details>