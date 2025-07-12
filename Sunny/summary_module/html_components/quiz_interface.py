"""
Quiz Interface Generator for Learning Dashboard

Generates interactive quiz components with multiple choice questions,
progress tracking, and results display.
"""

import os
import sys
from typing import List, Dict

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.schema import Quiz, QuizQuestion


class QuizInterfaceGenerator:
    """Generates interactive quiz HTML components."""
    
    def generate(self, quiz: Quiz) -> str:
        """Generate complete quiz interface HTML."""
        
        if not quiz or not quiz.questions:
            return self._generate_no_quiz_message()
        
        questions_html = self._generate_questions(quiz.questions)
        progress_html = self._generate_progress_bar(len(quiz.questions))
        results_html = self._generate_results_section(quiz)
        
        return f"""
        <div class="quiz-container">
            <div class="quiz-header">
                <h3>📝 {quiz.title}</h3>
                <p class="quiz-description">{quiz.description}</p>
                <div class="quiz-meta">
                    <span class="quiz-time">⏱️ Estimated time: {quiz.estimated_time}</span>
                    <span class="quiz-passing">🎯 Passing score: {quiz.passing_score}%</span>
                    <span class="quiz-count">📊 {len(quiz.questions)} questions</span>
                </div>
            </div>
            
            {progress_html}
            
            <div class="quiz-content">
                {questions_html}
            </div>
            
            <div class="quiz-controls">
                <button id="prev-question" onclick="previousQuestion()" disabled>⬅️ Previous</button>
                <button id="next-question" onclick="nextQuestion()">Next ➡️</button>
                <button id="submit-quiz" onclick="submitQuiz()" style="display: none;">🎯 Submit Quiz</button>
                <button id="restart-quiz" onclick="restartQuiz()" style="display: none;">🔄 Restart</button>
            </div>
            
            {results_html}
        </div>
        
        {self._generate_quiz_javascript(quiz)}
        """
    
    def _generate_questions(self, questions: List[QuizQuestion]) -> str:
        """Generate HTML for all quiz questions."""
        
        questions_html = []
        
        for i, question in enumerate(questions):
            question_html = f"""
            <div class="quiz-question" id="question-{i}" style="{'display: block;' if i == 0 else 'display: none;'}">
                <div class="question-header">
                    <h4>Question {i + 1}</h4>
                    <span class="question-concept">Topic: {question.concept}</span>
                </div>
                
                <div class="question-text">
                    <p>{question.question}</p>
                </div>
                
                <div class="question-options">
                    {self._generate_options(question.options, i)}
                </div>
                
                <div class="question-source">
                    <small>Source: <a href="{question.source_url}" target="_blank">{question.source_url}</a></small>
                </div>
                
                <div class="question-explanation" id="explanation-{i}" style="display: none;">
                    <div class="explanation-content">
                        <h5>Explanation:</h5>
                        <p>{question.explanation}</p>
                    </div>
                </div>
            </div>
            """
            questions_html.append(question_html)
        
        return "".join(questions_html)
    
    def _generate_options(self, options: List[str], question_index: int) -> str:
        """Generate HTML for question options."""
        
        options_html = []
        
        for i, option in enumerate(options):
            option_html = f"""
            <label class="option-label">
                <input type="radio" name="question-{question_index}" value="{i}" 
                       onchange="selectAnswer({question_index}, {i})">
                <span class="option-text">{option}</span>
            </label>
            """
            options_html.append(option_html)
        
        return "".join(options_html)
    
    def _generate_progress_bar(self, total_questions: int) -> str:
        """Generate progress bar HTML."""
        
        return f"""
        <div class="quiz-progress">
            <div class="progress-info">
                <span id="current-question-num">1</span> of {total_questions} questions
            </div>
            <div class="progress-bar">
                <div class="progress-fill" id="progress-fill" style="width: {100/total_questions}%;"></div>
            </div>
        </div>
        """
    
    def _generate_results_section(self, quiz: Quiz) -> str:
        """Generate results display section."""
        
        return f"""
        <div class="quiz-results" id="quiz-results" style="display: none;">
            <div class="results-header">
                <h3>🎯 Quiz Results</h3>
            </div>
            
            <div class="results-score">
                <div class="score-circle">
                    <span id="score-percentage">0%</span>
                </div>
                <div class="score-details">
                    <p id="score-text">Calculating...</p>
                    <p id="passing-status"></p>
                </div>
            </div>
            
            <div class="results-breakdown">
                <h4>📊 Question Breakdown</h4>
                <div id="question-results">
                    <!-- Question results will be populated here -->
                </div>
            </div>
            
            <div class="results-recommendations">
                <h4>💡 Learning Recommendations</h4>
                <div id="learning-recommendations">
                    <!-- Recommendations will be populated here -->
                </div>
            </div>
        </div>
        """
    
    def _generate_no_quiz_message(self) -> str:
        """Generate message when no quiz is available."""
        
        return f"""
        <div class="no-quiz-container">
            <div class="no-quiz-message">
                <h3>📝 Quiz Not Available</h3>
                <p>No quiz questions could be generated for the current content.</p>
                <p>This might be because:</p>
                <ul>
                    <li>Not enough content has been analyzed</li>
                    <li>The LLM service is not available</li>
                    <li>The content doesn't contain suitable concepts for quiz generation</li>
                </ul>
                <button onclick="location.reload()" class="refresh-button">🔄 Try Again</button>
            </div>
        </div>
        """
    
    def _generate_quiz_javascript(self, quiz: Quiz) -> str:
        """Generate JavaScript for quiz functionality."""
        
        # Convert quiz data to JavaScript format
        questions_js = []
        for q in quiz.questions:
            questions_js.append({
                'question': q.question,
                'options': q.options,
                'correct_answer': q.correct_answer,
                'explanation': q.explanation,
                'concept': q.concept,
                'source_url': q.source_url
            })
        
        return f"""
        <script>
        // Quiz data and state
        const quizData = {questions_js};
        const totalQuestions = {len(quiz.questions)};
        const passingScore = {quiz.passing_score};
        let currentQuestion = 0;
        let userAnswers = new Array(totalQuestions).fill(-1);
        let quizCompleted = false;
        
        // Navigation functions
        function nextQuestion() {{
            if (currentQuestion < totalQuestions - 1) {{
                showQuestion(currentQuestion + 1);
            }} else {{
                showSubmitButton();
            }}
        }}
        
        function previousQuestion() {{
            if (currentQuestion > 0) {{
                showQuestion(currentQuestion - 1);
            }}
        }}
        
        function showQuestion(questionIndex) {{
            // Hide current question
            document.getElementById(`question-${{currentQuestion}}`).style.display = 'none';
            
            // Update current question
            currentQuestion = questionIndex;
            
            // Show new question
            document.getElementById(`question-${{currentQuestion}}`).style.display = 'block';
            
            // Update progress
            updateProgress();
            
            // Update navigation buttons
            updateNavigationButtons();
        }}
        
        function updateProgress() {{
            const progressPercent = ((currentQuestion + 1) / totalQuestions) * 100;
            document.getElementById('progress-fill').style.width = progressPercent + '%';
            document.getElementById('current-question-num').textContent = currentQuestion + 1;
        }}
        
        function updateNavigationButtons() {{
            const prevBtn = document.getElementById('prev-question');
            const nextBtn = document.getElementById('next-question');
            const submitBtn = document.getElementById('submit-quiz');
            
            // Previous button
            prevBtn.disabled = currentQuestion === 0;
            
            // Next/Submit button
            if (currentQuestion === totalQuestions - 1) {{
                nextBtn.style.display = 'none';
                submitBtn.style.display = 'inline-block';
            }} else {{
                nextBtn.style.display = 'inline-block';
                submitBtn.style.display = 'none';
            }}
        }}
        
        function showSubmitButton() {{
            document.getElementById('next-question').style.display = 'none';
            document.getElementById('submit-quiz').style.display = 'inline-block';
        }}
        
        function selectAnswer(questionIndex, answerIndex) {{
            userAnswers[questionIndex] = answerIndex;
            
            // Enable next button if answer is selected
            if (questionIndex === currentQuestion) {{
                document.getElementById('next-question').disabled = false;
            }}
        }}
        
        function submitQuiz() {{
            if (userAnswers.includes(-1)) {{
                alert('Please answer all questions before submitting.');
                return;
            }}
            
            quizCompleted = true;
            calculateAndShowResults();
        }}
        
        function calculateAndShowResults() {{
            let correctAnswers = 0;
            
            // Calculate score
            for (let i = 0; i < totalQuestions; i++) {{
                if (userAnswers[i] === quizData[i].correct_answer) {{
                    correctAnswers++;
                }}
            }}
            
            const scorePercentage = Math.round((correctAnswers / totalQuestions) * 100);
            const passed = scorePercentage >= passingScore;
            
            // Show results section
            document.querySelector('.quiz-content').style.display = 'none';
            document.querySelector('.quiz-controls').style.display = 'none';
            document.getElementById('quiz-results').style.display = 'block';
            
            // Update score display
            document.getElementById('score-percentage').textContent = scorePercentage + '%';
            document.getElementById('score-text').textContent = 
                `You got ${{correctAnswers}} out of ${{totalQuestions}} questions correct.`;
            document.getElementById('passing-status').innerHTML = passed ? 
                '<span class="pass-status">✅ Congratulations! You passed!</span>' :
                '<span class="fail-status">❌ You need ' + passingScore + '% to pass. Keep learning!</span>';
            
            // Show question breakdown
            showQuestionBreakdown();
            
            // Show learning recommendations
            showLearningRecommendations(correctAnswers, totalQuestions);
            
            // Show restart button
            document.getElementById('restart-quiz').style.display = 'inline-block';
        }}
        
        function showQuestionBreakdown() {{
            const resultsContainer = document.getElementById('question-results');
            let resultsHTML = '';
            
            for (let i = 0; i < totalQuestions; i++) {{
                const question = quizData[i];
                const userAnswer = userAnswers[i];
                const correct = userAnswer === question.correct_answer;
                
                resultsHTML += `
                <div class="question-result ${{correct ? 'correct' : 'incorrect'}}">
                    <div class="question-result-header">
                        <span class="question-num">Q${{i + 1}}</span>
                        <span class="question-status">${{correct ? '✅' : '❌'}}</span>
                        <span class="question-concept">${{question.concept}}</span>
                    </div>
                    <div class="question-result-details">
                        <p><strong>Question:</strong> ${{question.question}}</p>
                        <p><strong>Your answer:</strong> ${{question.options[userAnswer]}}</p>
                        ${{!correct ? `<p><strong>Correct answer:</strong> ${{question.options[question.correct_answer]}}</p>` : ''}}
                        <p><strong>Explanation:</strong> ${{question.explanation}}</p>
                    </div>
                </div>
                `;
            }}
            
            resultsContainer.innerHTML = resultsHTML;
        }}
        
        function showLearningRecommendations(correct, total) {{
            const recommendationsContainer = document.getElementById('learning-recommendations');
            const scorePercentage = (correct / total) * 100;
            
            let recommendations = '';
            
            if (scorePercentage >= 90) {{
                recommendations = `
                <div class="recommendation excellent">
                    <h5>🎉 Excellent Performance!</h5>
                    <p>You have a strong understanding of the material. Consider exploring advanced topics or helping others learn!</p>
                </div>
                `;
            }} else if (scorePercentage >= 70) {{
                recommendations = `
                <div class="recommendation good">
                    <h5>👍 Good Job!</h5>
                    <p>You have a solid foundation. Review the concepts you missed and practice with more examples.</p>
                </div>
                `;
            }} else {{
                recommendations = `
                <div class="recommendation needs-improvement">
                    <h5>📚 Keep Learning!</h5>
                    <p>Focus on reviewing the fundamental concepts. Go back to the learning resources and practice more.</p>
                </div>
                `;
            }}
            
            // Add specific concept recommendations based on incorrect answers
            const missedConcepts = [];
            for (let i = 0; i < totalQuestions; i++) {{
                if (userAnswers[i] !== quizData[i].correct_answer) {{
                    missedConcepts.push(quizData[i].concept);
                }}
            }}
            
            if (missedConcepts.length > 0) {{
                const uniqueConcepts = [...new Set(missedConcepts)];
                recommendations += `
                <div class="concept-recommendations">
                    <h5>📖 Focus on these concepts:</h5>
                    <ul>
                        ${{uniqueConcepts.map(concept => `<li>${{concept}}</li>`).join('')}}
                    </ul>
                </div>
                `;
            }}
            
            recommendationsContainer.innerHTML = recommendations;
        }}
        
        function restartQuiz() {{
            // Reset state
            currentQuestion = 0;
            userAnswers = new Array(totalQuestions).fill(-1);
            quizCompleted = false;
            
            // Reset UI
            document.querySelector('.quiz-content').style.display = 'block';
            document.querySelector('.quiz-controls').style.display = 'block';
            document.getElementById('quiz-results').style.display = 'none';
            
            // Reset form
            const radioButtons = document.querySelectorAll('input[type="radio"]');
            radioButtons.forEach(radio => radio.checked = false);
            
            // Show first question
            showQuestion(0);
            
            // Reset buttons
            document.getElementById('restart-quiz').style.display = 'none';
            document.getElementById('next-question').style.display = 'inline-block';
            document.getElementById('submit-quiz').style.display = 'none';
        }}
        </script>
        """
