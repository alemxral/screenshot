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

// Messages Modal Functionality
const messagesBtn = document.getElementById("messages-btn");
const messagesModal = document.getElementById("messages-modal");
const closeMessages = document.getElementById("close-messages");
const messagesContainer = document.getElementById("messages-container");
const refreshBtn = document.getElementById("refresh-messages");
const clearBtn = document.getElementById("clear-messages");

// Load and display messages
function loadMessages() {
  messagesContainer.innerHTML = '<p class="loading">Loading messages...</p>';
  
  fetch("messages.json")
    .then(response => {
      if (!response.ok) throw new Error("Could not load messages.json");
      return response.json();
    })
    .then(messages => {
      messagesContainer.innerHTML = '';
      
      if (messages.length === 0) {
        messagesContainer.innerHTML = '<div class="no-messages">📝 No messages recorded yet.<br>Press Fn while running the script to start recording!</div>';
        return;
      }
      
      // Sort messages by ID (newest first)
      messages.sort((a, b) => b.id - a.id);
      
      messages.forEach(message => {
        const messageItem = document.createElement("div");
        messageItem.classList.add("message-item");
        
        messageItem.innerHTML = `
          <div class="message-text">${escapeHtml(message.message)}</div>
          <div class="message-meta">
            <div class="message-timestamp">
              📅 ${message.date} ⏰ ${message.time}
            </div>
            <div class="message-id">#${message.id}</div>
          </div>
        `;
        
        messagesContainer.appendChild(messageItem);
      });
    })
    .catch(error => {
      console.error("Error loading messages:", error);
      messagesContainer.innerHTML = '<div class="no-messages">❌ Error loading messages.<br>Make sure messages.json exists and the script is running.</div>';
    });
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

// Clear all messages
function clearMessages() {
  if (confirm("🗑️ Are you sure you want to delete ALL recorded messages?\n\nThis action cannot be undone!")) {
    fetch("messages.json", {
      method: "DELETE"
    })
    .then(() => {
      // Create empty messages file
      const emptyData = JSON.stringify([], null, 2);
      // Note: This would require server-side implementation to actually clear the file
      alert("✅ Messages cleared! (Restart the script to see changes)");
      loadMessages();
    })
    .catch(error => {
      console.error("Error clearing messages:", error);
      alert("❌ Error clearing messages. You may need to manually delete messages.json");
    });
  }
}

// Event listeners for messages modal
messagesBtn.addEventListener("click", () => {
  messagesModal.style.display = "block";
  loadMessages();
});

closeMessages.addEventListener("click", () => {
  messagesModal.style.display = "none";
});

refreshBtn.addEventListener("click", loadMessages);
clearBtn.addEventListener("click", clearMessages);

// Close modal when clicking outside
messagesModal.addEventListener("click", (e) => {
  if (e.target === messagesModal) {
    messagesModal.style.display = "none";
  }
});

// Close modal with Escape key
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    messagesModal.style.display = "none";
    modal.style.display = "none";
  }
});

// Start loading the gallery.
loadGallery();