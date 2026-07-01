# Architecture

AI Readable PDF Capture は、許可された資料を画面キャプチャし、AIに読み込ませやすいPDFへ変換するためのローカル実行型アプリです。

## コンポーネント

| コンポーネント | 役割 | 主なファイル |
|---|---|---|
| CLI | ユーザー入力、ワークフロー起動 | `src/ai_readable_pdf_capture/cli.py` |
| GUI | Tkinterによる簡易操作画面 | `src/ai_readable_pdf_capture/gui.py` |
| Capture Engine | スクリーンショット取得、ページ送り | `src/ai_readable_pdf_capture/capture.py` |
| PDF Builder | 画像PDF化、OCRテキストレイヤー、QR、メタデータ | `src/ai_readable_pdf_capture/pdf_builder.py` |
| Config Loader | YAML設定読み込み | `src/ai_readable_pdf_capture/config.py` |
| Demo Generator | CI/検証用のサンプルPDF生成 | `src/ai_readable_pdf_capture/demo.py` |

## 処理フロー

```mermaid
sequenceDiagram
    actor User as ユーザー
    participant Viewer as 資料ビューア
    participant CLI as CLI/GUI
    participant Capture as Capture Engine
    participant PDF as PDF Builder
    participant OCR as Tesseract OCR
    participant AI as AIサービス

    User->>Viewer: 許可された資料を開く
    User->>CLI: ページ数・領域・ページ送り方法を指定
    CLI->>Capture: CaptureConfigを渡す
    Capture->>Viewer: スクリーンショット取得
    Capture->>Viewer: key/clickでページ送り
    Capture-->>CLI: PNG画像一覧
    CLI->>PDF: PDFBuildOptionsと画像一覧
    alt OCRあり
        PDF->>OCR: 単語と座標を抽出
        OCR-->>PDF: text/x/y/w/h/confidence
        PDF->>PDF: 透明テキストレイヤーを重ねる
    else OCRなし
        PDF->>PDF: 画像PDFのみ作成
    end
    PDF->>PDF: 所有者ラベル・QR・メタデータを埋め込み
    PDF-->>User: PDF出力
    User->>AI: ユーザー自身がPDFをアップロード
```

## 設計上の境界線

- DRM解除やコピー防止回避は実装しない
- キャプチャ可否はユーザーの権利・契約・規約に依存するため、実行時に明示的な `--acknowledge-compliance` を要求する
- OCRはローカルTesseractを使うため、文書内容を外部APIへ送信しない
- 生成PDFには所有者ラベルやQRを埋め込めるが、これは共有抑止の補助であり、法的・技術的な完全保護ではない

## データフロー

```mermaid
flowchart LR
    A[Screen pixels] --> B[PNG files]
    B --> C[ReportLab image pages]
    B --> D[Tesseract OCR]
    D --> E[Word boxes]
    E --> F[Invisible PDF text]
    C --> G[PDF]
    F --> G
    H[Owner label / QR] --> G
```

## CI/CD

GitHub Actions `CI` は次を実行します。

- `ruff check .`
- `pytest`
- `ai-pdf-capture demo --output-dir outputs/demo`
- `outputs/demo` をArtifactとしてアップロード

実画面キャプチャはGUIセッションが必要なためCIでは行いません。CIではドライラン画像からPDF生成までを検証します。

## 今後の拡張案

- 矩形選択UI
- 重複ページ検出による自動停止
- PDF分割出力
- OCRmyPDF連携モード
- Playwright/Seleniumによる許可されたWeb資料のブラウザ自動キャプチャ
- 社内監査ログ出力
