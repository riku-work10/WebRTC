const widthInput = document.getElementById("widthInput") as HTMLInputElement;
const heightInput = document.getElementById("heightInput") as HTMLInputElement;
const fpsInput = document.getElementById("fpsInput") as HTMLInputElement;
const startButton = document.getElementById("startButton") as HTMLButtonElement;
const grayscaleButton = document.getElementById("grayscaleButton") as HTMLButtonElement;
const video = document.getElementById("video") as HTMLVideoElement;
const canvas = document.getElementById("canvas") as HTMLCanvasElement;
const configuredFpsOutput = document.getElementById("configuredFps") as HTMLSpanElement;
const actualFpsOutput = document.getElementById("actualFps") as HTMLSpanElement;
const infoOutput = document.getElementById("infoOutput") as HTMLPreElement;

// canvasの２D用のコンテキストの取得→ctxの中にはいろんなメソッドが入っている
const ctx = canvas.getContext("2d") as CanvasRenderingContext2D;

let currentStream: MediaStream | null = null;
let animationFrameId: number | null = null;
let drawnFrameCount = 0;

// requestAnimationFrameで予約したIDを保持しておき、必要に応じてそのIDを使用してキャンセルするための関数
function stopDrawing(): void {
  if (animationFrameId !== null) {
    cancelAnimationFrame(animationFrameId);
    animationFrameId = null;
  }
}

function stopCurrentStream(): void {
  // Startボタンを押すとdrawFrame()の処理を止める
  stopDrawing();
  if (currentStream) {
    for (const track of currentStream.getTracks()) {
      track.stop();
    }
    currentStream = null;
  }
}

// video要素に流れている「今この瞬間のフレーム」を、そのままcanvasに描き写す。
// video自体はブラウザが勝手に描画してくれるが、canvasには自分で毎回描く必要がある。
// drawFrame()は永遠に呼ばれ続ける
function drawFrame(): void {
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  drawnFrameCount++;
  // requestAnimationFrameが予約を成功するとIDを返すので、次の描画予約をする前にIDを保持しておく。
  // これを保持しておくことで、必要に応じてキャンセルすることができる。
  animationFrameId = requestAnimationFrame(drawFrame);
}

async function startStream(): Promise<void> {
  stopCurrentStream();

  const constraints: MediaStreamConstraints = {
    video: {
      width: { ideal: Number(widthInput.value) },
      height: { ideal: Number(heightInput.value) },
      frameRate: { ideal: Number(fpsInput.value) },
    },
    audio: false,
  };

  const stream = await navigator.mediaDevices.getUserMedia(constraints);
  currentStream = stream;
  video.srcObject = stream;

  await video.play();

  // videoの実際の解像度(希望通りにならないこともある)に、canvasのサイズを合わせる。
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const [videoTrack] = stream.getVideoTracks();
  const settings = videoTrack.getSettings();
  configuredFpsOutput.textContent = String(settings.frameRate ?? "?");

  drawFrame();
}

// 1秒ごとに「実際に何回drawFrameが呼ばれたか」を数えて表示する。
// configured(希望値)とここで見えるactual(実測値)がズレることがある、というのを観察する。
setInterval(() => {
  actualFpsOutput.textContent = String(drawnFrameCount);
  drawnFrameCount = 0;
}, 1000);

// canvasをクリックした位置1ピクセル分のImageDataを取得し、RGBAの値を表示する。
// canvas要素をクリックしたらその座標とRGBA値を取得して表示している
canvas.addEventListener("click", (event) => {
  const rect = canvas.getBoundingClientRect();
  // クリック座標はCSS表示上の座標なので、canvasの実解像度に合わせて変換する。
  const x = Math.floor(((event.clientX - rect.left) / rect.width) * canvas.width);
  const y = Math.floor(((event.clientY - rect.top) / rect.height) * canvas.height);

  // クリックした位置の1ピクセル分のImageDataを取得する
  const pixel = ctx.getImageData(x, y, 1, 1).data;
  infoOutput.textContent = JSON.stringify(
    {
      x,
      y,
      r: pixel[0],
      g: pixel[1],
      b: pixel[2],
      a: pixel[3],
    },
    null,
    2
  );
});

// canvas全体のImageDataを取り出し、各ピクセルのR/G/Bを平均値に置き換えて書き戻す。
// 動画・画像が「ただの数値の配列」であることを体感するための実験。
grayscaleButton.addEventListener("click", () => {
  stopDrawing(); // 描き続けているとすぐ上書きされてしまうので、一旦動画の更新を止める

  // canvasの全ピクセルのRGBA値を取得する
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const pixels = imageData.data; // [r, g, b, a, r, g, b, a, ...] という1次元配列

  // rgbaの順番になっているから、4つずつループして平均値を計算して書き換える
  for (let i = 0; i < pixels.length; i += 4) {
    const gray = (pixels[i] + pixels[i + 1] + pixels[i + 2]) / 3;
    pixels[i] = gray;
    pixels[i + 1] = gray;
    pixels[i + 2] = gray;
    // pixels[i + 3] (アルファ値)はそのまま変更しない
  }

  // 書き換えたImageDataをcanvasに戻す
  ctx.putImageData(imageData, 0, 0);
});

startButton.addEventListener("click", startStream);
