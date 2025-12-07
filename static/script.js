// 🌸 ----------- LIVE PREVIEW UPDATE -----------

const nameInput = document.getElementById("name");
const bioInput = document.getElementById("bio");
const instagramInput = document.getElementById("instagram");
const twitterInput = document.getElementById("twitter");
const youtubeInput = document.getElementById("youtube");
const linkedinInput = document.getElementById("linkedin");
const githubInput = document.getElementById("github");
const customLabelInput = document.getElementById("customLabel");
const customUrlInput = document.getElementById("customUrl");

const previewName = document.getElementById("previewName");
const previewBio = document.getElementById("previewBio");
const linkInstagram = document.getElementById("linkInstagram");
const linkTwitter = document.getElementById("linkTwitter");
const linkYoutube = document.getElementById("linkYoutube");
const linkLinkedin = document.getElementById("linkLinkedin");
const linkGithub = document.getElementById("linkGithub");
const linkCustom = document.getElementById("linkCustom");
const linkCustomLabel = document.getElementById("linkCustomLabel");

function toggleLink(anchorEl, url) {
  if (!anchorEl) return;
  const trimmed = (url || "").trim();
  if (trimmed !== "") {
    anchorEl.style.display = "flex";
    anchorEl.href = trimmed;
  } else {
    anchorEl.style.display = "none";
  }
}

function updatePreview() {
  // Name + bio
  if (previewName && nameInput) {
    const name = (nameInput.value || "").trim();
    previewName.textContent = name || "Your Name";
  }

  if (previewBio && bioInput) {
    const bio = (bioInput.value || "").trim();
    previewBio.textContent =
      bio || "Your bio will appear here. Make it short, cute, and very you.";
  }

  // Links
  if (instagramInput) toggleLink(linkInstagram, instagramInput.value);
  if (twitterInput) toggleLink(linkTwitter, twitterInput.value);
  if (youtubeInput) toggleLink(linkYoutube, youtubeInput.value);
  if (linkedinInput) toggleLink(linkLinkedin, linkedinInput.value);
  if (githubInput) toggleLink(linkGithub, githubInput.value);

  if (linkCustom && customUrlInput) {
    const customLabel = (customLabelInput?.value || "").trim();
    const customUrl = (customUrlInput.value || "").trim();
    if (customUrl !== "") {
      linkCustom.style.display = "flex";
      linkCustom.href = customUrl;
      if (linkCustomLabel) {
        linkCustomLabel.textContent = customLabel || "Custom Link";
      }
    } else {
      linkCustom.style.display = "none";
    }
  }
}

// Run live preview listeners
document.addEventListener("DOMContentLoaded", () => {
  updatePreview();
  [
    nameInput,
    bioInput,
    instagramInput,
    twitterInput,
    youtubeInput,
    linkedinInput,
    githubInput,
    customLabelInput,
    customUrlInput,
  ].forEach((input) => {
    if (input) input.addEventListener("input", updatePreview);
  });
});

// 🌟 ----------- COPY PROFILE LINK FEATURE -----------

document.addEventListener("DOMContentLoaded", () => {
  const copyBtn = document.getElementById("copyLinkBtn");
  const publicLink = document.getElementById("publicLink");

  if (!copyBtn || !publicLink) return;

  copyBtn.addEventListener("click", async () => {
    const baseUrl = window.location.origin;
    const fullUrl = `${baseUrl}${publicLink.textContent.trim()}`;

    try {
      await navigator.clipboard.writeText(fullUrl);
      showCopyToast(`✅ Link copied: ${fullUrl}`);
    } catch (err) {
      showCopyToast("❌ Unable to copy link");
      console.error("Clipboard error:", err);
    }
  });
});

// 💫 ----------- TOAST MESSAGE ANIMATION -----------

function showCopyToast(message) {
  let toast = document.getElementById("copyToast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "copyToast";
    toast.style.position = "fixed";
    toast.style.top = "20px";
    toast.style.right = "20px";
    toast.style.padding = "10px 18px";
    toast.style.background = "linear-gradient(135deg,#6366f1,#ec4899)";
    toast.style.color = "#fff";
    toast.style.fontSize = "0.9rem";
    toast.style.borderRadius = "12px";
    toast.style.boxShadow = "0 8px 24px rgba(0,0,0,0.3)";
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.3s ease, transform 0.3s ease";
    toast.style.zIndex = "9999";
    document.body.appendChild(toast);
  }

  toast.textContent = message;
  toast.style.opacity = "1";
  toast.style.transform = "translateY(0)";
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(-10px)";
  }, 2500);
}
