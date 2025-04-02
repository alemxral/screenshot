// Get references to the DOM elements.
const gallery = document.getElementById("gallery");
const modal = document.getElementById("modal");
const modalImage = document.getElementById("modal-image");
const basePath = "screenshots/";

// Load registry.json and display each unique image with its filename and upload time.
function loadGallery() {
  fetch("registry.json")
    .then(response => {
      if (!response.ok) throw new Error("Could not load registry.json");
      return response.json();
    })
    .then(data => {
      const seen = new Set(); // To avoid duplicate filenames.
      data.forEach(({ filename, upload_time }) => {
        if (seen.has(filename)) return;
        seen.add(filename);

        const imgPath = `${basePath}${filename}`;
        const imgContainer = document.createElement("div");
        imgContainer.classList.add("img-container");

        const img = new Image();
        img.src = imgPath;
        img.alt = filename;

        img.onload = () => {
          // Create a caption that shows both the filename and upload time.
          const caption = document.createElement("div");
          caption.classList.add("caption");
          caption.textContent = `${filename} - Uploaded: ${upload_time}`;
          imgContainer.appendChild(img);
          imgContainer.appendChild(caption);
          gallery.appendChild(imgContainer);
        };

        img.addEventListener("click", () => {
          modalImage.src = img.src;
          modal.style.display = "flex";
        });

        img.onerror = () => console.error(`Image not found: ${imgPath}`);
      });
    })
    .catch(error => console.error("Error loading registry:", error));
}

// Close the modal when clicking anywhere on it.
modal.addEventListener("click", () => {
  modal.style.display = "none";
});

// Start loading the gallery.
loadGallery();
