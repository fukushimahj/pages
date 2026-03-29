
# スタートガイド

## ダウンロード

Githubからgitを使ってダウンロード可能です(現状はprivate repository)。

```
git clone git@github.com:fukushimahj/SFUMATO_sharp.git
```

## Directory

ディレクトリの構造は次のようになっています。

## SFUMATO_sharp ディレクトリ構造
```
SFUMATO_sharp/
├── src/                # ソースコード
├── julia/              # 解析用スクリプト・ファイル
├── Configs/            # 環境設定用ファイル
└── works/              # 各テスト計算を格納
    ├── shock_tube/     # 衝撃波管問題 (Shock tube)
    ├── HII/            # 電離領域の膨張 (HII region expansion)
    ├── BE/             # Bonnor-Ebert 球 (Bonnor-Ebert sphere)
    └── GMC/            # 巨大分子雲・星団形成 (Giant Molecular Cloud)
```
コードの実行に関しては、works内部にfolderを作成し、そこで計算を実行する設計になっています。

## 計算の実行までの流れ

shocktubeのテスト計算の実行までの流れを解説し、

### 環境設定
