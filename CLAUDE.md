# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Japanese-language technical book project: "理論計算機科学教本 - コンピュータサイエンス基礎理論"

## Book Framework Migration

**IMPORTANT**: This book has been migrated to **book-formatter**.

- ✅ **Current**: Uses book-formatter system

## Key Commands and Workflows

### Development
```bash
npm start                    # Start Jekyll development server
npm run build               # Build the book for production
npm run preview             # Local preview of built book
npm run deploy              # Deploy to GitHub Pages
```

### Content Management
```bash
npm run lint                # Check markdown formatting
npm run check-links         # Validate internal links
npm test                    # Run all tests (lint + links)
npm run clean               # Clean build artifacts
```

## SVG図表作成ガイドライン

**重要**: このプロジェクトでは学術品質のSVG図表を推奨しています。

### 基本方針
- **学術レベル**: 論文・教科書レベルの視覚品質
- **アクセシビリティ**: WCAG AA準拠
- **日本語対応**: Unicode対応とフォント最適化
- **ベクター形式**: 倍率非依存の高品質表示

### 実績
- **34+ SVG図表作成完了** (全12章対応)
- **Mermaid→SVG完全移行達成**
- **理論計算機科学分野の複雑な概念の視覚化**

詳細な作成手法は [SVG_CREATION_GUIDE.md](SVG_CREATION_GUIDE.md) を参照してください。

## Contact Information

**Author**: ITDO Inc.（株式会社アイティードゥ）  
**Email**: knowledge@itdo.jp  
**GitHub**: [@itdojp](https://github.com/itdojp)
