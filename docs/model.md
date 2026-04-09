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
基本的には、GPUの関数はCUDAで記載しているが、　AMDを使用する場合にはHIP用の関数にmacroを使ってこれらの関数を設定している(./src/gpu_vendors.cuhを参照).

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

/*------------------------*/
/*      GPU check         */
/*------------------------*/
#define CHECK_GPU               YES
#define OUTPUT_GPUPROP          YES

/*------------------------*/
/*  Memory optionas       */
/*------------------------*/
//#define MEMORY_ON_HOST

/*------------------------*/
/*     DEBUG              */
/*------------------------*/
#define KERNEL_DEBUG_MODE       OFF


```
