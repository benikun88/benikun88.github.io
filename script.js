(function () {
  var video = document.getElementById("demo-video");
  var play = document.getElementById("play-toggle");
  var seek = document.getElementById("seek");
  var readout = document.getElementById("time-readout");
  var captions = document.getElementById("caption-toggle");
  var fullscreen = document.getElementById("full-toggle");
  var stage = document.querySelector(".stage");
  var buttons = Array.prototype.slice.call(document.querySelectorAll("[data-start]"));

  if (!video || !play || !seek) {
    return;
  }

  video.controls = false;

  function showMissingFile() {
    var note = document.getElementById("video-status");
    if (note) {
      note.hidden = false;
    }
  }

  function missing() {
    return Boolean(video.error) || video.networkState === 3;
  }

  function checkMissing() {
    if (missing()) {
      showMissingFile();
    }
  }

  function clock(seconds) {
    if (!Number.isFinite(seconds)) {
      return "0:00";
    }
    var whole = Math.max(0, Math.floor(seconds));
    var minutes = Math.floor(whole / 60);
    var remain = whole % 60;
    return minutes + ":" + (remain < 10 ? "0" : "") + remain;
  }

  function paint() {
    var duration = Number.isFinite(video.duration) ? video.duration : 60;
    readout.textContent = clock(video.currentTime) + " / " + clock(video.duration);
    if (document.activeElement !== seek) {
      seek.max = String(duration);
      seek.value = String(video.currentTime || 0);
    }
    seek.setAttribute("aria-valuetext", clock(video.currentTime));

    var active = null;
    buttons.forEach(function (button) {
      if (Number(button.getAttribute("data-start")) <= video.currentTime) {
        active = button;
      }
    });
    buttons.forEach(function (button) {
      if (button === active) {
        button.setAttribute("aria-current", "true");
      } else {
        button.removeAttribute("aria-current");
      }
    });
  }

  function setPlayLabel(playing) {
    play.textContent = playing ? "Pause" : "Play";
  }

  play.addEventListener("click", function () {
    if (missing()) {
      showMissingFile();
      return;
    }
    if (video.paused) {
      var pending = video.play();
      if (pending && typeof pending.catch === "function") {
        pending.catch(showMissingFile);
      }
    } else {
      video.pause();
    }
  });

  video.addEventListener("play", function () {
    setPlayLabel(true);
  });
  video.addEventListener("pause", function () {
    setPlayLabel(false);
  });
  video.addEventListener("timeupdate", paint);
  video.addEventListener("loadedmetadata", paint);
  video.addEventListener("error", checkMissing);
  Array.prototype.forEach.call(video.querySelectorAll("source"), function (source) {
    source.addEventListener("error", checkMissing);
  });
  window.setTimeout(checkMissing, 400);

  seek.addEventListener("input", function () {
    if (missing()) {
      showMissingFile();
      return;
    }
    video.currentTime = Number(seek.value);
    paint();
  });

  if (captions) {
    captions.addEventListener("click", function () {
      var track = video.textTracks && video.textTracks[0];
      if (!track) {
        return;
      }
      var on = track.mode !== "showing";
      track.mode = on ? "showing" : "hidden";
      captions.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }

  if (fullscreen && stage && stage.requestFullscreen) {
    fullscreen.addEventListener("click", function () {
      if (document.fullscreenElement) {
        document.exitFullscreen();
      } else {
        stage.requestFullscreen();
      }
    });
  }

  buttons.forEach(function (button) {
    button.addEventListener("click", function () {
      var start = Number(button.getAttribute("data-start"));
      if (!Number.isFinite(start)) {
        return;
      }
      if (missing()) {
        showMissingFile();
        return;
      }
      function seekTo() {
        if (missing()) {
          showMissingFile();
          return;
        }
        video.currentTime = start;
        var pending = video.play();
        if (pending && typeof pending.catch === "function") {
          pending.catch(showMissingFile);
        }
      }
      if (video.readyState >= 1) {
        seekTo();
      } else {
        video.addEventListener("loadedmetadata", seekTo, { once: true });
        video.addEventListener("error", showMissingFile, { once: true });
        video.load();
      }
    });
  });

  var motion = window.matchMedia("(prefers-reduced-motion: reduce)");
  if (document.startViewTransition) {
    document.addEventListener("click", function (event) {
      if (motion.matches || event.defaultPrevented || event.button !== 0) {
        return;
      }
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
        return;
      }
      var link = event.target.closest("a[href^='#']");
      if (!link) {
        return;
      }
      var id = link.getAttribute("href").slice(1);
      var target = document.getElementById(id);
      if (!target) {
        return;
      }
      event.preventDefault();
      document.startViewTransition(function () {
        target.scrollIntoView();
        history.pushState(null, "", "#" + id);
      });
    });
  }
})();
