# model.hppの設定

計算の設定は主に、`model.hpp`で行います。
以下に主要なオプションについて記載します。
ただ、問題ごとに固有の名前空間の変数がついている場合があります。

## モデルの名前

```
#define MODEL_NAME      "GMC"          // model name
```

計算には影響しない

## GPU のvendorの選択

```
/*------------------------*/
/*       GPU TYPES        */
/*------------------------*/
#define NVIDIA_GPU_ON  0
#define AMD_GPU_ON     1
#define GPU_TYPE_USED   NVIDIA_GPU_ON
```

現状はNVIDIAかAMDに対応.
基本的には、GPUの関数はCUDAで記載しているが、AMDを使用する場合にはHIP用の関数にmacroを使ってこれらの関数を設定している(./src/gpu_vendors.cuhを参照).

## MPI & OpenMP並列

```
/*------------------------*/
/*   SYSTEM OPTION        */
/*------------------------*/
#define NPE 4 // number of device


// MPI PARALLEL
#define PARALLEL_MPI      /* MPI */

// openmp
#define PARALLEL_OMP      /* OMP */
#define OMP_NUM_THREADS_SINK  10    // number of thread for sink
```

`NPE` MPI並列数, 1GPUにつき、1CPUランクを使用する設計。

`PARALLEL_MPI` MPI並列機能をONにする (現状このマクロが有効とする必要あり。今後, MPIを使用せずCUDA/HIP単独で実行可能にする予定)

`PARALLEL_OMP` OpenMP機能をONにする (化学計算でCPU 機能もONにした場合のみ使用している)

`OMP_NUM_THREADS_SINK` 使用していないマクロ (後日削除予定)

## GPU関連のエラー探査

```
/*------------------------*/
/*      GPU check         */
/*------------------------*/
#define CHECK_GPU               YES
#define OUTPUT_GPUPROP          YES

/*------------------------*/
/*     DEBUG              */
/*------------------------*/
#define KERNEL_DEBUG_MODE       OFF
```

`CHECK_GPU` macro `CHECK`でcuda kernelのエラー探査を実施　(./src/gpulib.cuhで定義)

`OUTPUT_GPUPROP` 使用するGPUの性能を計算の開始時に表示

`KERNEL_DEBUG_MODE` 実行中のkernelをターミナル上で表示。一部kernelについては、実行後にcudaDeviceSyncrhonize()を実行し、完了を待つ仕様になっている。

## メモリーに関して

```
/*------------------------*/
/*  Memory optionas       */
/*------------------------*/
//#define MEMORY_ON_HOST
```

`MEMORY_ON_HOST` このマクロが有効な場合、グリッドの情報はunified memoryとして、ホスト上に確保される。無効な場合はデバイス上で確保する。

## MPIのOption関連

```
/*------------------------*/
/*    option for MPI      */
/*------------------------*/
#define PRIMARY_RANK   0 // primary rank

#define FL4OPENMPI     0
#define FL4MVAPICH2    1
#define FL4INTEL       2

#define MPI_OPTION   FL4OPENMPI
//#define PACKARR_MANAGED           // 転送用のデータはcudaMallocManagedでホスト上に確保される
```

`PRIMARY_RANK` primary rankの設定。特別な理由がない以外は0にする。

`MPI_OPTION` 基本は、openmpiの利用を想定しているが、他のmpiを利用したい場合は変更する (MPIとGPUを組み合わせる際の起動時の処理と関連)

`PACKARR_MANAGED` MPI通信用のメモリーの確保の方法を指定。基本はデバイス上で確保するが、このマクロを有効にすると、unified memoryとして確保する。miyabiでの実行時には、このマクロを有効にしたほうがいいかも(コンパイラー関連のエラーを踏む可能性があり、回避方法があるみたいだが、未対応)

## IO関連

```
/* ---------------------- */
/*          IO            */
/* ---------------------- */
#define BLOCKING_IO            OFF
#define OUTPUT_INTERMEDIATE_FILE
#define STEP_INTERMEDIATE_FILE   10000
#define OUTPUT_DATA_CONSTANT_TIME
```

`BLOCKING_IO` ONの場合、計算引き継ぎ用のファイルの出力時にrankごとに順番に出力。OFFの場合は同時に出力する。

`OUTPUT_INTERMEDIATE_FILE` 有効の場合、`STEP_INTERMEDIATE_FILE`で指定されたステップごとに、計算引き継ぎ用のデータを出力する。

`OUTPUT_DATA_CONSTANT_TIME` 可視化用のデータを一定時間ごとに出力するオプション (adaptive timestep時のみ有効, 出力感覚はmodelParameter::Dtime_ODCTで指定)

データ出力や引き継ぎ・可視化用のデータ出力に関しては[こちら](outputdata.md)もご覧ください。

## pinned memory 関連

```
/* ---------------------- */
/*    pinned memory       */
/* ---------------------- */
//#define WITHOUT_PINNED_MEMORY
```

pinned memoryが枯渇する場合に対応するオプションを設立中. (あんまり使える場面ないかも...)

## Timestep

```
/*------------------------*/
/*  option for timestep   */
/*------------------------*/
#define SINGLE_STEP
```

`SINGLE_STEP` このオプションが有効時にsingle timestep, 無効時にadaptive timestepモードになる。

## グリッド構造

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

#define NL           20       // maximum level of refinement
```

`N_GHOST_CELL 2` ghost cellの数

`Ni, Nj, Nk` 各グリッドのx, y, z方向の数、現状同じ数になることを仮定している

`NGI_BASE, NGJ_BASE, NGK_BASE` Level=0におけるグリッドの数

`NL` refinement levelの最大値

## 流体関連

```
/* ---------------------- */
/*        timestep        */
/* ---------------------- */
#define CFL_HYDRO    0.7

/* ---------------------- */
/*         hydro          */
/* ---------------------- */
#define FLUX_ROEM2             // use numerical flux RoeM2

/*------------------------*/
/*  boundary condition    */
/*------------------------*/
#define bd_cond_OUTFLOW     0
#define bd_cond_PERIODIC    1
#define BDCONDITION         bd_cond_OUTFLOW
//#define ZERO_AVERAGE_DENSITY   // used in fmg

/*------------------------*/
/*  eos solver            */
/*------------------------*/
#define EOS_ADIABATIC_KIM   0
#define EOS_HLLC_minus      1
#define EOS_SOLVER EOS_HLLC_minus
```

`CFL_HYDRO` timestepの大きさを決定

`FLUX_ROEM2` H-correction, Kim+2003, JCP, 185, 342を導入　(これを無効にするオプションは現在準備中)

`BDCONDITION` 境界条件, 自由端(bd_cond_OUTFLOW)と周期境界(bd_cond_PERIODIC)条件を用意

`EOS_SOLVER` 流体スキーム

## refinement 関連

```
/*------------------------*/
/*  refinement            */
/*------------------------*/
#define REFINEMENT          ON
#define REFINEMENT_NESTED   ON
#define REFINEMENT_JEANS    ON

#define LMAX0_NEST          1        // level of nsted grid
#define JEANS_CONST         16       // cell number to resolve a jeans length

#define MERGE_KYOUDAI_MAGO           // if this macro is defined, existence of ancle grid is ensured.
#define REFINE_NANAME                // if this macro is defined, diagonal grid is also refined
```

`REFINEMENT` ONの場合、refinement機能が有効になる, OFFの場合は一様格子が採用される

`REFINEMENT_NESTED` Nested grid構造を設置

`REFINEMENT_JEANS` Jeans長によるrefinementを有効にする

`LMAX0_NEST` nested gridの最大level

`JEANS_CONST` 1 Jeans長を何セルで解像するかを選択

## 自己重力

```
/*------------------------*/
/*  self gravity          */
/*------------------------*/
#define SELF_GRAVITY        ON
```

`SELF_GRAVITY` ONの場合、自己重力がONになる

## 計算Floor設置　& Nan検知

```
/* ---------------------- */
/* rescue options         */
/* ---------------------- */
#define RESCUE_NANINF       ON
#define RESCUE_FLOOR        ON
```

`RESCUE_NANINF` ONの場合、Nanの検知を行う

`RESCUE_FLOOR` 密度、温度、速度に関してfloorを設置 (値は、名前空間　`modelParameter` で定義)

## 計算時間の測定

```
/* -----------------------*/
/*   count time*/
/* -----------------------*/
#define OUTPUT_CALTIME      ON
```

`OUTPUT_CALTIME` ONの場合、各パートの計算時間の測定を開始する

## 注意点

- オリジナル SFUMATOにあったグリッド数の上限値は撤廃.

<br>
[マニュアルへ戻る](sfumato_manual.md)
