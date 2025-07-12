// Quiz functionality
function renderQuiz(quizData, taskName = "Learning Quiz") {
    const container = document.getElementById('quizContainer');
    
    if (!quizData || !Array.isArray(quizData) || quizData.length === 0) {
        container.innerHTML = '<div class="error">No quiz data available.</div>';
        return;
    }

    let correctAnswers = 0;
    let totalQuestions = quizData.length;

    // Create quiz HTML
    let quizHTML = `
        <div class="quiz-header">
            <h1 class="quiz-title">${taskName}</h1>
            <p class="quiz-instructions">Select the best answer for each question. You'll get instant feedback!</p>
        </div>
    `;

    // Generate questions
    quizData.forEach((item, questionIndex) => {
        const questionNumber = questionIndex + 1;
        
        quizHTML += `
            <div class="question" data-question="${questionIndex}">
                <div class="question-number">Question ${questionNumber}</div>
                <div class="question-text">${item.question}</div>
                <div class="options">
        `;

        // Generate options
        item.options.forEach((option, optionIndex) => {
            const optionId = `q${questionIndex}_opt${optionIndex}`;
            quizHTML += `
                <label class="option" for="${optionId}">
                    <input type="radio" 
                           class="radio-input" 
                           id="${optionId}"
                           name="question_${questionIndex}" 
                           value="${optionIndex}"
                           data-correct="${item.correctIndex === optionIndex}"
                           onchange="handleAnswer(${questionIndex}, ${optionIndex}, ${item.correctIndex})">
                    <span class="radio-custom"></span>
                    <span class="option-text">${option}</span>
                </label>
            `;
        });

        quizHTML += `
                </div>
                <div class="feedback" id="feedback_${questionIndex}"></div>
            </div>
        `;
    });

    // Add score display
    quizHTML += `
        <div class="score-display" id="scoreDisplay">
            Score: <span id="scoreText">0/${totalQuestions}</span>
        </div>
    `;

    container.innerHTML = quizHTML;
}

// Global functions for quiz interaction
window.handleAnswer = function(questionIndex, selectedIndex, correctIndex) {
    console.log('handleAnswer called:', { questionIndex, selectedIndex, correctIndex });
    const feedback = document.getElementById(`feedback_${questionIndex}`);
    console.log('Feedback element:', feedback);
    const isCorrect = selectedIndex === correctIndex;
    console.log('Is correct:', isCorrect);
    
    // Get all options for this question
    const questionElement = document.querySelector(`[data-question="${questionIndex}"]`);
    const options = questionElement.querySelectorAll('.option');
    const radioInputs = questionElement.querySelectorAll('.radio-input');
    
    // Disable all radio inputs for this question after selection
    radioInputs.forEach(input => {
        input.disabled = true;
    });
    
    // Remove any existing visual feedback classes
    options.forEach(option => {
        option.classList.remove('selected-correct', 'selected-incorrect', 'correct-answer');
    });
    
    // Add visual feedback to the selected option
    const selectedOption = options[selectedIndex];
    if (isCorrect) {
        selectedOption.classList.add('selected-correct');
        feedback.textContent = '✅ Correct!';
        feedback.className = 'feedback correct';
    } else {
        selectedOption.classList.add('selected-incorrect');
        // Also highlight the correct answer
        const correctOption = options[correctIndex];
        correctOption.classList.add('correct-answer');
        feedback.textContent = `❌ Incorrect!`;
        feedback.className = 'feedback incorrect';
    }
    
    feedback.style.display = 'block';
    console.log('Feedback display set to block, text:', feedback.textContent);

    // Update score
    updateScore();
};

window.updateScore = function() {
    const correctInputs = document.querySelectorAll('input[data-correct="true"]:checked');
    const score = correctInputs.length;
    const totalQuestions = document.querySelectorAll('.question').length;
    document.getElementById('scoreText').textContent = `${score}/${totalQuestions}`;
};

// Hardcoded quiz data from "Foundations of Agentic AI in Business"
const hardcodedQuizData = [
    {
        "question": "Agentic AI is best described as AI that _____.",
        "options": [
            "A. Passively returns search results only",
            "B. Acts autonomously to pursue goals and make decisions",
            "C. Requires constant human coding for each action",
            "D. Only analyzes historical data without acting"
        ],
        "correctIndex": 1
    },
    {
        "question": "Which capability is a hallmark of Agentic AI?",
        "options": [
            "A. Batch image compression",
            "B. Self-driven reasoning and planning",
            "C. Static rule-based routing only",
            "D. Manual spreadsheet entry"
        ],
        "correctIndex": 1
    },
    {
        "question": "A key business benefit of Agentic AI is _____.",
        "options": [
            "A. Eliminating all employees immediately",
            "B. Proactive, continuous process optimization",
            "C. Converting PDFs to Word docs",
            "D. Higher electricity consumption"
        ],
        "correctIndex": 1
    },
    {
        "question": "In the sense-plan-act loop, the \"plan\" step mainly involves _____.",
        "options": [
            "A. Random guessing",
            "B. Choosing a sequence of actions toward a goal",
            "C. Compressing images",
            "D. Sending raw logs to storage"
        ],
        "correctIndex": 1
    },
    {
        "question": "Which industry is often cited as an early adopter of Agentic AI for customer engagement?",
        "options": [
            "A. Heavy metal mining",
            "B. E-commerce and retail",
            "C. Antique book restoration",
            "D. Lumber milling"
        ],
        "correctIndex": 1
    }
];

// Load quiz data when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Quiz script loaded, rendering quiz...');
    renderQuiz(hardcodedQuizData, 'Foundations of Agentic AI in Business');
}); 