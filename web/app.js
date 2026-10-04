/**
 * CapCut Cache Recover — Pure In-Browser Client-Side BDVE Type 1 Stream Recovery
 * 
 * Engineered by PixelPie Media • Founded by Md. Zobaed Islam Shanto.
 * 100% Client-Side. Zero server calls. Bitstream-exact periodic XOR stream recovery.
 */

(() => {
  'use strict';

  // DOM Elements
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');
  const emptyState = document.getElementById('emptyState');
  const selectedState = document.getElementById('selectedState');
  const btnBrowse = document.getElementById('btnBrowse');
  const btnReset = document.getElementById('btnReset');
  const fileName = document.getElementById('fileName');
  const fileSize = document.getElementById('fileSize');
  const btnStartRecover = document.getElementById('btnStartRecover');
  const progressContainer = document.getElementById('progressContainer');
  const progressBar = document.getElementById('progressBar');
  const progressText = document.getElementById('progressText');
  const progressPercent = document.getElementById('progressPercent');
  const termLogs = document.getElementById('termLogs');
  const resultBox = document.getElementById('resultBox');
  const videoPreview = document.getElementById('videoPreview');
  const btnDownload = document.getElementById('btnDownload');

  let currentFile = null;
  let currentObjectUrl = null;

  // Formatting helper
  function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  // Logger helper
  function log(message, type = 'info') {
    const time = new Date().toTimeString().split(' ')[0];
    const line = document.createElement('div');
    line.className = `log-line log-${type}`;
    line.textContent = `[${time}] ${message}`;
    termLogs.appendChild(line);
    termLogs.scrollTop = termLogs.scrollHeight;
  }

  function clearLogs() {
    termLogs.innerHTML = '';
  }

  // File Selection
  btnBrowse.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
      handleSelectedFile(e.target.files[0]);
    }
  });

  // Drag and Drop
  ['dragenter', 'dragover'].forEach(name => {
    dropZone.addEventListener(name, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.add('drag-active');
    });
  });

  ['dragleave', 'drop'].forEach(name => {
    dropZone.addEventListener(name, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.remove('drag-active');
    });
  });

  dropZone.addEventListener('drop', (e) => {
    if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleSelectedFile(e.dataTransfer.files[0]);
    }
  });

  function handleSelectedFile(file) {
    currentFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = formatBytes(file.size);

    emptyState.style.display = 'none';
    selectedState.style.display = 'block';
    progressContainer.style.display = 'none';
    resultBox.style.display = 'none';

    if (currentObjectUrl) {
      URL.revokeObjectURL(currentObjectUrl);
      currentObjectUrl = null;
    }

    clearLogs();
    log(`Loaded file: ${file.name} (${formatBytes(file.size)})`);
    log(`File type detected: ${file.type || 'application/octet-stream'}`);
    log(`Ready for in-browser cryptanalysis.`);
  }

  btnReset.addEventListener('click', () => {
    currentFile = null;
    fileInput.value = '';
    emptyState.style.display = 'block';
    selectedState.style.display = 'none';
    progressContainer.style.display = 'none';
    resultBox.style.display = 'none';
    if (currentObjectUrl) {
      URL.revokeObjectURL(currentObjectUrl);
      currentObjectUrl = null;
    }
  });

  // -------------------------------------------------------------------------
  // Cryptographic Engine: BDVE Type 1 Periodic XOR Parser & Solver
  // -------------------------------------------------------------------------

  function parseBdveFooter(bytes) {
    const len = bytes.length;
    if (len < 68) return null;

    // Search last 256 bytes for ByteDance BDVE box
    const searchWindow = Math.min(len, 256);
    const startOffset = len - searchWindow;

    for (let i = startOffset; i <= len - 68; i++) {
      // Check for 'bdve' atom (0x62 0x64 0x76 0x65)
      if (
        bytes[i + 4] === 0x62 &&
        bytes[i + 5] === 0x64 &&
        bytes[i + 6] === 0x76 &&
        bytes[i + 7] === 0x65
      ) {
        const boxSize = (bytes[i] << 24) | (bytes[i + 1] << 16) | (bytes[i + 2] << 8) | bytes[i + 3];
        if (boxSize === 68 && i + 68 <= len) {
          // Parse crpt box inside
          const crptType = (bytes[i + 16] << 24) | (bytes[i + 17] << 16) | (bytes[i + 18] << 8) | bytes[i + 19];
          const crptVer = (bytes[i + 20] << 24) | (bytes[i + 21] << 16) | (bytes[i + 22] << 8) | bytes[i + 23];
          const sha256 = bytes.slice(i + 24, i + 56);

          return {
            footerStart: i,
            footerSize: 68,
            cryptorType: crptType,
            version: crptVer,
            targetSha256: sha256
          };
        }
      }
    }
    return null;
  }

  function uint8ToHex(bytes) {
    return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
  }

  async function sha256Bytes(data) {
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    return new Uint8Array(hashBuffer);
  }

  function buffersEqual(a, b) {
    if (a.length !== b.length) return false;
    for (let i = 0; i < a.length; i++) {
      if (a[i] !== b[i]) return false;
    }
    return true;
  }

  async function solveBdveParameters(bytes, key, targetHash, logFn) {
    logFn(`Gathering container boundary observations...`);

    // In ISO Base Media File Format (MP4), offset 0-3 is 4-byte big endian atom length (usually 0x00000020 or 0x00000018)
    // Offset 4-7 is 'ftyp'
    const observations = [
      { pos: 0, encrypted: true },
      { pos: 4, encrypted: true },
      { pos: 32, encrypted: true }
    ];

    // Find markers
    const ftypAscii = [0x66, 0x74, 0x79, 0x70];
    const mdatAscii = [0x6d, 0x64, 0x61, 0x74];
    const moovAscii = [0x6d, 0x6f, 0x6f, 0x76];

    // Fast search for marker positions
    function findSub(needle) {
      for (let i = 0; i < Math.min(bytes.length, 500000); i++) {
        let match = true;
        for (let j = 0; j < needle.length; j++) {
          if (bytes[i + j] !== needle[j]) { match = false; break; }
        }
        if (match) return i;
      }
      return -1;
    }

    [ftypAscii, mdatAscii, moovAscii].forEach(marker => {
      const rawPos = findSub(marker);
      if (rawPos >= 0) observations.push({ pos: rawPos, encrypted: false });
      const encMarker = marker.map(b => b ^ key);
      const encPos = findSub(encMarker);
      if (encPos >= 0) observations.push({ pos: encPos, encrypted: true });
    });

    logFn(`Identified ${observations.length} bitstream constraints. Solving via Web Crypto API...`);

    const MAX_STEP = 1500000;
    const testBuffer = new Uint8Array(9);
    testBuffer[8] = key;

    for (let step = 1; step <= MAX_STEP; step++) {
      let low = 1;
      let high = step;

      for (const obs of observations) {
        const remainder = obs.pos % step;
        if (obs.encrypted) {
          low = Math.max(low, remainder + 1);
        } else {
          high = Math.min(high, remainder);
        }
        if (low > high) break;
      }

      if (low > high) continue;

      // Pack step into testBuffer[0..3]
      testBuffer[0] = (step >>> 24) & 0xff;
      testBuffer[1] = (step >>> 16) & 0xff;
      testBuffer[2] = (step >>> 8) & 0xff;
      testBuffer[3] = step & 0xff;

      for (let length = low; length <= high; length++) {
        testBuffer[4] = (length >>> 24) & 0xff;
        testBuffer[5] = (length >>> 16) & 0xff;
        testBuffer[6] = (length >>> 8) & 0xff;
        testBuffer[7] = length & 0xff;

        const hash = await sha256Bytes(testBuffer);
        if (buffersEqual(hash, targetHash)) {
          return { step, length, key };
        }
      }
    }

    return null;
  }

  // Main Recovery Trigger
  btnStartRecover.addEventListener('click', async () => {
    if (!currentFile) return;

    btnStartRecover.disabled = true;
    progressContainer.style.display = 'block';
    progressBar.style.width = '0%';
    progressPercent.textContent = '0%';
    progressText.textContent = 'Reading video file into memory...';
    resultBox.style.display = 'none';

    try {
      log(`Allocating buffer for ${formatBytes(currentFile.size)}...`);
      const arrayBuffer = await currentFile.arrayBuffer();
      const bytes = new Uint8Array(arrayBuffer);

      log(`Inspecting ByteDance container trailer...`);
      const footer = parseBdveFooter(bytes);

      if (!footer) {
        log(`[-] No ByteDance BDVE cryptor footer detected!`, 'error');
        alert(`No BDVE trailer was found in this file. It may already be unencrypted or a standard MP4.`);
        btnStartRecover.disabled = false;
        progressContainer.style.display = 'none';
        return;
      }

      log(`[+] BDVE trailer found at byte ${footer.footerStart.toLocaleString()}!`, 'success');
      log(`    - Cryptor Type: ${footer.cryptorType}`);
      log(`    - Version:      ${footer.version}`);
      log(`    - Hash Digest:  ${uint8ToHex(footer.targetSha256).slice(0, 16)}...`);

      // Derive Key: First byte of MP4 atom length is always 0x00 in unencrypted file
      const key = bytes[0] ^ 0x00;
      log(`[+] Derived XOR Mask Key: 0x${key.toString(16).toUpperCase()}`, 'success');

      progressText.textContent = 'Deriving periodic encryption parameters...';
      progressBar.style.width = '20%';
      progressPercent.textContent = '20%';

      const startTime = performance.now();
      const params = await solveBdveParameters(bytes, key, footer.targetSha256, (m) => log(m));

      if (!params) {
        log(`[-] Parameter derivation failed. File signature mismatch.`, 'error');
        alert(`Could not mathematically verify BDVE parameters against SHA-256 trailer.`);
        btnStartRecover.disabled = false;
        progressContainer.style.display = 'none';
        return;
      }

      log(`[+] Parameters verified in ${((performance.now() - startTime) / 1000).toFixed(2)}s:`, 'success');
      log(`    • Step:   ${params.step.toLocaleString()} bytes`);
      log(`    • Length: ${params.length.toLocaleString()} bytes`);
      log(`    • Key:    0x${params.key.toString(16).toUpperCase()}`);

      progressText.textContent = 'Inverting bitstream periodic XOR mask...';

      // Bitstream Inversion
      const payloadEnd = footer.footerStart;
      const decrypted = new Uint8Array(payloadEnd);
      decrypted.set(bytes.subarray(0, payloadEnd));

      const chunkSize = 5000000; // Yield every ~5MB to keep browser responsive
      let processed = 0;

      for (let blockStart = 0; blockStart < payloadEnd; blockStart += params.step) {
        const blockEnd = Math.min(blockStart + params.length, payloadEnd);
        for (let i = blockStart; i < blockEnd; i++) {
          decrypted[i] ^= params.key;
        }

        processed = blockEnd;
        if (blockStart % chunkSize === 0) {
          const pct = Math.floor((processed / payloadEnd) * 75) + 20;
          progressBar.style.width = `${pct}%`;
          progressPercent.textContent = `${pct}%`;
          await new Promise(r => setTimeout(r, 0));
        }
      }

      progressBar.style.width = '100%';
      progressPercent.textContent = '100%';
      progressText.textContent = 'Finalizing clean MP4 container...';

      const totalElapsed = ((performance.now() - startTime) / 1000).toFixed(2);
      log(`[SUCCESS] Decryption completed in ${totalElapsed}s with 0% generational loss!`, 'success');

      // Create downloadable Blob & Object URL
      const cleanBlob = new Blob([decrypted], { type: 'video/mp4' });
      currentObjectUrl = URL.createObjectURL(cleanBlob);

      videoPreview.src = currentObjectUrl;
      videoPreview.load();

      const outName = currentFile.name
        .replace(/\.(tmp|cache|dat|mp4_temp)$/i, '')
        .replace(/_video$/i, '') + '_RECOVERED.mp4';

      btnDownload.href = currentObjectUrl;
      btnDownload.download = outName;

      resultBox.style.display = 'block';
      log(`[+] Stream ready. You can preview above or download clean MP4.`, 'success');

    } catch (err) {
      log(`[-] Error during recovery: ${err.message}`, 'error');
      console.error(err);
      alert(`Recovery failed: ${err.message}`);
    } finally {
      btnStartRecover.disabled = false;
      progressContainer.style.display = 'none';
    }
  });

})();
