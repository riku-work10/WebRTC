import { annotate } from "./sdpParser.js";

const generateButton = document.getElementById("generateButton") as HTMLButtonElement;
const rawSdp = document.getElementById("rawSdp") as HTMLPreElement;
const tableBody = document.querySelector("#annotatedTable tbody") as HTMLTableSectionElement;

async function generate(): Promise<void> {
  generateButton.disabled = true;

  // 実際にカメラ/マイクを取得しなくても、addTransceiver()だけでm=行を持つSDPが作れる
  const pc = new RTCPeerConnection();
  pc.addTransceiver("video", { direction: "sendrecv" });
  pc.addTransceiver("audio", { direction: "sendrecv" });

  const offer = await pc.createOffer();
  const sdp = offer.sdp ?? "";
  rawSdp.textContent = sdp;

  tableBody.innerHTML = "";
  for (const line of sdp.split("\r\n").filter((l) => l.length > 0)) {
    const tr = document.createElement("tr");

    const lineCell = document.createElement("td");
    lineCell.textContent = line;

    const descCell = document.createElement("td");
    descCell.textContent = annotate(line);

    tr.append(lineCell, descCell);
    tableBody.appendChild(tr);
  }

  pc.close();
  generateButton.disabled = false;
}

generateButton.addEventListener("click", () => {
  generate().catch((error) => {
    rawSdp.textContent = `Error: ${(error as Error).message}`;
  });
});
