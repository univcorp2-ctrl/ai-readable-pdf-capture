# Setup Guide

## 1. 共通セットアップ

```bash
git clone <repo-url>
cd ai-readable-pdf-capture
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

動作確認:

```bash
ai-pdf-capture demo --output-dir outputs/demo
```

## 2. WindowsでOCRを使う

1. Tesseract OCR for Windowsをインストールします。
2. 日本語OCRを使う場合は `jpn.traineddata` を入れます。
3. `tesseract.exe` にPATHを通します。
4. PowerShellを開き直して確認します。

```powershell
tesseract --version
```

OCR付きPDF:

```powershell
ai-pdf-capture build outputs/demo/pages --output outputs/searchable.pdf --ocr --language eng+jpn
```

## 3. macOSでOCRを使う

```bash
brew install tesseract tesseract-lang
ai-pdf-capture build outputs/demo/pages --output outputs/searchable.pdf --ocr --language eng+jpn
```

## 4. Ubuntu/DebianでOCRを使う

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-jpn
ai-pdf-capture build outputs/demo/pages --output outputs/searchable.pdf --ocr --language eng+jpn
```

## 5. 実キャプチャの準備

1. キャプチャ対象の資料をビューアで開きます。
2. ページ送りキーを確認します。例: `right`, `left`, `pagedown`, `space`。
3. 必要ならキャプチャ領域を決めます。形式は `x,y,width,height` です。
4. 実行します。

```bash
ai-pdf-capture run \
  --pages 20 \
  --advance key:right \
  --delay 0.6 \
  --region 120,80,1200,1600 \
  --owner-label "private-use-only" \
  --output outputs/result.pdf \
  --acknowledge-compliance
```

## 6. 本番運用チェックリスト

- [ ] 対象資料のキャプチャが著作権・契約・規約上許可されている
- [ ] 機密資料の場合、社内ルール上AIサービスへのアップロードが許可されている
- [ ] OCR用Tesseractと言語データが入っている
- [ ] ページ送り方法が安定している
- [ ] 出力PDFに所有者ラベル・QRを入れている
- [ ] 作成PDFを第三者へ配布しない運用になっている

## 7. トラブルシューティング

### `Real screen capture requires --acknowledge-compliance`

実画面キャプチャでは、合法・許可済み用途であることを明示するため `--acknowledge-compliance` が必須です。

### OCRで `Tesseract executable was not found`

Tesseract本体が未インストール、またはPATHが通っていません。`tesseract --version` が動く状態にしてください。

### 日本語OCRができない

日本語言語データが不足しています。Ubuntuなら `tesseract-ocr-jpn`、macOS Homebrewなら `tesseract-lang` を入れてください。

### キャプチャ画像が大きすぎる

`--region` で必要な範囲だけ切り取るか、ビューアのウィンドウサイズを小さくしてください。
