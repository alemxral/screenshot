// Get references to the DOM elements for the gallery and modal.
const gallery = document.getElementById("gallery");
const modal = document.getElementById("modal");
const modalImage = document.getElementById("modal-image");
const basePath = "screenshots/";

// Helper function to convert the upload_time string to a Date.
// This expects the format "YYYY-MM-DD HH:MM:SS" and converts it to "YYYY-MM-DDTHH:MM:SS".
function parseUploadTime(upload_time) {
  return new Date(upload_time.replace(" ", "T"));
}

// Load the registry.json file and populate the gallery.
function loadGallery() {
  fetch('registry.json')
    .then(response => {
      if (!response.ok) {
        throw new Error('Could not load registry.json');
      }
      return response.json();
    })
    .then(data => {
      // Sort the data by upload_time (newest first)
      data.sort((a, b) => parseUploadTime(b.upload_time) - parseUploadTime(a.upload_time));
      
      data.forEach(entry => {
        const { filename, upload_time } = entry;
        const imgPath = `${basePath}${filename}`;

        const imgContainer = document.createElement("div");
        imgContainer.classList.add("img-container");

        const img = new Image();
        img.src = imgPath;
        img.alt = `Screenshot ${filename}`;
        img.classList.add("screenshot");

        img.onload = () => {
          const caption = document.createElement("div");
          caption.classList.add("caption");
          caption.textContent = `${filename} - Uploaded: ${upload_time}`;

          imgContainer.appendChild(img);
          imgContainer.appendChild(caption);
          gallery.appendChild(imgContainer);

          img.addEventListener("click", () => {
            modalImage.src = img.src;
            modal.style.display = "flex";
          });
        };

        img.onerror = () => {
          console.error(`Image not found: ${imgPath}`);
        };
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
