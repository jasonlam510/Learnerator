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
    
    // Mock learning plan data from mocks folder
    const mockLearningPlan = [
        {
            header: "1. Foundations of Agentic AI in Business",
            details: "Understand what Agentic AI is, why it matters for business automation, and identify key beginner concepts and terminology.",
            keywords: ["agentic AI", "business automation", "AI fundamentals"],
            status: "ongoing",
            urls: [
                "https://beam.ai/agentic-insights/what-is-agentic-ai-the-2025-beginner-s-guide-for-entrepreneurs",
                "https://www.capably.ai/resources/agentic-ai",
                "https://www.mendix.com/blog/guide-to-agentic-ai/",
                "https://www.chaione.com/blog/agentic-ai-a-beginners-guide"
            ]
        },
        {
            header: "2. Beginner Tools for Agentic AI and Automation",
            details: "Get hands-on with beginner-friendly tools for Agentic AI, including low-code platforms, Microsoft Copilot, and simple Python frameworks.",
            keywords: ["AI tools", "low-code platforms", "Python frameworks"],
            status: "pending",
            urls: [
                "https://www.youtube.com/watch?v=g5pY1Tb_r4g",
                "https://www.youtube.com/watch?v=d-CuF6dlqLg",
                "https://www.youtube.com/watch?v=vF2Z4T97xcQ",
                "https://www.getpassionfruit.com/blog/how-to-build-your-first-ai-workflow-with-n8n-beginners-guide",
                "https://www.udemy.com/course/ai-agents-ai-automation-the-practical-agentic-ai-guide/"
            ]
        },
        {
            header: "3. Real-World Business Use Cases and Case Studies",
            details: "Discover how businesses are applying Agentic AI for customer service, support, and workflow optimization. Learn from practical examples and measurable outcomes.",
            keywords: ["use cases", "case studies", "customer service"],
            status: "pending",
            urls: [
                "https://www.vktr.com/ai-disruption/5-ai-case-studies-in-customer-service-and-support/",
                "https://www.japeto.ai/chatbots-in-industry-customer-service-case-studies/",
                "https://www.creolestudios.com/real-world-ai-agent-case-studies/",
                "https://www.chaione.com/blog/agentic-ai-a-beginners-guide"
            ]
        },
        {
            header: "4. Building Your First Agentic AI Workflows",
            details: "Apply your knowledge by building simple Agentic AI workflows using beginner-friendly tools and frameworks. Learn basic Python automation and explore agent frameworks like LangChain.",
            keywords: ["workflows", "LangChain", "Python automation"],
            status: "pending",
            urls: [
                "https://www.youtube.com/watch?v=8BV9TW490nQ",
                "https://www.singlestore.com/blog/beginners-guide-to-langchain/",
                "https://python.langchain.com/docs/tutorials/",
                "https://www.youtube.com/watch?v=w0H1-b044KY",
                "https://flowster.app/workflow-automation-for-beginners-secrets-to-success/",
                "https://www.blinkops.com/blog/ai-workflow-automation"
            ]
        }
    ];
    

    // Initialize popup
    async function initializePopup() {
        console.log('🔍 Initializing popup...');
        console.log('📝 No cached data, showing input form');
        // Focus on input when popup opens
        topicInput.focus();
    }

    // Call initialize function
    initializePopup();

    // Function to get relevant URLs for a stage
    function getStageUrls(topic, stageHeader, keywords, stageData = null) {
        // First check if we have URLs from the backend API
        if (stageData && stageData.urls && stageData.urls.length > 0) {
            console.log(`🔍 Using backend API URLs for ${stageHeader}:`, stageData.urls);
            return stageData.urls;
        }
        
        console.log(`🔍 Falling back to mock URLs for ${stageHeader}`);
        
        const topicLower = topic.toLowerCase();
        const headerLower = stageHeader.toLowerCase();
        
        // Check if we have specific URLs for this topic
        return mockLearningPlan[0].urls ? mockLearningPlan[0].urls : [];
        if (mockLearningPlan[0].urls) {
            const topicUrls = mockLearningPlan[0].urls;
            
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
        return mockLearningPlan[0].urls;
    }

    // Function to open tabs for a stage
    async function openStageResources(stage, stageIndex) {
        try {
            console.log('🔍 Opening resources for stage:', stage.header);
            
            // Get URLs for this stage (now with backend API support)
            const urls = getStageUrls(currentTopic, stage.header, stage.keywords || [], stage);
            
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
                        const urlSource = stage.urls && stage.urls.length > 0 ? 'backend API' : 'curated collection';
                        const successMessage = `
                            <p>🚀 <strong>Opened learning resources for "${stage.header}"</strong></p>
                            <p>Created tab group with ${urls.length} helpful resources from ${urlSource}:</p>
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
        
        // Call backend chatbot API
        callChatbotAPI(message).then(response => {
            // Remove typing indicator
            typingDiv.remove();
            
            if (response && response.answer) {
                // Display the API response
                addMessage(response.answer);
                
                // If there are sources, show them too
                if (response.sources && response.sources.length > 0) {
                    const sourcesMessage = `
                        <p><strong>📚 Sources:</strong></p>
                        <ul>
                            ${response.sources.map(source => `<li><a href="${source}" target="_blank">${source}</a></li>`).join('')}
                        </ul>
                    `;
                    addMessage(sourcesMessage);
                }
            } else {
                // Fallback to local response if API fails
                const fallbackResponse = generateBotResponse(message);
                addMessage(fallbackResponse);
            }
        }).catch(error => {
            // Remove typing indicator
            typingDiv.remove();
            
            console.error('❌ Chatbot API error:', error);
            
            // Show error message and fallback to local response
            const errorMessage = `
                <p>⚠️ <em>Backend chatbot temporarily unavailable. Using local responses.</em></p>
            `;
            addMessage(errorMessage);
            
            // Fallback to local response
            const fallbackResponse = generateBotResponse(message);
            addMessage(fallbackResponse);
        });
    }

    // Function to call backend chatbot API
    async function callChatbotAPI(question) {
        return new Promise((resolve, reject) => {
            // Create request data for the chatbot API
            const requestData = {
                question: question,
                session_id: currentTopic || 'default' // Use current topic as session ID
            };
            
            console.log('🤖 Calling backend chatbot API with question:', question);
            
            // Call the backend chatbot API using background script
            chrome.runtime.sendMessage({
                action: "xhttp",
                method: "POST",
                url: "http://localhost:7000/api/chat",
                data: JSON.stringify(requestData),
                headers: {
                    'Content-Type': 'application/json'
                }
            }, function(response) {
                if (response && response.success && response.status === 200) {
                    const chatData = response.data;
                    console.log('✅ Chatbot API response received:', chatData);
                    
                    resolve({
                        answer: chatData.answer || 'Sorry, I could not generate a response.',
                        sources: chatData.sources || [],
                        session_id: chatData.session_id || 'default',
                        error: chatData.error || null
                    });
                } else {
                    console.warn('⚠️ Chatbot API failed:', response?.error);
                    reject(new Error(response?.error || 'Failed to get chatbot response'));
                }
            });
        });
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
    

        // const learningPlan = await callOllamaAPI(topic);


        // Fallback to mock data
        console.log('Using mock data for topic:', topic);
        const learningPlan = mockLearningPlan;
        
        // Call backend API to get URLs for each stage
        console.log('🔍 Calling backend API to find learning resources...');
        
        for (let i = 0; i < learningPlan.length; i++) {
            const stage = learningPlan[i];
            
            // Create request data for the backend API
            const requestData = {
                header: stage.header,
                details: stage.details,
                keywords: stage.keywords || [],
                status: stage.status
            };
            
            console.log(`🔍 Finding resources for stage ${i + 1}: ${stage.header}`);
            
            // Call the backend API using background script
            console.log('🔍 Sending request to backend API:', requestData);
            const urlResponse = await new Promise((resolve) => {
                chrome.runtime.sendMessage({
                    action: "xhttp",
                    method: "POST",
                    url: "http://localhost:7000/api/find-resources",
                    data: JSON.stringify(requestData),
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }, function(response) {
                    resolve(response);
                });
            });
            
            if (urlResponse && urlResponse.success && urlResponse.status === 200) {
                const urlData = urlResponse.data;
                console.log(`✅ Found ${urlData.urls?.length || 0} URLs for ${stage.header}`);

                
                // Add URLs to the stage
                // learningPlan[i].urls = urlData.urls || [];
                // learningPlan[i].covered_topics = urlData.covered_topics || [];
                // learningPlan[i].has_basics_tutorial = urlData.has_basics_tutorial || false;
                // learningPlan[i].has_youtube_demo = urlData.has_youtube_demo || false;

            } else {
                console.warn(`⚠️ Failed to get URLs for ${stage.header}:`, urlResponse?.error);
                // Keep the stage without URLs
                learningPlan[i].urls = [];
            }
            
            // Add a small delay to avoid overwhelming the API
            await new Promise(resolve => setTimeout(resolve, 500));
        }
        
        console.log('✅ Finished fetching URLs from backend API');
        
        
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
            console.log(`🔍 Rendering stage ${index + 1}:`, stage);
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