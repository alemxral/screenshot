// gallery.js

// Get references to the DOM elements for the gallery and modal.
const gallery = document.getElementById("gallery");
const modal = document.getElementById("modal");
const modalImage = document.getElementById("modal-image");
const basePath = "screenshots/";

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
      // data is an array of objects, each with "filename" and "upload_time"
      data.forEach(entry => {
        const { filename, upload_time } = entry;
        const imgPath = `${basePath}${filename}`;

        // Create a container div for the image and its caption.
        const imgContainer = document.createElement("div");
        imgContainer.classList.add("img-container");

        const img = new Image();
        img.src = imgPath;
        img.alt = `Screenshot ${filename}`;
        img.classList.add("screenshot");

        img.onload = () => {
          // Create a caption element with the image filename and upload date/time.
          const caption = document.createElement("div");
          caption.classList.add("caption");
          caption.textContent = `${filename} - Uploaded: ${upload_time}`;

          // Append the image and its caption to the container
          imgContainer.appendChild(img);
          imgContainer.appendChild(caption);
          gallery.appendChild(imgContainer);

          // When the image is clicked, open the modal with an enlarged version.
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
