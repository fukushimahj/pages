# 巨大分子雲(GMC)計算

一様密度球+初期乱流速度場を初期条件に星団形成シミュレーションを実行する設定。

## 計算の実行まで

コンパイル方法などはこれまでと同じ。
ただし、初期の乱流速度場のデータ(`turb.d`)をダウンロードして設定する必要がある。
このファイルは[ここ](https://www.dropbox.com/scl/fi/h3f9rvfc4mlommvgu7yw8/turb.d?rlkey=72c1zakllpkeba71ghpmoi9x2&st=41hha76z&dl=0)からダウンロード可能です。

GMC計算固有のパラメータとして、`model.hpp`内の名前空間 modelParameter内に

```
// Turbulent sphere models
constexpr REAL Rcl            = 3.e0*unit::cgs_pc/unit::Unit_l;   // radius of cloud
constexpr REAL Boxsize        = 4.e0*Rcl;                         // Boxsize
constexpr REAL Mcl            = 1.e3*unit::cgs_msun/unit::Unit_m; // cloud mass
constexpr REAL alpha          = 1.e0;                             // virial parameter
constexpr REAL T0             = 10.e0;                  // gas temperature     [K]
constexpr REAL cs_HI          = unit_func::sqrt(unit::cgs_kb*T0/(unit::cgs_mh*(1.e0+4.e0*unit::cgs_yHe)/(1.e0+unit::cgs_yHe)))/unit::Unit_v;   // isothermal sound speed of HI
constexpr REAL rho_ext        = 1.e-4;
```

という変数が追加で設定されている。
これらは、

`Rcl` ガス球の半径

`Boxsize` 計算領域のサイズ (実際はこれの2倍の長さをもつ立方体が設定される)

`Mcl` ガス球の質量

`alpha` virial parameter (乱流強度)

`T0` 初期のガス温度

`cs_HI` 初期のガスの音速

`外部領域の密度`　ガス球と比べて何倍の密度のガスを設置するか？

`model.hpp`の他の設定方法については、[こちら](model.md)をご覧ください。

## 図の作成

GMC計算では、基本的にAMRのcell情報をすべて書き出す、`vr*`形式でデータが出力されています。
これを図にするためには、一様格子に変換してから図を作成します。

一様格子データの作成については、以下のコマンドから行います。

```
julia julia/convert_hdf5.jl
```

このコードを実行すると、h5というディレクトリの中に、hdf5 形式のファイルが生成されます。
そして、

```
julia julia/plot_h5.jl
```

を実行すると、図がgraph_sigというフォルダーの中に生成されます。
図の可視化に関しては、[こちら](outputdata.md)にも解説を載せています。

<br>
[マニュアルへ戻る](sfumato_manual.md)
