// gallery.js

// Get references to the DOM elements for the gallery and modal.
const gallery = document.getElementById("gallery");
const modal = document.getElementById("modal");
const modalImage = document.getElementById("modal-image");

const NUM_IMAGES = 50; // Maximum images to check/load
const basePath = "screenshots/";

function preloadImages() {
  for (let i = 1; i <= NUM_IMAGES; i++) {
    const imgPath = `${basePath}img${i}.png`;
    const img = new Image();
    img.src = imgPath;
    img.alt = `Screenshot ${i}`;

    img.onload = () => {
      gallery.appendChild(img);
      // When the image is clicked, open the modal with an enlarged version.
      img.addEventListener("click", () => {
        modalImage.src = img.src;
        modal.style.display = "flex";
      });
    };

    img.onerror = () => {
      console.error(`Image not found: ${imgPath}`);
    };
  }
}

// Close the modal when clicking anywhere on it.
modal.addEventListener("click", () => {
  modal.style.display = "none";
});

// Start preloading images.
preloadImages();
