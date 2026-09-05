const cameraSelect = document.getElementById("cameraSelect") as HTMLSelectElement;
const micSelect = document.getElementById("micSelect") as HTMLSelectElement;
const widthInput = document.getElementById("widthInput") as HTMLInputElement;
const heightInput = document.getElementById("heightInput") as HTMLInputElement;
const fpsInput = document.getElementById("fpsInput") as HTMLInputElement;
const startButton = document.getElementById("startButton") as HTMLButtonElement;
const video = document.getElementById("video") as HTMLVideoElement;
const infoOutput = document.getElementById("infoOutput") as HTMLPreElement;

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
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    currentStream = stream;
    video.srcObject = stream;

    // ラベル付きのデバイス名は permission 許可後でないと取得できないため、
    // ここで一覧を取り直して <select> に反映する。
    await populateDeviceSelects();

    const info = stream.getTracks().map(describeTrack);
    infoOutput.textContent = JSON.stringify(info, null, 2);
  } catch (error) {
    infoOutput.textContent = `Error: ${(error as Error).message}`;
  }
}

startButton.addEventListener("click", startStream);
cameraSelect.addEventListener("change", startStream);
micSelect.addEventListener("change", startStream);

populateDeviceSelects();
