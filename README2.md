# ZundamonGPTonYouTube
[English](README.md) | 日本語<br><br>
かしこいずんだもんがYouTubeのチャット欄にGPTずのーでこたえてくれるプログラムです。
<br><br>

## はじめに
- このアプリケーションは日本製のボイスジェネレータ VOICEVOX に依存しているため日本語限定ですが、ソースコードをMITライセンスで公開しているので、自由にカスタマイズできます。

## 動作環境
- Windows OS (10 にて動作確認済)
- .Net Framework v.4 (v4.7.2 にて動作確認済)
- [VOICEVOX](https://voicevox.hiroshiba.jp/) のインストールが必要 (v.0.14.6 にて動作確認済)

    コアモジュールはPythonで作成されているため、その他の複数のOSやボイスジェネレータに適応可能です。<br>
    キャラクター表示ウィンドウだけはC#で作られているためWindowsに強く依存しています。キャラクター表示ウィンドウについてもPythonへの移植を計画しています。
<br><br>

## 機能
- YouTubeチャットを自動で拾い、それに対するChatGPTの回答をずんだもんの声で読み上げます。 <br>
日本語以外のメッセージに対しても日本語で返答します。
- YouTubeのすべてのチャットメッセージ、ピックアップされたメッセージ、ピックアップされたメッセージへの回答コメントを表示できます。
- ずんだもんの立ち絵を背景透過で表示できます。
- 声や立ち絵はずんだもん以外に変更することも可能です。<br>
[![GttsAIStreamer sample](ReadMeParts/zundamon_thumbnail.png)](https://www.youtube.com/embed/7GgssTTo2-c)

## 使い方
- [VOICEVOX](https://voicevox.hiroshiba.jp/) をリンク先からインストール。
- OpenAIのapi-keyを取得。 取得方法は [ここ(英語)](https://www.howtogeek.com/885918/how-to-get-an-openai-api-key/) か [ここ(日本語)](https://laboratory.kazuuu.net/how-to-get-an-openai-api-key/) を参照してください。
- .exe ファイルから実行する場合
    - [ここ](https://github.com/GeneralYadoc/ZundamonGPTonYouTube/releases) をクリックして最新版をダウンロード。
    - "ZundamonGPTonYouTube.zip" ファイルを解凍。
    - "ZundamonGPTonYouTube" フォルダを開き、 ZundamonGPTonYouTube.exe ファイルをダブルクリック。
- ソースコードから実行する場合
    - ffmpegをインストール。<br>
      <b>Linux の場合：</b> 以下のコマンドを実行。
      ```ffmpeg installation for Linux
      $ sudo apt-get install ffmpeg
      ```
  
      <b>Windows の場合：</b>[ここ](https://github.com/BtbN/FFmpeg-Builds/releases) にアクセスして、'\*-win64-gpl.zip' をダウンロード。<br>
      zip ファイルを解凍し、中の3つの exe ファイル（ffmpeg.exe, ffprobe.exe, ffplay.exe）を、ZundamonGPTonYouTube 実行フォルダ、もしくはパスの通ったフォルダに置く。<br>
      <br>
      <b>Mac の場合：</b>[ここ](https://brew.sh/)にアクセスし、記載されているコマンドを端末に貼り付けて Enter を押下。<br>
      以下のコマンドを実行。
      ```
      brew install ffmpeg
      ```
    - リポジトリをクローン。<br>
        ```clone
        git clone https://github.com/GeneralYadoc/ZundamonGPTonYouTube.git
        ```
    - ZundamonGPTonYouTube ディレクトリに移動。
        ```mv
        mv ZundamonGPTonYouTube.
        ```
    - アプリケーションをインストール。
        ```install
        pip install .
        ```
    - アプリケーションを開始。
        ```
        python3 ZundamonGPTonYouTube.py
        ```
- 対象 YouTube ストリームの Video ID をチェック。<br>
    ![](ReadMeParts/video_id.png)
- スタートウィンドウの Video ID 欄に YouTube ストリームの Video ID を記入。 (Ctrl+V で貼り付けできます)
- スタートウィンドウの API Key 欄に OpenAI の api key を記入。 (Ctrl+V で貼り付けできます)
- "すたーと" ボタンをクリック。<br>
    ![](ReadMeParts/start_form.png)

### 注意
- OpenAI の apikey と Video ID は "variable_cache.yaml" という名前のファイルに記録され、2回目以降の入力を省略できます。
- OpenAI の api key が流出しないよう、"variable_cache.yaml" の扱いには気をつけてください。
<br><br>

## 画面構成

### メインウィンドウ
- "ちゃっと" ボタンを押すことでチャット欄ウィンドウの、"しつもん" ボタンを押すことで質問ウィンドウの、"こたえ" ボタンを押すことで回答ウィンドウの、"立ち絵" ボタンを押すことで立ち絵ウィンドウの表示・非表示を切り替えることができます。
- ウィンドウ下部のスライドバーで音声ボリュームを調整できます。
- スライドバーの右隣にあるテキストボックスに値を記入し、エンターキーを押下する方法でも、音量変更が可能です。 
- ウィンドウ右上の "x" ボタンをクリックすることで、アプリケーションを終了できます。<br>
    ![](ReadMeParts/main_window.png)

### 立ち絵ウィンドウ
- 設定ファイルに画像ファイルパスを指定することで好きなイラストを表示できます。
- 立ち絵をダブルクリックすることで、背景の透過・不透過を切り替えることができます。
- キャラクターのサイズは背景不透明モードのときに変更することができます。キャラクターのサイズを調整した後に背景を消してください。
- ウィンドウの最小化についても、実行できるのは背景不透明モードのときです。<br>
- このウィンドウを閉じてもアプリケーションは動作し続けますので、不要な場合は閉じてください。<br>
    ![](ReadMeParts/zundamon_opaque_transparent.png)

### YouTubu チャットウィンドウ
- ほぼすべての YouTube チャットコメントがここに表示されます。
- 絵文字のみで構成されているコメントは無視されます。
- ポーリング間隔の隙間に入ったコメントは漏れることがあります。
- メッセージ領域をダブルクリックすることで、ウィンドウ枠の表示・非表示を切り替えることができます。
- ウィンドウをリサイズするときはウィンドウ枠を表示させてください。
- このウィンドウを閉じてもアプリケーションは動作し続けますので、不要な場合は閉じてください。<br>
    ![](ReadMeParts/monitor_window.png)

### 質問ウィンドウ
- ChatAI に回答させるためにピックアップしたすべてのコメントがここに表示されます。
- メッセージ領域をダブルクリックすることで、ウィンドウ枠の表示・非表示を切り替えることができます。
- ウィンドウをリサイズするときはウィンドウ枠を表示させてください。
- このウィンドウを閉じてもアプリケーションは動作し続けますので、不要な場合は閉じてください。<br>
    ![](ReadMeParts/ask_window.png)

### 回答ウィンドウ
- ピックアップされたメッセージに対する ChatAI の回答がここに表示されます。
- メッセージ領域をダブルクリックすることで、ウィンドウ枠の表示・非表示を切り替えることができます。
- ウィンドウをリサイズするときはウィンドウ枠を表示させてください。
- このウィンドウを閉じてもアプリケーションは動作し続けますので、不要な場合は閉じてください。<br>
    ![](ReadMeParts/answer_window.png)<br>

### 注意
 - 以下のウィンドウは、外部アプリケーション "VoiceVox" のものです。<br>
 ずんだもんの音声再生に必要ですので、閉じないでください。（隠したい場合は最小化してください）
    ![](ReadMeParts/voicevox_window.png)<br>
<br><br>

# 設定

アプリケーションの .exe ファイルと同じ階層にある設定ファイル "setting.yaml" を用いて、設定を変更することが出来ます。
```setting.yaml
# VoiceVoxの設定
voicevox_path: ''

# チャット欄ウィンドウの設定
display_user_name_on_chat_window: 'True'
chat_window_title: 'ちゃっとらん'
chat_window_size: '350x754'
chat_window_padx : '9'
chat_window_pady : '9'
chat_window_color: '#ffffff'
chat_font_color: '#000000'
chat_font_size: '10'
chat_font_type: 'Courier'
chat_rendering_method: 'normal'

# 質問ウィンドウの設定
display_user_name_on_ask_window: 'False'
ask_window_title: 'ぐみんのしつもん'
ask_window_size: '500x250'
ask_window_padx : '9'
ask_window_pady : '9'
ask_window_color: '#354c87'
ask_font_color: '#ffe4fb'
ask_font_size: '12'
ask_font_type: 'Courier'
ask_rendering_method: 'refresh'

# 回答ウィンドウの設定
answer_window_title: 'てんさいずんだもんのこたえ'
answer_window_size: '500x450'
answer_window_padx : '9'
answer_window_pady : '9'
answer_window_color: '#ffe4e0'
answer_font_color: '#004cF7'
answer_font_size: '13'
answer_font_type: 'Helvetica'
answer_rendering_method: 'incremental'

# AIの設定
model: 'gpt-3.5-turbo'
max_tokens_per_request: 1024
ask_interval_sec: 20.0

# 回答キャラクターの設定
speaker_type: 1
volume: 100
system_role: 'あなたはユーザーとの会話を楽しく盛り上げるために存在する、日本語話者の愉快なアシスタントです。'
image_file: zundamon.gif
```

- VOICEVOX を標準の場所にインストールしている場合は、"voicevox_path" を空欄のままにしておくことができます。
- "model" の値を変更することで、AI のモデルを変更できます。
- "speaker_type" の値を変更することで、回答の声を変更できます。
- "image_file" に記載のパスを変更することで、キャラクター画像を変更できます。
<br><br>
# ライセンス
- このアプリケーションはMITライセンスですので、自由にカスタマイズ可能です。
- リリースパッケージに含まれる ffmpeg の実行ファイル一式は LGPL ライセンスです。
<br><br>
# リンク集
- [Pixiv page of 坂本アヒル](https://www.pixiv.net/users/12147115) &emsp; GIF アニメーションに使用したずんだもん立ち絵静止画の入手元。
- [ChatAIStreamer](https://github.com/taizan-hokuto/pytchat) &emsp; YouTube チャットに対するChatGPTの音声付き回答を取得することができる Python ライブラリ。
