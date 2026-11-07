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
    var duration = Number.isFinite(video.duration) ? video.duration : 90;
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

})();

(function () {
  var toggle = document.getElementById("theme-toggle");
  if (!toggle) return;

  function current() {
    return document.documentElement.getAttribute("data-theme") === "light" ? "light" : "dark";
  }

  function paint(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", theme === "light" ? "#f4f5f1" : "#090b11");
    toggle.setAttribute("aria-label", theme === "light" ? "Switch to dark mode" : "Switch to light mode");
  }

  paint(current());
  toggle.addEventListener("click", function () {
    var next = current() === "dark" ? "light" : "dark";
    try {
      localStorage.setItem("theme", next);
    } catch (error) {
      /* keep the choice for this view */
    }
    paint(next);
  });
})();

(function () {
  var button = document.getElementById("menu-toggle");
  var nav = document.getElementById("nav-links");
  if (!button || !nav) return;

  function set(open) {
    nav.classList.toggle("open", open);
    button.setAttribute("aria-expanded", open ? "true" : "false");
  }

  button.addEventListener("click", function () {
    set(!nav.classList.contains("open"));
  });
  nav.addEventListener("click", function (event) {
    if (event.target.closest("a")) set(false);
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && nav.classList.contains("open")) {
      set(false);
      button.focus();
    }
  });
})();

(function () {
  var links = Array.prototype.slice.call(document.querySelectorAll(".nav-links a"));
  var sections = links.map(function (link) {
    return document.getElementById(link.getAttribute("href").slice(1));
  }).filter(Boolean);

  function paint() {
    var current = null;
    sections.forEach(function (section) {
      if (section.getBoundingClientRect().top <= 160) current = section;
    });
    links.forEach(function (link) {
      if (current && link.getAttribute("href") === "#" + current.id) link.setAttribute("aria-current", "true");
      else link.removeAttribute("aria-current");
    });
  }

  paint();
  window.addEventListener("scroll", paint, { passive: true });
  window.addEventListener("resize", paint);
})();

(function () {
  var filters = Array.prototype.slice.call(document.querySelectorAll(".filter"));
  var cards = Array.prototype.slice.call(document.querySelectorAll(".project"));

  filters.forEach(function (filter) {
    filter.addEventListener("click", function () {
      var wanted = filter.getAttribute("data-filter");
      filters.forEach(function (other) {
        other.setAttribute("aria-pressed", other === filter ? "true" : "false");
      });
      cards.forEach(function (card) {
        var tags = (card.getAttribute("data-category") || "").split(" ");
        card.hidden = !(wanted === "all" || tags.indexOf(wanted) !== -1);
      });
    });
  });
})();

(function () {
  var backdrop = document.getElementById("modal-backdrop");
  var close = document.getElementById("modal-close");
  var title = document.getElementById("modal-title");
  var body = document.getElementById("modal-body");
  if (!backdrop || !close || !title || !body) return;
  var opener = null;

  function shut() {
    backdrop.classList.remove("open");
    document.body.style.overflow = "";
    if (opener) opener.focus();
  }

  Array.prototype.forEach.call(document.querySelectorAll(".project-link"), function (button) {
    button.addEventListener("click", function () {
      var card = button.closest(".project");
      var detail = card.querySelector(".project-detail");
      opener = button;
      title.textContent = card.querySelector("h3").textContent;
      body.replaceChildren();
      Array.prototype.forEach.call(detail.children, function (node) {
        body.appendChild(node.cloneNode(true));
      });
      backdrop.classList.add("open");
      document.body.style.overflow = "hidden";
      close.focus();
    });
  });

  close.addEventListener("click", shut);
  backdrop.addEventListener("click", function (event) {
    if (event.target === backdrop) shut();
  });
  document.addEventListener("keydown", function (event) {
    if (!backdrop.classList.contains("open")) return;
    if (event.key === "Escape") {
      shut();
      return;
    }
    if (event.key !== "Tab") return;
    var nodes = backdrop.querySelectorAll("a, button");
    var first = nodes[0];
    var last = nodes[nodes.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });
})();

(function () {
  var year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());

  var items = document.querySelectorAll(".reveal");
  if (!("IntersectionObserver" in window)) {
    Array.prototype.forEach.call(items, function (item) {
      item.classList.add("visible");
    });
    return;
  }
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.09 });
  Array.prototype.forEach.call(items, function (item) {
    observer.observe(item);
  });
})();
