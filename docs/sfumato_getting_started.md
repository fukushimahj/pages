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
    ├── shocktube/      # 衝撃波管問題 (Shock tube)
    ├── HII/            # 電離領域の膨張 (HII region expansion)
    ├── BE/             # Bonnor-Ebert 球 (Bonnor-Ebert sphere)
    ├── GMC/            # 巨大分子雲・星団形成 (Giant Molecular Cloud)
    └── Configs/        # 各スパコンでのConfiguration.defsとmakefile
```

コードの実行に関しては、works内部にfolderを作成し、そこで計算を実行する設計になっています。

## 計算の実行までの流れ

shocktubeのテスト計算を通して、環境設定から計算実行、図示するところまでを解説します。

### 環境設定

まず、`./works/shocktube`へ移動し、`Configuration.defs`を開きます。

```
#################################################
##                                             ##
##             Configuration file              ##
##                                             ##
#################################################
SFUMATO_DIR   = /home/hogehoge/SFUMATO_sharp
SRC_DIR       = $(SFUMATO_DIR)/src
WORK_DIR      = $(SFUMATO_DIR)/works/shocktube
DATA_DIR      = $(WORK_DIR)/data

```

上で示すように、`SFUMATO_DIR`にSFUMATO_sharpへの絶対パスを設定してください。
環境設定の詳細については、[こちら](sfumato_configuration.md)もご覧ください。

### コンパイル & 実行

コンパイルは

```
make (並列でコンパイルしたい場合は make -j 12など)
```

問題がなければ、`sfumato` という実行ファイルが生成される。
計算の実行は次のコードにより実行する。

```
mpirun -np 1 ./sfumato 2>&1 | tee -a stdout
```

計算を実行すると、`./data/`内に、`cb*`というファイルが出力される。

### 計算結果を出力する

計算結果の可視化はすべて[julia](https://julialang.org/) を使用して実行します。
インストール方法などはこちらを参照してください。

```
julia julia/plot.jl
```

このコードにより以下のようなshocktube問題の結果が図示できれば、計算がうまくいっています。
<video controls width="800">

  <source src="https://fukushimahj.github.io/pages/movie/shocktube.mp4" type="video/mp4">
</video>

また、衝撃波管問題の解析解との比較用に、`./julia/shock_tube.jl` (解析解導出)と`./julia/shockbube.ipynb` (jupyterlabのファイル, 図示用)も用意しているので活用してください。

これで、一通りの計算までの流れについての説明は終わりです。各設定の詳細については、マニュアルのページからご覧ください。

<br>
[マニュアルへ戻る](sfumato_manual.md)
