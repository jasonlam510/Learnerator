document.addEventListener('DOMContentLoaded', function() {
    const topicInput = document.getElementById('topicInput');
    const generateBtn = document.getElementById('generateBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const timelineContainer = document.getElementById('timelineContainer');
    const inputSection = document.getElementById('inputSection');
    const learningHeader = document.getElementById('learningHeader');
    const learningTopic = document.getElementById('learningTopic');
    const timeline = document.getElementById('timeline');

    // Chatbot elements
    const mainContainer = document.getElementById('mainContainer');
    const chatbotToggle = document.getElementById('chatbotToggle');
    const chatbotPanel = document.getElementById('chatbotPanel');
    const chatbotClose = document.getElementById('chatbotClose');
    const chatbotMessages = document.getElementById('chatbotMessages');
    const chatbotInput = document.getElementById('chatbotInput');
    const chatbotSend = document.getElementById('chatbotSend');

    // Current learning plan data
    let currentLearningPlan = [];
    let currentTopic = '';

    // Cache management functions
    async function saveToCache(topic, learningPlan) {
        try {
            const cacheData = {
                topic: topic,
                learningPlan: learningPlan,
                timestamp: Date.now()
            };
            
            await chrome.storage.local.set({
                'learnflow_cache': cacheData
            });
            
            console.log('✅ Learning plan cached successfully');
        } catch (error) {
            console.error('❌ Error caching learning plan:', error);
        }
    }

    async function loadFromCache() {
        try {
            const result = await chrome.storage.local.get(['learnflow_cache']);
            
            if (result.learnflow_cache) {
                const cacheData = result.learnflow_cache;
                const cacheAge = Date.now() - cacheData.timestamp;
                const maxAge = 24 * 60 * 60 * 1000; // 24 hours
                
                // Check if cache is still valid (less than 24 hours old)
                if (cacheAge < maxAge) {
                    console.log('✅ Loading learning plan from cache');
                    return {
                        topic: cacheData.topic,
                        learningPlan: cacheData.learningPlan
                    };
                } else {
                    console.log('🔄 Cache expired, clearing old data');
                    await clearCache();
                }
            }
            
            return null;
        } catch (error) {
            console.error('❌ Error loading from cache:', error);
            return null;
        }
    }

    async function clearCache() {
        try {
            await chrome.storage.local.remove(['learnflow_cache']);
            console.log('✅ Cache cleared successfully');
        } catch (error) {
            console.error('❌ Error clearing cache:', error);
        }
    }

    // Function to restore UI state from cached data
    function restoreUIState(topic, learningPlan) {
        currentTopic = topic;
        currentLearningPlan = learningPlan;
        
        // Show learning header
        showLearningHeader(topic);
        
        // Render the timeline
        renderTimeline(learningPlan);
        
        // Show timeline
        timelineContainer.style.display = 'block';
        
        // Add "New Plan" button to allow creating a new learning plan
        addNewPlanButton();
        
        // Add welcome message to chatbot
        const welcomeMessage = `
            <p>👋 Welcome back! You were learning <strong>${topic}</strong>.</p>
            <p>Your learning plan has been restored. You can:</p>
            <ul>
                <li>Continue where you left off</li>
                <li>Ask me about specific stages</li>
                <li>Click on any stage to open learning resources</li>
            </ul>
            <p>How can I help you today?</p>
        `;
        addMessage(welcomeMessage);
    }

    // Function to add "New Plan" button when showing cached data
    function addNewPlanButton() {
        // Check if button already exists
        if (document.getElementById('newPlanBtn')) {
            return;
        }
        
        const newPlanBtn = document.createElement('button');
        newPlanBtn.id = 'newPlanBtn';
        newPlanBtn.textContent = '+ New Learning Plan';
        newPlanBtn.className = 'new-plan-btn';
        newPlanBtn.style.cssText = `
            background: rgba(102, 126, 234, 0.1);
            border: 1px solid rgba(102, 126, 234, 0.3);
            color: #667eea;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            margin-top: 10px;
            transition: all 0.2s ease;
        `;
        
        newPlanBtn.addEventListener('click', async function() {
            // Clear cache and reset UI
            await clearCache();
            
            // Reset variables
            currentLearningPlan = [];
            currentTopic = '';
            
            // Show input section and hide learning header
            inputSection.classList.remove('hidden');
            document.querySelector('.logo-header').classList.remove('hidden');
            learningHeader.style.display = 'none';
            timelineContainer.style.display = 'none';
            
            // Remove the new plan button
            newPlanBtn.remove();
            
            // Focus on input
            topicInput.focus();
            
            // Clear input
            topicInput.value = '';
            
            // Clear chatbot messages
            chatbotMessages.innerHTML = '';
        });
        
        // Add hover effect
        newPlanBtn.addEventListener('mouseenter', function() {
            this.style.background = 'rgba(102, 126, 234, 0.2)';
            this.style.borderColor = 'rgba(102, 126, 234, 0.5)';
        });
        
        newPlanBtn.addEventListener('mouseleave', function() {
            this.style.background = 'rgba(102, 126, 234, 0.1)';
            this.style.borderColor = 'rgba(102, 126, 234, 0.3)';
        });
        
        // Insert button after learning header
        learningHeader.appendChild(newPlanBtn);
    }

    // Initialize popup - check for cached data
    async function initializePopup() {
        console.log('🔍 Initializing popup...');
        
        const cachedData = await loadFromCache();
        
        if (cachedData) {
            console.log('🔄 Restoring from cache:', cachedData.topic);
            restoreUIState(cachedData.topic, cachedData.learningPlan);
        } else {
            console.log('📝 No cached data found, showing input form');
            // Focus on input when popup opens (only if no cached data)
            topicInput.focus();
        }
    }

    // Call initialize function
    initializePopup();

    // Mock URLs for different topics and stages
    const mockUrls = {
        'react': {
            'fundamentals': [
                'https://react.dev/learn',
                'https://developer.mozilla.org/en-US/docs/Learn/Tools_and_testing/Client-side_JavaScript_frameworks/React_getting_started',
                'https://www.freecodecamp.org/learn/front-end-development-libraries/react/',
                'https://reactjs.org/tutorial/tutorial.html'
            ],
            'components': [
                'https://react.dev/learn/your-first-component',
                'https://react.dev/learn/passing-props-to-a-component',
                'https://react.dev/learn/conditional-rendering',
                'https://beta.reactjs.org/learn/rendering-lists'
            ],
            'state': [
                'https://react.dev/learn/state-a-components-memory',
                'https://react.dev/learn/render-and-commit',
                'https://react.dev/reference/react/useState',
                'https://react.dev/reference/react/useEffect'
            ],
            'hooks': [
                'https://react.dev/reference/react/hooks',
                'https://react.dev/learn/reusing-logic-with-custom-hooks',
                'https://usehooks.com/',
                'https://github.com/streamich/react-use'
            ],
            'routing': [
                'https://reactrouter.com/en/main/start/tutorial',
                'https://github.com/remix-run/react-router',
                'https://reactrouter.com/en/main/route/route',
                'https://reactrouter.com/en/main/hooks/use-navigate'
            ],
            'api': [
                'https://react.dev/learn/synchronizing-with-effects',
                'https://tanstack.com/query/latest',
                'https://swr.vercel.app/',
                'https://axios-http.com/docs/intro'
            ],
            'testing': [
                'https://testing-library.com/docs/react-testing-library/intro/',
                'https://jestjs.io/docs/tutorial-react',
                'https://github.com/testing-library/react-testing-library',
                'https://kentcdodds.com/blog/common-mistakes-with-react-testing-library'
            ]
        },
        'javascript': {
            'fundamentals': [
                'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide',
                'https://javascript.info/',
                'https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/',
                'https://eloquentjavascript.net/'
            ],
            'es6': [
                'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/let',
                'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/Arrow_functions',
                'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring_assignment',
                'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import'
            ],
            'async': [
                'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise',
                'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function',
                'https://javascript.info/async-await',
                'https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API'
            ]
        },
        'python': {
            'fundamentals': [
                'https://docs.python.org/3/tutorial/',
                'https://www.python.org/about/gettingstarted/',
                'https://www.freecodecamp.org/learn/scientific-computing-with-python/',
                'https://realpython.com/python-basics/'
            ],
            'data-structures': [
                'https://docs.python.org/3/tutorial/datastructures.html',
                'https://realpython.com/python-data-structures/',
                'https://www.geeksforgeeks.org/python-data-structures/',
                'https://docs.python.org/3/library/collections.html'
            ],
            'web': [
                'https://flask.palletsprojects.com/en/2.3.x/quickstart/',
                'https://docs.djangoproject.com/en/4.2/intro/tutorial01/',
                'https://fastapi.tiangolo.com/tutorial/',
                'https://realpython.com/python-web-applications/'
            ]
        },
        'default': [
            'https://developer.mozilla.org/en-US/',
            'https://stackoverflow.com/',
            'https://github.com/',
            'https://www.freecodecamp.org/'
        ]
    };

    // Function to get relevant URLs for a stage
    function getStageUrls(topic, stageHeader, keywords) {
        const topicLower = topic.toLowerCase();
        const headerLower = stageHeader.toLowerCase();
        
        // Check if we have specific URLs for this topic
        if (mockUrls[topicLower]) {
            const topicUrls = mockUrls[topicLower];
            
            // Try to match based on keywords first
            for (const keyword of keywords) {
                const keywordLower = keyword.toLowerCase();
                if (topicUrls[keywordLower]) {
                    return topicUrls[keywordLower];
                }
            }
            
            // Try to match based on header content
            for (const [key, urls] of Object.entries(topicUrls)) {
                if (headerLower.includes(key) || key.includes(headerLower.split(' ')[0])) {
                    return urls;
                }
            }
            
            // Return first available URLs for this topic
            const firstKey = Object.keys(topicUrls)[0];
            if (firstKey) {
                return topicUrls[firstKey];
            }
        }
        
        // Fallback to default URLs
        return mockUrls.default;
    }

    // Function to open tabs for a stage
    async function openStageResources(stage, stageIndex) {
        try {
            console.log('🔍 Opening resources for stage:', stage.header);
            
            // Get URLs for this stage
            const urls = getStageUrls(currentTopic, stage.header, stage.keywords || []);
            
            // Create group name
            const groupName = `${currentTopic} - ${stage.header}`;
            
            console.log('🔍 Creating tab group:', groupName);
            console.log('🔍 URLs:', urls);
            
            // Send message to background script to create tab group
            chrome.runtime.sendMessage({
                action: "createTabGroup",
                groupName: groupName,
                urls: urls
            }, function(response) {
                if (response && response.success) {
                    console.log('✅ Tab group created successfully:', response);
                    
                    // Show success message in chatbot if it's open
                    if (mainContainer.classList.contains('expanded')) {
                        const successMessage = `
                            <p>🚀 <strong>Opened learning resources for "${stage.header}"</strong></p>
                            <p>Created tab group with ${urls.length} helpful resources:</p>
                            <ul>
                                ${urls.map(url => {
                                    const domain = new URL(url).hostname;
                                    return `<li><strong>${domain}</strong></li>`;
                                }).join('')}
                            </ul>
                            <p>Check your new tab group to start learning! 📚</p>
                        `;
                        addMessage(successMessage);
                    }
                } else {
                    console.error('❌ Failed to create tab group:', response?.error);
                    
                    // Show error message in chatbot if it's open
                    if (mainContainer.classList.contains('expanded')) {
                        const errorMessage = `
                            <p>❌ <strong>Failed to open learning resources</strong></p>
                            <p>Error: ${response?.error || 'Unknown error'}</p>
                            <p>You can manually visit these helpful resources:</p>
                            <ul>
                                ${urls.map(url => `<li><a href="${url}" target="_blank">${url}</a></li>`).join('')}
                            </ul>
                        `;
                        addMessage(errorMessage);
                    }
                }
            });
            
        } catch (error) {
            console.error('❌ Error opening stage resources:', error);
            
            // Show error in chatbot if it's open
            if (mainContainer.classList.contains('expanded')) {
                const errorMessage = `
                    <p>❌ <strong>Error opening learning resources</strong></p>
                    <p>Error: ${error.message}</p>
                    <p>Please try again or manually search for resources related to: <strong>${stage.header}</strong></p>
                `;
                addMessage(errorMessage);
            }
        }
    }

    // Dummy data for testing when API is not available
    const dummyLearningPlan = [
        {
            header: "1. JavaScript Fundamentals",
            details: "Master ES6+ features, async/await, promises, and modern JavaScript concepts. Focus on arrow functions, destructuring, and modules. Practice with real-world examples and build small projects to reinforce your understanding.",
            keywords: ["javascript basics", "ES6 features", "async programming"],
            status: "finished"
        },
        {
            header: "2. HTML & CSS Basics",
            details: "Learn semantic HTML, CSS Grid, Flexbox, and responsive design principles. Understand the box model and CSS selectors. Create responsive layouts and understand modern CSS techniques.",
            keywords: ["HTML5", "CSS Grid", "responsive design"],
            status: "finished"
        },
        {
            header: "3. React Core Concepts",
            details: "Understand JSX, components, props, state, and the component lifecycle. Learn about functional components and hooks. Build simple components and understand React's declarative nature.",
            keywords: ["React basics", "JSX", "components", "hooks"],
            status: "ongoing"
        },
        {
            header: "4. State Management",
            details: "Master useState, useEffect, useContext, and custom hooks. Learn about state lifting and prop drilling patterns. Implement complex state management solutions and understand when to use different approaches.",
            keywords: ["state management", "useState", "useEffect", "context"],
            status: "pending"
        },
        {
            header: "5. Advanced React Patterns",
            details: "Explore higher-order components, render props, compound components, and performance optimization techniques. Learn about React.memo, useMemo, and useCallback for performance optimization.",
            keywords: ["HOCs", "render props", "performance optimization"],
            status: "pending"
        },
        {
            header: "6. Routing & Navigation",
            details: "Implement client-side routing with React Router, handle dynamic routes, and manage navigation state. Learn about route guards, nested routes, and programmatic navigation.",
            keywords: ["React Router", "routing", "navigation"],
            status: "pending"
        },
        {
            header: "7. API Integration",
            details: "Learn to fetch data from APIs, handle loading states, error boundaries, and implement data fetching patterns. Understand RESTful APIs, GraphQL, and modern data fetching libraries like React Query.",
            keywords: ["API integration", "fetch", "error handling"],
            status: "pending"
        },
        {
            header: "8. Testing React Applications",
            details: "Write unit tests with Jest and React Testing Library, test user interactions, and implement integration tests. Learn about testing best practices, mocking, and test-driven development.",
            keywords: ["testing", "Jest", "React Testing Library"],
            status: "pending"
        }
    ];

    // Chatbot functionality
    function toggleChatbot() {
        const isExpanded = mainContainer.classList.contains('expanded');
        
        if (isExpanded) {
            mainContainer.classList.remove('expanded');
        } else {
            mainContainer.classList.add('expanded');
            // Focus on chatbot input when opened
            setTimeout(() => {
                chatbotInput.focus();
            }, 400);
        }
    }

    function closeChatbot() {
        mainContainer.classList.remove('expanded');
    }

    function addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        if (typeof content === 'string') {
            messageContent.innerHTML = content;
        } else {
            messageContent.appendChild(content);
        }
        
        messageDiv.appendChild(messageContent);
        chatbotMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    function generateBotResponse(userMessage) {
        const message = userMessage.toLowerCase();
        
        // Context-aware responses based on current learning plan
        if (currentLearningPlan.length > 0) {
            // Check if user is asking about a specific stage
            const stageNumber = message.match(/(\d+)/);
            if (stageNumber) {
                const stageIndex = parseInt(stageNumber[1]) - 1;
                if (stageIndex >= 0 && stageIndex < currentLearningPlan.length) {
                    const stage = currentLearningPlan[stageIndex];
                    return `
                        <p><strong>${stage.header}</strong></p>
                        <p>Status: <span style="color: ${getStatusColor(stage.status)}">${stage.status}</span></p>
                        <p>${stage.details}</p>
                        <p><strong>Key topics:</strong> ${stage.keywords.join(', ')}</p>
                        <p><em>💡 Tip: Click on the stage in your timeline to open learning resources!</em></p>
                    `;
                }
            }
            
            // Topic-specific responses
            if (message.includes('current') || message.includes('ongoing')) {
                const ongoingStages = currentLearningPlan.filter(stage => stage.status === 'ongoing');
                if (ongoingStages.length > 0) {
                    return `
                        <p>You're currently working on:</p>
                        <ul>
                            ${ongoingStages.map(stage => `<li><strong>${stage.header}</strong></li>`).join('')}
                        </ul>
                        <p>Would you like me to explain any of these concepts in more detail?</p>
                        <p><em>💡 Tip: Click on any stage to open helpful learning resources!</em></p>
                    `;
                }
            }
            
            if (message.includes('next') || message.includes('upcoming')) {
                const nextStages = currentLearningPlan.filter(stage => stage.status === 'pending').slice(0, 3);
                if (nextStages.length > 0) {
                    return `
                        <p>Your upcoming learning stages:</p>
                        <ul>
                            ${nextStages.map(stage => `<li><strong>${stage.header}</strong></li>`).join('')}
                        </ul>
                        <p>Ready to dive into any of these topics?</p>
                        <p><em>💡 Tip: Click on any stage to open curated learning resources!</em></p>
                    `;
                }
            }
            
            if (message.includes('progress') || message.includes('status')) {
                const finished = currentLearningPlan.filter(stage => stage.status === 'finished').length;
                const total = currentLearningPlan.length;
                const percentage = Math.round((finished / total) * 100);
                
                return `
                    <p>📊 <strong>Learning Progress for ${currentTopic}:</strong></p>
                    <p>✅ Completed: ${finished}/${total} stages (${percentage}%)</p>
                    <p>🔄 In Progress: ${currentLearningPlan.filter(stage => stage.status === 'ongoing').length}</p>
                    <p>⏳ Upcoming: ${currentLearningPlan.filter(stage => stage.status === 'pending').length}</p>
                    <p>Keep up the great work! 🚀</p>
                `;
            }
        }
        
        // General responses
        if (message.includes('help') || message.includes('what can you do')) {
            return `
                <p>I can help you with:</p>
                <ul>
                    <li>📚 Explaining concepts from your learning plan</li>
                    <li>📈 Tracking your progress</li>
                    <li>🔍 Finding resources for specific topics</li>
                    <li>💡 Suggesting practice exercises</li>
                    <li>❓ Answering questions about your current stage</li>
                    <li>🚀 Opening curated learning resources (click on any stage!)</li>
                </ul>
                <p>Just ask me anything about your learning journey!</p>
            `;
        }
        
        if (message.includes('resource') || message.includes('tutorial') || message.includes('learn more')) {
            return `
                <p>🔗 <strong>Great learning resources:</strong></p>
                <ul>
                    <li><strong>MDN Web Docs</strong> - Comprehensive web development documentation</li>
                    <li><strong>freeCodeCamp</strong> - Interactive coding challenges</li>
                    <li><strong>YouTube</strong> - Video tutorials and explanations</li>
                    <li><strong>Stack Overflow</strong> - Community Q&A</li>
                    <li><strong>GitHub</strong> - Real-world code examples</li>
                </ul>
                <p>Would you like specific resources for any topic in your learning plan?</p>
                // <p><em>💡 Pro tip: Click on any stage in your timeline to automatically open curated resources!</em></p>
            `;
        }
        
        if (message.includes('practice') || message.includes('exercise') || message.includes('project')) {
            return `
                <p>🛠️ <strong>Practice Ideas:</strong></p>
                <ul>
                    <li>Build small projects for each concept you learn</li>
                    <li>Solve coding challenges on platforms like LeetCode or HackerRank</li>
                    <li>Contribute to open-source projects</li>
                    <li>Create a portfolio website</li>
                    <li>Join coding communities and participate in discussions</li>
                </ul>
                <p>Which stage would you like practice suggestions for?</p>
                <p><em>💡 Click on any stage to open resources with practice exercises!</em></p>
            `;
        }
        
        // Default response
        return `
            <p>I'd be happy to help! You can ask me about:</p>
            <ul>
                <li>Your current learning progress</li>
                <li>Specific stages in your plan</li>
                <li>Learning resources and tutorials</li>
                <li>Practice exercises and projects</li>
            </ul>
            <p>What would you like to know more about?</p>
            <p><em>💡 Remember: Click on any stage in your timeline to open curated learning resources!</em></p>
        `;
    }

    function getStatusColor(status) {
        switch (status) {
            case 'finished': return '#10b981';
            case 'ongoing': return '#f59e0b';
            case 'pending': return '#6b7280';
            default: return '#6b7280';
        }
    }

    function sendMessage() {
        const message = chatbotInput.value.trim();
        if (!message) return;
        
        // Add user message
        addMessage(message, true);
        
        // Clear input
        chatbotInput.value = '';
        
        // Show typing indicator
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing';
        typingDiv.innerHTML = '<div class="message-content"><p>Thinking...</p></div>';
        chatbotMessages.appendChild(typingDiv);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
        
        // Generate and add bot response after a delay
        setTimeout(() => {
            typingDiv.remove();
            const response = generateBotResponse(message);
            addMessage(response);
        }, 1000);
    }

    // Event listeners for chatbot
    chatbotToggle.addEventListener('click', toggleChatbot);
    chatbotClose.addEventListener('click', closeChatbot);
    chatbotSend.addEventListener('click', sendMessage);
    
    chatbotInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Function to check if backend is available using background script
    async function checkBackendHealth() {
        return new Promise((resolve) => {
            chrome.runtime.sendMessage({
                action: "checkBackendHealth"
            }, function(response) {
                if (response && response.success) {
                    console.log('Backend available:', response.available);
                    resolve(response.available);
                } else {
                    console.log('Backend not available');
                    resolve(false);
                }
            });
        });
    }

    // Function to check if Ollama API is available using background script
    async function checkOllamaAPI() {
        return new Promise((resolve) => {
            chrome.runtime.sendMessage({
                action: "checkOllamaHealth"
            }, function(response) {
                if (response && response.success) {
                    console.log('Ollama API available:', response.available);
                    resolve(response.available);
                } else {
                    console.log('Ollama API not available:', response?.error);
                    resolve(false);
                }
            });
        });
    }

    // Function to get learning plan from backend using background script
    async function getLearningPlanFromBackend(topic) {
        return new Promise((resolve) => {
            chrome.runtime.sendMessage({
                action: "xhttp",
                method: "GET",
                url: `http://localhost:3000/api/learning-plans/${encodeURIComponent(topic)}`
            }, function(response) {
                if (response && response.success && response.status === 200) {
                    const data = response.data;
                    const learningPlan = data.stages.map(stage => ({
                        header: stage.header,
                        details: stage.details,
                        keywords: stage.keywords || [],
                        status: stage.status
                    }));
                    resolve(learningPlan);
                } else {
                    resolve(null);
                }
            });
        });
    }

    // Function to save learning plan to backend using background script
    async function saveLearningPlanToBackend(topic, learningPlan) {
        return new Promise((resolve) => {
            chrome.runtime.sendMessage({
                action: "xhttp",
                method: "POST",
                url: "http://localhost:3000/api/learning-plans",
                data: JSON.stringify({
                    topic: topic,
                    stages: learningPlan
                }),
                headers: {
                    'Content-Type': 'application/json'
                }
            }, function(response) {
                if (response && response.success) {
                    console.log('Learning plan saved to backend');
                    resolve(true);
                } else {
                    console.error('Failed to save learning plan');
                    resolve(false);
                }
            });
        });
    }

    // Function to call Ollama API using background script
    async function callOllamaAPI(topic) {
        return new Promise((resolve, reject) => {
            chrome.runtime.sendMessage({
                action: "generateLearningPlan",
                topic: topic,
                model: 'llama2'
            }, function(response) {
                console.log('🔍 Popup: Full response received:', response);
                
                if (response && response.success && response.data) {
                    console.log('✅ Popup: Ollama API response received successfully');
                    console.log('🔍 Popup: Topic name:', response.data.topic_name);
                    console.log('🔍 Popup: Stages:', response.data.stages);
                    
                    // Validate stages array
                    if (!Array.isArray(response.data.stages) || response.data.stages.length === 0) {
                        reject(new Error('No stages found in response'));
                        return;
                    }
                    
                    // Convert API response to extension format
                    const learningPlan = response.data.stages.map(stage => ({
                        header: stage.header || 'Untitled Stage',
                        details: stage.details || 'No details available',
                        keywords: stage.keywords || [],
                        status: stage.status || 'pending'
                    }));
                    
                    console.log('🔍 Popup: Converted learning plan:', learningPlan);
                    resolve(learningPlan);
                } else {
                    const errorMessage = response?.error || 'Failed to generate learning plan';
                    console.error('❌ Popup: API error:', errorMessage);
                    reject(new Error(errorMessage));
                }
            });
        });
    }

    // Function to call LLM server (updated to use background script with fallback)
    async function callLLMServer(topic) {
        // First, check if backend is available
        // const backendAvailable = await checkBackendHealth();
        
        // if (backendAvailable) {
        //     // Try to get existing plan from backend
        //     const existingPlan = await getLearningPlanFromBackend(topic);
        //     if (existingPlan) {
        //         console.log('Found existing plan in backend');
        //         return existingPlan;
        //     }
        // }
        
        // Check if Ollama API is available
        const ollamaAvailable = await checkOllamaAPI();
        
        if (ollamaAvailable) {
            try {
                console.log('🎯 Using Ollama API to generate learning plan');
                const learningPlan = await callOllamaAPI(topic);
                
                // // Save to backend if available
                // if (backendAvailable) {
                //     await saveLearningPlanToBackend(topic, learningPlan);
                // }
                
                return learningPlan;
            } catch (error) {
                console.error('Failed to call Ollama API, falling back to dummy data:', error);
                // Fall back to dummy data if Ollama API fails
            }
        } else {
            console.log('Ollama API not available, using dummy data');
        }
        
        // Fallback to dummy data
        console.log('Using dummy data for topic:', topic);
        const learningPlan = dummyLearningPlan;
        
        // // Save to backend if available
        // if (backendAvailable) {
        //     await saveLearningPlanToBackend(topic, learningPlan);
        // }
        
        return learningPlan;
    }

    // Function to format details into bullet points
    function formatDetails(details) {
        // Split by periods and filter out empty strings
        const sentences = details.split('.').map(s => s.trim()).filter(s => s.length > 0);
        
        // Create bullet points from sentences
        return sentences.map(sentence => sentence.charAt(0).toUpperCase() + sentence.slice(1));
    }

    // Function to show learning header
    function showLearningHeader(topic) {
        // Hide input section and logo header
        inputSection.classList.add('hidden');
        document.querySelector('.logo-header').classList.add('hidden');
        
        // Set the topic text
        learningTopic.textContent = topic;
        
        // Show learning header
        learningHeader.style.display = 'block';
    }

    // Function to render timeline with keywords support
    function renderTimeline(learningPlan) {
        timeline.innerHTML = '';

        learningPlan.forEach((stage, index) => {
            const timelineItem = document.createElement('div');
            timelineItem.className = `timeline-item ${stage.status}`;

            const dot = document.createElement('div');
            dot.className = `timeline-dot ${stage.status}`;

            // Create header container
            const header = document.createElement('div');
            header.className = 'timeline-header';
            header.textContent = stage.header;
            
            // Make header clickable
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                // Show stage details including keywords
                console.log('Clicked on stage:', stage.header);
                console.log('Stage data:', stage);
                console.log('Keywords:', stage.keywords || []);
                console.log('Stage index:', index);
                
                // Open learning resources for this stage
                openStageResources(stage, index);
            });

            // Create details container with bullet points
            const details = document.createElement('div');
            details.className = 'timeline-details';

            const bulletPoints = formatDetails(stage.details);
            const ul = document.createElement('ul');
            
            bulletPoints.forEach(point => {
                const li = document.createElement('li');
                li.textContent = point;
                ul.appendChild(li);
            });

            details.appendChild(ul);

            // Add a hint about clicking for resources
            const hintDiv = document.createElement('div');
            hintDiv.className = 'stage-hint';
            hintDiv.innerHTML = '<p style="font-size: 12px; color: rgba(102, 126, 234, 0.8); margin-top: 12px; font-style: italic;">💡 Click the header above to open curated learning resources</p>';
            details.appendChild(hintDiv);

            // Assemble the timeline item
            timelineItem.appendChild(dot);
            timelineItem.appendChild(header);
            timelineItem.appendChild(details);
            timeline.appendChild(timelineItem);
        });
    }

    // Handle generate button click
    generateBtn.addEventListener('click', async function() {
        const topic = topicInput.value.trim();
        
        if (!topic) {
            alert('Please enter a topic to learn!');
            return;
        }

        // Show loading state
        generateBtn.disabled = true;
        loadingSpinner.style.display = 'block';
        timelineContainer.style.display = 'none';

        try {
            // Call LLM server to get learning plan
            const learningPlan = await callLLMServer(topic);
            
            // Store current learning plan and topic for chatbot
            currentLearningPlan = learningPlan;
            currentTopic = topic;
            
            // Save to cache
            await saveToCache(topic, learningPlan);

            // Hide loading and show learning header
            loadingSpinner.style.display = 'none';
            showLearningHeader(topic);
            
            // Render the timeline
            renderTimeline(learningPlan);
            
            // Show timeline
            timelineContainer.style.display = 'block';
            
            // Add welcome message to chatbot
            setTimeout(() => {
                const welcomeMessage = `
                    <p>🎉 Great choice learning <strong>${topic}</strong>!</p>
                    <p>I've analyzed your learning plan and I'm here to help you succeed. You can ask me about:</p>
                    <ul>
                        <li>Your current progress</li>
                        <li>Specific stages or concepts</li>
                        <li>Learning resources and tutorials</li>
                        <li>Practice exercises</li>
                    </ul>
                    <p>What would you like to know first?</p>
                    <p><em>💡 Pro tip: Click on any stage header to open curated learning resources automatically!</em></p>
                `;
                
                // Clear existing messages except the first one
                const messages = chatbotMessages.querySelectorAll('.message');
                if (messages.length > 1) {
                    for (let i = 1; i < messages.length; i++) {
                        messages[i].remove();
                    }
                }
                
                addMessage(welcomeMessage);
            }, 1000);
            
        } catch (error) {
            console.error('Error generating learning plan:', error);
            
            // Hide loading spinner
            loadingSpinner.style.display = 'none';
            
            // Show error message to user
            alert(`Error generating learning plan: ${error.message}\n\nPlease make sure:\n1. Ollama is running (ollama serve)\n2. The FastAPI server is running on port 8000\n3. You have a compatible model pulled (e.g., ollama pull llama2)`);
        } finally {
            // Re-enable button
            generateBtn.disabled = false;
        }
    });

    // Handle Enter key press
    topicInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            generateBtn.click();
        }
    });
}); 