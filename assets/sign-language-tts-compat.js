(function () {
  "use strict";

  const nativePause = HTMLMediaElement.prototype.pause;
  const nativePlay = HTMLMediaElement.prototype.play;
  const audioPlayers = new Set();
  const ONLINE_READING_ONLY_RE = /^FOR\s+ONLINE\s+READING\s+ONLY$/i;
  const ONLINE_READING_ONLY_SW_RE = /^KWA\s+AJILI\s+YA\s+KUSOMA\s+MTANDAONI\s+TU$/i;
  const ONLINE_ONLY_VARIANT_RE = /^(?:FOR\s+ONLINE\s+READING\s+ONLY|KWA\s+KUSOMA\s+MTANDAONI\s+TU\.?|KUSOMA\s+MTANDAONI\s+TU\.?)$/i;
  const ISBN_RE = /^ISBN:\s*978-9912-753-63-1$/i;
  const SECTION_LETTER_RE = /^([A-Ha-h])\.$/;
  const SECTION_LETTER_PREFIX_RE = /^([A-Ha-h])\.\s+(.*)$/;
  const ROMAN_NUMERAL_RE = /^\((i|ii|iii|iv|v|vi|vii|viii|ix|x)\)(?:\s*(.*))?$/i;
  const BLANK_ITEM_RE = /\[\[blank:item-\d+(?::[^\]]+)?\]\]/gi;
  const ONE_TO_EIGHT_RANGE_RE = /\b1\s*[-–]\s*8\b/gi;
  const X_TIMES_TWO_RE = /\bx\s*2\b/gi;
  const originalTextById = new Map();
  const ROMAN_NUMERAL_WORDS = {
    i: "moja",
    ii: "mbili",
    iii: "tatu",
    iv: "nne",
    v: "tano",
    vi: "sita",
    vii: "saba",
    viii: "nane",
    ix: "tisa",
    x: "kumi",
  };
  const SECTION_LETTER_WORDS = {
    a: "aa",
    b: "bee",
    c: "chee",
    d: "dee",
    e: "ee",
    f: "efu",
    g: "gee",
    h: "hee",
  };
  const SAMPLE_SEPARATOR_KEYS = new Set([
    "pg108_n0074",
    "pg108_n0075",
    "pg108_n0074_easy_read",
    "pg108_n0075_easy_read",
    "pg109_n0004",
    "pg109_n0005",
    "pg109_n0004_easy_read",
    "pg109_n0005_easy_read",
  ]);
  const SILENT_TEXT_KEYS = new Set([
    "pg001_n0013",
    "pg001_n0013_easy_read",
    "pg002_n0005",
    "pg002_n0005_easy_read",
  ]);
  const CUSTOM_TTS_TEXT_BY_KEY = {
    pg002_n0014: "Baruapepe: dairekta jenero at tai go tanzania",
    pg002_n0014_easy_read: "Barua pepe: dairekta jenero at tai go tanzania",
    pg002_n0015: "Tovuti: dablyu dablyu dablyu dot tai dot go dot tanzania",
    pg002_n0015_easy_read: "Tovuti: dablyu dablyu dablyu dot tai dot go dot tanzania",
  };
  const STATIC_BLOCKED_AUDIO_IDS = new Set([
    "pg005_n0032",
    "pg005_n0032_easy_read",
    "pg009_n0032",
    "pg009_n0032_easy_read",
    "pg029_n0035_easy_read",
    "pg040_n0035_easy_read",
    "pg062_n0041_easy_read",
    "pg114_n0077",
    "pg114_n0077_easy_read",
  ]);
  const CORRECTED_RECORDED_AUDIO_IDS = new Set([
    "pg062_n0004",
    "pg062_n0005",
    "pg062_n0007",
    "pg062_n0008",
    "pg062_n0011",
    "pg062_n0013",
    "pg062_n0015",
    "pg062_n0017",
    "pg062_n0019",
    "pg062_n0021",
    "pg062_n0023",
    "pg062_n0026",
    "pg062_n0028",
    "pg062_n0030",
    "pg062_n0032",
    "pg062_n0034",
    "pg062_n0036",
    "pg062_n0038",
    "pg062_n0040",
    "pg062_n0043",
    "pg062_n0047",
    "pg062_n0050",
    "pg062_n0053",
    "pg062_n0056",
    "pg062_n0059",
    "pg062_n0004_easy_read",
    "pg062_n0005_easy_read",
    "pg062_n0007_easy_read",
    "pg062_n0008_easy_read",
    "pg062_n0011_easy_read",
    "pg062_n0013_easy_read",
    "pg062_n0015_easy_read",
    "pg062_n0017_easy_read",
    "pg062_n0019_easy_read",
    "pg062_n0021_easy_read",
    "pg062_n0023_easy_read",
    "pg062_n0026_easy_read",
    "pg062_n0028_easy_read",
    "pg062_n0030_easy_read",
    "pg062_n0032_easy_read",
    "pg062_n0034_easy_read",
    "pg062_n0036_easy_read",
    "pg062_n0038_easy_read",
    "pg062_n0040_easy_read",
    "pg062_n0043_easy_read",
    "pg062_n0047_easy_read",
    "pg062_n0050_easy_read",
    "pg062_n0053_easy_read",
    "pg062_n0056_easy_read",
    "pg062_n0059_easy_read",
  ]);
  for (const id of window.__ADT_CORRECTED_RECORDED_AUDIO_IDS__ || []) {
    if (typeof id === "string") CORRECTED_RECORDED_AUDIO_IDS.add(id);
  }
  const PAGE_AUDIO_SUPPLEMENT_IDS = new Set(
    (window.__ADT_PAGE_AUDIO_SUPPLEMENT_IDS__ || []).filter(
      (id) => typeof id === "string",
    ),
  );
  const runtimeBlockedAudioIds = new Set(STATIC_BLOCKED_AUDIO_IDS);
  const isSignVideo = (media) =>
    media instanceof HTMLVideoElement &&
    /\/content\/i18n\/[^/]+\/video\/page_\d+\.mp4(?:[?#]|$)/i.test(
      media.currentSrc || media.src || "",
    );
  const normalizeText = (value) => (value || "").replace(/\s+/g, " ").trim();
  const snapshotOriginalTexts = (root) => {
    root.querySelectorAll?.("[data-id]").forEach((element) => {
      const id = element.getAttribute("data-id");
      if (!id || originalTextById.has(id)) return;
      originalTextById.set(id, element.textContent || "");
    });
  };
  const hasOneToEightRange = (value) => /\b1\s*[-–]\s*8\b/i.test(value || "");
  const withRuntimeBlockedId = (id) => {
    if (id) runtimeBlockedAudioIds.add(id);
    return id;
  };
  const isBlockedAudioSource = (value) =>
    Array.from(runtimeBlockedAudioIds).some((id) =>
      new RegExp(`(?:^|[\\\\/_-])${id}(?:\\.mp3)?(?:[?#]|$)`, "i").test(value || ""),
    );
  const rewriteRomanNumeralText = (value) => {
    const match = ROMAN_NUMERAL_RE.exec(normalizeText(value));
    if (!match) return null;
    const numeral = match[1].toLowerCase();
    const rest = normalizeText(match[2] || "");
    const label = ROMAN_NUMERAL_WORDS[numeral];
    if (!label) return null;
    return rest ? `${label}. ${rest}` : label;
  };
  const rewriteSectionLetterText = (value) => {
    const exactMatch = SECTION_LETTER_RE.exec(normalizeText(value));
    if (exactMatch) return SECTION_LETTER_WORDS[exactMatch[1].toLowerCase()] || null;
    const prefixMatch = SECTION_LETTER_PREFIX_RE.exec(normalizeText(value));
    if (!prefixMatch) return null;
    const label = SECTION_LETTER_WORDS[prefixMatch[1].toLowerCase()];
    if (!label) return null;
    return `${label}. ${prefixMatch[2]}`;
  };
  const rewriteTextForTts = (value) => {
    let rewritten = rewriteSectionLetterText(value) ?? rewriteRomanNumeralText(value) ?? value;
    rewritten = rewritten.replace(ONE_TO_EIGHT_RANGE_RE, "moja hadi nane");
    rewritten = rewritten.replace(BLANK_ITEM_RE, "dash");
    rewritten = rewritten.replace(X_TIMES_TWO_RE, "mara mbili");
    rewritten = rewritten.replace(/\s+,/g, ",");
    rewritten = rewritten.replace(/\s+\./g, ".");
    rewritten = rewritten.replace(/\s{2,}/g, " ").trim();
    return rewritten;
  };
  const rewriteSampleSeparatorText = (key, value) => {
    if (!SAMPLE_SEPARATOR_KEYS.has(key)) return value;
    return value.replace(/\s+[–-]\s+/g, ", dash, ");
  };
  const rewriteSilentText = (key, value) => {
    if (ONLINE_ONLY_VARIANT_RE.test(normalizeText(value))) return "";
    if (!SILENT_TEXT_KEYS.has(key)) return value;
    return "";
  };
  const rewriteCustomTextByKey = (key, value) =>
    Object.prototype.hasOwnProperty.call(CUSTOM_TTS_TEXT_BY_KEY, key)
      ? CUSTOM_TTS_TEXT_BY_KEY[key]
      : value;
  const buildTextPatchPlan = (source) => {
    const patched = { ...source };
    const blockedAudioIds = new Set();
    for (const [key, rawValue] of Object.entries(source || {})) {
      if (typeof rawValue !== "string") continue;
      const rewritten = rewriteCustomTextByKey(
        key,
        rewriteSilentText(key, rewriteSampleSeparatorText(key, rewriteTextForTts(rawValue))),
      );
      const shouldForceTts =
        /moja hadi nane/i.test(rawValue) ||
        hasOneToEightRange(rawValue) ||
        ISBN_RE.test(normalizeText(rawValue)) ||
        ONLINE_ONLY_VARIANT_RE.test(normalizeText(rawValue));
      if (rewritten !== rawValue) {
        patched[key] = rewritten;
        if (!CORRECTED_RECORDED_AUDIO_IDS.has(key)) blockedAudioIds.add(key);
        continue;
      }
      if (shouldForceTts) blockedAudioIds.add(key);
    }
    for (const id of STATIC_BLOCKED_AUDIO_IDS) blockedAudioIds.add(id);
    return { patched, blockedAudioIds };
  };
  const textPatchPlans = new Map();
  const cloneJsonResponse = async (response, payload) =>
    new Response(JSON.stringify(payload), {
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
    });
  const getTextPatchPlan = async (textsUrl, fallbackResponse) => {
    if (!textPatchPlans.has(textsUrl)) {
      textPatchPlans.set(
        textsUrl,
        (async () => {
          const response = fallbackResponse || (await nativeFetch(textsUrl));
          const source = { ...(await response.clone().json()) };
          Object.assign(source, window.__ADT_READING_TEXT_OVERRIDES__ || {});
          for (const id of PAGE_AUDIO_SUPPLEMENT_IDS) {
            const element = document.querySelector(`[data-id="${id}"]`);
            if (!element) continue;
            const value = normalizeText(element.textContent);
            if (!value) continue;
            source[id] = value;
            source[`${id}_easy_read`] = value;
          }
          return buildTextPatchPlan(source);
        })(),
      );
    }
    return textPatchPlans.get(textsUrl);
  };
  const patchResponseIfNeeded = async (url, response) => {
    if (!response || !response.ok) return response;
    if (/\/content\/i18n\/[^/]+\/texts\.json(?:[?#]|$)/i.test(url)) {
      const plan = await getTextPatchPlan(url, response);
      for (const id of plan.blockedAudioIds) withRuntimeBlockedId(id);
      return cloneJsonResponse(response, plan.patched);
    }
    if (/\/content\/i18n\/[^/]+\/audios\.json(?:[?#]|$)/i.test(url)) {
      const textsUrl = url.replace(/audios\.json([?#].*)?$/i, "texts.json");
      const plan = await getTextPatchPlan(textsUrl);
      const payload = { ...(await response.clone().json()) };
      for (const id of PAGE_AUDIO_SUPPLEMENT_IDS) {
        payload[id] = `${id}.mp3`;
        payload[`${id}_easy_read`] = `${id}_easy_read.mp3`;
      }
      for (const id of plan.blockedAudioIds) {
        withRuntimeBlockedId(id);
        delete payload[id];
      }
      return cloneJsonResponse(response, payload);
    }
    return response;
  };
  const nativeFetch = window.fetch.bind(window);
  window.fetch = async function (resource, init) {
    const response = await nativeFetch(resource, init);
    const url =
      resource && typeof resource === "object" && typeof resource.url === "string"
        ? resource.url
        : String(resource);
    return patchResponseIfNeeded(url, response);
  };

  const prepareSignVideo = (video) => {
    if (!isSignVideo(video)) return;
    video.muted = true;
    video.defaultMuted = true;
    video.volume = 0;
    video.setAttribute("muted", "");
  };

  const injectWatermarkCleanupStyles = () => {
    if (document.getElementById("online-reading-watermark-cleanup")) return;
    const style = document.createElement("style");
    style.id = "online-reading-watermark-cleanup";
    style.textContent = `
      .restored-page::before {
        content: none !important;
      }
    `;
    (document.head || document.documentElement).appendChild(style);
  };

  const suppressOnlineReadingWatermark = (root) => {
    root.querySelectorAll?.("*").forEach((element) => {
      if (element.tagName === "SCRIPT" || element.tagName === "STYLE") return;
      if (!ONLINE_ONLY_VARIANT_RE.test(normalizeText(element.textContent))) return;
      if (Array.from(element.children).some((child) => normalizeText(child.textContent))) return;
      element.textContent = "";
      element.setAttribute("aria-hidden", "true");
      element.style.display = "none";
    });
  };

  const restoreOriginalVisibleText = (root) => {
    root.querySelectorAll?.("[data-id]").forEach((element) => {
      const id = element.getAttribute("data-id");
      if (!id || !originalTextById.has(id)) return;
      if (element.getAttribute("aria-hidden") === "true") return;
      if (element.getAttribute("data-tts-skip")) return;
      if (element.style?.display === "none") return;
      if (Array.from(element.children).some((child) => normalizeText(child.textContent))) return;
      const original = originalTextById.get(id);
      if ((element.textContent || "") === original) return;
      element.textContent = original;
    });
  };

  const suppressFooterTts = (root) => {
    root.querySelectorAll?.("[data-id]").forEach((element) => {
      const text = normalizeText(element.textContent);
      const skip =
        STATIC_BLOCKED_AUDIO_IDS.has(element.getAttribute("data-id") || "") ||
        ISBN_RE.test(text) ||
        ONLINE_READING_ONLY_RE.test(text) ||
        ONLINE_READING_ONLY_SW_RE.test(text) ||
        ONLINE_ONLY_VARIANT_RE.test(text) ||
        /KISWAHILI\s+LENYE\s+MABORESHO\s+YOTE\.indd/i.test(text) ||
        /^\d{1,2}\/\d{1,2}\/20\d{2}\s+\d{1,2}:\d{2}$/.test(text);
      if (!skip) return;
      element.removeAttribute("data-id");
      element.setAttribute("data-tts-skip", "footer");
      element.setAttribute("aria-hidden", "true");
    });
  };

  HTMLMediaElement.prototype.pause = function () {
    if (isSignVideo(this)) return;
    return nativePause.call(this);
  };

  HTMLMediaElement.prototype.play = function () {
    if (this instanceof HTMLAudioElement) {
      if (isBlockedAudioSource(this.currentSrc || this.src || "")) {
        this.pause();
        return Promise.resolve();
      }
      for (const player of audioPlayers) {
        if (player !== this && !player.paused) nativePause.call(player);
      }
      audioPlayers.add(this);
    }
    if (isSignVideo(this)) prepareSignVideo(this);
    return nativePlay.call(this);
  };

  window.addEventListener(
    "play",
    (event) => {
      const video = event.target;
      if (!isSignVideo(video)) return;
      prepareSignVideo(video);
      event.stopImmediatePropagation();
    },
    true,
  );

  new MutationObserver((records) => {
    for (const record of records) {
      for (const node of record.addedNodes) {
        if (!(node instanceof Element)) continue;
        snapshotOriginalTexts(node);
        if (node instanceof HTMLVideoElement) prepareSignVideo(node);
        node.querySelectorAll?.("video").forEach(prepareSignVideo);
      }
    }
    injectWatermarkCleanupStyles();
    suppressOnlineReadingWatermark(document);
    suppressFooterTts(document);
    restoreOriginalVisibleText(document);
    document.querySelectorAll?.("audio").forEach((audio) => {
      if (!(audio instanceof HTMLAudioElement)) return;
      if (!isBlockedAudioSource(audio.currentSrc || audio.src || "")) return;
      audio.removeAttribute("src");
      audio.load();
    });
  }).observe(document.documentElement, { childList: true, subtree: true });

  snapshotOriginalTexts(document);
  injectWatermarkCleanupStyles();
  suppressOnlineReadingWatermark(document);
  suppressFooterTts(document);
  restoreOriginalVisibleText(document);
  document.querySelectorAll?.("audio").forEach((audio) => {
    if (!(audio instanceof HTMLAudioElement)) return;
    if (!isBlockedAudioSource(audio.currentSrc || audio.src || "")) return;
    audio.removeAttribute("src");
    audio.load();
  });
})();
