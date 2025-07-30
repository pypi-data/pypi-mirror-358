# collect-license

pipインストールされたパッケージのライセンスファイルを収集するモジュールです。
pip-licensesを使用します。

## 動作確認OS

- `Windows 11 Pro`

## インストール方法

``` cmd or bash
pip install collectlicense
```

## 実行方法

``` cmd or bash
python -m collectlicense --out .licenses --clear
```
- --out：収集したライセンスファイルの保存先ディレクトリ
- --clear：--outで指定したディレクトリを削除してから収集する


## ソースから実行する方法

``` cmd or bash
git clone https://github.com/hamacom2004jp/collect-license.git
cd collect-license
python -m venv .venv
.venv\Scripts\activate
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
python -m collectlicense
deactivate
```

## pyplにアップするための準備

``` cmd or bash
python setup.py sdist
python setup.py bdist_wheel
```

- pyplのユーザー登録【本番】
  https://pypi.org/account/register/

- pyplのユーザー登録【テスト】
  https://test.pypi.org/account/register/

- それぞれ2要素認証とAPIトークンを登録

- ホームディレクトリに```.pypirc```を作成
``` .pypirc
[distutils]
index-servers =
  pypi
  testpypi

[pypi]
repository: https://upload.pypi.org/legacy/
username: __token__
password: 本番環境のAPIトークン

[testpypi]
repository: https://test.pypi.org/legacy/
username: __token__
password: テスト環境のAPIトークン
```

- テスト環境にアップロード
  ```.pyplrc```を作っていない場合はコマンド実行時にusernameとpasswordを要求される
  成功するとURLが返ってくる。
``` cmd or bash
twine upload --repository testpypi dist/*
```
- pipコマンドのテスト
``` cmd or bash
pip install -i https://test.pypi.org/simple/ collectlicense
```

- 本番環境にアップロード
``` cmd or bash
twine upload --repository pypi dist/*
```
