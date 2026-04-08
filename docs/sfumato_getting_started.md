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

### 解像度を変更する

上の計算では、 $64^3$の一様格子を設置していましたが、これを変更してみます。
計算の設定の変更は主に、`model.hpp`で行います。
このファイルのgridという項目に、

```
/*------------------------*/
/*        grid            */
/*------------------------*/
#define N_GHOST_CELL 2        // number of ghost cell

#define Ni           8        // grid cell number
#define Nj           8
#define Nk           8

#define NGI_BASE     8
#define NGJ_BASE     8
#define NGK_BASE     8

#define NL           1       // maximum level of refinement
```

とあります。
SFUMATOが採用しているAMRは、`Ni` $\times$ `Nj` $\times$ `Nk`のブロック構造を単位として、空間上に格子を設置する方式を採用しています。
また、AMR機能がONとなるときは、一つのブロック構造を８分割して、セルサイズが$1/2$の８つのブロックを生成します。新しく生成されたブロックも`Ni` $\times$ `Nj` $\times$ `Nk`のセルを保持しています。
`NGI_BASE`, `NGJ_BASE`, `NGK_BASE`は最も粗いlevel (Level=0)で上のブロックを各方向に何個並べるかを指定します。
ですので、上記の場合は$64^3$の一様格子の設定となります。
例えば、これを

```
/*------------------------*/
/*        grid            */
/*------------------------*/
#define N_GHOST_CELL 2        // number of ghost cell

#define Ni           8        // grid cell number
#define Nj           8
#define Nk           8

#define NGI_BASE     16
#define NGJ_BASE     16
#define NGK_BASE     16

#define NL           1       // maximum level of refinement
```

とすると、$128^3$の計算が可能となります。
ヘッダーファイルを変更した場合は、`make clean` & `make`を再度実行する必要があります。

この際、出力されるデータのサイズについても変更する必要があります。
`model.hpp`の`modelParameter`という名前空間に、`ncout`という変数があります。
これは、出力されるデータのサイズを制御するパラメータで、計算で用いる格子サイズと合わせて`constexpr INT32 ncout = 128; `へ変更する必要があります。
あとの計算実行から、図に出力するまでの作業は同じです。

### Nested gridで計算する

次に、AMR のrefinement機能をONにして、nested gridでの計算を実行してみます。
これも`model.hpp`の以下の機能を編集します。

```
/*------------------------*/
/*        grid            */
/*------------------------*/
#define N_GHOST_CELL 2        // number of ghost cell

#define Ni           8        // grid cell number
#define Nj           8
#define Nk           8

#define NGI_BASE     8
#define NGJ_BASE     8
#define NGK_BASE     8

#define NL           1       // maximum level of refinement


/*------------------------*/
/*  refinement            */
/*------------------------*/
#define REFINEMENT          OFF
#define REFINEMENT_NESTED   OFF
#define REFINEMENT_JEANS    OFF

#define LMAX0_NEST          2        // level of nsted grid
#define JEANS_CONST         10       // cell number to resolve a jeans length

#define MERGE_KYOUDAI_MAGO           // if this macro is defined, existence of ancle grid is ensured.
#define REFINE_NANAME                // if this macro is defined, diagonal grid is also refined
```

まず、gridの項目の`NL`はAMR機能をONにしたときの最大レベルを指定します。NLが１の場合は、一様格子を示します。
`REFINEMENT`を`ON`にすると、refinement機能が有効となります。
現状、nested grid構造を設置する機能と、Jeans長を基準にAMR機能をONにする機能が用意されています。
nested gridを設置する場合は、`REFINEMENT_NESTED`を`ON`にします。また、`LMAX0_NEST`はnested gridを設置する最大levelを指定します(NLがこの値より大きい場合に有効となる)。
上の説明をまとめると、次のように`model.hpp`を編集します。

```
/*------------------------*/
/*        grid            */
/*------------------------*/
#define N_GHOST_CELL 2        // number of ghost cell

#define Ni           8        // grid cell number
#define Nj           8
#define Nk           8

#define NGI_BASE     8
#define NGJ_BASE     8
#define NGK_BASE     8

#define NL           4 // 1      // maximum level of refinement


/*------------------------*/
/*  refinement            */
/*------------------------*/
#define REFINEMENT          ON
#define REFINEMENT_NESTED   ON
#define REFINEMENT_JEANS    OFF

#define LMAX0_NEST          4        // level of nsted grid
#define JEANS_CONST         10       // cell number to resolve a jeans length

#define MERGE_KYOUDAI_MAGO           // if this macro is defined, existence of ancle grid is ensured.
#define REFINE_NANAME                // if this macro is defined, diagonal grid is also refined
```

ちなみに、計算結果の出力は`cb*`という名前のファイルとして生成されます。
これは計算領域を一様格子、もしくはrefinmentが起こっている場合には、nested grid構造に計算結果からデータを再構築する仕様になっています。
他にも`vr*`という、すべての格子データを出力する形式もあります。こちらはAMR機能をONにして計算する際に便利です。
データの出力形式とその制御に関しては、[こちら](outputdata.md)で解説します。

これで、一通りの計算までの流れについての説明は終わりです。各設定の詳細については、マニュアルのページからご覧ください。

<br>
[マニュアルへ戻る](sfumato_manual.md)
