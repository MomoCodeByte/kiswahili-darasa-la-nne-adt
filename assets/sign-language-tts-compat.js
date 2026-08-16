(function () {
  "use strict";

  const nativePause = HTMLMediaElement.prototype.pause;
  const nativePlay = HTMLMediaElement.prototype.play;
  const audioPlayers = new Set();
  const isSignVideo = (media) =>
    media instanceof HTMLVideoElement &&
    /\/content\/i18n\/[^/]+\/video\/page_\d+\.mp4(?:[?#]|$)/i.test(
      media.currentSrc || media.src || "",
    );

  const prepareSignVideo = (video) => {
    if (!isSignVideo(video)) return;
    video.muted = true;
    video.defaultMuted = true;
    video.volume = 0;
    video.setAttribute("muted", "");
  };

  HTMLMediaElement.prototype.pause = function () {
    if (isSignVideo(this)) return;
    return nativePause.call(this);
  };

  HTMLMediaElement.prototype.play = function () {
    if (this instanceof HTMLAudioElement) {
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
        if (node instanceof HTMLVideoElement) prepareSignVideo(node);
        node.querySelectorAll?.("video").forEach(prepareSignVideo);
      }
    }
  }).observe(document.documentElement, { childList: true, subtree: true });
})();
