(function () {
  var video = document.getElementById("demo-video");
  if (!video) {
    return;
  }

  var buttons = Array.prototype.slice.call(
    document.querySelectorAll("[data-start]")
  );

  function showMissingFile() {
    var note = document.getElementById("video-status");
    if (note) {
      note.hidden = false;
    }
  }

  function checkMissing() {
    if (video.error || video.networkState === 3) {
      showMissingFile();
    }
  }

  video.addEventListener("error", checkMissing);
  Array.prototype.forEach.call(video.querySelectorAll("source"), function (source) {
    source.addEventListener("error", checkMissing);
  });
  window.setTimeout(checkMissing, 400);

  buttons.forEach(function (button) {
    button.addEventListener("click", function () {
      var start = Number(button.getAttribute("data-start"));
      if (!Number.isFinite(start)) {
        return;
      }

      function seek() {
        if (video.error) {
          showMissingFile();
          return;
        }
        video.currentTime = start;
        var pending = video.play();
        if (pending && typeof pending.catch === "function") {
          pending.catch(function () {
            showMissingFile();
          });
        }
      }

      if (video.error || video.networkState === 3) {
        showMissingFile();
        return;
      }
      if (video.readyState >= 1) {
        seek();
      } else {
        video.addEventListener("loadedmetadata", seek, { once: true });
        video.addEventListener("error", showMissingFile, { once: true });
        video.load();
      }
    });
  });

  video.addEventListener("timeupdate", function () {
    var time = video.currentTime;
    var active = null;
    buttons.forEach(function (button) {
      if (Number(button.getAttribute("data-start")) <= time) {
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
  });
})();
