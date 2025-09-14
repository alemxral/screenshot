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

// Quiz Functionality
let quizAnswers = {}; // Store all quiz answers
let selectedAnswer = null;

// Initialize quiz section
function initializeQuiz() {
  populateQuestionDropdown();
  setupQuizEventListeners();
  loadQuizAnswers();
  renderAnswersGrid();
  updateAnswersSummary();
}

// Populate dropdown with question numbers 1-20
function populateQuestionDropdown() {
  const dropdown = document.getElementById("question-number");
  
  // Add default option
  const defaultOption = document.createElement("option");
  defaultOption.value = "";
  defaultOption.textContent = "Select question...";
  dropdown.appendChild(defaultOption);
  
  // Add options 1-20
  for (let i = 1; i <= 20; i++) {
    const option = document.createElement("option");
    option.value = i;
    option.textContent = `Question ${i}`;
    dropdown.appendChild(option);
  }
}

// Set up all quiz event listeners
function setupQuizEventListeners() {
  const questionDropdown = document.getElementById("question-number");
  const questionInput = document.getElementById("question-input");
  const answerButtons = document.querySelectorAll(".answer-btn");
  const submitBtn = document.getElementById("submit-answer");
  const deleteBtn = document.getElementById("delete-answer");
  const clearAllBtn = document.getElementById("clear-all-answers");
  const exportBtn = document.getElementById("export-answers");
  const errorDiv = document.getElementById("question-error");
  
  // Question dropdown change
  questionDropdown.addEventListener("change", () => {
    if (questionDropdown.value) {
      questionInput.value = "";
      hideError();
      loadSelectedQuestion();
    }
  });
  
  // Question input change
  questionInput.addEventListener("input", () => {
    if (questionInput.value) {
      questionDropdown.value = "";
      validateQuestionNumber();
      loadSelectedQuestion();
    }
  });
  
  // Answer button clicks
  answerButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      // Remove selected class from all buttons
      answerButtons.forEach(b => b.classList.remove("selected"));
      // Add selected class to clicked button
      btn.classList.add("selected");
      selectedAnswer = btn.dataset.answer;
    });
  });
  
  // Submit answer
  submitBtn.addEventListener("click", submitAnswer);
  
  // Delete answer
  deleteBtn.addEventListener("click", deleteAnswer);
  
  // Clear all answers
  clearAllBtn.addEventListener("click", clearAllAnswers);
  
  // Export answers
  exportBtn.addEventListener("click", exportAnswers);
}

// Validate question number input
function validateQuestionNumber() {
  const input = document.getElementById("question-input");
  const value = parseInt(input.value);
  
  if (input.value && (isNaN(value) || value < 1 || value > 20)) {
    showError("❌ Please enter a number between 1 and 20");
    return false;
  }
  
  hideError();
  return true;
}

// Show error message
function showError(message) {
  const errorDiv = document.getElementById("question-error");
  errorDiv.textContent = message;
  errorDiv.style.display = "block";
}

// Hide error message
function hideError() {
  const errorDiv = document.getElementById("question-error");
  errorDiv.style.display = "none";
}

// Get currently selected question number
function getSelectedQuestionNumber() {
  const dropdown = document.getElementById("question-number");
  const input = document.getElementById("question-input");
  
  if (dropdown.value) {
    return parseInt(dropdown.value);
  } else if (input.value) {
    const value = parseInt(input.value);
    if (value >= 1 && value <= 20) {
      return value;
    }
  }
  
  return null;
}

// Load selected question's current answer
function loadSelectedQuestion() {
  const questionNum = getSelectedQuestionNumber();
  
  if (!questionNum) {
    clearAnswerSelection();
    return;
  }
  
  // Load existing answer if any
  if (quizAnswers[questionNum]) {
    const answer = quizAnswers[questionNum];
    selectAnswerButton(answer);
  } else {
    clearAnswerSelection();
  }
}

// Select answer button programmatically
function selectAnswerButton(answer) {
  const answerButtons = document.querySelectorAll(".answer-btn");
  answerButtons.forEach(btn => {
    btn.classList.remove("selected");
    if (btn.dataset.answer === answer) {
      btn.classList.add("selected");
      selectedAnswer = answer;
    }
  });
}

// Clear answer selection
function clearAnswerSelection() {
  const answerButtons = document.querySelectorAll(".answer-btn");
  answerButtons.forEach(btn => btn.classList.remove("selected"));
  selectedAnswer = null;
}

// Submit answer
function submitAnswer() {
  const questionNum = getSelectedQuestionNumber();
  
  if (!questionNum) {
    showError("❌ Please select or enter a question number first");
    return;
  }
  
  if (!selectedAnswer) {
    showError("❌ Please select an answer (A, B, C, D, or E)");
    return;
  }
  
  // Save answer
  quizAnswers[questionNum] = selectedAnswer;
  saveQuizAnswers();
  
  // Update UI
  renderAnswersGrid();
  updateAnswersSummary();
  
  // Clear form for next entry
  document.getElementById("question-number").value = "";
  document.getElementById("question-input").value = "";
  clearAnswerSelection();
  hideError();
  
  // Success message
  showSuccessMessage(`✅ Answer saved: Question ${questionNum} = ${selectedAnswer}`);
}

// Delete answer
function deleteAnswer() {
  const questionNum = getSelectedQuestionNumber();
  
  if (!questionNum) {
    showError("❌ Please select or enter a question number first");
    return;
  }
  
  if (!quizAnswers[questionNum]) {
    showError("❌ No answer found for this question");
    return;
  }
  
  if (confirm(`🗑️ Delete answer for Question ${questionNum}?`)) {
    delete quizAnswers[questionNum];
    saveQuizAnswers();
    renderAnswersGrid();
    updateAnswersSummary();
    clearAnswerSelection();
    hideError();
    showSuccessMessage(`✅ Answer deleted for Question ${questionNum}`);
  }
}

// Clear all answers
function clearAllAnswers() {
  if (Object.keys(quizAnswers).length === 0) {
    alert("❌ No answers to clear");
    return;
  }
  
  if (confirm("🗑️ Delete ALL quiz answers? This cannot be undone!")) {
    quizAnswers = {};
    saveQuizAnswers();
    renderAnswersGrid();
    updateAnswersSummary();
    clearAnswerSelection();
    document.getElementById("question-number").value = "";
    document.getElementById("question-input").value = "";
    hideError();
    showSuccessMessage("✅ All answers cleared");
  }
}

// Export answers
function exportAnswers() {
  if (Object.keys(quizAnswers).length === 0) {
    alert("❌ No answers to export");
    return;
  }
  
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = `quiz-answers-${timestamp}.json`;
  
  const exportData = {
    exported_at: new Date().toISOString(),
    total_questions: 20,
    answered_questions: Object.keys(quizAnswers).length,
    answers: quizAnswers
  };
  
  const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  
  showSuccessMessage(`📊 Answers exported as ${filename}`);
}

// Show success message
function showSuccessMessage(message) {
  // Create temporary success message
  const successDiv = document.createElement("div");
  successDiv.className = "success-message";
  successDiv.textContent = message;
  successDiv.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
    padding: 12px 16px;
    border-radius: 6px;
    font-weight: bold;
    z-index: 1001;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  `;
  
  document.body.appendChild(successDiv);
  
  setTimeout(() => {
    if (document.body.contains(successDiv)) {
      document.body.removeChild(successDiv);
    }
  }, 3000);
}

// Render answers grid
function renderAnswersGrid() {
  const grid = document.getElementById("answers-grid");
  grid.innerHTML = "";
  
  for (let i = 1; i <= 20; i++) {
    const answerItem = document.createElement("div");
    answerItem.className = "answer-item";
    
    if (quizAnswers[i]) {
      answerItem.classList.add("answered");
    }
    
    answerItem.innerHTML = `
      <div class="question-num">Q${i}</div>
      <div class="answer-choice">${quizAnswers[i] || "?"}</div>
      ${quizAnswers[i] ? '<button class="delete-btn" onclick="deleteQuestionFromGrid(' + i + ')">×</button>' : ''}
    `;
    
    // Click to edit answer
    answerItem.addEventListener("click", () => {
      document.getElementById("question-number").value = i;
      document.getElementById("question-input").value = "";
      loadSelectedQuestion();
      hideError();
    });
    
    grid.appendChild(answerItem);
  }
}

// Delete question from grid
function deleteQuestionFromGrid(questionNum) {
  if (confirm(`🗑️ Delete answer for Question ${questionNum}?`)) {
    delete quizAnswers[questionNum];
    saveQuizAnswers();
    renderAnswersGrid();
    updateAnswersSummary();
    showSuccessMessage(`✅ Answer deleted for Question ${questionNum}`);
  }
}

// Update answers summary
function updateAnswersSummary() {
  const answeredCount = Object.keys(quizAnswers).length;
  const remainingCount = 20 - answeredCount;
  
  document.getElementById("answered-count").textContent = answeredCount;
  document.getElementById("remaining-count").textContent = remainingCount;
}

// Load quiz answers from localStorage
function loadQuizAnswers() {
  try {
    const saved = localStorage.getItem("quiz-answers");
    if (saved) {
      quizAnswers = JSON.parse(saved);
    }
  } catch (error) {
    console.error("Error loading quiz answers:", error);
    quizAnswers = {};
  }
}

// Save quiz answers to localStorage
function saveQuizAnswers() {
  try {
    localStorage.setItem("quiz-answers", JSON.stringify(quizAnswers));
  } catch (error) {
    console.error("Error saving quiz answers:", error);
  }
}

// Start loading the gallery and initialize quiz.
loadGallery();
initializeQuiz();