## 51% Attack

これは**51% Attack**の**Toy Program**です。

最低限の機能を持った独自の仮想通貨(*Virtual Currency*)を使ってブロックチェーンのルールを検証します。

以下の特徴があります。

- Flaskを使って提供されるAPIを用いて操作します。

- 楕円曲線暗号を用いて電子署名を行います。パラメータはビットコインの値を参考にしています。

- 3つのノードのうち1つだけ非公開にしてマイニングさせます。

- 非公開ノードは公開ノードの2.5倍のスピードでマイニングします。

- 公開ノードがマイニングを開始してしばらくたった後で非公開ノードはマイニングを開始します。


### File
main.py : 複数のプロセスを使って51% Attackの検証を行う  
virtual_currency.py : 仮想通貨の機能を持ったブロックチェーンのクラスとFlaskを使ったAPIの提供  
digital_signiture.py : 電子署名(楕円曲線DSA)の関数  
ellipti_curve.py : 楕円曲線上の演算のためのクラス  
galois_field.py : ガロア体(有限体)の演算のためのクラス  

### Class
VC : 仮想通貨(*Virtual Currency*)を定義したクラス  
EC : 楕円曲線(*Ellipti Curve*)上の演算のためのクラス  
GF : ガロア体(*Galois Field*)(有限体)の演算のためのクラス  

### Usage
以下のコマンドを入力。
```
python3 main.py
```
APIからのメッセージとnodeにおけるチェーンの長さとコインの保有量を表示されます。
成功メッセージが表示されたあとはCtrl+Cで終了します。


### Reference
ブロックチェーン部分の実装には[こちら](https://qiita.com/hidehiro98/items/841ece65d896aeaa8a2a)を参考にしました。