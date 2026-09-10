const startButton = document.getElementById("startButton") as HTMLButtonElement;
const localVideo = document.getElementById("localVideo") as HTMLVideoElement;
const remoteVideo = document.getElementById("remoteVideo") as HTMLVideoElement;
const logOutput = document.getElementById("logOutput") as HTMLPreElement;

function log(message: string): void {
  console.log(message);
  logOutput.textContent += `\n${message}`;
}

// 公開STUNサーバー(Phase 7で自作したものと同じ役割)。
// 同じPC内のループバック接続でも、RTCPeerConnectionは実際にSTUNへ問い合わせてsrflx candidateを作る
const ICE_SERVERS: RTCConfiguration = {
  iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
};

async function start(): Promise<void> {
  startButton.disabled = true;
  logOutput.textContent = "";

  const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
  localVideo.srcObject = stream;
  log("[getUserMedia] カメラ取得完了");

  const pc1 = new RTCPeerConnection(ICE_SERVERS);
  const pc2 = new RTCPeerConnection(ICE_SERVERS);
  log("[RTCPeerConnection] pc1(送信側) / pc2(受信側) を作成");

  // addIceCandidate() はsetRemoteDescription()が終わるまで安全に呼べないため、
  // 先にcandidateが届いた場合は一旦キューに溜めておく(trickle ICEの典型的な扱い)
  const pending2: RTCIceCandidate[] = [];
  const pending1: RTCIceCandidate[] = [];
  let remoteSetOn2 = false;
  let remoteSetOn1 = false;

  pc1.onicecandidate = async (e) => {
    if (!e.candidate) {
      log("[pc1] candidate収集完了(null candidate)");
      return;
    }
    log(`[pc1→pc2] candidate: type=${e.candidate.type} ${e.candidate.address}:${e.candidate.port}`);
    if (remoteSetOn2) {
      await pc2.addIceCandidate(e.candidate);
    } else {
      pending2.push(e.candidate);
    }
  };

  pc2.onicecandidate = async (e) => {
    if (!e.candidate) {
      log("[pc2] candidate収集完了(null candidate)");
      return;
    }
    log(`[pc2→pc1] candidate: type=${e.candidate.type} ${e.candidate.address}:${e.candidate.port}`);
    if (remoteSetOn1) {
      await pc1.addIceCandidate(e.candidate);
    } else {
      pending1.push(e.candidate);
    }
  };

  pc1.oniceconnectionstatechange = () => log(`[pc1] iceConnectionState=${pc1.iceConnectionState}`);
  pc2.oniceconnectionstatechange = () => log(`[pc2] iceConnectionState=${pc2.iceConnectionState}`);
  pc1.onconnectionstatechange = () => log(`[pc1] connectionState=${pc1.connectionState}`);
  pc2.onconnectionstatechange = () => log(`[pc2] connectionState=${pc2.connectionState}`);

  pc2.ontrack = (e) => {
    log(`[pc2] ontrack: kind=${e.track.kind} 受信`);
    remoteVideo.srcObject = e.streams[0];
  };

  for (const track of stream.getTracks()) {
    pc1.addTrack(track, stream);
  }

  // --- Offer/Answerの交換(このページ内で直接渡しているが、本来はシグナリングサーバー経由でやる部分) ---
  const offer = await pc1.createOffer();
  log(`[pc1] createOffer完了 (SDP ${offer.sdp?.length}文字。詳細はPhase 10で読む)`);
  await pc1.setLocalDescription(offer);

  await pc2.setRemoteDescription(offer);
  remoteSetOn2 = true;
  log("[pc2] setRemoteDescription(offer)完了");
  for (const c of pending2.splice(0)) {
    await pc2.addIceCandidate(c);
  }

  const answer = await pc2.createAnswer();
  log(`[pc2] createAnswer完了 (SDP ${answer.sdp?.length}文字)`);
  await pc2.setLocalDescription(answer);

  await pc1.setRemoteDescription(answer);
  remoteSetOn1 = true;
  log("[pc1] setRemoteDescription(answer)完了");
  for (const c of pending1.splice(0)) {
    await pc1.addIceCandidate(c);
  }

  log("[done] offer/answer交換完了。あとはICEが裏でcandidateペアの疎通確認(Phase 8参照)をしてDTLS/SRTPのハンドシェイクへ進む");
}

startButton.addEventListener("click", () => {
  start().catch((error) => log(`[error] ${(error as Error).message}`));
});
