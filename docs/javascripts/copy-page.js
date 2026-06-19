/**
 * Self-hosted "Copy page for LLM" control for the Dango docs.
 *
 * Replaces the mkdocs-copy-to-llm plugin with a WorkOS-style split button:
 * a primary "Copy page" action plus a dropdown (copy / view Markdown, open in
 * ChatGPT / Claude / Cursor / Perplexity).
 *
 * The same-origin Markdown twin URL is read from the <meta name="llm:md-url">
 * tag injected by docs/hooks/llm_md.py, so no path guessing is needed.
 */
(function () {
  "use strict";

  var PROMPT = function (mdAbs) {
    return "I have a question about this documentation page: " + mdAbs;
  };

  var ICONS = {
    copy: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M16 1H4a2 2 0 0 0-2 2v14h2V3h12V1zm3 4H8a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2zm0 16H8V7h11v14z"/></svg>',
    chevron: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M7 10l5 5 5-5z"/></svg>',
    link: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M3.9 12a3.1 3.1 0 0 1 3.1-3.1h4V7H7a5 5 0 0 0 0 10h4v-1.9H7A3.1 3.1 0 0 1 3.9 12zM8 13h8v-2H8v2zm9-6h-4v1.9h4a3.1 3.1 0 1 1 0 6.2h-4V17h4a5 5 0 0 0 0-10z"/></svg>',
    markdown: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M22.27 19.385H1.73A1.73 1.73 0 0 1 0 17.655V6.345a1.73 1.73 0 0 1 1.73-1.73h20.54A1.73 1.73 0 0 1 24 6.345v11.308a1.73 1.73 0 0 1-1.73 1.731zM5.769 15.923v-4.5l2.308 2.885l2.307-2.885v4.5h2.308V8.078h-2.308l-2.307 2.885l-2.308-2.885H3.46v7.847zM21.232 12h-2.309V8.077h-2.307V12h-2.308l3.461 4.039z"/></svg>',
    external: '<svg viewBox="0 0 24 24" width="14" height="14" class="llm-ext" aria-hidden="true"><path fill="currentColor" d="M14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/></svg>',
    chatgpt: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M22.282 9.821a6 6 0 0 0-.516-4.91a6.05 6.05 0 0 0-6.51-2.9A6.065 6.065 0 0 0 4.981 4.18a6 6 0 0 0-3.998 2.9a6.05 6.05 0 0 0 .743 7.097a5.98 5.98 0 0 0 .51 4.911a6.05 6.05 0 0 0 6.515 2.9A6 6 0 0 0 13.26 24a6.06 6.06 0 0 0 5.772-4.206a6 6 0 0 0 3.997-2.9a6.06 6.06 0 0 0-.747-7.073M13.26 22.43a4.48 4.48 0 0 1-2.876-1.04l.141-.081l4.779-2.758a.8.8 0 0 0 .392-.681v-6.737l2.02 1.168a.07.07 0 0 1 .038.052v5.583a4.504 4.504 0 0 1-4.494 4.494M3.6 18.304a4.47 4.47 0 0 1-.535-3.014l.142.085l4.783 2.759a.77.77 0 0 0 .78 0l5.843-3.369v2.332a.08.08 0 0 1-.033.062L9.74 19.95a4.5 4.5 0 0 1-6.14-1.646M2.34 7.896a4.5 4.5 0 0 1 2.366-1.973V11.6a.77.77 0 0 0 .388.677l5.815 3.354l-2.02 1.168a.08.08 0 0 1-.071 0l-4.83-2.786A4.504 4.504 0 0 1 2.34 7.872zm16.597 3.855l-5.833-3.387L15.119 7.2a.08.08 0 0 1 .071 0l4.83 2.791a4.494 4.494 0 0 1-.676 8.105v-5.678a.79.79 0 0 0-.407-.667m2.01-3.023l-.141-.085l-4.774-2.782a.78.78 0 0 0-.785 0L9.409 9.23V6.897a.07.07 0 0 1 .028-.061l4.83-2.787a4.5 4.5 0 0 1 6.68 4.66zm-12.64 4.135l-2.02-1.164a.08.08 0 0 1-.038-.057V6.075a4.5 4.5 0 0 1 7.375-3.453l-.142.08L8.704 5.46a.8.8 0 0 0-.393.681zm1.097-2.365l2.602-1.5l2.607 1.5v2.999l-2.597 1.5l-2.607-1.5Z"/></svg>',
    claude: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M17.304 3.541h-3.672l6.696 16.918H24Zm-10.608 0L0 20.459h3.744l1.37-3.553h7.005l1.369 3.553h3.744L10.536 3.541Zm-.371 10.223L8.616 7.82l2.291 5.945Z"/></svg>',
    cursor: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M3 6.5 12 1l9 5.5v11L12 23l-9-5.5v-11Zm9 .5L4.8 7.2 12 11.4l7.2-4.2L12 7Zm-7.5 1.6v7.1L11 19.7v-7.1L4.5 8.6Zm15 0L13 12.6v7.1l6.5-3.9V8.6Z"/></svg>',
    perplexity: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path fill="currentColor" d="M12 2.5 19 7v10l-7 4.5L5 17V7l7-4.5Zm0 2.3L7 8v8l5 3.2L17 16V8l-5-3.2ZM11.25 7.5h1.5v9h-1.5v-9Z"/></svg>',
  };

  var PROVIDERS = [
    {
      label: "Open in ChatGPT",
      icon: ICONS.chatgpt,
      url: function (p) {
        return "https://chatgpt.com/?q=" + encodeURIComponent(p);
      },
    },
    {
      label: "Open in Claude",
      icon: ICONS.claude,
      url: function (p) {
        return "https://claude.ai/new?q=" + encodeURIComponent(p);
      },
    },
    {
      label: "Open in Cursor",
      icon: ICONS.cursor,
      url: function (p) {
        return "https://cursor.com/link/prompt?text=" + encodeURIComponent(p);
      },
    },
    {
      label: "Open in Perplexity",
      icon: ICONS.perplexity,
      url: function (p) {
        return "https://www.perplexity.ai/?q=" + encodeURIComponent(p);
      },
    },
  ];

  function getMdUrls() {
    var meta = document.querySelector('meta[name="llm:md-url"]');
    var rel = meta && meta.getAttribute("content");
    if (!rel) return null;
    return { abs: new URL(rel, location.href).href };
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      try {
        var ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        document.body.removeChild(ta);
        resolve();
      } catch (e) {
        reject(e);
      }
    });
  }

  var toastTimer;
  function toast(message) {
    var el = document.querySelector(".llm-toast");
    if (!el) {
      el = document.createElement("div");
      el.className = "llm-toast";
      document.body.appendChild(el);
    }
    el.textContent = message;
    el.classList.add("llm-toast--show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      el.classList.remove("llm-toast--show");
    }, 2200);
  }

  function menuItem(icon, label, external) {
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "llm-menu-item";
    btn.setAttribute("role", "menuitem");
    btn.innerHTML =
      icon +
      '<span class="llm-menu-label">' +
      label +
      "</span>" +
      (external ? ICONS.external : "");
    return btn;
  }

  function build() {
    var content = document.querySelector(".md-content__inner");
    var h1 = content && content.querySelector("h1");
    if (!h1 || content.querySelector(".llm-copy")) return;

    var urls = getMdUrls();
    if (!urls) return;

    // Wrap the title so the control can sit at the top-right of the page.
    var row = document.createElement("div");
    row.className = "llm-title-row";
    h1.parentNode.insertBefore(row, h1);
    row.appendChild(h1);

    var group = document.createElement("div");
    group.className = "llm-copy";

    var copyBtn = document.createElement("button");
    copyBtn.type = "button";
    copyBtn.className = "llm-btn llm-btn-main";
    copyBtn.innerHTML = ICONS.copy + '<span class="llm-btn-text">Copy page</span>';

    var caret = document.createElement("button");
    caret.type = "button";
    caret.className = "llm-btn llm-btn-caret";
    caret.setAttribute("aria-haspopup", "menu");
    caret.setAttribute("aria-expanded", "false");
    caret.setAttribute("aria-label", "More copy options");
    caret.innerHTML = ICONS.chevron;

    var menu = document.createElement("div");
    menu.className = "llm-menu";
    menu.setAttribute("role", "menu");
    menu.hidden = true;

    var copyMd = menuItem(ICONS.copy, "Copy page as Markdown", false);
    var copyLink = menuItem(ICONS.link, "Copy markdown link", false);
    var viewMd = menuItem(ICONS.markdown, "View Markdown", true);
    menu.appendChild(copyMd);
    menu.appendChild(copyLink);
    menu.appendChild(viewMd);

    PROVIDERS.forEach(function (provider) {
      var item = menuItem(provider.icon, provider.label, true);
      item.addEventListener("click", function () {
        closeMenu();
        window.open(provider.url(PROMPT(urls.abs)), "_blank", "noopener");
      });
      menu.appendChild(item);
    });

    function openMenu() {
      menu.hidden = false;
      caret.setAttribute("aria-expanded", "true");
      document.addEventListener("click", onOutside, true);
      document.addEventListener("keydown", onKey, true);
    }
    function closeMenu() {
      menu.hidden = true;
      caret.setAttribute("aria-expanded", "false");
      document.removeEventListener("click", onOutside, true);
      document.removeEventListener("keydown", onKey, true);
    }
    function onOutside(e) {
      if (!group.contains(e.target)) closeMenu();
    }
    function onKey(e) {
      if (e.key === "Escape") {
        closeMenu();
        caret.focus();
      }
    }

    caret.addEventListener("click", function () {
      if (menu.hidden) openMenu();
      else closeMenu();
    });

    function doCopyPage() {
      fetch(urls.abs)
        .then(function (r) {
          if (!r.ok) throw new Error(String(r.status));
          return r.text();
        })
        .then(function (text) {
          return copyText(text);
        })
        .then(function () {
          toast("Page copied as Markdown");
        })
        .catch(function () {
          toast("Couldn't copy this page");
        });
    }

    copyBtn.addEventListener("click", doCopyPage);
    copyMd.addEventListener("click", function () {
      closeMenu();
      doCopyPage();
    });
    copyLink.addEventListener("click", function () {
      closeMenu();
      copyText(urls.abs).then(function () {
        toast("Markdown link copied");
      });
    });
    viewMd.addEventListener("click", function () {
      closeMenu();
      window.open(urls.abs, "_blank", "noopener");
    });

    group.appendChild(copyBtn);
    group.appendChild(caret);
    group.appendChild(menu);
    row.appendChild(group);
  }

  // Material for MkDocs exposes a `document$` observable that fires on every
  // (instant) navigation; fall back to a plain load event otherwise.
  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(build);
  } else if (document.readyState !== "loading") {
    build();
  } else {
    document.addEventListener("DOMContentLoaded", build);
  }
})();
