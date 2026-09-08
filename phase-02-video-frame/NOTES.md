# Phase 2 学習記録: Video Frameを理解する

## コード全体の流れ（[src/main.ts](src/main.ts)）

```
Startを押す
   ↓
getUserMedia(constraints) で MediaStream を取得
   ↓
video.srcObject = stream
   → ここから先、videoの映像更新はブラウザの内部実装が勝手にやってくれる(後述)
   ↓
canvas.width/height を video.videoWidth/videoHeight に合わせる
   → 希望した解像度(ideal)と実際の解像度がズレることがあるため
   ↓
drawFrame() ループを開始(requestAnimationFrameで自分自身を再予約し続ける)
   → videoに今映っている1枚を、毎回canvasにdrawImageでコピーする
   → これを繰り返すことで「動画」に見える
```

## `<canvas>` と `getContext("2d")`

```
<canvas> → ただの空の描画エリア。何かを自動で表示する機能は一切ない
getContext("2d") → 描画のための道具セット(CanvasRenderingContext2D)を取得する
                    ("webgl"を指定すれば3D描画用の別の道具セットが返る)
```

`<video>`と違い、canvasは1ピクセルたりとも自動更新されない。「映像とは、色のついた点の集まりを描き変え続けているだけ」ということを体感するために、あえて自動化されていないcanvasを使っている。

## `drawImage` と 描画ループ

```typescript
ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
```
「映像ソース(video)に今映っている1枚の静止画を、canvasにコピーする」処理。これ単体では1回きりのコピーにしかならない。

```typescript
function drawFrame(): void {
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  drawnFrameCount++;
  animationFrameId = requestAnimationFrame(drawFrame);
}
```

`requestAnimationFrame(drawFrame)`は「次の画面描画タイミングの直前にdrawFrameを呼んで」という予約。`drawFrame`が自分自身を再予約し続けることで、自己駆動のループになる。これが「動画は静止画の高速な連続」であることの実物。

`animationFrameId`はその予約を識別するID。`cancelAnimationFrame(animationFrameId)`でその**次の**予約だけをキャンセルすると、連鎖が途切れてループ全体が止まる（`drawFrame`が呼ばれなくなる→次のrequestAnimationFrameも呼ばれなくなる）。グレースケール処理の直前で`stopDrawing()`を呼んでいるのは、ループを止めないと次の描画タイミングで元のカラー映像に即座に上書きされてしまうため。

## FPS計測の仕組み(2つの独立したタイマー)

```
時計①: requestAnimationFrame
   ディスプレイの更新タイミングに合わせてdrawFrameを呼び続ける
   呼ばれるたびに drawnFrameCount++

時計②: setInterval(..., 1000)
   1秒ごとに「直近のdrawnFrameCount」を画面に表示し、0にリセットする
   → これが実測FPS(actualFps)になる
```

`getUserMedia`に`frameRate: { ideal: N }`と希望した値(configuredFps)と、実際に描画された回数(actualFps)は必ずしも一致しない。カメラの性能やOSの都合、ディスプレイのリフレッシュレートなどによってズレることがある、というのを実際に数値で観察できる。

## ピクセルとImageData

```
1ピクセル = 画面を構成する1つの点。R(赤)/G(緑)/B(青)/A(透明度)の4つの数値(各0〜255)で色を表現する
画像・動画 = 大量のピクセルそれぞれに、この4つの数値を割り当てただけのもの
```

```typescript
const imageData = ctx.getImageData(x, y, w, h); // 指定範囲のピクセルを取り出す
imageData.data // Uint8ClampedArray: [R,G,B,A, R,G,B,A, ...] の1次元配列
ctx.putImageData(imageData, 0, 0); // 書き換えたデータを画面に描き戻す
```

- `getImageData`はcanvasの今の見た目を**独立したデータとしてコピー**する。この時点でデータと画面は切り離される。
- `imageData.data`をfor文で直接書き換えても、画面(canvas)にはまだ反映されない。
- `putImageData`を呼んで初めて、書き換えたデータが画面に焼き付けられる。

### グレースケール処理の中身

```typescript
for (let i = 0; i < pixels.length; i += 4) {
  const gray = (pixels[i] + pixels[i + 1] + pixels[i + 2]) / 3; // RGBの平均
  pixels[i] = pixels[i + 1] = pixels[i + 2] = gray; // R,G,Bを平均値に統一
  // pixels[i+3](A)は触らない
}
```
1ピクセルがRGBAの4要素なので4つ飛ばしでループ。RGBを同じ値に揃えると色味が消えてグレーに見える、という単純な原理。

## 参照とコピー(重要な性質)

```typescript
const pixels = imageData.data;
```
これは配列の**コピーではなく参照**。`pixels`と`imageData.data`は同じ実体を指す別名でしかないため、`pixels[i] = gray`と書いた瞬間、`imageData.data`自体もすでに書き換わっている。

```javascript
// 検証実験
let arr1 = [1, 2, 3];
let arr2 = arr1;      // 参照が渡るだけ(コピーではない)
arr2[0] = 99;
console.log(arr1);    // [99, 2, 3] ← arr1まで変わる

let arr3 = [...arr1]; // スプレッド構文で本物のコピーを作る
arr3[0] = 0;
console.log(arr1);    // [99, 2, 3] ← arr3を変えてもarr1は影響を受けない
```

プリミティブ値(数値・文字列)は代入・関数への引き渡しで「値」がコピーされるが、配列・オブジェクトは「参照(住所)」が渡されるだけで実体は共有される。関数に渡しても同じで、引数名は呼び出し元の実体への別名でしかない。

## `getBoundingClientRect` と座標変換

```
canvas { width: 320px; } (CSSでの見た目のサイズ)
canvas.width = 640        (JSで設定した内部の実解像度)
```
見た目のサイズと内部の実解像度がズレていることがあるため、クリック位置(見た目基準の座標)をデータ上の座標に変換する必要がある。

```typescript
const rect = canvas.getBoundingClientRect(); // 要素が画面上のどこに、どのサイズで表示されているか
const x = Math.floor(((event.clientX - rect.left) / rect.width) * canvas.width);
//        ①画面全体基準のクリック位置 → ②canvas内での見た目上の位置(rect.leftを引く)
//        → ③canvas幅に対する割合(0〜1、rect.widthで割る) → ④データ上の実際のピクセル座標(canvas.widthを掛ける)
```

## `video.srcObject` が"勝手に"更新され続ける理由

```typescript
video.srcObject = stream;
```
このコード自体は1回きりの代入で、ループもしていない。にもかかわらず映像が更新され続けるのは、**代入後の「継続的に描画し続ける」処理を、ブラウザの内部実装(C++で書かれた部分)が肩代わりしてくれている**ため。

```
canvas → 自分でrequestAnimationFrameループを書かないと1ミリ秒も更新されない
         (「描き続ける責任」がJS側にある)

video(srcObject使用時) → 代入した瞬間に「あとはよろしく」という合図になり、
         ブラウザ内部がJSとは別のスレッドで継続的にフレームを取り込んで描画し続ける
         (「描き続ける責任」がブラウザ側に移る)
```

Phase 2でcanvas用に手書きした`drawFrame()`ループは、`<video>`要素がネイティブに標準装備している仕組みを、自分の手でJSとして再現したもの、と捉えると理解しやすい。

## 今後の課題

- ブラウザ内部の描画パイプライン(コンポジタなど)の詳細は範囲外として一旦保留
- Phase 3でPython Socketを自分の手で書き、Phase 1で保留していたsocketの理解に戻る
