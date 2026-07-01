# CODEX Instructions

このリポジトリは、許可された資料をAIに読み込ませやすいPDFへ変換するローカルツールです。

## 守ること

- DRM回避、コピー防止回避、規約違反を助ける機能を追加しない。
- 実画面キャプチャには `--acknowledge-compliance` 相当の明示確認を残す。
- CIはヘッドレス環境なので、実画面キャプチャではなく `demo` または `dry_run` を使う。
- OCRはTesseractが無い環境でも `--ocr` を使わなければ動く状態を保つ。
- 主要変更時はREADME、docs/architecture.md、docs/setup.mdを更新する。

## ローカル確認

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
ai-pdf-capture demo --output-dir outputs/demo
```

## 推奨Issue/PR方針

- バグ修正: 再現テストを追加
- 新機能: READMEに利用例を追加
- OCR/キャプチャ変更: 法令・規約遵守の注意書きを維持
