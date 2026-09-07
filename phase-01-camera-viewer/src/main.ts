// HTMLの要素を取得している <select id="cameraSelect"></select> これとか
const cameraSelect = document.getElementById("cameraSelect") as HTMLSelectElement;
console.log(cameraSelect);
const micSelect = document.getElementById("micSelect") as HTMLSelectElement;
const widthInput = document.getElementById("widthInput") as HTMLInputElement;
const heightInput = document.getElementById("heightInput") as HTMLInputElement;
const fpsInput = document.getElementById("fpsInput") as HTMLInputElement;
const startButton = document.getElementById("startButton") as HTMLButtonElement;
const video = document.getElementById("video") as HTMLVideoElement;
const infoOutput = document.getElementById("infoOutput") as HTMLPreElement;

// カメラやマイクのストリームを保持する変数
let currentStream: MediaStream | null = null;

async function populateDeviceSelects(): Promise<void> {
  const devices = await navigator.mediaDevices.enumerateDevices();

  const cameras = devices.filter((d) => d.kind === "videoinput");
  const mics = devices.filter((d) => d.kind === "audioinput");

  cameraSelect.innerHTML = cameras
    .map((d, i) => `<option value="${d.deviceId}">${d.label || `Camera ${i}`}</option>`)
    .join("");

  micSelect.innerHTML = mics
    .map((d, i) => `<option value="${d.deviceId}">${d.label || `Mic ${i}`}</option>`)
    .join("");
}

function stopCurrentStream(): void {
  if (currentStream) {
    for (const track of currentStream.getTracks()) {
      track.stop();
    }
    currentStream = null;
  }
}

function describeTrack(track: MediaStreamTrack): object {
  return {
    kind: track.kind,
    label: track.label,
    readyState: track.readyState,
    enabled: track.enabled,
    settings: track.getSettings(),
    capabilities: track.getCapabilities(),
  };
}

async function startStream(): Promise<void> {
  // 既存のストリームがあれば停止するが後続で新しいストリームを開始するから止まったようにはみえない
  stopCurrentStream();

  const constraints: MediaStreamConstraints = {
    video: {
      deviceId: cameraSelect.value ? { exact: cameraSelect.value } : undefined,
      width: { ideal: Number(widthInput.value) },
      height: { ideal: Number(heightInput.value) },
      frameRate: { ideal: Number(fpsInput.value) },
    },
    audio: {
      deviceId: micSelect.value ? { exact: micSelect.value } : undefined,
    },
  };

  try {
    // ユーザーのカメラとマイクのストリームを取得する→許可を求めるダイアログが出る
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    currentStream = stream;
    //video要素にストリームをセットすることで、カメラ映像が表示される
    //srcObjectにMediaStreamをセットすることで、video要素に映像が表示される
    //srcとは異なり、URLではなくMediaStreamを直接セットすることができる
    video.srcObject = stream;

    // ラベル付きのデバイス名は permission 許可後でないと取得できないため、
    // ここで一覧を取り直して <select> に反映する。
    await populateDeviceSelects();

    const info = stream.getTracks().map(describeTrack); //.map((track) => describeTrack(track))の省略形
    // JSON.stringify(値, 第2引数, 第3引数:改行やインデントの指定)で、オブジェクトをJSON文字列に変換する 
    infoOutput.textContent = JSON.stringify(info, null, 2);
  } catch (error) {
    infoOutput.textContent = `Error: ${(error as Error).message}`;
  }
}

startButton.addEventListener("click", startStream);
cameraSelect.addEventListener("change", startStream);
micSelect.addEventListener("change", startStream);

populateDeviceSelects();
