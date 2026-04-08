# 環境設定

環境設定は、`Configuration.defs`で行う。

```
#################################################
##                                             ##
##             Configuration file              ##
##                                             ##
#################################################
SFUMATO_DIR   = /home/hogehoge/SFUMATO_sharp
SRC_DIR       = $(SFUMATO_DIR)/src
WORK_DIR      = $(SFUMATO_DIR)/works/GMC
DATA_DIR      = $(WORK_DIR)/data
CUDA_INSTALL_PATH = /usr/local/cuda

GENCODE_SM80    := -gencode arch=compute_80,code=sm_80
GENCODE_SM90    := -gencode arch=compute_90,code=sm_90
GENCODE_FLAGS   := $(GENCODE_SM80) $(GENCODE_SM90)


#################
# Compiler     ##
#################
NVCC  = nvcc
CC    = mpic++

CFLAGS     = -std=c++11
MPICFLAGS  = -I${MPI_HOME}/include
CUDACFLAGS = -I${CUDA_INSTALL_PATH}/include

NVCCFLAGS   = $(GENCODE_FLAGS) --default-stream per-thread -std=c++11 -lmpi -lcudadevrt -lcudart -Xcompiler -fopenmp
CUDALDFLAGS = -I${CUDA_INSTALL_PATH}/include -L${CUDA_INSTALL_PATH}/lib64 -lcudart -lgomp

################
# Options     ##
################
INCLUDE_SELF_GRAVITY = 1      # if 1 == ON
INCLUDE_CHEMISTRY    = 1
INCLUDE_RADTR        = 1
```

<br>
各項目の詳細は以下のようになります(Compiler option除く)。

`SFUMATO_DIR` 計算実行するSFUMATOのdirectoryへの絶対パス

`SRC_DIR SRC` directoryへの絶対パス。異なるsrcで計算したい場合は変更する

`WORK_DIR` 計算を実行するdirectoryへの絶対パス

`DATA_DIR` データを保存するdirectoryへの絶対パス

`CUDA_INSTALL_PATH` cudaのインストール先、cfcaのGPUなど、指定しなくて良い場合もある

`GENCODE_FLAGS` NVIDIAのGPUで実行する際に計算を実行するGPUにあったarchitecturesを指定する。詳細については こちら を確認して、計算実行するGPUにあったものを選択する。

`INCLUDE_SELF_GRAVITY` 自己重力を含める場合は1を指定　(それ以外は0)

`INCLUDE_CHEMISTRY` 化学計算を含める場合は1を指定　(それ以外は0)

`INCLUDE_RADTR` 輻射輸送を含める場合は1を指定　(それ以外は0)

`GETCODE_FLAGS` 使用するGPUごとに、どの世代のGPUを指定する必要がある。詳細は、[こちら](https://arnon.dk/matching-sm-architectures-arch-and-gencode-for-various-nvidia-cards/)を参照してください。

# 各スパコンでの環境設定

各スパコンでの設定方法に関しては、`./works/Configs/` 内に個別に記載してあるので、参考にしてください。
設定方法でもしより良いものや最新のバージョンに変更が必要そうなものがある場合にはご連絡ください。

## 更新日時

- miyabi: 260407
- g01: 260408

<br>
[マニュアルへ戻る](sfumato_manual.md)
