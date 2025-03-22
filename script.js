function loadGallery() {
    fetch('registry.json')
      .then(response => {
        if (!response.ok) {
          throw new Error('Could not load registry.json');
        }
        return response.json();
      })
      .then(data => {
        // ✅ Sort alphabetically by filename
        data.sort((a, b) => a.filename.localeCompare(b.filename));
  
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
  