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

document.addEventListener("DOMContentLoaded", () => {
  // Initial state (for values loaded from server)
  updatePreview();

  // Live update when typing
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
    if (input) {
      input.addEventListener("input", updatePreview);
    }
  });
});
